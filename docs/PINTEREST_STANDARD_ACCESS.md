# Pinterest API v5 — getting to Standard access

Path 3 of `PINTEREST_PATHS.md`. This is the $0/mo endgame; Buffer at ~$20/mo is the
bridge that keeps pins flowing until this clears.

## Why this is required and not optional

Trial-tier pins are **sandbox entities visible only to their creator**. The account is on
Trial. So the 401 in `PINTEREST_401_BLOCKER.md` was masking a second failure: even a valid
token would have published invisible pins. Standard access is the only thing that makes a
pin publicly visible through Pinterest's own API.

Both tiers cost nothing. The gate is a review, not a payment.

## Code status — done as of this commit

`post_pinterest` now refreshes before it posts. v5 access tokens are 30-day; refresh
tokens are ~1-year.

- `pinterest_refresh(brand)` — `POST https://api.pinterest.com/v5/oauth/token`,
  HTTP Basic with `app_id:app_secret`, form body `grant_type=refresh_token`.
- `pinterest_token(brand)` — refresh first, fall back to the static
  `PINTEREST_ACCESS_TOKEN`, cached once per brand per process.
- `pinterest_configured(brand)` — true for a static token **or** a complete refresh
  triple, checked before any network call so `DRY_RUN` stays inert.

Failure behaviour is deliberately non-fatal: a failed refresh falls back to the static
token rather than dropping the slot, and logs the reason. Only when both are unusable does
it return `False`.

Six new secrets are wired into `auto_post.yml` (three brands x three keys), none set yet:

```
{BRAND}_PINTEREST_REFRESH_TOKEN
{BRAND}_PINTEREST_APP_ID
{BRAND}_PINTEREST_APP_SECRET
```

Adding a secret requires **both** the `secret()` naming convention and the `env:` block —
both are done. Covered by `tests/test_pinterest_refresh.py`, 11 cases including refresh
success, 401 fallback, malformed 200, transport exception, partial triple, DRY_RUN
inertness, and one-exchange-per-run.

## What Don has to do

### 1. Confirm the app's current tier

`https://developers.pinterest.com/apps/` — the app card shows the access tier. If it reads
Trial, the upgrade request lives on that app's page.

### 2. Scopes the app must request

To create pins the token needs at minimum:

```
boards:read  pins:write  user_accounts:read
```

Add `boards:write` only if the app should create boards. Requesting scopes the app does
not visibly use is a review risk; requesting too few means `pins:write` calls 403 after
approval.

### 3. The demo video

The review requires a **screen recording of the app's OAuth flow**, and this is required
even for a solo developer whose only user is themselves
([Vorp Labs](https://vorplabs.com/agent-tools/pinterest-api)). Capturing login credentials
or session cookies instead of running real OAuth is grounds for denial.

The recording should show, unbroken and in one take:

1. The app initiating authorization — the redirect to Pinterest's consent screen.
2. The Pinterest consent screen itself, with the requested scopes visible.
3. Clicking Authorize.
4. The redirect back to the app's registered redirect URI, and the app confirming it
   received a token.
5. The app then creating a pin, and that pin appearing on the board.

Step 5 matters more than it looks. The review evaluates the app's *behaviour*, not just its
code, so showing the actual end-to-end outcome is stronger than stopping at the token.

### 4. The honest risk

Pinterest's policy says an app may not "offer features that enable end users to
automatically initiate actions without specifically considering each action." Scheduling is
explicitly **not** treated as auto-initiation when each scheduled action was specifically
considered — which is true here, since every pin is authored by hand into
`brands/<brand>/posts/<date>.md`. That framing is worth stating plainly in the submission:
this is a scheduling tool for content the operator wrote, not an autonomous generator.

Review duration is not published anywhere I could verify. That uncertainty is the whole
reason Buffer runs in parallel rather than instead.

### 5. Fallback route if the app page has no upgrade control

`https://help.pinterest.com/en/contact` → category **Pinterest API and Developer Tools**,
which offers **API Access** and **Request Access to Beta or Advanced Features**.

## Once approved

1. Mint a token via the OAuth flow, capture the **refresh** token, not just the access token.
2. Set the three `GRISSOM_PINTEREST_*` secrets above.
3. Flip routing from `buffer_pinterest` back to `pinterest`.
4. Verify one live pin is publicly visible from a logged-out browser — the Trial-sandbox
   failure mode is silent, so this check is the only real confirmation.
5. **Cancel the Buffer upgrade back to 3 channels.** Otherwise it bills ~$20/mo forever.

## Unverified

- How long the review takes.
- Whether the upgrade request is a button on the app page or a support-form submission for
  this account's app state.
- Exact numeric pin-creation rate limits per tier; Pinterest does not publish them at the
  endpoint level.
