# Instagram playbook

**Status: LIVE — image-feed publishing works when the brand’s Meta token, Instagram user ID, and repo-relative image are present. Reels are not wired.**

## Publish-ready creative

- **Caption:** write a strong first line and keep the production version within Instagram’s 2,200-character caption limit; the live function passes the full caption through rather than truncating it. [Instagram publishing requirements](https://docs.contentstudio.io/article/830-what-are-the-requirements-to-directly-publish-images-and-videos-to-instagram)
- **Feed image:** supply a JPG/JPEG, 320–1440 px wide, in 1.91:1 to 4:5; use 1080×1350 (4:5) as the standard. The current live route uses only `image_url`, so PNG, carousel, Story, and Reel production should be treated as manual/future work unless tested against Meta’s API. [Instagram content-publishing API](https://developers.facebook.com/docs/instagram-platform/instagram-graph-api/reference/ig-user/media/)
- **Reel (manual/future wiring):** use 1080×1920 (9:16) MP4/H.264 with captions and a cover designed for a 4:5 profile-grid crop. Do not put a Reel in the short-form queue and expect `post_instagram` to upload it.
- **File size:** keep the public source image under 8 MB; make it available at the committed repo-relative path so Meta can retrieve the raw GitHub URL. [Instagram publishing requirements](https://docs.contentstudio.io/article/830-what-are-the-requirements-to-directly-publish-images-and-videos-to-instagram)

## Cadence, reach, and hashtags

- **Operating ceiling:** one feed post or Reel per brand a day, plus Stories manually when there is real behind-the-scenes material.
- **What gets reduced or removed:** copied content, fake engagement, repetitive spam, and Community-Guideline violations are risk factors; use original assets and real calls to action. [Instagram Community Guidelines FAQ](https://about.instagram.com/blog/announcements/instagram-community-guidelines-faqs)
- **Hashtags:** use three to five specific tags after the caption, not 20–30 generic tags. For book posts, use reader intent such as `#SmallTownRomance` rather than a broad engagement dump.

## How it is wired here

- Function: `post_instagram(brand, text, image_path)`; it creates an image container at Meta Graph API v21.0, then publishes it. [Instagram function](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L235-L263)
- Required GitHub repository secrets: `ORA_META_LONG_TOKEN` + `ORA_INSTAGRAM_USER_ID`; `GRISSOM_META_LONG_TOKEN` + `GRISSOM_INSTAGRAM_USER_ID`; or `FAMILYBOOK_META_LONG_TOKEN` + `FAMILYBOOK_INSTAGRAM_USER_ID`.
- Brand gate: none beyond `ora`, `grissom`, and `familybook`. An `image:` is mandatory; the function does not consume `video:`.
- Failure modes: no Meta token, user ID, or image logs “missing keys or image — skipping”; failed container creation or publish logs the first API response; exceptions log `Instagram FAIL`. The scheduler’s asset URL points to `main`, so the asset must be committed and publicly reachable first. [asset URL and function](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L127-L129) [Instagram function](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L235-L263)

## Worked intake-file example

Save as `clone_drafts/familybook/family-book-instagram-2026-09-08.md`.

```md
---
kind: post
brand: familybook
platforms: [instagram]
scheduled: 2026-09-08T18:30:00-05:00
image: brands/familybook/assets/first-family-book-1080x1350.jpg
filename: family-book-instagram-2026-09-08.md
---
The stories in your family deserve more than a camera roll.

Start your Family Book today, one memory at a time. Use FIRSTBOOK50 for 50% off your first book.
#FamilyHistory #FamilyStories #MemoryKeeping
```

## Preflight checklist

- Use a committed JPG at the exact repo-relative `image:` path; the scheduler turns that path into a raw GitHub URL.
- Open that raw URL before launch; a 404, private asset, or bad extension becomes a Meta-side publish failure.
- Use 1080×1350 as the default and keep text away from the outer edges for feed crops.
- Make the first caption line work before the “more” break and put the CTA before the hashtags.
- Do not schedule a `video:` field expecting a Reel; this function neither reads it nor makes a Reel container.
- Confirm both `META_LONG_TOKEN` and `INSTAGRAM_USER_ID` are GitHub secrets for the same brand.
- If the first Meta request succeeds, still inspect the second publish call in Actions; the code uses a two-step container workflow.
- Keep the source asset under the cited 8 MB target and avoid untested transparency/format conversions.

## Intake-format guardrails

- Put exactly one post in a `clone_drafts/<brand>/` Markdown file.
- Open and close YAML frontmatter with `---` fences.
- Keep `kind: post` and the matching `brand:` field.
- Use a bracketed list such as `platforms: [instagram]`, never a prose label.
- Use a full ISO 8601 `scheduled:` value with its UTC offset.
- Use repo-relative `image:` or `video:` paths, never a hosted URL.
- Keep a specific `filename:` that matches the draft’s purpose and date.
- The intake script turns a valid `scheduled:` value into a UTC queue hour; the GitHub Action reads that queue, not this intake file directly. [intake normalization](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/ingest_clone_drafts.py#L189-L209) [scheduled dispatcher](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L339-L373)
