# Ora-auto — Content Playbook

The 30-second loop for filling the content calendar. Use this any time you want to line up posts + emails for the next N days.

## System state (as of 2026-08-04)

- **Auto-Post (Multi-Brand)** workflow: ACTIVE — fires hourly, matches on today's UTC date + hour
- **Send Clone Emails** workflow: ACTIVE — sends via MailerLite with per-brand sender defaults
- **Ingest Clone Drafts** workflow: ACTIVE — n8n webhook drops drafts in the right folder
- **PowerShell helper**: `Commit-CloneFromClipboard` (defined in `$PROFILE`)

## Grissom brand canon (repeat in every Claude prompt)

- **Hero:** Don Rourke, 42, ex-Navy Seabee, blond silvering, blue eyes
- **Heroine:** Dana Whitfield, widow, honey-blonde, green-eyed, freckled
- **Setting:** Cedar Hollow, Tennessee
- **Byline:** D.K. Grissom (publisher: Grissom Press)
- **Series:** Book 1 Handy Hearts (Don/Dana), Book 2 Hollow Bean (Nancy/Wes), Book 3 Whistlepig Nights (Cal/Ellen)
- **Launch:** 2026-09-08
- **Tagline:** "Grief doesn't end. It changes shape."
- **Voice:** warm, slow-burn, small-town, no melodrama

## The Claude prompt (paste into "Ora Text Clone" project)

```
Draft the next 14 days of Handy Hearts launch content following the
2-week schedule PDF I gave you. Output ONE draft per message so I can
commit them individually with Commit-CloneFromClipboard.

Rules (repeat from project instructions):
- Hero: Don Rourke (42, ex-Navy Seabee, blond silvering, blue eyes)
- Heroine: Dana Whitfield (widow, honey-blonde, green, freckled)
- Setting: Cedar Hollow, Tennessee
- Byline: D.K. Grissom
- Launch: 2026-09-08
- Tagline: "Grief doesn't end. It changes shape."
- Voice: warm, slow-burn, small-town, no melodrama

Start with day 1 (Aug 5). Give me ONE draft with proper frontmatter
(kind: post OR email, brand: grissom, platforms, filename). Then wait
for me to say "next" before drafting day 2.
```

## The commit loop

For each Claude reply:

1. Copy the whole message (⌘A / Ctrl-A inside the code block, or just triple-click)
2. In PowerShell: `Commit-CloneFromClipboard`
3. n8n picks it up, routes to `clone_drafts/grissom/` → `brands/grissom/posts/<date>.md` or `email_drafts/grissom/<name>.md`
4. Say **"next"** to Claude

For 14 drafts, that's ~15 minutes of clipboard shuffling. Zero API burn on Perplexity.

## What each workflow does with committed drafts

### Social posts

- Landing spot: `brands/grissom/posts/<YYYY-MM-DD>.md` (UTC date in filename)
- Format: sections headed by `## HH:MM UTC` — scheduler matches on today's UTC date file AND current hour
- Auto-Poster fires at the top of each hour
- Bluesky is live. Threads/LinkedIn/Pinterest/TikTok wait on approvals

### Emails

- Landing spot: `email_drafts/grissom/<slug>.md`
- Frontmatter fields needed: `subject`, `schedule: YYYY-MM-DD HH:MM UTC`
- Sender defaults inherited from `scripts/send_clone_emails.py` → `D.K. Grissom <dkgrissom@gmail.com>`
- Send Clone Emails workflow creates the MailerLite campaign, schedules it, then archives the draft to `_sent/`

## Safety nets

- **Nothing fires without a schedule.** A draft without a date/time just sits in the folder.
- **Dry-run any time** — from PowerShell:
  ```powershell
  gh workflow run "Auto-Post (Multi-Brand)" -R dkgrissom-tech/Ora-auto -f dry_run=true
  gh workflow run "Send Clone Emails" -R dkgrissom-tech/Ora-auto -f dry_run=true
  ```
- **Check last run** —
  ```powershell
  gh run list -R dkgrissom-tech/Ora-auto --workflow="Auto-Post (Multi-Brand)" --limit 3
  ```

## GitHub secrets currently wired (Grissom brand)

- `GRISSOM_BLUESKY_HANDLE` = `grissompress.bsky.social`
- `GRISSOM_BLUESKY_APP_PASSWORD` = *(rotate any time in bsky.app → Settings → App Passwords)*
- `GRISSOM_MAILERLITE_API_KEY`
- `GRISSOM_MAILERLITE_GROUP_ID` = `194828132607329641` (Grissom List)
- `GRISSOM_PINTEREST_ACCESS_TOKEN` *(pending Pinterest developer app resubmit)*
- `GRISSOM_PINTEREST_BOARD_ID` = `Grissompress/grissom-press-coloring-books`

## Deferred integrations

- **Pinterest** — dev app rejected, needs verified business website
- **Threads** — needs tester approval in Threads app
- **LinkedIn** — needs Grissom Press company page created first
- **TikTok** — API application not yet submitted

## When something breaks

1. Check the last workflow run: `gh run list -R dkgrissom-tech/Ora-auto --limit 5`
2. Grab logs: `gh run view <ID> --log-failed -R dkgrissom-tech/Ora-auto`
3. Common failures + fixes:
   - **Bluesky 401** → app password wrong. Check `GRISSOM_BLUESKY_HANDLE` len should be 24; regenerate app password if unsure.
   - **MailerLite 422** → sender not verified in MailerLite. Confirm the `from_email` matches a verified sender in your MailerLite account.
   - **"No posts scheduled for hour N"** → filename date is wrong (must be today UTC) OR `## HH:00 UTC` doesn't match current UTC hour.
