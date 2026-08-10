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
| GP-03 | `brands/grissom/assets/gp-03-coloring-landing-hero-4x5.jpg` | 1080x1350 | none (rebuilt — see below) | grissompress.pplx.app/free-printable hero |

GP-05 arrived at 940x788 (neither 4:5 nor 1080-wide). Rebuilt to 1080x1350 by
extending the flat cream field symmetrically (sampled `#FCF6E6`) and scaling
1.15x. No content was cropped.

## Publisher reality check

Verified against `scripts/run_scheduler.py` at time of writing:

- **Bluesky image support — WIRED 2026-08-10.** See the dedicated section below.
- **Tumblr is not a supported platform.** There is no `post_tumblr` and no
  dispatch branch, so `tumblr` falls through to
  `return "skip", f"unknown platform '{platform}'"`. HH-03's scheduled Aug 12
  17:00 UTC post cannot publish until a Tumblr poster is written.
- **HH-05 and GP-03 are landing-page heroes, not queue posts.** The sites
  (`cedarhollow.pplx.app`, `grissompress.pplx.app`) are not in this repo, so
  these two files are staged here for reference only. They must be wired into
  whatever deploys those pages.
- **GP-05 is a manual Facebook group post** and needs no publisher support.

Net: HH-02 and GP-05 now have working delivery paths. HH-03 still cannot publish
(no Tumblr support), and HH-05/GP-03 await landing-page wiring.

## Bluesky image support (added 2026-08-10)

`post_bluesky` previously took only `(brand, text)` and called `send_post`, so
every image on a Bluesky-bound post was silently discarded. It now takes
`(brand, text, image_path=None, alt_text=None)` and calls
`client.send_image(text=..., image=<bytes>, image_alt=...)` when an image
resolves.

Bluesky is the only platform here that uploads bytes as a blob; every other
poster passes an `asset_url()`. So `load_asset_bytes(brand, path)` was added. It
reads from the local checkout first — Actions already has the file, which avoids
both a network round trip and raw.githubusercontent's propagation delay on
freshly committed assets — and falls back to HTTP for assets present upstream
but absent locally.

Guards, all of which degrade to a text-only post rather than losing the post:

- **Missing asset** — logs `image <path> unavailable - posting text only`.
- **Oversized asset** — the PDS rejects blobs over ~976KB, so
  `BLUESKY_BLOB_LIMIT = 976_560` is checked before upload and the actual byte
  count is named in the log. 29 of 123 assets under `brands/*/assets/` exceed it
  (the large source PNGs); all 7 queue blocks referencing one are in the past,
  so nothing scheduled is affected. There is no Pillow in `auto_post.yml`'s pip
  install, so the scheduler cannot recompress — oversized assets must be
  re-exported offline (`tools/make_pins.py` already has PIL).
- **Missing alt text** — a new `alt:` queue field feeds `image_alt`. When absent,
  the value is derived from the body and the log says so, because Bluesky
  surfaces alt text prominently.

Image resolution happens *before* the `DRY_RUN` gate, so a dry run surfaces a bad
asset instead of hiding it until the first live post.

`parse_today` now reads `alt:` alongside `image:`. Covered by
`tests/test_bluesky_image.py` — 5 cases: real asset, missing asset, oversized,
text-only, derived alt.

### Consequence: Pinterest reroutes now carry images too

`PINTEREST_FALLBACK = ["buffer_instagram", "bluesky"]`, so every Pinterest post
already fans out to Bluesky while Pinterest is offline. Those blocks carry an
`image:` field that Bluesky previously ignored. They now attach it.

For 2026-08-11 that means **6 Bluesky deliveries, all carrying images**: the one
native Bluesky post plus 5 rerouted pins, two of which land in the same 23:00 UTC
tick. Across all queue files, 139 blocks reach Bluesky. There is no Bluesky daily
cap in the scheduler. If that volume is too high, the lever is a cap counted from
`logs/posted.json` — the same fix the Instagram cap needs, since `_ig_sent_today`
is module-level and resets every process.

### HH-02 placement

The source doc scheduled HH-02 for Aug 11 15:00 UTC, but **no 15:00 block was
ever written into `brands/grissom/posts/2026-08-11.md`** — that schedule existed
only in the doc. The single existing Bluesky slot is 23:00 UTC, whose body is the
porch-light passage about Don. HH-02 was attached there with alt text, since the
imagery matches. That block carries no destination link, so it does not drive
`/porch-before` the way the doc intended; adding a dedicated linked block is a
content decision rather than a wiring one.

## GP-03 — rebuilt 2026-08-10

The defective text layer has been removed and the asset is now live at
`brands/grissom/assets/gp-03-coloring-landing-hero-4x5.jpg`. Method: walk down
from the vertical midpoint to find the first row whose horizontal deviation
collapses below 1.5 — the boundary between the photograph and the flat cream
field, found at y=902 — sample the cream twelve pixels below that line
(`#FFFCF2`), then repaint from y=906 to the bottom edge. A post-condition
asserts the darkest surviving value below the paint line is above 200, so any
text residue fails the build rather than shipping.

The flat-lay photograph is untouched and the lower 444px (33% of height) is now
a clean cream field, which matches the original spec: a clean image with the
landing page supplying its own copy. Script:
`/home/user/workspace/drive_ads/rebuild_gp03.py`.

### What was wrong with the delivered version

The overlay read:

> Free debut of 3 hex kits of enchantress!
> Free Cozy Goth Coloring Book
> Download your Grissom printable now.

The first line is incoherent, and "hex kits of enchantress" matches no product.
Actual product names are Dark & Dreamy Gothic (`/l/pfaepq`), Spooky Sweet Shop
(`/l/usdqt`), and Cozy Goth Mega Bundle (`/l/wucxhi`). The third line uses
"Grissom" as an adjective. The source doc also described GP-03 as "clean image,
no overlay — text handled by HTML page", which contradicts the delivered file.

The underlying flat-lay illustration was good and was kept. Only the text layer
was discarded.

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
