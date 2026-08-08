# Prompt 16 — Ora evergreen productivity pin

**Brand:** Ora  
**Platform(s):** Pinterest  
**Pillar:** Evergreen discovery  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Create an evergreen Pinterest pin about faceless product demos and Ora's waitlist without making unsupported productivity claims. It must be a visual, searchable pin with Ora's verified destination URL.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Pinterest requires `image:`, `pinterest_title:`, and `pinterest_url:` in the YAML. The image path must be repo-relative.
- Set `pinterest_url: https://meetora-app.pplx.app`. Do not send Pinterest traffic to an invented page.
- Avoid superlatives such as "best" or guaranteed outcomes.

## Complete worked example of the expected output

```md
---
kind: post
brand: ora
platforms: [pinterest]
scheduled: 2026-08-29T09:00:00-05:00
image: brands/ora/assets/zara_lookB_hero.png
pinterest_title: Faceless Product Demo Ideas from Ora
pinterest_url: https://meetora-app.pplx.app
filename: ora-faceless-demo-pin-2026-08-29.md
---

Looking for a clearer way to introduce a product without putting a person on camera? Ora is sharing early faceless demos with Zara, its AI persona, while the product is in waitlist mode. Visit Ora for updates: https://meetora-app.pplx.app

#ProductDemo #FacelessContent #AIProduct #ProductivityIdeas
```
