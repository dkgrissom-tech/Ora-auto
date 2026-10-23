#!/usr/bin/env python3
"""
Stage 2: Run a specialized agent for a persona.

Loads:
  - brand-brain/brands/<persona>/brain/brain_map.json
  - brand-brain/brands/<persona>/brain/style_examples.jsonl (optional, top-K sampled)
  - brand-brain/brands/<persona>/agents/<agent>.md  (Jinja-lite template with {{placeholders}})

Then calls Claude and prints the response to stdout (usually JSON, per the agent
prompt's contract). Downstream tooling in Ora-auto can pipe this into the
brands/<brand>/posts/YYYY-MM-DD.md writer.

Usage:
  python brand-brain/scripts/agent_run.py \\
    --persona zara \\
    --agent ig_poster \\
    --task "Day 3 Ora launch, video zara_meetora_9x16.mp4"

Optional: --k 5  (number of style examples to include, default 5)
          --mode-filter hook,cta  (only pull examples of these modes)
"""

from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
from pathlib import Path

import urllib.request
import urllib.error

REPO_ROOT = Path(__file__).resolve().parents[2]
BRAND_BRAIN = REPO_ROOT / "brand-brain"

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"

PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


def render(template: str, ctx: dict) -> str:
    def sub(match: re.Match) -> str:
        key = match.group(1)
        if key not in ctx:
            sys.exit(f"[agent_run] Template references unknown placeholder: {{{{{key}}}}}")
        val = ctx[key]
        if isinstance(val, (dict, list)):
            return json.dumps(val, indent=2)
        return str(val)
    return PLACEHOLDER_RE.sub(sub, template)


def load_examples(persona: str, k: int, mode_filter: list[str] | None) -> list[dict]:
    path = BRAND_BRAIN / "brands" / persona / "brain" / "style_examples.jsonl"
    if not path.exists():
        return []
    examples = []
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if mode_filter and obj.get("mode") not in mode_filter:
            continue
        examples.append(obj)
    if not examples:
        return []
    # v1: random sample. v2: embed task + cosine-rank via pgvector.
    random.shuffle(examples)
    return examples[:k]


def call_claude(prompt: str, model: str, max_tokens: int = 2000) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("[agent_run] ANTHROPIC_API_KEY not set")

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
        with urllib.request.urlopen(req, timeout=90) as resp:
            body = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"[agent_run] Anthropic HTTP {e.code}: {e.read().decode('utf-8', errors='replace')}")

    blocks = body.get("content", [])
    return "".join(b.get("text", "") for b in blocks if b.get("type") == "text").strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--persona", required=True)
    ap.add_argument("--agent", required=True, help="Agent template name (without .md)")
    ap.add_argument("--task", required=True, help="Task description injected as {{task}}")
    ap.add_argument("--brand", default="", help="Optional brand name for {{brand}} (defaults to persona)")
    ap.add_argument("--model", default="claude-sonnet-4-5")
    ap.add_argument("--k", type=int, default=5, help="Number of style examples to include")
    ap.add_argument("--mode-filter", default="", help="Comma-separated modes to filter examples (hook,cta,etc)")
    ap.add_argument("--max-tokens", type=int, default=2000)
    args = ap.parse_args()

    brain_path = BRAND_BRAIN / "brands" / args.persona / "brain" / "brain_map.json"
    agent_path = BRAND_BRAIN / "brands" / args.persona / "agents" / f"{args.agent}.md"

    if not brain_path.exists():
        sys.exit(f"[agent_run] No brain_map at {brain_path}. Run build_brain.py first.")
    if not agent_path.exists():
        sys.exit(f"[agent_run] No agent template at {agent_path}")

    brain_map = json.loads(brain_path.read_text())
    template = agent_path.read_text()

    mode_filter = [m.strip() for m in args.mode_filter.split(",") if m.strip()] or None
    examples = load_examples(args.persona, args.k, mode_filter)

    ctx = {
        "brand": args.brand or args.persona,
        "persona": args.persona,
        "brain_map": brain_map,
        "banned_phrases": brain_map.get("voice", {}).get("banned_phrases", []),
        "signature_phrases": brain_map.get("voice", {}).get("signature_phrases", []),
        "examples": examples,
        "task": args.task,
    }

    prompt = render(template, ctx)
    output = call_claude(prompt, args.model, args.max_tokens)
    print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
