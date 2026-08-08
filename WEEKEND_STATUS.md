# Weekend Build Status — Aug 8-9, 2026

Live status against `Claude Weekend Master Directions — n8n + Marketing + Video Pipeline`.
**Last updated: 2026-08-07 evening.** Update this file rather than relying on chat history.

| Module | State |
|---|---|
| 1 — n8n workflow consolidation | ~70% |
| 2 — Marketing plan | 0% — not started |
| 3 — Video generator APIs | ~60% — code written and tested, not deployed (needs Replit access) |

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

## Module 3 — Video generator APIs (~60%, code done, deploy blocked)

**Updated 2026-08-08.** The endpoint code now exists in this repo under `server/` and is
smoke-tested. It is **not deployed** — that still needs Replit access, which Computer
does not have.

### Written and tested

| Path | Contents |
|---|---|
| `server/yt_studio/` | `main.py`, `jobstore.py`, `middleware/auth.py`, and 5 routers (`research`, `scripts`, `voice`, `video`, `thumbnail`) |
| `server/content_ideas_generator/api/` | `generate.py`, `status.py`, `jobstore.py` |
| `docs/video_api_contracts.md` | request/response contracts the n8n video pipeline expects |

Verified locally with FastAPI `TestClient`: health endpoints return 200, missing and
wrong `X-API-Key` both return 401, valid key with an unknown job returns 404, CORS allows
`*.replit.app` and rejects other origins, and job state survives a module reload.

### Fixed before it ever ran

- **Job state no longer lives in a dict.** The first draft kept `jobs: dict = {}` in
  module memory. Autoscale sleeps idle containers, and the n8n pipeline polls
  `GET /api/video/:job_id` every 30s — a poll after a sleep would 404 forever on a video
  that had actually rendered. Both services now persist one JSON file per job via
  `jobstore.py`, written atomically.
- **CIG router would not have loaded.** `status.py` used `from .generate import ...` with
  no `__init__.py` anywhere. Package markers added, and both services now try a relative
  import and fall back to a flat one, so they work whether Replit runs them as a package
  or from the project root.
- **CORS glob was dead config.** `allow_origins=["https://*.replit.app"]` never matches —
  Starlette does exact string comparison there. Moved to `allow_origin_regex`.
- **API key comparison** switched to `hmac.compare_digest`, and the expected key is now
  read per request instead of captured at import time.

### Deploy requirements (Don, in Replit)

1. Copy `server/yt_studio/` into the YT Studio workspace, `server/content_ideas_generator/api/`
   into the CIG workspace.
2. `pip install fastapi uvicorn anthropic httpx pillow python-multipart`; CIG also needs
   ffmpeg (`nix-env -iA nixpkgs.ffmpeg`).
3. Secrets: `YT_STUDIO_API_KEY` / `CIG_API_KEY` (separate UUIDs), `ANTHROPIC_API_KEY`,
   `ELEVENLABS_API_KEY`, `API_BASE_URL`.
4. **Set Autoscale max instances = 1 on both.** The file-backed job store fixes restarts,
   not cross-instance routing — the render thread and its output file must stay on the
   same machine.
5. Point `JOB_STORE_DIR` and `VIDEO_DIR` (`CIG_VIDEO_DIR` for CIG) at paths that survive a
   restart. The defaults sit under `/tmp`, which Replit wipes on recycle.
6. Mirror the two API keys into Railway env vars for n8n as `$env.YT_STUDIO_API_KEY` and
   `$env.CIG_API_KEY` — **not** n8n Variables, which Community edition does not have.

Until deployed: `video_source: yt-studio` and `video_source: content-ideas-generator`
drafts still cannot work. **`video_source: manual` is unaffected** and is the whole
pipeline today.

> Renderer note: per the Content Ideas Generator decisions, native **9:16 output with
> burned-in word-synced captions** is the outstanding product gate. Verify vertical
> renders before wiring this to TikTok / Reels / Shorts.

