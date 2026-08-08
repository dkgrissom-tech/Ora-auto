# Prompt 26 — Family Book Creator low-pressure launch prompt

**Brand:** Family Book Creator  
**Platform(s):** Threads  
**Pillar:** Product education & activation  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a Threads post that breaks the blank-page problem into one inviting first step: choose a person, choose a memory, or ask a question. End with a low-pressure invitation to begin with Family Book Creator.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Keep under 400 characters.
- Use the verified $29.95 price only if it helps clarity. Do not imply that the product writes a book automatically or has a feature not confirmed in the brief.

## Complete worked example of the expected output

```md
---
kind: post
brand: familybook
platforms: [threads]
scheduled: 2026-08-31T18:00:00-05:00
filename: familybook-first-step-not-perfect-book-2026-08-31.md
---

Do not start with "I need to make the whole family book."

Start with one person. One question. One memory you would hate to lose.

That is enough to begin. Family Book Creator is here when you are ready to gather the pieces.

#FamilyLegacy #MemoryKeeping
```
