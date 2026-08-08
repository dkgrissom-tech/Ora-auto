# Prompt 06 — Reader Circle magnet invitation

**Brand:** Grissom / Handy Hearts  
**Platform(s):** Bluesky  
**Pillar:** Email-list growth & reader connection  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a concise invitation to the Reader Circle that gives readers a reason to visit the Cedar Hollow landing page and learn about the reader magnet novella, The Porch Before. Make it welcoming and specific, never manipulative.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Mention The Porch Before only as the reader magnet novella; do not invent its plot, length, or delivery timing.
- Keep the post under 300 characters and include the landing page as plain text: cedarhollow.pplx.app.

## Complete worked example of the expected output

```md
---
kind: post
brand: grissom
platforms: [bluesky]
scheduled: 2026-08-30T10:00:00-05:00
filename: handy-hearts-reader-circle-invitation-2026-08-30.md
---

Want a little more Cedar Hollow before Handy Hearts arrives?

The Reader Circle is where I share news, behind-the-scenes notes, and The Porch Before, the reader magnet novella.

Join us at cedarhollow.pplx.app
```
