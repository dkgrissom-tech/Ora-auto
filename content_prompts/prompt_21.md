# Prompt 21 — Family Book Creator heirloom gift pin

**Brand:** Family Book Creator  
**Platform(s):** Pinterest  
**Pillar:** Gift discovery  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a searchable Pinterest pin for people looking for a meaningful family-memory gift. The destination should be Family Book Creator's verified Gumroad product link, and the copy should be helpful instead of pressure-heavy.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Pinterest requires `image:`, `pinterest_title:`, and `pinterest_url:` in YAML.
- Set `pinterest_url: https://grissom77.gumroad.com/l/wcnuhs`. Mention the verified $29.95 price only if useful; do not make up a discount. Use 3–6 relevant hashtags.

## Complete worked example of the expected output

```md
---
kind: post
brand: familybook
platforms: [pinterest]
scheduled: 2026-08-20T09:00:00-05:00
image: brands/familybook/assets/family-memory-book-gift-pin-2026-08-20.jpg
pinterest_title: A Meaningful Gift for Preserving Family Stories
pinterest_url: https://grissom77.gumroad.com/l/wcnuhs
filename: familybook-memory-book-gift-pin-2026-08-20.md
---

Give the stories in your family a place to live beyond a phone album. Family Book Creator is a $29.95 way to begin collecting favorite memories, traditions, and voices into a keepsake book.

#FamilyGift #MemoryBook #FamilyLegacy #MeaningfulGift
```
