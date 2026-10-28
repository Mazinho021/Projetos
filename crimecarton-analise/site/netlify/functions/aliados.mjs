// GET /api/aliados: the open part's list of allies and the next ally number, for the page.
// It only ever returns handles and numbers, never e-mails or payment details.
import { SERIE } from '../lib/serie.mjs';
import { pagamentos, token } from '../lib/mercadopago.mjs';
import { montarLista } from '../lib/aliados.mjs';

// The CDN keeps the answer for a minute, so busy hours don't search the payments on every visit.
const CACHE = {
  'Cache-Control': 'public, max-age=0, must-revalidate',
  'Netlify-CDN-Cache-Control': 'public, durable, s-maxage=60, stale-while-revalidate=300',
};

export default async () => {
  const base = { parte: SERIE.parte, vagas: SERIE.vagas, fecha: SERIE.fecha };
  if (!token()) {
    return Response.json({ ...base, ligado: false, aliados: [], proximoNumero: 1 }, { headers: CACHE });
  }
  try {
    const { numeros, partes } = montarLista(await pagamentos(SERIE.inicio), SERIE.vagas, SERIE.correcoes);
    const aliados = (partes.get(SERIE.parte) || []).map(a => ({ arroba: `@${a}`, numero: numeros.get(a) }));
    return Response.json({ ...base, ligado: true, aliados, proximoNumero: numeros.size + 1 }, { headers: CACHE });
  } catch (e) {
    console.error(e);
    return Response.json({ ...base, erro: 'Não deu para ler a lista agora.' }, { status: 502, headers: { 'Cache-Control': 'no-store' } });
  }
};

export const config = { path: '/api/aliados', method: 'GET' };
