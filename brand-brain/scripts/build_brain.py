#!/usr/bin/env python3
"""
Stage 1: Build the brain map for a persona.

Reads brand-brain/brands/<persona>/corpus/**/*.{md,txt}, sends the concatenated
corpus to Claude with a strict schema, writes:
  - brand-brain/brands/<persona>/brain/brain_map.json
  - brand-brain/brands/<persona>/brain/style_examples.jsonl

Usage:
  export ANTHROPIC_API_KEY=...
  python brand-brain/scripts/build_brain.py --persona zara
  python brand-brain/scripts/build_brain.py --persona zara --diff    # respects hand-edits

Design notes:
  - No pgvector, no framework. Plain requests + JSON.
  - Model default: claude-sonnet-4-5 (adjustable via --model).
  - Diff mode: if brain_map.json exists and hand_edited=true, we ask Claude
    to propose only additions/updates as a JSON patch, and we merge conservatively.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import urllib.request
import urllib.error

REPO_ROOT = Path(__file__).resolve().parents[2]
BRAND_BRAIN = REPO_ROOT / "brand-brain"
SCHEMA_PATH = BRAND_BRAIN / "schemas" / "brain_map.schema.json"

CORPUS_EXTS = {".md", ".txt"}
MAX_CORPUS_CHARS = 400_000  # ~100K tokens, well under Sonnet's window

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


def load_corpus(persona: str) -> tuple[str, dict]:
    """Concatenate all corpus files with source tags. Return (text, stats)."""
    corpus_dir = BRAND_BRAIN / "brands" / persona / "corpus"
    if not corpus_dir.exists():
        sys.exit(f"[build_brain] No corpus directory at {corpus_dir}")

    parts = []
    stats = {"files": 0, "chars": 0, "by_source": {}}
    for path in sorted(corpus_dir.rglob("*")):
        if path.suffix.lower() not in CORPUS_EXTS or not path.is_file():
            continue
        source = path.parent.name  # social / long_form / voice / product
        try:
            text = path.read_text(encoding="utf-8").strip()
        except Exception as e:
            print(f"[build_brain] skip {path}: {e}", file=sys.stderr)
            continue
        if not text:
            continue
        rel = path.relative_to(corpus_dir)
        parts.append(f"<file source=\"{source}\" path=\"{rel}\">\n{text}\n</file>")
        stats["files"] += 1
        stats["chars"] += len(text)
        stats["by_source"][source] = stats["by_source"].get(source, 0) + 1

    if not parts:
        sys.exit(f"[build_brain] Corpus at {corpus_dir} is empty. Add source files first.")

    joined = "\n\n".join(parts)
    if len(joined) > MAX_CORPUS_CHARS:
        print(
            f"[build_brain] Corpus is {len(joined):,} chars; truncating to {MAX_CORPUS_CHARS:,}. "
            "Split into a second persona or prune older files if you want everything included.",
            file=sys.stderr,
        )
        joined = joined[:MAX_CORPUS_CHARS]

    return joined, stats


def build_prompt(persona: str, corpus_text: str, schema: dict, prior: dict | None) -> str:
    schema_str = json.dumps(schema, indent=2)
    prior_block = ""
    if prior:
        prior_block = (
            "\n\n<prior_brain_map hand_edited=\"true\">\n"
            + json.dumps(prior, indent=2)
            + "\n</prior_brain_map>\n"
            "The prior brain map above was HAND-EDITED. Preserve every hand-edited field verbatim. "
            "Only propose changes where the new corpus provides clear evidence for an addition "
            "(e.g. a new signature phrase, a new topic). Do not paraphrase or 'improve' existing fields."
        )

    return f"""You are extracting the intellectual DNA of one persona from their own writing.

Persona: {persona}

Your output MUST be a single JSON object matching this schema exactly:

<schema>
{schema_str}
</schema>

Rules:
1. Ground every non-null field in at least 3 corpus samples. If evidence is thin, use null (or [] for arrays).
2. Do NOT invent traits that flatter the persona. If the corpus is dry, say the tone is dry.
3. `banned_phrases` should include AI-ese and hype words this persona never uses (check the corpus — do not just copy a generic list).
4. `signature_phrases` must be verbatim strings that appear 2+ times in the corpus.
5. `tone_dimensions` scores are 0-10 integers with corpus evidence.
6. Output ONLY the JSON object, no prose, no code fences.{prior_block}

