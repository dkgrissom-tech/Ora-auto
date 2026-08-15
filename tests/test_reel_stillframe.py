"""Reels-named still images must not be sent to Buffer's Instagram channel.

Buffer's Instagram channel rejects any post with 'reel' semantics unless a
real video is attached. On 2026-08-14 18:00 UTC a block with
    image: handy-hearts-ig-reel-porch-scene-2026-08-14.jpg
was routed to Buffer/instagram and the API returned 'Instagram Reels require
a video', which flipped the whole run red. The scheduler now skips such
blocks at delivery time with an actionable message so a naming mistake does
not take down the whole tick.

Run: DRY_RUN=true python3 tests/test_reel_stillframe.py
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


# --- is_reel_named_stillframe ----------------------------------------------

check(
    "reel in name + jpg is a still-frame mismatch",
    rs.is_reel_named_stillframe("handy-hearts-ig-reel-porch-scene-2026-08-14.jpg"),
)
check(
    "reel in name + mp4 is a real reel",
    not rs.is_reel_named_stillframe("porch-scene-reel-2026-08-14.mp4"),
)
check(
    "reel in name + mov is a real reel",
    not rs.is_reel_named_stillframe("porch-scene-reel.mov"),
)
check(
    "reel in name + m4v is a real reel",
    not rs.is_reel_named_stillframe("porch-scene-reel.m4v"),
)
check(
    "reel in name + webm is a real reel",
    not rs.is_reel_named_stillframe("porch-scene-reel.webm"),
)
check(
    "reel-less name + jpg is fine",
    not rs.is_reel_named_stillframe("handy-hearts-porch-scene-2026-08-14.jpg"),
)
check(
    "reel-less name + mp4 is fine",
    not rs.is_reel_named_stillframe("porch-scene-2026-08-14.mp4"),
)
check(
    "case-insensitive: REEL in an uppercase filename still triggers",
    rs.is_reel_named_stillframe("HANDY-HEARTS-IG-REEL-PORCH.JPG"),
)
check(
    "empty path is not a mismatch",
    not rs.is_reel_named_stillframe(""),
)
check(
    "None is not a mismatch",
    not rs.is_reel_named_stillframe(None),
)
check(
    "reel appearing inside another word (e.g. 'reeled') also triggers",
    rs.is_reel_named_stillframe("reeled-in-2026.png"),
    detail="the check is substring-based so 'reeled' matches - acceptable, err on the side of skipping",
)


# --- deliver() returns skip for the mismatch --------------------------------

post = {
    "brand": "grissom",
    "hour": 18,
    "platforms": ["instagram"],
    "image": "brands/grissom/assets/handy-hearts-ig-reel-porch-scene-2026-08-14.jpg",
    "body": "Chapter 3 wrecks me every time I read it. A porch. A storm.",
}

status, detail = rs.deliver("grissom", post, "instagram")
check(
    "deliver() skips reel-named JPG on 'instagram' platform",
    status == "skip",
    detail=f"got status={status} detail={detail!r}",
)
check(
    "skip detail mentions the offending asset",
    "reel" in (detail or "").lower() and "video" in (detail or "").lower(),
    detail=f"detail={detail!r}",
)

status2, detail2 = rs.deliver("grissom", post, "buffer_instagram")
check(
    "deliver() also skips on 'buffer_instagram' platform",
    status2 == "skip",
    detail=f"got status={status2}",
)

# A real reel (video) should NOT be skipped by this check. It might still be
# skipped for other reasons (no token, cap, etc.), so we accept skip-with-a-
# different-reason too — the important thing is our reel-stillframe message
# is not the one used.
post_real_reel = dict(post, image="brands/grissom/assets/porch-scene-reel-2026-08-14.mp4")
status3, detail3 = rs.deliver("grissom", post_real_reel, "instagram")
check(
    "deliver() does NOT skip a real .mp4 reel with our stillframe message",
    "reel" not in (detail3 or "").lower() or "video" not in (detail3 or "").lower()
    or status3 != "skip",
    detail=f"status={status3} detail={detail3!r}",
)


if FAILURES:
    print(f"\n{len(FAILURES)} FAILED")
    sys.exit(1)
print("\nall passed")
