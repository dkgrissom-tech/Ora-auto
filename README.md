# Ora Auto-Post

Free-tier multi-platform poster for [Ora](https://meetora-app.pplx.app).

## How it works

1. Drop a markdown file at `posts/YYYY-MM-DD.md` with timed post blocks
2. GitHub Actions cron fires every hour at :05
3. The scheduler reads today's file, finds any block matching the current UTC hour, posts to the platforms listed
4. All API keys live in GitHub Secrets — never in code, never in chat

## Platforms

| Platform | Status | Notes |
|---|---|---|
| X (Twitter) | Free tier, 1500 posts/mo | Same-day signup |
| LinkedIn | Free | Same-day OAuth |
| Threads | Free | Requires Meta App Review (2-4 wk) |
| Instagram | Free | Requires Meta App Review (2-4 wk) |
| Pinterest | Free | Requires Standard access review (1-4 wk) |
| TikTok | Free | Requires Content Posting audit (2-6 wk) |

## Post file format

```markdown
## 14:00 UTC  (09:00 CDT)
platforms: x, linkedin, threads
image: assets/zara_drop1.png
video: assets/ora_demo.mp4
pinterest_title: Just say Ora
pinterest_url: https://meetora-app.pplx.app
---
Body of the post.
Can be multiple lines.
---
```

## Dry-run testing

Actions tab → Ora Auto-Post → Run workflow → set `dry_run: true` → Run.
Log appears in the run output and `logs/scheduler.log` (not committed).

## Manual posting

To post outside the cron window, just run the workflow manually with `dry_run: false`.

---

See `SETUP_INSTRUCTIONS.md` for the elementary-step setup guide.
