# Phase 4b — Clone Email Sender · Install Guide

This is the email-side counterpart to Phase 4a. It reads campaigns your text
clone writes into `email_drafts/<brand>/*.md` and hands them to MailerLite as
scheduled or instant campaigns. Same architecture as Phase 4a: additive,
free-tier, idempotent.

## What's in the patch

```
scripts/send_clone_emails.py            ← the workhorse
.github/workflows/send_clone_emails.yml ← hourly cron (:35) + manual trigger
email_drafts/README.md                  ← draft format + how the clone should write files
email_drafts/{ora,grissom,familybook}/  ← per-brand inboxes
tests/test_send_clone_emails.py         ← 18 unit tests, all green
INSTALL.md                              ← you are here
```

Nothing in the repo is modified. All files are new. Safe to merge behind
the paused auto-poster workflow.

## Install

```bash
cd /path/to/Ora-auto
unzip /path/to/phase4b_patch.zip -d .
git checkout -b phase4b-email-sender
git add scripts/send_clone_emails.py \
        .github/workflows/send_clone_emails.yml \
        email_drafts/ \
        tests/test_send_clone_emails.py \
        INSTALL.md
git commit -m "Phase 4b: MailerLite email agent for clone drafts"
git push origin phase4b-email-sender
gh pr create --title "Phase 4b: MailerLite email agent" --body "See INSTALL.md."
```

## Add secrets (per brand, all optional up front)

Repo → **Settings → Secrets and variables → Actions → New repository secret**

Add whichever brands you're ready to launch first — brands without secrets
are just skipped, no crash.

| Brand | Secret name | Where to get it |
|---|---|---|
| Ora | `ORA_MAILERLITE_API_KEY` | MailerLite → Integrations → Developer API → Generate |
| Ora | `ORA_MAILERLITE_GROUP_ID` | MailerLite → Subscribers → Groups → click group → copy id from URL |
| Grissom Press | `GRISSOM_MAILERLITE_API_KEY` | same, in Grissom Press account |
| Grissom Press | `GRISSOM_MAILERLITE_GROUP_ID` | same |
| Family Book | `FAMILYBOOK_MAILERLITE_API_KEY` | same, in Family Book account |
| Family Book | `FAMILYBOOK_MAILERLITE_GROUP_ID` | same |

If you're running one MailerLite account for all brands, use the same
API key three times but three different group ids.

## Verify

1. **Dry-run from Actions tab**
   → Actions → *Send Clone Emails* → **Run workflow** → check "Dry run"

2. **Real send test.** Drop a file at `email_drafts/ora/test.md`:

   ```
   ---
   subject: Ora email pipeline test
   from_name: Don at Ora
   from_email: your-verified-sender@yourdomain.com
   ---
   # It works

   If you're reading this, the clone can now email you.
   ```

   Commit + push. Wait for the next :35 cron, or trigger the workflow
   manually (without dry-run). MailerLite will send instantly. The draft
   moves to `email_drafts/ora/_sent/`.

3. **Schedule test.** Same file, add `schedule: 2026-08-05 14:00 UTC` to
   the frontmatter. MailerLite will schedule instead of send.

## How the timing shakes out

| :05 of every hour | Auto-Post (Multi-Brand) — currently paused |
| :35 of every hour | **Send Clone Emails** ← new |
| :50 of every hour | Ingest Clone Drafts |

Fifteen minutes between each workflow so git pull/push races can't collide.

## Rollback

```bash
git revert <phase4b commit sha>
```

Or just delete the workflow file — no other file in the repo depends on it.
