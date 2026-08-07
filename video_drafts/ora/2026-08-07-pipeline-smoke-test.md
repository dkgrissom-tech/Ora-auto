---
brand: ora
video_source: manual
video_url: https://raw.githubusercontent.com/dkgrissom-tech/Ora-auto/main/brands/ora/assets/ora_iphone_demo_9x16.mp4
video_type: short
platforms: tiktok
caption: Ora turns a rambling voice note into a clean, searchable note. No typing.
---

# Smoke test for Video Content Pipeline v2

Purpose: exercise the full pipeline path end to end on one platform, one brand,
one real asset — before any generator API or multi-platform fan-out is trusted.

## Why brand `ora` and not `grissom`

`brands/grissom/assets/` contains only PNGs. The only real video assets in the repo
are the five 9:16 files under `brands/ora/assets/`, so an Ora draft is the only test
that pairs a real brand with a real video. Pointing a Grissom draft at an Ora video
would publish Ora content to a Grissom account.

## Why these field values

- `video_source: manual` skips the YT Studio / CIG generator branch and the 15-minute
  poll loop, so a failure here is unambiguously a publish problem, not a render problem.
- `video_url` is a `raw.githubusercontent.com` link. The repo is public, so TikTok's
  `PULL_FROM_URL` and Instagram's container fetch can both reach it. A private repo or
  a signed URL would fail.
- `platforms: tiktok` — one platform only. TikTok is a single API call, so it's the
  cleanest first signal. Add `instagram` once this passes.
- No `scheduled:` / `time:` — the draft is immediately due, so a manual execution
  picks it up without waiting on the 90-minute window.

## Path this exercises

List folders → GitHub list → filter → fetch → parse frontmatter → Ready to Publish?
→ Route by Video Source (manual) → Fan Out → Resolve Brand Token → Credentials
Present? → TikTok init → Stamp Draft Context → One Marker Per Draft →
Write .posted Marker → Delete Original Draft

A successful run renames this file to `.posted-YYYY-MM-DD.md` and deletes the original,
which is also the proof that the anti-repost write-back works.

## Expected outcomes

| Result | Meaning |
|---|---|
| Ends at `Log Missing Credentials` | `ORA_TIKTOK_ACCESS_TOKEN` is not set in Railway — expected until step 2 is done |
| Ends at `Log Skipped Drafts` | Frontmatter parse problem — check the node's log line for the reason |
| Reaches `Delete Original Draft` | Full path works, and the draft is marked posted |

Nothing here can fire on its own: the workflow is inactive and its schedule trigger is
disabled, and publishing additionally requires `PAUSE_ALL=false`.
