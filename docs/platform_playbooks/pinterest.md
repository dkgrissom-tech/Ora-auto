# Pinterest playbook

**Status: BLOCKED UPSTREAM — the Pinterest developer app is awaiting resubmission, so queued pins will fail until that approval clears.**

## Publish-ready creative

- **Image Pin:** use a 1000×1500 (2:3) vertical JPG or PNG as the working standard. Pinterest accepts BMP, JPEG, PNG, TIFF, and WEBP; titles max at 100 characters and descriptions max at 800. [Pinterest Pin specs](https://help.pinterest.com/en/article/review-pin-specs)
- **Video Pin:** use 1080×1920 (9:16), H.264 or H.265, four seconds to five minutes. Pinterest also supports 1:2, 2:3, 3:4, 4:5, and 1:1 video ratios. [Pinterest video specs](https://help.pinterest.com/en/article/review-pin-specs)
- **File size:** Pinterest’s current organic Pin-spec page does not publish a file-size ceiling; keep source files web-ready and test the actual upload after app approval rather than inventing a limit. [Pinterest Pin specs](https://help.pinterest.com/en/article/review-pin-specs)
- **Safe layout:** keep text clear of the 270 px top, 65 px left, 195 px right, and 790 px bottom safe-zone guidance for vertical Pins. [Pinterest Pin specs](https://help.pinterest.com/en/article/review-pin-specs)

## Cadence, reach, and hashtags

- **Operating ceiling:** three to five *fresh* Pins per brand per day once unblocked; use a new image/URL/copy combination rather than repeatedly saving the same creative.
- **What gets throttled or removed:** unapproved automation, duplicate or deceptive Pins, irrelevant links, and spammy behavior are policy risks. Pinterest says it removes spam and prohibits unapproved automation. [Pinterest Community Guidelines](https://policy.pinterest.com/en/community-guidelines)
- **Hashtags:** use no hashtag block. Put exact search phrases in the Pin title, on-image text, and description; Pinterest says descriptions help determine relevance for delivery. [Pinterest Pin specs](https://help.pinterest.com/en/article/review-pin-specs)

## How it is wired here

- The scheduled GitHub Action runs `post_pinterest(brand, text, title, dest_url, image_path)`; it is the live publisher, not Postiz. [workflow](https://github.com/dkgrissom-tech/Ora-auto/blob/main/.github/workflows/auto_post.yml#L3-L6) [Pinterest function](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L265-L296)
- Required GitHub repository secrets per brand: `ORA_PINTEREST_ACCESS_TOKEN` + `ORA_PINTEREST_BOARD_ID`; `GRISSOM_PINTEREST_ACCESS_TOKEN` + `GRISSOM_PINTEREST_BOARD_ID`; or `FAMILYBOOK_PINTEREST_ACCESS_TOKEN` + `FAMILYBOOK_PINTEREST_BOARD_ID`.
- Brand gate: none beyond `ora`, `grissom`, and `familybook`. Optional non-secret destination variables are `ORA_PINTEREST_LINK`, `GRISSOM_PINTEREST_LINK`, and `FAMILYBOOK_PINTEREST_LINK`; `pinterest_url` then falls back to the Grissom or Family Book canonical link. Ora has no code default, so supply the destination URL. [pin-link logic](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L115-L125)
- Failure modes: missing token, board, or image skips; the function sends the image as a GitHub raw URL, cuts title to 100 and description to 500; API rejection and exceptions log `Pinterest FAIL`. App approval remains the known upstream blocker. [Pinterest function](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L265-L296)

## Worked intake-file example

Save as `clone_drafts/grissom/handy-hearts-pinterest-2026-09-08.md`. Both Pin fields are required in every Pinterest intake draft.

```md
---
kind: post
brand: grissom
platforms: [pinterest]
scheduled: 2026-09-08T20:00:00-05:00
image: brands/grissom/assets/handy-hearts-pinterest-1000x1500.jpg
pinterest_title: Handy Hearts: Small-Town Romance in Oklahoma
pinterest_url: https://cedarhollow.pplx.app
filename: handy-hearts-pinterest-2026-09-08.md
---
A tender small-town romance about grief, a second chance, and the porch that starts it all. Read Handy Hearts by D.K. Grissom.
```

## Preflight checklist

- Do not treat this as a live launch channel until the developer-app resubmission is approved and a real pin succeeds.
- Make the title a readable search phrase and keep it under the scheduler’s 100-character slice.
- Put the commercial destination in `pinterest_url:`; do not rely on a profile-link instruction in body copy.
- Include a committed, repo-relative `image:` path. Pinterest has no usable text-only path in this scheduler.
- Make one fresh 1000×1500 cover for each distinct promise, product, or reader search term.
- Keep text inside the safe zones before rendering the final image.
- Use descriptive image filenames so a human can verify the raw GitHub asset is the intended creative.
- After approval, inspect a live Pin for its title, destination URL, board, and image; the function only logs a status code, not the published Pin URL.

## Intake-format guardrails

- Put exactly one post in a `clone_drafts/<brand>/` Markdown file.
- Open and close YAML frontmatter with `---` fences.
- Keep `kind: post` and the matching `brand:` field.
- Use a bracketed list such as `platforms: [instagram]`, never a prose label.
- Use a full ISO 8601 `scheduled:` value with its UTC offset.
- Use repo-relative `image:` or `video:` paths, never a hosted URL.
- Keep a specific `filename:` that matches the draft’s purpose and date.
- The intake script turns a valid `scheduled:` value into a UTC queue hour; the GitHub Action reads that queue, not this intake file directly. [intake normalization](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/ingest_clone_drafts.py#L189-L209) [scheduled dispatcher](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L339-L373)
