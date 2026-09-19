#!/usr/bin/env python3
"""Weekly Build-Measure-Learn loop for the toolstack queue.

Reads TikTok performance from brands/toolstack/learnings/performance.csv (fed
manually or by an n8n metrics pull), scores the last 7 days of rendered posts
by views, marks the top 20% as `winner`, and appends 14 new queue rows that
inherit the winning series and beat structure.

Runs on GitHub Actions Sundays 10:00 America/Chicago (15:00 UTC).

Never modifies existing rows. Never runs a render. Cheap and idempotent.
"""
from __future__ import annotations

import csv
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUEUE_CSV = ROOT / "brands" / "toolstack" / "queue.csv"
PERF_CSV = ROOT / "brands" / "toolstack" / "learnings" / "performance.csv"


def load(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open() as f:
        return list(csv.DictReader(f))


def write(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    perf = load(PERF_CSV)
    if not perf:
        print("No performance rows — nothing to learn")
        return 0

    # Last 7 days by 'posted_date' if present, else all
    cutoff = (date.today() - timedelta(days=7)).isoformat()
    recent = [r for r in perf if r.get("posted_date", "") >= cutoff] or perf

    def views(r: dict) -> int:
        try:
            return int(r.get("views", "0") or 0)
        except ValueError:
            return 0

    recent.sort(key=views, reverse=True)
    if not recent:
        print("No recent rows")
        return 0

    top_n = max(1, len(recent) // 5)  # top 20%
    winners = recent[:top_n]
    winner_ids = {r["creative_id"] for r in winners}

    queue = load(QUEUE_CSV)
    changed = 0
    for r in queue:
        if r["creative_id"] in winner_ids and r.get("status") != "winner":
            r["status"] = "winner"
            changed += 1

    # Append 14 new rows for next week that inherit the winning series distribution
    winning_series = [w["creative_id"].split("-")[0].lower() for w in winners]
    if not winning_series:
        winning_series = ["milo", "rita", "barkley", "milo2"]

    next_start = date.today() + timedelta(days=(7 - date.today().weekday()) % 7 or 7)
    slots = ["morning", "evening"]

    # Find the highest-numbered NEXTGEN row so we don't collide
    existing_nextgen = [r for r in queue if r["creative_id"].startswith("NEXTGEN-")]
    base = len(existing_nextgen)

    new_rows = []
    for i in range(7):
        series = winning_series[i % len(winning_series)]
        for j, slot in enumerate(slots):
            n = base + i * 2 + j + 1
            cid = f"NEXTGEN-{series.upper()}-{n:03d}"
            new_rows.append({
                "creative_id": cid,
                "scheduled_date": (next_start + timedelta(days=i)).isoformat(),
                "time_slot": slot,
                "series": series,
                "hook": "TODO — copy winning hook or rewrite variation",
                "beat1_prompt": "TODO — inherit winning beat1 structure",
                "beat2_prompt": "TODO — inherit winning beat2 structure",
                "beat3_prompt": "TODO — inherit winning beat3 structure",
                "ref_url": "",
                "status": "draft",
                "rendered_at": "",
            })

    fieldnames = list(queue[0].keys()) if queue else [
        "creative_id", "scheduled_date", "time_slot", "series",
        "hook", "beat1_prompt", "beat2_prompt", "beat3_prompt",
        "ref_url", "status", "rendered_at",
    ]
    write(QUEUE_CSV, queue + new_rows, fieldnames)
    print(f"Marked {changed} winners, appended {len(new_rows)} draft rows for {next_start}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
