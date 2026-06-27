# Multi-Brand Auto-Post Setup — Elementary Steps

This poster runs three brands from one repo:

- **Ora** — meeting assistant app — X: @meetora, **TikTok: @toolstack-y4g**
- **Grissom Press** — gothic coloring books (Pinterest-primary, no TikTok)
- **Family Book Creator** — personalized kids books (Pinterest-primary, no TikTok)

**TikTok policy:** Only Ora posts to TikTok via this poster (account @toolstack-y4g). Grissom Press and Family Book Creator intentionally skip TikTok — Pinterest converts better for visual products and avoids cross-niche algorithm penalties.

Each brand needs its own API keys. The work below is the same for each brand — just repeat with that brand's accounts and secrets.

---

## X (Twitter) — MANUAL ONLY

**X charges now** (Free tier requires a credit card on file; Basic tier is $200/month). Per the no-paid-services rule, the auto-poster does NOT touch X.

When you have a big-moment X post to make (Product Hunt launch day, major milestone, viral reply), just post it by hand from your phone like a normal person. The auto-poster handles the daily volume across the other platforms.

---

## DAY 1 — Bluesky for all 3 brands (truly free, same-hour, ~5 min/brand)

Bluesky replaces X as the short-form text channel. No credit card, no review, no API approval — just create the account and generate an app password.

### For each brand:

1. Open **https://bsky.app** on iPhone or PC
2. **Create account** (or sign in if you already have one for the brand)
3. Handle suggestions:
   - Ora: **meetora.bsky.social** (or claim a custom domain later)
   - Grissom Press: **grissompress.bsky.social**
   - Family Book Creator: **familybookcreator.bsky.social**
4. Use email + password — they don't ask for a credit card
5. Once logged in, go to **Settings → App Passwords → Add App Password**
6. Name it: **AutoPoster**
7. Bluesky generates a one-time password like `abcd-efgh-ijkl-mnop` — copy it immediately, you can't view it again
8. Reply tagged like:

For Ora:
```
ORA_BLUESKY_HANDLE=meetora.bsky.social
ORA_BLUESKY_APP_PASSWORD=abcd-efgh-ijkl-mnop
```

For Grissom:
```
GRISSOM_BLUESKY_HANDLE=grissompress.bsky.social
GRISSOM_BLUESKY_APP_PASSWORD=...
```

For Family Book:
```
FAMILYBOOK_BLUESKY_HANDLE=familybookcreator.bsky.social
FAMILYBOOK_BLUESKY_APP_PASSWORD=...
```

9. I'll walk you through pasting them into GitHub Secrets at https://github.com/dkgrissom-tech/Ora-auto/settings/secrets/actions

✅ **After this round: all 3 brands post automatically to Bluesky.**

**Honest time estimate: 5-10 min per brand, no waiting periods.**

---

## DAY 2 — LinkedIn (same-day, ~15 min/brand)

For LinkedIn you have two options:

**Option A (simplest):** All 3 brands post from your personal LinkedIn — Ora content gets cross-pollinated to your professional audience, Grissom Press posts feel out of place. Not recommended.

**Option B (recommended):** Create a **Company Page** for each brand, post from the page. LinkedIn lets you create up to 100 company pages from one personal profile.

### For each brand:

1. Open **https://www.linkedin.com/company/setup/new/**
2. Page name: **Ora** / **Grissom Press** / **Family Book Creator**
3. Industry, size, type — fill in (any reasonable answer is fine for a small business)
4. Click **Create page**
5. Once each page exists, open **https://www.linkedin.com/developers/apps/new**
6. App name: same as X (e.g. **OraAutoPoster**)
7. Associate it with the LinkedIn Company Page for that brand
8. Privacy policy URL: brand's website
9. Tap **Create**
10. Auth tab → copy Client ID + Client Secret. Reply tagged like:
    ```
    ORA_LINKEDIN_CLIENT_ID=...
    ORA_LINKEDIN_CLIENT_SECRET=...
    ```
11. I'll generate the OAuth URL for that brand → you click → approve → I get the access token

✅ **After this: all 3 brands post automatically to LinkedIn.**

---

## DAY 3+ — Meta App Review for IG + Threads (2-4 wk wait per brand)

### IMPORTANT — review submission limits

