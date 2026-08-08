"""
POST /api/voice
Body: { "script_text": "...", "voice_id": "elevenlabs-voice-id" }
Returns: { "audio_url": "...", "timestamps": [ { "word", "start", "end" }, ... ] }

ElevenLabs API: https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps
Audio is base64-encoded in the response — we write it to /tmp and serve it.
In production, upload to R2/S3 and return that URL instead.
"""

import os
import uuid
import json
import base64
import httpx
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
DEFAULT_VOICE_ID = os.environ.get("ELEVENLABS_DEFAULT_VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # Adam
AUDIO_DIR = Path("/tmp/audio")
AUDIO_DIR.mkdir(exist_ok=True)


class VoiceRequest(BaseModel):
    script_text: str
    voice_id: Optional[str] = None
    stability: Optional[float] = 0.5
    similarity_boost: Optional[float] = 0.75


@router.post("/voice")
def generate_voice(req: VoiceRequest):
    if not ELEVENLABS_API_KEY:
        raise HTTPException(status_code=500, detail="ELEVENLABS_API_KEY not set")

    voice_id = req.voice_id or DEFAULT_VOICE_ID
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/with-timestamps"

    payload = {
        "text": req.script_text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": req.stability,
            "similarity_boost": req.similarity_boost
        }
    }

    headers = {
        "xi-api-key": ELEVENLABS_API_KEY,
        "Content-Type": "application/json"
    }

    try:
        with httpx.Client(timeout=60) as client:
            resp = client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=502, detail=f"ElevenLabs error: {e.response.text}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Save audio to /tmp
    audio_bytes = base64.b64decode(data.get("audio_base64", ""))
    audio_id = str(uuid.uuid4())
    audio_path = AUDIO_DIR / f"{audio_id}.mp3"
    audio_path.write_bytes(audio_bytes)

    # Build timestamps list from ElevenLabs alignment data
    alignment = data.get("alignment", {})
    chars = alignment.get("characters", [])
    starts = alignment.get("character_start_times_seconds", [])
    ends = alignment.get("character_end_times_seconds", [])

    # Group into word-level timestamps (rough grouping by spaces)
    timestamps = []
    current_word = ""
    word_start = 0.0
    for i, char in enumerate(chars):
        if char == " " or i == len(chars) - 1:
            if current_word:
                timestamps.append({
                    "word": current_word,
                    "start": round(word_start, 3),
                    "end": round(ends[i - 1] if i > 0 else 0.0, 3)
                })
            current_word = ""
            word_start = starts[i + 1] if i + 1 < len(starts) else 0.0
        else:
            if not current_word:
                word_start = starts[i] if i < len(starts) else 0.0
            current_word += char

    # In production: upload audio_path to R2/S3, return CDN URL
    # For now: serve from /tmp via /api/audio/<id>
    base_url = os.environ.get("API_BASE_URL", "https://yt-studio-grissom.replit.app")
    audio_url = f"{base_url}/api/audio/{audio_id}"

    return {
        "audio_url": audio_url,
        "audio_id": audio_id,
        "timestamps": timestamps,
        "duration_sec": ends[-1] if ends else 0.0
    }


@router.get("/audio/{audio_id}")
def serve_audio(audio_id: str):
    """Serve generated audio file from /tmp."""
    audio_path = AUDIO_DIR / f"{audio_id}.mp3"
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(str(audio_path), media_type="audio/mpeg")
