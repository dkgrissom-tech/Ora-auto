# X playbook

**Status: MANUAL-ONLY — the live scheduler deliberately skips X; draft here, then post by hand.**

## Publish-ready creative

- **Text:** standard Posts allow 280 characters; X also exposes longer-post options to eligible users, but write the main message so it works at 280. [X posting help](https://help.x.com/en/using-x/how-to-post)
- **Images:** attach up to four; API image uploads accept JPG, PNG, GIF, and WebP at up to 5 MB each. Use 1600×900 (16:9) or 1080×1080 (1:1) as working sizes. [X media API best practices](https://docs.x.com/x-api/media/quickstart/best-practices)
- **Video:** use MP4/MOV, H.264/AAC, 1280×720 landscape, 720×1280 portrait, or 720×720 square; X recommends 16:9 or 1:1. Premium Media Studio uploads can be as large as 8 GB, but do not rely on that entitlement for ordinary manual posting. [X media API best practices](https://docs.x.com/x-api/media/quickstart/best-practices) [Media Studio help](https://help.x.com/en/using-x/media-studio-faqs)
- **File size:** use the 5 MB API cap for stills; check the manual uploader’s current limit before a video campaign because eligibility changes by account tier.

## Cadence, reach, and hashtags

- **Operating ceiling:** one to three hand-posted originals per day per account, plus human replies. Do not schedule a wall of near-identical launch posts.
- **What gets throttled or acted on:** inauthentic accounts, behavior, and content intended to manipulate the platform are prohibited; do not automate engagement or reuse deceptive link bait. [X Authenticity policy](https://help.x.com/en/rules-and-policies/authenticity)
- **Hashtags:** use zero to two. If the book title itself is a search term, prefer the exact title in the sentence and one readable tag.

## How it is wired here

- There is **no** `post_x` function. In `main()`, the `x` branch only logs “X is manual-only by policy — skipping auto-post.” [X dispatch branch](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L351-L356)
- Required GitHub repository secrets: **none** for the live scheduler. Do not add X tokens expecting a post; the workflow exports no X secrets. [Auto-post workflow](https://github.com/dkgrissom-tech/Ora-auto/blob/main/.github/workflows/auto_post.yml#L26-L66)
- Brand gate: manual-only for all registered brands. `platforms: [x]` survives the scheduler parse but will never publish automatically.
- Failure mode: policy skip only, not an API failure. A draft can enter the queue, the Action will run, and the log will still show that it was skipped.

## Worked intake-file example

Save as `clone_drafts/grissom/handy-hearts-x-manual-2026-09-08.md`, then copy the body to X manually at the scheduled time.

```md
---
kind: post
brand: grissom
platforms: [x]
scheduled: 2026-09-08T12:00:00-05:00
image: brands/grissom/assets/handy-hearts-cover-1600x900.jpg
filename: handy-hearts-x-manual-2026-09-08.md
---
HANDY HEARTS is out today.

A widowed woman. A quiet handyman. A small Oklahoma town that knows grief changes shape.
https://cedarhollow.pplx.app
```

## Preflight checklist

- Treat `platforms: [x]` as a reminder draft, not an automated task; copy it into X manually.
- Confirm that the account and browser session are correct before pasting the post.
- Recount the final body in X’s composer; links and current entitlement can affect the available space.
- Attach the visual manually and use its native crop, not only the intake path.
- If adding a video, check the account’s live upload UI rather than assuming the Media Studio maximum applies.
- Post during the intended local window, then reply from the account only when the reply is genuinely useful.
- Record the live URL in the campaign notes if it needs later reporting; the scheduler creates no audit record for X.
- Do not add X API secrets merely to “fix” the skip. This is a policy decision in source, not missing configuration.

## Intake-format guardrails

- Put exactly one post in a `clone_drafts/<brand>/` Markdown file.
- Open and close YAML frontmatter with `---` fences.
- Keep `kind: post` and the matching `brand:` field.
- Use a bracketed list such as `platforms: [instagram]`, never a prose label.
- Use a full ISO 8601 `scheduled:` value with its UTC offset.
- Use repo-relative `image:` or `video:` paths, never a hosted URL.
- Keep a specific `filename:` that matches the draft’s purpose and date.
- The intake script turns a valid `scheduled:` value into a UTC queue hour; the GitHub Action reads that queue, not this intake file directly. [intake normalization](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/ingest_clone_drafts.py#L189-L209) [scheduled dispatcher](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L339-L373)
