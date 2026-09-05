# Grissom Press Shop

Static landing page + Cloudflare Pages Functions that sell **Pip the Pumpkin** (and future Grissom Press books) via Stripe Payment Links with instant PDF download.

Mirrors the `ora-landing/` structure and reuses its CSS system.

## How it works

1. Buyer clicks **Buy now** on `/` → sent to a **Stripe Payment Link** (created by hand in your Stripe dashboard, no API keys needed for checkout).
2. Stripe processes payment → redirects buyer to `/thanks.html?session_id=cs_...`.
3. `/thanks.html` calls `/verify?session_id=...` — a Pages Function that confirms with Stripe (`payment_status === 'paid'`) using your secret key, then returns a short-lived signed download URL.
4. Buyer clicks the download button → hits `/download?slug=...&sig=...` — a second Pages Function that validates the HMAC signature and streams the PDF from `/_files/`. Direct hotlinking to `/_files/*` is blocked at the edge.

## Project structure

```
shop-landing/
├── public/
│   ├── index.html               # book landing page
│   ├── thanks.html              # post-purchase, calls /verify then shows download button
│   ├── _files/
│   │   └── pip-the-pumpkin.pdf  # PDF (external access blocked by _redirects)
│   ├── _headers                 # security + private cache for /_files
│   ├── _redirects               # blocks external /_files/* access
│   ├── robots.txt
│   ├── sitemap.xml
│   └── assets/
│       ├── css/site.css         # shared with ora-landing
│       ├── css/shop.css         # shop-specific overrides (Halloween palette)
│       └── img/pip-cover.png    # book cover
└── functions/
    ├── verify.js                # /verify — confirms Stripe session, returns signed URL
    └── download.js              # /download — validates HMAC, streams PDF
```

## Setup (one-time)

### 1. Create the Stripe Payment Link
In Stripe dashboard → **Payment Links** → **New**:
- Product name: `Pip the Pumpkin — A Halloween Coloring Book`
- Price: **$4.99 USD** (one-time)
- After payment: **Redirect to your website** → `https://<your-pages-url>/thanks.html?session_id={CHECKOUT_SESSION_ID}`
- Advanced options: **Collect customer email** (on by default)
- Save → copy the resulting URL (looks like `https://buy.stripe.com/xxxx`)

Paste that URL into `public/index.html`, replacing `REPLACE_ME_WITH_STRIPE_PAYMENT_LINK` (there's one occurrence).

### 2. Deploy to Cloudflare Pages
- Cloudflare dashboard → Pages → **Create a project** → connect GitHub → pick `dkgrissom-tech/Ora-auto` → set **root directory** to `shop-landing/public` and **Functions directory** to `shop-landing/functions`. Build command: none. Build output: `.`
- Or if `ora-landing` is already deployed via a similar Pages project, create a **second** project pointing at this folder.

### 3. Set environment variables
In the Pages project → **Settings → Environment variables** (production):

| Variable | Value | Where to get it |
|---|---|---|
| `STRIPE_SECRET_KEY` | `sk_live_...` | Stripe dashboard → Developers → API keys |
| `DOWNLOAD_SIGNING_SECRET` | any long random string (e.g. `openssl rand -hex 32`) | generate once, never share |
| `PRODUCT_SLUG` | `pip-the-pumpkin` | matches PDF filename in `_files/` |

Save and **redeploy** so the Function picks up the vars.

### 4. Test
- Use Stripe **test mode** first: create a test Payment Link with a `sk_test_...` key, use test card `4242 4242 4242 4242`, verify the download works end-to-end.
- Switch to live keys + live Payment Link when you're happy.

## Adding a new book later

1. Drop `<slug>.pdf` into `public/_files/`.
2. Add `<slug>` to the `KNOWN` set in `functions/download.js`.
3. Create a new Stripe Payment Link redirecting to `/thanks-<slug>.html?session_id={CHECKOUT_SESSION_ID}`.
4. Copy `thanks.html` → `thanks-<slug>.html`, update cover + title.
5. Deploy.

(Or refactor into a multi-product router later — one book at a time first.)

## Why this instead of Gumroad

- Zero platform fees (Stripe standard rate only: 2.9% + 30¢)
- Your buyer's email lands directly in Stripe → export anytime
- Same brand experience end-to-end
- Free hosting on Cloudflare Pages
- Reuses your existing Ora landing infrastructure
