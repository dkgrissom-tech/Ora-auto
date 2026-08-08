# Threads playbook

**Status: DEAD for Grissom until GitHub secrets `GRISSOM_THREADS_USER_ID` and `GRISSOM_META_LONG_TOKEN` are added; the scheduler otherwise skips the post.**

## Publish-ready creative

- **Text:** write to 500 characters or fewer. Threads’ API supports text, image, video, and carousel posts, while the live function explicitly creates `media_type=TEXT` and truncates the body at 500. [Threads Posts API](https://developers.facebook.com/docs/threads/posts/) [live function](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L204-L233)
- **Still images (manual/future wiring):** use 1080×1350 (4:5) JPG or PNG; current size guidance lists a 100 MB image maximum. Keep the critical copy centered for 1:1 and 9:16 crops. [current Threads size guide](https://moda.app/resources/sizes/threads)
- **Video (manual/future wiring):** render vertical 1080×1920 (9:16) MP4/MOV with H.264, at or under five minutes and 1 GB. The current scheduler cannot publish it because it only requests a text container. [current Threads size guide](https://moda.app/resources/sizes/threads)
- **Carousels:** plan no more than 10 assets and make slide 1 understandable without the rest; this is manual/future work, not a current Action capability.

## Cadence, reach, and hashtags

- **Hard API ceiling:** Threads profiles are limited to 250 API-published posts in a moving 24-hour window. **Operating ceiling:** one to three useful posts a day per brand, not a burst. [Threads API overview](https://developers.facebook.com/docs/threads/overview/)
- **What gets throttled or removed:** treat repetitive sales copy, automated engagement, and guideline-breaking material as distribution risks; Meta applies its Community Standards to Threads content. [Meta Community Standards](https://transparency.meta.com/policies/community-standards/)
- **Hashtags:** use zero to three topical tags, and prefer a complete searchable sentence. Do not copy a long Instagram hashtag block.

## How it is wired here

- The live route is GitHub Actions at `:05` UTC into `scripts/run_scheduler.py`, not Postiz. [Auto-post workflow](https://github.com/dkgrissom-tech/Ora-auto/blob/main/.github/workflows/auto_post.yml#L3-L6)
- Function: `post_threads(brand, text)`.
- Required GitHub repository secrets: `ORA_THREADS_USER_ID` + `ORA_META_LONG_TOKEN`; `GRISSOM_THREADS_USER_ID` + `GRISSOM_META_LONG_TOKEN`; or `FAMILYBOOK_THREADS_USER_ID` + `FAMILYBOOK_META_LONG_TOKEN`. `secret(brand, KEY)` reads `{BRAND}_{KEY}`. [secret helper](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L48-L52) [Threads function](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L204-L233)
- Brand gate: none beyond the three registered brands. The current Grissom checklist records both required Grissom values as missing; without both, Grissom Threads is dead. [current checklist](https://github.com/dkgrissom-tech/Ora-auto/blob/main/docs/n8n-env-var-checklist.md#L49-L53)
- Failure modes: missing token/user ID skips; a failed container creation or publish logs the first response; exceptions log `Threads FAIL`. A malformed successful response with no creation ID will fail in the publish step.

## Worked intake-file example

Save as `clone_drafts/grissom/handy-hearts-threads-2026-09-08.md` after the two Grissom secrets are present.

```md
---
kind: post
brand: grissom
platforms: [threads]
scheduled: 2026-09-08T19:00:00-05:00
image: brands/grissom/assets/handy-hearts-cover-1080x1350.jpg
filename: handy-hearts-threads-2026-09-08.md
---
A widow. A handyman. One porch that has to come down before either of them can begin again.

HANDY HEARTS, Book One of the Cedar Hollow series, is out today. Cedar Hollow is in Oklahoma.
```

## Preflight checklist

- Add the two **GitHub repository** secrets for the specific brand; a token placed in Postiz or a local shell does nothing for this Action.
- Verify the Threads user ID matches the same Meta identity that issued the long-lived token.
- Keep the final body under 500 characters before it reaches Python, including any link and tags.
- Do not expect the `image:` line in the intake example to create a visual post; `media_type` is hard-coded to `TEXT`.
- Treat 1080×1350 JPG/PNG and a sub-10 MB source as a safe hand-off target for future image wiring, not as proof the current function will upload it.
- Avoid sending a burst after a token fix; use the one-to-three-a-day operating cadence.
- Check both creation and publish responses in the Action log. A container can be created and still fail to publish.
- Recheck secret expiry during launch week; missing or expired credentials produce the same skipped/failed outcome to the scheduler.

## Intake-format guardrails

- Put exactly one post in a `clone_drafts/<brand>/` Markdown file.
- Open and close YAML frontmatter with `---` fences.
- Keep `kind: post` and the matching `brand:` field.
- Use a bracketed list such as `platforms: [instagram]`, never a prose label.
- Use a full ISO 8601 `scheduled:` value with its UTC offset.
- Use repo-relative `image:` or `video:` paths, never a hosted URL.
- Keep a specific `filename:` that matches the draft’s purpose and date.
- The intake script turns a valid `scheduled:` value into a UTC queue hour; the GitHub Action reads that queue, not this intake file directly. [intake normalization](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/ingest_clone_drafts.py#L189-L209) [scheduled dispatcher](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L339-L373)
