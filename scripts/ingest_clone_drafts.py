"""
Phase 4a — Clone Drafts Ingest
==============================

Reads text-clone output from `clone_drafts/<brand>/*.md` and appends the
resulting scheduled post blocks into `brands/<brand>/posts/YYYY-MM-DD.md`
in the exact format the existing `run_scheduler.py` already knows how to parse.

This is the bridge between:
  BRAIN → TEXT CLONE (Claude Project) → clone_drafts/<brand>/*.md
  → (this script) → brands/<brand>/posts/YYYY-MM-DD.md
  → (existing run_scheduler.py) → Bluesky / LinkedIn / Threads / IG / Pinterest / TikTok

Design rules
------------
- Never destroys hand-written blocks. Ingested blocks are appended, not
  overwritten, and are wrapped in a `<!-- CLONE:START id=... -->` / `<!-- CLONE:END -->`
  fence so re-runs are idempotent (same id => skip).
- Never posts anything itself. This script only writes markdown that the
  existing scheduler reads on its normal :05-of-the-hour cron tick.
- Every draft it consumes is moved to `clone_drafts/<brand>/_processed/`
  with the assigned id, so the Claude Project never re-emits the same post.
- Honors the same brand policies as the scheduler
  (TIKTOK_ALLOWED_BRANDS = {"ora", "grissom"}).

Draft file format (what the text clone writes)
----------------------------------------------
`clone_drafts/<brand>/<anything>.md` — one file per DAY, but any number of
blocks. Each block:

    ---
    date: 2026-08-05           # required, YYYY-MM-DD (UTC)
    time: 14:00                # required, HH:MM in UTC (24h)
    platforms: bluesky, threads, instagram, pinterest    # or [bluesky, threads] YAML-list style
    image: brands/ora/assets/drop1_8am_listening.png     # optional
    video: brands/ora/assets/ora_demo.mp4                # optional
    pinterest_title: Just say Ora
    pinterest_url: https://meetora-app.pplx.app
    ---
    Body of the post goes here.
    Multiple lines OK.
    Emoji OK. URLs OK.

If a draft omits `date`, it defaults to TODAY (UTC). If it omits `time`,
it uses the brand's next open slot from `SLOT_DEFAULTS` below.

Usage
-----
    python scripts/ingest_clone_drafts.py            # ingest all drafts
    python scripts/ingest_clone_drafts.py --dry-run  # show what would happen
    python scripts/ingest_clone_drafts.py --brand ora
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = ROOT / "clone_drafts"
BRANDS_DIR = ROOT / "brands"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Mirrors run_scheduler.py registry — keep in sync.
BRANDS = ["ora", "grissom", "familybook"]
TIKTOK_ALLOWED_BRANDS = {"ora", "grissom"}

# Default posting slots per brand (UTC hours), used when a draft omits `time`.
# 13/17/21 UTC == 08/12/16 CDT — matches your Daily Launch Packet cadence.
SLOT_DEFAULTS: Dict[str, List[str]] = {
    "ora":        ["13:00", "18:00", "22:00"],
    "grissom":    ["14:00", "19:00", "23:00"],
    "familybook": ["15:00", "20:00", "00:00"],
}

VALID_PLATFORMS = {"bluesky", "x", "linkedin", "threads", "instagram", "pinterest", "tiktok"}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^\d{2}:\d{2}$")


def _utcnow() -> dt.datetime:
    # timezone-aware UTC without tzinfo attached, for stable string formatting
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)


def log(msg: str) -> None:
    ts = _utcnow().isoformat() + "Z"
    line = f"[{ts}] [ingest] {msg}"
    print(line, flush=True)
    with open(LOG_DIR / "ingest.log", "a") as f:
        f.write(line + "\n")


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def parse_draft_file(path: Path) -> List[dict]:
    """Split a draft file into a list of block dicts.

    Each block is three fences:

        ---            (opening)
        key: value
        key: value
        ---            (meta/body separator)
        body line
        body line
        ---            (closing, optional at EOF)

    Blank lines between blocks are OK. Windows line endings are normalized.
    """
    raw = path.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    if not raw:
        return []
    lines = raw.split("\n")

    def is_fence(s: str) -> bool:
        return s.strip() == "---"

    blocks: List[dict] = []
    i = 0
    n = len(lines)
    while i < n:
        # 1. Skip blank / non-fence lines until we find an opening fence.
        while i < n and not is_fence(lines[i]):
            i += 1
        if i >= n:
            break
        i += 1  # step past opening fence

        # 2. Collect meta lines until the meta/body separator fence.
        meta: Dict[str, str] = {}
        while i < n and not is_fence(lines[i]):
            line = lines[i]
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip().lower()] = v.strip()
            i += 1
        if i >= n:
            break
        i += 1  # step past meta/body separator

        # 3. Collect body lines until closing fence (or EOF).
        body_lines: List[str] = []
        while i < n and not is_fence(lines[i]):
            body_lines.append(lines[i])
            i += 1
        # Consume closing fence so it isn't misread as the opener of the
        # next block.
        if i < n and is_fence(lines[i]):
            i += 1

        body = "\n".join(body_lines).strip()
        if meta or body:
            blocks.append({"meta": meta, "body": body})
    return blocks


# --------------------------------------------------------------------------
# Validation & normalization
# --------------------------------------------------------------------------

def next_open_slot(brand: str, date_str: str, existing_hours: set) -> Optional[str]:
    """Return the next SLOT_DEFAULTS time for `brand` on `date_str` that
    isn't already used in existing_hours (a set of ints)."""
    for slot in SLOT_DEFAULTS.get(brand, []):
        h = int(slot.split(":")[0])
        if h not in existing_hours:
            return slot
    return None


