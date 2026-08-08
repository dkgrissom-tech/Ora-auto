# Prompt 15 — Ora founder insight

**Brand:** Ora  
**Platform(s):** LinkedIn  
**Pillar:** Product thinking & credibility  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a LinkedIn post about why faceless product demonstrations can improve clarity. Use Zara as Ora's AI persona, describe one design principle, and end with a low-pressure waitlist invitation.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Keep it under 1,200 characters; use a strong opening and short paragraphs.
- Do not claim performance metrics, customer adoption, or a product capability without verified input.

## Complete worked example of the expected output

```md
---
kind: post
brand: ora
platforms: [linkedin]
scheduled: 2026-08-26T08:00:00-05:00
filename: ora-faceless-demo-design-principle-2026-08-26.md
---

A product demo should make the next step clearer, not make the presenter the story.

That is one reason we use Zara, Ora's AI persona, in early faceless demos. The format keeps attention on the workflow and gives us a repeatable way to explain the product without adding another layer of presentation.

Ora is currently building its waitlist. Follow @meetora or join at https://meetora-app.pplx.app for future updates.
```