---

## Blockers needing Don

1. **Postiz Public API key** — the key tried on Aug 7 returned `{"msg":"Invalid API key"}`
   from `POST /api/public/v1/integrations`. The path was correct, so the value was wrong.
   Needs the one from Postiz → Settings → Developers → **Public API**.
2. **Decision on the legacy workflow** — deactivate `OCo1e3DoDuk0WY5J` or leave it.
3. **:05 collision** — the short-form n8n workflow and `auto_post.yml` both own
   `clone_drafts/` at :05. One must be disabled before the other activates.
4. **Replit access** for Module 3 deploy — the code is written and tested as of Aug 8, so
   this is now a deploy step, not a build step. Or drop it and stay on `video_source: manual`.
5. **Pinterest** developer-app resubmission — blocked upstream, unrelated to n8n.

## Discrepancies found in the brief

- Brief says short-form drafts live in `content_drafts/`. That path **does not exist**;
  the real one is `clone_drafts/`.
- Brief lists 5 brands including **Grissom Shop** (@grissomshop), but `brands/`,
  `clone_drafts/` and `video_drafts/` only contain `ora`, `grissom`, `familybook`. Either
  Grissom Shop needs folders creating or it isn't a pipeline brand yet. Unresolved.
- Brief references `docs/n8n-env-var-checklist.md` as pre-existing. It did not exist
  until this commit.

## Update — Aug 7, 6:40 PM CDT

### Correction found: both short-form builds read the wrong folder
v2 (and my first v3 attempt) read `clone_drafts/<brand>/*.md` as one-post-per-file
with YAML frontmatter. That is the **intake** folder. `scripts/run_scheduler.py` —
the code `auto_post.yml` actually runs — reads `brands/<brand>/posts/<UTC-today>.md`,
splits on `## `, and fires a block when its UTC hour matches. Different format,
different folder, comma-separated platforms instead of a bracketed list.

Verified from source, not assumed: `run_scheduler.py:53-96` (`parse_today`),
`:38` (`BRANDS`), `:306` (`TIKTOK_ALLOWED_BRANDS = {"ora"}`), `:324` (X is
manual-only by policy).

- Short-Form v3 rebuilt against the real queue: n8n id `zrpFOQ6UpMV0pHzh`,
  19 nodes, inactive, trigger disabled, cron `25 * * * *`.
- v2 renamed `_SUPERSEDED Short-Form v2 (read clone_drafts - wrong queue)`
  (id `71gVEXd7G2OzyIUp`) so it cannot be activated by mistake.
- No PUT/DELETE against the repo: dated files hold many posts, so marking one
  posted would corrupt the day. Hour matching prevents repeats, same as the Action.
- X stays manual-only and TikTok/YouTube stay with the video pipeline. Assertions
  in the builder enforce both.

### Dry-tested against real data
Ran the parser, channel matcher and payload builder locally under `node` over all
24 UTC hours against the actual `brands/grissom/posts/2026-08-08.md`: 6 posts would
publish, 1 block correctly refused (tiktok-only, routed to the video pipeline),
disabled Postiz channels excluded, 404 for brands with no file handled as normal.

### Content gap found
61 of the 66 Pinterest pins scheduled Aug 4-18 have no `pinterest_title` and no
`pinterest_url`. `post_pinterest()` would have titled them all `grissom` with no
destination link. The pipeline now derives a title from the first body line and
takes a link from `{BRAND}_PINTEREST_LINK` / `POSTIZ_DEFAULT_LINK`. The real fix is
at the generator — noted in the Module 2 brief.

### Queue depth (the actual marketing problem)
| Brand | Day files | Runs through |
|---|---|---|
| grissom | 16 | 2026-08-18 |
| ora | 8 | 2026-07-25 (dry 13 days) |
| familybook | 1 | 2026-06-28 (dead) |

