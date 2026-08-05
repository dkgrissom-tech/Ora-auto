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

## Weekly Trend Scan (upgrade path — do this AFTER launch push)

Right now Claude drafts from canon + platform best-practices, not live viral data. To sharpen conversion, layer in a weekly trend scan.

### The 30-minute Sunday ritual

**Step 1 — Ask Perplexity for the week's top hooks (5 min)**

Open a NEW Perplexity chat (not this ongoing one) and paste:

```
Find the top 10 BookTok / Instagram Reels / Threads posts in the last 7 days
in these niches: widow romance, small-town romance, grief romance, second
chance romance, blue collar hero romance. For each, give me:
- Hook line (first 3 seconds of caption or opening line)
- Platform + posting date
- View count / engagement signal
- Sound used (if TikTok/Reel)
- Top 3 comment themes
- Why it worked (1 sentence)

Return as a markdown table.
```

**Step 2 — Save the output (2 min)**

Save the response to a new file in the repo:
```
trends/grissom/2026-WW.md   (WW = ISO week number)
```

Commit via `Commit-CloneFromClipboard` — it lands in the right place automatically.

**Step 3 — Paste top 3 hooks into Claude prompt (5 min)**

When drafting next week's content in the Ora Text Clone project, add this line to the prompt:

```
Here are 3 hooks that went viral this week in adjacent niches. Adapt the
STRUCTURE (not the exact words) to Don Rourke / Dana Whitfield / Cedar Hollow:

1. [paste hook 1]
2. [paste hook 2]
3. [paste hook 3]
```

Claude will produce content that matches proven-viral structure while staying on-brand.

**Step 4 — Track what actually converts (once you have data)**

After 2-3 weeks of posting, check MailerLite + Bluesky analytics:
- Which posts drove the most preorder-link clicks?
- Which emails had the highest open rate?
- Which hooks got the most saves/shares?

Add a `wins.md` file to the trends folder with the top 5 performing hooks + why. THIS is your real conversion data — worth more than any external viral scan.

### Automation (later — free path)

Add a GitHub Action that runs every Sunday at 9am CDT:
1. Reads `trends/grissom/latest.md`
2. Sends you a MailerLite email or Bluesky DM with the top hooks
3. Reminder to run the Sunday ritual

Can build this in an evening when you're ready.

### Paid tools (only if free path fails, per your standing rules)

- **Tokfluence** ($29/mo) — TikTok trend + viral video search
- **ExplodingTopics** ($39/mo) — early trend detection across platforms
- **Metricool** ($22/mo) — competitor content tracking + analytics
- **Publer** ($10/mo) — cross-platform scheduling with analytics

Skip these until your free workflow proves insufficient. The Sunday Perplexity ritual replicates 80% of what these tools do.

### Why this waits until after launch push

Your current 58-slot schedule is built on 2026 platform-best-practice research (sources at the bottom of the schedule PDF). Adding viral-hook adaptation is polish, not foundation. Launch first. Optimize after real conversion data lands.

---

## When something breaks

1. Check the last workflow run: `gh run list -R dkgrissom-tech/Ora-auto --limit 5`
2. Grab logs: `gh run view <ID> --log-failed -R dkgrissom-tech/Ora-auto`
3. Common failures + fixes:
   - **Bluesky 401** → app password wrong. Check `GRISSOM_BLUESKY_HANDLE` len should be 24; regenerate app password if unsure.
   - **MailerLite 422** → sender not verified in MailerLite. Confirm the `from_email` matches a verified sender in your MailerLite account.
   - **"No posts scheduled for hour N"** → filename date is wrong (must be today UTC) OR `## HH:00 UTC` doesn't match current UTC hour.
