# Weekend Blockers

Everything listed here is blocked by an external dependency, a missing secret, or a manual step that only Don can do.
Resolve these in order of priority. Check off as done.

> **Corrections applied 2026-08-08 — read before working this list.**
>
> - **Ignore every "add to n8n Variables" instruction.** This instance is n8n **Community
>   edition**; `$vars` does not exist. Add the value as a **Railway environment variable**
>   on the n8n service instead, and reference it as `$env.NAME`. See
>   `docs/n8n-env-var-checklist.md` (repo version) for the authoritative list.
> - **Skip steps 11 and 12 as written.** They tell you to import
>   `n8n_workflows/workflow_*_v1.json` and deactivate `Auto-Post (Multi-Brand)`. Those v1
>   files are superseded and unusable here — see `n8n_workflows/archive/README.md`.
>   v2/v3 are already imported and inactive on the live instance.
> - **Pinterest (item 4) is understated.** Scopes are one problem; the live call also
>   returned **401** with no token-refresh path. See `docs/PINTEREST_401_BLOCKER.md`.
> - **Items 1–9 are otherwise valid** and are the real unblock path.

---

## 🔴 BLOCKING: Cannot Post Without These

### 1. GitHub PAT for n8n
**Blocks:** Both workflows (all GitHub API calls)
**Fix:**
1. Go to github.com → Settings → Developer settings → Fine-grained personal access tokens
2. New token → Name: "n8n-ora-auto" → Expiration: 90 days
3. Resource owner: `dkgrissom-tech` → Repository access: `Ora-auto` only
4. Permissions: Contents (Read and write)
5. Generate → Copy token
6. n8n → Credentials → + New → Header Auth → Name: "GitHub PAT Header" → Header Name: `Authorization` → Header Value: `token <paste-token>`

---

### 2. Threads User ID + Meta Long Token
**Blocks:** Threads posts (Short-Form Pipeline)
**Fix:**
1. Go to developers.facebook.com → Graph API Explorer
2. In the top dropdown, select your Threads app
3. Add permissions: `threads_basic`, `threads_content_publish`
4. Click "Generate Access Token" → this is your short-lived token
5. Exchange for long-lived (60-day): `GET https://graph.threads.net/access_token?grant_type=th_exchange_token&client_id={app_id}&client_secret={app_secret}&access_token={short_token}`
6. Get your user ID: `GET https://graph.threads.net/v1.0/me?access_token={long_token}` → copy the `id` field
7. Add to n8n Variables: `GRISSOM_THREADS_USER_ID` = the id, `GRISSOM_META_LONG_TOKEN` = the token
8. **Set a reminder for 55 days from now** to refresh this token

---

### 3. Bluesky App Password
**Blocks:** Bluesky posts
**Fix:**
1. bsky.social → Settings → App Passwords → Add App Password → Name: "n8n-autopost"
2. n8n → Credentials → + New → Header Auth
   - Name: "Bluesky App Password Header"
   - Header Name: `Authorization`
   - Header Value: `Bearer {your-handle}:{app-password}` (literally concatenated with colon)
3. Add to n8n Variables: `GRISSOM_BLUESKY_HANDLE` = your Bluesky handle

---

## 🟡 BLOCKING (for those platforms only)

### 4. Pinterest API App Resubmission
**Blocks:** Pinterest auto-posting
**Interim fix:** Use Pinterest's native browser scheduler (up to 30 days ahead)
**Long-term fix:**
1. Go to developers.pinterest.com → My Apps
2. Find the existing app → click "Request additional scopes"
3. Request: `boards:read`, `pins:read`, `pins:write`
4. Fill out the use case form — be specific: "Schedule pins for my own business accounts across brands I own"
5. Timeline: Usually 3–10 business days for approval
6. After approval: Add `GRISSOM_PINTEREST_ACCESS_TOKEN` and `GRISSOM_PINTEREST_BOARD_ID` to n8n
7. Then swap the Pinterest NoOp node in Workflow 1 with the HTTP Request node (see `docs/n8n-workflow-map.md`)

---