Meta lets you submit 1 app at a time per developer account. You have two choices:

**Option A (faster, recommended):** Create **3 separate Meta apps** under your one developer account (it allows this) — one per brand. Submit all three for review on the same day. Reviews run in parallel.

**Option B (slower):** Submit one, wait, submit the next.

### For each brand, repeat these steps:

#### Step 1: Convert IG to Business
1. Open IG app
2. Profile → menu top right → **Settings and activity**
3. **Account type and tools** → **Switch to professional account**
4. Category:
   - Ora: **Entrepreneur**
   - Grissom Press: **Artist** or **Author**
   - Family Book Creator: **Author**
5. Select **Business** (NOT Creator)

#### Step 2: Create Facebook Page + link IG
1. Open **https://www.facebook.com/pages/create** on PC
2. Page name: Brand name
3. Category: App page / Author / Artist
4. After created → Settings → Linked Accounts → Instagram → Connect → log in with brand's IG

#### Step 3: Create Meta Developer App
1. Open **https://developers.facebook.com/apps/create**
2. Use case: **Other** → Business app type
3. App name: **OraAutoPoster** / **GrissomAutoPoster** / **FamilyBookAutoPoster**
4. Contact email: dkgrissom@gmail.com
5. Add Products: **Instagram** + **Threads API**

#### Step 4: Request permissions
- `instagram_basic`
- `instagram_content_publish`
- `pages_show_list`
- `pages_read_engagement`
- `business_management`
- `threads_basic`
- `threads_content_publish`

#### Step 5: Record demo video + submit
For each permission Meta wants a 30-90 sec screen recording showing the API working. I'll write the exact tap-by-tap script when you get to this step.

✅ **After 2-4 wk wait: all 3 brands post automatically to IG + Threads.**

---

## DAY 4+ — Pinterest Standard Access (1-4 wk wait per brand)

### For each brand:

1. **https://developers.pinterest.com/apps/** → Create app
2. App name: **OraAutoPoster** etc
3. App description (paste, swap brand):
   > "Automated cross-posting for [Brand]. The app posts marketing pins on behalf of the @[handle] Pinterest business account only. No data reading, no scraping, owner-account writes only."
4. Submit for **Trial access** (approved next business day)
5. Record 2-min demo of pin-creation flow → submit for **Standard access**
6. I'll write the demo script when you reach this step

✅ **After 1-4 wk wait: all 3 brands post automatically to Pinterest.**

---

## DAY 5+ — TikTok Content Posting (Ora only, 2-6 wk wait)

**Only one brand needs this: Ora, on @toolstack-y4g.** Grissom and Family Book intentionally skip TikTok.

1. **https://developers.tiktok.com** → sign in with **@toolstack-y4g**
2. **Manage apps** → **Create app**
3. App name: **OraAutoPoster**
4. Add product: **Content Posting API**
5. Scopes: `video.publish` + `video.upload`
6. Redirect URI: `https://meetora-app.pplx.app/oauth/tiktok` — will set up the verification file when you reach this step
7. Submit for audit

✅ **After 2-6 wk wait: Ora posts automatically to TikTok via @toolstack-y4g.**

---

## What you'll need from each brand BEFORE we start

For each brand, confirm or create:

| Item | Ora | Grissom Press | Family Book |
|---|---|---|---|
| Bluesky handle | needs creation | needs creation | needs creation |
| X handle (manual only) | @meetora | @grissompress (?) | (?) |
| TikTok handle | **@toolstack-y4g** | — (skipped) | — (skipped) |
| Instagram handle | (?) | (?) | (?) |
| Pinterest business account | (?) | ✓ | (?) |
| Facebook page for IG link | needed | needed | needed |
| Landing page URL | meetora-app.pplx.app | grissompress.pplx.app | familybookcreator.app |

**If any of those handles don't exist yet, tell me which ones and I'll write the signup steps for those too.**

---

## What you do RIGHT NOW

Two steps, both fast:

1. **Create the 3 Bluesky accounts** — 5 min each, no credit card. Follow the DAY 1 section above.
2. **Reply with the 3 handles + 3 app passwords** in the tagged format.

That unblocks Bluesky posting for all 3 brands today. Then we move to LinkedIn tomorrow, then Meta/Pinterest reviews start the multi-week wait.
