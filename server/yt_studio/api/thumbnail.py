"""
POST /api/thumbnail
Body: { "template": "viral-yellow", "headline": "...", "sub": "...", "badge": "NEW" }
Returns: { "thumbnail_url": "..." }

Generates YouTube thumbnail using Pillow (PIL).
Templates: viral-yellow, dark-bold, clean-white, grissom-press
"""

import os
import uuid
import base64
from io import BytesIO
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

THUMB_DIR = Path("/tmp/thumbnails")
THUMB_DIR.mkdir(exist_ok=True)
BASE_URL = os.environ.get("API_BASE_URL", "https://yt-studio-grissom.replit.app")

TEMPLATES = {
    "viral-yellow": {"bg": (255, 215, 0), "text": (0, 0, 0), "accent": (220, 0, 0)},
    "dark-bold": {"bg": (13, 13, 13), "text": (255, 255, 255), "accent": (255, 215, 0)},
    "clean-white": {"bg": (255, 255, 255), "text": (30, 30, 30), "accent": (0, 120, 255)},
    "grissom-press": {"bg": (26, 26, 46), "text": (255, 215, 0), "accent": (200, 50, 50)},
}


class ThumbnailRequest(BaseModel):
    template: Optional[str] = "viral-yellow"
    headline: str
    sub: Optional[str] = ""
    badge: Optional[str] = ""  # e.g. "NEW", "PART 2", "VIRAL"


@router.post("/thumbnail")
def generate_thumbnail(req: ThumbnailRequest):
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        raise HTTPException(
            status_code=500,
            detail="Pillow not installed. Run: pip install Pillow --break-system-packages"
        )

    tmpl = TEMPLATES.get(req.template, TEMPLATES["viral-yellow"])
    bg_color = tmpl["bg"]
    text_color = tmpl["text"]
    accent_color = tmpl["accent"]

    # YouTube thumbnail: 1280x720
    img = Image.new("RGB", (1280, 720), bg_color)
    draw = ImageDraw.Draw(img)

    # Try to load a bold font; fall back to default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 96)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 52)
        font_badge = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except Exception:
        font_large = ImageFont.load_default()
        font_medium = font_large
        font_badge = font_large

    # Draw badge (top-right pill)
    if req.badge:
        badge_text = req.badge.upper()
        bbox = draw.textbbox((0, 0), badge_text, font=font_badge)
        bw = bbox[2] - bbox[0] + 40
        bh = bbox[3] - bbox[1] + 20
        bx, by = 1280 - bw - 30, 30
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12, fill=accent_color)
        draw.text((bx + 20, by + 10), badge_text, fill=(255, 255, 255), font=font_badge)

    # Draw headline (center, wrapped at ~20 chars)
    headline_lines = _wrap_text(req.headline, 20)
    y_offset = 200
    for line in headline_lines:
        bbox = draw.textbbox((0, 0), line, font=font_large)
        tw = bbox[2] - bbox[0]
        draw.text(((1280 - tw) / 2, y_offset), line, fill=text_color, font=font_large)
        y_offset += 110

    # Draw sub text
    if req.sub:
        sub_lines = _wrap_text(req.sub, 32)
        for line in sub_lines:
            bbox = draw.textbbox((0, 0), line, font=font_medium)
            tw = bbox[2] - bbox[0]
            draw.text(((1280 - tw) / 2, y_offset + 20), line, fill=accent_color, font=font_medium)
            y_offset += 65

    # Add bottom accent bar
    draw.rectangle([0, 680, 1280, 720], fill=accent_color)

    # Save
    thumb_id = str(uuid.uuid4())
    thumb_path = THUMB_DIR / f"{thumb_id}.jpg"
    img.save(str(thumb_path), "JPEG", quality=95)

    thumbnail_url = f"{BASE_URL}/api/thumbnail-file/{thumb_id}"
    return {"thumbnail_url": thumbnail_url, "thumbnail_id": thumb_id}


@router.get("/thumbnail-file/{thumb_id}")
def serve_thumbnail(thumb_id: str):
    thumb_path = THUMB_DIR / f"{thumb_id}.jpg"
    if not thumb_path.exists():
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(str(thumb_path), media_type="image/jpeg")


def _wrap_text(text: str, max_chars: int) -> list:
    words = text.split()
    lines, current = [], ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current = (current + " " + word).strip()
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines
