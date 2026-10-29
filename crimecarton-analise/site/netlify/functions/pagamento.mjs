// GET /api/pagamento?id=…: how a payment went, checked with Mercado Pago rather than read from
// the return address. The Pix window asks it every few seconds until the Pix is paid.
// It answers only the status and the part.
import { mp, situacao, token } from '../lib/mercadopago.mjs';

const resposta = (dados, status = 200) => Response.json(dados, { status, headers: { 'Cache-Control': 'no-store' } });

export default async (req) => {
  const id = new URL(req.url).searchParams.get('id') || '';
  if (!/^\d{1,20}$/.test(id)) return resposta({ erro: 'Pagamento inválido.' }, 400);
  if (!token()) return resposta({ erro: 'O pagamento ainda não está ligado.' }, 503);
  let pagamento;
  try {
    pagamento = await mp(`/v1/payments/${id}`);
  } catch (e) {
    if (e.status === 404) return resposta({ erro: 'Pagamento não encontrado.' }, 404);
    console.error(e);
    return resposta({ erro: 'Não deu para conferir o pagamento agora.' }, 502);
  }
  // Only passes of the series: any other payment of the account stays private.
  const [tipo, parte] = String(pagamento.external_reference || '').split('|');
  if (tipo !== 'aliado') return resposta({ erro: 'Pagamento não encontrado.' }, 404);
  return resposta({ status: situacao(pagamento.status), parte: Number(parte) });
};

export const config = { path: '/api/pagamento', method: 'GET' };
