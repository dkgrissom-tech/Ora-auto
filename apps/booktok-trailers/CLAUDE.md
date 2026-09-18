# CLAUDE.md — BookTok Trailer Factory

You are Claude Code working inside the `booktok-trailers` repository. Read this file completely before your first action. Follow it verbatim.

## What we are building

A SaaS at **booktok-trailers.com** where an indie KDP author pastes an Amazon book URL and receives 8 vertical (9:16) BookTok trailers per week, each using a different cinematic camera preset. Priced at **$29/mo (8 trailers/week)** and **$79/mo (unlimited)**.

Target buyer: indie romance/thriller/nonfiction authors on KDP. Warm proof case: the operator's own imprint "Grissom Press" and its Handy Hearts romance series — dogfood on it first.

## Non-negotiables

- The user (Don) prefers concise, copy-ready output over long explanation. No preambles. Never explain what you're about to do — do it.
- Never guess a UI direction (e.g. "click the button in the top right"). Use verified interfaces and one action at a time.
- If a step fails twice with the same error, stop and report — do not loop.
- All commit messages: imperative, ≤72 chars, no emojis.
- Prefer Higgsfield skills over hand-rolled orchestration. If a skill in `~/.claude/skills/higgsfield/` covers a step, invoke it — do not re-implement.

## Stack

- Next.js 15 App Router, TypeScript, Tailwind
- Supabase (auth + Postgres)
- Stripe (two prices: $29/mo, $79/mo)
- BullMQ + Upstash Redis (job queue)
- Playwright (Amazon cover + blurb scrape)
- S3 (MP4 storage)
- Resend (delivery emails)
- Higgsfield CLI (Phase 1 inference) → local ComfyUI (Phase 2)
- ffmpeg (caption overlay, concat)

## Higgsfield skills used

