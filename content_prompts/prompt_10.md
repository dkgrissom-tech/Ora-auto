# Prompt 10 — Handy Hearts launch-week visual gratitude

**Brand:** Grissom / Handy Hearts  
**Platform(s):** Instagram  
**Pillar:** Sept. 8 launch week  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Create an Instagram caption for launch week that thanks early readers and invites new readers into Cedar Hollow. It should pair with a warm book-and-porch visual and be useful after launch day, not just on launch morning.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Instagram requires an `image:` path under `brands/grissom/assets/`.
- Schedule during Sept. 8–14, 2026. State that Handy Hearts is Book One and use the exact tagline once. Use 5–8 hashtags.

## Complete worked example of the expected output

```md
---
kind: post
brand: grissom
platforms: [instagram]
scheduled: 2026-09-10T18:00:00-05:00
image: brands/grissom/assets/handy-hearts-launch-week-porch-2026-09-10.jpg
filename: handy-hearts-launch-week-porch-2026-09-10.md
---

Launch week feels a little like standing on a porch with the light on, hoping the right people find their way in.

Thank you for welcoming Handy Hearts into the world. Book One of Cedar Hollow is here.

Grief doesn't end. It changes shape.

#HandyHearts #DKGrissom #SmallTownRomance #SlowBurnRomance #RomanceReaders #BookLaunch #WidowRomance
```
