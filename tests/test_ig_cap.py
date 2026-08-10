"""The Instagram daily cap must survive a process restart.

BUFFER_IG_DAILY_CAP was enforced against a module-level counter, and every cron
tick is a fresh process, so the "daily" cap was really a per-run cap - 2026-08-09
recorded 3 Instagram deliveries against a cap of 2. The count now comes from the
delivery ledger, which persists.

Run: DRY_RUN=true python3 tests/test_ig_cap.py
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
TODAY = dt.datetime.utcnow().strftime("%Y-%m-%d")
YESTERDAY = (dt.datetime.utcnow() - dt.timedelta(days=1)).strftime("%Y-%m-%d")


def check(label, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'}  {label}" + (f"  {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(label)


def fake_ledger(keys):
    rs.load_ledger = lambda: set(keys)


def k(date, platform, brand="grissom", hour=13, digest="abc1234567"):
    return f"{date}|{brand}|{hour:02d}|{platform}|{digest}"


rs._ig_sent_this_run = 0

# --- counting ---------------------------------------------------------------
fake_ledger([])
check("empty ledger counts zero", rs.ig_sent_today() == 0)

fake_ledger([k(TODAY, "buffer_instagram", hour=13), k(TODAY, "buffer_instagram", hour=17)])
check("today's rerouted posts are counted", rs.ig_sent_today() == 2)

fake_ledger([k(TODAY, "instagram", hour=13), k(TODAY, "buffer_instagram", hour=17)])
check("both Instagram routes count against the same account budget",
      rs.ig_sent_today() == 2)

fake_ledger([k(YESTERDAY, "buffer_instagram", hour=h) for h in (13, 17, 21)])
check("yesterday's posts do not count toward today", rs.ig_sent_today() == 0)

fake_ledger([k(TODAY, "bluesky"), k(TODAY, "tiktok"), k(TODAY, "buffer_pinterest"),
             k(TODAY, "buffer_instagram")])
check("other platforms are not counted as Instagram", rs.ig_sent_today() == 1)

fake_ledger([k(TODAY, "buffer_instagram", brand="ora"),
             k(TODAY, "buffer_instagram", brand="grissom")])
check("the cap is per Buffer account, so every brand counts",
      rs.ig_sent_today() == 2)

fake_ledger(["", "garbage", "a|b|c", k(TODAY, "buffer_instagram")])
check("malformed ledger keys do not crash the count", rs.ig_sent_today() == 1)

# In-process deliveries must add on top of the ledger, because the ledger file is
# only written once at the end of a run.
fake_ledger([k(TODAY, "buffer_instagram")])
rs._ig_sent_this_run = 1
check("posts made earlier in this same run are added to the ledger count",
      rs.ig_sent_today() == 2)
rs._ig_sent_this_run = 0

# --- enforcement ------------------------------------------------------------
rs.post_buffer = lambda *a, **kw: True
rs.buffer_token = lambda: "tok"
post = {"hour": 13, "body": "hi", "image": None, "video": None, "alt": None,
        "tags": None, "pinterest_title": None, "pinterest_url": None,
        "platforms": ["pinterest"]}

# NB: the ledger is a set, so distinct entries need distinct hours - two posts
# in the same hour with the same body genuinely are one delivery.
rs.IG_DAILY_CAP = 2
fake_ledger([k(TODAY, "buffer_instagram", hour=13),
             k(TODAY, "buffer_instagram", hour=17)])
rs._ig_sent_this_run = 0
status, detail = rs.deliver("grissom", post, "buffer_instagram")
check("a cap already reached in an EARLIER run is honoured", status == "skip",
      f"{status} {detail}")
check("the skip says how many were already sent today", "2/2" in detail, detail)

fake_ledger([k(TODAY, "buffer_instagram")])
rs._ig_sent_this_run = 0
status, _ = rs.deliver("grissom", post, "buffer_instagram")
check("under the cap still delivers", status == "ok")
check("a delivery increments the in-run counter", rs._ig_sent_this_run == 1)

fake_ledger([k(TODAY, "buffer_instagram")])
rs._ig_sent_this_run = 0
first, _ = rs.deliver("grissom", post, "buffer_instagram")
second, sdetail = rs.deliver("grissom", post, "buffer_instagram")
check("two reroutes in one run still hit the cap",
      first == "ok" and second == "skip", f"{first} then {second} {sdetail}")

rs.IG_DAILY_CAP = 0
fake_ledger([k(TODAY, "buffer_instagram", hour=h) for h in range(9)])
rs._ig_sent_this_run = 0
status, _ = rs.deliver("grissom", post, "buffer_instagram")
check("cap of 0 means unlimited", status == "ok")

rs.IG_DAILY_CAP = 2
fake_ledger([k(TODAY, "buffer_instagram", hour=13),
             k(TODAY, "buffer_instagram", hour=17)])
rs._ig_sent_this_run = 0
status, _ = rs.deliver("grissom", post, "instagram")
check("a deliberately scheduled Instagram post is never capped", status == "ok")
check("but it does register against the day's budget", rs._ig_sent_this_run == 1)

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILED: " + "; ".join(FAILURES))
    sys.exit(1)
print("all instagram cap tests passed")
