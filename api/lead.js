// Vercel serverless function: stores lead-form submissions in Upstash Redis (KV)
// Env vars (Vercel → Project → Settings → Environment Variables, or connect the Upstash store):
//   KV_REST_API_URL, KV_REST_API_TOKEN   (Upstash REST credentials)
//   LEAD_NOTIFY_WEBHOOK (optional) — any URL to POST the lead to (Zapier/Make/Slack/email relay)
export default async function handler(req, res) {
  if (req.method !== 'POST') { res.setHeader('Allow', 'POST'); return res.status(405).json({ ok: false }); }
  let body = req.body;
  if (typeof body === 'string') { try { body = JSON.parse(body); } catch { body = {}; } }
  body = body || {};
  if (body.website) return res.status(200).json({ ok: true }); // honeypot — silently drop bots
  const name = String(body.name || '').trim().slice(0, 120);
  const phone = String(body.phone || '').trim().slice(0, 40);
  if (!name || !phone) return res.status(400).json({ ok: false, error: 'Name and phone are required.' });

  const lead = {
    id: `lead_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`,
    site: 'plumbersbonneylake.com',
    receivedAt: new Date().toISOString(),
    name, phone,
    email: String(body.email || '').trim().slice(0, 160),
    city: String(body.city || '').trim().slice(0, 60),
    service: String(body.service || '').trim().slice(0, 120),
    urgency: String(body.urgency || '').trim().slice(0, 60),
    message: String(body.message || '').trim().slice(0, 2000),
    page: String(body.page || '').slice(0, 200),
    ip: (req.headers['x-forwarded-for'] || '').split(',')[0].trim(),
    ua: String(req.headers['user-agent'] || '').slice(0, 300)
  };

  const url = process.env.KV_REST_API_URL, token = process.env.KV_REST_API_TOKEN;
  try {
    if (url && token) {
      const h = { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' };
      await fetch(`${url}/pipeline`, { method: 'POST', headers: h, body: JSON.stringify([
        ['SET', `leads:${lead.id}`, JSON.stringify(lead)],
        ['LPUSH', 'leads:index', lead.id],
        ['LTRIM', 'leads:index', 0, 999]
      ]) });
    } else {
      console.warn('KV env vars missing — lead logged only', lead);
    }
    if (process.env.LEAD_NOTIFY_WEBHOOK) {
      await fetch(process.env.LEAD_NOTIFY_WEBHOOK, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(lead) }).catch(() => {});
    }
    return res.status(200).json({ ok: true, id: lead.id });
  } catch (e) {
    console.error('lead store failed', e);
    return res.status(500).json({ ok: false });
  }
}
