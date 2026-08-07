# Weekend Build Status — Aug 8-9, 2026

Live status against `Claude Weekend Master Directions — n8n + Marketing + Video Pipeline`.
**Last updated: 2026-08-07 evening.** Update this file rather than relying on chat history.

| Module | State |
|---|---|
| 1 — n8n workflow consolidation | ~70% |
| 2 — Marketing plan | 0% — not started |
| 3 — Video generator APIs | 0% — needs Replit access |

---

## Module 1 — n8n workflows (~70%)

### Done

- **Workflow 2, Video Content Pipeline v3** (`RTXbEpnpMCU0wywu`, 32 nodes) — imported
  inactive, trigger disabled. Publishes via the self-hosted Postiz instance instead of
  calling YouTube / TikTok / Instagram directly.
- **Workflow 1, Short-Form Content Pipeline v2** (`71gVEXd7G2OzyIUp`, 25 nodes) — imported
  inactive, trigger disabled. Bluesky, Threads and LinkedIn post for real.
- `PAUSE_ALL` kill switch on both. Defaults to paused.
- Both workflow JSONs committed under `n8n_workflows/`.
- `docs/n8n-workflow-map.md` and `docs/n8n-env-var-checklist.md`.
- `video_drafts/{ora,grissom,familybook}/README.md` with the frontmatter contract.
- Smoke-test draft at `video_drafts/ora/2026-08-07-pipeline-smoke-test.md`.

### Open

- [ ] **Legacy workflow still active.** `OCo1e3DoDuk0WY5J` (now showing as "Claude Draft
      v4") was supposed to be renamed `_LEGACY_do_not_use` and deactivated. It is still
      running. Not touched because deactivating a live workflow needs Don's say-so.
- [ ] Short-form Instagram, Pinterest and X/Twitter are **stub nodes** that log and stop.
      Brief asked for all three.
- [ ] MailerLite still owned by the GitHub Action, not n8n.
- [ ] `GRISSOM_THREADS_USER_ID` and `GRISSOM_META_LONG_TOKEN` still missing, so Threads
      cannot post.
- [ ] No manual-trigger webhook. The n8n public API has no run endpoint, so manual runs
      are UI-only.
- [ ] No `posting_log/<date>.md` writing — failures go to execution logs only.
- [ ] Neither workflow has run end-to-end yet, so the "executes with no errors" success
      criterion is **unmet**.

---

## Module 2 — Marketing plan (0%)

Nothing exists. Verified missing from the repo: `marketing_plan.md`, `content_prompts/`
(prompts 01-30), `docs/platform_playbooks/` (8 files).

Partial credit elsewhere: a `Handy Hearts Launch — 2-Week Content Schedule` PDF was built
in an earlier session, and the 7-phase Cedar Hollow marketing calendar exists in notes.
Neither is in the repo, and neither covers Aug 7 → Dec 31 across all brands.

This is the largest untouched chunk and the one most tied to the **Sept 8 Handy Hearts
launch** — 32 days out.

---

## Module 3 — Video generator APIs (0%, blocked)

Requires adding REST endpoints to YT Studio and Content Ideas Generator inside Don's
Replit workspaces and deploying both to Autoscale. Computer has no access to those
workspaces, so this cannot be done for him — only specced.

Consequence: `video_source: yt-studio` and `video_source: content-ideas-generator` drafts
cannot work. **`video_source: manual` is unaffected** and is the whole pipeline today.

---

## Blockers needing Don

1. **Postiz Public API key** — the key tried on Aug 7 returned `{"msg":"Invalid API key"}`
   from `POST /api/public/v1/integrations`. The path was correct, so the value was wrong.
   Needs the one from Postiz → Settings → Developers → **Public API**.
2. **Decision on the legacy workflow** — deactivate `OCo1e3DoDuk0WY5J` or leave it.
3. **:05 collision** — the short-form n8n workflow and `auto_post.yml` both own
   `clone_drafts/` at :05. One must be disabled before the other activates.
4. **Replit access** for Module 3, or drop it and stay on `video_source: manual`.
5. **Pinterest** developer-app resubmission — blocked upstream, unrelated to n8n.

## Discrepancies found in the brief

- Brief says short-form drafts live in `content_drafts/`. That path **does not exist**;
  the real one is `clone_drafts/`.
- Brief lists 5 brands including **Grissom Shop** (@grissomshop), but `brands/`,
  `clone_drafts/` and `video_drafts/` only contain `ora`, `grissom`, `familybook`. Either
  Grissom Shop needs folders creating or it isn't a pipeline brand yet. Unresolved.
- Brief references `docs/n8n-env-var-checklist.md` as pre-existing. It did not exist
  until this commit.
