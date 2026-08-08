# Handoff — Threads tokens & Postiz account recovery

**Paste this whole file to Claude Code (or your twin) as the task.**
**Repo:** `dkgrissom-tech/Ora-auto` · **Written:** Aug 7 2026, after the Pinterest outage fix (`e929b45`)

You are picking up two independent infrastructure jobs. Job A is straightforward and
unblocks a dead channel. Job B is a recovery operation on a production database and
needs Don's explicit go-ahead before the write.

Read the whole file before starting. Do them in order — A is worth more.

---

## Context you need first

The live publisher is the GitHub Action `.github/workflows/auto_post.yml`, which runs
hourly at `:05` UTC and executes `scripts/run_scheduler.py`. **It is not Postiz.**
Earlier docs in this repo claim publishing is migrating to self-hosted Postiz — that
migration is parked because Don cannot log in (Job B).

**Critical failure mode, do not forget this:** `auto_post.yml` exits 0 even when every
single post fails. A green checkmark in the Actions tab means nothing. Always judge by
the log lines — `posted OK` versus `FAIL` versus `missing — skipping`. This masked a
live Pinterest outage for an unknown number of days.

Secrets are read by a helper in `run_scheduler.py`:

```python
def secret(brand, key):
    return os.environ.get(f"{brand.upper()}_{key}")
```

So `secret('grissom', 'THREADS_USER_ID')` reads the env var `GRISSOM_THREADS_USER_ID`.
Those env vars are populated from **GitHub repo secrets** in `auto_post.yml`. Adding a
secret is therefore two steps: create the repo secret, **and** wire it into the `env:`
block of the workflow. Miss the second step and the variable is silently empty.

---

# JOB A — Get Threads publishing

## Why

The scheduler currently logs `[grissom] Threads keys missing — skipping` on every run.
14 Threads posts are queued between Aug 4–18 and none of them are going out. It needs
two values:

| Secret | What it is |
|---|---|
| `GRISSOM_THREADS_USER_ID` | numeric Threads user ID |
| `GRISSOM_META_LONG_TOKEN` | 60-day long-lived Threads access token |

First, confirm the exact names by reading `post_threads()` in `scripts/run_scheduler.py`
and the `env:` block of `.github/workflows/auto_post.yml`. Trust the source over this
table if they disagree.

## The trap that wastes the most time

