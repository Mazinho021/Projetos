// Mercado Pago's REST API, called with the account's access token from MP_ACCESS_TOKEN.
const API = 'https://api.mercadopago.com';

const ambiente = nome => (globalThis.Netlify?.env.get(nome) ?? process.env[nome] ?? '').trim();

export function token() {
  return ambiente('MP_ACCESS_TOKEN');
}

// The public key goes to the page, for Mercado Pago's card form. Only a value shaped like a
// public key is handed out, so an access token put in the wrong variable never reaches the page.
export function chavePublica() {
  const valor = ambiente('MP_PUBLIC_KEY');
  return /^(APP_USR|TEST)-[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$/i.test(valor) ? valor : '';
}

// Mercado Pago's payment statuses, in the three states the page shows.
const SITUACAO = {
  approved: 'aprovado', in_mediation: 'aprovado',
  pending: 'pendente', in_process: 'pendente', authorized: 'pendente',
  rejected: 'falhou', cancelled: 'falhou', refunded: 'falhou', charged_back: 'falhou',
};
export const situacao = status => SITUACAO[status] || 'pendente';

export async function mp(caminho, { method = 'GET', body, cabecalhos = {} } = {}) {
  const headers = { Authorization: `Bearer ${token()}`, Accept: 'application/json', ...cabecalhos };
  if (body) headers['Content-Type'] = 'application/json';
  const res = await fetch(API + caminho, { method, headers, body: body && JSON.stringify(body) });
  const dados = await res.json().catch(() => ({}));
  if (!res.ok) {
    const causa = (dados.cause || []).map(c => c.code).join(',');
    const erro = new Error(`Mercado Pago ${res.status} em ${caminho.split('?')[0]}: ${dados.message || res.statusText}${causa ? ` (${causa})` : ''}`);
    erro.status = res.status;
    throw erro;
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
