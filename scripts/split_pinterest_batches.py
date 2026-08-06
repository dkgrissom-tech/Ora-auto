#!/usr/bin/env python3
"""
Split Pinterest batch drafts (5 pins per file) into individual per-pin drafts.

Input: batch files in /tmp/original_handy-hearts-pinterest-*.md (restored from git)
Output: N individual drafts per batch, one per Pin, written to clone_drafts/grissom/.

Each pin gets:
- kind: social, brand: grissom, platforms: [pinterest]
- scheduled: <date>T<HH>:00:00-05:00 with staggered hours across the day
- image: brands/grissom/assets/<slug>.jpg
- body: Title + Description + hashtags

Pin times (5 pins spread through a day):
  09:00, 12:00, 15:00, 18:00, 21:00 Central

Old batch file gets deleted after successful split.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFTS = ROOT / "clone_drafts" / "grissom"
TMP = Path("/tmp")
ASSETS_BASE = "brands/grissom/assets"

# Staggered posting hours for 5 pins/day (Central time)
PIN_HOURS = ["09:00", "12:00", "15:00", "18:00", "21:00"]

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)
PIN_BLOCK_RE = re.compile(r"^##\s*Pin\s+(\d+)[^\n]*\n(.*?)(?=^##\s*Pin\s+\d+|\Z)", re.DOTALL | re.MULTILINE)


def parse_meta(text: str):
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


def slugify(title: str) -> str:
    s = re.sub(r"[^\w\s-]", "", title.lower())
    s = re.sub(r"\s+", "-", s).strip("-")
    return s[:60]


def extract_pin(block: str):
    """Extract title, desc, hashtags from a Pin block."""
    title_m = re.search(r"\*\*Title:\*\*\s*(.+?)(?=\n)", block)
    desc_m = re.search(r"\*\*Desc:\*\*\s*(.+?)(?=\n#|\Z)", block, re.DOTALL)
    tags_m = re.search(r"^(#\w+(?:\s+#\w+)+)", block, re.MULTILINE)

    title = title_m.group(1).strip() if title_m else ""
    desc = desc_m.group(1).strip() if desc_m else ""
    tags = tags_m.group(1).strip() if tags_m else ""
    return title, desc, tags


def split_batch(batch_path: Path, dry_run: bool = False):
    text = batch_path.read_text(encoding="utf-8")
    meta, body = parse_meta(text)

    if not meta:
        return "no frontmatter", []

    date = meta.get("scheduled", "").split("T")[0]
    if not date:
        return "no date", []

    # Find all pin blocks
    pins = PIN_BLOCK_RE.findall(body)
    if not pins:
        return "no pins found", []

    batch_name = batch_path.stem
    # Strip 'original_' tmp prefix so output slugs are clean
    batch_name = re.sub(r"^original_", "", batch_name)
    # Strip trailing date from batch name to make a nice per-pin prefix
    batch_prefix = re.sub(r"-\d{4}-\d{2}-\d{2}$", "", batch_name)
    batch_prefix = batch_prefix.replace("handy-hearts-pinterest-", "hh-pin-")

    outputs = []
    for i, (pin_num, block) in enumerate(pins):
        if i >= len(PIN_HOURS):
            break  # Only 5 slots available
        title, desc, tags = extract_pin(block)
        if not title or not desc:
            continue

        # Build slug from title (short)
        theme_slug = slugify(title.split("|")[0])[:40]
        pin_slug = f"{batch_prefix}-pin{pin_num}-{theme_slug}-{date}"

        hour = PIN_HOURS[i]
        scheduled = f"{date}T{hour}:00-05:00"
        image_path = f"{ASSETS_BASE}/{pin_slug}.jpg"

        # Body: Title as first line, then description, then tags
        pin_body = f"**{title}**\n\n{desc}"
        if tags:
            pin_body += f"\n\n{tags}"

        content = f"""---
kind: social
brand: grissom
platforms: [pinterest]
scheduled: {scheduled}
filename: {pin_slug}.md
image: {image_path}
---

{pin_body}
"""
        out_path = DRAFTS / f"{pin_slug}.md"
        outputs.append((out_path, content))

        if not dry_run:
            out_path.write_text(content, encoding="utf-8")

    return f"split into {len(outputs)} pins", outputs


def main():
    dry_run = "--dry-run" in sys.argv
    batch_files = sorted(TMP.glob("original_handy-hearts-pinterest-*.md"))

    print(f"Found {len(batch_files)} batch files (dry_run={dry_run})\n")

    total_written = 0
    for bf in batch_files:
        status, outs = split_batch(bf, dry_run=dry_run)
        print(f"  {bf.name} → {status}")
        for out_path, _ in outs:
            print(f"      → {out_path.name}")
        total_written += len(outs)

        # Remove the collapsed/empty file in clone_drafts (the one that has no body)
        collapsed = DRAFTS / bf.name.replace("original_", "")
        if collapsed.exists() and not dry_run:
            collapsed.unlink()
            print(f"      ✗ removed empty collapsed file: {collapsed.name}")

    print(f"\nTotal pins written: {total_written}")


if __name__ == "__main__":
    main()
