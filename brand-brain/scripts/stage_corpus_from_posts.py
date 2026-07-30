#!/usr/bin/env python3
"""
One-shot: extract post bodies from brands/<brand>/posts/YYYY-MM-DD.md files
into brand-brain/brands/<persona>/corpus/social/ as individual .md files.

Each post block in the source looks like:

    ## 14:00 UTC  (09:00 CDT)
    platforms: bluesky, linkedin, threads
    image: ...
    ---
    Body of the post.
    ---

This script writes one file per block:
    corpus/social/<date>-<hour>utc-<platforms>.md

with a YAML front-matter header preserving the metadata so build_brain.py
can see platform, date, and asset context alongside the body text.

Usage:
  python brand-brain/scripts/stage_corpus_from_posts.py \\
    --brand ora --persona zara --since 2026-07-19 --until 2026-07-25
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BLOCK_HEADER_RE = re.compile(r"^##\s+(\d{1,2}):(\d{2})\s+UTC\b", re.MULTILINE)


def parse_blocks(md_text: str) -> list[dict]:
    """Split a post file into blocks. Each block = one scheduled post."""
    blocks = []
    matches = list(BLOCK_HEADER_RE.finditer(md_text))
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
        chunk = md_text[start:end].rstrip()

        hour = int(m.group(1))
        # Metadata lines between "## HH:MM UTC ..." and the first "---"
        lines = chunk.splitlines()
        # Skip header line
        meta_lines = []
        body_lines = []
        seen_first_sep = False
        seen_second_sep = False
        for ln in lines[1:]:
            if ln.strip() == "---":
                if not seen_first_sep:
                    seen_first_sep = True
                    continue
                if not seen_second_sep:
                    seen_second_sep = True
                    continue
            if not seen_first_sep:
                if ln.strip():
                    meta_lines.append(ln.strip())
            elif not seen_second_sep:
                body_lines.append(ln)

        meta = {}
        for ml in meta_lines:
            if ":" in ml:
                k, v = ml.split(":", 1)
                meta[k.strip().lower()] = v.strip()

        platforms = [p.strip() for p in meta.get("platforms", "").split(",") if p.strip()]
        body = "\n".join(body_lines).strip()
        if not body:
            continue
        blocks.append({
            "hour_utc": hour,
            "platforms": platforms,
            "image": meta.get("image", ""),
            "video": meta.get("video", ""),
            "body": body,
        })
    return blocks


def in_range(d: date, since: date | None, until: date | None) -> bool:
    if since and d < since:
        return False
    if until and d > until:
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True, help="Source brand under brands/ (e.g. ora)")
    ap.add_argument("--persona", required=True, help="Target persona under brand-brain/brands/ (e.g. zara)")
    ap.add_argument("--since", default="", help="Optional YYYY-MM-DD lower bound (inclusive)")
    ap.add_argument("--until", default="", help="Optional YYYY-MM-DD upper bound (inclusive)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    src_dir = REPO_ROOT / "brands" / args.brand / "posts"
    dst_dir = REPO_ROOT / "brand-brain" / "brands" / args.persona / "corpus" / "social"
    if not src_dir.exists():
        sys.exit(f"[stage] No source posts dir at {src_dir}")
    dst_dir.mkdir(parents=True, exist_ok=True)

    since = date.fromisoformat(args.since) if args.since else None
    until = date.fromisoformat(args.until) if args.until else None

    written = 0
    for src in sorted(src_dir.glob("*.md")):
        try:
            file_date = date.fromisoformat(src.stem)
        except ValueError:
            print(f"[stage] skip non-dated file {src.name}")
            continue
        if not in_range(file_date, since, until):
            continue

        blocks = parse_blocks(src.read_text(encoding="utf-8"))
        for b in blocks:
            plat_slug = "-".join(b["platforms"]) or "unknown"
            fname = f"{src.stem}-{b['hour_utc']:02d}utc-{plat_slug}.md"
            dst = dst_dir / fname
            fm = [
                "---",
                f"source_brand: {args.brand}",
                f"persona: {args.persona}",
                f"post_date: {src.stem}",
                f"hour_utc: {b['hour_utc']:02d}",
                f"platforms: [{', '.join(b['platforms'])}]",
            ]
            if b["image"]:
                fm.append(f"image: {b['image']}")
            if b["video"]:
                fm.append(f"video: {b['video']}")
            fm.append("---")
            content = "\n".join(fm) + "\n\n" + b["body"] + "\n"

            if args.dry_run:
                print(f"[stage] would write {dst}")
            else:
                dst.write_text(content, encoding="utf-8")
                written += 1

    print(f"[stage] Wrote {written} corpus file(s) to {dst_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
