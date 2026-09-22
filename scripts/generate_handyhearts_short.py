#!/usr/bin/env python3
"""Generate one Handy Hearts book trailer from the queue.

Reads the next `queued` row from brands/handyhearts/queue.csv, renders a
17-second vertical short on VideoGen.io (`script-to-video` workflow), then
runs an ffmpeg pass that:
  1. Converts the 1920x1080 landscape VideoGen output to a 1080x1920 vertical
     with a blurred-amber background (no zoom crop).
  2. Overlays the REAL Handy Hearts cover (D.K. Grissom) for the last 4
     seconds so no AI-fabricated book/author can appear on screen.

Then it writes a scheduled post block under brands/handyhearts/posts/ so the
existing multi-brand auto-poster picks the video up on its next slot hour.
Posts fan out to the `grissom` brand's connected accounts (TikTok, Instagram,
Pinterest via Buffer) since Handy Hearts is a Grissom Press release.

Environment:
  VIDEOGEN_API_KEY          VideoGen.io API bearer token
  HANDYHEARTS_RENDER_ENABLED  "false" kills all renders (default true)
  HANDYHEARTS_DRY_RUN         "true" prints plan, no API call (default false)
"""
from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

# --- Config ---------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
BRAND_DIR = ROOT / "brands" / "handyhearts"
QUEUE_CSV = BRAND_DIR / "queue.csv"
ASSETS_DIR = BRAND_DIR / "assets"
COSTS_CSV = BRAND_DIR / "learnings" / "render_costs.csv"

COVER_PATH = ASSETS_DIR / "cover-master.png"

VIDEOGEN_API = "https://api.videogen.io"
VIDEOGEN_TIMEOUT_S = 600
VIDEOGEN_POLL_S = 15

# Cost per short in VideoGen credits (measured across 7 test renders).
# Test #3-#9 landed 105-280 depending on scene complexity. 250 is the safe
# ceiling for budget math — cheaper in practice.
CREDIT_COST_PER_SHORT = 250
CREDIT_BUDGET_PER_MONTH = 15000  # leaves 3000 buffer on the 18000/mo plan


# --- Helpers --------------------------------------------------------------


def log(msg: str) -> None:
    print(f"[handyhearts] {msg}", flush=True)


def env_bool(name: str, default: bool) -> bool:
    v = os.environ.get(name, "").strip().lower()
    if not v:
        return default
    return v in ("1", "true", "yes", "on")


def read_queue() -> list[dict]:
    with QUEUE_CSV.open() as f:
        return list(csv.DictReader(f))


def write_queue(rows: list[dict]) -> None:
    if not rows:
        return
    with QUEUE_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def next_queued(rows: list[dict]) -> dict | None:
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    current_hour = now.hour
    # Slot to UTC hour: morning=14 (09:00 CDT), evening=22 (17:00 CDT)
    slot_hours = {"morning": 14, "evening": 22}
    for r in rows:
        if r.get("status", "").strip() != "queued":
            continue
        sched = r.get("scheduled_date", "").strip()
        if not sched:
            continue
        if sched > today:
            continue
        if sched == today:
            slot = r.get("time_slot", "").strip().lower()
            slot_hour = slot_hours.get(slot)
            if slot_hour is not None and current_hour < slot_hour:
                # Not yet time for this slot today
                continue
        return r
    return None


def append_cost(creative_id: str, credits: int) -> None:
    COSTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    new = not COSTS_CSV.exists()
    with COSTS_CSV.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp_utc", "creative_id", "credits"])
        w.writerow([datetime.now(timezone.utc).isoformat(), creative_id, credits])


def credits_spent(window_hours: int) -> int:
    if not COSTS_CSV.exists():
        return 0
    cutoff = time.time() - window_hours * 3600
    total = 0
    with COSTS_CSV.open() as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                t = datetime.fromisoformat(row["timestamp_utc"]).timestamp()
                if t >= cutoff:
                    total += int(row["credits"])
            except (KeyError, ValueError):
                continue
    return total


def budget_ok() -> tuple[bool, str]:
    month_spent = credits_spent(24 * 30)
    if month_spent + CREDIT_COST_PER_SHORT > CREDIT_BUDGET_PER_MONTH:
        return False, f"month_spent {month_spent} + {CREDIT_COST_PER_SHORT} > {CREDIT_BUDGET_PER_MONTH}"
    return True, "ok"


# --- VideoGen API ---------------------------------------------------------


