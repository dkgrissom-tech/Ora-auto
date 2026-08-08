# Prompt 13 — Ora problem-first waitlist conversation

**Brand:** Ora  
**Platform(s):** Threads  
**Pillar:** Audience problem discovery  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a Threads post that opens with a relatable workflow friction and asks a genuine question. Mention that Ora is building toward a better experience, but keep the focus on listening and the waitlist rather than an unverified promise.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Do not name or imply a feature unless it is confirmed in the prompt input.
- Keep it under 400 characters, include one question, and use at most two hashtags.

## Complete worked example of the expected output

```md
---
kind: post
brand: ora
platforms: [threads]
scheduled: 2026-08-21T17:00:00-05:00
filename: ora-workflow-friction-question-2026-08-21.md
---

The best product ideas often start with one repeated moment of friction.

What is the small task in your day that feels more complicated than it should?

Ora is in waitlist mode, and we are listening.

#MeetOra #ProductBuilding
```
