# n8n Environment Variable Checklist

Set these as **Railway service variables** on the n8n service in project
`pleasing-dream`. Community edition has no `$vars`, so `$env` + Railway is the only
route. Railway restarts the service on save.

Tick each one as you add it.

## Required by both pipelines

- [ ] `PAUSE_ALL` — set to `true` now. Must be the exact string `false` before anything
      publishes. This is the phone kill switch.
- [ ] `GITHUB_TOKEN` — fine-grained PAT scoped to `dkgrissom-tech/Ora-auto` with
      **Contents: read and write**. Nothing else.
- [ ] `N8N_BLOCK_ENV_ACCESS_IN_NODE` — confirm unset or `false`, or Code nodes cannot
      read `$env` at all.

## Video Content Pipeline v3 (Postiz) — `RTXbEpnpMCU0wywu`

- [ ] `POSTIZ_API_URL` = `https://postiz-v2113-production-a347.up.railway.app`
- [ ] `POSTIZ_API_KEY` — Postiz → Settings → Developers → **Public API**.
      Not the `pca_`/`pcs_` pair from the Apps screen; those are rejected.
- [ ] `POSTIZ_CHANNEL_MAP` — *optional.* Only needed if a brand has two channels on the
      same platform. Shape:
      `{"ora":{"tiktok":"<id>"},"grissom":{"youtube":"<id>"}}`

Because Postiz holds the YouTube / TikTok / Instagram OAuth grants, **none** of these
are needed any more: `YOUTUBE_OAUTH_TOKEN`, `TIKTOK_ACCESS_TOKEN`, and the nine
`{ORA,GRISSOM,FAMILYBOOK}_{TIKTOK_ACCESS_TOKEN,META_LONG_TOKEN,IG_USER_ID}` variables.

### Only for generated video

Skip these entirely if every draft uses `video_source: manual`. Both depend on Module 3,
which is not built.

- [ ] `YT_STUDIO_API_URL` — requires YT Studio deployed off its Replit dev preview
- [ ] `YT_STUDIO_API_KEY`
- [ ] `CIG_API_URL` — requires Content Ideas Generator deployed
- [ ] `CIG_API_KEY`

## Short-Form Content Pipeline v2 — `71gVEXd7G2OzyIUp`

Read via bracket lookup in `Resolve Brand Credentials`: it tries the brand-prefixed name
first, then the bare name. A missing key makes that platform **skip** rather than post to
the wrong brand's account.

Working platforms:

- [ ] `GRISSOM_BLUESKY_HANDLE` — use `grissompress.bsky.social`, not `dkgrissom.bsky.social`
- [ ] `GRISSOM_BLUESKY_APP_PASSWORD`
- [ ] `GRISSOM_THREADS_USER_ID` — **still missing as of Aug 7**
- [ ] `GRISSOM_META_LONG_TOKEN` — **still missing as of Aug 7**
- [ ] `ORA_LINKEDIN_TOKEN`

Stub nodes — setting these does nothing until the nodes are built:

- [ ] `GRISSOM_PINTEREST_ACCESS_TOKEN` / `GRISSOM_PINTEREST_BOARD_ID` — also blocked
      upstream on Pinterest developer-app resubmission
- [ ] `ORA_X_BEARER_TOKEN`
- [ ] MailerLite (`GRISSOM_MAILERLITE_API_KEY`, `GRISSOM_MAILERLITE_GROUP_ID`) — still
      owned by the existing GitHub Action, not n8n

## Bring-up order

1. Set `PAUSE_ALL=true`, `GITHUB_TOKEN`, and the two `POSTIZ_*` variables.
2. Open `RTXbEpnpMCU0wywu`, run manually. It should stop at `PAUSE_ALL Gate`.
3. Set `PAUSE_ALL=false`, run manually again. Watch `Match Brand Channels` resolve real
   channel IDs.
4. Confirm the post in the Postiz calendar and the `.posted-` marker in the repo.
5. Only then enable the schedule trigger and activate.
6. Leave the short-form pipeline alone until `auto_post.yml` is disabled — see the
   :05 collision warning in `n8n-workflow-map.md`.