A Meta app with the Threads use case has **two App IDs and two App Secrets** — one for
the parent Meta app, one for Threads specifically. You must use the **Threads** pair.
Using the parent pair produces confusing `invalid_client` errors
([ArtDrop's setup guide](https://getartdrop.com/help/threads-setup)).

## Steps

Don has to do steps 1–4 in a browser; you can do 5–7.

**1. Create the app.** [developers.facebook.com/apps](https://developers.facebook.com/apps)
→ Create App → under **Use cases** pick **Access the Threads API** → name it, add a
contact email, create.

**2. Get the Threads credentials.** Left sidebar → **Use cases** → **Access the Threads
API** → **Customize** → scroll to **Settings** → copy the **Threads App ID** and
**Threads App Secret**. Not the parent app's pair.

**3. Permissions and URLs.** Same Customize screen:
- **Permissions** → add `threads_basic` and `threads_content_publish`. Add
  `threads_manage_insights` only if you want metrics later.
- **Settings** → set Redirect Callback URL, Deauthorize Callback URL and Data Deletion
  Request URL. Any HTTPS URL Don controls works — `https://grissompress.pplx.app/` is
  fine. All three must be HTTPS.

**4. Add himself as a Threads Tester.** Left sidebar → **App roles** → **Roles** →
scroll to **Threads Testers** → **Add Threads Testers** → enter his Threads username →
send invite. Then accept it at [threads.net/settings](https://threads.net/settings).

> **Do NOT flip the app to Live mode.** Development mode is correct here. Only admins
> and testers can authorize a dev-mode app, which is all Don needs. Live mode triggers
> full App Review — 2 to 4 weeks and a screencast — for zero benefit on a single-user
> setup.

**5. Authorize.** Have Don open this in a browser where he's logged into Threads:

```
https://threads.net/oauth/authorize
  ?client_id={THREADS_APP_ID}
  &redirect_uri={REDIRECT_URL}
  &scope=threads_basic,threads_content_publish
  &response_type=code
  &state=orauto
```

He clicks Authorize, gets redirected, and copies the `code=...` value out of the address
bar. **Strip the trailing `#_`** — Meta appends it and it is not part of the code. The
code expires in about an hour and is single-use, so move straight to step 6
([Meta's access token docs](https://developers.facebook.com/docs/threads/get-started/get-access-tokens-and-permissions/)).

**6. Exchange for a short-lived token.**

```bash
curl -X POST https://graph.threads.net/oauth/access_token \
  -F client_id={THREADS_APP_ID} \
  -F client_secret={THREADS_APP_SECRET} \
  -F grant_type=authorization_code \
  -F redirect_uri={REDIRECT_URL} \
  -F code={CODE}
```

Returns `{"access_token":"THAAx...","user_id":123456789012345}`. **That `user_id` is
`GRISSOM_THREADS_USER_ID`** — save it now, this is the only place it appears cleanly.
The token is valid ~1 hour.

**7. Exchange for the 60-day token.**

```bash
curl -G https://graph.threads.net/access_token \
  -d grant_type=th_exchange_token \
  -d client_secret={THREADS_APP_SECRET} \
  -d access_token={SHORT_TOKEN}
```

Returns a token with `expires_in: 5183944` (60 days). **That is `GRISSOM_META_LONG_TOKEN`.**

Verify before saving anything:

```bash
curl -s "https://graph.threads.net/v1.0/me?fields=id,username&access_token={LONG_TOKEN}"
```

The `username` must be the Grissom Press Threads account and the `id` must match the
`user_id` from step 6. If they don't match, stop — you have tokens for the wrong account.

**8. Install the secrets.**

```bash
gh secret set GRISSOM_THREADS_USER_ID --repo dkgrissom-tech/Ora-auto
gh secret set GRISSOM_META_LONG_TOKEN --repo dkgrissom-tech/Ora-auto
```

Then add both to the `env:` block of `.github/workflows/auto_post.yml` following the
pattern of the existing Bluesky and Pinterest entries. Commit as
`fix(ci): wire Threads secrets into auto_post env`.

**9. Verify for real.** Trigger a dry run and read the log:

```bash
gh workflow run auto_post.yml --repo dkgrissom-tech/Ora-auto -f dry_run=true
# wait ~45s
gh run list --workflow=auto_post.yml --repo dkgrissom-tech/Ora-auto --limit 1
gh run view <RUN_ID> --log --repo dkgrissom-tech/Ora-auto | grep -i threads
```

Success is the disappearance of `Threads keys missing — skipping`. If the hour you
dry-ran has no Threads post due, pick an hour that does from
`brands/grissom/posts/<today>.md` and note that you could not exercise it — do not
claim success you didn't observe.

## The catch to write down

**This token dies in 60 days**, around **Oct 6 2026** — which lands inside the Handy
Hearts launch window (Sept 8). Refreshing requires calling the `th_refresh_token`
endpoint before expiry, or redoing steps 5–7 by hand. Add a note to
`docs/n8n-env-var-checklist.md` with the exact expiry date, and tell Don he needs a
calendar reminder for early October. Do not let this silently expire mid-launch.

---

# JOB B — Recover Don's Postiz login

## Do not start this without asking Don first

This ends in a **write to the password column of a production database**. Ask for
explicit confirmation before the `UPDATE`. Everything before that point is read-only
and safe.

## Instance

`https://postiz-v2113-production-a347.up.railway.app` — self-hosted Postiz v2.11.3,
Railway project `faithful-simplicity`. Don's account email is `dkgrissom@gmail.com`.

## What has already been ruled out — don't repeat this work

**Google sign-in cannot work.** `GET /api/auth/oauth/GOOGLE` returns a Google consent
URL with **no `client_id` parameter at all**, because the instance has no
`GOOGLE_CLIENT_ID` env var. Google rejects it before rendering a consent screen. This
is the "Access blocked" error Don keeps hitting. Verify yourself:

```bash
curl -s "https://postiz-v2113-production-a347.up.railway.app/api/auth/oauth/GOOGLE" | head -c 400
```

**Registering fresh doesn't help.** `POST /api/auth/register` returns
`400 Email already exists` for his address. An account exists.

**Password reset is a dead end.** `/auth/forgot` renders and appears to work, but the
instance has **no email provider configured** (no Resend/SMTP vars among its 28 env
vars), so the reset mail goes nowhere.

Other verified facts: the signup page is `/auth`, not `/auth/register` (which 404s).
Login is `/auth/login`. New accounts on this instance auto-activate, because
`organization.repository.ts:294` sets `activated: body.provider !== 'LOCAL' || !hasEmail`
and `hasEmail` is false here.

## Two routes. Try Route 1 first.

### Route 1 — repair Google OAuth (non-destructive, preferred)

Create a Google Cloud OAuth 2.0 Web client, then add `GOOGLE_CLIENT_ID` and
`GOOGLE_CLIENT_SECRET` to the Postiz service on Railway and redeploy. The authorized
redirect URI must exactly match what Postiz sends. Confirm it from the curl above —
observed value was `.../integrations/social/youtube`, which is unintuitive, so read it
rather than assuming. This touches no data and fixes login permanently.

### Route 2 — reset the password directly in Postgres

Only if Don declines Route 1 or it fails, and only with his explicit OK.

Postiz hashes with **bcrypt at 10 rounds** — confirmed in
`libraries/helpers/src/auth/auth.service.ts`:

```ts
static hashPassword(password: string) { return hashSync(password, 10); }
static comparePassword(password: string, hash: string) { return compareSync(password, hash); }
```

So a bcrypt hash generated anywhere with cost 10 will validate.

1. Get the Postgres connection string from the Railway dashboard: project
   `faithful-simplicity` → Postgres service → **Variables** → `DATABASE_URL`. The
   internal `*.railway.internal` host is **not reachable from outside** — use the public
   TCP proxy host and port shown on the Connect tab.
2. Generate a hash:
   ```bash
   python3 -c "import bcrypt,secrets,string
   pw=''.join(secrets.choice(string.ascii_letters+string.digits) for _ in range(20))
   print(pw); print(bcrypt.hashpw(pw.encode(),bcrypt.gensalt(10)).decode())"
   ```
3. **Read first.** Confirm exactly one row matches and inspect it before writing:
   ```sql
   SELECT id, email, provider, activated FROM "User" WHERE email = 'dkgrissom@gmail.com';
   ```
   If `provider` is `GOOGLE`, note that setting a password may not be enough on its own —
   check whether the login path branches on provider in
   `apps/backend/src/services/auth/auth.service.ts` before proceeding.
4. Write, scoped to that single id, and verify the row count is 1:
   ```sql
   UPDATE "User" SET password = '<BCRYPT_HASH>', activated = true WHERE id = '<ID>';
   ```
5. Log in at `/auth/login` with the new password. Then have Don change it in the UI.

## Once he's in — the actual objective

The point of all this is one value: the **Postiz Public API key**.

Settings → **Developers** tab → the **Access** sub-tab (**not** Apps) → the "API Key"
card → **Reveal** → **Copy**.

Get this right, because Don has repeatedly grabbed the wrong credential:

- The **Access** tab holds the Public API key. This is the one. It has **no prefix**
  and is scoped **per organization**.
- The **Apps** tab is for building OAuth apps against Postiz. It offers "Production" as
  the only environment choice, which is why it looks correct. It is not.
- Wrong values, for the avoidance of doubt: anything starting `pos_`, `pca_` or `pcs_`,
  and any Railway token.
- **Never click "Rotate Key"** — it invalidates the existing key immediately.

The tab is client-side React state with no URL of its own, so you cannot deep-link it;
he has to click through. Documented path:
[Postiz public API docs](https://docs.postiz.com/public-api/introduction).

Verify the key works before declaring victory — note the auth header is a **bare**
`Authorization: <key>` with **no `Bearer` prefix**:

```bash
curl -s -H "Authorization: <KEY>" \
  "https://postiz-v2113-production-a347.up.railway.app/api/public/v1/integrations"
```

A JSON array of channels means success. `{"msg":"Invalid API key"}` means it's the
wrong value — go back to the Access tab.

**Then report the channel IDs and names back to Don.** The parked n8n workflow
`zrpFOQ6UpMV0pHzh` ("Short-Form Content Pipeline v3") needs them mapped to the brands
`ora`, `grissom` and `familybook`. If Route 2 created a new organization rather than
recovering the original, the integrations array will be **empty** — say so plainly
rather than reporting success, because it means the connected channels live on a
different org.

---

## Conventions for both jobs

- Commit prefixes `feat:` / `fix:` / `docs:`, subject under 72 chars, straight to `main`,
  no branches. Append `[skip ci]` unless you intend the Actions to fire.
- Set git identity first — the sandbox has none:
  `git config user.email "dkgrissom@gmail.com" && git config user.name "Ora Auto Agent"`
- New or changed secrets go in `docs/n8n-env-var-checklist.md`. **Never commit a real
  secret value and never invent a placeholder that looks real.**
- Blockers go in `WEEKEND_BLOCKERS.md`; unexpected errors in `debug_log/<date>.md`.
- Do not modify `scripts/run_scheduler.py` or `n8n_workflows/` beyond what Job A
  requires — flag it if you think you need to.
- Report what you **observed in logs**, not what should have happened. Don's biggest
  complaint about this project is false confidence from green checkmarks.
