# Gate 3 — Ora Social Secrets (mobile-friendly)

**Time:** 30-45 min | **Device:** phone OK (GitHub mobile web works) | **Repo:** `dkgrissom-tech/Ora-auto`

---

## Ground truth (verified Aug 15, 2026)

- **Zero `ORA_*` secrets currently set** in the repo. Every Ora post has been publishing to nothing since July 25.
- The workflow file `.github/workflows/auto_post.yml` expects these EXACT secret names — case matters, underscores matter.
- **Ora does NOT post to X/Twitter in the current workflow.** Skip X — it's not wired in code. My earlier draft was wrong.

## This weekend's minimum: LinkedIn only

Do LinkedIn first. It's the B2B channel that matches Ora's ICP (consultants + boutique agencies). Everything else can wait.

**Ora LinkedIn secrets needed:**

| Secret name (paste EXACTLY) | What it is | Where to get it |
|---|---|---|
| `ORA_LINKEDIN_ACCESS_TOKEN` | OAuth 2.0 access token for Ora's LinkedIn page | LinkedIn Developer Portal → Ora app → Auth |
| `ORA_LINKEDIN_AUTHOR_URN` | URN of the posting entity (Ora Company Page or your profile) | LinkedIn API `/me` endpoint OR Buffer settings |

---

## Numbered steps

### Step 1 — Confirm Ora's LinkedIn presence exists

1. Open LinkedIn mobile app
2. Search for "Ora" or "Dons Notes" — is there a Company Page?
3. If YES → note the page name, skip to Step 2
4. If NO → create it:
   - Tap your profile pic → **Work** → **Create a Company Page**
   - Type: **Small business**
   - Name: `Ora` (or whatever the app is branded as publicly)
   - Website: your Ora landing page URL
   - Industry: `Software Development`
   - Save

### Step 2 — Get the LinkedIn access token

**Easiest path (Buffer already handles OAuth):**

1. Open Buffer app or [buffer.com](https://buffer.com) on your phone
2. **Settings → Channels → Add Channel → LinkedIn**
3. Connect Ora's Company Page (not personal profile)
4. Buffer will show a "connected" status
5. Buffer generates a long-lived token behind the scenes — but you can't extract it directly from Buffer's UI

**If you want a direct token (bypasses Buffer):**

1. Go to [linkedin.com/developers/apps](https://www.linkedin.com/developers/apps) on desktop-view (this WILL work with Request Desktop Website on your phone)
2. **Create app** if none exists → name it `Ora Auto Poster`
3. Under **Products** → request access to **Share on LinkedIn** and **Sign In with LinkedIn using OpenID Connect**
4. Under **Auth**:
   - Add redirect URL: `https://oauth.buffer.com/oauth2/authorize` (or your own if not using Buffer)
   - Copy the **Access Token** from the OAuth 2.0 tools section (there's a "Generate Token" button)
5. Copy that long token string

### Step 3 — Get the author URN

1. In LinkedIn mobile, go to Ora's Company Page
2. Tap the page name at the top → URL will look like `linkedin.com/company/12345678`
3. The number at the end is the Company ID (e.g., `12345678`)
4. Your author URN is: `urn:li:organization:12345678`
5. Save that string — you'll paste it as the secret value

**If posting from personal profile instead:**
- Author URN format: `urn:li:person:YOUR_PROFILE_ID`
- Get your profile ID from [linkedin.com/in/YOU](https://www.linkedin.com) → view source → search for `member:` — or easier, use LinkedIn API `/me` endpoint

### Step 4 — Add secrets to GitHub

1. Open [github.com/dkgrissom-tech/Ora-auto/settings/secrets/actions](https://github.com/dkgrissom-tech/Ora-auto/settings/secrets/actions) on your phone
2. Tap **New repository secret**
3. First secret:
   - Name: `ORA_LINKEDIN_ACCESS_TOKEN` (copy-paste this, don't type — case matters)
   - Value: paste the long token from Step 2
   - **Add secret**
4. Tap **New repository secret** again
5. Second secret:
   - Name: `ORA_LINKEDIN_AUTHOR_URN`
   - Value: paste the `urn:li:organization:XXXX` string from Step 3
   - **Add secret**

### Step 5 — Trigger a test workflow run

1. Open [github.com/dkgrissom-tech/Ora-auto/actions/workflows/auto_post.yml](https://github.com/dkgrissom-tech/Ora-auto/actions/workflows/auto_post.yml)
2. Tap **Run workflow** button (top right — may need to scroll)
3. Leave inputs at defaults, tap **Run workflow** to confirm
4. Wait 60-90 seconds
5. Refresh the page — should show a green checkmark

### Step 6 — Verify LIVE on LinkedIn (do NOT skip)

1. Open Ora's LinkedIn Company Page in LinkedIn mobile
2. Look for the test post — should appear within 2 minutes of the green workflow
3. **If post is live:** delete it (keep feed clean), Gate 3 done
4. **If workflow green but no post:** LinkedIn silently rejected — check step 5's log output for error messages

---

## Verification checklist

- [ ] Both secrets appear in GitHub → Settings → Secrets → Actions (values hidden, that's normal)
- [ ] `ORA_LINKEDIN_ACCESS_TOKEN` name is EXACT (all caps, correct underscores)
- [ ] `ORA_LINKEDIN_AUTHOR_URN` name is EXACT
- [ ] Test workflow run shows green
- [ ] Test post visible on Ora's actual LinkedIn page (not just "workflow succeeded")
- [ ] Test post deleted after verification

---

## What we're intentionally NOT doing this weekend

**Skip these secrets — they're for platforms we don't need yet:**

- `ORA_BLUESKY_*` — Bluesky is low-ROI for B2B, skip
- `ORA_META_LONG_TOKEN` + `ORA_INSTAGRAM_USER_ID` — Instagram is visual, Ora content is text, mismatch
- `ORA_THREADS_USER_ID` — same Meta setup pain, defer
- `ORA_PINTEREST_*` — 5 secrets, wrong audience, defer
- `ORA_TIKTOK_ACCESS_TOKEN` — Ora is B2B, TikTok is B2C, wrong channel

If Gate 3 succeeds with just LinkedIn and you have appetite for more, Instagram + Threads can go in next weekend (they share `ORA_META_LONG_TOKEN`, so it's 3 additional secrets total).

---

## Failure modes to avoid

- **Secret name typos** — `ORA_LINKEDIN_TOKEN` (missing ACCESS) will silently fail. Must be `ORA_LINKEDIN_ACCESS_TOKEN`.
- **Author URN wrong format** — `12345678` alone won't work. Must be `urn:li:organization:12345678` OR `urn:li:person:XXXXX`.
- **Pasting the token into commit messages** — instant token compromise. Only paste into the GitHub secret value field.
- **Trusting the workflow "success" status without checking LinkedIn** — LinkedIn silently drops posts sometimes. Always verify live on the destination.
- **Using personal LinkedIn profile when Ora Company Page is available** — B2B credibility. Use the Company Page URN.

---

## When done, paste back

- "Gate 3 done — LinkedIn test post landed live at [URL]"
- OR "Gate 3 failed at Step X — [what happened]"
- OR the error message from the failing workflow run
