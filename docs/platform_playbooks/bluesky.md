# Bluesky playbook

**Status: LIVE — text-only through the current GitHub Action, provided the brand secrets exist.**

## Publish-ready creative

- **Text:** keep the finished copy to 300 characters or fewer; the live function hard-cuts it to 300 before sending. Bluesky’s post record supports up to four images, but this publisher does not attach them. [Bluesky post guide](https://docs.bsky.app/docs/advanced-guides/posts)
- **Still images (manual/future wiring):** use JPG, PNG, or WebP; keep each image at or below 1 MB, add meaningful alt text, and use a clear native aspect ratio. The protocol documentation does not prescribe a single pixel dimension. [Bluesky image requirements](https://docs.bsky.app/docs/advanced-guides/posts)
- **Video (manual/future wiring):** deliver MP4 with explicit width/height metadata; Bluesky requires verified email for video uploads and has an undisclosed daily video-post cap. [Bluesky video tutorial](https://docs.bsky.app/docs/tutorials/video)
- **Working creative target:** 1080×1350 (4:5) or 1080×1080 (1:1) stills; 1080×1920 (9:16) MP4 for a future video route. These are composition targets, not a Bluesky API mandate.

## Cadence, reach, and hashtags

- **Operating ceiling:** one or two original feed posts per brand per day; use replies for genuine conversation rather than duplicating the same promotional post.
- **What gets throttled or acted on:** bulk/automated interactions that generate notifications, repetitive posting, and other spam can violate Bluesky’s developer and community rules. [Developer Guidelines](https://docs.bsky.app/docs/support/developer-guidelines) [Community Guidelines](https://bsky.social/about/support/community-guidelines)
- **Hashtags:** use zero to two searchable, reader-facing tags only. Put the important keywords in plain language, not in a hashtag wall.

## How it is wired here

- The live publisher is the hourly `:05` UTC GitHub Action, which runs `scripts/run_scheduler.py`; it is **not** Postiz. [Auto-post workflow](https://github.com/dkgrissom-tech/Ora-auto/blob/main/.github/workflows/auto_post.yml#L3-L6) [scheduler](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L339-L378)
- Function: `post_bluesky(brand, text)`.
- Required GitHub repository secrets, per posting brand: `ORA_BLUESKY_HANDLE` + `ORA_BLUESKY_APP_PASSWORD`; `GRISSOM_BLUESKY_HANDLE` + `GRISSOM_BLUESKY_APP_PASSWORD`; or `FAMILYBOOK_BLUESKY_HANDLE` + `FAMILYBOOK_BLUESKY_APP_PASSWORD`. The helper resolves `secret(brand, "BLUESKY_HANDLE")` as `{BRAND}_BLUESKY_HANDLE` and likewise for the app password. [secret helper and function](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L48-L52) [Bluesky function](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L130-L166)
- Brand gate: none beyond the registered brands `ora`, `grissom`, and `familybook`; Grissom’s handle should be `grissompress.bsky.social`, not `dkgrissom.bsky.social`. [brand registry](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L38-L39)
- Failure modes: missing handle/password logs “keys missing — skipping”; malformed handle is normalized but a bad login or API exception logs `Bluesky FAIL`; `DRY_RUN=true` only logs success. The function sends text only, so an intake `image:` is ignored on Bluesky. [Bluesky function](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L132-L166)

## Worked intake-file example

Save as `clone_drafts/grissom/handy-hearts-bluesky-2026-09-08.md`. This is intake format, so it must be ingested to the UTC queue before the scheduler can see it.

```md
---
kind: post
brand: grissom
platforms: [bluesky]
scheduled: 2026-09-08T18:00:00-05:00
image: brands/grissom/assets/handy-hearts-porch-1080x1350.jpg
filename: handy-hearts-bluesky-2026-09-08.md
---
Cedar Hollow, Oklahoma has a new beginning on the porch.

HANDY HEARTS by D.K. Grissom is out September 8.
Grief doesn't end. It changes shape.
#SmallTownRomance
```

## Preflight checklist

- Confirm the post is intended for `ora`, `grissom`, or `familybook`; no other folder is read by the live scheduler. [brand registry](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L38-L39)
- Confirm the queue time is the converted UTC hour, not merely the local time in the intake file.
- Confirm the GitHub secret is an **app password**, not the account password.
- Remove any leading `@` and accidental whitespace from a saved handle; the function normalizes them, but the actual handle still must authenticate.
- Count links, tags, and spaces within the 300-character final body because code truncation can cut a URL or tag.
- Add alt text in the eventual media workflow; the live function cannot do that work for you.
- Do not assume an attached intake image will post. It is only a creative reference until image embedding is added.
- Check the Action log after the UTC hour; a “posted OK” line is the only success signal from this scheduler.

## Intake-format guardrails

- Put exactly one post in a `clone_drafts/<brand>/` Markdown file.
- Open and close YAML frontmatter with `---` fences.
- Keep `kind: post` and the matching `brand:` field.
- Use a bracketed list such as `platforms: [instagram]`, never a prose label.
- Use a full ISO 8601 `scheduled:` value with its UTC offset.
- Use repo-relative `image:` or `video:` paths, never a hosted URL.
- Keep a specific `filename:` that matches the draft’s purpose and date.
- The intake script turns a valid `scheduled:` value into a UTC queue hour; the GitHub Action reads that queue, not this intake file directly. [intake normalization](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/ingest_clone_drafts.py#L189-L209) [scheduled dispatcher](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L339-L373)
