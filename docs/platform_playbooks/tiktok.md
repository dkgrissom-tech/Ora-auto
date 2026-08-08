# TikTok playbook

**Status: LIVE FOR ORA ONLY — the scheduler deliberately skips Grissom and Family Book Creator.**

## Publish-ready creative

- **Caption:** write to 2,200 UTF-16 characters or fewer. Hashtags and @mentions must be separated by spaces or line breaks so TikTok can recognize them; the live scheduler currently truncates text to 150 characters before its API call. [TikTok Direct Post API](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post) [live function](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L298-L333)
- **Video:** use vertical 1080×1920 (9:16), MP4/H.264, with clear audio and burned-in captions. TikTok’s Direct Post page gives MP4 as its example and says it supports many formats, but does not state an aspect-ratio, duration, or total-file-size maximum. [TikTok Direct Post API](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post)
- **Working file limit:** keep a publish asset comfortably below 500 MB. This is an internal delivery target, not a TikTok platform limit; the current API documentation exposes byte size/chunk fields but no maximum upload-size number. [TikTok Direct Post API](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post)
- **Cover:** compose the decisive first second at the center; the function requests the cover at 1,000 ms.

## Cadence, reach, and hashtags

- **Operating ceiling:** one Ora post a day; the API has a six-requests-per-minute token limit and an undisclosed daily post cap, so do not burst retries. [TikTok Direct Post API](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post)
- **What gets throttled or restricted:** repeated posting can hit `spam_risk_too_many_posts`; unaudited clients are restricted to private visibility; platform manipulation and fake engagement are prohibited. [TikTok Direct Post API](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post) [TikTok integrity policy](https://www.tiktok.com/community-guidelines/en/integrity-authenticity)
- **Hashtags:** use three to five specific discovery tags, not a generic #fyp pile. For Ora, favor the actual use case, such as `#VoiceNotes`, `#IdeaCapture`, and `#ADHDTools` only when truthful.

## How it is wired here

- Function: `post_tiktok(brand, text, video_path)` in the hourly GitHub Action scheduler. [TikTok function](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L298-L333)
- Required GitHub repository secret for the only allowed brand: `ORA_TIKTOK_ACCESS_TOKEN`, resolved from `secret("ora", "TIKTOK_ACCESS_TOKEN")`. The workflow also defines Grissom and Family Book variables, but policy prevents their use. [workflow secrets](https://github.com/dkgrissom-tech/Ora-auto/blob/main/.github/workflows/auto_post.yml#L30-L64)
- Brand gate: `TIKTOK_ALLOWED_BRANDS = {"ora"}`. Family Book Creator intentionally skips TikTok, and Grissom is skipped by the same live gate. [policy gate](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L335-L337) [dispatch](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L369-L373)
- Failure modes: missing token or `video:` skips; a non-Ora post is skipped before calling the function; API errors/exceptions log `TikTok FAIL`. The code asks TikTok to pull a public GitHub raw URL, so an uncommitted, incorrect, or inaccessible repo-relative video path cannot publish.

## Worked intake-file example

Save as `clone_drafts/ora/ora-voice-note-tiktok-2026-09-08.md`.

```md
---
kind: post
brand: ora
platforms: [tiktok]
scheduled: 2026-09-08T17:00:00-05:00
video: brands/ora/assets/ora-3am-idea-1080x1920.mp4
filename: ora-voice-note-tiktok-2026-09-08.md
---
That 3 a.m. idea deserves more than a promise you will remember it. Say it to Ora, then go back to sleep. #VoiceNotes #IdeaCapture #MeetOra
```

## Preflight checklist

- Use `brand: ora`; every other brand is deliberately skipped even if its own TikTok token exists.
- Include a `video:` field with a committed repo-relative MP4 path; an `image:` field cannot satisfy the live function.
- Keep the full caption meaningful within 150 characters because that is the code path’s actual truncation point.
- Route a product-focused TikTok call to action to Shopify, not Amazon, per the brand direction.
- Ensure the public GitHub raw video URL is reachable before the scheduled hour; TikTok pulls the asset rather than receiving an uploaded file from Actions.
- Do not count on a test from an unaudited client being publicly visible; TikTok documents private-viewing restrictions for unaudited clients. [TikTok Direct Post API](https://developers.tiktok.com/doc/content-posting-api-reference-direct-post)
- Avoid retry storms: the Action has no backoff or publish-status polling after the initial request.
- Check the returned Action log and TikTok profile separately; an HTTP 200 is the scheduler’s only confirmation.

## Intake-format guardrails

- Put exactly one post in a `clone_drafts/<brand>/` Markdown file.
- Open and close YAML frontmatter with `---` fences.
- Keep `kind: post` and the matching `brand:` field.
- Use a bracketed list such as `platforms: [instagram]`, never a prose label.
- Use a full ISO 8601 `scheduled:` value with its UTC offset.
- Use repo-relative `image:` or `video:` paths, never a hosted URL.
- Keep a specific `filename:` that matches the draft’s purpose and date.
- The intake script turns a valid `scheduled:` value into a UTC queue hour; the GitHub Action reads that queue, not this intake file directly. [intake normalization](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/ingest_clone_drafts.py#L189-L209) [scheduled dispatcher](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L339-L373)
