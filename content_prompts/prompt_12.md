# Prompt 12 — Ora waitlist visual hook

**Brand:** Ora  
**Platform(s):** Instagram  
**Pillar:** Waitlist awareness  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Create an Instagram post that positions Ora as an early-access product worth watching, using a curiosity-driven visual hook and a non-hyped waitlist invitation. Use only verified, current Ora facts when running the prompt.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Instagram requires `image:` using a repo-relative Ora asset path.
- Ora uses @meetora on Instagram. Do not invent a release date, price, testimonial, or product outcome. Use 4–7 concise hashtags.

## Complete worked example of the expected output

```md
---
kind: post
brand: ora
platforms: [instagram]
scheduled: 2026-08-19T11:00:00-05:00
image: brands/ora/assets/zara_lookB_hero.png
filename: ora-waitlist-visual-hook-2026-08-19.md
---

A better demo does not need a talking head.

Meet Zara, the AI persona behind Ora's faceless walkthroughs. Ora is building a clearer way to handle the work that follows a meeting.

Join the waitlist: https://meetora-app.pplx.app

#MeetOra #AIProduct #ProductDemo #Waitlist #FacelessContent
```
