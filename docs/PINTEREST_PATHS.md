# Pinterest publishing — the three real paths (2026-08-10)

Supersedes the "resolved path" section of `PINTEREST_401_BLOCKER.md` on the cost claim.
That section said connecting Pinterest in Buffer needs "no new secret, no Pinterest app
review" — true — but it did not say it costs money. It does. Corrected below.

## The thing the 401 was hiding

`PINTEREST_401_BLOCKER.md` treated the dead `GRISSOM_PINTEREST_ACCESS_TOKEN` as the
blocker and listed "the developer app lost API access / Trial access is time-boxed" as one
of four unresolved causes. Pinterest v5 runs two tiers, and **Trial-tier pins are sandbox
entities visible only to their creator.** So even a freshly minted working token on a
Trial-tier app would have published 66 pins that nobody but Don could see, and the
workflow would have exited 0 the whole time.

Fixing the token was never sufficient. Standard access is the actual gate.

## Option 1 — Pinterest in Buffer

- **Code: already written and tested.** `resolve_buffer_pinterest()` + 8 cases in
  `tests/test_buffer_pinterest.py`. Zero new code.
- **Manual step:** connect Pinterest inside Buffer. One click, Don's login.
- **Cost: ~$20/mo.** Buffer free caps at 3 channels and Instagram, TikTok and YouTube
  already fill them. Pinterest is a 4th. Buffer bills **per channel** on Essentials
  ($5/channel/mo) and explicitly states that upgrading from Free means paying for
  *every* channel, including ones held while free — so 4 x $5, not $5.
- Buffer owns token refresh. Nothing to rotate.

## Option 2 — Tailwind API

Genuinely new: a public REST API, verified live 2026-08-10.

- **Base URL:** `https://api-v1.tailwind.ai/v1` (spec: `https://api-v1.tailwind.ai/openapi.json`,
  OpenAPI 3.0.3, "Tailwind Public API" 1.0.0; `/health` returns `{"status":"ok"}`)
- **Auth:** `Authorization: Bearer tw_pk_...`, minted at Settings > API Access.
- **Rate limit:** 5,000 req/day per key, resets midnight UTC. `429` carries no `Retry-After`.
- **Endpoints:** `GET /v1/me`, `GET /v1/accounts`, `GET /v1/accounts/{id}/boards`,
  `/board-lists`, `/timeslots`, `GET|POST /v1/accounts/{id}/posts`,
  `GET|DELETE /v1/accounts/{id}/posts/{postId}`,
  `POST /v1/accounts/{id}/posts/{postId}/schedule`,
  `POST /v1/accounts/{id}/generations`, `GET /v1/generations/{id}`.
- **Create post:** only `mediaUrl` is required. Optional `mediaType`, `title` (<=100),
  `description` (<=500), `url`, `boardId`, `altText`, `sendAt`, `isSimplifiedPin`,
  `productTagPinIds`. `mediaUrl` is a **public remote URL** — exactly what `asset_url()`
  already emits, so no upload step. Non-public media -> `422`.
- **Cost: $17.99/mo Pro** = 150 posts/mo, 1 Pinterest account. Grissom runs 5 pins/day
  = ~150/mo, and that allowance is **shared across Instagram, Pinterest and Facebook**,
  so Pro is at zero headroom. Advanced is $29.99/mo for 300/mo and 2 accounts.
  Insufficient credits returns `402 PAYMENT_REQUIRED` / `insufficient_credits`.

**Architectural mismatch.** Tailwind is a scheduler, not a publisher: `sendAt` must be
>=15 minutes out. `auto_post.yml` fires hourly at `:20` and publishes immediately. Adopting
Tailwind means a once-daily job that pushes the whole day's pins with their real slot
times, not the hourly publish model. That is a different shape from every other publisher
in `run_scheduler.py`.

## Option 3 — Pinterest API v5, Standard access

- **Cost: $0/mo, permanently.** Both tiers are free; the gate is non-monetary.
- **Gate:** a one-time review requiring a **video recording of the app's OAuth flow**,
  required even for a solo developer serving only themselves. Capturing credentials or
  cookies instead of OAuth is grounds for denial. Review duration is not published.
- **Code: mostly already written.** `post_pinterest` exists — it is what threw the 401.
  Standard access plus a live token makes it work.
- **Still owed:** refresh logic. v5 access tokens are 30-day with a 1-year refresh token
  and there is no `refresh_token` call anywhere in `run_scheduler.py`. Option 2 of the
  blocker doc (exchange the refresh token at the top of the Pinterest branch) remains the
  right fix and is required before Sept 8 regardless.

## Cost over 12 months

| path | year 1 | new code | manual gate |
| :--- | ---: | :--- | :--- |
| Buffer | ~$240 | none | one click |
| Tailwind Pro | ~$216 | new publisher + daily push job | key paste |
| Pinterest direct | $0 | refresh logic | OAuth-flow video review |

## Incidental confirmations

- Tailwind's own current guidance is **1-5 fresh pins/day**, and it says the old
  15-25/day advice is retired. The queue's 5/day is at the top of the sane band, not low.
- Tailwind supports `altText`, which the queue already carries as `alt`.
- No Tailwind connector exists in Perplexity's catalog; it would be a custom credential.
