# Prompt 09 — Handy Hearts launch-day announcement

**Brand:** Grissom / Handy Hearts  
**Platform(s):** Bluesky  
**Pillar:** Sept. 8 launch week  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write the launch-day announcement for Handy Hearts. State that it is available today, name D.K. Grissom and the series tagline, and direct readers to the Cedar Hollow landing page. The feeling should be grateful, grounded, and clear.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- This is specifically for Tuesday, September 8, 2026.
- Do not call it a preorder. Do not claim bestseller status, retailer availability, or reviews not supplied. Keep it under 300 characters.

## Complete worked example of the expected output

```md
---
kind: post
brand: grissom
platforms: [bluesky]
scheduled: 2026-09-08T08:00:00-05:00
filename: handy-hearts-launch-day-2026-09-08.md
---

Handy Hearts is out today.

Book One of the Cedar Hollow series by D.K. Grissom: a small-town romance about love, loss, and what we carry forward.

Grief doesn't end. It changes shape.

Find it at cedarhollow.pplx.app
```
