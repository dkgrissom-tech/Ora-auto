#!/usr/bin/env bash
# End-to-end smoke test. Assumes:
#   - dev server is running (`pnpm dev`)
#   - worker is running (`pnpm worker:dev`)
#   - you set SUPABASE_TEST_JWT to a valid session JWT for a paid test user
#   - the URL below points to a real Handy Hearts (or any) Amazon listing
set -euo pipefail

: "${SUPABASE_TEST_JWT:?set SUPABASE_TEST_JWT to a signed-in test user JWT}"
URL="${SMOKE_URL:-https://www.amazon.com/dp/B0C5Q9DKPJ}"

echo "→ POST /api/generate for $URL"
RESP=$(curl -sS -X POST http://localhost:3000/api/generate \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $SUPABASE_TEST_JWT" \
  -d "{\"amazonUrl\":\"$URL\"}")
echo "$RESP"

JOB_ID=$(echo "$RESP" | jq -r .id)
echo "→ Polling /api/jobs/$JOB_ID"

for i in $(seq 1 60); do
  STATUS=$(curl -sS http://localhost:3000/api/jobs/$JOB_ID | jq -r .status)
  printf "  [%02d] %s\n" "$i" "$STATUS"
  [[ "$STATUS" == "done" ]] && { echo "✓ done"; exit 0; }
  [[ "$STATUS" == "failed" ]] && { echo "✗ failed"; exit 1; }
  sleep 15
done

echo "✗ timed out after 15 min"
exit 1
