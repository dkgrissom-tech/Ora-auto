# Prompt 04 — Handy Hearts trope discovery pin

**Brand:** Grissom / Handy Hearts  
**Platform(s):** Pinterest  
**Pillar:** Reader discovery & tropes  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Create one searchable Pinterest pin description that sells the emotional promise of Handy Hearts through verified romance tropes. Use a clear title, an image concept path, and a destination URL that sends prospective readers to the Cedar Hollow landing page.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Pinterest is visual: include `image:`.
- Pinterest output must also include both `pinterest_title:` and `pinterest_url:` in the YAML. Use `https://cedarhollow.pplx.app` as the destination.
- Do not use a bare "link in bio" call to action. Use searchable natural language and 3–6 relevant hashtags.

## Complete worked example of the expected output

```md
---
kind: post
brand: grissom
platforms: [pinterest]
scheduled: 2026-08-27T09:00:00-05:00
image: brands/grissom/assets/handy-hearts-slow-burn-tropes-pin-2026-08-27.jpg
pinterest_title: Slow Burn Small Town Romance with a Handyman Hero
pinterest_url: https://cedarhollow.pplx.app
filename: handy-hearts-slow-burn-tropes-pin-2026-08-27.md
---

Looking for a slow burn small town romance with a steady handyman hero and a heroine finding room for new love? Handy Hearts by D.K. Grissom is a grief-aware romance set in Cedar Hollow, Oklahoma. Arriving September 8, 2026.

#SlowBurnRomance #SmallTownRomance #HandymanHero #WidowRomance #RomanceBooks
```
