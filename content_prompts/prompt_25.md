# Prompt 25 — Family Book Creator holiday keepsake pin

**Brand:** Family Book Creator  
**Platform(s):** Pinterest  
**Pillar:** Q4 holiday gifting  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Create a Pinterest pin for an early holiday planner looking for a personal family keepsake. Use a distinctive title, a holiday-ready image path, and the direct Family Book Creator Gumroad link. Give the code only as a genuine offer, not a fake countdown.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Pinterest requires `image:`, `pinterest_title:`, and `pinterest_url:` in YAML.
- Set the destination to `https://grissom77.gumroad.com/l/wcnuhs`. Code `FIRSTBOOK50` is verified. Do not use TikTok for Family Book Creator.

## Complete worked example of the expected output

```md
---
kind: post
brand: familybook
platforms: [pinterest]
scheduled: 2026-11-05T09:00:00-06:00
image: brands/familybook/assets/familybook-holiday-keepsake-pin-2026-11-05.jpg
pinterest_title: Create a Family Story Book for a Meaningful Holiday Gift
pinterest_url: https://grissom77.gumroad.com/l/wcnuhs
filename: familybook-holiday-keepsake-pin-2026-11-05.md
---

A family story book is a gift people can return to long after the wrapping paper is gone. Gather favorite memories, traditions, and everyday details in one keepsake with Family Book Creator. Use code FIRSTBOOK50 at checkout.

#HolidayGiftIdea #FamilyKeepsake #MemoryBook #MeaningfulGifts
```
