// POST /api/checkout: checks the form and opens a Mercado Pago checkout (Checkout Pro) for one
// pass, paid with Pix or card. The page sends JSON and redirects to the returned init_point;
// without JavaScript, the form posts itself here and is redirected straight to Mercado Pago.
import { SERIE } from '../lib/serie.mjs';
import { mp, pagamentos, token } from '../lib/mercadopago.mjs';
import { montarLista, parteDaCompra, referencia } from '../lib/aliados.mjs';

const ERROS = {
  desligado: [503, 'O pagamento ainda não está ligado. Tenta de novo mais tarde ou chama no direct do @golpecartoon.'],
  pedido: [400, 'Não deu para ler o pedido. Recarregue a página e tente de novo.'],
  arroba: [400, 'Escreva o seu @ do Instagram, só com letras, números, ponto ou sublinhado.'],
  email: [400, 'Confira o seu e-mail: ele precisa ter @ e um domínio, como voce@email.com.'],
  autorizo: [400, 'Marque a autorização para usarmos o seu @ na história.'],
  falha: [502, 'Não deu para abrir o pagamento agora. Tenta de novo em alguns minutos.'],
};

export default async (req) => {
  const site = new URL(req.url).origin;
  const formulario = !(req.headers.get('content-type') || '').includes('application/json');
  // A JSON answer for the page; a redirect for a form posted without JavaScript, whose errors
  // travel as a code (never as free text) back to the form.
  const responder = (dados, status = 200) => {
    if (formulario) {
      const destino = dados.init_point || `${site}/?erro=${dados.codigo}#aliado`;
      return Response.redirect(destino, 303);
    }
    return Response.json(dados, { status, headers: { 'Cache-Control': 'no-store' } });
  };
  const falhar = (codigo, erro = ERROS[codigo][1]) => responder({ codigo, erro }, ERROS[codigo]?.[0] ?? 409);

  if (!token()) return falhar('desligado');
  let dados;
  try {
    dados = formulario ? Object.fromEntries(await req.formData()) : await req.json();
  } catch {
    return falhar('pedido');
  }
  const arroba = String(dados.arroba ?? '').trim().replace(/^@+/, '').toLowerCase();
  const email = String(dados.email ?? '').trim();
  if (!/^[a-z0-9._]{1,30}$/.test(arroba)) return falhar('arroba');
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) return falhar('email');
  if (dados.autorizo !== true && dados.autorizo !== 'sim') return falhar('autorizo');

  try {
    const { partes } = montarLista(await pagamentos(SERIE.inicio), SERIE.vagas, SERIE.correcoes);
    const parte = parteDaCompra(SERIE, Date.now(), partes);
    if ((partes.get(parte) || []).includes(arroba)) {
      return falhar('repetido', `O @${arroba} já está na lista da Parte ${parte}.`);
    }
    // Mercado Pago refuses auto_return when the return address is not public HTTPS (netlify dev).
    const publico = /^https:\/\//.test(site) && !/^https:\/\/(localhost|127\.0\.0\.1|0\.0\.0\.0)(:|\/|$)/.test(site);
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
        ...(publico ? { auto_return: 'approved' } : {}),
        // Pix and cards only: a boleto can take days, past the deadline of the list.
        payment_methods: { excluded_payment_types: [{ id: 'ticket' }], installments: 1 },
        statement_descriptor: 'GOLPECARTOON',
      },
    });
    return responder({ init_point: preferencia.init_point, parte });
  } catch (e) {
    console.error(e);
    return falhar('falha');
  }
};

export const config = { path: '/api/checkout', method: 'POST' };
