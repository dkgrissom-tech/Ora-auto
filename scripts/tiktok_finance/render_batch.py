#!/usr/bin/env python3
"""Bulk render TikTok finance shorts via short-video-maker (running in Docker sidecar).

Reads scripts.yaml, hits the local short-video-maker API for each script,
polls until each render completes, downloads the MP4 to out/, and writes
captions.md with copy-paste captions + hashtags for TikTok Studio upload.
"""
from __future__ import annotations

import os
import sys
import time
import json
import pathlib
import subprocess
import urllib.request
import urllib.error

import yaml

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)

API = os.environ.get("SVM_API", "http://localhost:3123")
SCRIPTS_PATH = HERE / "scripts.yaml"
POLL_INTERVAL = 5
TIMEOUT = 900  # 15 min per video


def post_json(url: str, body: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def get_status(video_id: str) -> str:
    with urllib.request.urlopen(f"{API}/api/short-video/{video_id}/status", timeout=30) as r:
        return json.loads(r.read()).get("status", "unknown")


def download_video(video_id: str, out_path: pathlib.Path) -> None:
    url = f"{API}/api/short-video/{video_id}"
    with urllib.request.urlopen(url, timeout=120) as r, open(out_path, "wb") as f:
        while chunk := r.read(64 * 1024):
            f.write(chunk)


def render_one(script: dict) -> pathlib.Path | None:
    sid = script["id"]
    scenes_payload = [
        {"text": s["text"], "searchTerms": s["search_terms"]}
        for s in script["scenes"]
    ]
    body = {
        "scenes": scenes_payload,
        "config": {
            "paddingBack": 1500,
            "music": "chill",
            "captionPosition": "center",
            "captionBackgroundColor": "yellow",
            "voice": "am_michael",  # confident male
            "orientation": "portrait",
            "musicVolume": "low",
        },
    }
    print(f"→ submitting {sid}...", flush=True)
    try:
        resp = post_json(f"{API}/api/short-video", body)
    except urllib.error.HTTPError as e:
        print(f"  ✗ submit failed: {e.code} {e.reason}\n  {e.read().decode()[:400]}", flush=True)
        return None

    video_id = resp.get("videoId")
    if not video_id:
        print(f"  ✗ no videoId in response: {resp}", flush=True)
        return None
    print(f"  videoId: {video_id}", flush=True)

    # Poll for completion
    start = time.time()
    while time.time() - start < TIMEOUT:
        try:
            status = get_status(video_id)
        except Exception as e:
            print(f"  ⚠ status poll error: {e}", flush=True)
            time.sleep(POLL_INTERVAL)
            continue
        if status == "ready":
            break
        if status == "failed":
            print(f"  ✗ render failed for {sid}", flush=True)
            return None
        print(f"  ...status={status} ({int(time.time()-start)}s)", flush=True)
        time.sleep(POLL_INTERVAL)
    else:
        print(f"  ✗ timeout for {sid}", flush=True)
        return None

    out_path = OUT / f"{sid}.mp4"
    download_video(video_id, out_path)
    print(f"  ✓ saved {out_path.name} ({out_path.stat().st_size // 1024} KB)", flush=True)
    return out_path


def wait_for_api(max_seconds: int = 600) -> bool:
    """Wait for short-video-maker to be reachable. Uses /api/music-tags as liveness probe."""
    print(f"waiting for {API} ...", flush=True)
    start = time.time()
    last_err = ""
    while time.time() - start < max_seconds:
        try:
            with urllib.request.urlopen(f"{API}/api/music-tags", timeout=5) as r:
                if r.status == 200:
                    print(f"  ✓ API ready in {int(time.time()-start)}s", flush=True)
                    return True
        except Exception as e:
            last_err = str(e)[:120]
        elapsed = int(time.time() - start)
        if elapsed % 30 < 5:
            print(f"  ...still waiting ({elapsed}s) — last: {last_err}", flush=True)
        time.sleep(5)
    print(f"  ✗ API never came up (last error: {last_err})", flush=True)
    return False


def main() -> int:
    if not wait_for_api():
        return 1

    scripts = yaml.safe_load(SCRIPTS_PATH.read_text())
    limit = int(os.environ.get("RENDER_LIMIT", "0") or 0)
    if limit > 0:
        scripts = scripts[:limit]
    print(f"loaded {len(scripts)} scripts (limit={limit})", flush=True)

    captions_lines = ["# TikTok Captions — @toolstack-y4g\n"]
    captions_lines.append("Upload each MP4 below to TikTok Studio, then paste the caption + hashtags.\n")

    rendered = 0
    for script in scripts:
        result = render_one(script)
        captions_lines.append(f"\n## {script['id']} — {script['title']}\n")
        if result:
            captions_lines.append(f"File: `{result.name}`\n")
            rendered += 1
        else:
            captions_lines.append(f"File: (render failed — see logs)\n")
        captions_lines.append(f"\n**Caption:** {script['caption']}\n")
        captions_lines.append(f"\n**Hashtags:** `{script['hashtags']}`\n")

    (OUT / "captions.md").write_text("".join(captions_lines))
    print(f"\n=== {rendered}/{len(scripts)} rendered ===", flush=True)
    return 0 if rendered > 0 else 1


if __name__ == "__main__":
    sys.exit(main())
