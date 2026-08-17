# apps/tracker — Grissom Press attribution

First-party Measure layer for the Ora-auto publishing pipeline. Feeds Phases 2 (weekly reallocation) and 3 (daily-move) in the HeyCatch replacement plan.

## Layout

- `worker/` — Cloudflare Worker (ingest edge)
- `web/` — `track.js` browser tracker
- `db/` — Supabase migrations
- `tests/` — Vitest unit tests

## Attribution contract

- **post_id** = `YYYY-MM-DD-HHMM` from the block header in `brands/<brand>/posts/YYYY-MM-DD.md`
- **utm_source** = platform (`bluesky` | `threads` | `instagram` | `pinterest` | `tiktok` | `linkedin` | `email`)
- **utm_content** = post_id (redundant with post_id but preserved as-received)
- **utm_campaign** = campaign slug (e.g. `handy-hearts-launch`)

## Endpoints

- `POST https://track.grissompress.com/e` — browser event ingest
- `POST https://track.grissompress.com/gumroad` — Gumroad ping webhook (protected by `secret` form field)

## Local dev

    cd apps/tracker/worker
    npm install
    npm run test     # runs the 14 unit tests
    npm run dev      # local Wrangler with fake secrets

## Deploy (Don runs after Supabase project is live)

    cd apps/tracker/worker
    wrangler secret put SUPABASE_SERVICE_KEY
    wrangler secret put DAILY_SALT
    wrangler secret put GUMROAD_PING_SECRET
    # Edit wrangler.toml → replace SUPABASE_URL placeholder
    wrangler deploy

## Install snippet (landing pages)

    <script async src="https://track.grissompress.com/track.js" data-brand="grissom"></script>

Install order:
1. `cedarhollow.pplx.app` (pilot — Handy Hearts launch)
2. `grissompress.pplx.app`
3. Ora landing pages (Phase 4)

## Smoke test (Phase 1 acceptance)

See `docs/measure-smoke-test.md`.
