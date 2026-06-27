# Auto-Post — Multi-Brand

Free-tier social-media auto-poster for three brands:

- **Ora** — [meetora-app.pplx.app](https://meetora-app.pplx.app) (iOS meeting assistant)
- **Grissom Press** — [grissompress.pplx.app](https://grissompress.pplx.app) (gothic coloring books)
- **Family Book Creator** — [familybookcreator.app](https://familybookcreator.app) (personalized kids books)

## How it works

1. Drop a markdown file at `brands/<brand>/posts/YYYY-MM-DD.md` with timed post blocks
2. GitHub Actions cron fires every hour at :05
3. The scheduler reads today's file for every brand, finds blocks matching the current UTC hour, posts to the platforms listed using that brand's API keys
4. All API keys live in GitHub Secrets — never in code, never in chat

## Brands & secrets

Each brand has its own set of secrets, prefixed by brand name in caps:

- `ORA_X_API_KEY`, `ORA_LINKEDIN_ACCESS_TOKEN`, ...
- `GRISSOM_X_API_KEY`, `GRISSOM_PINTEREST_ACCESS_TOKEN`, ...
- `FAMILYBOOK_X_API_KEY`, `FAMILYBOOK_PINTEREST_ACCESS_TOKEN`, ...

To add a 4th brand later:
1. Add the brand to the `BRANDS` list in `scripts/run_scheduler.py`
2. Create `brands/<newbrand>/posts/` and `brands/<newbrand>/assets/`
3. Add the secrets to `.github/workflows/auto_post.yml` and to GitHub Secrets

## Platforms

| Platform | Approval | Notes |
|---|---|---|
| **Bluesky** | Same-hour | Free, no review, no credit card. Replaces X. |
| **LinkedIn** | Same-day | Free, OAuth |
| **Threads** | 2-4 wk | Meta App Review required |
| **Instagram** | 2-4 wk | Meta App Review required |
| **Pinterest** | 1-4 wk | Standard access review required |
| **TikTok** | 2-6 wk | Content Posting audit required. Ora only (@toolstack-y4g). |
| **X (Twitter)** | MANUAL ONLY | X charges now ($200/mo Basic). Auto-poster doesn't touch it. Post by hand for big moments. |

## Post file format

```markdown
## 14:00 UTC  (09:00 CDT)
platforms: x, linkedin, threads
image: brands/ora/assets/zara_drop1.png
video: brands/ora/assets/ora_demo.mp4
pinterest_title: Just say Ora
pinterest_url: https://meetora-app.pplx.app
---
Body of the post.
Can be multiple lines.
---
```

## Testing

Go to **Actions** tab → **Auto-Post (Multi-Brand)** → **Run workflow** → set `dry_run: true` → Run. The run log shows what would have been posted to each platform per brand, with no actual API calls.

## Multi-brand isolation

If brand A's keys are missing or revoked, brand B and C still post. The scheduler iterates each brand independently and logs failures without halting.

---

See `SETUP_INSTRUCTIONS.md` for the elementary-step guide to getting each brand's API keys.
