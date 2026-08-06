#!/usr/bin/env python3
"""
Normalize legacy visual drafts (TikTok, IG, Pinterest) into the ingest schema.

Reads clone_drafts/grissom/*.md that predate the current pipeline schema and:
- Fixes kind: post -> kind: social
- Normalizes platform (e.g. instagram-reel -> instagram)
- Adds image:/video: frontmatter pointing to brands/grissom/assets/<slug>.jpg|mp4
- Rewrites the body to just the caption text
- For TikTok: preserves the shot list/voiceover if already present, otherwise
  synthesizes one from the video concept + caption

Idempotent: skips drafts that already have image:/video: fields set.

Usage: python3 scripts/normalize_visual_drafts.py [--dry-run]
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
DRAFTS = ROOT / "clone_drafts" / "grissom"
ASSETS_BASE = "brands/grissom/assets"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> Tuple[dict, str]:
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}, text
    meta_raw, body = m.group(1), m.group(2)
    meta = {}
    for line in meta_raw.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta, body


def emit_frontmatter(meta: dict, body: str) -> str:
    order = ["kind", "brand", "platforms", "scheduled", "filename", "image", "video"]
    lines = ["---"]
    for k in order:
        if k in meta:
            lines.append(f"{k}: {meta[k]}")
    for k, v in meta.items():
        if k not in order:
            lines.append(f"{k}: {v}")
    lines.append("---")
    lines.append("")
    return "\n".join(lines) + body.lstrip("\n")


def extract_caption(body: str) -> str:
    """Pull the caption section — a block under '## Caption' or similar."""
    m = re.search(r"##\s*Caption[^\n]*\n(.*?)(?=\n##|\Z)", body, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    # Fallback: first non-empty paragraph after any # heading
    paras = [p.strip() for p in body.split("\n\n") if p.strip() and not p.strip().startswith("#")]
    return paras[0] if paras else body.strip()


def extract_hashtags(body: str) -> str:
    m = re.search(r"##\s*Hashtags?\s*\n(.*?)(?=\n##|\Z)", body, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return ""


def extract_shot_list(body: str) -> Optional[str]:
    """Preserve existing video concept / shot list if present."""
    parts = []
    for section in ["Video Concept", "Shot List", "Voiceover", "On-screen text", "Music"]:
        m = re.search(rf"##\s*{re.escape(section)}[^\n]*\n(.*?)(?=\n##|\Z)", body, re.DOTALL | re.IGNORECASE)
        if m:
            parts.append(f"## {section}\n{m.group(1).strip()}")
    return "\n\n".join(parts) if parts else None


def synthesize_shot_list(caption: str, video_concept: str = "") -> str:
    """Build a basic shot list scaffold from the caption + video concept."""
    return f"""## Shot list
1. HOOK (0-2s): Cover close-up, morning light through window
2. BEAT (2-5s): Hands on tools, sawdust, wedding-ring detail
3. BEAT (5-9s): Cedar Hollow porch, wide shot
4. PAYOFF (9-12s): Cover reveal with title card
5. CTA (12-15s): "Preorder Sept 8" text + link overlay

## Voiceover
{caption}

## On-screen text
- 0-2s: "Grief does not end. It changes shape."
- 5s: Cedar Hollow, Oklahoma
- 12s: Preorder — September 8

## Music
Sparse acoustic guitar, warm and melancholy — indie folk, no vocals"""


def normalize_platform(plat_raw: str) -> str:
    p = plat_raw.strip().strip("[]").strip()
    p = p.replace("instagram-reel", "instagram").replace("instagram-carousel", "instagram")
    p = p.replace("tiktok-video", "tiktok")
    return f"[{p}]"


def process_file(path: Path, dry_run: bool = False) -> str:
    text = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(text)

    if not meta:
        return "SKIP: no frontmatter"
    if "video" in meta or "image" in meta:
        # Already normalized
        return "SKIP: already normalized"

    platforms = meta.get("platforms", "").lower()
    slug = path.stem  # filename without .md

    # Determine asset type
    is_tiktok = "tiktok" in platforms
    is_ig = "instagram" in platforms
    is_pin = "pinterest" in platforms

    if not (is_tiktok or is_ig or is_pin):
        return "SKIP: not a visual platform"

    # Fix kind
    meta["kind"] = "social"
    meta["platforms"] = normalize_platform(meta.get("platforms", ""))

    # Add asset path
    if is_tiktok:
        meta["video"] = f"{ASSETS_BASE}/{slug}.mp4"
    else:
        meta["image"] = f"{ASSETS_BASE}/{slug}.jpg"

    # Extract caption
    caption = extract_caption(body)
    hashtags = extract_hashtags(body)

    # Rebuild body
    caption_block = caption
    if hashtags and not any(h in caption for h in hashtags.split()[:2]):
        caption_block = caption + "\n\n" + hashtags

    if is_tiktok:
        shot_list = extract_shot_list(body) or synthesize_shot_list(caption)
        new_body = caption_block + "\n\n" + shot_list + "\n"
    else:
        new_body = caption_block + "\n"

    new_text = emit_frontmatter(meta, "\n" + new_body)

    if not dry_run:
        path.write_text(new_text, encoding="utf-8")
    return f"OK: {'tiktok' if is_tiktok else ('ig' if is_ig else 'pin')}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = sorted(DRAFTS.glob("*.md"))
    files = [f for f in files if not f.name.startswith("_")]

    print(f"Processing {len(files)} drafts (dry_run={args.dry_run})\n")
    results = {}
    for f in files:
        r = process_file(f, dry_run=args.dry_run)
        results[r] = results.get(r, 0) + 1
        print(f"  [{r}]  {f.name}")

    print(f"\nSummary:")
    for r, c in sorted(results.items()):
        print(f"  {c}x  {r}")


if __name__ == "__main__":
    main()