def validate_and_normalize(brand: str, block: dict, existing_hours_by_date) -> Optional[dict]:
    meta = block["meta"]
    body = block["body"]
    if not body:
        log(f"[{brand}] SKIP: empty body")
        return None

    # date
    date_str = meta.get("date") or _utcnow().strftime("%Y-%m-%d")
    if not DATE_RE.match(date_str):
        log(f"[{brand}] SKIP: bad date '{date_str}'")
        return None

    # time
    time_str = meta.get("time")
    if time_str and not TIME_RE.match(time_str):
        log(f"[{brand}] SKIP: bad time '{time_str}'")
        return None
    if not time_str:
        used = existing_hours_by_date.setdefault(date_str, set())
        time_str = next_open_slot(brand, date_str, used)
        if not time_str:
            log(f"[{brand}] SKIP: no open slot on {date_str}")
            return None

    # platforms
    # Accept comma string ("bluesky, threads") or YAML list style ("[bluesky]", "[bluesky, threads]").
    # Strip brackets and split on commas so Claude drafts survive either convention.
    plats_raw = meta.get("platforms", "")
    plats_clean = plats_raw.strip().strip("[]")
    plats = [p.strip().strip("'\"").lower() for p in plats_clean.split(",") if p.strip().strip("'\"")]
    if not plats:
        log(f"[{brand}] SKIP: no platforms listed")
        return None
    bad = [p for p in plats if p not in VALID_PLATFORMS]
    if bad:
        log(f"[{brand}] SKIP: unknown platforms {bad}")
        return None
    if "tiktok" in plats and brand not in TIKTOK_ALLOWED_BRANDS:
        log(f"[{brand}] WARN: TikTok not allowed for this brand — dropping tiktok")
        plats = [p for p in plats if p != "tiktok"]
        if not plats:
            return None

    # tiktok needs video
    if "tiktok" in plats and not meta.get("video"):
        log(f"[{brand}] SKIP: tiktok requires video path")
        return None

    # instagram/pinterest need image
    if ("instagram" in plats or "pinterest" in plats) and not meta.get("image"):
        log(f"[{brand}] SKIP: instagram/pinterest requires image path")
        return None

    # track used hours per date so subsequent blocks in same file get different slots
    hh = int(time_str.split(":")[0])
    existing_hours_by_date.setdefault(date_str, set()).add(hh)

    return {
        "brand": brand,
        "date": date_str,
        "time": time_str,
        "platforms": plats,
        "image": meta.get("image"),
        "video": meta.get("video"),
        "pinterest_title": meta.get("pinterest_title"),
        "pinterest_url": meta.get("pinterest_url"),
        "body": body,
    }


# --------------------------------------------------------------------------
# Emission (write to brands/<brand>/posts/YYYY-MM-DD.md)
# --------------------------------------------------------------------------

CLONE_FENCE_START = "<!-- CLONE:START id={id} -->"
CLONE_FENCE_END = "<!-- CLONE:END -->"
CLONE_ID_RE = re.compile(r"<!-- CLONE:START id=([a-f0-9]{12}) -->")


def block_id(post: dict) -> str:
    """Stable 12-char id derived from brand+date+time+body — same content
    always produces same id, so re-runs are idempotent."""
    seed = f"{post['brand']}|{post['date']}|{post['time']}|{post['body']}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


def render_post_block(post: dict) -> str:
    """Render one scheduled post block in the format run_scheduler.py parses.
    UTC time in header, CDT shown as a courtesy comment.
    """
    hh, mm = post["time"].split(":")
    # CDT = UTC-5 (America/Chicago in DST). Approximate for human readability.
    utc_hour = int(hh)
    cdt_hour = (utc_hour - 5) % 24
    cdt = f"{cdt_hour:02d}:{mm}"

    header = f"## {post['time']} UTC  ({cdt} CDT)"
    meta_lines = [f"platforms: {', '.join(post['platforms'])}"]
    if post.get("image"):
        meta_lines.append(f"image: {post['image']}")
    if post.get("video"):
        meta_lines.append(f"video: {post['video']}")
    if post.get("pinterest_title"):
        meta_lines.append(f"pinterest_title: {post['pinterest_title']}")
    if post.get("pinterest_url"):
        meta_lines.append(f"pinterest_url: {post['pinterest_url']}")

    return (
        CLONE_FENCE_START.format(id=block_id(post))
        + "\n"
        + header
        + "\n"
        + "\n".join(meta_lines)
        + "\n---\n"
        + post["body"]
        + "\n---\n"
        + CLONE_FENCE_END
        + "\n"
    )


