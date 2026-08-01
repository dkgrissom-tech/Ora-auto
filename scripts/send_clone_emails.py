"""
Phase 4b — Clone Email Sender
=============================

Reads email drafts from `email_drafts/<brand>/*.md`, hands them to MailerLite as
scheduled or instant campaigns, and archives the source files.

Mirrors the Phase 4a ingest architecture exactly:

  BRAIN  →  Text Clone (Claude Project)
             │
             ▼
   email_drafts/<brand>/*.md     ← YOU or the clone writes here
             │
             ▼   (this script, :35 of every hour)
     MailerLite scheduled campaign
             │
             ▼
        Your subscribers

Design rules
------------
- **Idempotent.** SHA-256 id in the archived filename means the same
  content can't be double-sent.
- **Never sends without a plan.** `--dry-run` builds the API payload but
  posts nothing.
- **Fail closed.** Missing API key or missing group id for a brand →
  the draft stays in place, script exits non-zero so CI surfaces it.
- **Per-brand secrets** — same convention as `run_scheduler.py`:
  `ORA_MAILERLITE_API_KEY`, `ORA_MAILERLITE_GROUP_ID`, etc.

Draft file format
-----------------
`email_drafts/<brand>/<anything>.md`:

    ---
    subject: Ora goes live in 72 hours
    from_name: Don at Ora
    from_email: hello@meetora.app     # must be verified in MailerLite
    reply_to: don@grissom.tech        # optional
    schedule: 2026-08-05 14:00 UTC    # optional; omit for instant send
    ---
    # Ora goes live in 72 hours

    Say it and it starts listening.

    Founding-user pricing goes away on launch day.

    [Join the waitlist](https://meetora-app.pplx.app)

Body is markdown. Converted to minimal HTML on the way to MailerLite so the
account name / address / unsubscribe footer that MailerLite auto-injects
still renders correctly on free-tier accounts.

Usage
-----
    python scripts/send_clone_emails.py                  # process all brands
    python scripts/send_clone_emails.py --dry-run        # build + validate, don't send
    python scripts/send_clone_emails.py --brand ora      # single brand
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
DRAFTS_DIR = ROOT / "email_drafts"
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Mirrors run_scheduler.py / ingest_clone_drafts.py registry.
BRANDS = ["ora", "grissom", "familybook"]

MAILERLITE_BASE = "https://connect.mailerlite.com/api"
DRY_RUN_ENV = os.environ.get("DRY_RUN", "false").lower() == "true"

DATETIME_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<hh>\d{2}):(?P<mm>\d{2})(?:\s*UTC)?$"
)


def _utcnow() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc).replace(tzinfo=None)


def log(msg: str) -> None:
    ts = _utcnow().isoformat() + "Z"
    line = f"[{ts}] [email] {msg}"
    print(line, flush=True)
    with open(LOG_DIR / "email.log", "a") as f:
        f.write(line + "\n")


def secret(brand: str, key: str) -> Optional[str]:
    """Read a brand-prefixed env var. secret('ora', 'MAILERLITE_API_KEY')
    → ORA_MAILERLITE_API_KEY."""
    return os.environ.get(f"{brand.upper()}_{key}")


# ------------------------------------------------------------------
# Parsing
# ------------------------------------------------------------------

def parse_email_draft(path: Path) -> Optional[dict]:
    """Parse one email draft file. Returns dict with meta + body_md, or None
    on hard parse errors."""
    raw = path.read_text(encoding="utf-8").replace("\r\n", "\n").strip()
    if not raw:
        return None
    lines = raw.split("\n")

    if not lines or lines[0].strip() != "---":
        log(f"parse error in {path.name}: missing opening --- fence")
        return None

    meta: Dict[str, str] = {}
    i = 1
    while i < len(lines) and lines[i].strip() != "---":
        line = lines[i]
        if ":" in line:
            k, v = line.split(":", 1)
            meta[k.strip().lower()] = v.strip()
        i += 1

    if i >= len(lines):
        log(f"parse error in {path.name}: missing closing --- of frontmatter")
        return None

    body_md = "\n".join(lines[i + 1 :]).strip()
    if not body_md:
        log(f"parse error in {path.name}: empty body")
        return None

    return {"meta": meta, "body_md": body_md, "source": path.name}


# ------------------------------------------------------------------
# Validation + normalization
# ------------------------------------------------------------------

def parse_schedule(value: str) -> Optional[Tuple[str, str, str]]:
    """Return (date, hh, mm) UTC tuple, or None if unparseable."""
    m = DATETIME_RE.match(value.strip())
    if not m:
        return None
    return m.group("date"), m.group("hh"), m.group("mm")


def validate(draft: dict) -> Optional[dict]:
    m = draft["meta"]
    missing = [k for k in ("subject", "from_name", "from_email") if not m.get(k)]
    if missing:
        log(f"{draft['source']}: missing required fields {missing}")
        return None

    schedule = None
    if m.get("schedule"):
        parsed = parse_schedule(m["schedule"])
        if not parsed:
            log(f"{draft['source']}: bad schedule '{m['schedule']}' "
                f"(want 'YYYY-MM-DD HH:MM UTC')")
            return None
        date_str, hh, mm = parsed
        # must be in the future
        target = dt.datetime.strptime(f"{date_str} {hh}:{mm}", "%Y-%m-%d %H:%M")
        if target <= _utcnow():
            log(f"{draft['source']}: schedule '{m['schedule']}' is in the past")
            return None
        schedule = {"date": date_str, "hours": hh, "minutes": mm}

    return {
        "subject": m["subject"],
        "from_name": m["from_name"],
        "from_email": m["from_email"],
        "reply_to": m.get("reply_to"),
        "schedule": schedule,
        "body_md": draft["body_md"],
        "source": draft["source"],
    }


# ------------------------------------------------------------------
# Markdown → minimal HTML (no external deps)
# ------------------------------------------------------------------

_HTML_ESC = {"&": "&amp;", "<": "&lt;", ">": "&gt;"}

def _escape(s: str) -> str:
    for k, v in _HTML_ESC.items():
        s = s.replace(k, v)
    return s

_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC_RE = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")


def _inline(line: str) -> str:
    line = _escape(line)
    line = _LINK_RE.sub(r'<a href="\2">\1</a>', line)
    line = _BOLD_RE.sub(r"<strong>\1</strong>", line)
    line = _ITALIC_RE.sub(r"<em>\1</em>", line)
    return line


def md_to_html(md: str) -> str:
    """Minimal markdown → HTML. Handles: # headings, blank-line paragraphs,
    - / * bullet lists, inline links, bold, italic. Enough for
    launch-email copy from the clone. Any raw HTML in the source passes through
    after escaping. MailerLite injects the required footer (unsubscribe,
    address, account name) automatically."""
    out: List[str] = []
    lines = md.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue
        # headings
        m = re.match(r"^(#{1,6})\s+(.*)$", stripped)
        if m:
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue
        # bullet list
        if re.match(r"^[-*]\s+", stripped):
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(_inline(re.sub(r"^[-*]\s+", "", lines[i].strip())))
                i += 1
            out.append("<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>")
            continue
        # paragraph — collect until blank line
        para: List[str] = []
        while i < len(lines) and lines[i].strip() and not re.match(
            r"^(#{1,6}\s+|[-*]\s+)", lines[i].strip()
        ):
            para.append(_inline(lines[i].strip()))
            i += 1
        out.append("<p>" + "<br>".join(para) + "</p>")
    return "\n".join(out)


# ------------------------------------------------------------------
# MailerLite API
# ------------------------------------------------------------------

def _api_call(method: str, path: str, api_key: str, payload: Optional[dict] = None) -> dict:
    """Thin wrapper. Keeps `requests` local so tests don't need the module."""
    import requests
    url = f"{MAILERLITE_BASE}{path}"
    r = requests.request(
        method,
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        data=json.dumps(payload) if payload is not None else None,
        timeout=30,
    )
    if r.status_code >= 400:
        raise RuntimeError(
            f"MailerLite {method} {path} → {r.status_code} {r.text[:300]}"
        )
    return r.json() if r.text else {}


