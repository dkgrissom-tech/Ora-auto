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
2. **Zara imagery and app screenshots are not yet supplied**, so the hero
   and "Meet Zara" sections render the dark-navy placeholder pattern from
   Step 2, and the "How it works" steps use the `.how-image-placeholder`
   pattern already defined in the CSS for step 4. Drop the real files into
   `public/assets/img/` (`zara-hero.jpg`, `zara-quote.jpg`,
   `ora-app-screen-1.png`, `ora-app-screen-2.png`, `ora-app-screen-3.png`)
   and swap the placeholder `<div>`s for `<img>` tags — dimensions already
   match so layout won't shift.
3. **`favicon.png` and `og-card.png`** are solid-color placeholders
   (generated, not designed) so the page doesn't 404 on those assets.
   Replace with real brand assets when available.
4. **`iphone-meeting-playbook.pdf`** is not in `public/downloads/` — Don
   uploads this separately per the brief.
