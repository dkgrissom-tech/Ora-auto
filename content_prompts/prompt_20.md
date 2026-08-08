# Prompt 20 — Family Book Creator family-story visual

**Brand:** Family Book Creator  
**Platform(s):** Instagram  
**Pillar:** Family legacy & emotional benefit  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Create an Instagram caption that helps a parent or grandparent imagine turning everyday family memories into a meaningful book. Make the product invitation simple and emotionally specific, supported by a warm visual.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Instagram requires `image:` using `brands/familybook/assets/`.
- Use the brand name Family Book Creator and the verified site `familybookcreator.app`. Do not invent feature details or testimonials. Use 4–7 hashtags.

## Complete worked example of the expected output

```md
---
kind: post
brand: familybook
platforms: [instagram]
scheduled: 2026-08-17T11:00:00-05:00
image: brands/familybook/assets/family-story-everyday-moments-2026-08-17.jpg
filename: familybook-everyday-moments-2026-08-17.md
---

The stories worth keeping are often the ordinary ones: a favorite recipe, a road-trip joke, the way someone always signed a card.

Family Book Creator helps make room for those memories in a book your family can hold onto. Learn more at familybookcreator.app

#FamilyMemories #FamilyLegacy #MemoryKeeping #GiftIdea #FamilyBookCreator
```
