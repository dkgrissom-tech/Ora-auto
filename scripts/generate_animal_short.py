#!/usr/bin/env python3
"""Generate one toolstack talking-animal short from the queue.

Reads the next `queued` row from brands/toolstack/queue.csv, renders 3 beats on
Replicate wan-2.2-i2v-480p-fast, stitches them with ffmpeg, commits the MP4,
and marks the row `rendered`.

Budget guards (see brands/toolstack/BUDGET.md) hard-fail before any API call.

Environment:
  REPLICATE_API_TOKEN  Replicate token (Bearer)
  TOOLSTACK_RENDER_ENABLED  "false" kills all renders (default true)
  TOOLSTACK_DRY_RUN         "true"  prints plan, no API call (default false)
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
BRAND_DIR = ROOT / "brands" / "toolstack"
QUEUE_CSV = BRAND_DIR / "queue.csv"
ASSETS_DIR = BRAND_DIR / "assets"
REFS_DIR = ASSETS_DIR / "refs"
COSTS_CSV = BRAND_DIR / "learnings" / "render_costs.csv"

MODEL = "wan-video/wan-2.2-i2v-480p-fast"
# Pinned version (fill this in after first sanity call; see README)
MODEL_VERSION = os.environ.get("TOOLSTACK_MODEL_VERSION", "")

# Costs (see BUDGET.md)
COST_PER_BEAT_USD = 0.05
MAX_COST_PER_POST_USD = 0.30
MAX_COST_PER_DAY_USD = 1.00
MAX_COST_PER_MONTH_USD = 30.00
BEATS_PER_POST = 3

REPLICATE_API = "https://api.replicate.com/v1"

# --- Helpers --------------------------------------------------------------


def log(msg: str) -> None:
    print(f"[toolstack] {msg}", flush=True)


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
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    for r in rows:
        if r.get("status", "").strip() != "queued":
            continue
        sched = r.get("scheduled_date", "").strip()
        if sched and sched > today:
            continue
        return r
    return None


def append_cost(creative_id: str, beat: int, seconds: int, cost: float) -> None:
    COSTS_CSV.parent.mkdir(parents=True, exist_ok=True)
    new = not COSTS_CSV.exists()
    with COSTS_CSV.open("a", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["timestamp_utc", "creative_id", "beat", "model", "seconds", "estimated_cost_usd"])
        w.writerow([datetime.now(timezone.utc).isoformat(), creative_id, beat, MODEL, seconds, f"{cost:.4f}"])


def spent(window_hours: int) -> float:
    if not COSTS_CSV.exists():
        return 0.0
    cutoff = time.time() - window_hours * 3600
    total = 0.0
    with COSTS_CSV.open() as f:
        r = csv.DictReader(f)
        for row in r:
            try:
                t = datetime.fromisoformat(row["timestamp_utc"]).timestamp()
                if t >= cutoff:
                    total += float(row["estimated_cost_usd"])
            except (KeyError, ValueError):
                continue
    return total


def budget_ok(post_cost: float) -> tuple[bool, str]:
    if post_cost > MAX_COST_PER_POST_USD:
        return False, f"post_cost {post_cost:.2f} > {MAX_COST_PER_POST_USD}"
    today_spent = spent(24)
    if today_spent + post_cost > MAX_COST_PER_DAY_USD:
        return False, f"day_spent {today_spent:.2f} + {post_cost:.2f} > {MAX_COST_PER_DAY_USD}"
    month_spent = spent(24 * 30)
    if month_spent + post_cost > MAX_COST_PER_MONTH_USD:
        return False, f"month_spent {month_spent:.2f} + {post_cost:.2f} > {MAX_COST_PER_MONTH_USD}"
    return True, "ok"


# --- Replicate API --------------------------------------------------------


def replicate_headers() -> dict:
    token = os.environ.get("REPLICATE_API_TOKEN", "")
    if not token:
        raise SystemExit("REPLICATE_API_TOKEN not set")
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Prefer": "wait",
    }


def http_json(method: str, url: str, body: dict | None = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = Request(url, data=data, method=method, headers=replicate_headers())
    with urlopen(req, timeout=300) as resp:
        return json.loads(resp.read().decode())


def run_prediction(inputs: dict) -> str:
    """Fire a prediction and wait. Returns the output MP4 URL."""
    if MODEL_VERSION:
        body = {"version": MODEL_VERSION, "input": inputs}
        r = http_json("POST", f"{REPLICATE_API}/predictions", body)
    else:
        # Use model-slug endpoint (uses model's default version)
        body = {"input": inputs}
        r = http_json("POST", f"{REPLICATE_API}/models/{MODEL}/predictions", body)

    # Prefer: wait may return terminal status directly.
    status = r.get("status")
    prediction_id = r.get("id")
    while status not in ("succeeded", "failed", "canceled"):
        time.sleep(3)
        r = http_json("GET", f"{REPLICATE_API}/predictions/{prediction_id}")
        status = r.get("status")

    if status != "succeeded":
        raise RuntimeError(f"prediction {prediction_id} status={status} error={r.get('error')}")

    out = r.get("output")
    if isinstance(out, list):
        out = out[0]
    if not isinstance(out, str) or not out.startswith("http"):
        raise RuntimeError(f"prediction {prediction_id} unexpected output: {out!r}")
    return out


def download(url: str, dst: Path) -> None:
    with urlopen(url, timeout=120) as resp, dst.open("wb") as f:
        while True:
            chunk = resp.read(1 << 16)
            if not chunk:
                break
            f.write(chunk)


# --- FFmpeg stitch --------------------------------------------------------


def stitch(beat_paths: list[Path], out: Path) -> None:
    concat = out.with_suffix(".concat.txt")
    concat.write_text("".join(f"file '{p.name}'\n" for p in beat_paths))
    cmd = [
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat),
        # wan-2.2 480p outputs 512x768 @ 16 fps. TikTok's posting API needs
        # 23-60 fps (Buffer accepts, TikTok silently drops), so upscale to
        # 1080x1920 vertical and resample to 30 fps.
        "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,"
               "pad=1080:1920:(ow-iw)/2:(oh-ih)/2:color=black,fps=30",
        "-r", "30",
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
        "-movflags", "+faststart",
        str(out),
    ]
    subprocess.run(cmd, check=True, cwd=out.parent, capture_output=True)
    concat.unlink()


# --- Voice (free edge-tts) ------------------------------------------------
# wan-2.2 renders silent video. Veo-era test shorts had native speech; the
# scheduled pipeline shipped mute until this step. Each beat prompt carries
# its line as "says: <line>.." (beat1 says the hook).
import asyncio
import re

SERIES_VOICE = {
    # (voice, rate, pitch) — cartoon-leaning tweaks on stock neural voices
    "milo":    ("en-US-ChristopherNeural", "+0%",  "+12Hz"),
    "milo2":   ("en-US-ChristopherNeural", "+0%",  "+12Hz"),
    "rita":    ("en-US-JennyNeural",       "+6%",  "+18Hz"),
    "barkley": ("en-US-GuyNeural",         "-6%",  "-14Hz"),
}
DEFAULT_VOICE = ("en-US-ChristopherNeural", "+0%", "+0Hz")


def beat_line(prompt: str, hook: str) -> str:
    m = re.search(r"says:\s*(.+?)\.{1,2}\s+The character speaks", prompt, re.S)
    if m:
        return m.group(1).strip()
    m = re.search(r"says:\s*([^\n]+?)(?:\.\.|$)", prompt)
    if m:
        return m.group(1).strip()
    return hook.strip()


def tts(text: str, series: str, out: Path) -> None:
    import edge_tts
    voice, rate, pitch = SERIES_VOICE.get(series, DEFAULT_VOICE)
    async def _go():
        await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(str(out))
    for attempt in range(3):
        try:
            asyncio.run(_go())
            if out.exists() and out.stat().st_size > 1000:
                return
        except Exception as e:  # network blips on the runner
            log(f"  tts attempt {attempt + 1} failed: {e}")
        time.sleep(3)
    raise RuntimeError(f"edge-tts failed for: {text[:60]}")


def _dur(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], capture_output=True, text=True, check=True)
    return float(out.stdout.strip() or 0)


def voice_beat(beat_mp4: Path, line: str, series: str) -> Path:
    """Mux a spoken line onto one silent beat. If the line is longer than the
    clip, hold the last frame so the sentence is never cut off."""
    mp3 = beat_mp4.with_suffix(".mp3")
    tts(line, series, mp3)
    vdur, adur = _dur(beat_mp4), _dur(mp3)
    target = max(vdur, adur + 0.35)
    hold = max(0.0, target - vdur)
    out = beat_mp4.with_name(beat_mp4.stem + "_vo.mp4")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(beat_mp4), "-i", str(mp3),
        "-filter_complex",
        f"[0:v]tpad=stop_mode=clone:stop_duration={hold:.3f}[v];"
        f"[1:a]adelay=150|150,apad,atrim=0:{target:.3f},loudnorm=I=-14:TP=-1[a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-crf", "18", "-preset", "fast", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
        "-t", f"{target:.3f}", str(out),
    ], check=True, capture_output=True)
    mp3.unlink(missing_ok=True)
    return out


# --- Main -----------------------------------------------------------------


def main() -> int:
    if not env_bool("TOOLSTACK_RENDER_ENABLED", True):
        log("TOOLSTACK_RENDER_ENABLED=false — halted")
        return 0

    dry_run = env_bool("TOOLSTACK_DRY_RUN", False)

    rows = read_queue()
    row = next_queued(rows)
    if not row:
        log("No queued rows due — nothing to do")
        return 0

    creative_id = row["creative_id"]
    series = row["series"]
    ref_path = REFS_DIR / f"{series}_ref.png"
    if not ref_path.exists():
        log(f"MISSING_REF {series} → {ref_path}. Generate a character portrait first.")
        return 0

    post_cost = COST_PER_BEAT_USD * BEATS_PER_POST
    ok, why = budget_ok(post_cost)
    if not ok:
        log(f"BUDGET_HALT {why}")
        return 0

    log(f"Rendering {creative_id} (series={series}, projected=${post_cost:.2f})")
    if dry_run:
        log("DRY_RUN=true — skipping API calls")
        return 0

    ref_url = row.get("ref_url", "").strip()
    if not ref_url:
        log(f"MISSING ref_url for {creative_id}. Upload {ref_path.name} to a public URL and set the column.")
        return 0

    beat_paths: list[Path] = []
    for i in (1, 2, 3):
        prompt = row[f"beat{i}_prompt"]
        log(f"  beat{i}: {prompt[:80]}")
        out_url = run_prediction({
            "image": ref_url,
            "prompt": prompt,
            "num_frames": 81,
            "resolution": "480p",
            "aspect_ratio": "9:16",
        })
        beat_mp4 = ASSETS_DIR / f"{creative_id}_beat{i}.mp4"
        download(out_url, beat_mp4)
        line = beat_line(prompt, row.get("hook", "")) if i > 1 else row.get("hook", "")
        log(f"  beat{i} voice: {line}")
        voiced = voice_beat(beat_mp4, line, series)
        beat_mp4.unlink(missing_ok=True)
        beat_paths.append(voiced)
        append_cost(creative_id, i, 5, COST_PER_BEAT_USD)

    final = ASSETS_DIR / f"{creative_id}.mp4"
    stitch(beat_paths, final)
    log(f"Rendered {final.name}")

    # Clean intermediates
    for p in beat_paths:
        p.unlink(missing_ok=True)

    # Mark row rendered
    for r in rows:
        if r["creative_id"] == creative_id:
            r["status"] = "rendered"
            r["rendered_at"] = datetime.now(timezone.utc).isoformat()
            break
    write_queue(rows)

    # Bridge: write a scheduled post block so the auto-post workflow picks
    # this MP4 up on its slot hour. Morning=14:00 UTC (09:00 CDT),
    # Evening=22:00 UTC (17:00 CDT), matching this workflow's own cron.
    write_post_block(row, final)

    log("DONE")
    return 0


# ---------------------------------------------------------------------------
# Post-block bridge
# ---------------------------------------------------------------------------
#
# The auto-post scheduler reads brands/<brand>/posts/YYYY-MM-DD.md and fires
# blocks whose header hour matches the current UTC hour. This function writes
# one block per rendered creative so no manual hand-off is needed between the
# renderer and the poster. It fans out to TikTok (@amgriss1 via Buffer),
# Instagram (dkgrissom via Buffer), and Pinterest (Grissompress board via
# Buffer).

SLOT_TO_HOUR = {"morning": 14, "evening": 22}
SLOT_TO_CDT = {"morning": "09:00 CDT", "evening": "17:00 CDT"}

# Fixed hashtag set per character. Kept small and stable so posts read as a
# series rather than a hashtag dump.
SERIES_TAGS = {
    "milo":    "#TalkingCats #OfficeCat #CatTok #FunnyCats #WorkLife",
    "milo2":   "#TalkingCats #OfficeCat #CatTok #FunnyCats #WorkLife",
    "rita":    "#Raccoon #TrashPanda #FunnyAnimals #NeighborhoodDrama",
    "barkley": "#DetectiveDog #GoldenRetriever #NoirComedy #FunnyDogs",
}


def _pinterest_title(series: str, hook: str) -> str:
    """Short Pinterest title — first 90 chars of the hook, series-prefixed."""
    label = {
        "milo": "Milo the Office Cat",
        "milo2": "Milo the Office Cat",
        "rita": "Rita the Raccoon",
        "barkley": "Detective Barkley",
    }.get(series, series.title())
    body = (hook or "").strip().rstrip(".")
    return f"{label}: {body}"[:100]


def write_post_block(row: dict, video_path: Path) -> None:
    """Append a scheduled post block for the rendered MP4.

    Idempotent per creative_id: if a block with the same id already exists in
    the target date file, we do not write a second one. Safe to call on retry.
    """
    creative_id = row["creative_id"]
    scheduled_date = row.get("scheduled_date", "").strip()
    slot = row.get("time_slot", "").strip().lower()
    series = row.get("series", "").strip().lower()
    hook = row.get("hook", "").strip()

    hour = SLOT_TO_HOUR.get(slot)
    if hour is None:
        log(f"POST_BLOCK skipped — unknown time_slot={slot!r}")
        return
    if not scheduled_date:
        log(f"POST_BLOCK skipped — no scheduled_date on {creative_id}")
        return

    # The renderer often runs after its queue slot has passed (it lags the
    # queue by up to a day), and the poster never goes back for past blocks.
    # If the slot is already behind us, post at the next whole UTC hour today.
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    try:
        slot_dt = datetime.strptime(scheduled_date, "%Y-%m-%d").replace(
            hour=hour, tzinfo=timezone.utc)
    except ValueError:
        slot_dt = now
    if slot_dt <= now:
        nxt = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        log(f"POST_BLOCK slot {scheduled_date} {hour:02d}:00 already passed — "
            f"rescheduling to {nxt:%Y-%m-%d %H}:00 UTC")
        scheduled_date, hour = nxt.strftime("%Y-%m-%d"), nxt.hour
    cdt_label = f"{(hour - 5) % 24:02d}:00 CDT"

    # Path is repo-relative, as the poster resolves relative to repo root.
    rel_video = video_path.relative_to(ROOT).as_posix()
    tags = SERIES_TAGS.get(series, "#TalkingAnimals #FunnyAnimals")
    pin_title = _pinterest_title(series, hook)

    posts_dir = ROOT / "brands" / "toolstack" / "posts"
    posts_dir.mkdir(parents=True, exist_ok=True)
    target = posts_dir / f"{scheduled_date}.md"

    marker_id = f"toolstack-{scheduled_date}-{hour:02d}00-{creative_id.lower()}"
    existing = target.read_text() if target.exists() else ""
    if f"CLONE:START id={marker_id}" in existing:
        log(f"POST_BLOCK exists for {creative_id} — no-op")
        return

    header = existing if existing else f"# Toolstack — Animal Shorts — {scheduled_date}\n"
    # `\n## ` splits the block parser's input, so keep exactly that shape.
    block = (
        f"\n<!-- CLONE:START id={marker_id} -->\n"
        f"## {hour:02d}:00 UTC  ({cdt_label})\n"
        # Instagram excluded: our current render pipeline outputs 16 fps but
        # Instagram Posts/Reels require >=23 fps. TikTok is the primary
        # discovery channel for animal shorts anyway; Pinterest kept for pins.
        f"platforms: tiktok, pinterest\n"
        f"video: {rel_video}\n"
        f"image: {rel_video}\n"  # Buffer Pinterest wants an image; MP4 is fine as the media
        f"creative_id: {creative_id}\n"
        f"series: {series}\n"
        f"pinterest_title: {pin_title}\n"
        f"---\n"
        f"{hook}\n\n"
        f"{tags}\n"
        f"---\n"
        f"<!-- CLONE:END -->\n"
    )
    target.write_text(header + block)
    log(f"POST_BLOCK wrote {target.name} for {creative_id} at {hour:02d}:00 UTC")


if __name__ == "__main__":
    sys.exit(main())
