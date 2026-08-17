# Ora Landing Page

Conversion-focused landing page for Ora — the iPhone meeting recorder. Static
HTML/CSS/vanilla JS, no framework, deployed to Cloudflare Pages.

## Project structure

```
ora-landing/
├── public/                  # everything Cloudflare Pages serves
│   ├── index.html
│   ├── disclosure.html
│   ├── thanks.html
│   ├── assets/
│   │   ├── css/site.css
│   │   ├── js/track.js      # page_view / cta_click / email_capture -> TRACKER_ENDPOINT
│   │   ├── js/site.js       # email capture form handling
│   │   └── img/
│   ├── downloads/           # iphone-meeting-playbook.pdf goes here (uploaded separately)
│   ├── robots.txt
│   └── sitemap.xml
├── functions/
│   └── subscribe.js         # Cloudflare Pages Function -> MailerLite
├── .env.example
└── build.sh                 # preflight guardrail script
```

## Local development

No build step. Serve the `public/` directory directly:

```bash
npx serve public/
```

Then open `http://localhost:3000`.

The `/subscribe` endpoint (Cloudflare Pages Function) only runs under the
Cloudflare Pages dev server, not plain `npx serve`. To test the full form
flow including the MailerLite handoff, use:

```bash
npx wrangler pages dev public/ --compatibility-date=2026-08-17
```

with a local `.dev.vars` file (copy `.env.example`, fill in real values,
never commit it).

## Environment variables

Set these in the Cloudflare Pages project settings — do not commit real
values. See `.env.example` for the full list:

- `MAILERLITE_API_KEY`
- `MAILERLITE_GROUP_ID_WAITLIST`
- `TRACKER_ENDPOINT`
- `PLAYBOOK_URL`
- `SITE_ORIGIN`

## Preflight / guardrail

Run before every deploy:

```bash
bash build.sh
```

Fails the build on: stale launch dates, broken `#appstore` anchors,
forbidden marketing terms (lawsuit-proof, sue-proof, CIPA, BIPA, wiretap),
lingering Web3Forms references, a missing tracker script, a missing
`/disclosure` footer link, or an `<img>` without `alt` text.

## Known deviations from the build brief (flagged for Don)

1. **`track.js` is not copied from PR #10.** PR #10 in `dkgrissom-tech/Ora-auto`
   is an unrelated Instagram-posting bugfix, and none of the referenced
   context docs (`ora-auto-pr10-claude-direction.md`,
   `ora-marketing-strategy.md`, `ora-disclosure-and-terms.md`,
   `ora-mailerlite-welcome-sequence.md`, `ora-week1-tiktok-scripts.md`)
   exist anywhere in this repo. `track.js` is a fresh, minimal implementation
   of the behavior Step 7 of the brief describes — swap it for the real
   PR #10 tracker if it differs.
2. **Zara imagery**: `zara-hero.jpg` and `zara-quote.jpg` are cropped from
   the "Zara Canonical Reference - Look A" portrait Don supplied. That
   source is a professional office headshot (blazer, glasses, office
   background) — not literally "at a coffee shop, iPhone flat on the
   table" as the original brief's alt text described, so the alt text was
   rewritten to describe what's actually in the photo
   (`"Zara, smiling, wearing glasses and a blazer"` /
   `"Zara, close-up portrait, smiling"`). The hero/final-CTA copy still
   tells the coffee-shop story; if Don wants the photo to match that scene
   literally, a coffee-shop generation should replace this one — otherwise
   this canonical portrait is a fine "meet the person" identity shot as-is.
   **App screenshots** (`ora-app-screen-1/2/3.png`) are still not supplied,
   so the "How it works" steps use the `.how-image-placeholder` pattern —
   drop the real files into `public/assets/img/` and swap the placeholder
   `<div>`s for `<img>` tags when ready; dimensions already match so layout
   won't shift.
3. **`favicon.png` and `og-card.png`** are solid-color placeholders
   (generated, not designed) so the page doesn't 404 on those assets.
   Replace with real brand assets when available.
4. **`iphone-meeting-playbook.pdf`** is not in `public/downloads/` — Don
   uploads this separately per the brief.