def existing_hours_in_file(target: Path) -> set:
    """Return the set of hours (ints) already scheduled in a posts file
    so we don't collide when auto-assigning slots."""
    if not target.exists():
        return set()
    hours = set()
    for line in target.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+(\d{2}):\d{2}\s+UTC", line.strip())
        if m:
            hours.add(int(m.group(1)))
    return hours


def existing_clone_ids_in_file(target: Path) -> set:
    if not target.exists():
        return set()
    return set(CLONE_ID_RE.findall(target.read_text(encoding="utf-8")))


def append_post_to_daily_file(post: dict, dry_run: bool) -> str:
    """Append a rendered clone block to the correct brands/<brand>/posts/YYYY-MM-DD.md
    Returns one of: 'wrote', 'skip-duplicate', 'dry-run'.
    """
    target = BRANDS_DIR / post["brand"] / "posts" / f"{post['date']}.md"
    target.parent.mkdir(parents=True, exist_ok=True)

    bid = block_id(post)
    if bid in existing_clone_ids_in_file(target):
        log(f"[{post['brand']}] skip: {post['date']} {post['time']} already ingested (id={bid})")
        return "skip-duplicate"

    rendered = render_post_block(post)

    if dry_run:
        log(f"[{post['brand']}] [DRY] would append to {target.relative_to(ROOT)} "
            f"(id={bid}, {post['time']} UTC, {post['platforms']})")
        return "dry-run"

    if not target.exists():
        header = f"# {post['brand'].title()} — Auto-ingested — {post['date']}\n\n"
        target.write_text(header, encoding="utf-8")

    with open(target, "a", encoding="utf-8") as f:
        f.write("\n" + rendered + "\n")
    log(f"[{post['brand']}] wrote: {post['date']} {post['time']} UTC "
        f"(id={bid}, platforms={post['platforms']}) -> {target.relative_to(ROOT)}")
    return "wrote"


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------

def ingest_brand(brand: str, dry_run: bool) -> Dict[str, int]:
    stats = {"drafts": 0, "blocks": 0, "wrote": 0, "skipped": 0, "invalid": 0}
    brand_dir = DRAFTS_DIR / brand
    if not brand_dir.exists():
        return stats
    processed_dir = brand_dir / "_processed"
    processed_dir.mkdir(exist_ok=True)

    existing_hours_by_date: Dict[str, set] = {}

    draft_files = sorted(p for p in brand_dir.glob("*.md") if p.is_file())
    for draft in draft_files:
        stats["drafts"] += 1
        blocks = parse_draft_file(draft)
        if not blocks:
            log(f"[{brand}] empty draft: {draft.name}")
            continue
        wrote_from_file = 0
        for block in blocks:
            stats["blocks"] += 1
            # Preload existing hours for whatever date this block resolves to.
            date_str = block["meta"].get("date") or _utcnow().strftime("%Y-%m-%d")
            if date_str not in existing_hours_by_date:
                target = BRANDS_DIR / brand / "posts" / f"{date_str}.md"
                existing_hours_by_date[date_str] = existing_hours_in_file(target)

            post = validate_and_normalize(brand, block, existing_hours_by_date)
            if not post:
                stats["invalid"] += 1
                continue
            result = append_post_to_daily_file(post, dry_run)
            if result == "wrote":
                stats["wrote"] += 1
                wrote_from_file += 1
            elif result == "skip-duplicate":
                stats["skipped"] += 1

        # Only move the draft file out if we're not in dry-run and something happened.
        if not dry_run and (wrote_from_file > 0 or stats["invalid"] == 0):
            dest = processed_dir / f"{_utcnow().strftime('%Y%m%dT%H%M%SZ')}__{draft.name}"
            shutil.move(str(draft), str(dest))
            log(f"[{brand}] archived draft -> {dest.relative_to(ROOT)}")

    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="Show what would happen, write nothing")
    ap.add_argument("--brand", choices=BRANDS, help="Restrict to one brand")
    args = ap.parse_args()

    brands = [args.brand] if args.brand else BRANDS
    log(f"Ingest tick — brands={brands} dry_run={args.dry_run}")
    grand: Dict[str, int] = {"drafts": 0, "blocks": 0, "wrote": 0, "skipped": 0, "invalid": 0}
    for b in brands:
        s = ingest_brand(b, args.dry_run)
        for k in grand:
            grand[k] += s[k]
        log(f"[{b}] summary: {s}")
    log(f"TOTAL: {grand}")
    # Exit code policy:
    #   0 = at least one post was written, or nothing needed writing (drafts=0)
    #   1 = there were drafts to process but nothing was written AND there were invalid blocks
    # This treats "invalid" alongside successful writes as a warning, not a failure, so CI does not
    # go red every time a tiktok/pinterest draft is missing its media path.
    if args.dry_run:
        return 0
    if grand["wrote"] > 0:
        return 0
    if grand["drafts"] == 0:
        return 0
    return 1 if grand["invalid"] else 0


if __name__ == "__main__":
    sys.exit(main())
