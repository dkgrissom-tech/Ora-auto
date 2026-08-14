"""Buffer's Instagram API only accepts type='reel' when a video is attached.

A reel-named still image ('handy-hearts-ig-reel-porch-scene-2026-08-14.jpg')
red-X'd the whole Auto-Post workflow on 2026-08-11 and 2026-08-14 with
'InvalidInputError - Invalid post: Instagram Reels require a video.' The
fix: gate the reel/story type on the file extension and fall through to a
normal 9:16 feed post otherwise.

Run: DRY_RUN=true python3 tests/test_ig_post_type.py
"""
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


# --- ig_post_type -----------------------------------------------------------
# Reel-named STILL images caused the outage. They must publish as a normal
# feed post, not a reel, or Buffer rejects the whole tick.
check("reel-named .jpg is a regular post (the 2026-08-14 regression)",
      rs.ig_post_type("handy-hearts-ig-reel-porch-scene-2026-08-14.jpg") == "post")
check("reel-named .png is a regular post",
      rs.ig_post_type("handy-hearts-ig-reel-porch.png") == "post")
check("reel-named .mp4 really is a reel",
      rs.ig_post_type("handy-hearts-ig-reel-porch.mp4") == "reel")
check("reel-named .mov really is a reel",
      rs.ig_post_type("handy-hearts-ig-reel-porch.mov") == "reel")
check("reel-named .webm really is a reel",
      rs.ig_post_type("handy-hearts-ig-reel-porch.webm") == "reel")

# Story shares the same still-vs-video gate: a story cover as a JPG is fine
# as a plain post, but story TYPE requires a video asset.
check("story-named .jpg is a regular post",
      rs.ig_post_type("handy-hearts-ig-story-cover.jpg") == "post")
check("story-named .mp4 is a story",
      rs.ig_post_type("handy-hearts-ig-story-cover.mp4") == "story")

# Baseline: plain pins and empty paths stay as feed posts.
check("a plain pin filename is a post",
      rs.ig_post_type("hh-pin-aug14-porch.jpg") == "post")
check("empty path defaults to post", rs.ig_post_type("") == "post")
check("None path defaults to post", rs.ig_post_type(None) == "post")

# Case-insensitive: uppercase extensions still count as video.
check("uppercase .MP4 is still a reel",
      rs.ig_post_type("handy-hearts-ig-reel-porch.MP4") == "reel")

# --- soft-fail on the scheduler exit code -----------------------------------
# One malformed IG draft should not red-X the whole tick when other posts
# landed. But a tick where every attempt failed still exits non-zero, because
# that is the outage signal we actually want (Pinterest ran silent-green for
# five days before the exit(1) went in on 2026-08-06).
import subprocess

RUNNER = r"""
import sys, pathlib, types
sys.path.insert(0, str(pathlib.Path(__REPO__) / 'scripts'))
import run_scheduler as rs

class FakeNow:
    hour = 13
    def isoformat(self):
        return '2026-08-14T13:00:00'
    def strftime(self, fmt):
        return '2026-08-14' if 'Y' in fmt else '2026-08-14T13:00:00'
class FakeDatetime:
    @classmethod
    def utcnow(cls):
        return FakeNow()
rs.dt = types.SimpleNamespace(datetime=FakeDatetime, timedelta=rs.dt.timedelta)

rs.BRANDS = ['grissom']
rs.buffer_token = lambda: 'tok'
rs.load_ledger = lambda: set()
rs.save_ledger = lambda ledger: None
rs.write_summary = lambda results, hour: None

# Two platforms this hour: one succeeds, one fails.
rs.parse_today = lambda brand: [{
    'hour': 13, 'body': 'test post body', 'image': None, 'video': None,
    'alt': None, 'tags': None, 'pinterest_title': None, 'pinterest_url': None,
    'platforms': ['bluesky', 'instagram'],
}]
rs.route = lambda platforms, brand=None: list(platforms)

MODE = '__MODE__'  # 'partial' or 'total'
def deliver(brand, post, plat):
    if MODE == 'total':
        return 'fail', 'boom'
    return ('ok', 'sent') if plat == 'bluesky' else ('fail', 'boom')
rs.deliver = deliver

rs.main()
"""

repo = str(ROOT)
def _runner(mode):
    return RUNNER.replace('__REPO__', repr(repo)).replace('__MODE__', mode)

partial = subprocess.run([sys.executable, "-c", _runner("partial")],
                         capture_output=True, text=True)
check("partial failure (1 ok + 1 fail) exits 0", partial.returncode == 0,
      f"exit={partial.returncode} stderr={partial.stderr[-200:]}")

total = subprocess.run([sys.executable, "-c", _runner("total")],
                       capture_output=True, text=True)
check("total failure (0 ok + 1 fail) exits 1", total.returncode == 1,
      f"exit={total.returncode} stderr={total.stderr[-200:]}")

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILED: " + "; ".join(FAILURES))
    sys.exit(1)
print("all ig_post_type + soft-fail tests passed")
