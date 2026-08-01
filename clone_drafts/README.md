# Clone Drafts — the "in-tray" for the text clone

This is where the **text clone** (Claude Project loaded with `brain.md`) drops
posts that the auto-poster should schedule and publish. It is the last mile of
Phase 4a of the Clone Super Agent build.

## How it flows

```
brain.md  →  Text Clone (Claude Project)
                 │
                 ▼
     clone_drafts/<brand>/<anything>.md      ← YOU or the clone writes here
                 │
                 ▼   (ingest_clone_drafts.py, runs :50 of every hour)
     brands/<brand>/posts/YYYY-MM-DD.md      ← existing scheduler reads here
                 │
                 ▼   (run_scheduler.py, runs :05 of every hour)
        Bluesky / LinkedIn / Threads / IG / Pinterest / TikTok
```

- Drop one `.md` file per topic/session — filename doesn't matter.
- Any number of blocks per file.
- After ingest, the source file is moved to `_processed/` and stamped with a UTC
  timestamp, so the clone never re-emits the same post.

## Draft block format (paste this into your Claude Project as a template)

```
---
date: 2026-08-05
time: 14:00
platforms: bluesky, threads, instagram, pinterest
image: brands/ora/assets/drop1_8am_listening.png
pinterest_title: Just say Ora
pinterest_url: https://meetora-app.pplx.app
---
Say it and it starts listening.
Ora — iPhone only. Waitlist open.
https://meetora-app.pplx.app
```

### Field cheat-sheet

| Field | Required? | Notes |
|---|---|---|
| `date` | no | YYYY-MM-DD (UTC). Defaults to today. |
| `time` | no | HH:MM UTC. If omitted, ingest picks the next open slot from `SLOT_DEFAULTS` for the brand. |
| `platforms` | **yes** | Comma-separated. Any of: `bluesky, x, linkedin, threads, instagram, pinterest, tiktok`. `x` is manual-only by policy (scheduler skips it, on purpose). |
| `image` | conditional | Required for `instagram` and `pinterest`. Path must be a real file in `brands/<brand>/assets/`. |
| `video` | conditional | Required for `tiktok`. |
| `pinterest_title` | optional | Pin title (≤100 chars). |
| `pinterest_url` | optional | Destination URL for the pin. |

### Rules ingest enforces (silent fail with log line, never crash)

- TikTok is only allowed for `ora`. If Grissom/Familybook drafts include tiktok,
  it is dropped from the platforms list.
- Instagram / Pinterest without `image` → skipped.
- TikTok without `video` → skipped.
- Same block content ingested twice → deduped via SHA-256 id in the fence
  `<!-- CLONE:START id=... -->`.
- Auto-slotting never collides with a slot that's already used in that day's file.

## Handy commands

```bash
# Preview what would happen (writes nothing, doesn't move files)
python scripts/ingest_clone_drafts.py --dry-run

# Ingest only Ora drafts
python scripts/ingest_clone_drafts.py --brand ora

# Manual trigger from GitHub Actions
# → Actions tab → "Ingest Clone Drafts" → Run workflow
```

## Where things end up

- Ingested block → `brands/<brand>/posts/YYYY-MM-DD.md`
  (wrapped in `<!-- CLONE:START id=... -->` … `<!-- CLONE:END -->`)
- Original draft file → `clone_drafts/<brand>/_processed/YYYYMMDDTHHMMSSZ__<original>.md`
- Log → `logs/ingest.log` (also uploaded as a workflow artifact each run)
