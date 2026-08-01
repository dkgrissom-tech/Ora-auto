# Email Drafts — the "in-tray" for the email agent

This is where the **text clone** drops email campaigns for MailerLite to
deliver. It's the email-side counterpart to `clone_drafts/`.

## Flow

```
brain.md → Text Clone (Claude Project)
                 │
                 ▼
     email_drafts/<brand>/<anything>.md      ← YOU or the clone writes here
                 │
                 ▼   (send_clone_emails.py, runs :35 of every hour)
     MailerLite campaign (scheduled or instant)
                 │
                 ▼
              Subscribers
```

After a successful create+schedule call, the source draft moves to
`email_drafts/<brand>/_sent/` with a UTC timestamp and a 12-char content id,
so the clone can't accidentally re-send the same campaign.

## Draft format

```
---
subject: Ora goes live in 72 hours
from_name: Don at Ora
from_email: hello@meetora.app
reply_to: don@grissom.tech
schedule: 2026-08-05 14:00 UTC
---
# Ora goes live in 72 hours

Say it and it starts listening.

Founding-user pricing goes away on launch day.

[Join the waitlist](https://meetora-app.pplx.app)
```

### Field cheat-sheet

| Field | Required | Notes |
|---|---|---|
| `subject` | **yes** | ≤255 chars |
| `from_name` | **yes** | Display name |
| `from_email` | **yes** | **Must already be verified in MailerLite for this brand's account** |
| `reply_to` | no | Different reply-to address |
| `schedule` | no | `YYYY-MM-DD HH:MM UTC`. If omitted, the campaign is sent **instantly** on the next :35 cron tick. Must be in the future. |

Body is standard markdown: `#/##/###` headings, `-` or `*` bullets,
`**bold**`, `*italic*`, `[link](url)`. MailerLite auto-appends the required
footer (unsubscribe, account name, address).

## Required secrets — per brand

Add these in **Repo → Settings → Secrets and variables → Actions**:

| Brand | Secrets |
|---|---|
| Ora | `ORA_MAILERLITE_API_KEY`, `ORA_MAILERLITE_GROUP_ID` |
| Grissom | `GRISSOM_MAILERLITE_API_KEY`, `GRISSOM_MAILERLITE_GROUP_ID` |
| Family Book | `FAMILYBOOK_MAILERLITE_API_KEY`, `FAMILYBOOK_MAILERLITE_GROUP_ID` |

You can add them one brand at a time — brands without secrets are simply
skipped with a log line, no crash.

**Get the API key:** MailerLite → Integrations → Developer API → Generate.
**Get the group id:** MailerLite → Subscribers → Groups → click the group,
the id is in the URL, or via `GET /api/groups` with your key.

## Handy commands

```bash
# Preview what would happen (no API calls made)
python scripts/send_clone_emails.py --dry-run

# One brand only
python scripts/send_clone_emails.py --brand ora

# Manual trigger from GitHub Actions
# → Actions tab → "Send Clone Emails" → Run workflow
```

## Where things end up

- Sent draft → `email_drafts/<brand>/_sent/YYYYMMDDTHHMMSSZ__<id>__<name>.md`
- Log → `logs/email.log` (also uploaded as workflow artifact)

## Failure modes (all soft)

| Condition | Behavior |
|---|---|
| API key or group id missing for that brand | Draft stays in place, log line, run continues |
| Missing required frontmatter field | Draft stays in place, invalid counter increments, run exits non-zero |
| Schedule in the past | Same as above |
| MailerLite API error | Same as above, error surfaced in log |
| Duplicate content (same subject + from + body seen in `_sent/`) | Draft moved to `_sent/` again with duplicate tag, no API call |
