export interface Env {
  GROQ_API_KEY: string;
  GROQ_MODEL?: string; // ej: "llama-3.1-70b-versatile"
  BUSINESS_JSON_URL?: string; // opcional: URL cruda al JSON del repo
}

interface BusinessProfile {
  id: string;
  name: string;
  defaultLocale: string;
  currency: string;
  tone: { style: string; signoff: string };
  policies: { delivery?: string; returns?: string; disclaimer?: string; stock?: string };
  payments: {
    discounts: { label: string; percent: number; key: string }[];
    installments?: { count: number; noInterest: boolean; label: string };
  };
  catalog: { sku: string; title: string; price: number; weight_g?: number; attrs?: Record<string,string> }[];
}

type ChatReq = { message: string; locale?: string; business?: BusinessProfile };

const DEFAULT_MODEL = "llama3-70b-8192"; // fallback seguro en caso de no setear env

function cors(res: Response): Response {
  const headers = new Headers(res.headers);
  headers.set('Access-Control-Allow-Origin', '*');
  headers.set('Access-Control-Allow-Methods', 'GET,POST,OPTIONS');
  headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  return new Response(res.body, { status: res.status, headers });
}

function formatMoney(n: number, locale: string, currency: string) {
  try {
    return new Intl.NumberFormat(locale, { style: 'currency', currency }).format(n);
  } catch {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(n);
  }
}

function computeOffers(biz: BusinessProfile, locale: string) {
  const out: Record<string, any> = {};
  for (const p of biz.catalog) {
    const base = p.price;
    const discounts = biz.payments.discounts.map(d => ({
      key: d.key,
      label: d.label,
      value: Math.round(base * (1 - d.percent / 100)),
    }));
    let installments: { label: string; perInstallment: number; count: number } | undefined;
    if (biz.payments.installments && biz.payments.installments.count > 0) {
      const count = biz.payments.installments.count;
      // Sin interés: dividir exacto; con interés: (PoC) asumimos 0% también
      const each = Math.round(base / count);
      installments = { label: biz.payments.installments.label, perInstallment: each, count };
    }
    out[p.sku] = {
      sku: p.sku,
      title: p.title,
      base_price: base,
      formatted: {
        base: formatMoney(base, locale, biz.currency),
        discounts: discounts.map(d => ({ ...d, formatted: formatMoney(d.value, locale, biz.currency) })),
        installments: installments
          ? {
              ...installments,
              formattedEach: formatMoney(installments.perInstallment, locale, biz.currency)
            }
          : undefined,
      }
    };
  }
  return out;
}

function buildSystemPrompt(biz: BusinessProfile, locale: string, offers: Record<string, any>) {
  const policies = [biz.policies.stock, biz.policies.disclaimer].filter(Boolean).join(' ');
  return `Eres un agente comercial del negocio "${biz.name}". Habla en ${locale}. Tono: ${biz.tone.style}.

Reglas:
- Usa EXCLUSIVAMENTE la información de catálogo y de ofertas calculadas que te paso. No inventes stock, precios ni tiempos.
- Si falta información clave, pide SOLO un dato adicional de manera breve.
- Formatea como chat amigable estilo WhatsApp, con bullets y emojis moderados. Evita párrafos largos.
- Cuando menciones precios, utiliza los números ya FORMATEADOS provistos y NO recalcules.
- Cierra con: "${biz.tone.signoff}". Si hablaste de precios, añade: "${policies}".
` +
  `\nCATÁLOGO RELEVANTE (con ofertas):\n` +
  Object.values(offers).map((o: any) => {
    const ds = o.formatted.discounts.map((d: any) => `• ${d.label}: ${d.formatted}`).join('\n');
    const inst = o.formatted.installments
      ? `• ${o.formatted.installments.label}: ${o.formatted.installments.count} pagos de ${o.formatted.installments.formattedEach}`
      : '';
    return `- ${o.sku} · ${o.title}\n  Precio base: ${o.formatted.base}\n  ${ds}\n  ${inst}`;
  }).join('\n');
}

async function fetchBusiness(env: Env): Promise<BusinessProfile> {
  if (env.BUSINESS_JSON_URL) {
    const r = await fetch(env.BUSINESS_JSON_URL);
    if (r.ok) return await r.json<BusinessProfile>();
  }
  
  // Fallback: usar el business.json del repo
  const r = await fetch('https://raw.githubusercontent.com/kvothesson/chat-saas-poc/main/data/business.json');
  if (r.ok) return await r.json<BusinessProfile>();
  
  throw new Error('No se pudo cargar el perfil de negocio');
}

function detectLocale(input?: string, fallback?: string) {
  if (!input) return fallback || 'es-AR';
  const s = input.toLowerCase();
  if (/[áéíóúñ¡¿]/.test(s) || /(hola|gracias|buen[oa]s|consulta)/.test(s)) return 'es-AR';
  if (/(hello|hi|thanks|price|shipping)/.test(s)) return 'en-US';
  return fallback || 'es-AR';
}

async function callGroq(env: Env, systemPrompt: string, user: string) {
  const model = env.GROQ_MODEL || DEFAULT_MODEL;
  const body = {
    model,
    messages: [
      { role: 'system', content: systemPrompt },
      { role: 'user', content: user }
    ],
    temperature: 0.6,
    max_tokens: 700
  };

  const r = await fetch('https://api.groq.com/openai/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${env.GROQ_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  });
  if (!r.ok) throw new Error(`Groq API error ${r.status}`);
  const data = await r.json<any>();
  const text = data.choices?.[0]?.message?.content || '';
  return text;
}

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    if (request.method === 'OPTIONS') {
      return cors(new Response(null, { status: 204 }));
    }

    const url = new URL(request.url);
    if (url.pathname === '/chat' && request.method === 'POST') {
      try {
        const { message, locale, business } = (await request.json()) as ChatReq;
        const biz = business || await fetchBusiness(env);
        const loc = locale || detectLocale(message, biz.defaultLocale);
        const offers = computeOffers(biz, loc);
        const sys = buildSystemPrompt(biz, loc, offers);
        const reply = await callGroq(env, sys, message);
        const res = { reply, locale: loc, business: biz.id };
        return cors(new Response(JSON.stringify(res), { status: 200, headers: { 'Content-Type': 'application/json' } }));
      } catch (e: any) {
        return cors(new Response(JSON.stringify({ error: e.message }), { status: 500, headers: { 'Content-Type': 'application/json' } }));
      }
    }

    if (url.pathname === '/') {
      return cors(new Response('Agent Worker OK', { status: 200 }));
    }

    return cors(new Response('Not found', { status: 404 }));
  }
};
