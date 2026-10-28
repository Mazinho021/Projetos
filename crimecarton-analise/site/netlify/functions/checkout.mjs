// POST /api/checkout: checks the form and opens a Mercado Pago checkout for one pass,
// paid with Pix or card. The page sends the buyer to the returned url.
import { SERIE } from '../lib/serie.mjs';
import { mp, pagamentos, token } from '../lib/mercadopago.mjs';
import { montarLista, parteDaCompra, referencia } from '../lib/aliados.mjs';

const resposta = (dados, status = 200) => Response.json(dados, { status, headers: { 'Cache-Control': 'no-store' } });

export default async (req) => {
  if (!token()) {
    return resposta({ erro: 'O pagamento ainda não está ligado. Tenta de novo mais tarde ou chama no direct do @golpecartoon.' }, 503);
  }
  let dados;
  try {
    dados = await req.json();
  } catch {
    return resposta({ erro: 'Não deu para ler o pedido. Recarregue a página e tente de novo.' }, 400);
  }
  const arroba = String(dados.arroba ?? '').trim().replace(/^@+/, '').toLowerCase();
  const email = String(dados.email ?? '').trim();
  if (!/^[a-z0-9._]{1,30}$/.test(arroba)) {
    return resposta({ erro: 'Escreva o seu @ do Instagram, só com letras, números, ponto ou sublinhado.' }, 400);
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return resposta({ erro: 'Confira o seu e-mail: ele precisa ter @ e um domínio, como voce@email.com.' }, 400);
  }
  if (dados.autorizo !== true) {
    return resposta({ erro: 'Marque a autorização para usarmos o seu @ na história.' }, 400);
  }

  try {
    const { partes } = montarLista(await pagamentos(SERIE.inicio), SERIE.vagas, SERIE.correcoes);
    const parte = parteDaCompra(SERIE, Date.now(), partes);
    if ((partes.get(parte) || []).includes(arroba)) {
      return resposta({ erro: `O @${arroba} já está na lista da Parte ${parte}.` }, 409);
    }
    const site = new URL(req.url).origin;
    const preferencia = await mp('/checkout/preferences', {
      method: 'POST',
      body: {
        items: [{
          id: `passe-aliado-${parte}`,
          title: `Passe de aliado · Parte ${parte}`,
          description: `@${arroba} na Parte ${parte} de A parte que faltou`,
          quantity: 1,
          currency_id: 'BRL',
          unit_price: SERIE.preco,
        }],
        payer: { email },
        external_reference: referencia(parte, arroba),
        metadata: { arroba, parte },
        back_urls: {
          success: `${site}/?pagamento=aprovado&parte=${parte}`,
          pending: `${site}/?pagamento=pendente&parte=${parte}`,
          failure: `${site}/?pagamento=falhou&parte=${parte}`,
        },
        auto_return: 'approved',
        // Pix and cards only: a boleto can take days, past the deadline of the list.
        payment_methods: { excluded_payment_types: [{ id: 'ticket' }], installments: 1 },
        statement_descriptor: 'GOLPECARTOON',
      },
    });
    return resposta({ url: preferencia.init_point, parte });
  } catch (e) {
    console.error(e);
    return resposta({ erro: 'Não deu para abrir o pagamento agora. Tenta de novo em alguns minutos.' }, 502);
  }
};

export const config = { path: '/api/checkout', method: 'POST' };
