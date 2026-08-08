# Prompt 17 — Ora before-and-after demo caption

**Brand:** Ora  
**Platform(s):** TikTok  
**Pillar:** Faceless demo education  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Draft the caption and on-screen copy for a short Zara-led TikTok that contrasts a confusing meeting follow-up with a clearer Ora workflow. Keep the contrast focused on the post-meeting experience and avoid numerical claims.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- TikTok is allowed only for Ora. Include a repo-relative `video:` path.
- Route the CTA to the supplied verified Shopify or waitlist URL, never Amazon. Do not invent a before/after metric, product feature, or customer result.

## Complete worked example of the expected output

```md
---
kind: post
brand: ora
platforms: [tiktok]
scheduled: 2026-09-02T12:00:00-05:00
video: brands/ora/assets/zara_dontakenotes_9x16.mp4
filename: ora-zara-clearer-demo-2026-09-02.md
---

ON-SCREEN: A product demo should answer one question at a time.

Zara shows the difference: vague meeting notes first, then a focused look at a clearer follow-up.

Ora is in waitlist mode. Visit https://meetora-app.pplx.app for updates.
```