### 5. TikTok Content Posting API Approval
**Blocks:** Automated TikTok video posts (Workflow 2)
**Current status:** Sandbox (test only, doesn't post publicly)
**Fix:**
1. developers.tiktok.com → My Apps → select app → Content Posting API → Apply for Production
2. Fill use case: "Posting original short-form videos to my own TikTok accounts for my content brands"
3. Timeline: 2–8 weeks
4. Until approved: Manual TikTok posts from phone. Use n8n workflow to generate the video and caption, then Don posts manually.
5. After approval: Add `TIKTOK_ACCESS_TOKEN` to n8n Variables, set `TIKTOK_CLIENT_KEY` and `TIKTOK_CLIENT_SECRET`

---

### 6. YouTube OAuth Token
**Blocks:** Automated YouTube uploads (Workflow 2)
**Fix:**
1. console.cloud.google.com → New Project → Enable YouTube Data API v3
2. Credentials → + Create Credentials → OAuth 2.0 Client ID
3. Application type: Web application → Authorized redirect URIs: `https://n8n-production-b205b.up.railway.app/rest/oauth2-credential/callback`
4. In n8n → Credentials → + New → Google OAuth2 API → paste client ID + secret → connect your YouTube account
5. Token scope needed: `https://www.googleapis.com/auth/youtube.upload`
6. Add `YOUTUBE_OAUTH_TOKEN` to n8n Variables (n8n manages refresh automatically via credential)

---

### 7. X/Twitter API Tier
**Blocks:** High-volume X posts (>500/month)
**Current status:** Free tier = 500 tweet writes/month
**Fix (if needed):** Upgrade to Basic ($100/mo) at developer.twitter.com for 10,000 writes/month
**Workaround:** Limit X posts to 3–4/day across all brands. Track monthly usage.

---

## 🟠 DEPLOY STEPS (Don must do these in Replit)

### 8. Deploy YT Studio to Replit Autoscale
**Needed for:** n8n Workflow 2 video generation
**Steps:**
1. Open YT Studio Replit workspace
2. Copy the files from `server/yt_studio/` in this repo into the Replit project
3. In Replit: Shell → `pip install fastapi uvicorn anthropic elevenlabs httpx pillow python-multipart`
4. In Replit Secrets: Add `ANTHROPIC_API_KEY`, `ELEVENLABS_API_KEY`, `YT_STUDIO_API_KEY` (generate a UUID)
5. Deploy → Autoscale → Subdomain: `yt-studio-grissom` → Deploy
6. Test: Browser → `https://yt-studio-grissom.replit.app/health` → should return `{"status": "ok"}`
7. Add to n8n Variables: `YT_STUDIO_API_URL` = `https://yt-studio-grissom.replit.app`, `YT_STUDIO_API_KEY` = same UUID

### 9. Deploy Content Ideas Generator to Replit Autoscale
**Needed for:** n8n Workflow 2 scene-based video
**Steps:**
1. Open Content Ideas Generator Replit workspace
2. Add `server/content_ideas_generator/api/generate.py` and `status.py` to the Replit project
3. In Replit Secrets: Add `CIG_API_KEY` (generate a different UUID), `ELEVENLABS_API_KEY`, `API_BASE_URL`
4. Add FastAPI router imports to main app file
5. Install ffmpeg in Replit: Shell → `nix-env -iA nixpkgs.ffmpeg`
6. Deploy → Autoscale → Subdomain: `content-ideas-grissom`
7. Add to n8n Variables: `CIG_API_URL` = `https://content-ideas-grissom.replit.app`, `CIG_API_KEY` = your UUID

---

## 🔵 AFTER EVERYTHING ABOVE IS DONE

### 10. Point Cloudflare CNAMEs
- `studio.grissompress.com` → `yt-studio-grissom.replit.app`
- `videos.grissompress.com` → `content-ideas-grissom.replit.app`
- `grissompress.com` (root) → point to Shopify or Perplexity page

### 11. Import n8n Workflows
1. n8n → Workflows → Import from file
2. Import `n8n_workflows/workflow_short_form_pipeline_v1.json`
3. Import `n8n_workflows/workflow_video_pipeline_v1.json`
4. For each: open workflow → go through each node flagged with credential placeholders → select the correct credential
5. Rename old `Auto-Post (Multi-Brand)` workflow to `_LEGACY_do_not_use` → deactivate (do NOT delete)
6. Set both new workflows to **Active**

### 12. End-to-End Test (confirm before leaving Sunday)
1. Create a test draft: `content_drafts/test/test-post.md` with `scheduled:` set to 5 minutes from now
2. Wait for the :05 UTC trigger OR hit the manual webhook URL
3. Watch n8n execution log for the run
4. Confirm: post appears on at least 1 platform, file gets renamed to `.posted-<timestamp>.md`
5. If failure: check `posting_log/` in repo for error details

---

## 📝 Notes on Items NOT Built This Weekend

- **LinkedIn image posts**: API requires asset upload endpoint + media registration. Added to the workflow as text-only for now. Will extend when needed.
- **Instagram Reels via API with locally-rendered video**: The Media Graph API for Reels requires the video to be hosted at a publicly accessible URL before posting. YT Studio Autoscale serves this URL — this will work once step 8 is done.
- **n8n polling loop for video render**: n8n doesn't support true loops natively. The workflow polls once and stops if the video isn't done. For production: either (a) use n8n's Loop Over Items pattern with a time-limited retry, or (b) have the video API send a webhook to n8n when done. See `docs/video_api_contracts.md` for details.
