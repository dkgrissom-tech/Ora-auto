"""
POST /api/video   — submit video render job
GET  /api/video/:job_id — poll job status

Video rendering uses Remotion (headless) or ffmpeg depending on template.
Jobs run async in a background thread; status stored in memory dict.

In production: use a proper job queue (Redis/Bull). For Replit Autoscale,
in-memory is fine since renders complete in <5 min.
"""

import os
import uuid
import time
import json
import subprocess
import threading
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

# In-memory job store: { job_id: { status, video_url, error, started_at } }
jobs: dict = {}

VIDEO_DIR = Path("/tmp/videos")
VIDEO_DIR.mkdir(exist_ok=True)

TEMPLATES = ["scrolling-text-gradient", "minimal-dark", "bold-yellow", "neon-outline"]
BASE_URL = os.environ.get("API_BASE_URL", "https://yt-studio-grissom.replit.app")


class VideoRequest(BaseModel):
    script_text: str
    audio_url: str
    timestamps: Optional[List[dict]] = []
    template: Optional[str] = "scrolling-text-gradient"
    aspect: Optional[str] = "9:16"


def render_video_worker(job_id: str, req_data: dict):
    """Background worker: renders video using ffmpeg + generated subtitles."""
    try:
        jobs[job_id]["status"] = "rendering"

        script_text = req_data["script_text"]
        audio_url = req_data["audio_url"]
        template = req_data.get("template", "scrolling-text-gradient")
        aspect = req_data.get("aspect", "9:16")

        # Determine dimensions
        if aspect == "9:16":
            width, height = 1080, 1920
        elif aspect == "1:1":
            width, height = 1080, 1080
        else:  # 16:9
            width, height = 1920, 1080

        output_path = VIDEO_DIR / f"{job_id}.mp4"

        # Download audio to local file
        audio_path = Path(f"/tmp/{job_id}_audio.mp3")
        import httpx
        with httpx.Client(timeout=30) as client:
            r = client.get(audio_url)
            r.raise_for_status()
            audio_path.write_bytes(r.content)

        # Build SRT subtitle file from timestamps
        srt_path = Path(f"/tmp/{job_id}.srt")
        timestamps = req_data.get("timestamps", [])
        if timestamps:
            srt_lines = []
            for i, ts in enumerate(timestamps, 1):
                start = _sec_to_srt(ts.get("start", 0))
                end = _sec_to_srt(ts.get("end", ts.get("start", 0) + 0.5))
                srt_lines.append(f"{i}\n{start} --> {end}\n{ts.get('word', '')}\n")
            srt_path.write_text("\n".join(srt_lines))
        else:
            # No timestamps: show full text as single block
            srt_path.write_text(f"1\n00:00:00,000 --> 00:00:30,000\n{script_text[:200]}\n")

        # Choose background color based on template
        bg_color = {
            "scrolling-text-gradient": "0x1a1a2e",
            "minimal-dark": "0x0d0d0d",
            "bold-yellow": "0xffd700",
            "neon-outline": "0x000000"
        }.get(template, "0x1a1a2e")

        font_color = "0xffd700" if template != "bold-yellow" else "0x000000"

        # ffmpeg command: colored background + subtitles + audio
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={bg_color}:size={width}x{height}:rate=30",
            "-i", str(audio_path),
            "-vf", (
                f"subtitles={srt_path}:force_style='"
                f"FontSize=72,FontName=Arial Bold,PrimaryColour=&H{font_color[2:]}&,"
                f"Alignment=10,MarginV=100'"
            ),
            "-shortest",
            "-c:v", "libx264",
            "-c:a", "aac",
            "-preset", "fast",
            "-crf", "23",
            str(output_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

        if result.returncode != 0:
            raise RuntimeError(f"ffmpeg failed: {result.stderr[-500:]}")

        video_url = f"{BASE_URL}/api/video-file/{job_id}"
        jobs[job_id].update({
            "status": "done",
            "video_url": video_url,
            "completed_at": time.time()
        })

    except Exception as e:
        jobs[job_id].update({
            "status": "failed",
            "error": str(e),
            "failed_at": time.time()
        })


def _sec_to_srt(seconds: float) -> str:
    """Convert float seconds to SRT timestamp format HH:MM:SS,mmm."""
    ms = int((seconds % 1) * 1000)
    s = int(seconds) % 60
    m = int(seconds) // 60 % 60
    h = int(seconds) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


@router.post("/video")
def submit_video_job(req: VideoRequest):
    job_id = str(uuid.uuid4())
    jobs[job_id] = {
        "status": "queued",
        "video_url": None,
        "error": None,
        "started_at": time.time()
    }
    thread = threading.Thread(
        target=render_video_worker,
        args=(job_id, req.dict()),
        daemon=True
    )
    thread.start()
    return {"job_id": job_id, "status": "queued"}


@router.get("/video/{job_id}")
def get_video_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return jobs[job_id]


@router.get("/video-file/{job_id}")
def serve_video(job_id: str):
    from fastapi.responses import FileResponse
    video_path = VIDEO_DIR / f"{job_id}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    return FileResponse(str(video_path), media_type="video/mp4")
