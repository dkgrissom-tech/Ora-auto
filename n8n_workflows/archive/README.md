# Archived n8n workflows — do NOT import

Files in this directory are superseded. They are kept only as reference for node
layout and platform request bodies.

## `workflow_short_form_pipeline_v1.json`, `workflow_video_pipeline_v1.json`

Arrived in the 2026-08-08 weekend handoff package. **Not importable into this
instance.** Two reasons:

1. **`$vars` does not exist here.** Both v1 files reference `$vars.GRISSOM_BLUESKY_HANDLE`,
   `$vars.GRISSOM_META_LONG_TOKEN`, `$vars.YT_STUDIO_API_KEY`, and others. The n8n
   instance at `n8n-production-b205b.up.railway.app` runs **Community edition**, where
   n8n Variables are unavailable. Every `$vars.*` reference resolves to undefined, so
   the workflows would run, look green, and post nothing — or post malformed requests.
   The live workflows use `$env.*` backed by Railway environment variables instead.

2. **They are older than what is already imported.** The live instance already has:

   | Workflow | n8n ID | State |
   |---|---|---|
   | Short-Form Content Pipeline v2 (Community / clone_drafts) | `71gVEXd7G2OzyIUp` | imported, inactive, trigger disabled |
   | Short-Form Content Pipeline v3 (Postiz / brands posts) | — | imported, inactive |
   | Video Content Pipeline v3 (Postiz / video_drafts) | `RTXbEpnpMCU0wywu` | imported, inactive, trigger disabled |

   v3 publishes through the self-hosted Postiz instance rather than calling YouTube /
   TikTok / Instagram / Pinterest directly. The v1 files call every platform API
   directly, which reintroduces the per-platform token problem Postiz was adopted to
   solve.

Additionally, v1's short-form pipeline reads `content_drafts/<brand>/*.md`. Nothing
writes to that path. The live queue is `brands/<brand>/posts/YYYY-MM-DD.md` with
`## HH:MM UTC` blocks (see `scripts/run_scheduler.py`), which is where the ingested
Handy Hearts drafts actually live.

**If you want anything from v1**, port the individual node bodies into v3 — do not
import the file.
