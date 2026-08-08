# Prompt 03 — Handy Hearts Dana carousel caption

**Brand:** Grissom / Handy Hearts  
**Platform(s):** Instagram  
**Pillar:** Character discovery  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Create a caption for a character-introduction carousel focused on Dana. Lead with a memorable three-beat description, then give a reader-facing reason to care and a concise launch reminder. Pair it with a specific vertical carousel image path.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Instagram posts must include `image:` in frontmatter; use a repo-relative `.jpg` path.
- Dana is honey-blonde, green-eyed, freckled, and a widow. Do not make her grief her only personality. Use 5–8 relevant hashtags.

## Complete worked example of the expected output

```md
---
kind: post
brand: grissom
platforms: [instagram]
scheduled: 2026-08-25T11:00:00-05:00
image: brands/grissom/assets/handy-hearts-meet-dana-carousel-2026-08-25.jpg
filename: handy-hearts-meet-dana-carousel-2026-08-25.md
---

Honey-blonde. Green eyes. Freckles and a sense of humor that shows up right when she needs it.

Meet Dana, the heart of Handy Hearts. She is learning that carrying love forward can look different than she expected.

Book One of the Cedar Hollow series arrives September 8.

#HandyHearts #DKGrissom #SmallTownRomance #WidowRomance #SlowBurnRomance #RomanceReads
```
