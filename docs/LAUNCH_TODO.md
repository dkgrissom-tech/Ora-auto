# Handy Hearts — Path to Live

**Launch: Tuesday Sept 8 2026. 32 days out as of Aug 7.**

This is the single authoritative todo list. Everything else in `docs/` is reference for
one of these items.

## Where things actually stand

Measured from the run log of `31234321466`, not assumed:

| Channel | Credentials | Assets | Status |
|---|---|---|---|
| Bluesky | present, verified | 15 OK, 0 missing | **working** |
| Pinterest | present but **401** | 4 OK, **66 missing** | blocked twice over |
| Threads | **empty** | 14 OK, 0 missing | dark |
| Instagram | **empty** | 9 OK, **7 missing** | dark |
| LinkedIn | **empty** | 3 OK, 0 missing | dark |
| TikTok | **empty** + brand-gated | 9 OK, **9 missing** | dark |
| X | n/a | — | manual by policy |
| YouTube | no code at all | — | not implemented |

**One working channel.** Bluesky is carrying the entire launch right now. That is the
headline, and it is not a content problem — the queue is full and the copy is written.
It is five credential problems and one artwork problem.

---

## Tier 1 — do these or the launch has no reach

### 1. Pinterest 401

`docs/PINTEREST_401_BLOCKER.md`

Diagnose first:

```bash
curl -s -o /dev/null -w '%{http_code}\n' \
  -H "Authorization: Bearer YOUR_TOKEN" \
  https://api.pinterest.com/v5/user_account
```

`200` → the repo secret is truncated or has whitespace; re-paste it.
`401` → token is dead; re-authorize and mint a new one.

Pinterest is your highest-volume channel by a wide margin — 70 of 101 scheduled posts.
Fixing this one credential unlocks more of the calendar than everything else combined.

### 2. The 66 pin images

`docs/HANDY_HEARTS_PIN_PROMPTS.md`, visual system in `docs/pin_style_guide.md`

Only worth starting after item 1 clears, otherwise you can't verify a single one.
Save under the exact `Save as:` path — the scheduler builds the raw GitHub URL from it,
so a renamed file 404s identically to a missing one.

Minimum viable: pins 01–14 plus the ARC-recruitment set. That covers the next ten days
and the review-team push. The rest can trail in.

### 3. Make failures loud

`scripts/run_scheduler.py`, `main()`

Track whether any live post returned False and `sys.exit(1)` if so. Roughly ten lines.

This is out of order by urgency and in order by leverage. Every other item on this list
was discovered by accident because the pipeline reports success unconditionally. Fix this
and the remaining items find themselves.

---

## Tier 2 — real reach, not required to launch

### 4. Threads tokens

`docs/CLAUDE_HANDOFF_THREADS_AND_POSTIZ.md`

`GRISSOM_THREADS_USER_ID`, `GRISSOM_META_LONG_TOKEN`. The trap: a Meta app with the
Threads use case carries two App ID/Secret pairs, and only the Threads pair works.
14 posts already queued with assets present — this is pure credential work, no content
needed.

### 5. Instagram

Same `GRISSOM_META_LONG_TOKEN` from item 4, plus `GRISSOM_INSTAGRAM_USER_ID`. Doing
Threads first makes this nearly free. Needs 7 images beyond the 66.

### 6. Credential expiry, before it bites

Pinterest tokens are 30-day. The Threads long-lived token is 60-day and expires **~Oct 6**
— inside your launch window. There is no refresh logic anywhere in the scheduler.

Any token pasted this weekend expires during or just after launch week. Either add refresh
token exchange (Pinterest refresh tokens last a year) or put a hard calendar reminder at
3-week intervals. The first is a morning's work and then it's done.

---

## Tier 3 — decide and move on

### 7. Grissom TikTok

`TIKTOK_ALLOWED_BRANDS = {"ora"}` at ~line 306. Nine Grissom posts queued, silently
skipping, no token, and nine missing videos.

Recommend: delete the nine blocks, keep TikTok Ora-only through launch. Enabling it now
converts silent skips into loud failures without adding a single post.

### 8. Loose ends

- Legacy n8n workflow `OCo1e3DoDuk0WY5J` (Claude Draft v4) — deactivate?
- The `:05` cron collision between `auto_post` and other workflows
- Whether `grissomshop` is a brand or a channel — no repo folder exists, nothing created
- Postiz is fully diagnosed and parked; not on the launch path
- YouTube has no publisher, no dispatch branch, no secret. Genuinely unimplemented,
  not broken. Ignore until after launch.

---

## Honest read

You have 32 days, and the work remaining is almost entirely mechanical: paste five
credentials, generate artwork you already have prompts for, and make the pipeline stop
lying about success. No writing, no strategy, no new content.

The risk is not that any single item is hard. It's that the pipeline reports success
either way, so a missed credential stays invisible until you check a specific log line by
hand. That's why item 3 is Tier 1 despite feeling like cleanup.

Bluesky posting today means the launch is not at zero. But one channel is not a launch,
and Pinterest at 70 of 101 posts is where the actual audience is.
