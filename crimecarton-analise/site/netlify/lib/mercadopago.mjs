// Mercado Pago's REST API, called with the account's access token from MP_ACCESS_TOKEN.
const API = 'https://api.mercadopago.com';

export function token() {
  const valor = globalThis.Netlify?.env.get('MP_ACCESS_TOKEN') ?? process.env.MP_ACCESS_TOKEN;
  return (valor || '').trim();
}

export async function mp(caminho, { method = 'GET', body } = {}) {
  const headers = { Authorization: `Bearer ${token()}`, Accept: 'application/json' };
  if (body) headers['Content-Type'] = 'application/json';
  const res = await fetch(API + caminho, { method, headers, body: body && JSON.stringify(body) });
  const dados = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(`Mercado Pago ${res.status} em ${caminho.split('?')[0]}: ${dados.message || res.statusText}`);
  }
  return dados;
}

// Every payment created since `desde`, oldest first. The search returns at most 50 a page.
export async function pagamentos(desde) {
  const todos = [];
  for (let offset = 0; offset <= 10000; offset += 50) {
    const busca = new URLSearchParams({
      sort: 'date_created', criteria: 'asc', range: 'date_created',
      begin_date: desde, end_date: 'NOW', limit: '50', offset: String(offset),
    });
    const pagina = await mp(`/v1/payments/search?${busca}`);
    const lote = pagina.results || [];
    todos.push(...lote);
    if (lote.length < 50 || offset + 50 >= (pagina.paging?.total ?? 0)) break;
  }
  return todos;
}
