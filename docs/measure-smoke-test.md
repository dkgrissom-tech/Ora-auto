# Phase 1 — Measure smoke test

Run this end-to-end **before** touching Phase 2 (weekly-reallocate).

## Prereqs
- Supabase project created, `001_init.sql` run
- Cloudflare Worker deployed to `track.grissompress.com`
- Secrets set in Wrangler
- Tracker snippet installed on `cedarhollow.pplx.app`
- Gumroad ping URL set to `https://track.grissompress.com/gumroad?secret=<GUMROAD_PING_SECRET>` on `l/handy-hearts`

## Test

1. Manually post one Bluesky block with:
   - `destination: https://grissom77.gumroad.com/l/handy-hearts?utm_source=bluesky&utm_content=2026-08-14-1400&utm_campaign=handy-hearts-launch`
2. Click your own link from Bluesky on a phone or a fresh browser session.
3. In Supabase SQL editor, run:

       select brand, post_id, platform, event, ts
       from public.events
       where post_id = '2026-08-14-1400'
       order by ts desc;

   Expect: at least one `page_view` row with `platform='bluesky'`, arrived within 60s.

4. Complete a $0 Gumroad test purchase from the same link.
5. Re-run the query. Expect: one additional row with `event='purchase'`, matching `post_id`, `amount_cents` set.

If both rows land with correct attribution, Phase 1 is done — hand back to Don to begin PR #12 (weekly-reallocate).

## Fail modes

| Symptom | Fix |
|---|---|
| `page_view` never lands | Check browser console for CORS. Origin must be in `ALLOWED_ORIGINS` in `worker/index.ts`. |
| `purchase` never lands | Verify Gumroad ping URL includes the `secret=` query param. |
| `post_id` is null on purchase | Gumroad stripped `url_params` — verify the outbound link had `utm_content` on it. |
| Supabase 5xx | Service key wrong in Worker secret or RLS blocking service role (shouldn't — service key bypasses RLS). |
