# Prompt 08 — Why quiet competence reads romantic

**Brand:** Grissom / Handy Hearts  
**Platform(s):** LinkedIn  
**Pillar:** Romance craft & professional insight  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a LinkedIn craft post about quiet competence as a romantic signal. Use Don's handyman role as an illustrative example, then give a transferable writing insight for other storytellers.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Keep the tone practical and professional; do not write a fictional excerpt.
- Don is a 42-year-old handyman, not a military hero in the marketing copy. Keep the post under 1,200 characters.

## Complete worked example of the expected output

```md
---
kind: post
brand: grissom
platforms: [linkedin]
scheduled: 2026-09-03T08:30:00-05:00
filename: handy-hearts-quiet-competence-craft-2026-09-03.md
---

Quiet competence is one of the most useful tools in a romance writer's kit.

A character does not need a grand speech to reveal care. Let the reader watch what they notice, what they fix, and what they make easier for someone else.

In Handy Hearts, Don Rourke's work as a handyman lets him communicate through attention long before he is ready to explain himself. The craft lesson is simple: choose actions that carry emotional weight.

Handy Hearts by D.K. Grissom launches September 8.
```
