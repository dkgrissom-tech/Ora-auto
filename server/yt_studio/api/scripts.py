"""
POST /api/scripts
Body: { "topic": "...", "hook": "...", "template": "hook-problem-shift-tools-close" }
Returns: { "script": { "hook", "problem", "shift", "tools", "close" }, "estimated_duration_sec": 45 }
"""

import os
import json
import anthropic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

router = APIRouter()
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

TEMPLATES = {
    "hook-problem-shift-tools-close": {
        "sections": ["hook", "problem", "shift", "tools", "close"],
        "target_words": {"hook": 20, "problem": 40, "shift": 30, "tools": 60, "close": 25},
    },
    "listicle": {
        "sections": ["hook", "item1", "item2", "item3", "close"],
        "target_words": {"hook": 20, "item1": 35, "item2": 35, "item3": 35, "close": 20},
    },
    "story": {
        "sections": ["hook", "setup", "conflict", "resolution", "cta"],
        "target_words": {"hook": 20, "setup": 50, "conflict": 50, "resolution": 40, "cta": 20},
    }
}


class ScriptRequest(BaseModel):
    topic: str
    hook: Optional[str] = ""
    template: Optional[str] = "hook-problem-shift-tools-close"
    brand_voice: Optional[str] = "conversational, warm, direct — no fluff"


@router.post("/scripts")
def generate_script(req: ScriptRequest):
    tmpl = TEMPLATES.get(req.template, TEMPLATES["hook-problem-shift-tools-close"])
    sections = tmpl["sections"]
    word_targets = tmpl["target_words"]

    section_instructions = "\n".join([
        f'- "{s}": ~{word_targets.get(s, 30)} words' for s in sections
    ])

    prompt = f"""You are a short-form video scriptwriter. Brand voice: {req.brand_voice}.

Write a short video script for the topic: "{req.topic}"
{f'Opening hook line to use or riff on: "{req.hook}"' if req.hook else ''}

Template: {req.template}
Sections and word targets:
{section_instructions}

Rules:
- Each section is read aloud on screen — write for speech, not reading
- No filler phrases ("In today's video...", "Don't forget to like...")
- Every sentence earns its place or gets cut
- The hook must create a pattern interrupt in the first 3 words

Respond with ONLY valid JSON:
{{
  {', '.join([f'"{s}": "..."' for s in sections])},
  "estimated_duration_sec": 45
}}"""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        return {"script": data, "estimated_duration_sec": data.get("estimated_duration_sec", 45)}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Claude returned invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
