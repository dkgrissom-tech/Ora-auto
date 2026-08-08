"""
Content Ideas Generator API
POST /api/generate-video
GET  /api/video/:job_id

Wraps the existing Remotion renderer. Add this file to the CIG Replit project
alongside the existing Remotion compositions.

Env vars needed in CIG Replit Secrets:
  CIG_API_KEY        (UUID you generate, mirror to n8n)
  ELEVENLABS_API_KEY (for voice synthesis)
  API_BASE_URL       (https://content-ideas-grissom.replit.app after deploy)
"""

import hmac
import os
import uuid
import time
import json
import subprocess
import threading
from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

try:
    from . import jobstore
except ImportError:  # running flat on Replit (cwd = project root)
    import jobstore

router = APIRouter()

# Rendered files must survive a container restart, same as the job store.
VIDEO_DIR = Path(os.environ.get("CIG_VIDEO_DIR", "/tmp/cig_videos"))
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

BASE_URL = os.environ.get("API_BASE_URL", "https://content-ideas-grissom.replit.app")


def check_api_key(request: Request):
    """Call this at the top of each endpoint.

    Reads the env var per request rather than at import time so a key added
    after boot takes effect on restart-free redeploys, and compares in constant
    time so the endpoint can't be used as a timing oracle.
    """
    expected = os.environ.get("CIG_API_KEY", "")
    key = request.headers.get("X-API-Key", "")
    if not expected:
        raise HTTPException(status_code=500, detail="CIG_API_KEY env var not set")
    if not hmac.compare_digest(key, expected):
        raise HTTPException(status_code=401, detail="Invalid X-API-Key")


class BeatScene(BaseModel):
    scene_type: str  # "title" | "stat" | "quote" | "callout"
    text: str
    duration_sec: Optional[float] = 3.0
    bg_color: Optional[str] = ""
    text_color: Optional[str] = ""


class GenerateVideoRequest(BaseModel):
    beat_sheet: List[BeatScene]
    voice_id: Optional[str] = ""
    aspect: Optional[str] = "9:16"  # "16:9" | "9:16" | "1:1"
    music_mood: Optional[str] = "warm"  # "warm" | "energetic" | "calm"


def render_cig_video_worker(job_id: str, req_data: dict):
    """Background worker: calls Remotion CLI to render the beat sheet."""
    try:
        jobstore.update(job_id, {"status": "rendering"})

        beat_sheet = req_data["beat_sheet"]
        aspect = req_data.get("aspect", "9:16")
        music_mood = req_data.get("music_mood", "warm")
        voice_id = req_data.get("voice_id", "")

        # Determine dimensions for Remotion
        if aspect == "9:16":
            width, height = 1080, 1920
        elif aspect == "1:1":
            width, height = 1080, 1080
        else:
            width, height = 1920, 1080

        output_path = VIDEO_DIR / f"{job_id}.mp4"

        # Write beat sheet to a temp JSON file that Remotion reads as props
        props_path = Path(f"/tmp/{job_id}_props.json")
        props_data = {
            "beatSheet": beat_sheet,
            "aspect": aspect,
            "musicMood": music_mood,
            "voiceId": voice_id,
            "width": width,
            "height": height
        }
        props_path.write_text(json.dumps(props_data))

        # Remotion render command
        # Assumes Remotion project is at /home/user/remotion in Replit
        # Composition ID: "BeatSheetVideo" (you need to add this composition)
        remotion_dir = os.environ.get("REMOTION_DIR", "/home/user/remotion")
        cmd = [
            "npx", "remotion", "render",
            "BeatSheetVideo",
            str(output_path),
            f"--props={props_path}",
            f"--width={width}",
            f"--height={height}",
            "--codec=h264",
            "--log=error"
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600,
            cwd=remotion_dir
        )

        if result.returncode != 0:
            raise RuntimeError(f"Remotion render failed: {result.stderr[-800:]}")

        video_url = f"{BASE_URL}/api/video-file/{job_id}"
        jobstore.update(job_id, {
            "status": "done",
            "video_url": video_url,
            "completed_at": time.time()
        })

    except Exception as e:
        jobstore.update(job_id, {
            "status": "failed",
            "error": str(e),
            "failed_at": time.time()
        })


@router.post("/generate-video")
def generate_video(req: GenerateVideoRequest, request: Request):
    check_api_key(request)
    job_id = str(uuid.uuid4())
    jobstore.create(job_id)
    thread = threading.Thread(
        target=render_cig_video_worker,
        args=(job_id, req.dict()),
        daemon=True
    )
    thread.start()
    return {"job_id": job_id, "status": "queued"}
