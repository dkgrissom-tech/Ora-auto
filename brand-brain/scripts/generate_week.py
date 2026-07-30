#!/usr/bin/env python3
"""
Generate the next 7 days of post files for one brand.

Reads brand-brain/schedules/<brand>.yaml, expands day_of_week + hour_utc slots
into concrete dates, calls agent_run.py for each slot, and writes:

    brands/<brand>/posts/YYYY-MM-DD.md

...in the exact ## HH:00 UTC block format that run_scheduler.py expects.

Gates: if any file listed under `gates:` in the schedule is missing, the run
aborts for that brand with a clear non-zero exit code and a stderr message.
This is how Build 100 blocks Ora launch content until interruption-safe
recaps ship.

Usage:
  # Standard run: generate the coming Mon-Sun window
  python brand-brain/scripts/generate_week.py --brand ora

  # Dry-run: prints what would be generated, calls no APIs, writes no files
  python brand-brain/scripts/generate_week.py --brand ora --dry-run

  # Custom start date (Mon-Sun window rooted at this date)
  python brand-brain/scripts/generate_week.py --brand ora --start 2026-08-03

  # Explicit output dir (defaults to brands/<brand>/posts/)
  python brand-brain/scripts/generate_week.py --brand ora --out /tmp/preview

Cost note: at ~$0.02 per agent call and ~15 slots/week, one brand-week is
roughly $0.30 in Anthropic spend. Three brands per week ≈ $1/week.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BRAND_BRAIN = REPO_ROOT / "brand-brain"
AGENT_RUN = BRAND_BRAIN / "scripts" / "agent_run.py"

DOW_MAP = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6}
DOW_GROUPS = {
    "weekday": {0, 1, 2, 3, 4},
    "weekend": {5, 6},
    "all": {0, 1, 2, 3, 4, 5, 6},
}


def load_yaml(path: Path) -> dict:
    """Minimal YAML loader — uses PyYAML if available, else fails clearly."""
    try:
        import yaml
    except ImportError:
        sys.exit("[generate_week] PyYAML not installed. Run: pip install pyyaml")
    return yaml.safe_load(path.read_text())


def next_week_start(today: date | None = None) -> date:
    """Return the coming Monday. If today IS Monday, return today."""
    today = today or date.today()
    days_ahead = (0 - today.weekday()) % 7
    return today + timedelta(days=days_ahead)


def slot_dates(week_start: date, day_of_week: str) -> list[date]:
    """Expand a day_of_week token into concrete dates within the week."""
    dow = day_of_week.strip().lower()
    if dow in DOW_MAP:
        return [week_start + timedelta(days=DOW_MAP[dow])]
    if dow in DOW_GROUPS:
        return [week_start + timedelta(days=n) for n in sorted(DOW_GROUPS[dow])]
    sys.exit(f"[generate_week] Unknown day_of_week: {day_of_week!r}")


def check_gates(schedule: dict, brand: str) -> None:
    gates = schedule.get("gates") or []
    missing = []
    for g in gates:
        gate_path = REPO_ROOT / g["path"]
        if not gate_path.exists():
            missing.append((g["path"], g.get("reason", "no reason given")))
    if missing:
        print(f"[generate_week] GATE(S) NOT MET for brand {brand!r} — aborting:", file=sys.stderr)
        for path, reason in missing:
            print(f"  - missing file: {path}", file=sys.stderr)
            print(f"    reason: {reason}", file=sys.stderr)
        print(
            "\n[generate_week] Create the gate file(s) once the prerequisite ships, then re-run.",
            file=sys.stderr,
        )
        sys.exit(2)


def call_agent(persona: str, agent: str, brand: str, angle: str, dry_run: bool) -> dict | None:
    """Invoke agent_run.py and return parsed JSON output, or None on failure."""
    if dry_run:
        print(f"    [DRY] would call agent_run.py --persona {persona} --agent {agent} --brand {brand}")
        return {
            "body": f"[DRY-RUN placeholder for {persona}/{agent} — angle: {angle}]",
            "preview_hook": "[DRY-RUN]",
            "caption": f"[DRY-RUN placeholder for {persona}/{agent} — angle: {angle}]",
            "hashtags": [],
        }

    cmd = [
        sys.executable, str(AGENT_RUN),
        "--persona", persona,
        "--agent", agent,
        "--brand", brand,
        "--task", angle or "Generate a post consistent with the persona's brain map.",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        print(f"    [FAIL] agent_run timed out", file=sys.stderr)
        return None
    if result.returncode != 0:
        print(f"    [FAIL] agent_run exit {result.returncode}: {result.stderr.strip()[:300]}", file=sys.stderr)
        return None

    raw = result.stdout.strip()
    if raw.startswith("```"):
        raw = raw.strip("`")
        if raw.lower().startswith("json"):
            raw = raw[4:]
        raw = raw.strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"    [FAIL] agent_run returned non-JSON: {e}\n---\n{raw[:500]}", file=sys.stderr)
        return None


def extract_body(agent_output: dict, agent_name: str) -> str:
    """Different agent templates return different top-level fields. Normalize."""
    for key in ("body", "caption", "post", "text"):
        if key in agent_output and isinstance(agent_output[key], str):
            return agent_output[key].strip()
    # Fallback: dump the whole JSON — reviewer will notice and fix the agent template.
    print(f"    [WARN] agent {agent_name!r} returned no body/caption/post/text field; embedding full JSON", file=sys.stderr)
    return json.dumps(agent_output, indent=2)


def format_block(slot: dict, body: str, agent_output: dict) -> str:
    hour = int(slot["hour_utc"])
    cdt_hour = (hour - 5) % 24  # America/Chicago is UTC-5 in CDT
    lines = [f"## {hour:02d}:00 UTC  ({cdt_hour:02d}:00 CDT)"]
    lines.append(f"platforms: {', '.join(slot['platforms'])}")
    if slot.get("asset"):
        asset = slot["asset"]
        if asset.endswith((".mp4", ".mov", ".webm")):
            lines.append(f"video: {asset}")
        else:
            lines.append(f"image: {asset}")
    # Pull hashtags from IG-style agents into a comment for reviewer visibility
    if agent_output.get("hashtags"):
        lines.append(f"# hashtags: {' '.join(agent_output['hashtags'])}")
    if agent_output.get("hook_variants"):
        alts = agent_output["hook_variants"][:3]
        lines.append("# hook_variants (reviewer can swap):")
        for i, h in enumerate(alts, 1):
            lines.append(f"#   {i}. {h}")
    lines.append("---")
    lines.append(body)
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", required=True)
    ap.add_argument("--start", default="", help="YYYY-MM-DD Monday to start from (default: coming Monday)")
    ap.add_argument("--out", default="", help="Output dir (default: brands/<brand>/posts/)")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    schedule_path = BRAND_BRAIN / "schedules" / f"{args.brand}.yaml"
    if not schedule_path.exists():
        sys.exit(f"[generate_week] No schedule at {schedule_path}")

    schedule = load_yaml(schedule_path)
    if not schedule.get("enabled", True):
        print(f"[generate_week] Brand {args.brand} disabled in schedule; skipping.")
        return 0

    persona = schedule.get("persona")
    if not persona:
        sys.exit(f"[generate_week] Schedule for {args.brand} has no persona field")

    check_gates(schedule, args.brand)

    # Warn (but don't abort) if the persona's brain map is missing or not hand-edited
    brain_path = BRAND_BRAIN / "brands" / persona / "brain" / "brain_map.json"
    if not brain_path.exists():
        sys.exit(f"[generate_week] No brain_map for persona {persona!r}. Run build_brain.py first.")
    try:
        brain = json.loads(brain_path.read_text())
        if not brain.get("hand_edited"):
            print(
                f"[generate_week] WARNING: {persona} brain_map has hand_edited=false. "
                "Generated posts may need heavier reviewer editing.",
                file=sys.stderr,
            )
    except json.JSONDecodeError:
        sys.exit(f"[generate_week] {brain_path} is not valid JSON")

    if args.start:
        week_start = date.fromisoformat(args.start)
        if week_start.weekday() != 0:
            print(f"[generate_week] WARNING: --start {args.start} is not a Monday.", file=sys.stderr)
    else:
        week_start = next_week_start()

    out_dir = Path(args.out) if args.out else REPO_ROOT / "brands" / args.brand / "posts"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Expand slots into per-date buckets
    by_date: dict[date, list[dict]] = {}
    for slot in schedule.get("slots", []):
        for d in slot_dates(week_start, slot["day_of_week"]):
            by_date.setdefault(d, []).append(slot)
    # Sort each day's slots by hour
    for d in by_date:
        by_date[d].sort(key=lambda s: int(s["hour_utc"]))

    total_slots = sum(len(v) for v in by_date.values())
    print(f"[generate_week] brand={args.brand} persona={persona} week_start={week_start} slots={total_slots} dry_run={args.dry_run}")

    failures = 0
    for d in sorted(by_date):
        slots = by_date[d]
        print(f"  {d} ({d.strftime('%a')}): {len(slots)} slot(s)")

        blocks = []
        for slot in slots:
            agent_name = slot["agent"]
            angle = slot.get("angle", "")
            print(f"    → {slot['hour_utc']:02d}UTC  {agent_name}  platforms={slot['platforms']}")
            agent_output = call_agent(persona, agent_name, args.brand, angle, args.dry_run)
            if agent_output is None:
                failures += 1
                continue
            body = extract_body(agent_output, agent_name)
            blocks.append(format_block(slot, body, agent_output))

        if not blocks:
            print(f"    (no successful slots for {d}, skipping file)")
            continue

        # Header for the day file
        header = (
            f"# {args.brand.title()} — {d.isoformat()} ({d.strftime('%A')})\n\n"
            f"<!-- Generated by generate_week.py on {datetime.now(timezone.utc).isoformat()} "
            f"from schedules/{args.brand}.yaml, persona: {persona} -->\n"
            f"<!-- Reviewer: edit bodies freely; do not change ## HH:00 UTC headers or the platforms/image/video meta lines. -->\n\n"
        )
        content = header + "".join(blocks)

        out_path = out_dir / f"{d.isoformat()}.md"
        if args.dry_run:
            print(f"    [DRY] would write {out_path} ({len(content)} chars)")
        else:
            if out_path.exists():
                print(f"    [SKIP] {out_path} already exists (delete to regenerate)")
                continue
            out_path.write_text(content, encoding="utf-8")
            print(f"    [OK] wrote {out_path}")

    if failures:
        print(f"\n[generate_week] Completed with {failures} slot failure(s). Check stderr.", file=sys.stderr)
        return 1
    print(f"\n[generate_week] Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
