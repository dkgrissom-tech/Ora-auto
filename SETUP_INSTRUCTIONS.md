# Ora Auto-Post Setup — Elementary Steps

Read top to bottom. Each phase has a wait time. Start Phase 1 today.

---

## PHASE 1 — Same-day live (X + LinkedIn)

### Step 1A: Create a GitHub repo for the auto-poster (3 min)

1. Open Safari on your iPhone (or PC browser)
2. Go to **https://github.com/new**
3. Repo name: **ora-auto**
4. Owner: **dkgrissom-tech** (your org)
5. **Public** (must be public for image hosting to work)
6. Check **"Add a README file"**
7. Tap **Create repository**
8. Reply "repo done" — I'll push all the code to it for you

### Step 1B: Get X (Twitter) API keys (10 min)

1. Open Safari
2. Go to **https://developer.x.com/en/portal/petition/essential/basic-info**
3. Sign in with your X account (the @meetora one)
4. Use case: select **"Making a bot"**
5. Country: United States
6. App name: **OraAutoPoster**
7. Tap **Next** through the screens, accepting defaults
8. On the keys page you'll see four values — copy each one and reply with them tagged:
   - `X_API_KEY=…`
   - `X_API_SECRET=…`
   - `X_ACCESS_TOKEN=…`
   - `X_ACCESS_SECRET=…`
9. ⚠️ Make sure to set permissions to **Read and Write** — Settings → User authentication settings → Read and Write → Save
10. After changing permissions, **regenerate the Access Token & Secret** and re-send those two values

### Step 1C: Get LinkedIn keys (8 min)

1. Open **https://www.linkedin.com/developers/apps/new**
2. App name: **OraAutoPoster**
3. LinkedIn Page: select your personal page (or create a Company Page for Ora first if you'd rather)
4. Privacy policy URL: **https://meetora-app.pplx.app/privacy**
5. App logo: upload the Ora icon
6. Tap **Create app**
7. Go to **Auth** tab → copy the **Client ID** and **Client Secret**
8. Reply with them tagged:
   - `LINKEDIN_CLIENT_ID=…`
   - `LINKEDIN_CLIENT_SECRET=…`
9. I'll generate the access token + author URN for you on the next round (needs a one-time OAuth click from you)

### Step 1D: Paste keys into GitHub Secrets (5 min) — DO THIS AFTER 1B+1C

1. Open **https://github.com/dkgrissom-tech/ora-auto/settings/secrets/actions**
2. Tap **New repository secret** for each value below
3. Name + Secret pairs:
   - `X_API_KEY` + the value
   - `X_API_SECRET` + the value
   - `X_ACCESS_TOKEN` + the value
   - `X_ACCESS_SECRET` + the value
   - `LINKEDIN_ACCESS_TOKEN` + the value (I'll give you this after OAuth)
   - `LINKEDIN_AUTHOR_URN` + the value (I'll give you this)
4. Reply "secrets done"

✅ **After Phase 1: X and LinkedIn post automatically. No more manual posts on those two.**

---

## PHASE 2 — 2-4 week wait (Instagram + Threads)

### Step 2A: Convert Instagram to Business (5 min)

1. Open Instagram app on iPhone
2. Profile → top right hamburger menu → **Settings and activity**
3. **Account type and tools** → **Switch to professional account**
4. Category: **Entrepreneur**
5. Select **Business** (NOT Creator — fewer API restrictions)
6. Enter dkgrissom@gmail.com
7. Done

### Step 2B: Create / link Facebook Page (10 min)

1. Open **https://www.facebook.com/pages/create** on your PC (easier than iPhone)
2. Page name: **Ora — AI Meeting Assistant**
3. Category: **App page**
4. Bio: "Just say Ora. She listens, then emails you everything."
5. Create
6. On the new page → Settings → Linked Accounts → Instagram → **Connect Account** → log in with your @meetora IG
7. Reply "FB page done"

### Step 2C: Create Meta Developer App (15 min)

1. Open **https://developers.facebook.com/apps/create**
2. Sign in with the same Facebook account
3. Use case: **Other**
4. App type: **Business**
5. App name: **OraAutoPoster**
6. Contact email: dkgrissom@gmail.com
7. Create
8. From left menu: **Add Product** → Add **Instagram** AND **Threads API**
9. Go to **App Review → Permissions and Features**
10. Request these permissions:
    - `instagram_basic`
    - `instagram_content_publish`
    - `pages_show_list`
    - `pages_read_engagement`
    - `business_management`
    - `threads_basic`
    - `threads_content_publish`
11. For each one, you'll need to record a **screen-recording video** showing the API working with a test post
12. Reply "Meta app created" — I'll write the exact video script and code to test before you submit

### Step 2D: Submit for Meta App Review

After steps 2A-2C are done, you'll record one 2-3 minute screen recording showing the full posting flow, then click Submit. Then we **wait 2-4 weeks** for Meta to approve.

✅ **After Phase 2: IG + Threads also post automatically.**

---

## PHASE 3 — 1-4 week wait (Pinterest)

### Step 3A: Pinterest Business account (3 min)

1. Already have business account from the Grissom Press work — skip if so
2. Otherwise: Pinterest app → Profile → Settings → **Convert to business account**

### Step 3B: Pinterest Developer app (10 min)

1. Open **https://developers.pinterest.com/apps/**
2. **Create app**
3. App name: **OraAutoPoster**
4. App description: "Automated cross-posting for Ora, an iOS meeting assistant"
5. Save
6. Submit for **Trial access** — usually approved next business day
7. Once trial approved, record a 2-min demo video of pin-creation flow → submit for **Standard access**
8. Reply "Pinterest app created" — I'll write the demo video script

### Step 3C: Get the access token (5 min after Standard approval)

I'll walk you through OAuth when the time comes.

✅ **After Phase 3: Pinterest pins post automatically.**

---

## PHASE 4 — 2-6 week wait (TikTok)

### Step 4A: TikTok Developer app (10 min)

1. Open **https://developers.tiktok.com**
2. Sign in with your TikTok @meetora account
3. **Manage apps** → **Create app**
4. App name: **OraAutoPoster**
5. App description: "Automated short-form video posting for Ora, an iOS meeting assistant"
6. Add product: **Content Posting API**
7. Request scopes: `video.publish` + `video.upload`
8. Set redirect URI: `https://meetora-app.pplx.app/oauth/tiktok`
9. Verify URL prefix on the meetora-app.pplx.app domain (I'll add the verification file when you reach this step)
10. Submit for audit
11. Reply "TikTok app created" — I'll write the audit demo video script

✅ **After Phase 4: TikTok posts automatically.**

---

## Throughout: what you'll NEVER have to do manually

After all 4 phases land:

- ❌ Never paste a post to X again
- ❌ Never paste to LinkedIn
- ❌ Never paste to Threads
- ❌ Never upload an IG photo by hand
- ❌ Never schedule a pin in the Pinterest app
- ❌ Never upload a video to TikTok

✅ Reddit you'll **manually** do once or twice during the launch (auto-Reddit = ban)
✅ Product Hunt launch is **1 click on July 10** at 12:01am PT — that's it

---

## What I need from you RIGHT NOW

Just Phase 1, Step 1A:

**Create the empty GitHub repo `dkgrissom-tech/ora-auto` (public, with README), then reply "repo done".**

That unblocks me to push the auto-poster code, draft all 14 days of posts, and start filling in keys as you produce them.
