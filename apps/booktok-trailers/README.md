# BookTok Trailer Factory

SaaS: paste an Amazon book URL → get 8 vertical BookTok trailers per week, one per cinematic camera preset. Priced at $29/mo (8/week) and $79/mo (unlimited). Built on Higgsfield API (Phase 1) with a hybrid swap-in to local ComfyUI + Wan 2.2 once at 40+ paying users (Phase 2).

## Prerequisites

- Node 20+ and pnpm 9+
- Higgsfield CLI authed: `higgsfield auth login`
- `~/.claude/skills/higgsfield` cloned (see `../00-install/INSTALL.md`)
- Supabase project (free tier)
- Stripe account with two prices: $29/mo and $79/mo
- Upstash Redis (free tier is fine)
- AWS S3 bucket + IAM user with `s3:PutObject`, `s3:GetObject`
- Resend API key
- ffmpeg installed on the worker host (`brew install ffmpeg` or `apt install ffmpeg`)
- Supabase Auth → URL Configuration: add `<NEXT_PUBLIC_APP_URL>/auth/callback` as a redirect URL (needed for magic-link sign-in)

## First run

```bash
pnpm install
pnpm exec playwright install chromium

# fill env vars
cp .env.local.example .env.local
# edit .env.local with all creds

# apply the Supabase migration
psql "$SUPABASE_DB_URL" -f supabase/migrations/0001_init.sql

# run app + worker in two terminals
pnpm dev            # terminal 1
pnpm worker:dev     # terminal 2

# smoke test end-to-end (creates one order for Handy Hearts)
pnpm smoke
```

## What Claude Code does

Open the repo in Claude Code and it will read `CLAUDE.md` automatically. From there it can:
1. Wire remaining UI polish (`app/dashboard`)
2. Add Stripe portal + downgrade flow
3. Ship the Phase 2 hybrid swap-in (see `worker/comfyui.ts.example`)

## Repository layout

```
booktok-trailers/
├── CLAUDE.md                       # what Claude Code reads first
├── README.md                       # this file (human)
├── package.json / tsconfig / next.config.mjs / tailwind.config.ts
├── .env.local.example
├── app/
│   ├── layout.tsx
│   ├── page.tsx                    # landing + generate form
│   ├── dashboard/page.tsx          # past orders, downloads
│   └── api/
│       ├── generate/route.ts       # POST { amazonUrl } → enqueue
│       ├── stripe/checkout/route.ts
│       ├── stripe/webhook/route.ts
│       └── jobs/[id]/route.ts
├── lib/
│   ├── env.ts                      # typed env with zod
│   ├── presets.ts                  # 8 camera prompts
│   ├── higgsfield.ts               # CLI wrapper (Phase 1)
│   ├── comfyui.ts                  # local endpoint (Phase 2, feature-flagged)
│   ├── supabase-server.ts
│   ├── supabase-browser.ts
│   ├── stripe.ts
│   ├── queue.ts                    # BullMQ producer
│   └── s3.ts
├── worker/
│   ├── index.ts                    # BullMQ consumer entrypoint
│   ├── scrape.ts                   # Playwright: Amazon → cover + blurb
│   ├── generate.ts                 # 8 parallel preset jobs
│   ├── caption.ts                  # ffmpeg drawtext burn-in
│   ├── deliver.ts                  # S3 upload + Resend email
│   └── workflows/                  # Phase 2 ComfyUI graphs (empty for now)
├── supabase/migrations/0001_init.sql
├── scripts/smoke-test.sh
└── public/
```

## Costs

| Phase | Per 8-trailer order | Margin at $29/mo |
|---|---:|---:|
| Phase 1 (Higgsfield API) | ~$10.40 | 64% |
| Phase 2 (70% local Wan 2.2) | ~$3.10 | 89% |
| Phase 3 (fully local + API burst) | ~$0.10 | 99.7% |

## Bounty positioning

A Higgsfield team member is offering $50K to a developer who ships a competing product on their API. On launch tweet:

- Tag `@higgsfield_ai` and Alex Mashrabov
- Mention the specific skills used
- Post the Handy Hearts before/after