def videogen_headers() -> dict:
    token = os.environ.get("VIDEOGEN_API_KEY", "")
    if not token:
        raise SystemExit("VIDEOGEN_API_KEY not set")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def http_json(method: str, url: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = Request(url, data=data, method=method, headers=videogen_headers())
    with urlopen(req, timeout=VIDEOGEN_TIMEOUT_S) as resp:
        return json.loads(resp.read().decode())


def run_videogen(script: str, scenes: list[dict]) -> str:
    """Submit a script-to-video render and poll for the download URL."""
    body = {
        "script": script,
        "visualStyle": {
            "type": "AI_IMAGE",
            "aiStyle": (
                "Warm cinematic small-town Southern romance photograph. "
                "Vertical composition, 9:16 aspect ratio. Golden hour lighting, "
                "soft focus, painterly texture. A cozy Southern town with weathered "
                "wooden porches, wildflowers, blue-collar hands, and quiet emotional "
                "moments. Warm amber and cream palette. Do not include any books, "
                "novels, hardcovers, or written text of any kind."
            ),
        },
        "aspectRatio": {"width": 9, "height": 16},
        "visualPacing": "MEDIUM",
        "quality": "HIGH",
        "scenes": scenes,
        "autoExport": True,
        "remixActions": [{"type": "ENABLE_CAPTIONS"}],
    }
    r = http_json("POST", f"{VIDEOGEN_API}/v1/workflows/script-to-video", body)
    run_id = r.get("workflowRunId")
    if not run_id:
        raise RuntimeError(f"videogen submit returned no workflowRunId: {r}")

    deadline = time.time() + VIDEOGEN_TIMEOUT_S
    while time.time() < deadline:
        time.sleep(VIDEOGEN_POLL_S)
        r = http_json("GET", f"{VIDEOGEN_API}/v1/workflows/runs/{run_id}")
        status = r.get("status")
        if status == "succeeded":
            url = r.get("downloadUrl")
            if not url:
                raise RuntimeError(f"videogen succeeded but no downloadUrl: {r}")
            return url
        if status in ("failed", "cancelled"):
            raise RuntimeError(f"videogen {status}: {r.get('error') or r}")
    raise RuntimeError(f"videogen timeout after {VIDEOGEN_TIMEOUT_S}s")


def download_bypass_proxy(url: str, dst: Path) -> None:
    """VideoGen download URLs are pre-signed CDN links that reject the
    HTTPS proxy. Use curl with proxy env stripped."""
    subprocess.run(
        ["curl", "-sSL", "-o", str(dst), url],
        check=True,
        env={**os.environ, "HTTPS_PROXY": "", "https_proxy": "", "HTTP_PROXY": "", "http_proxy": ""},
    )


# --- FFmpeg vertical + cover overlay --------------------------------------


def compose(raw: Path, out: Path, cover_start: float = 12.8, cover_duration: float = 4.0) -> None:
    """Convert 1920x1080 landscape to 1080x1920 vertical with blur-fill
    background, then overlay the real cover for the last 4 seconds.

    Recipe validated across 4 test renders (Test #6 → #9). Anything else
    (center-crop, pad, plain overlay) either zooms in or lets the AI's fake
    book/author show through.
    """
    if not COVER_PATH.exists():
        raise SystemExit(f"COVER MISSING: {COVER_PATH}")

    filter_complex = (
        "[0:v]split[bg][fg];"
        "[bg]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,gblur=sigma=30[blurbg];"
        "[fg]scale=1080:-1[main];"
        "[blurbg][main]overlay=(W-w)/2:(H-h)/2[base];"
        f"[1:v]scale=1000:-1,format=yuva420p,fade=t=in:st=0:d=0.4:alpha=1,setpts=PTS-STARTPTS+{cover_start}/TB[cov];"
        "[base][cov]overlay=(W-w)/2:(H-h)/2:eof_action=pass"
    )
    cmd = [
        "ffmpeg", "-y",
        "-i", str(raw),
        "-loop", "1", "-t", str(cover_duration), "-i", str(COVER_PATH),
        "-filter_complex", filter_complex,
        "-c:a", "copy",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True)


# --- Main -----------------------------------------------------------------


def main() -> int:
    if not env_bool("HANDYHEARTS_RENDER_ENABLED", True):
        log("HANDYHEARTS_RENDER_ENABLED=false — halted")
        return 0

    dry_run = env_bool("HANDYHEARTS_DRY_RUN", False)

    rows = read_queue()
    row = next_queued(rows)
    if not row:
        log("No queued rows due — nothing to do")
        return 0

    creative_id = row["creative_id"]

    ok, why = budget_ok()
    if not ok:
        log(f"BUDGET_HALT {why}")
        return 0

    script = row["script"]
    scenes = [
        {"startSeconds": float(row["scene1_start"]), "endSeconds": float(row["scene1_end"]), "description": row["scene1_prompt"]},
        {"startSeconds": float(row["scene2_start"]), "endSeconds": float(row["scene2_end"]), "description": row["scene2_prompt"]},
        {"startSeconds": float(row["scene3_start"]), "endSeconds": float(row["scene3_end"]), "description": row["scene3_prompt"]},
        {"startSeconds": float(row["scene4_start"]), "endSeconds": float(row["scene4_end"]), "description": row["scene4_prompt"]},
    ]

    log(f"Rendering {creative_id} (projected credits <= {CREDIT_COST_PER_SHORT})")
    if dry_run:
        log("DRY_RUN=true — skipping API calls")
        for i, s in enumerate(scenes, 1):
            log(f"  scene{i}: {s['description'][:80]}")
        return 0

    # 1. VideoGen render
    raw = ASSETS_DIR / f"{creative_id}_raw.mp4"
    log("VideoGen: submitting render…")
    download_url = run_videogen(script, scenes)
    log(f"VideoGen: downloading raw MP4 → {raw.name}")
    download_bypass_proxy(download_url, raw)
    append_cost(creative_id, CREDIT_COST_PER_SHORT)

    # 2. FFmpeg vertical + real cover overlay
    final = ASSETS_DIR / f"{creative_id}.mp4"
    log(f"FFmpeg: compose → {final.name}")
    compose(raw, final)

    # Clean intermediate
    raw.unlink(missing_ok=True)

    # 3. Mark row rendered
    for r in rows:
        if r["creative_id"] == creative_id:
            r["status"] = "rendered"
            r["rendered_at"] = datetime.now(timezone.utc).isoformat()
            break
    write_queue(rows)

    # 4. Write scheduled post block for the auto-poster
    write_post_block(row, final)

    log("DONE")
    return 0


# ---------------------------------------------------------------------------
# Post-block bridge
# ---------------------------------------------------------------------------
#
# Handy Hearts posts fan out under the `grissom` brand rails (which are already
# wired to TikTok @amgriss1 via Buffer, Instagram @dkgrissom via Buffer, and
# Pinterest Grissompress via Postiz/Buffer). That means we write the post
# block into brands/grissom/posts/ so the multi-brand scheduler picks it up.

SLOT_TO_HOUR = {"morning": 14, "evening": 22}
SLOT_TO_CDT = {"morning": "09:00 CDT", "evening": "17:00 CDT"}

DEFAULT_TAGS = "#BookTok #Romance #SmallTownRomance #CedarHollow #HandyHearts #DKGrissom"


def write_post_block(row: dict, video_path: Path) -> None:
    creative_id = row["creative_id"]
    scheduled_date = row.get("scheduled_date", "").strip()
    slot = row.get("time_slot", "").strip().lower()
    hook = row.get("hook", "").strip()
    tags = row.get("tags", "").strip() or DEFAULT_TAGS
    pin_title = row.get("pinterest_title", "").strip()
    if not pin_title:
        pin_title = f"Handy Hearts: {hook.rstrip('.')}"[:100]

    hour = SLOT_TO_HOUR.get(slot)
    if hour is None:
        log(f"POST_BLOCK skipped — unknown time_slot={slot!r}")
        return
    if not scheduled_date:
        log(f"POST_BLOCK skipped — no scheduled_date on {creative_id}")
        return

    # Force-post override: write the block into TODAY UTC at the next reachable
    # hour (either current hour or current+1) so the auto-poster's next :20 tick
    # picks it up. Used for smoke tests. Also stamps the scheduled_date/time_slot
    # back onto the row so re-runs don't try to fire it again.
    if env_bool("HANDYHEARTS_FORCE_POST_NOW", False):
        now = datetime.now(timezone.utc)
        # Next tick fires at :20 of every hour. If we are before :20 this hour,
        # target THIS hour. Otherwise target next hour.
        target_hour = now.hour if now.minute < 20 else (now.hour + 1) % 24
        scheduled_date = now.strftime("%Y-%m-%d")
        hour = target_hour
        log(f"FORCE_POST_NOW → writing block for {scheduled_date} at {hour:02d}:00 UTC")

    rel_video = video_path.relative_to(ROOT).as_posix()

    posts_dir = ROOT / "brands" / "grissom" / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)
    target = posts_dir / f"{scheduled_date}.md"

    marker_id = f"handyhearts-{scheduled_date}-{hour:02d}00-{creative_id.lower()}"
    existing = target.read_text() if target.exists() else ""
    if f"CLONE:START id={marker_id}" in existing:
        log(f"POST_BLOCK exists for {creative_id} — no-op")
        return

    header = existing if existing else f"# Grissom Press — {scheduled_date}\n"
    body_text = row.get("caption", "").strip() or hook
    block = (
        f"\n<!-- CLONE:START id={marker_id} -->\n"
        f"## {hour:02d}:00 UTC  ({SLOT_TO_CDT[slot]})\n"
        f"platforms: tiktok, instagram, pinterest\n"
        f"video: {rel_video}\n"
        f"image: {rel_video}\n"
        f"creative_id: {creative_id}\n"
        f"series: handyhearts\n"
        f"pinterest_title: {pin_title}\n"
        f"pinterest_url: https://cedarhollow.pplx.app\n"
        f"---\n"
        f"{body_text}\n\n"
        f"{tags}\n"
        f"---\n"
        f"<!-- CLONE:END -->\n"
    )
    target.write_text(header + block)
    log(f"POST_BLOCK wrote {target.name} for {creative_id} at {hour:02d}:00 UTC")


if __name__ == "__main__":
    sys.exit(main())
