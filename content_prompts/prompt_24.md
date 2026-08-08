# Prompt 24 — Family Book Creator collaboration insight

**Brand:** Family Book Creator  
**Platform(s):** LinkedIn  
**Pillar:** Legacy collaboration  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a LinkedIn post about why shared family-history projects work better when they invite contribution rather than demand perfection. Connect the idea to Family Book Creator, a $29.95 product, in a professional, empathetic voice.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Keep below 1,200 characters; short paragraphs; no invented customer stories or statistics.
- You may mention the $5 add-on only if it is directly relevant, and do not invent what the add-on does.

## Complete worked example of the expected output

```md
---
kind: post
brand: familybook
platforms: [linkedin]
scheduled: 2026-08-27T08:00:00-05:00
filename: familybook-shared-history-project-2026-08-27.md
---

The best family-history projects do not begin with perfect archives. They begin with an invitation.

Ask one person for a recipe, another for a photo caption, and someone else for the story behind a familiar name. Contribution lowers the pressure and often makes the result richer.

Family Book Creator is built for people who want to turn those pieces into a keepsake book. The core product is $29.95 at familybookcreator.app.
```
