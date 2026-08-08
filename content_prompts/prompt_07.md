# Prompt 07 — Cedar Hollow reader question

**Brand:** Grissom / Handy Hearts  
**Platform(s):** Threads  
**Pillar:** Community conversation  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a warm conversation-starter asking romance readers what makes a fictional small town feel real. Tie the prompt lightly to Cedar Hollow and encourage replies without asking for a purchase.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Cedar Hollow is a fictional town in Muskogee County, Oklahoma, population 1,847.
- Keep it under 350 characters. Ask one clear question and use no more than two hashtags.

## Complete worked example of the expected output

```md
---
kind: post
brand: grissom
platforms: [threads]
scheduled: 2026-09-01T18:00:00-05:00
filename: cedar-hollow-small-town-question-2026-09-01.md
---

For me, a fictional small town feels real when people remember the tiny things: who takes coffee black, which porch needs fixing, who will show up before you ask.

What detail makes a romance town feel like home to you?

#SmallTownRomance #HandyHearts
```
