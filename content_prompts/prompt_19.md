# Prompt 19 — Ora early-access reminder

**Brand:** Ora  
**Platform(s):** Instagram  
**Pillar:** Waitlist conversion  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write an Instagram reminder that Ora is still gathering its early community. Use an upcoming Zara faceless demo as the reason to join the waitlist, with an image that makes the post legible in-feed.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Include a repo-relative `image:` path.
- Do not say "last chance," create false urgency, or promise access timing. Use 4–7 hashtags and a verified waitlist destination in natural language.

## Complete worked example of the expected output

```md
---
kind: post
brand: ora
platforms: [instagram]
scheduled: 2026-09-06T17:00:00-05:00
image: brands/ora/assets/drop6_7pm_tomorrow.png
filename: ora-early-access-reminder-2026-09-06.md
---

Ora is still taking shape, and the waitlist is where we share the earliest looks.

If you want to see Zara's next faceless demo, join the Ora waitlist: https://meetora-app.pplx.app

#MeetOra #Waitlist #ProductDemo #AIProduct #EarlyAccess
```
