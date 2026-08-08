# Prompt 29 — Holiday visual ritual post

**Brand:** Cross-brand: Ora / Family Book Creator  
**Platform(s):** Instagram  
**Pillar:** Seasonal reflection  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Create one reflective seasonal Instagram post for either Ora or Family Book Creator. Pick a verified brand angle: Ora's waitlist/early demos or Family Book Creator's memory keeping. It must feel like a helpful end-of-year ritual, not a product claim.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Output exactly one post using either `brand: ora` or `brand: familybook`, with a matching repo-relative `image:` path.
- For Ora, do not invent features or a release date. For Family Book Creator, do not use TikTok or invent a feature. Use 4–7 hashtags.

## Complete worked example of the expected output

```md
---
kind: post
brand: familybook
platforms: [instagram]
scheduled: 2026-12-03T11:00:00-06:00
image: brands/familybook/assets/familybook-year-end-memory-ritual-2026-12-03.jpg
filename: familybook-year-end-memory-ritual-2026-12-03.md
---

Before the year closes, save one story you heard and do not want to lose.

It can be a recipe, a voice note, a photo caption, or the answer to one good question. Small pieces become family history when we keep them.

Family Book Creator: familybookcreator.app

#FamilyMemories #YearEndReflection #MemoryKeeping #FamilyLegacy #Keepsake
```
