# Prompt 05 — Handy Hearts author craft note

**Brand:** Grissom / Handy Hearts  
**Platform(s):** LinkedIn  
**Pillar:** Writing craft & author credibility  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a professional-but-human LinkedIn post about building an interconnected small-town series. Share one concrete creative decision, explain the reader benefit, and connect it to Handy Hearts as Book One without turning the post into a hard sell.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Keep it under 1,200 characters and use short paragraphs.
- Name the pen name D.K. Grissom and the series order accurately: Handy Hearts, then Hollow Bean (Nancy/Wes, spring 2027), then Whistlepig Nights (Cal/Ellen).
- Do not claim an unverified audience result, sales result, or bestseller status.

## Complete worked example of the expected output

```md
---
kind: post
brand: grissom
platforms: [linkedin]
scheduled: 2026-08-28T08:00:00-05:00
filename: handy-hearts-interconnected-series-craft-2026-08-28.md
---

I wanted Cedar Hollow to feel like a place readers could return to, not a backdrop that disappeared after one ending.

So Handy Hearts introduces a community whose supporting characters carry their own unfinished hopes into later books. Nancy and Wes lead Hollow Bean in spring 2027; Cal and Ellen follow in Whistlepig Nights.

For me, an interconnected series is a promise: every book gives a complete love story, while the town keeps breathing around it.

Handy Hearts, Book One by D.K. Grissom, arrives September 8, 2026.
```
