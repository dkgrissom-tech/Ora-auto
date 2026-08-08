"""
GET /api/video/:job_id  — poll render job status
GET /api/video-file/:job_id — serve rendered video

Import this router into the CIG FastAPI app alongside generate.py
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

try:
    from . import jobstore
    from .generate import VIDEO_DIR, check_api_key
except ImportError:  # running flat on Replit (cwd = project root)
    import jobstore
    from generate import VIDEO_DIR, check_api_key

router = APIRouter()


@router.get("/video/{job_id}")
def get_video_status(job_id: str, request: Request):
    check_api_key(request)
    record = jobstore.get(job_id)
    if record is None:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return record


@router.get("/video-file/{job_id}")
def serve_video(job_id: str, request: Request):
    check_api_key(request)
    video_path = VIDEO_DIR / f"{job_id}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not ready or not found")
    return FileResponse(str(video_path), media_type="video/mp4")


@router.get("/health")
def health():
    return {
        "status": "ok",
        "service": "content-ideas-generator-api",
        "jobs": jobstore.count(),
    }
