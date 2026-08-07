# Handoff Brief — Module 2: Marketing Plan & Content Engine

**For:** Claude (or Twin) working in `dkgrissom-tech/Ora-auto`
**From:** the n8n/Module 1 work session, Aug 7 2026
**Status of Module 2 when this was written:** 0% — none of the target files exist

Read this whole brief before writing anything. It contains corrections to the
original weekend brief, which is stale in three places that will cause you to
produce files the automation cannot consume.

---

## 1. Corrections to the original weekend brief

The weekend master brief (`Claude-Weekend-Master-Directions--n8n--Marketing--Video-Pipeline.md`)
is wrong or outdated on these points. Trust this document instead.

| Brief says | Reality in the repo | Consequence |
|---|---|---|
| Drafts live in `content_drafts/` | That folder does not exist. Intake is `clone_drafts/<brand>/` | Writing to `content_drafts/` produces dead files |
| 5 brands including Grissom Shop (@grissomshop) | Only `ora`, `grissom`, `familybook` exist under `brands/`, `clone_drafts/`, `video_drafts/` | See §2 — ask Don before inventing a 4th brand folder |
| — | The **posting queue** is `brands/<brand>/posts/YYYY-MM-DD.md`, not the intake folder | This is the format that actually publishes. See §3 |

**Verify before you trust anything here.** `scripts/run_scheduler.py` is the
source of truth for what publishes; `scripts/ingest_clone_drafts.py` is the
source of truth for how intake becomes queue.

## 2. Open question — do not guess

`brands/grissomshop/` does not exist, but the brief lists Grissom Shop
(@grissomshop, cozy-goth coloring books, TikTok Shop lane) as a brand. Two
readings: it is a *sales channel* of Grissom Press, or it is a separate brand
needing its own folders. **Ask Don. Do not create the folder on your own** — the
scheduler iterates a hardcoded `BRANDS = ["ora", "grissom", "familybook"]` list
(`scripts/run_scheduler.py:38`), so a new folder posts nothing until that list
and the n8n `List Brands` node are both updated.

## 3. The two file formats — get these exactly right

### Intake (what you write): `clone_drafts/<brand>/<slug>-<date>.md`

YAML frontmatter, one post per file, body is the post text:

```
---
kind: post
brand: grissom
platforms: [bluesky]
scheduled: 2026-09-08T18:00:00-05:00
image: brands/grissom/assets/whatever.jpg
filename: handy-hearts-launch-day-2026-09-08.md
---
Post body goes here. This exact text is what publishes.
```

Rules, all verified against the 109 real drafts in `clone_drafts/grissom/_processed/`:
- `platforms` is a **bracketed list**: `[bluesky]`, `[pinterest]`
- `scheduled` is **full ISO 8601 with offset**: `2026-09-08T18:00:00-05:00`. Not a bare date
- `image` / `video` are **repo-relative paths**, never URLs
- Instagram and Pinterest posts **must** have an `image` — they are dropped without one
- Body is plain text. No `## Shot list` sections — those belong in `video_drafts/`

### Queue (what ingest produces, and what publishes): `brands/<brand>/posts/YYYY-MM-DD.md`

Many posts per file, split on `## `, meta above the first `---`, body between the
two `---`:

```
## 18:00 UTC  (13:00 CDT)
platforms: pinterest
image: brands/grissom/assets/pin1.png
pinterest_title: Dark & Dreamy Gothic Coloring Book
pinterest_url: https://grissom77.gumroad.com/l/pfaepq
---
Body text here.
---
```

Note the differences from intake: **platforms are comma-separated here, not
bracketed**, and the hour in the `## ` header is **UTC**. A block fires only when
its UTC hour equals the current hour.

**You normally should not hand-write queue files** — write intake files and let
`ingest_clone_drafts.py` convert them. If you do write queue files directly, match
this format character for character.

### Known content gap to fix as you go

61 of the 66 Pinterest pins scheduled Aug 4–18 have **no `pinterest_title` and no
`pinterest_url`**. The n8n pipeline now derives a title from the first body line
and falls back to a per-brand link env var, but that is a safety net, not a fix.
**Every Pinterest post you write must include `pinterest_title` and
`pinterest_url`.** A pin without a destination link cannot drive preorders.

## 4. Current state — where the gaps actually are

Queue depth as of Aug 7 2026:

| Brand | Day files | Queue runs through | Verdict |
|---|---|---|---|
| grissom | 16 | **2026-08-18** | healthy |
| ora | 8 | **2026-07-25** | dry 13 days |
| familybook | 1 | **2026-06-28** | effectively dead |

Platform mix, Aug 4–18, all brands: 66 pinterest, 14 threads, 10 bluesky, 9
tiktok, 7 instagram, 3 linkedin. That is **73% Pinterest and one brand**.

So the highest-value work is not more Grissom Pinterest pins. It is:
1. Ora and Family Book Creator queues, which are empty
2. Platform diversity for Grissom beyond Pinterest
3. The Sept 8 launch window, which has no content at all past Aug 18

## 5. Deliverables

### 5.1 `marketing_plan.md` (repo root)

Success test, quoted from the original brief: **"Don can open marketing_plan.md
on his phone and know exactly what to post today."** Optimize for that. Phone
reading means short lines, tables that do not sprawl, today-first ordering.

- **Section 1 — Positioning**, one block per brand (ora, grissom, familybook, plus
  grissomshop only if Don confirms §2). Each: one-sentence promise, audience,
  3 content pillars, what never to post, canonical link.
- **Section 2 — Weekly cadence**, a table per brand: day × time (UTC and CDT) ×
  platform × pillar. Must not schedule Instagram or Pinterest slots without a
  matching image asset, and must not put TikTok slots on familybook — Family Book
  Creator intentionally skips TikTok. TikTok is also currently `ora`-only in
  `run_scheduler.py:306`.