<corpus>
{corpus_text}
</corpus>
"""


def build_examples_prompt(persona: str, corpus_text: str) -> str:
    return f"""From the corpus below, extract 30 verbatim snippets (5-40 words each) that best exemplify {persona}'s voice.

Output ONE JSON object per line (JSONL), each with:
  {{"mode": "hook|transition|cta|teach|story|opinion", "text": "<verbatim>", "source_hint": "<file source attr>"}}

Rules:
- Verbatim only. Do not paraphrase.
- Diverse modes: aim for ~5 per mode.
- Prefer snippets that would be useful few-shot examples for a copywriting agent.
- Output ONLY the JSONL lines, no prose.

<corpus>
{corpus_text}
</corpus>
"""


def call_claude(prompt: str, model: str, max_tokens: int = 8000) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("[build_brain] ANTHROPIC_API_KEY not set")

    payload = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }).encode("utf-8")

    req = urllib.request.Request(
        ANTHROPIC_URL,
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"[build_brain] Anthropic HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")
    except urllib.error.URLError as e:
        sys.exit(f"[build_brain] Anthropic network error: {e}")

    # Concatenate text blocks
    blocks = body.get("content", [])
    text = "".join(b.get("text", "") for b in blocks if b.get("type") == "text")
    if not text:
        sys.exit(f"[build_brain] Empty response from Claude: {body}")
    return text.strip()


def parse_json_strict(raw: str) -> dict:
    # Tolerate accidental ```json fences even though we asked for none.
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
        cleaned = cleaned.strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        sys.exit(f"[build_brain] Claude returned invalid JSON: {e}\n---\n{raw[:2000]}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--persona", required=True, help="Persona directory name under brand-brain/brands/")
    ap.add_argument("--model", default="claude-sonnet-4-5")
    ap.add_argument("--diff", action="store_true", help="Preserve hand-edits in existing brain_map.json")
    ap.add_argument("--skip-examples", action="store_true", help="Skip style_examples.jsonl generation")
    args = ap.parse_args()

    schema = json.loads(SCHEMA_PATH.read_text())
    brain_dir = BRAND_BRAIN / "brands" / args.persona / "brain"
    brain_dir.mkdir(parents=True, exist_ok=True)
    brain_path = brain_dir / "brain_map.json"
    examples_path = brain_dir / "style_examples.jsonl"

    prior = None
    if args.diff and brain_path.exists():
        try:
            candidate = json.loads(brain_path.read_text())
            if candidate.get("hand_edited"):
                prior = candidate
                print("[build_brain] Diff mode: prior brain_map was hand-edited, preserving fields.")
        except json.JSONDecodeError:
            print("[build_brain] Existing brain_map.json is not valid JSON; ignoring for diff.", file=sys.stderr)

    print(f"[build_brain] Loading corpus for persona '{args.persona}'...")
    corpus_text, stats = load_corpus(args.persona)
    print(f"[build_brain] Corpus: {stats['files']} files, {stats['chars']:,} chars, sources: {stats['by_source']}")

    print(f"[build_brain] Calling {args.model} for brain map...")
    prompt = build_prompt(args.persona, corpus_text, schema, prior)
    raw = call_claude(prompt, args.model)
    brain_map = parse_json_strict(raw)

    brain_map["generated_at"] = datetime.now(timezone.utc).isoformat()
    brain_map["corpus_stats"] = stats
    brain_map.setdefault("hand_edited", False)

    brain_path.write_text(json.dumps(brain_map, indent=2) + "\n")
    print(f"[build_brain] Wrote {brain_path}")

    if not args.skip_examples:
        print(f"[build_brain] Calling {args.model} for style examples...")
        ex_raw = call_claude(build_examples_prompt(args.persona, corpus_text), args.model, max_tokens=4000)
        # Filter to lines that parse as JSON objects
        good_lines = []
        for line in ex_raw.splitlines():
            line = line.strip()
            if not line or line.startswith("```"):
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict) and "text" in obj and "mode" in obj:
                    good_lines.append(json.dumps(obj))
            except json.JSONDecodeError:
                continue
        examples_path.write_text("\n".join(good_lines) + "\n")
        print(f"[build_brain] Wrote {examples_path} ({len(good_lines)} examples)")

    print("\n[build_brain] Done. Next: hand-edit brain_map.json, set \"hand_edited\": true, commit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
