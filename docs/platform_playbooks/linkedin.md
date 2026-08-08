# LinkedIn playbook

**Status: LIVE — text-only through the current GitHub Action when each brand’s LinkedIn token and author URN are set.**

## Publish-ready creative

- **Text:** the API limit is 3,000 characters, and the live function truncates body text at exactly 3,000. Lead with the practical insight, then add one concrete proof point and one low-friction next step. [LinkedIn UGC API](https://learn.microsoft.com/en-us/linkedin/compliance/integrations/shares/ugc-post-api)
- **Image (manual/future wiring):** use a 1200×627 (1.91:1) JPG/PNG for link-like business graphics or 1080×1350 (4:5) for a document-style visual; include large readable text. The current function sets `shareMediaCategory` to `NONE` and cannot attach either `image:` or `video:`. [live function](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L168-L202)
- **Video (manual/future wiring):** use MP4/H.264, 1920×1080 (16:9) or 1080×1920 (9:16), captions on, and a concise hook. LinkedIn Pages accept 256×144 through 4096×2304, three seconds through 10 minutes, 10–60 FPS, and up to 5 GB; upload the asset separately before creating a UGC post. [LinkedIn video specifications](https://www.linkedin.com/help/linkedin/answer/a1311816)
- **File size:** use a JPG/PNG under 5 MB for the manual image target, and the cited 5 GB cap for manual Page video. The live text-only scheduler itself has no media-upload limit.

## Cadence, reach, and hashtags

- **Operating ceiling:** one substantive post per brand per business day, or three per week if the post needs a case study, founder voice, or product demo to be useful.
- **What gets throttled or acted on:** irrelevant high-visibility advertising is LinkedIn’s definition of spam; misleading, repetitive, or automated-looking outreach undermines reach and can trigger policy enforcement. [LinkedIn spam guidance](https://www.linkedin.com/help/linkedin/answer/a1344213/recognize-and-report-spam-inappropriate-and-abusive-content?lang=en) [Professional Community Policies](https://www.linkedin.com/legal/professional-community-policies)
- **Hashtags:** use three to five topical tags at most, placed after the copy. Avoid #innovation, #success, and other unqualified tag clutter.

## How it is wired here

- Function: `post_linkedin(brand, text)`, called by the hourly `:05` UTC GitHub Action. [workflow](https://github.com/dkgrissom-tech/Ora-auto/blob/main/.github/workflows/auto_post.yml#L3-L6) [LinkedIn function](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L168-L202)
- Required GitHub repository secrets: `ORA_LINKEDIN_ACCESS_TOKEN` + `ORA_LINKEDIN_AUTHOR_URN`; `GRISSOM_LINKEDIN_ACCESS_TOKEN` + `GRISSOM_LINKEDIN_AUTHOR_URN`; or `FAMILYBOOK_LINKEDIN_ACCESS_TOKEN` + `FAMILYBOOK_LINKEDIN_AUTHOR_URN`.
- Brand gate: none beyond the registered `ora`, `grissom`, and `familybook` list.
- Failure modes: missing token or URN skips; non-200/201 responses log status plus the first 200 characters of body; network/API exceptions log `LinkedIn FAIL`; assets are ignored because the function always posts `shareMediaCategory: NONE`.

## Worked intake-file example

Save as `clone_drafts/ora/ora-linkedin-founder-2026-09-08.md`.

```md
---
kind: post
brand: ora
platforms: [linkedin]
scheduled: 2026-09-08T08:15:00-05:00
image: brands/ora/assets/ora-think-out-loud-1200x627.jpg
filename: ora-linkedin-founder-2026-09-08.md
---
Most idea capture fails before the note exists.

Ora is built for the moment your hands are busy and the thought is about to disappear: speak it, find it later, and keep moving.
```

## Preflight checklist

- Write as a business insight, not a generic cross-post; LinkedIn’s spam definition includes irrelevant high-visibility promotion. [LinkedIn spam guidance](https://www.linkedin.com/help/linkedin/answer/a1344213/recognize-and-report-spam-inappropriate-and-abusive-content?lang=en)
- Check the exact author URN belongs to the intended person or organization before scheduling.
- Keep final text below 3,000 characters because the code silently slices it at that boundary.
- Do not promise that a linked intake image will appear. The function deliberately sets `shareMediaCategory` to `NONE`.
- For a future manual media post, keep an original 1200×627 JPG/PNG or 1920×1080 MP4 available, then verify the current uploader’s limits in LinkedIn itself.
- Avoid posting more than once in a business day unless there is a genuine event or launch update.
- Use line breaks and a single clear CTA rather than an outbound-link stack.
- After publishing, check the visible LinkedIn post as well as the Action log; the function does not return a post URL.

## Intake-format guardrails

- Put exactly one post in a `clone_drafts/<brand>/` Markdown file.
- Open and close YAML frontmatter with `---` fences.
- Keep `kind: post` and the matching `brand:` field.
- Use a bracketed list such as `platforms: [instagram]`, never a prose label.
- Use a full ISO 8601 `scheduled:` value with its UTC offset.
- Use repo-relative `image:` or `video:` paths, never a hosted URL.
- Keep a specific `filename:` that matches the draft’s purpose and date.
- The intake script turns a valid `scheduled:` value into a UTC queue hour; the GitHub Action reads that queue, not this intake file directly. [intake normalization](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/ingest_clone_drafts.py#L189-L209) [scheduled dispatcher](https://github.com/dkgrissom-tech/Ora-auto/blob/main/scripts/run_scheduler.py#L339-L373)
