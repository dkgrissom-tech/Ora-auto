/**
 * GET /download?slug=pip-the-pumpkin&exp=...&sid=...&sig=...
 *
 * Serves the PDF only if the HMAC signature is valid AND not expired.
 * Prevents random people from hotlinking /downloads/pip-the-pumpkin.pdf directly.
 *
 * The file itself lives at /downloads/<slug>.pdf inside the same Pages project,
 * but /downloads/ is blocked from direct access by _headers (see file).
 */

export async function onRequestGet(context) {
  const { request, env } = context;
  const url = new URL(request.url);
  const slug = url.searchParams.get('slug');
  const exp = parseInt(url.searchParams.get('exp') || '0', 10);
  const sid = url.searchParams.get('sid');
  const sig = url.searchParams.get('sig');

  if (!slug || !exp || !sid || !sig) return text('bad request', 400);
  if (!env.DOWNLOAD_SIGNING_SECRET) return text('server misconfigured', 500);

  const now = Math.floor(Date.now() / 1000);
  if (now > exp) return text('link expired — please re-open your thank-you page', 410);

  // Re-derive the signature and constant-time compare
  const expected = await hmacSha256(env.DOWNLOAD_SIGNING_SECRET, `${slug}.${exp}.${sid}`);
  if (!timingSafeEqual(sig, expected)) return text('invalid signature', 403);

  // Only allow known product slugs (prevents path traversal)
  const KNOWN = new Set(['pip-the-pumpkin']);
  if (!KNOWN.has(slug)) return text('unknown product', 404);

  // Fetch the PDF from the same Pages deployment. _files/ is blocked at the
  // edge by _redirects for external requests, but Pages Functions can still
  // fetch it via env.ASSETS.fetch() which bypasses redirects.
  const assetUrl = new URL(`/_files/${slug}.pdf`, request.url);
  const assetRes = await context.env.ASSETS
    ? context.env.ASSETS.fetch(assetUrl.toString())
    : fetch(assetUrl.toString());

  if (!assetRes.ok) return text('file not found', 404);

  return new Response(assetRes.body, {
    status: 200,
    headers: {
      'Content-Type': 'application/pdf',
      'Content-Disposition': `attachment; filename="${slug}.pdf"`,
      'Cache-Control': 'no-store',
    },
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

function timingSafeEqual(a, b) {
  if (a.length !== b.length) return false;
  let r = 0;
  for (let i = 0; i < a.length; i++) r |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return r === 0;
}

function text(msg, status = 200) {
  return new Response(msg, {
    status,
    headers: { 'Content-Type': 'text/plain', 'Cache-Control': 'no-store' },
  });
}
