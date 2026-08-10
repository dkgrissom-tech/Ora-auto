# Shared spine — read before writing any funnel brief

Both halves of the funnel build inherit this file. It exists so two people working in
parallel produce assets that fit the same pipeline instead of two incompatible piles.

**Date:** 2026-08-10 · **Launch:** Tuesday Sept 8 2026 (29 days) · **Paid ads: out of scope.**

## The decision that shapes everything

No paid spend. Every unit must earn its own distribution. That rules out anything whose
performance depends on budget, and it rules *in* three things: search-durable content,
lead magnets that trade something real for an email, and borrowed audiences (other
people's lists, communities, and readers).

Practical consequence: **an "ad" here is a piece of organic content engineered to convert.**
Same discipline as a paid ad — one hook, one promise, one destination — but it has to survive
without a media buy behind it.

## Funnel doctrine

Every product gets the same five-stage shape. If a unit doesn't sit in a named stage, it
doesn't get built.

| Stage | Job | Success signal |
|---|---|---|
| 1. Reach | Get in front of a stranger on a free surface | impressions, saves, shares |
| 2. Hook | Earn one click | click-through to the magnet |
| 3. Capture | Trade value for an email | email captured |
| 4. Nurture | Build enough trust to buy | open rate, replies |
| 5. Convert | Ask for the sale once, clearly | preorder, purchase, install |

Two rules that matter more than they sound:

- **Every reach unit must name its destination.** A post with no next step is a hobby.
- **Capture beats conversion before launch.** A preorder is one sale. An email is every
  future launch. Until Sept 8, weight the funnel toward stage 3.

## Free surfaces, ranked by realistic return

Ranked for *these* products specifically, not in general.

**Tier 1 — build here first**

- **Pinterest.** Longest content half-life of any free surface; a pin drives traffic for
  months. Dominant for coloring books and strong for romance. Currently offline in the
  pipeline (see Constraints) but being repaired tonight — build the assets anyway.
- **Email.** The only audience nobody can throttle. Every funnel terminates here.
- **Newsletter swaps / cross-promos.** Borrowed lists, zero cost. StoryOrigin and
  BookFunnel group promos for romance; creator swaps for the apps.

**Tier 2 — real return, more effort**

- **TikTok / Reels / Shorts** — same vertical asset, three destinations.
- **Tumblr** — genuinely undervalued for romance; long reblog tails.
- **Bluesky** — working in the pipeline right now, and the only channel confirmed
  delivering today.
- **Facebook Groups** — coloring and parenting communities convert well and tolerate
  self-promo when it leads with a freebie.

**Tier 3 — worth a slot, don't over-invest**

- Reddit (strict self-promo rules — read each sub's policy or get banned), Threads,
  Goodreads author profile, BookBub author profile, Amazon Follow, KDP A+ content,
  Instagram, Lemon8, Discord communities, Indie Hackers / BetaList / Product Hunt for Ora.

**Do not build for:** X (manual-approval-only by policy), YouTube long-form (no publisher
exists in the pipeline), anything requiring ad spend.

## Hard constraints — violating these breaks the pipeline

**Setting:** Cedar Hollow is in **Muskogee County, OKLAHOMA**, population 1,847. Never
Tennessee. Eastern Oklahoma is oak and hickory woodland, red clay, rolling hills, big sky,
cross-timbers. Never Appalachian mountains or misty peaks.

**Channel reality as of this morning, measured from run logs — not assumed:**

| Channel | State | What it means for you |
|---|---|---|
| Bluesky | working | safe to schedule |
| Instagram via Buffer | working, but see cap bug | safe, schedule sparingly |
| Pinterest | **offline, silently rerouted to Instagram** | build assets, do not schedule until fixed tonight |
| Threads | credentials empty | write copy, hold scheduling |
| LinkedIn | credentials empty | Ora only, hold scheduling |
| TikTok | brand-gated to `ora`, no token | build assets, hold scheduling |
| X | manual approval only | never auto-schedule |
| YouTube | no publisher code exists | ignore |

Two live bugs to route around, both being fixed tonight:

1. Pinterest posts reroute to Instagram at the wrong aspect ratio (pins are 2:3, Instagram
   wants 4:5), so they get center-cropped through the text overlay.
2. The Instagram "daily cap" resets every run instead of every day, so Instagram can be
   over-posted. **Keep new Instagram scheduling light until this is fixed.**

**Brand facts, load-bearing:**

- **Handy Hearts** — Book One, pen name **D.K. Grissom**, launches **Tue Sept 8 2026**.
  43,407 words, 16 chapters. $3.99 ebook / $7.99 boxed set. KU-exclusive 90 days, then
  wide. Tagline: **"Grief doesn't end. It changes shape."** Landing: `cedarhollow.pplx.app`
  - Characters: **Don Rourke** (handyman, 42, ex-Navy Seabee, blond going silver, blue
    eyes). **Dana Whitfield** (widow ~14 months, honey-blonde, green eyes, freckled,
    **still wears her wedding ring**). **Nancy Beaumont** (Hollow Bean Café).
  - Series: Handy Hearts → *Hollow Bean* (Nancy/Wes, spring 2027) → *Whistlepig Nights*
    (Cal/Ellen). Lead magnet novella: **The Porch Before**.
- **Grissom Press** — `grissompress.pplx.app`. Gumroad: Dark & Dreamy Gothic `/l/pfaepq`,
  Spooky Sweet Shop `/l/usdqt`, Cozy Goth Mega Bundle `/l/wucxhi`. Pinterest-led.
  TikTok Shop sells physical paperbacks; **drive TikTok traffic to Shopify, not Amazon**
  (4–5× the profit per unit).
- **Family Book Creator** — `familybookcreator.app`. Gumroad `/l/wcnuhs` ($29.95) and
  `/l/aulfo` ($5). Discount code **FIRSTBOOK50**. **Intentionally skips TikTok** — do not
  add it.
- **Ora** — `@meetora`, waitlist stage, `meetora-app.pplx.app`. Zara is the AI persona used
  for faceless demos.

**Email:** MailerLite, sending from dkgrissom@gmail.com. **Bluesky:** posts go out from
`grissompress.bsky.social`.

## Visual rules

Reuse the established system rather than inventing a second one —
`docs/pin_style_guide.md` has the full version. Short form:

- **No identifiable faces.** Hands, backs of heads, silhouettes, cropped torsos, objects
  implying a person. Applies to romance especially; it's the genre convention and it avoids
  uncanny generated faces.
- **No text baked into generated images.** Generate clean, overlay type in Canva. Every
  prompt reserves a quiet low-detail third for it.
- **Handy Hearts / Grissom Press palette:** weathered cedar, honey gold, cream, dusty sage,
  faded denim, rust sparingly. 35mm film, Kodak Portra 400 grain, natural light only.
- **Specs:** Pinterest 2:3 at 1000×1500 · Instagram 4:5 at 1080×1350 · vertical video 9:16
  at 1080×1920 · Tumblr 4:5 or square.
- **Never** teal-and-orange grading, plastic skin, floating dust particles, lens flare,
  illegible pseudo-text, or stock-photo eye contact.

Write geography as a **positive assertion**, not a negation. "The horizon stays low and
rolling" works; "no mountains" often produces mountains, because image models weight nouns
and drop negations.

## Deliverable format — both halves must match

Every unit you write uses this exact block. Consistency is what lets these get scheduled
in bulk tonight.

```
### UNIT <ID>
**Product:** Handy Hearts | Grissom Press | Family Book Creator | Ora
**Stage:** 1 Reach | 2 Hook | 3 Capture | 4 Nurture | 5 Convert
**Surface:** Pinterest | Bluesky | Tumblr | TikTok/Reels/Shorts | Email | Facebook Group | ...
**Format:** e.g. Pinterest pin, 2:3, 1000x1500
**Destination:** exact URL
**Hook:** first line, or first 2 seconds for video — the whole unit lives or dies here
**Copy:**
<the actual finished text, ready to publish — not a description of the text>
**CTA:** one clear ask
**Asset needed:** image prompt / video shot list / "none"
**Filename:** brands/<brand>/assets/<descriptive-slug>.<ext>
**Schedule:** date + UTC hour, or HOLD with the reason
```

Two things people get wrong here: writing *about* the copy instead of writing the copy, and
inventing a filename that doesn't match the asset. Write finished text. Match filenames.

## Pipeline intake — how these actually get published

Anything ready to schedule goes in `clone_drafts/<brand>/` as a markdown file with YAML
frontmatter. Brands are exactly `ora`, `grissom`, `familybook`. Handy Hearts and the
coloring books **share the `grissom` brand**.

```markdown
---
kind: post
brand: grissom
platforms: [bluesky]
scheduled: 2026-09-08T18:00:00-05:00
image: brands/grissom/assets/hh-launch-day-pin.jpg
filename: hh-launch-day-bluesky
---
Post body goes here, exactly as it should publish.
```

Details that break ingestion if you get them wrong:

- `platforms` is **bracketed** in intake (`[bluesky]`) but comma-separated once it lands in
  the queue file. Use brackets here.
- `scheduled` needs the **full ISO timestamp with offset**. `-05:00` is CDT.
- `image` / `video` paths are **repo-relative**, and the file must exist or the post fails
  at the platform with a 404.
- Instagram and Pinterest posts are dropped silently if there's no `image`.

## Where to save your work

- Brief A → `docs/funnels/A_*.md`
- Brief B → `docs/funnels/B_*.md`
- Ready-to-schedule posts → `clone_drafts/<brand>/`
- Image and video assets → `brands/<brand>/assets/`

Commit convention: `feat:` / `fix:` / `docs:`, subject under 72 characters, straight to
`main`, no branches. Append `[skip ci]` unless the Actions run should fire.

**Do not touch:** `scripts/run_scheduler.py`, `.github/workflows/`, or anything in
`brands/*/posts/`. Wiring happens tonight, separately. Two people editing the publisher at
once is how duplicate posts and deleted drafts happen.

## Definition of done

- Every unit sits in a named funnel stage with a real destination URL
- Copy is finished and publishable, not described
- Every asset has a prompt and a filename that match
- Anything scheduled respects the channel table above
- Nothing violates the Oklahoma rule, the no-faces rule, or the no-baked-text rule
