# Prompt 14 — Ora building-in-public note

**Brand:** Ora  
**Platform(s):** Bluesky  
**Pillar:** Build-in-public trust  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a short Bluesky building-in-public update about learning from early interest in Ora. It should be transparent and human, with no numerical claims unless supplied, and invite people to follow @meetora for future demos.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Keep it under 300 characters.
- Ora is a waitlist play. Do not claim it is launched or available for purchase.

## Complete worked example of the expected output

```md
---
kind: post
brand: ora
platforms: [bluesky]
scheduled: 2026-08-24T10:00:00-05:00
filename: ora-building-in-public-2026-08-24.md
---

Building Ora means paying close attention to the moments people want to feel simpler.

We are still in waitlist mode, still learning, and sharing early faceless demos with Zara along the way.

Follow @meetora for the next look.
```
