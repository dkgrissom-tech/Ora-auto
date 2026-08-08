# Prompt 30 — Year-end creator reflection

**Brand:** Cross-brand: Grissom / Ora / Family Book Creator  
**Platform(s):** LinkedIn  
**Pillar:** Creator reflection & next-step planning  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write one LinkedIn year-end reflection for exactly one existing brand: Grissom, Ora, or Family Book Creator. Share a supported lesson about creating stories, product clarity, or preserving memories, and end with one specific next step for the audience.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Output exactly one intake post using only `brand: grissom`, `brand: ora`, or `brand: familybook`; never create a new brand name.
- Keep under 1,200 characters. Do not report metrics or milestones unless supplied. If the chosen brand is Ora, keep it in waitlist mode; if Family Book Creator, do not mention TikTok.

## Complete worked example of the expected output

```md
---
kind: post
brand: grissom
platforms: [linkedin]
scheduled: 2026-12-17T08:00:00-06:00
filename: grissom-year-end-small-stories-2026-12-17.md
---

This year reinforced a simple creative lesson for me: small details are not filler. They are often where readers decide a story feels true.

A porch light. A familiar mug. A town that remembers who needs help before anyone asks. Those details helped shape Cedar Hollow and Handy Hearts.

As the year closes, I am carrying that lesson forward: notice the specific thing, then make room for it on the page.

D.K. Grissom
```
