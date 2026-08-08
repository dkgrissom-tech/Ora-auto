# Prompt 27 — Q4 coloring book gift pin

**Brand:** Grissom Press  
**Platform(s):** Pinterest  
**Pillar:** Holiday gift discovery  
**Cadence:** One reusable post; vary the hook and asset for each run without repeating a recent post.

## What to generate

Create a Q4 Pinterest pin for Grissom Press's coloring-book audience. Focus on the Cozy Goth Mega Bundle as a cozy, creative gift and use the verified Gumroad destination. Keep it clearly separate from Handy Hearts romance content.

## Hard constraints

- Return **only one complete intake draft**: start with YAML frontmatter and then the publishable body. Do not add analysis, alternatives, a queue block, or `##` sections.
- The frontmatter must contain exactly the intake essentials: `kind: post`, the stated `brand`, `platforms` as a bracketed list, `scheduled` as a full ISO 8601 timestamp with an offset, and `filename`.
- Use the stated brand and platform only. Keep `platforms` in intake syntax (for example, `[bluesky]`), never the queue's comma-separated syntax.
- `filename` must be a lowercase, hyphenated `.md` name and must agree with the concept and scheduled date.
- The body is plain publishable post text. Do not add a shot list, production notes, markdown heading, or a link placeholder.
- Any `image:` or `video:` value must be a repo-relative path under `brands/<brand>/assets/`, never a URL. Use only an asset that exists or will be created before scheduling.
- Do not invent product features, prices, release dates, characters, locations, or links. Use only the facts supplied in this prompt and the current verified brief.
- Output intake metadata with `brand: grissom`, because Grissom Press content uses the existing Grissom brand folder.
- Pinterest requires `image:`, `pinterest_title:`, and `pinterest_url:`. Set the destination to `https://grissom77.gumroad.com/l/wucxhi`.
- Do not create a new brand folder or call Grissom Shop a separate brand. Use 3–6 search-friendly hashtags.

## Complete worked example of the expected output

```md
---
kind: post
brand: grissom
platforms: [pinterest]
scheduled: 2026-11-12T09:00:00-06:00
image: brands/grissom/assets/cozy-goth-mega-bundle-holiday-pin-2026-11-12.jpg
pinterest_title: Cozy Goth Coloring Book Bundle for Holiday Creativity
pinterest_url: https://grissom77.gumroad.com/l/wucxhi
filename: grissom-cozy-goth-bundle-holiday-pin-2026-11-12.md
---

Give a cozy creative escape this holiday season. The Cozy Goth Mega Bundle from Grissom Press brings darkly delightful coloring pages together for quiet winter afternoons and thoughtful gifts.

#ColoringBookGift #CozyGoth #HolidayGiftIdea #AdultColoring #CreativeGift
```
