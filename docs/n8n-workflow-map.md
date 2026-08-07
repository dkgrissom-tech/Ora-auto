# n8n Workflow Map

Last verified: 2026-08-07 against the live instance.

n8n: `https://n8n-production-b205b.up.railway.app` — self-hosted **Community edition**
on Railway project `pleasing-dream`. Community edition has no `$vars` (Enterprise
only), so every secret is read with `$env.NAME` and set as a Railway service variable.

## What runs when

| Time (UTC) | Owner | What | Path |
|---|---|---|---|
| :05 | **GitHub Actions** (`auto_post.yml`) | posts short-form drafts | `clone_drafts/` |
| :05 | n8n `Short-Form Content Pipeline v2` | same job, n8n replacement — **inactive** | `clone_drafts/` |
| :15 | n8n `Video Content Pipeline v3 (Postiz)` — **inactive** | video | `video_drafts/` |
| :50 | **GitHub Actions** (`ingest_clone_drafts.yml`) | ingests new drafts | `clone_drafts/` |

⚠️ **Collision risk.** The GitHub Action at :05 and the n8n short-form workflow at :05
own the *same* folder. Do not activate the n8n one until `auto_post.yml` is disabled,
or every draft posts twice. The video pipeline is safe — it runs at :15 and only touches
`video_drafts/`, which no Action reads.

## Live workflows

| ID | State | Nodes | Name |
|---|---|---|---|
| `x2rq7UHA72ehb0fx` | **active** | 9 | Clone → GitHub commit |
| `OCo1e3DoDuk0WY5J` | **active** | 5 | Claude Draft v4 — this is the legacy Auto-Post (Multi-Brand) |
| `71gVEXd7G2OzyIUp` | off, trigger disabled | 25 | Short-Form Content Pipeline v2 |
| `Dr1hOvAhcYVHm6l2` | off, trigger disabled | 36 | Video Content Pipeline v2 — superseded by v3 |
| `RTXbEpnpMCU0wywu` | off, trigger disabled | 32 | Video Content Pipeline v3 (Postiz) |

## Fail points and recovery

**Both pipelines**

- `PAUSE_ALL` — the kill switch. Anything other than the string `false` stops the run at
  the second node. Change it in Railway and the n8n service restarts on its own.
- `GITHUB_TOKEN` missing or expired → `List Draft Files` returns 401 and the run ends
  with zero items. Looks identical to "no drafts today," so check the node output rather
  than trusting an empty run.
- `N8N_BLOCK_ENV_ACCESS_IN_NODE` must be unset or `false`, otherwise every Code node
  reading `$env` throws.
- A draft is only marked done at the very end (`Create .posted Marker` → `Delete
  Original Draft`). If the run dies mid-way the draft stays put and retries next hour.
  Safe against loss, but a partial publish **can** repost. Check the platform before
  re-running by hand.

**Video pipeline v3 specifically**

- `Postiz: List Channels` 401 → wrong `POSTIZ_API_KEY`. It must come from Postiz →
  Settings → Developers → **Public API**. The `pca_`/`pcs_` values from the Apps screen
  are OAuth app credentials and are always rejected here.
- `Match Brand Channels` refuses when a platform matches **two** channels for one brand
  rather than guessing. Fix by setting `POSTIZ_CHANNEL_MAP`.
- Render polling gives up after 30 attempts at 30s (15 min) and routes to
  `Log Render Failure`.
- Postiz rate limits: 30 uploads/hour, 90 create-post/hour.

## Manual recovery

The n8n public API v1 has **no run-workflow endpoint** — manual execution has to happen
in the UI. There is also no manual-trigger webhook on either pipeline yet.

To re-post something already marked done: rename `X.posted-YYYY-MM-DD.md` back to `X.md`
and it gets picked up on the next run.

## Known gaps

- Short-form: Instagram, Pinterest and X/Twitter are **stub nodes** that log and stop.
  Only Bluesky, Threads and LinkedIn actually post. MailerLite is left to the existing
  Action.
- Pinterest is blocked upstream on developer-app resubmission regardless of workflow.
- No `posting_log/<date>.md` writing — failures go to execution logs via `console.log`,
  not to the repo.
