# Phase 4a — Ora Auto-Poster Clone Ingest — Install Guide

Drop-in extension for `dkgrissom-tech/Ora-auto`. Adds the "text clone → scheduler"
bridge. Zero changes to existing files.

## What you're adding

```
Ora-auto/
├── scripts/
│   └── ingest_clone_drafts.py           ← NEW
├── .github/workflows/
│   └── ingest_clone_drafts.yml          ← NEW
├── clone_drafts/                        ← NEW
│   ├── README.md
│   ├── ora/.gitkeep
│   ├── grissom/.gitkeep
│   └── familybook/.gitkeep
└── tests/
    └── test_ingest.py                   ← NEW
```

Nothing in `scripts/run_scheduler.py`, `brands/`, or the existing
`.github/workflows/auto_post.yml` is modified. Fully additive.

## Install

```bash
# from a fresh clone of Ora-auto
git checkout -b phase4a-clone-ingest
unzip /path/to/phase4a_patch.zip -d .

# sanity check
python -m unittest tests.test_ingest

# dry-run against the real repo (writes nothing)
python scripts/ingest_clone_drafts.py --dry-run

git add scripts/ingest_clone_drafts.py \
        .github/workflows/ingest_clone_drafts.yml \
        clone_drafts/ tests/ INSTALL.md
git commit -m "Phase 4a: clone drafts ingest → auto-poster"
git push -u origin phase4a-clone-ingest
gh pr create --fill
```

## How it works (30 seconds)

1. Your Claude Project (loaded with `brain.md`) writes posts as markdown files into `clone_drafts/<brand>/*.md`.
2. GitHub Action **Ingest Clone Drafts** fires at `:50` of every hour.
3. It parses each draft, validates rules (image required for IG/Pinterest, video for TikTok, TikTok only allowed for Ora, etc.), and appends the resulting blocks into `brands/<brand>/posts/YYYY-MM-DD.md` — the same file the existing scheduler already reads.
4. Ingested source files are moved to `clone_drafts/<brand>/_processed/` with a UTC timestamp so nothing gets re-emitted.
5. At `:05` of the next hour, your existing **Auto-Post (Multi-Brand)** workflow reads the updated file and posts.

## Guarantees

- **Never destroys hand-written posts.** Ingested blocks are wrapped in a `<!-- CLONE:START/END -->` fence.
- **Idempotent.** Same block content → same 12-char SHA id → skipped on re-run.
- **Slot-safe.** Auto-slotted posts skip any hour already used in that day's file.
- **Policy-preserving.** TikTok stays Ora-only. `x` stays manual-only.
- **Silent-fail with logs.** Invalid blocks are logged and skipped, not crashed on.

## Turn it on

1. Push the branch, merge the PR.
2. The workflow is scheduled automatically. First run is at the next `:50` of the hour.
3. To smoke-test now: **Actions → Ingest Clone Drafts → Run workflow → dry_run: true**.
4. When you're ready to unpause posting, re-enable workflow `303223510` (the existing `Auto-Post (Multi-Brand)`) in the Actions UI.

## What still needs a human

- **X/Twitter** posts remain manual (existing policy). Draft them in the clone project, ingest logs will show them scheduled, but the scheduler will `log("... X is manual-only by policy — skipping auto-post")`. Copy from your Daily Launch Packet as usual.
- **Approval flow** (optional, later): if you want a "pause between ingest and post" queue, add a `posts_pending/` directory and a manual promote-to-`posts/` step. Not built yet — say the word if you want it.
