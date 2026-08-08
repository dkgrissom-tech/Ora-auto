# YouTube playbook

**Status: DEAD — `run_scheduler.py` has no `post_youtube` function or `youtube` dispatch branch, and the intake validator does not accept `youtube`.**

## Publish-ready creative

- **Title and description:** keep titles at 100 characters or fewer and descriptions at 5,000 characters or fewer; put the video’s actual search phrase in the first lines of the description. [YouTube video resource](https://developers.google.com/youtube/v3/docs/videos#snippet.title) [YouTube description guidance](https://support.google.com/youtube/answer/12948449?hl=en)
- **Long-form video:** export MP4 with H.264 video and AAC audio, preserve the native frame rate and aspect ratio, and deliver 16:9 1920×1080 unless the concept is natively vertical. [YouTube upload formatting guidance](https://support.google.com/youtube/answer/4603579?hl=en)
- **Shorts:** use 1080×1920 (9:16) MP4/H.264, captions on, and a complete hook in the first second. This is a production target; it does not create a live scheduler route.
- **File size and duration:** unverified accounts are limited to 15 minutes; verified accounts can exceed that. The maximum upload is 256 GB or 12 hours, whichever is less. [YouTube upload limits](https://support.google.com/youtube/answer/71673?hl=en&co=GENIE.Platform=Desktop)

## Cadence, reach, and hashtags

- **Operating ceiling:** one useful long-form video weekly and up to three Shorts weekly per brand after the publishing route exists. Keep a dependable series cadence rather than dumping a back catalog.
- **What gets throttled or acted on:** excessive, repetitive, or untargeted videos; misleading titles/thumbnails/descriptions; and inorganic promotion violate YouTube’s spam policy. [YouTube spam policy](https://support.google.com/youtube/answer/2801973?hl=en)
- **Hashtags:** use zero to three accurate tags in the description; do not approach YouTube’s 60-hashtag cutoff, at which it ignores all hashtags, and avoid excessive tagging. [YouTube hashtag policy](https://support.google.com/youtube/answer/6390658)

## How it is wired here

- No publisher function exists: the scheduler defines only Bluesky, LinkedIn, Threads, Instagram, Pinterest, and TikTok publishers. Its platform dispatch has no `elif plat == "youtube"`. [scheduler functions](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L130-L333) [dispatch](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L351-L373)
- Required GitHub repository secrets: **none currently**, because there is no YouTube implementation and the Action exports no YouTube OAuth/token secret. [Auto-post workflow](https://github.com/dkgrissom-tech/Ora-auto/blob/main/.github/workflows/auto_post.yml#L26-L66)
- Brand gate: effectively all brands are blocked. The intake script’s `VALID_PLATFORMS` list excludes `youtube`, so a `[youtube]` draft is rejected before it reaches the queue. [intake validation](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/ingest_clone_drafts.py#L83-L84) [validation branch](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/ingest_clone_drafts.py#L227-L239)
- Failure mode: the intake logger reports an unknown platform; if a hand-written queue block somehow contains `youtube`, the scheduler silently has no matching dispatch branch. A video draft alone is not publishable.

## Worked intake-file example

This is the required intake shape, but **do not submit it yet**: it will be rejected until a YouTube publisher and validator support are implemented. Save it as `clone_drafts/grissom/handy-hearts-youtube-2026-09-08.md` only as a held draft.

```md
---
kind: post
brand: grissom
platforms: [youtube]
scheduled: 2026-09-08T16:00:00-05:00
video: brands/grissom/assets/handy-hearts-trailer-1920x1080.mp4
filename: handy-hearts-youtube-2026-09-08.md
---
Handy Hearts official trailer: a second-chance small-town romance set in Cedar Hollow, Oklahoma. Read more at https://cedarhollow.pplx.app
```

## Preflight checklist

- Do not place `platforms: [youtube]` in a production intake batch yet; the validator will reject it as unknown.
- Hold the source MP4 under `video_drafts/` or the brand asset library until an approved YouTube publishing route exists.
- Verify the channel and Google account have phone verification before planning anything over 15 minutes. [YouTube upload limits](https://support.google.com/youtube/answer/71673?hl=en&co=GENIE.Platform=Desktop)
- Make the title promise match the first 30 seconds and thumbnail; misleading metadata is a spam-policy risk. [YouTube spam policy](https://support.google.com/youtube/answer/2801973?hl=en)
- Use a 1280×720, 16:9 JPG/PNG thumbnail under 2 MB as a working production target, then validate it in YouTube Studio before upload. [current thumbnail guide](https://postfa.st/sizes/youtube/thumbnail)
- Keep a caption file, final description, chapters, and links with the video package so manual upload is repeatable.
- Do not assume a video in `video_drafts/` is a scheduled upload. The current GitHub Action never reads that folder.
- The needed remediation is code and OAuth/publishing support, not merely a new repository secret.

## Intake-format guardrails

- The example uses the same one-file, fenced-frontmatter shape as all future intake files.
- Keep `kind: post` and the matching `brand:` value.
- Use a bracketed list and a full ISO 8601 `scheduled:` value with offset.
- Keep media paths repo-relative, never a hosted URL.
- Keep the distinct `filename:` field so the asset package is traceable.
- Do not run this held draft through intake yet: `youtube` is not in `VALID_PLATFORMS`.
- When YouTube support is added, preserve this shape so the scheduler can convert it to a UTC queue block.
- Today, the intake script will log the unknown platform and skip it rather than publishing. [intake validation](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/ingest_clone_drafts.py#L227-L239)
