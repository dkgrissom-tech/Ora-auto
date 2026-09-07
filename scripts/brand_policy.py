"""Cross-cutting brand policy, defined once.

This existed in two places and drifted: ingest_clone_drafts.py allowed
{"ora", "grissom"} while run_scheduler.py allowed {"ora"}. The effect was that
Grissom TikTok posts were accepted into the queue and then skipped every day at
delivery, producing permanent noise for a post that could never publish. Any
policy both the ingester and the scheduler need belongs here.
"""
import os

# TikTok is enabled per brand because each brand needs its own connected account,
# either through a native Content Posting token OR through Buffer's TikTok
# channel slot. Grissom posts to @amgriss1 via Buffer (no native token needed);
# Ora posts as @toolstack-y4g. Family Book has no TikTok account yet, so its
# posts are dropped at ingest rather than queued and skipped.
#
# To enable another brand: connect the account in Buffer (or add
# {BRAND}_TIKTOK_ACCESS_TOKEN for native), and set TIKTOK_ALLOWED_BRANDS here
# or as an env var - one place, both scripts.
TIKTOK_ALLOWED_BRANDS = {
    b.strip().lower()
    for b in os.environ.get("TIKTOK_ALLOWED_BRANDS", "ora,grissom").split(",")
    if b.strip()
}
