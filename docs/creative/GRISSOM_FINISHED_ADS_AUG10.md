# Grissom Press — Finished Ad Assets (Aug 10 2026)

Brief A (publishing funnels) creative, built in Canva by Claude, retrieved and
placed in this repo on 2026-08-10.

## Why this file exists

The source doc ("Grissom Press — Finished Ads Aug 10 2026", Google Drive)
recorded each design as a `canva.com/d/<id>` link. Those are **editor** links
that resolve to `/api/design/<token>/edit` and require the creating account's
session — they return HTTP 403 to anyone else, even with the design set to
"Anyone with the link can view". They are not durable references. The flat
files below are the durable form.

## Placed assets

All served via `asset_url()` →
`https://raw.githubusercontent.com/dkgrissom-tech/Ora-auto/main/<path>`

| Unit | File | Size | Overlay copy | Destination |
|---|---|---|---|---|
| HH-02 | `brands/grissom/assets/hh-02-bluesky-4x5.jpg` | 1080x1350 | "She did not ask for a new beginning. She asked for a porch repair." | cedarhollow.pplx.app/porch-before |
| HH-03 | `brands/grissom/assets/hh-03-tumblr-4x5.jpg` | 1080x1350 | "Some love stories start with a grand gesture. This one starts with a porch repair." | cedarhollow.pplx.app/porch-before |
| HH-05 | `brands/grissom/assets/hh-05-landing-hero-4x5.jpg` | 1080x1350 | none (page HTML supplies text) | cedarhollow.pplx.app/porch-before hero |
| GP-05 | `brands/grissom/assets/gp-05-facebook-group-4x5.jpg` | 1080x1350 | "Color something strange and sweet" | grissompress.pplx.app/free-printable |
| GP-03 | `brands/grissom/assets/_hold/gp-03-coloring-landing-hero-4x5.jpg` | 1080x1350 | **defective — see below** | grissompress.pplx.app/free-printable hero |

GP-05 arrived at 940x788 (neither 4:5 nor 1080-wide). Rebuilt to 1080x1350 by
extending the flat cream field symmetrically (sampled `#FCF6E6`) and scaling
1.15x. No content was cropped.

## Publisher reality check

Verified against `scripts/run_scheduler.py` at time of writing:

- **Bluesky cannot carry an image.** `post_bluesky(brand, text)` takes no image
  argument and calls `client.send_post(text=text[:300])`. HH-02's overlay art
  will not attach; the scheduled Aug 11 15:00 UTC post publishes as text only.
  Adding image support means embedding a blob via the atproto client.
- **Tumblr is not a supported platform.** There is no `post_tumblr` and no
  dispatch branch, so `tumblr` falls through to
  `return "skip", f"unknown platform '{platform}'"`. HH-03's scheduled Aug 12
  17:00 UTC post cannot publish until a Tumblr poster is written.
- **HH-05 and GP-03 are landing-page heroes, not queue posts.** The sites
  (`cedarhollow.pplx.app`, `grissompress.pplx.app`) are not in this repo, so
  these two files are staged here for reference only. They must be wired into
  whatever deploys those pages.
- **GP-05 is a manual Facebook group post** and needs no publisher support.

Net: of the five finished designs, only GP-05 has a working delivery path today.

## GP-03 defect — do not ship

The overlay reads:

> Free debut of 3 hex kits of enchantress!
> Free Cozy Goth Coloring Book
> Download your Grissom printable now.

The first line is incoherent, and "hex kits of enchantress" matches no product.
Actual product names are Dark & Dreamy Gothic (`/l/pfaepq`), Spooky Sweet Shop
(`/l/usdqt`), and Cozy Goth Mega Bundle (`/l/wucxhi`). The third line uses
"Grissom" as an adjective. The source doc also described GP-03 as "clean image,
no overlay — text handled by HTML page", which contradicts the delivered file.

The underlying flat-lay illustration is good and worth keeping. Only the text
layer needs rebuilding, or removing entirely so the landing page supplies copy
as the doc originally specified.

## Other deviations worth noting

- **HH-02 / HH-03 use a sans-serif italic** for overlay type. `docs/pin_style_guide.md`
  specifies Playfair or Cormorant for emotional units and reserves
  Inter/Montserrat for utility. GP-03 and GP-05 correctly use a serif, so the
  set is internally inconsistent.
- **HH-03's setting is off-brand.** It shows a sprawling live oak over a
  manicured lawn, which reads Deep South. Cedar Hollow is Muskogee County,
  eastern Oklahoma — cross-timbers oak and hickory, red clay, low rolling hills.
  HH-05 gets this right (dormant winter pasture, bare hardwood treeline).
- **HH-02 shows Dana's wedding ring**, which is canon-correct: she still wears
  it roughly fourteen months out.
- No identifiable faces in any of the five. House rule holds.

## Still outstanding from Brief A

The source doc lists these as intentionally unbuilt, and no Canva links were
provided for them:

- Pinterest units HH-01, GP-01, GP-02, GP-09 — held while Pinterest is offline
  and silently rerouting to Instagram at the wrong aspect ratio
- TikTok/Reels units HH-04, GP-07 — no grissom publishing token
- Newsletter swap image SW-04 — held until a swap partner confirms
- BookBub/Goodreads header HH-10 — held until profile ownership is verified
