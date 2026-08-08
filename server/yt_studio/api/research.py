"""
POST /api/research
Body: { "niche": "romance authors", "profession": "indie novelist" }
Returns: { "topics": [ { "title", "hook", "score" }, ... ] }
"""

import os
import json
import anthropic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


class ResearchRequest(BaseModel):
    niche: str
    profession: Optional[str] = ""
    count: Optional[int] = 10


@router.post("/research")
def research(req: ResearchRequest):
    prompt = f"""You are a YouTube content strategist. Generate {req.count} high-potential video topic ideas for a creator in the "{req.niche}" niche{f', specifically a {req.profession}' if req.profession else ''}.

For each topic return:
- title: the video title (punchy, specific, under 70 chars)
- hook: the first sentence that will appear on screen (under 15 words, creates urgency or curiosity)
- score: virality score 1-10 based on search volume potential and emotional pull

Respond with ONLY valid JSON, no markdown, no explanation:
{{
  "topics": [
    {{"title": "...", "hook": "...", "score": 8}},
    ...
  ]
}}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        # Strip accidental markdown fences
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        return data
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Claude returned invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
