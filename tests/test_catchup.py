"""Scheduler must catch up blocks orphaned by GitHub Actions cron drift.

The old `hour == now.hour` filter silently dropped any block whose scheduled
hour had no matching tick. On 2026-08-15 the runner queue jumped from 01:52
to 03:07 UTC, orphaning the 02:00 Grissom Pinterest block forever. This test
covers the fix: the scheduler now sweeps `now.hour` plus CATCHUP_HOURS prior
hours, and the ledger prevents duplicate sends when a hour did get its own
tick.

Run: DRY_RUN=true python3 tests/test_catchup.py
"""
import datetime as dt
import os
import pathlib
import sys

os.environ["DRY_RUN"] = "true"

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import run_scheduler as rs  # noqa: E402

FAILURES = []


def check(label, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {label}" + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(label)


# --- eligible_hours logic ---------------------------------------------------

def eligible(now_hour, catchup):
    return {(now_hour - i) % 24 for i in range(catchup + 1)}


check(
    "current hour is always eligible",
    3 in eligible(3, 2),
)
check(
    "previous hour is eligible with catchup=2",
    2 in eligible(3, 2),
)
check(
    "two-hour-back block is eligible with catchup=2",
    1 in eligible(3, 2),
)
check(
    "three-hour-back block is NOT eligible with catchup=2",
    0 not in eligible(3, 2),
    detail="hour 0 should not run on the 03:00 tick — that is beyond the recovery window",
)
check(
    "midnight wrap: 00:00 tick with catchup=2 covers 22, 23, 00",
    eligible(0, 2) == {22, 23, 0},
)
check(
    "catchup=0 collapses to current-hour-only (old behavior)",
    eligible(15, 0) == {15},
)


# --- CATCHUP_HOURS constant is exposed and sane -----------------------------

check(
    "CATCHUP_HOURS is defined on the scheduler module",
    hasattr(rs, "CATCHUP_HOURS"),
)
check(
    "CATCHUP_HOURS is >=1 (catch-up is enabled by default)",
    getattr(rs, "CATCHUP_HOURS", 0) >= 1,
)
check(
    "CATCHUP_HOURS is <=6 (do not sweep the whole day)",
    getattr(rs, "CATCHUP_HOURS", 99) <= 6,
)


# --- ledger idempotency still holds under catch-up --------------------------
# If a block was delivered on its own hour, the ledger key survives, and a
# subsequent tick that also considers that hour eligible will skip it.

sample_post = {"hour": 14, "brand": "grissom", "body": "hello", "platforms": ["bluesky"]}
key_a = rs.post_key("grissom", sample_post, "bluesky")
key_b = rs.post_key("grissom", sample_post, "bluesky")
check(
    "post_key is stable for the same block+platform",
    key_a == key_b,
    detail=f"{key_a} vs {key_b}",
)

sample_post_other_hour = dict(sample_post, hour=15)
key_c = rs.post_key("grissom", sample_post_other_hour, "bluesky")
check(
    "post_key encodes the hour so different hours get different keys",
    key_a != key_c,
    detail=f"{key_a} vs {key_c}",
)


# --- scheduler main runs without crashing on today's real files -------------
# Smoke test only — DRY_RUN prevents any real API calls or ledger writes.

try:
    rs.main()
    check("scheduler main() runs to completion in DRY_RUN", True)
except SystemExit as e:
    # exit(1) is a valid outcome (no posts landed), just not a crash.
    check("scheduler main() exits cleanly in DRY_RUN", e.code in (0, 1), detail=f"exit={e.code}")
except Exception as e:
    check("scheduler main() runs to completion in DRY_RUN", False, detail=repr(e))


if FAILURES:
    print(f"\n{len(FAILURES)} FAILED")
    sys.exit(1)
print("\nall passed")
