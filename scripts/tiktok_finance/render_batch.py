#!/usr/bin/env python3
"""Bulk render TikTok finance shorts — pure Python, no Docker.

Pipeline per script:
1. edge-tts: neural male voice → MP3 per scene
2. Pexels API: portrait video search per scene → MP4 clip
3. moviepy: trim B-roll to voice length, add centered caption, concat scenes
4. Output 9:16 1080x1920 MP4

Reads scripts.yaml, writes out/*.mp4 + captions.md.
"""
from __future__ import annotations

import asyncio
import json
import os
import pathlib
import random
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request

import edge_tts
import yaml
from moviepy import (
    AudioFileClip,
    ColorClip,
    CompositeVideoClip,
    TextClip,
    VideoFileClip,
    concatenate_videoclips,
)
from moviepy.video.fx.Loop import Loop

HERE = pathlib.Path(__file__).parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)
CACHE = HERE / ".cache"
CACHE.mkdir(exist_ok=True)

PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")
if not PEXELS_KEY:
    print("FATAL: PEXELS_API_KEY not set", file=sys.stderr)
    sys.exit(1)

# Confident male US voice — Edge-TTS neural
VOICE = "en-US-GuyNeural"
TARGET_W, TARGET_H = 1080, 1920
FONT = "DejaVu-Sans-Bold"  # available on ubuntu runners


def pexels_search_video(query: str, per_page: int = 10) -> list[dict]:
    """Search Pexels for portrait videos matching query."""
    url = (
        "https://api.pexels.com/videos/search?"
        f"query={urllib.parse.quote(query)}&per_page={per_page}&orientation=portrait"
    )
    req = urllib.request.Request(url, headers={"Authorization": PEXELS_KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read()).get("videos", [])


def pick_pexels_clip(search_terms: list[str]) -> str | None:
    """Pick a random matching Pexels video and download it. Returns local path."""
    for term in search_terms:
        vids = pexels_search_video(term, per_page=15)
        if not vids:
            continue
        random.shuffle(vids)
        for v in vids:
            # Pick a video file at HD or SD, prefer portrait
            files = sorted(
                [f for f in v.get("video_files", []) if f.get("width") and f.get("height")],
                key=lambda f: abs(f["height"] / max(f["width"], 1) - TARGET_H / TARGET_W),
            )
            if not files:
                continue
            vf = files[0]
            local = CACHE / f"pexels_{v['id']}_{vf['id']}.mp4"
            if not local.exists():
                print(f"    ↓ Pexels {v['id']} ({vf['width']}x{vf['height']})", flush=True)
                try:
                    urllib.request.urlretrieve(vf["link"], local)
                except Exception as e:
                    print(f"    ✗ download failed: {e}", flush=True)
                    continue
            if local.stat().st_size < 10_000:
                local.unlink(missing_ok=True)
                continue
            return str(local)
    # Fallback: generic
    for term in ["business", "finance", "money", "office"]:
        vids = pexels_search_video(term, per_page=5)
        if vids:
            v = vids[0]
            files = v.get("video_files", [])
            if files:
                vf = files[0]
                local = CACHE / f"pexels_fb_{v['id']}.mp4"
                if not local.exists():
                    urllib.request.urlretrieve(vf["link"], local)
                return str(local)
    return None


async def tts_scene(text: str, out_path: pathlib.Path) -> None:
    """Generate MP3 for one scene via Edge TTS."""
    communicate = edge_tts.Communicate(text, VOICE, rate="+8%")
    await communicate.save(str(out_path))


def build_scene_clip(text: str, audio_path: pathlib.Path, video_path: str) -> VideoFileClip:
    """Build one scene: video B-roll trimmed to audio length + centered caption."""
    audio = AudioFileClip(str(audio_path))
    dur = audio.duration

    video = VideoFileClip(video_path).without_audio()

    # Loop or trim video to match audio duration
    if video.duration < dur:
        loops_needed = int(dur / video.duration) + 1
        video = concatenate_videoclips([video] * loops_needed)
    video = video.subclipped(0, dur)

    # Resize/crop to 1080x1920 (portrait). Fit height, crop width if wide.
    vw, vh = video.size
    target_ratio = TARGET_W / TARGET_H
    cur_ratio = vw / vh
    if cur_ratio > target_ratio:
        # too wide — scale by height then crop width
        new_h = TARGET_H
        new_w = int(vw * (TARGET_H / vh))
        video = video.resized((new_w, new_h))
        x_center = new_w // 2
        video = video.cropped(x_center=x_center, y_center=new_h // 2, width=TARGET_W, height=TARGET_H)
    else:
        # too tall — scale by width then crop height
        new_w = TARGET_W
        new_h = int(vh * (TARGET_W / vw))
        video = video.resized((new_w, new_h))
        video = video.cropped(x_center=new_w // 2, y_center=new_h // 2, width=TARGET_W, height=TARGET_H)

    # Caption: yellow bold text, centered, with dark background box
    caption = (
        TextClip(
            text=text,
            font_size=68,
            color="yellow",
            font="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            stroke_color="black",
            stroke_width=4,
            method="caption",
            size=(int(TARGET_W * 0.88), None),
            text_align="center",
        )
        .with_duration(dur)
        .with_position(("center", "center"))
    )

    composite = CompositeVideoClip([video, caption]).with_audio(audio)
    return composite


def render_script(script: dict) -> pathlib.Path | None:
    sid = script["id"]
    print(f"\n=== {sid}: {script['title']} ===", flush=True)
    tmpdir = pathlib.Path(tempfile.mkdtemp(prefix=f"scene_{sid}_"))
    try:
        scene_clips = []
        for i, scene in enumerate(script["scenes"]):
            text = scene["text"]
            print(f"  scene {i+1}/{len(script['scenes'])}: {text[:60]}...", flush=True)

            # 1. TTS
            audio_path = tmpdir / f"scene_{i:02d}.mp3"
            try:
                asyncio.run(tts_scene(text, audio_path))
            except Exception as e:
                print(f"    ✗ tts failed: {e}", flush=True)
                return None

            # 2. B-roll
            video_path = pick_pexels_clip(scene["search_terms"])
            if not video_path:
                print(f"    ✗ no Pexels clip found", flush=True)
                return None

            # 3. Composite scene
            try:
                clip = build_scene_clip(text, audio_path, video_path)
                scene_clips.append(clip)
            except Exception as e:
                print(f"    ✗ compose failed: {e}", flush=True)
                return None

        # Concatenate all scenes
        print(f"  concatenating {len(scene_clips)} scenes...", flush=True)
        final = concatenate_videoclips(scene_clips, method="compose")

        out_path = OUT / f"{sid}.mp4"
        final.write_videofile(
            str(out_path),
            fps=30,
            codec="libx264",
            audio_codec="aac",
            preset="fast",
            threads=2,
            logger=None,
        )
        print(f"  ✓ wrote {out_path.name} ({out_path.stat().st_size // 1024} KB)", flush=True)
        return out_path
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main() -> int:
    scripts_path = HERE / "scripts.yaml"
    scripts = yaml.safe_load(scripts_path.read_text())
    limit = int(os.environ.get("RENDER_LIMIT", "0") or 0)
    if limit > 0:
        scripts = scripts[:limit]
    print(f"loaded {len(scripts)} scripts (limit={limit})", flush=True)

    captions_lines = [
        "# TikTok Captions — @toolstack-y4g\n\n",
        "Upload each MP4 below to TikTok Studio, then paste the caption + hashtags.\n",
    ]

    rendered = 0
    for script in scripts:
        result = render_script(script)
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
