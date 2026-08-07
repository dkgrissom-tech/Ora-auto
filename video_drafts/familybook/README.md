# video_drafts/familybook

Video drafts for **familybook**, read by the n8n workflow
**Video Content Pipeline v2 (Community / video_drafts)** at :15 of every hour.

This directory is owned by n8n. The GitHub Actions rail
(`ingest_clone_drafts.yml` at :50, `auto_post.yml` at :05) works only inside
`clone_drafts/` and `brands/`, and never touches this tree — that separation is
what keeps video posts from being published twice.

## Filename rules

- One draft per `.md` file. Any name works; date-prefixed is easiest to scan,
  e.g. `2026-08-08-handy-hearts-hook.md`.
- `*.posted-YYYY-MM-DD.md` — written by the pipeline after a successful publish.
  Ignored on later runs.
- `*.skip.*` — manually retired. Ignored.
- `README.md` — ignored.

## Frontmatter contract

```yaml
---
brand: familybook
video_source: manual          # manual | yt-studio | content-ideas-generator
video_url: https://...        # required when video_source: manual
video_type: short             # short -> 9:16, anything else -> 16:9
platforms: tiktok, instagram  # youtube | tiktok | instagram
caption: Your hook goes here
scheduled: 2026-08-08         # optional; omit to publish on the next tick
time: 14:00                   # UTC, defaults to 12:00
---

Body copy below the frontmatter is not published. Use it for notes.
```

### Field notes

- `platforms` — only `youtube`, `tiktok`, and `instagram` are handled here.
  Bluesky, Threads, Pinterest, and LinkedIn stay on the social rail in
  `clone_drafts/`; listing them here just writes a log line.
- `caption` — required. `title:` is accepted as a fallback.
- `video_source: manual` needs a publicly reachable `video_url`. TikTok pulls the
  file from that URL and Instagram fetches it for the Reel container, so a signed
  or private link will fail.
- `yt-studio` / `content-ideas-generator` submit a render job, then the pipeline
  polls for up to 15 minutes before logging a render failure.
- Scheduling window: a draft publishes when it is within 90 minutes of its
  `scheduled` + `time`. More than 24 hours past due is logged as stale rather
  than fired late.

## Required Railway variables

Set on the n8n service. Brand-prefixed first, bare name as fallback — a missing
key refuses to post rather than posting to the wrong brand's account.

```
PAUSE_ALL=false                      # publishing is paused unless this is false
GITHUB_TOKEN=<PAT, Ora-auto contents:read+write>

FAMILYBOOK_TIKTOK_ACCESS_TOKEN=...
FAMILYBOOK_META_LONG_TOKEN=...
FAMILYBOOK_IG_USER_ID=...
```

YouTube uses an n8n YouTube OAuth2 credential on the `YouTube: Upload` node, not
a Railway variable.
