/**
 * GET /verify?session_id=cs_test_...
 *
 * Called by /thanks.html after Stripe redirects the buyer back.
 * Confirms the Checkout Session with Stripe, then returns a short-lived signed
 * download URL to the PDF. No API needed on Stripe's side — buyer created the
 * session via a Stripe Payment Link.
 *
 * Env vars (set in Cloudflare Pages → Settings → Environment variables):
 *   STRIPE_SECRET_KEY       — sk_live_... (or sk_test_... for testing)
 *   DOWNLOAD_SIGNING_SECRET — any long random string (used to HMAC download URLs)
 *   PRODUCT_SLUG            — "pip-the-pumpkin" (matches PDF filename in /downloads/)
 */

export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const sessionId = url.searchParams.get('session_id');

  if (!sessionId) return json({ error: 'missing session_id' }, 400);
  if (!env.STRIPE_SECRET_KEY) return json({ error: 'server misconfigured' }, 500);
  if (!env.DOWNLOAD_SIGNING_SECRET) return json({ error: 'server misconfigured' }, 500);

  // Fetch Checkout Session from Stripe
  let session;
  try {
    const res = await fetch(
      `https://api.stripe.com/v1/checkout/sessions/${encodeURIComponent(sessionId)}`,
      {
        headers: { 'Authorization': `Bearer ${env.STRIPE_SECRET_KEY}` },
      }
    );
    if (!res.ok) {
      console.error('Stripe session fetch failed', res.status, await res.text());
      return json({ error: 'session not found' }, 404);
    }
    session = await res.json();
  } catch (err) {
    console.error('Stripe fetch error', err);
    return json({ error: 'network error' }, 502);
  }

  // Only unlock the download if payment actually succeeded
  if (session.payment_status !== 'paid') {
    return json({ error: 'not paid', payment_status: session.payment_status }, 402);
  }

  // Sign a short-lived download token (15 min)
  const slug = env.PRODUCT_SLUG || 'pip-the-pumpkin';
  const exp = Math.floor(Date.now() / 1000) + 15 * 60;
  const payload = `${slug}.${exp}.${sessionId}`;
  const sig = await hmacSha256(env.DOWNLOAD_SIGNING_SECRET, payload);

  const downloadUrl = `/download?slug=${encodeURIComponent(slug)}` +
                      `&exp=${exp}` +
                      `&sid=${encodeURIComponent(sessionId)}` +
                      `&sig=${sig}`;

  return json({
    ok: true,
    download_url: downloadUrl,
    email: session.customer_details?.email || null,
  });
}

async function hmacSha256(secret, payload) {
  const enc = new TextEncoder();
  const key = await crypto.subtle.importKey(
    'raw', enc.encode(secret),
    { name: 'HMAC', hash: 'SHA-256' },
    false, ['sign']
  );
  const buf = await crypto.subtle.sign('HMAC', key, enc.encode(payload));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, '0')).join('');
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' },
  });
}
