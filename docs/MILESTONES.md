# Ora-auto — Milestones

Chronological log of major wiring, deploys, and pipeline events.

## 2026-08-03 — Clone→GitHub webhook LIVE + PowerShell self-serve

**Status:** production, hands-off end-to-end.

### What went live
- **n8n workflow** `Clone → GitHub commit` deployed on Railway
  (`https://n8n-production-b205b.up.railway.app/webhook/clone-commit`)
- **Fine-grained GitHub PAT** scoped to `dkgrissom-tech/Ora-auto` (Contents R+W, Pull requests R+W) stored as n8n credential
- **Header-auth webhook secret** protects the endpoint (rejects all POSTs missing `X-Webhook-Secret`)
- **Validation stage** enforces payload schema: brand ∈ {ora, grissom, familybook}, kind ∈ {social, email}, filename must be bare `.md` slug
- **Commit path** auto-generated as `clone_drafts/<brand>/<filename>`
- **Response** returns `commit_sha`, `commit_url`, `file_url`

### Producers (upstream)
1. **Claude Pro project** — Ora Text Clone project with custom instructions telling Claude to draft in brand voice AND emit a ready-to-run curl block with every reply
2. **PowerShell functions** on Don's laptop (`$PROFILE`):
   - `Commit-Clone` — opens Notepad with JSON template, commits on save
   - `Commit-CloneFromClipboard` — reads clipboard JSON, commits in one command

### Consumer (downstream)
- **Phase 4a Ingest workflow** (GH Actions, `:50` schedule) picks up new files under `clone_drafts/<brand>/`
- **Phase 4b Email workflow** (GH Actions, `:35` schedule) routes email-kind drafts to MailerLite

### Perf
- First smoke test round-trip: **1.7s** (Claude curl → n8n → GitHub commit landed)
- First real Claude draft ("3am Idea" Ora TikTok caption): **1.5s**

### Files
- Webhook config: `n8n_clone_webhook/clone_commit_webhook.json` (workspace)
- Claude Project instructions: `claude_ora_project_setup.md` (workspace)
- PowerShell setup: `commit_clone_v2.ps1` (workspace)

### Ops notes
- Webhook secret: stored in n8n credentials + Don's PowerShell profile. If leaked, rotate both.
- GitHub PAT: expires per fine-grained token settings. When it expires, regenerate on github.com, update the `GitHub Contents API — Ora-auto` credential in n8n.
- Railway free tier hosts n8n; monitor uptime. Backup: workflow JSON is in this repo's history.

## 2026-08-03 (afternoon) — First real Handy Hearts launch pack committed

Six D.K. Grissom launch drafts committed via the live Claude → PowerShell → n8n → GitHub pipeline in under 20 minutes.

### Drafts landed
- `clone_drafts/grissom/handy-hearts-tiktok-launch-2026-08-03.md` (TikTok #1 — "She Still Wears Her Wedding Ring")
- `clone_drafts/grissom/handy-hearts-tiktok-nancy-wes-tease-2026-08-03.md` (TikTok #2 — sequel-bait)
- `clone_drafts/grissom/handy-hearts-instagram-carousel-2026-08-03.md` (IG 3-slide carousel)
- `clone_drafts/grissom/handy-hearts-pinterest-pin-2026-08-03.md` (Pinterest mood-board pin)
- `clone_drafts/grissom/handy-hearts-tiktok-tropes-trench-coat-2026-08-03.md` (TikTok #3 — viral tropes format)
- `email_drafts/grissom/handy-hearts-prelaunch-announcement-2026-08-03.md` (MailerLite pre-launch email)

All in Cedar Hollow canon: Don Rourke × Dana Whitfield, D.K. Grissom byline, 9/8 launch, tagline "Grief doesn't end. It changes shape."

### Ora Auto-Poster status: PAUSED, ready to wire

- Workflow file: `.github/workflows/auto_post.yml`
- Supports 8 destinations × 3 brands = 24 channels (Bluesky, LinkedIn, Meta/IG, Threads, Pinterest, TikTok per brand)
- **Zero secrets currently configured** — `gh api repos/dkgrissom-tech/Ora-auto/actions/secrets` returns `total_count: 0`
- Cron schedule: `5 * * * *` (top of each hour + 5 min)
- Workflow trigger: paused pending Ora TestFlight Build 100 + credential provisioning

### Next-up plan for wiring live (deferred to tonight/tomorrow)

Recommended sequence — fastest reach for lowest setup pain:

1. **Bluesky** (5 min) — handle + app password only. Best "first win" to prove end-to-end posting.
2. **Threads** (15 min) — Meta developer app + Threads API.
3. **Instagram** (30-60 min) — Meta Business + Facebook Page + long-lived token.
4. **Pinterest** (15 min) — Developer account + app + token.
5. **LinkedIn** (15 min) — Developer app + OAuth (personal or D.K. Grissom author page).
6. **TikTok** (days-weeks) — Content Posting API requires app approval. Start the application in parallel with #1.

Secret names required per platform are defined in `auto_post.yml`. For each brand (`ORA_`, `GRISSOM_`, `FAMILYBOOK_`), the naming convention is:
- `<BRAND>_BLUESKY_HANDLE`, `<BRAND>_BLUESKY_APP_PASSWORD`
- `<BRAND>_LINKEDIN_ACCESS_TOKEN`, `<BRAND>_LINKEDIN_AUTHOR_URN`
- `<BRAND>_META_LONG_TOKEN`, `<BRAND>_INSTAGRAM_USER_ID`, `<BRAND>_THREADS_USER_ID`
- `<BRAND>_PINTEREST_ACCESS_TOKEN`, `<BRAND>_PINTEREST_BOARD_ID`
- `<BRAND>_TIKTOK_ACCESS_TOKEN`

Add via `gh secret set <NAME> -R dkgrissom-tech/Ora-auto` or the repo Settings → Secrets → Actions UI.

### Priority when we resume tonight

Don voted for option **A** — Bluesky first (5 min setup), one clean live post, sleep on it, layer platforms one per day.

For Handy Hearts launch specifically, when full stack is live, priority destinations for the 6 committed drafts:
- **BookTok/TikTok #1, #2, #3** → TikTok (primary), Threads, Bluesky, LinkedIn
- **IG carousel** → Instagram (primary), Threads
- **Pinterest pin** → Pinterest (primary)
- **Pre-launch email** → MailerLite (Phase 4b already wired, needs `MAILERLITE_API_KEY` + `GRISSOM_MAILERLITE_GROUP_ID` secrets)

### Blockers to unpause the Auto-Poster
1. At least one social credential provisioned (Bluesky minimum)
2. Ora TestFlight Build 100 shipped (per earlier build map rule keeping Auto-Post paused during Ora build lockdown)
