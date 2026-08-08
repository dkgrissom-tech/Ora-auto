# Marketing plan — Don Grissom portfolio

**Operating date:** Friday, August 7, 2026, 7:18 PM CDT  
**North star:** make the next right post obvious; do not fill the queue for its own sake.

## TODAY — Friday, Aug 7 (CDT)

| When | Do this | Do not do this |
|---|---|---|
| Now | Check the 7:05 PM CDT Action log. The 7:00 PM Bluesky block came from the Aug. 8 UTC queue and contains the wrong location; do not repost it. | Cedar Hollow is in Muskogee County, Oklahoma. |
| Before 9:00 PM | Audit the Aug. 8–18 Grissom queue. Replace every incorrect-state reference with Oklahoma; remove Grissom TikTok blocks or move the idea to an approved non-TikTok format. | Do not hand-write a new queue block as a shortcut. Use intake after this audit. |
| 9:00 PM | No manual post. A Grissom Pinterest attempt is already queued at 02:00 UTC in the Aug. 8 file. Check the Action log afterward. | Do not duplicate the pin by hand. Pinterest is blocked pending developer-app resubmission. |
| Before bed | Stage Monday’s Ora text post and Tuesday’s Family Book Creator text post in `clone_drafts/`; use a real repo asset only for an image/video slot. | Do not post to X unless a specific manual X post is approved. |

## THIS WEEK — Aug 7–13

1. **Protect the Handy Hearts launch.** Correct the location error in every future Grissom draft/queue entry before its scheduled hour.
2. **Refill the dry brands first.** Build one week of Ora, then one week of Family Book Creator, through intake—not by editing the live queue.
3. **Unblock what can publish.** Bluesky is the dependable text lane. Grissom Threads stays off until both required repo secrets are present. Pinterest stays queued/off until its developer app is approved.
4. **Asset gate every visual.** A post may name Instagram or Pinterest only after its exact `brands/<brand>/assets/...` file exists. Every Pinterest draft needs both `pinterest_title` and `pinterest_url`.
5. **Keep the launch fact sheet fixed.** *Handy Hearts* is Book One by D.K. Grissom, launching Tuesday, Sept. 8, 2026; Cedar Hollow is Oklahoma.

### Publishing control panel

The live publisher is GitHub Action `auto_post.yml`, hourly at `:05 UTC`, running `scripts/run_scheduler.py`. The queue is UTC-dated; a 9:00 PM CDT Friday slot is 02:00 UTC in Saturday’s file. Postiz is parked and is not a publishing dependency.

| Lane | Status now | Rule |
|---|---|---|
| Bluesky | Live text lane | Grissom publishes as `grissompress.bsky.social`. |
| Threads | Grissom is dead | Needs `GRISSOM_THREADS_USER_ID` and `GRISSOM_META_LONG_TOKEN` as repo secrets. |
| Instagram | Asset-gated | Schedule only with a verified image file. |
| Pinterest | Blocked upstream | Developer-app resubmission is pending; queue only after an image, title, and destination URL exist. |
| LinkedIn | Text lane | Use for Ora operator insight and Family Book Creator point of view. |
| TikTok | Ora only | Use a real vertical video; never schedule it for Grissom or Family Book Creator. |
| X | Manual-only | Draft here if useful; Don posts by hand. |
| YouTube | Video lane | Use its video workflow, not the short-form queue. |

> **Clock note:** times below are UTC / CDT through the Nov. 1 daylight-saving change. After that change, use CST, one hour earlier locally (for example, 14:00 UTC = 8:00 AM CST).

---

## 1. Positioning

### Ora

- **Promise:** Ora is a waitlist-stage iPhone meeting assistant for people who want conversations turned into clear follow-up instead of another pile of notes.
- **Audience:** busy iPhone-first operators, founders, and small teams who leave meetings with work to remember and follow through.
- **Pillars:** meeting pain → outcome; useful product proof; Zara-led faceless demos and waitlist urgency.
- **Never post:** fake customer proof; unverified launch dates, prices, integrations, or privacy claims; generic “AI changes everything” filler.
- **Canonical link:** <https://meetora-app.pplx.app>
- **Identity:** `@meetora` on X, TikTok, and Instagram.

### Grissom Press

