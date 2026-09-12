# YouTube Dual-Channel Automation Playbook
Repo: `dkgrissom-tech/Ora-auto`
Owner: Don Grissom
Last updated: 2026-08-11

## Channels

| Property | Grissom Capital Notes | Grissom War Room |
|---|---|---|
| Niche | Plain-English finance | Military history storytelling |
| Handle | @GrissomCapitalNotes | @GrissomWarRoom |
| Category ID | 25 (News/Politics) | 27 (Education) |
| Target length | 6–10 min | 10–14 min |
| Cadence (week 1) | 2/week (Tue, Fri) | 2/week (Wed, Sat) |
| Voice (ElevenLabs) | analyst_male_calm | narrator_male_documentary |
| GCP project | `grissom-yt-finance` | `grissom-yt-military` |
| n8n credential name | `FINANCE_YT_OAUTH` | `MILITARY_YT_OAUTH` |

## Folder layout (added to Ora-auto)

```
brands/
  finance/posts/YYYY-MM-DD.md      ← queue, one script per file
  finance/video_scripts/            ← Claude-generated long scripts
  military/posts/YYYY-MM-DD.md
  military/video_scripts/
video_drafts/
  finance/                          ← rendered .mp4 outputs
  military/
workflows/
  yt-dual-channel-publish.json      ← import into self-hosted n8n
```

## Post file frontmatter contract

Every post file MUST have this frontmatter (see brands/finance/posts/ example):

- `youtube_channel`: `finance` | `military`  (Switch node keys on this)
- `title`: ≤ 60 chars, keyword front-loaded
- `description`: keyword in first 150 chars, chapters, disclaimer
- `tags`: 5–10 items
- `category_id`: 25 or 27
- `made_for_kids`: `false`
- `privacy`: `private` (n8n schedules public via publish_at)
- `publish_at`: ISO 8601 with tz
- `thumbnail_prompt`: passed to Canva or image gen
- `duration_target_sec`: for renderer
- `voice`: ElevenLabs voice key
- `posted`: `false` on create, workflow flips to `true`
- `video_id`: `null` on create, workflow writes YT ID

## Cadence (avoid Actions collisions)

- `:05` = existing auto_post (GitHub Actions)
- `:15` = **new yt-dual-channel-publish (n8n)** ← this workflow
- `:50` = existing ingest_clone_drafts (GitHub Actions)

## YouTube best practices baked in

1. Upload with `privacyStatus=private` + `publishAt` → scheduled drop
2. Chapters in description (auto-parsed from `##` sections in script)
3. Custom thumbnail via `thumbnails.set` after upload
4. Category ID set per channel
5. `madeForKids: false` hardcoded
6. Tags 5–10, no tag stuffing
7. Quota: ~1,600 units/upload; 10,000/day/GCP project → separate projects per channel gives ~6 uploads/day each
8. Error Trigger → logs/yt-YYYY-MM-DD.md + Bluesky DM

## Weekly workflow (you)

**Mon:** Claude Pro drafts 2 finance + 2 military scripts. Save into `posts/`.
**Tue-Sat:** Workflow runs hourly at :15, picks up unposted rows, renders, uploads scheduled.
**Sun:** Review YT Studio analytics, tweak next week's topics.
