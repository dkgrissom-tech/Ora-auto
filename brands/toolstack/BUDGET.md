# Toolstack render budget — hard limits

The Replicate render worker will refuse to run if any of these are breached.
All limits are enforced in `scripts/generate_animal_short.py` before an API call is made.

| Limit | Value | Why |
|---|---|---|
| Model | `wan-video/wan-2.2-i2v-480p-fast` | ~$0.05 per 5-second clip |
| Max cost per post | $0.30 | 3 beats × ~$0.05 with 2x safety margin |
| Max cost per day | $1.00 | 3 posts/day worst case |
| Max cost per calendar month | $30.00 | 30-day sprint budget cap |
| Max renders per run | 3 | One post = 3 beats |
| Model version pinned | Yes | No auto-upgrades |
| Retry policy | 1 retry, then skip and log | No render loops |

## Kill switch
Set repo variable `TOOLSTACK_RENDER_ENABLED=false` in GitHub → Ora-auto → Settings → Variables to freeze all renders.
The workflow reads this at the start of every cron tick.

## Cost accounting
Every render appends a row to `brands/toolstack/learnings/render_costs.csv`:
`timestamp,creative_id,beat,model,seconds,estimated_cost_usd`

The script sums the last 24h and last 30d before firing. If either sum + projected cost exceeds the cap, it exits 0 (no failure) and logs `BUDGET_HALT`.

## Dry run
Set repo variable `TOOLSTACK_DRY_RUN=true` to print what would render without calling the API. Default `false`.