| Skill | Purpose |
|---|---|
| `higgsfield-generate` | 8 parallel Kling 3.0 / Seedance 2.5 image-to-video jobs, one per camera preset |
| `higgsfield-youtube-thumbnail` | Identity-preserving cover with burned-in text hook (used for the Reel's cover frame + Kindle A+ upsell) |
| `higgsfield-brandkit` | Series-level brand consistency for authors with multi-book runs (Phase 2 upsell) |

## Camera preset library

Store this as `/lib/presets.ts`. Each order fires all 8 in parallel.

```ts
export const CAMERA_PRESETS = [
  { id: "push-in",    prompt_suffix: "slow cinematic push-in on cover, romantic film grain, subtle candlelight glow" },
  { id: "orbit",      prompt_suffix: "smooth 180-degree orbit around subject, shallow depth of field, moody atmospheric lighting" },
  { id: "dolly-in",   prompt_suffix: "steady dolly-in through the scene, anamorphic bokeh, cinematic teal-and-orange grade" },
  { id: "crane-up",   prompt_suffix: "slow crane-up revealing wider environment, golden hour, dust motes floating" },
  { id: "fpv-drone",  prompt_suffix: "FPV drone fly-through, sweeping motion, high energy trailer feel" },
  { id: "pan-right",  prompt_suffix: "slow horizontal pan right across the scene, film grain, contemplative pacing" },
  { id: "zoom-out",   prompt_suffix: "dramatic zoom-out reveal, wide vista, epic scale" },
  { id: "handheld",   prompt_suffix: "handheld tension, subtle shake, thriller-style urgency" },
];
```

## Repo layout to scaffold on first run

```
booktok-trailers/
├── CLAUDE.md                    # this file
├── package.json
├── next.config.js
├── .env.local.example
├── app/
│   ├── page.tsx                 # landing
│   ├── dashboard/page.tsx       # user dashboard: past runs, downloads
│   ├── api/
│   │   ├── generate/route.ts    # POST { amazonUrl } — enqueues job
│   │   ├── stripe/webhook/route.ts
│   │   ├── stripe/checkout/route.ts
│   │   └── jobs/[id]/route.ts   # status polling
├── lib/
│   ├── presets.ts
│   ├── supabase.ts
│   ├── stripe.ts
│   ├── higgsfield.ts            # thin CLI wrapper (Phase 1)
│   └── comfyui.ts               # local endpoint wrapper (Phase 2, empty for now)
├── worker/
│   ├── index.ts                 # BullMQ worker entry
│   ├── scrape.ts                # Playwright: URL → { coverPath, blurb, title, author }
│   ├── generate.ts              # runs 8 preset jobs in parallel
│   ├── caption.ts               # ffmpeg drawtext burn-in
│   └── deliver.ts               # S3 upload + Resend email
├── supabase/
│   └── migrations/0001_init.sql # users, orders, generations
└── scripts/
    └── smoke-test.sh            # end-to-end test against Handy Hearts URL
```

## Environment variables (.env.local)

```
NEXT_PUBLIC_SUPABASE_URL=
NEXT_PUBLIC_SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
STRIPE_PRICE_29=
STRIPE_PRICE_79=
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
S3_BUCKET=booktok-trailers
RESEND_API_KEY=
# Phase 2 additions (leave empty for Phase 1):
COMFYUI_ENDPOINT=
```

## The one function that matters — `worker/generate.ts` (Phase 1)

```ts
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { CAMERA_PRESETS } from "@/lib/presets";
const run = promisify(execFile);

export async function generateTrailers(coverPath: string, blurb: string, jobId: string) {
  const results = await Promise.all(
    CAMERA_PRESETS.map(async (p) => {
      const prompt = `${blurb.slice(0, 200)}. ${p.prompt_suffix}`;
      const { stdout } = await run("higgsfield", [
        "generate", "create", "kling3_0",
        "--prompt", prompt,
        "--start-image", coverPath,
        "--duration", "5",
        "--mode", "pro",
        "--sound", "off",
        "--aspect-ratio", "9:16",
        "--wait",
        "--json",
      ]);
      const { url } = JSON.parse(stdout);
      return { presetId: p.id, url };
    })
  );
  return results;
}
```

**Phase 1 cost per order:** ~$10.40 (8 × $1.30 for 5-sec Kling 3.0 clips).

## Amazon scraping (`worker/scrape.ts`)

```ts
import { chromium } from "playwright";

export async function scrapeAmazon(url: string) {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(url, { waitUntil: "domcontentloaded" });

  const title = await page.locator("#productTitle").innerText();
  const author = await page.locator(".author a").first().innerText().catch(() => "");
  const blurb = await page.locator("#bookDescription_feature_div").innerText();
  const coverUrl = await page.locator("#landingImage").getAttribute("src");

  await browser.close();
  if (!coverUrl) throw new Error("cover not found");
  return { title, author, blurb, coverUrl };
}
```

## First-day checklist

The repo is already scaffolded — all files listed above exist. Your job:

1. `pnpm install && pnpm exec playwright install chromium`
2. Fill `.env.local` from `.env.local.example`. Create the two Stripe prices ($29 and $79 recurring).
3. Apply the migration: `psql "$SUPABASE_DB_URL" -f supabase/migrations/0001_init.sql`
4. Auth into Higgsfield on the worker host: `higgsfield auth login && higgsfield account status`
5. Terminal 1: `pnpm dev`. Terminal 2: `pnpm worker:dev`.
6. Sign up as a test user in the browser, subscribe via Stripe test mode.
7. Grab your session JWT from browser devtools → cookies, export as `SUPABASE_TEST_JWT`.
8. Run `pnpm smoke` against a real Handy Hearts URL — expect 8 MP4s in S3 within ~6 minutes.
9. Deploy: Vercel for the app, one Railway/Fly.io container for the BullMQ worker.
10. Ship. Post the Handy Hearts result on BookTok and DM 20 authors.

## Phase 2 — Hybrid Inference (do NOT start until Idea 1 has 40+ paying users)

**Trigger:** BookTok Trailer Factory reaches 40 paying subscribers.

### Infra changes

1. Rent a RunPod RTX 4090 Community Cloud pod at $0.34/hr, or buy a used RTX 3090 (~$1,000). Install:
   - ComfyUI + ComfyUI-Manager
   - Custom nodes: `ComfyUI-WanVideoWrapper`, `ComfyUI-LTXVideo`, `ComfyUI_IPAdapter_plus`, `ComfyUI-PuLID-Flux`
   - Weights: `Wan-AI/Wan2.2-I2V-A14B`, `Wan2.2-Fun-Camera-Control-14B`, `black-forest-labs/FLUX.1-schnell`
2. Export 8 API-format workflow JSON files, one per camera preset, saved as `worker/workflows/wan22_{preset_id}.json`.

### Code changes

Add `lib/comfyui.ts`:

```ts
import { readFileSync } from "node:fs";

export async function runComfyWorkflow(workflowPath: string, imagePath: string, prompt: string) {
  const workflow = JSON.parse(readFileSync(workflowPath, "utf8"));
  // Inject prompt + image into known node ids (positive prompt node = "6", image loader = "14")
  workflow["6"].inputs.text = prompt;
  workflow["14"].inputs.image = imagePath;

  const res = await fetch(`${process.env.COMFYUI_ENDPOINT}/prompt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt: workflow }),
  });
  const { prompt_id } = await res.json();

  // Poll history for completion
  while (true) {
    const h = await fetch(`${process.env.COMFYUI_ENDPOINT}/history/${prompt_id}`).then(r => r.json());
    if (h[prompt_id]?.status?.completed) {
      const output = h[prompt_id].outputs["9"].videos[0];
      return `${process.env.COMFYUI_ENDPOINT}/view?filename=${output.filename}&subfolder=${output.subfolder}&type=${output.type}`;
    }
    await new Promise(r => setTimeout(r, 2000));
  }
}
```

Modify `worker/generate.ts`:

```ts
export async function generateTrailers(coverPath: string, blurb: string, jobId: string) {
  const useLocal = !!process.env.COMFYUI_ENDPOINT;

  const results = await Promise.all(
    CAMERA_PRESETS.map(async (p) => {
      const prompt = `${blurb.slice(0, 200)}. ${p.prompt_suffix}`;
      const url = useLocal
        ? await runComfyWorkflow(`worker/workflows/wan22_${p.id}.json`, coverPath, prompt)
        : await runHiggsfield(coverPath, prompt);           // existing Phase 1 code
      return { presetId: p.id, url };
    })
  );
  return results;
}
```

**Phase 2 cost per order:** ~$3.10 (blend of local + API burst for hero shots).
**Phase 3 cost per order:** ~$0.10 (fully local, API only for failover).

## Distribution playbook (owner runs, not Claude)

- Day 4: dogfood on Handy Hearts. Post to `@dkgrissom` BookTok + tag `@higgsfield_ai`.
- Days 5–10: DM 50 KDP romance authors with a free trailer built from their book.
- Day 11: post in 5 romance-writing FB groups with Handy Hearts before/after.
- Day 14: reach out to 10 BookTok influencers with 30% recurring affiliate.

## Definition of done (Phase 1)

- [ ] `pnpm dev` runs locally.
- [ ] Signing up + subscribing to $29 tier works end-to-end.
- [ ] Pasting a real Amazon book URL produces 8 MP4s in S3 within 6 minutes.
- [ ] Email delivery includes signed URLs for all 8.
- [ ] Handy Hearts trailers posted publicly.
- [ ] First paying customer other than the operator.
