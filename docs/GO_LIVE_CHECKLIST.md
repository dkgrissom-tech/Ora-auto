# Go-Live by Friday, Aug 14 — Checklist

## TUESDAY Aug 11 (today)
- [ ] Merge the scaffolding PR into `dkgrissom-tech/Ora-auto` (link at end of task)
- [ ] Create YouTube channel: **Grissom Capital Notes** (@GrissomCapitalNotes)
- [ ] Create YouTube channel: **Grissom War Room** (@GrissomWarRoom)
  - Studio → avatar → Switch account → Add account → Brand Account
  - Verify by SMS (unlocks >15 min uploads + custom thumbnails)
  - Set banner, avatar, About with keywords
- [ ] In Google Cloud Console, create 2 projects:
  - `grissom-yt-finance` — enable YouTube Data API v3 + create OAuth 2.0 client
  - `grissom-yt-military` — same
- [ ] Import `workflows/yt-dual-channel-publish.json` into self-hosted n8n
- [ ] Add n8n credentials: `FINANCE_YT_OAUTH`, `MILITARY_YT_OAUTH`, `GITHUB_ORA_AUTO`, `CLAUDE_API`, `ELEVENLABS_API`, `PEXELS_API`

## WEDNESDAY Aug 12
- [ ] Test workflow manually against `brands/finance/posts/2026-08-12.md` (already committed as sample)
- [ ] Fix any auth/quota issues
- [ ] Have Claude generate 4 real scripts (2 finance, 2 military) → commit to `posts/`
- [ ] Activate workflow (toggle to "Active" in n8n)

## THURSDAY Aug 13
- [ ] Confirm first uploads landed as `private` in both YT Studios
- [ ] Confirm `publish_at` fields are correct
- [ ] QA thumbnails and descriptions in Studio
- [ ] If any renders failed, check `logs/yt-2026-08-13.md`

## FRIDAY Aug 14 — LIVE
- [ ] First finance video auto-publishes at 1:00 PM CDT
- [ ] First military video auto-publishes at 6:00 PM CDT
- [ ] Cross-post to Bluesky via existing `grissompress.bsky.social` (add YT link to post file)
- [ ] Share both channel links on your other socials manually or via next workflow iteration

## Success criteria
✅ 2 channels created and verified
✅ 4 videos in the queue by Wed night
✅ First 2 videos public by Fri EOD
✅ Zero manual clicks in Studio to publish (fully automated end-to-end)