Aug 4-18 platform mix: 66 pinterest, 14 threads, 10 bluesky, 9 tiktok,
7 instagram, 3 linkedin. 73% Pinterest, one brand.

### Module 2 handed off, not built
`docs/CLAUDE_MODULE2_BRIEF.md` — brief for Claude/Twin covering both file formats,
the three stale points in the original weekend brief, the grissomshop question,
platform wiring, brand facts, and a 9-point definition of done.

### New env vars
`{BRAND}_PINTEREST_LINK` (optional), `POSTIZ_DEFAULT_LINK` (optional fallback).

## Update — Aug 7, 7:15 PM CDT — PRODUCTION OUTAGE FOUND AND FIXED

### The headline
`auto_post.yml` has been reporting **success while posting almost nothing**. The job
exits 0 even when every individual post fails, so the green checkmarks in the Actions
tab were meaningless. 38 of the last 40 runs were "successful" and Pinterest was
crashing in all of them.

### Root cause (fixed in `e929b45`)
`parse_today()` stores `pinterest_title` as `None` when the meta key is absent.
`main()` then called `p.get("pinterest_title", brand)` — which returns `None`, not
`brand`, because the key *exists* with a `None` value. `title[:100]` then raised
`TypeError: 'NoneType' object is not subscriptable`.

**61 of the 66 Pinterest pins scheduled Aug 4–18 have no `pinterest_title`.**
Pinterest is 73% of the whole queue and the primary Handy Hearts preorder channel,
so this was the single most damaging bug in the system.

Fix:
- `derive_pin_title()` builds a title from the first real body line (strips markdown,
  comments, quotes; converts ` | ` to ` - `; caps at 100 chars)
- `pin_link()` falls back to a brand default (`grissom` → cedarhollow.pplx.app,
  `familybook` → familybookcreator.app), overridable via `{BRAND}_PINTEREST_LINK`
- `title`/`dest_url` guarded inside `post_pinterest` so a `None` can never crash a run
- `link` key omitted entirely when empty rather than sent as `""`

Verified against 19 real pins across 4 day files: 0 crashes, all titles clean.

### Channel status, measured not assumed
| Channel | State | Evidence |
|---|---|---|
| Bluesky | **Working** | CI dry run shows credentials present, app-password format correct |
| Pinterest | **Fixed, awaiting first live run** | first real pin fires 02:00 UTC (9:00 PM CDT Aug 7) |
| Threads | **Still dead** | `Threads keys missing — skipping` — needs `GRISSOM_THREADS_USER_ID` + `GRISSOM_META_LONG_TOKEN` |
| Instagram / LinkedIn / TikTok | untested | no posts due during observed runs |

### Postiz — deprioritized
Don cannot log in. Findings:
- Google sign-in is **permanently broken** on his instance: `/api/auth/oauth/GOOGLE`
  returns a Google URL with **no `client_id`**, so Google rejects it before any
  consent screen. Needs `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` on the Railway
  service to ever work.
- Registration API returns **"Email already exists"** for dkgrissom@gmail.com, so an
  account exists — a fresh signup is not the answer.
- Password reset is a **dead end**: no mail provider is configured, so `/auth/forgot`
  sends nothing. Only a direct DB password write would recover it.
- Signup URL is `/auth` (not `/auth/register`, which 404s). New accounts on this
  instance auto-activate: `activated: provider !== 'LOCAL' || !hasEmail`.

**Conclusion: Postiz is not on the critical path.** The GitHub Action already reaches
Bluesky/Pinterest/Threads/Instagram/LinkedIn. Postiz was only needed for TikTok and
YouTube video. The short-form n8n pipeline (`zrpFOQ6UpMV0pHzh`) stays parked until
Don has a working Postiz key — it is redundant with `auto_post.yml` for everything
except video.

### Next verification
The 02:00 UTC pin is the first live test of the fix. Check the `auto_post.yml` run at
02:05 UTC for `[grissom] Pinterest posted OK`.
