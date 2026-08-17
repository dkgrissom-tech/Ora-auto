#!/usr/bin/env bash
set -euo pipefail

echo "Ora landing preflight..."

# 1. No stale launch date
if grep -riE "June 22, 2026|Paid launch · Tuesday" public/; then
  echo "❌ Stale launch date found. Remove it."
  exit 1
fi

# 2. No broken #appstore CTAs
if grep -rE 'href="#appstore"' public/; then
  echo "❌ Broken #appstore anchor found."
  exit 1
fi

# 3. No forbidden marketing terms
# Note: CIPA/BIPA/wiretap use \b word boundaries — without them this regex
# false-positives on the legitimate word "participant" (contains "cipa"),
# which appears throughout the Disclosure page's legal text.
if grep -rniE "lawsuit-proof|sue-proof|no lawsuit|\bCIPA\b|\bBIPA\b|\bwiretap\b" public/; then
  echo "❌ Forbidden marketing term. See ora-marketing-strategy.md 'never say' list."
  exit 1
fi

# 4. No Web3Forms
if grep -riE "web3forms" public/; then
  echo "❌ Web3Forms still referenced. Should route to /subscribe."
  exit 1
fi

# 5. Tracker present
if ! grep -q "track.js" public/index.html; then
  echo "❌ Tracker script missing from index.html."
  exit 1
fi

# 6. Disclosure link in footer
if ! grep -q 'href="/disclosure"' public/index.html; then
  echo "❌ Disclosure link missing from footer."
  exit 1
fi

# 7. Alt text on all images (basic check)
missing_alt=$(grep -oE '<img [^>]*>' public/index.html | grep -v 'alt=' || true)
if [ -n "$missing_alt" ]; then
  echo "❌ Image without alt text: $missing_alt"
  exit 1
fi

echo "✅ Preflight passed."
