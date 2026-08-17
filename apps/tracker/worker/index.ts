// Cloudflare Worker: ingest events + Gumroad pings → Supabase.
// Fail loud on Supabase errors (matches run_scheduler.py operating rule).

export interface Env {
  SUPABASE_URL: string;
  SUPABASE_SERVICE_KEY: string;
  DAILY_SALT: string;
  GUMROAD_PING_SECRET: string;
}

const ALLOWED_ORIGINS = [
  "https://grissompress.pplx.app",
  "https://cedarhollow.pplx.app",
  "https://cedarhollow.grissompress.com",
  "https://grissom77.gumroad.com",
];

export default {
  async fetch(req: Request, env: Env): Promise<Response> {
    const url = new URL(req.url);
    const origin = req.headers.get("Origin") ?? "";
    const cors = {
      "Access-Control-Allow-Origin": ALLOWED_ORIGINS.includes(origin) ? origin : "null",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "content-type",
    };
    if (req.method === "OPTIONS") return new Response(null, { headers: cors });

    if (url.pathname === "/e" && req.method === "POST") return handleEvent(req, env, cors);
    if (url.pathname === "/gumroad" && req.method === "POST") return handleGumroad(req, env);
    return new Response("not found", { status: 404 });
  },
};

async function handleEvent(req: Request, env: Env, cors: Record<string, string>) {
  let body: any;
  try { body = await req.json(); }
  catch { return new Response("bad json", { status: 400, headers: cors }); }

  const ip = req.headers.get("CF-Connecting-IP") ?? "";
  const ua = req.headers.get("User-Agent") ?? "";
  const ip_hash = await sha256(ip + env.DAILY_SALT);
  const ua_hash = await sha256(ua + env.DAILY_SALT);

  const row = {
    brand:        String(body.brand ?? "").slice(0, 32),
    post_id:      body.post_id ? String(body.post_id).slice(0, 128) : null,
    platform:     body.platform ? String(body.platform).slice(0, 32) : null,
    event:        String(body.event ?? "").slice(0, 32),
    utm_content:  body.utm_content ?? null,
    utm_campaign: body.utm_campaign ?? null,
    session_id:   String(body.session_id ?? "").slice(0, 64),
    page_url:     body.page_url ?? null,
    referrer:     body.referrer ?? null,
    ip_hash, ua_hash,
  };

  if (!row.brand || !row.event || !row.session_id) {
    return new Response("missing fields", { status: 400, headers: cors });
  }

  const resp = await fetch(`${env.SUPABASE_URL}/rest/v1/events`, {
    method: "POST",
    headers: {
      apikey: env.SUPABASE_SERVICE_KEY,
      authorization: `Bearer ${env.SUPABASE_SERVICE_KEY}`,
      "content-type": "application/json",
      prefer: "return=minimal",
    },
    body: JSON.stringify(row),
  });

  if (!resp.ok) {
    console.error("supabase insert failed", resp.status, await resp.text());
    return new Response("ingest error", { status: 502, headers: cors });
  }
  return new Response(null, { status: 204, headers: cors });
}

async function handleGumroad(req: Request, env: Env) {
  const form = await req.formData();
  if (form.get("secret") !== env.GUMROAD_PING_SECRET) {
    return new Response("forbidden", { status: 403 });
  }
  const url_params = new URLSearchParams(String(form.get("url_params") ?? ""));
  const row = {
    brand:        inferBrand(String(form.get("permalink") ?? "")),
    post_id:      url_params.get("utm_content"),
    platform:     url_params.get("utm_source"),
    event:        "purchase",
    utm_content:  url_params.get("utm_content"),
    utm_campaign: url_params.get("utm_campaign"),
    session_id:   String(form.get("sale_id") ?? "gumroad"),
    amount_cents: Math.round(parseFloat(String(form.get("price") ?? "0")) * 100),
    product_sku:  String(form.get("permalink") ?? ""),
    page_url:     String(form.get("product_permalink") ?? ""),
  };
  const resp = await fetch(`${env.SUPABASE_URL}/rest/v1/events`, {
    method: "POST",
    headers: {
      apikey: env.SUPABASE_SERVICE_KEY,
      authorization: `Bearer ${env.SUPABASE_SERVICE_KEY}`,
      "content-type": "application/json",
    },
    body: JSON.stringify(row),
  });
  if (!resp.ok) {
    console.error("gumroad ingest failed", resp.status, await resp.text());
    return new Response("ingest error", { status: 502 });
  }
  return new Response("ok", { status: 200 });
}

export function inferBrand(permalink: string): string {
  const p = permalink.toLowerCase();
  if (p.includes("handy") || p.includes("cedar") || p.includes("gothic") || p.includes("spooky")) return "grissom";
  if (p.includes("familybook") || p.includes("kids"))                                             return "familybook";
  if (p.includes("ora"))                                                                          return "ora";
  return "grissom";
}

export async function sha256(s: string): Promise<string> {
  const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(s));
  return [...new Uint8Array(buf)].map(b => b.toString(16).padStart(2, "0")).join("");
}
