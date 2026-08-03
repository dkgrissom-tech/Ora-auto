# Ora-auto — Milestones

Chronological log of major wiring, deploys, and pipeline events.

## 2026-08-03 — Clone→GitHub webhook LIVE + PowerShell self-serve

**Status:** production, hands-off end-to-end.

### What went live
- **n8n workflow** `Clone → GitHub commit` deployed on Railway
  (`https://n8n-production-b205b.up.railway.app/webhook/clone-commit`)
- **Fine-grained GitHub PAT** scoped to `dkgrissom-tech/Ora-auto` (Contents R+W, Pull requests R+W) stored as n8n credential
- **Header-auth webhook secret** protects the endpoint (rejects all POSTs missing `X-Webhook-Secret`)
- **Validation stage** enforces payload schema: brand ∈ {ora, grissom, familybook}, kind ∈ {social, email}, filename must be bare `.md` slug
- **Commit path** auto-generated as `clone_drafts/<brand>/<filename>`
- **Response** returns `commit_sha`, `commit_url`, `file_url`

### Producers (upstream)
1. **Claude Pro project** — Ora Text Clone project with custom instructions telling Claude to draft in brand voice AND emit a ready-to-run curl block with every reply
2. **PowerShell functions** on Don's laptop (`$PROFILE`):
   - `Commit-Clone` — opens Notepad with JSON template, commits on save
   - `Commit-CloneFromClipboard` — reads clipboard JSON, commits in one command

### Consumer (downstream)
- **Phase 4a Ingest workflow** (GH Actions, `:50` schedule) picks up new files under `clone_drafts/<brand>/`
- **Phase 4b Email workflow** (GH Actions, `:35` schedule) routes email-kind drafts to MailerLite

### Perf
- First smoke test round-trip: **1.7s** (Claude curl → n8n → GitHub commit landed)
- First real Claude draft ("3am Idea" Ora TikTok caption): **1.5s**

### Files
- Webhook config: `n8n_clone_webhook/clone_commit_webhook.json` (workspace)
- Claude Project instructions: `claude_ora_project_setup.md` (workspace)
- PowerShell setup: `commit_clone_v2.ps1` (workspace)

### Ops notes
- Webhook secret: stored in n8n credentials + Don's PowerShell profile. If leaked, rotate both.
- GitHub PAT: expires per fine-grained token settings. When it expires, regenerate on github.com, update the `GitHub Contents API — Ora-auto` credential in n8n.
- Railway free tier hosts n8n; monitor uptime. Backup: workflow JSON is in this repo's history.
