# Prompt 28 — Q4 thoughtful-gift conversation

**Brand:** Cross-brand: Grissom Press / Family Book Creator  
**Platform(s):** Threads  
**Pillar:** Seasonal gifting conversation  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write one Threads post that starts a conversation about gifts that create time, memory, or quiet enjoyment. Choose exactly one supported brand angle per run: Grissom Press coloring books or Family Book Creator. Keep the result as one intake post for the corresponding actual brand.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- If using Grissom Press, output `brand: grissom`; if using Family Book Creator, output `brand: familybook`. Never invent a cross-brand folder.
- Keep under 400 characters, ask one genuine question, and do not make unsupported holiday delivery or discount claims.
- Do not use TikTok for Family Book Creator.

## Complete worked example of the expected output

```md
---
kind: post
brand: familybook
platforms: [threads]
scheduled: 2026-11-18T18:00:00-06:00
filename: familybook-gifts-that-keep-stories-2026-11-18.md
---

The gifts people return to are often the ones that make them pause.

A favorite story. A shared activity. A small ritual on a quiet afternoon.

What gift has felt meaningful in your family long after the holiday?

#FamilyKeepsake #HolidayGifts
```
