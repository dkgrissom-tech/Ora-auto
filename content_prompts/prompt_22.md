# Prompt 22 — Family memory interview question

**Brand:** Family Book Creator  
**Platform(s):** Threads  
**Pillar:** Community engagement & memory prompts  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a gentle Threads prompt that gives families one easy question to ask an older relative. The post should stand alone as useful content, then lightly mention Family Book Creator as a place to keep the answer.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Keep it under 400 characters, lead with the exact interview question in quotation marks, and use no more than two hashtags.
- Do not use TikTok or imply Family Book Creator has a TikTok presence.

## Complete worked example of the expected output

```md
---
kind: post
brand: familybook
platforms: [threads]
scheduled: 2026-08-23T18:00:00-05:00
filename: familybook-favorite-kitchen-memory-2026-08-23.md
---

"What is one kitchen memory you hope our family never forgets?"

Questions like this do more than collect facts. They invite a story, a voice, and sometimes a laugh you have not heard in years.

Keep the answers you love with Family Book Creator.

#FamilyMemories #MemoryKeeping
```