def build_create_payload(email: dict, group_id: str) -> dict:
    html = md_to_html(email["body_md"])
    email_block = {
        "subject": email["subject"],
        "from_name": email["from_name"],
        "from": email["from_email"],
        "content": html,
    }
    if email.get("reply_to"):
        email_block["reply_to"] = email["reply_to"]
    return {
        "name": f"[clone] {email['subject'][:120]}",
        "type": "regular",
        "emails": [email_block],
        "groups": [group_id],
    }


def build_schedule_payload(email: dict) -> dict:
    if email["schedule"]:
        return {
            "delivery": "scheduled",
            "schedule": email["schedule"],
        }
    return {"delivery": "instant"}


def send_email(brand: str, email: dict, dry_run: bool) -> str:
    """Return 'sent' | 'scheduled' | 'dry-run' | 'skipped-config'."""
    api_key = secret(brand, "MAILERLITE_API_KEY")
    group_id = secret(brand, "MAILERLITE_GROUP_ID")
    if not (api_key and group_id):
        log(f"[{brand}] SKIP {email['source']}: missing MAILERLITE api key or group id")
        return "skipped-config"

    create_body = build_create_payload(email, group_id)
    schedule_body = build_schedule_payload(email)

    if dry_run:
        log(f"[{brand}] [DRY] would create campaign '{email['subject']}' → "
            f"group={group_id}, delivery={schedule_body['delivery']}"
            + (f", schedule={schedule_body.get('schedule')}" if schedule_body.get('schedule') else ""))
        return "dry-run"

    created = _api_call("POST", "/campaigns", api_key, create_body)
    cid = (created.get("data") or {}).get("id") or created.get("id")
    if not cid:
        raise RuntimeError(f"MailerLite create returned no id: {created}")
    log(f"[{brand}] created campaign id={cid} subject='{email['subject']}'")

    _api_call("POST", f"/campaigns/{cid}/schedule", api_key, schedule_body)
    result = "scheduled" if email["schedule"] else "sent"
    log(f"[{brand}] {result} campaign id={cid}")
    return result


