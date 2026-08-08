# Prompt 11 — Ora Zara faceless demo concept

**Brand:** Ora  
**Platform(s):** TikTok  
**Pillar:** Faceless product demo  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Write a compact TikTok video-draft caption for Zara, Ora's AI persona. Use an on-screen hook about escaping post-meeting busywork and a clear waitlist CTA. The video should feel useful even with no human face on camera.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- TikTok is Ora-only. Include a repo-relative `video:` path for the finished vertical video.
- Do not invent a feature, price, release date, or result. TikTok traffic must use the current verified Ora Shopify or waitlist destination and must never route to Amazon.
- This is an intake-formatted video draft, but it belongs in Ora's video workflow for production.

## Complete worked example of the expected output

```md
---
kind: post
brand: ora
platforms: [tiktok]
scheduled: 2026-08-18T12:00:00-05:00
video: brands/ora/assets/zara_meetora_9x16.mp4
filename: ora-zara-waitlist-demo-2026-08-18.md
---

ON-SCREEN: Your meeting ended. The follow-up should not take all afternoon.

Zara is Ora's AI persona, here with a quick faceless early look at Ora.

Ora is in waitlist mode: https://meetora-app.pplx.app
```
