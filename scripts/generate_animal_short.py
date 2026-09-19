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
        "-c:v", "libx264", "-crf", "20", "-preset", "fast",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
        "-movflags", "+faststart",
        str(out),
    ]
    subprocess.run(cmd, check=True, cwd=out.parent, capture_output=True)
    concat.unlink()


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
        beat_paths.append(beat_mp4)
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

    log("DONE")
    return 0


if __name__ == "__main__":
    sys.exit(main())
