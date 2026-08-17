export async function onRequestPost(context) {
  const { request, env } = context;

  let body;
  try {
    body = await request.json();
  } catch {
    return json({ error: 'invalid body' }, 400);
  }

  const { email, utm_source, utm_medium, utm_campaign, utm_content, page } = body;

  if (!email || !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
    return json({ error: 'invalid email' }, 400);
  }

  if (!env.MAILERLITE_API_KEY || !env.MAILERLITE_GROUP_ID_WAITLIST) {
    console.error('Missing MailerLite env vars');
    return json({ error: 'server misconfigured' }, 500);
  }

  const mlBody = {
    email,
    fields: {
      utm_source: utm_source || '',
      utm_medium: utm_medium || '',
      utm_campaign: utm_campaign || '',
      utm_content: utm_content || '',
      signup_page: page || '/',
    },
    groups: [env.MAILERLITE_GROUP_ID_WAITLIST],
    status: 'active',
  };

  try {
    const res = await fetch('https://connect.mailerlite.com/api/subscribers', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${env.MAILERLITE_API_KEY}`,
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(mlBody),
    });

    if (!res.ok) {
      const errText = await res.text();
      console.error('MailerLite error', res.status, errText);
      return json({ error: 'subscribe failed' }, 502);
    }

    return json({ ok: true }, 200);
  } catch (err) {
    console.error('Subscribe fetch failed', err);
    return json({ error: 'network error' }, 502);
  }
}

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { 'Content-Type': 'application/json' },
  });
}