# ------------------------------------------------------------------
# Draft archival (idempotency safety net)
# ------------------------------------------------------------------

def content_id(email: dict) -> str:
    seed = f"{email['subject']}|{email['from_email']}|{email['body_md']}"
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12]


def archive_draft(brand: str, draft_path: Path, email: dict) -> Path:
    processed = DRAFTS_DIR / brand / "_sent"
    processed.mkdir(parents=True, exist_ok=True)
    stamp = _utcnow().strftime("%Y%m%dT%H%M%SZ")
    dest = processed / f"{stamp}__{content_id(email)}__{draft_path.name}"
    shutil.move(str(draft_path), str(dest))
    return dest


def already_sent(brand: str, email: dict) -> bool:
    processed = DRAFTS_DIR / brand / "_sent"
    if not processed.exists():
        return False
    cid = content_id(email)
    return any(cid in p.name for p in processed.iterdir())


# ------------------------------------------------------------------
# Main
# ------------------------------------------------------------------

def process_brand(brand: str, dry_run: bool) -> Dict[str, int]:
    stats = {"drafts": 0, "sent": 0, "scheduled": 0, "dry-run": 0,
             "skipped-duplicate": 0, "skipped-config": 0, "invalid": 0}
    brand_dir = DRAFTS_DIR / brand
    if not brand_dir.exists():
        return stats

    for draft in sorted(p for p in brand_dir.glob("*.md") if p.is_file()):
        stats["drafts"] += 1
        parsed = parse_email_draft(draft)
        if not parsed:
            stats["invalid"] += 1
            continue
        email = validate(parsed)
        if not email:
            stats["invalid"] += 1
            continue

        if already_sent(brand, email):
            log(f"[{brand}] skip: {draft.name} already sent (id={content_id(email)})")
            stats["skipped-duplicate"] += 1
            # move it out of the inbox so it doesn't keep triggering
            if not dry_run:
                archive_draft(brand, draft, email)
            continue

        try:
            result = send_email(brand, email, dry_run)
        except Exception as e:
            log(f"[{brand}] FAIL {draft.name}: {e}")
            stats["invalid"] += 1
            continue

        if result == "skipped-config":
            stats["skipped-config"] += 1
            # leave draft in place — user needs to add secrets
            continue

        if not dry_run and result in ("sent", "scheduled"):
            archive_draft(brand, draft, email)

        stats[result] = stats.get(result, 0) + 1

    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--brand", choices=BRANDS)
    args = ap.parse_args()
    dry_run = args.dry_run or DRY_RUN_ENV

    brands = [args.brand] if args.brand else BRANDS
    log(f"Email tick — brands={brands} dry_run={dry_run}")
    grand: Dict[str, int] = {}
    for b in brands:
        s = process_brand(b, dry_run)
        for k, v in s.items():
            grand[k] = grand.get(k, 0) + v
        log(f"[{b}] summary: {s}")
    log(f"TOTAL: {grand}")
    return 1 if grand.get("invalid", 0) and not dry_run else 0


if __name__ == "__main__":
    sys.exit(main())