- **Section 3 — Launch calendar, Aug 7 – Dec 31 2026.** Anchor: **Handy Hearts
  launches Tuesday Sept 8 2026.** Phases: pre-order push (now–Sept 7), launch week
  (Sept 8–14), sustain (Sept 15–Oct 31), holiday (Nov–Dec, coloring books are the
  Q4 earner). Mark KU-exclusive window: 90 days from Sept 8, wide after.
- **Section 4 — Prompts #01–30** in `content_prompts/prompt_01.md` … `prompt_30.md`,
  indexed from `marketing_plan.md`. Each prompt is a reusable generator that
  **must instruct its output into the §3 intake format**. Spread them across
  brands and pillars, not 30 Pinterest variants.
- **Section 5 — Platform playbooks**, `docs/platform_playbooks/<platform>.md` for
  all eight: bluesky, threads, pinterest, tiktok, instagram, linkedin, x, youtube.
  Each: character limit, image/video specs, cadence ceiling, hashtag norms, what
  gets throttled, and **how that platform is wired here** — see §6, this part
  matters and is easy to get wrong.

### 5.2 Queue refill

After the plan exists, write intake drafts to close the §4 gaps. Priority order:
Ora (13 days dry) → Handy Hearts Sept 8 launch window → Family Book Creator →
Grissom non-Pinterest.

## 6. Platform wiring facts for the playbooks

Publishing is moving from per-platform APIs in the GitHub Action to **self-hosted
Postiz**. Do not write playbooks that tell Don to get Meta or TikTok tokens.

- **X is manual-only by policy.** `run_scheduler.py:324` deliberately skips it and
  the n8n pipeline preserves that. The X playbook must say "draft here, post by
  hand" unless Don changes the policy.
- **TikTok and YouTube are video** and run through the separate video pipeline
  (`video_drafts/`), not the short-form one. TikTok is allowed for `ora` only.
- **Bluesky posts from `grissompress.bsky.social`**, not `dkgrissom.bsky.social`.
- **Pinterest is blocked upstream** — the developer app needs resubmission. Pins
  will queue and fail until that clears. Say so in the playbook.
- **Postiz covers** bluesky, threads, instagram, pinterest, linkedin, mastodon.
- Postiz rate limits: **30 uploads/hour, 90 post-creations/hour.** A cadence that
  exceeds these will silently drop posts. Section 2 must stay under them.

## 7. Brand facts — get these right, they are load-bearing

- **Cedar Hollow is in OKLAHOMA** (Muskogee County, pop. 1,847). **Never Tennessee.**
- **Handy Hearts** — Book One, pen name **D.K. Grissom**, launches **Tue Sept 8 2026**.
  43,407 words, 16 chapters. $3.99 single / $7.99 boxed set. KU-exclusive 90 days,
  then wide (Apple, Kobo, B&N, Gumroad).
- Series tagline: **"Grief doesn't end. It changes shape."**
- Series order: Handy Hearts → *Hollow Bean* (Bk2, Nancy/Wes, spring 2027) →
  *Whistlepig Nights* (Bk3, Cal/Ellen). Five interconnected standalones over 18 months.
- Characters: **Don Rourke** (handyman, 42, blond going silver, blue-eyed);
  **Dana** (widow, honey-blonde, green-eyed, freckled); **Nancy Beaumont**
  (owns the Hollow Bean Café).
- Reader magnet novella: *The Porch Before*. Reader Circle email list.
  Landing page `cedarhollow.pplx.app`. BookBub Featured Deal target late Jan 2027.
- **Grissom Press** — hub `grissompress.pplx.app`; owns `grissompress.com`
  (Cloudflare, not yet pointed). Pinterest-led. Gumroad: Dark & Dreamy Gothic
  `/l/pfaepq`, Spooky Sweet Shop `/l/usdqt`, Cozy Goth Mega Bundle `/l/wucxhi`.
- **Family Book Creator** — `familybookcreator.app`. Gumroad `/l/wcnuhs` ($29.95)
  + `/l/aulfo` ($5 add-on). Code `FIRSTBOOK50`. **Intentionally skips TikTok.**
- **Ora** — @meetora on X/TikTok/IG. Waitlist play. Zara AI persona for faceless demos.
- **TikTok traffic should route to Shopify, not Amazon** (4–5× profit per unit).

## 8. Conventions

- Commit prefixes `feat:` / `fix:` / `docs:`, subject under 72 chars, push straight
  to `main`, no branches. Add `[skip ci]` unless you intend the Actions to fire.
- Unexpected errors → `debug_log/<date>.md`. Blockers → `WEEKEND_BLOCKERS.md`.
- Missing secrets → add to `docs/n8n-env-var-checklist.md`. **Never hardcode
  placeholder secrets.**
- Do not touch `n8n_workflows/`, `scripts/run_scheduler.py`, or the `.github/workflows/`
  files without flagging it — Module 1 owns those and they are mid-migration.

## 9. Definition of done

- [ ] `marketing_plan.md` exists, all 5 sections, readable on a phone
- [ ] `content_prompts/prompt_01.md` … `prompt_30.md` exist and are indexed
- [ ] `docs/platform_playbooks/` has all 8 files with the §6 wiring facts
- [ ] Every Pinterest example includes `pinterest_title` and `pinterest_url`
- [ ] No file claims Cedar Hollow is in Tennessee
- [ ] No playbook tells Don to fetch Meta or TikTok tokens
- [ ] Ora and familybook queues have content again
- [ ] Sept 8 launch window is covered
- [ ] §2 grissomshop question is answered or explicitly logged as open
