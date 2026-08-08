# Prompt 01 — Handy Hearts character micro-scene

**Brand:** Grissom / Handy Hearts  
**Platform(s):** Bluesky  
**Pillar:** Character & emotional promise  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a compact, atmospheric post that lets a reader meet Don Rourke through one practical act of care. The goal is emotional recognition, not a plot summary. Use the supplied scheduling slot and keep the call to action soft: visit the Cedar Hollow page or follow for launch updates.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Cedar Hollow is in Muskogee County, Oklahoma (population 1,847). Don is 42, blond going silver, blue-eyed, and a handyman.
- Keep the body under 300 characters and do not overstate the romance or reveal a scene that is not verified.

## Complete worked example of the expected output

```md
---
kind: post
brand: grissom
platforms: [bluesky]
scheduled: 2026-08-20T18:00:00-05:00
filename: handy-hearts-don-porch-light-2026-08-20.md
---

Don Rourke is not much for speeches.

He is the man who notices a porch light burned out, replaces it before dark, and leaves before anyone can thank him.

Handy Hearts by D.K. Grissom arrives September 8.
```
