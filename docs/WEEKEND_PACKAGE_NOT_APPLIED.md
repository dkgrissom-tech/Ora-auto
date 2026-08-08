# Weekend handoff package — files deliberately NOT applied

**Date:** 2026-08-08
**Source:** `ora-auto` handoff zip (54 files)

The package overlapped 41 files that already exist in this repo. The repo versions are
**newer and verified against the live instance**; the package versions describe an
architecture this instance does not run. Overwriting them would have been a regression,
so they were left alone. This file records the decision so the same zip doesn't get
re-applied later.

## Not applied — repo version kept

| Path | Why the repo version wins |
|---|---|
| `marketing_plan.md` | Repo version (15.6 KB vs 11.5 KB) is operational and dated Aug 7 7:18 PM CDT. It carries the **Cedar Hollow = Muskogee County, Oklahoma** correction, the "no Grissom TikTok blocks" rule, and the "do not post to X unless specifically approved" rule. The package version reintroduces X as Ora's 60% primary channel and schedules Grissom TikTok — both reversals of live decisions. |
| `content_prompts/prompt_01.md` … `prompt_30.md` (30 files) | Repo prompts are ~2x longer, brand-scoped, and carry pillar/cadence/hard-constraint sections. Package prompts are generic multi-brand rewrites with `[INSERT TOPIC]` placeholders. |
| `docs/platform_playbooks/*.md` (8 files) | Repo playbooks are ~2x longer and platform-verified. |
| `docs/n8n-env-var-checklist.md` | Package version instructs adding **n8n Variables (`$vars`)**. Community edition has no `$vars`. Repo version documents the Railway `$env` path that actually works. |
| `docs/n8n-workflow-map.md` | Package version maps the v1 direct-to-platform architecture and the `content_drafts/` queue. Repo version is marked "Last verified: 2026-08-07 against the live instance" and maps the Postiz v3 architecture. |

## Applied

| Path | Note |
|---|---|
| `WEEKEND_BLOCKERS.md` | New. A correction banner was prepended — items 11/12 and the `$vars` instructions are wrong for this instance. |
| `docs/video_api_contracts.md` | New. No repo equivalent. |
| `server/yt_studio/**` (7 files) | New. Module 3 was at 0%; this is the first code for it. Not deployed. |
| `server/content_ideas_generator/api/**` (2 files) | New. Not deployed. |
| `n8n_workflows/archive/workflow_*_v1.json` | Archived, **not** placed in `n8n_workflows/` and **not** imported. See `n8n_workflows/archive/README.md`. |

## Two structural conflicts still needing a decision

1. **Publisher ownership.** The package assumes n8n publishes and GitHub Actions is
   retired. The current working boundary is n8n = producer, Actions = publisher, with a
   dormant n8n publisher left inert on purpose because two publishers duplicate posts and
   delete drafts before ingestion. Nothing in this PR changes that.
2. **Queue path.** Package pipelines read `content_drafts/<brand>/*.md`. Nothing writes
   there. The live queue is `brands/<brand>/posts/YYYY-MM-DD.md` with `## HH:MM UTC`
   blocks per `scripts/run_scheduler.py`, which is where the 53 ingested Handy Hearts
   drafts live.
