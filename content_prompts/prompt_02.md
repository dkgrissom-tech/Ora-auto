# Prompt 02 — Handy Hearts grief-aware craft reflection

**Brand:** Grissom / Handy Hearts  
**Platform(s):** Threads  
**Pillar:** Author voice & grief-aware romance  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a first-person author reflection on one craft choice in portraying grief and new love. Make it specific, humane, and conversational, ending with an invitation to readers to share a thought. Center the series promise rather than treating grief as a problem to solve.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Use the exact series tagline once if it fits naturally: "Grief doesn't end. It changes shape."
- Dana is a widow: never frame a new relationship as getting over her loss. Keep the body under 500 characters and use no more than two hashtags.

## Complete worked example of the expected output

```md
---
kind: post
brand: grissom
platforms: [threads]
scheduled: 2026-08-22T19:00:00-05:00
filename: handy-hearts-grief-is-not-linear-2026-08-22.md
---

While writing Dana, I kept returning to one truth: grief is not a straight road, and laughter is not betrayal.

That is why Handy Hearts makes room for the hard days, the ordinary days, and the surprising ones. Grief doesn't end. It changes shape.

What makes a romance feel emotionally honest to you?

#HandyHearts #RomanceReaders
```