- **Promise:** Grissom Press gives readers emotionally honest escape through D.K. Grissom’s small-town romance and a dark/cozy coloring-book catalog.
- **Audience:** readers of slow-burn, grief-aware small-town romance; secondarily, cozy-goth coloring-book and gift buyers.
- **Pillars:** *Handy Hearts* characters, tropes, and emotional truth; Cedar Hollow and the Reader Circle; gothic/cozy coloring books and seasonal bundles.
- **Never post:** a Cedar Hollow location other than Oklahoma; grief as something a hero “fixes”; spoilers; invented preorder/wide dates; Grissom TikTok posts.
- **Canonical hub:** <https://grissompress.pplx.app>
- **Reader Circle / *The Porch Before*:** <https://cedarhollow.pplx.app>
- **Catalog:** [Dark & Dreamy Gothic Coloring Book](https://grissom77.gumroad.com/l/pfaepq) · [Spooky Sweet Shop](https://grissom77.gumroad.com/l/usdqt) · [Cozy Goth Mega Bundle](https://grissom77.gumroad.com/l/wucxhi)

**Handy Hearts fact lock**

- Book One by D.K. Grissom; 43,407 words; 16 chapters.
- $3.99 single / $7.99 boxed set.
- Series line: **“Grief doesn't end. It changes shape.”**
- Don Rourke: 42, blond going silver, blue-eyed.
- Dana: honey-blonde, green-eyed, freckled.
- Nancy Beaumont owns the Hollow Bean Café.
- Order: *Handy Hearts* → *Hollow Bean* (Nancy/Wes, spring 2027) → *Whistlepig Nights* (Cal/Ellen).

### Family Book Creator

- **Promise:** Family Book Creator turns a child’s photo into a personalized story where that child is the hero.
- **Audience:** parents, grandparents, and gift buyers who want a meaningful, customized children’s book.
- **Pillars:** child-as-hero product proof; parent/grandparent emotion; gifting, add-ons, and seasonal conversion.
- **Never post:** TikTok; a child’s name, image, or testimonial without documented permission; unverified delivery promises or discounts.
- **Canonical link:** <https://familybookcreator.app>
- **Offer facts:** Gumroad [main product](https://gumroad.com/l/wcnuhs) ($29.95) · [add-on](https://gumroad.com/l/aulfo) ($5) · code `FIRSTBOOK50`.

### Open question — Grissom Shop

Is Grissom Shop a Grissom Press sales channel or a separate automation brand? Do not create `brands/grissomshop/`, a cadence, or a new account workflow until Don decides. The live scheduler currently recognizes only `ora`, `grissom`, and `familybook`.

---

## 2. Weekly cadence

**Use this as the default after the Aug. 7 cleanup.** It deliberately reduces the current Pinterest-heavy pattern and restores Ora and Family Book Creator. An **asset-gated** row is a reservation, not a scheduled post: create its intake/queue entry only after the exact asset file has been verified. If a blocked lane is still blocked, use the listed idea as the next Bluesky post instead.

### Ora

| Day | Time | Platform | Pillar |
|---|---|---|---|
| Mon | 14:00 UTC / 9:00 AM CDT | Bluesky | One meeting pain, one concrete outcome |
| Tue | 17:00 UTC / noon CDT | LinkedIn | Builder/operator lesson |
| Wed | 14:00 UTC / 9:00 AM CDT | Bluesky | Product proof or speaker/follow-up workflow |
| Thu | 16:00 UTC / 11:00 AM CDT | Instagram — asset-gated | Zara faceless demo |
| Fri | 18:00 UTC / 1:00 PM CDT | TikTok — Ora-only, video-gated | Zara vertical demo + waitlist |
| Sat | 14:00 UTC / 9:00 AM CDT | Bluesky | Waitlist urgency or FAQ |

### Grissom Press

| Day | Time | Platform | Pillar |
|---|---|---|---|
| Mon | 14:00 UTC / 9:00 AM CDT | Bluesky | Trope, hook, or exact launch fact |
| Tue | 17:00 UTC / noon CDT | Threads — blocked until secrets | Reader question or character conversation |
| Thu | 17:00 UTC / noon CDT | Bluesky + LinkedIn | Author note, grief-aware craft, Reader Circle |
| Fri | 16:00 UTC / 11:00 AM CDT | Instagram — asset-gated | Cover, character, or quote card |
| Sat | 14:00 UTC / 9:00 AM CDT | Pinterest — asset-gated/blocked | One mood, trope, or catalog pin |
| Sun | 14:00 UTC / 9:00 AM CDT | Bluesky | Cedar Hollow world or reader-magnet invitation |

**Grissom visual rule:** the repository currently lacks the Handy Hearts image/video paths referenced by much of the Aug. 4–18 queue. Do not schedule another Handy Hearts Instagram or Pinterest post until its actual asset is restored or created. Existing gothic-coloring assets may support the catalog lane only.

### Family Book Creator

| Day | Time | Platform | Pillar |
|---|---|---|---|
| Tue | 16:00 UTC / 11:00 AM CDT | Bluesky | Parent feeling: child as hero |
| Wed | 16:00 UTC / 11:00 AM CDT | Instagram — asset-gated | Sample-page or product proof |
| Thu | 19:00 UTC / 2:00 PM CDT | LinkedIn | Personalization point of view |
| Sat | 19:00 UTC / 2:00 PM CDT | Pinterest — asset-gated/blocked | Gift or seasonal discovery pin |
| Sun | 16:00 UTC / 11:00 AM CDT | Bluesky | Gift CTA, add-on, or `FIRSTBOOK50` |

**Cadence checklist before ingest:** correct brand; UTC date/time; a real asset for Instagram/Pinterest; a real video for Ora TikTok; Pinterest title and URL; no X auto-post; no familybook or Grissom TikTok.

---

## 3. Launch calendar — Aug. 7 to Dec. 31, 2026

**Anchor:** *Handy Hearts* launches **Tuesday, Sept. 8, 2026**.  
**KU window:** Sept. 8–Dec. 6 (90 days). Plan wide listings for **Dec. 7 onward**, only after confirming the KDP enrollment end date. Wide targets: Apple, Kobo, B&N, and Gumroad.

| Dates | Handy Hearts / Grissom Press | Ora + Family Book Creator | Gate / CTA |
|---|---|---|---|
| Aug. 7–9 | Repair the live queue: Oklahoma everywhere; no Grissom TikTok; preserve only truthful preorder copy. | Stage the first fresh weekly intake files. | Stop bad posts before adding volume. |
| Aug. 10–16 | Characters and tropes: Don, Dana, Nancy; reader-magnet invitation. | Start the §2 cadence. | Preorder / Reader Circle; Ora waitlist; Family Book product page. |
| Aug. 17–23 | “Three weeks” countdown; first-reader/ARC interest; no spoilers. | Keep text-first cadence; use visual slots only with real assets. | Build intent, not false urgency. |
| Aug. 24–30 | “Two weeks” mood, porch, small-town, and grief-aware promise. | Ora proof; Family Book parent/gift proof. | Preorder and email-list growth. |
| Aug. 31–Sept. 7 | Final-week countdown; explain who the book is for; prepare launch-day copies. | Maintain baseline only; do not let side brands consume launch time. | Final preorder / Reader Circle. |
| **Tue. Sept. 8** | **Launch day:** one Bluesky launch post; Threads only if fixed; one visual only if asset exists; send Reader Circle update. | Keep only pre-scheduled baseline posts. | “*Handy Hearts* is live” with the approved purchase link. |
| Sept. 9–14 | Launch-week follow-through: reader reactions, trope fit, and a respectful review ask. | Resume full weekly cadence. | Review only after readers have time; invite list sign-up. |
| Sept. 15–30 | Sustain: quote cards, Don/Dana moments, Cedar Hollow, and *The Porch Before*. | Continue product proof and conversion each week. | Book purchase / Reader Circle. |
| Oct. 1–15 | Keep Book One visible; seed *Hollow Bean* as Nancy/Wes, spring 2027. | Keep queues at least seven days ahead. | Reader retention, not a new release claim. |
| Oct. 16–31 | Shift the catalog lane toward dark/cozy coloring; keep romance evergreen. | Family Book: early holiday gift planning. | Coloring-book catalog / gift planning. |
| Nov. 1–15 | Holiday opener: coloring books are the Q4 earning lane; use approved bundle links. | Family Book gift proof; Ora stays waitlist-focused. | Gift discovery and bundle consideration. |
| Nov. 16–30 | Holiday conversion: catalog/bundle use cases, not made-up discounts. | Family Book gifting; use `FIRSTBOOK50` only as stated. | Approved offer and direct product links. |
| Dec. 1–6 | Final KU-exclusive week; prepare wide metadata and links off-channel. | Keep baseline; no launch distraction. | Do not announce wide availability yet. |
| Dec. 7–13 | Publish wide availability only after verification; name Apple, Kobo, B&N, and Gumroad only when live. | Gift reminders for Family Book; Ora year-end workflow. | Wide purchase path / gift path. |
| Dec. 14–31 | Last-minute digital coloring gifts; Reader Circle year-end note; tease 2027 carefully. | Family Book final gift push; Ora waitlist recap. | Email capture and January audience. |

### Launch-week fact guardrails

- Say **Cedar Hollow, Oklahoma** every time location matters.
- Say **D.K. Grissom**, *Handy Hearts*, Book One, and **Sept. 8, 2026** before launch; do not guess at any retailer URL.
- Keep grief language human: Dana is not broken, and Don is not a fix.
- Do not use Grissom TikTok to support the launch. TikTok is Ora-only.

---

## 4. Prompt index — #01–30

Another owner writes these files. The number encodes the brand and pillar so selection is fast: **01–10 Grissom Press**, **11–20 Ora**, **21–30 Family Book Creator**. Each prompt must tell its generator to emit one `clone_drafts/<brand>/<slug>-<date>.md` intake file—not a queue block—with bracketed platforms, a full ISO `scheduled` value, repo-relative media paths, and Pinterest title/URL when needed.

- **Grissom 01–04 — Handy Hearts:** [01 hook/trope](content_prompts/prompt_01.md) · [02 Don](content_prompts/prompt_02.md) · [03 Dana](content_prompts/prompt_03.md) · [04 Cedar Hollow](content_prompts/prompt_04.md)
- **Grissom 05–08 — Handy Hearts:** [05 grief-aware quote](content_prompts/prompt_05.md) · [06 preorder](content_prompts/prompt_06.md) · [07 Reader Circle](content_prompts/prompt_07.md) · [08 launch/review](content_prompts/prompt_08.md)
- **Grissom 09–10 — catalog:** [09 coloring-book discovery](content_prompts/prompt_09.md) · [10 cozy-goth bundle](content_prompts/prompt_10.md)
- **Ora 11–14 — problem/proof:** [11 meeting pain](content_prompts/prompt_11.md) · [12 follow-up outcome](content_prompts/prompt_12.md) · [13 speaker insight](content_prompts/prompt_13.md) · [14 operator lesson](content_prompts/prompt_14.md)
- **Ora 15–20 — waitlist/demo:** [15 FAQ](content_prompts/prompt_15.md) · [16 waitlist](content_prompts/prompt_16.md) · [17 Zara hook](content_prompts/prompt_17.md) · [18 faceless demo](content_prompts/prompt_18.md) · [19 vertical-video caption](content_prompts/prompt_19.md) · [20 waitlist close](content_prompts/prompt_20.md)
- **Family Book 21–25 — product/parent:** [21 child as hero](content_prompts/prompt_21.md) · [22 sample-page proof](content_prompts/prompt_22.md) · [23 parent emotion](content_prompts/prompt_23.md) · [24 grandparent gift](content_prompts/prompt_24.md) · [25 personalization POV](content_prompts/prompt_25.md)
- **Family Book 26–30 — conversion/holiday:** [26 main product](content_prompts/prompt_26.md) · [27 add-on](content_prompts/prompt_27.md) · [28 code `FIRSTBOOK50`](content_prompts/prompt_28.md) · [29 holiday gift](content_prompts/prompt_29.md) · [30 year-end reminder](content_prompts/prompt_30.md)

---

## 5. Platform playbooks

Use the relevant playbook before preparing a platform-specific post. These linked files own the platform limits, creative specs, cadence ceilings, throttling, and live wiring; they are intentionally maintained separately from this calendar.

[Bluesky](docs/platform_playbooks/bluesky.md) · [Threads](docs/platform_playbooks/threads.md) · [Pinterest](docs/platform_playbooks/pinterest.md) · [TikTok](docs/platform_playbooks/tiktok.md) · [Instagram](docs/platform_playbooks/instagram.md) · [LinkedIn](docs/platform_playbooks/linkedin.md) · [X](docs/platform_playbooks/x.md) · [YouTube](docs/platform_playbooks/youtube.md)
