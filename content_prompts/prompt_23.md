# Prompt 23 — Family Book Creator small memory note

**Brand:** Family Book Creator  
**Platform(s):** Bluesky  
**Pillar:** Everyday memory keeping  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a short Bluesky post that names one overlooked kind of family memory and nudges readers to save it today. Keep the brand mention soft and useful.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Keep under 300 characters.
- Use `familybookcreator.app` as the only external destination if a URL is needed. Do not add an image requirement for Bluesky.

## Complete worked example of the expected output

```md
---
kind: post
brand: familybook
platforms: [bluesky]
scheduled: 2026-08-25T10:00:00-05:00
filename: familybook-save-the-sayings-2026-08-25.md
---

Save the sayings, too.

The phrase your uncle repeats. The nickname only one person uses. The line that makes everyone at the table laugh before the story even begins.

Those are family history. Family Book Creator: familybookcreator.app
```
