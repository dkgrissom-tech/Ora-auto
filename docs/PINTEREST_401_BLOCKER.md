# Pinterest 401 — the actual top blocker

**Found:** 2026-08-08 02:09 UTC, run `31234321466`, live (not dry-run).

```
[grissom] Posting to ['pinterest']: **"Grief Does Not End. It Changes Shape." | Handy Hearts**
[grissom] Pinterest FAIL: 401 {"code":2,"message":"Authentication failed.","status":"failure"}
```

The workflow reported **success**. It did not post.

## What this changes

The working assumption was that missing artwork was the blocker and the pins would start
flowing once the 66 images existed. That is wrong. **`GRISSOM_PINTEREST_ACCESS_TOKEN` is
not authenticating**, so every pin fails at the API before the image URL is ever evaluated.

Generating all 66 images while this 401 stands produces 66 more silent failures.

Revised order:

1. **Fix the Pinterest token** ← nothing else in the Pinterest lane matters until this clears
2. Generate the artwork (`docs/HANDY_HEARTS_PIN_PROMPTS.md`)
3. Threads tokens
4. Grissom TikTok decision

## What is confirmed vs. not

Confirmed:

- The token secret **is present** and non-empty — the run log shows
  `GRISSOM_PINTEREST_ACCESS_TOKEN: ***`, and `post_pinterest` returns early with
  `missing keys/image — skipping` when it is blank. It got past that guard and made the call.
- `GRISSOM_PINTEREST_BOARD_ID` is also present.
- Pinterest rejected the credential itself, not the payload. `code: 2` is Pinterest's
  generic authentication failure.

Not yet determined — the 401 alone cannot distinguish these:

- Token expired. Pinterest v5 access tokens are **30-day**. See below.
- Token revoked, or the connected Pinterest account changed its password.
- The developer app lost API access. Trial access is time-boxed and the app
  resubmission is already a known upstream blocker.
- Token was truncated or has whitespace when it was pasted into the repo secret.

## The structural problem underneath it

There is **no refresh logic anywhere in `scripts/run_scheduler.py`** — zero matches for
`refresh_token`. Pinterest v5 issues a 30-day access token alongside a 1-year refresh
token. Without a refresh path, this credential dies roughly every 30 days and the entire
Pinterest lane goes dark, silently, because `auto_post.yml` still exits 0.

Launch is **Tue Sept 8 2026**. A token pasted today expires in early September — inside
the launch window. Fixing this by pasting a fresh token is a fix with a built-in
expiry date.

Two options once posting works again:

1. **Manual re-paste, calendared.** Zero code. Add a recurring reminder to refresh the
   token every 3 weeks. Fragile but immediate.
2. **Store the refresh token and exchange on each run.** Add
   `GRISSOM_PINTEREST_REFRESH_TOKEN`, POST to
   `https://api.pinterest.com/v5/oauth/token` with `grant_type=refresh_token` at the top
   of the Pinterest branch, use the returned short-lived token. Refresh tokens last a
   year, so this reduces the manual step to annual.

Option 2 is the right answer before Sept 8. Option 1 is acceptable only as a stopgap.

## Diagnose it in one command

Run this locally with the token value to separate "expired" from "wrong app access":

```bash
curl -s -o /dev/null -w '%{http_code}\n' \
  -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.pinterest.com/v5/user_account
```

- `200` — the token is fine, and the problem is the value stored in the repo secret
  (truncation or stray whitespace). Re-paste it.
- `401` — the token is genuinely dead. Re-authorize the app and mint a new one.

## Also worth fixing: the green checkmark

`auto_post.yml` exits 0 even when every post fails, which is why 38 of 40 "successful"
runs published nothing. Making the scheduler exit non-zero when a live post fails would
have surfaced this 401 the day it started. That is a small change to `main()` and it is
the difference between finding these on purpose and finding them by accident.

---

## Resolved path: publish through Buffer instead (2026-08-10)

Pinterest's own API is not the only way in. Buffer already publishes this org's
Instagram, TikTok and YouTube, and Buffer's GraphQL schema exposes Pinterest as a
first-class target. Confirmed by introspecting `api.buffer.com` directly rather
than assuming:

```
PinterestPostMetadataInput
  boardServiceId  String   The board ID of the Pin
  title           String   The title of the Pin
  url             String   The Pin destination link
```

All three are optional, and they map one-to-one onto fields the queue already
carries (`pinterest_title`, `pinterest_url`) plus the board. `Channel.metadata`
resolves to `PinterestMetadata { boards { id name serviceId } }`, so both the
channel ID and the board ID can be discovered at runtime from the existing
`BUFFER_ACCESS_TOKEN`.

That means **the only manual step is connecting Pinterest inside Buffer.** No new
secret, no ID to copy, no Pinterest app review, no 30-day token to rotate — Buffer
owns the refresh. `resolve_buffer_pinterest()` discovers the channel on the first
call of each run and caches it.

### Behaviour

`route()` sends a `pinterest` slot to `buffer_pinterest` only when a channel
actually resolves. Until then it fans out to `PINTEREST_FALLBACK` exactly as
before, so nothing silently stops working. It reroutes, with a logged reason, when
there is no Buffer token, no Pinterest channel, or the channel is disconnected.

### Why this matters beyond Pinterest

The fan-out was doing collateral damage. For 2026-08-11:

| target | Pinterest not connected | connected |
| :--- | ---: | ---: |
| `buffer_pinterest` | 0 | **5** |
| `bluesky` | 6 | 1 |
| `buffer_instagram` | 5 | 0 |
| instagram | 2 | 2 |

Connecting Pinterest simultaneously:

- restores the real Pinterest slot at the 2:3 aspect the 66 pins were built for
- stops 5 pins/day being center-cropped into Instagram's 4:5
- drops Bluesky from 6 posts/day to 1
- makes the `_ig_sent_today` per-run cap bug dormant, since the reroute that was
  overrunning the cap disappears

Covered by `tests/test_buffer_pinterest.py` — 8 cases including no token, no
channel, disconnected channel, board override, and a media-less pin.

Optional overrides, neither required: `BUFFER_CHANNEL_PINTEREST` to pin a specific
channel when several are connected, `BUFFER_PINTEREST_BOARD` to choose a board by
name. With multiple boards and no override, the first is used and every board name
is logged.
