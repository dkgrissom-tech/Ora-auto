# Gate 1 — Create Ora IAP Products in App Store Connect

**Time estimate:** 30-45 minutes (App Store Connect UI is slow)
**Device:** Desktop (Mac + Safari or Chrome)
**Prereqs:** Apple Developer account access to Ora's app record, paid Developer Program active

---

## What we're creating

Three in-app purchase products. **IDs pulled from ORA_BRAIN.md in the Dons-notes repo (verified Aug 15, 2026):**

| Product | Price | Type | Product ID (use EXACT) |
|---|---|---|---|
| Pro Monthly | $12.99 | Auto-renewable subscription | `com.donsnotes.app.pro.monthly` |
| Ora Pro Monthly | $19.99 | Auto-renewable subscription | `com.donsnotes.app.orapro.monthly` |
| Lifetime Access | $149.00 | Non-consumable | `com.donsnotes.app.lifetime` |

**Bundle prefix is `com.donsnotes.app`, NOT `com.dongrissom.ora`.** The app's bundle identifier ties to Dons-notes (the codename), not the Ora brand name. Product IDs must match exactly or Ora's paywall won't recognize purchases.

**Naming note:** The middle tier is called "Ora Pro Monthly" at $19.99 (not "Lumen Pro" — that was my earlier confusion). "Pro Monthly" $12.99 is the entry tier.

---

## Numbered steps (do NOT skip)

**Step 1 — Log in**
- Open `https://appstoreconnect.apple.com`
- Sign in with your Apple Developer account
- Click **My Apps** → select **Ora**

**Step 2 — Navigate to In-App Purchases**
- Left sidebar → **Monetization** → **In-App Purchases**
- If empty, you'll see "Create your first in-app purchase"

**Step 3 — Create Subscription Group first (required for the two subs)**
- Left sidebar → **Subscriptions** → **Subscription Groups**
- Click **+** next to "Subscription Groups"
- Name: `Ora Premium`
- Save

**Step 4 — Create Pro Monthly ($12.99)**
- Inside `Ora Premium` group → click **+** to create subscription
- Reference Name: `Pro Monthly`
- Product ID: `com.donsnotes.app.pro.monthly` (copy-paste, no typos)
- Subscription Duration: **1 Month**
- Price: **$12.99 USD** (Tier 13)
- Localizations → English (U.S.):
  - Display Name: `Ora Pro`
  - Description: `Unlimited meetings, cross-meeting search, and pre-meeting briefs.`
- **Review Screenshot:** Required. Upload any current Ora screenshot (App Store Connect just needs one image — you can replace later)
- Save

**Step 5 — Create Ora Pro Monthly ($19.99)**
- Same subscription group → **+** to add another
- Reference Name: `Ora Pro Monthly`
- Product ID: `com.donsnotes.app.orapro.monthly`
- Duration: **1 Month**
- Price: **$19.99 USD** (Tier 20)
- Display Name: `Ora Pro Plus`
- Description: `Everything in Pro plus Speaker ID, action-item ownership, and priority support.`
- Upload review screenshot
- Save

**Step 6 — Create Lifetime Access**
- Back to **In-App Purchases** (NOT Subscriptions this time)
- Click **+** → select **Non-Consumable**
- Reference Name: `Lifetime Access`
- Product ID: `com.donsnotes.app.lifetime`
- Price: **$149.00 USD** (Tier 149)
- Display Name: `Ora Lifetime`
- Description: `One-time purchase. Lifetime access to all Ora Pro features.`
- Upload review screenshot
- Save

**Step 7 — Submit for review (or leave in "Ready to Submit")**
- Each product should show status "Ready to Submit" or "Waiting for Review"
- If you're launching soon: submit them WITH the next app binary (Build 111+)
- If you want to test in TestFlight first: leave them at "Ready to Submit" — TestFlight users can already purchase in sandbox mode

---

## Verification — before you close the tab

- [ ] All 3 products show correct Product IDs (screenshot the list)
- [ ] Prices show $12.99 / $19.99 / $149.00
- [ ] Subscription Group `Ora Premium` contains both subs
- [ ] Lifetime is under In-App Purchases, NOT Subscriptions

**Screenshot the final list** and drop it in Ora-auto repo under `/docs/app-store/iap-created-YYYYMMDD.png` so we have proof-of-work.

---

## Failure modes to avoid

- **Wrong Product ID** = app doesn't recognize purchase = refunds/support tickets. Copy-paste, don't retype.
- **Skipping subscription group** = subs won't render correctly in Ora's paywall
- **Uploading wrong image** = review rejection later. Any current Ora screen works, doesn't have to be the paywall
- **Setting price manually** = App Store Connect actually uses tier numbers. Tier 13 = $12.99, Tier 20 = $19.99, Tier 149 = $149. If tier prices have drifted, pick the tier that matches USD closest.

---

## When done, tell me:

Paste back: "Gate 1 done — [screenshot URL or 'saved locally']"

Then move to Gate 2.
