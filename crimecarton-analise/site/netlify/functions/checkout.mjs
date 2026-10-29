// POST /api/checkout: checks the form and opens the payment for one pass, on the site itself.
// The page asks for a Pix it shows in its own window (meio: 'pix'), or sends the token of
// Mercado Pago's card form shown in that window (meio: 'cartao'). Anything else gets a
// Checkout Pro page on Mercado Pago's site: the card while the card form is off, and a form
// posted without JavaScript, which is redirected there.
import { randomUUID } from 'node:crypto';
import { SERIE } from '../lib/serie.mjs';
import { mp, pagamentos, situacao, token } from '../lib/mercadopago.mjs';
import { montarLista, parteDaCompra, referencia } from '../lib/aliados.mjs';

const ERROS = {
  desligado: [503, 'O pagamento ainda não está ligado. Tenta de novo mais tarde ou chama no direct do @golpecartoon.'],
  pedido: [400, 'Não deu para ler o pedido. Recarregue a página e tente de novo.'],
  arroba: [400, 'Escreva o seu @ do Instagram, só com letras, números, ponto ou sublinhado.'],
  email: [400, 'Confira o seu e-mail: ele precisa ter @ e um domínio, como voce@email.com.'],
  autorizo: [400, 'Marque a autorização para usarmos o seu @ na história.'],
  cartao: [400, 'Faltaram dados do cartão. Preencha o formulário do cartão de novo.'],
  falha: [502, 'Não deu para abrir o pagamento agora. Tenta de novo em alguns minutos.'],
};

// Why a card was refused, in words the buyer can act on (Mercado Pago's status_detail).
const RECUSAS = {
  cc_rejected_bad_filled_card_number: 'Confira o número do cartão.',
  cc_rejected_bad_filled_date: 'Confira a validade do cartão.',
  cc_rejected_bad_filled_security_code: 'Confira o código de segurança do cartão.',
  cc_rejected_bad_filled_other: 'Confira os dados do cartão.',
  cc_rejected_insufficient_amount: 'O cartão não tem limite para esse valor.',
  cc_rejected_call_for_authorize: 'O banco pede que você autorize o pagamento. Fale com o banco ou pague com Pix.',
  cc_rejected_card_disabled: 'O cartão não está ativo. Ative com o banco ou pague com Pix.',
  cc_rejected_duplicated_payment: 'Você fez um pagamento igual agora há pouco. Confira o seu e-mail antes de tentar de novo.',
  cc_rejected_max_attempts: 'O cartão chegou ao limite de tentativas. Use outro cartão ou pague com Pix.',
  cc_rejected_high_risk: 'O Mercado Pago recusou o pagamento por segurança. Pague com Pix ou outro cartão.',
};
const RECUSA = 'O cartão foi recusado, e nada foi cobrado. Tente outro cartão ou pague com Pix.';

// Mercado Pago takes a Pix that lasts at least 30 minutes; the extra minute covers the trip.
const PRAZO_PIX = 31 * 60 * 1000;

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
  const meio = formulario ? 'pagina' : dados.meio;
  const cartao = meio === 'cartao' ? lerCartao(dados.cartao) : null;
  if (meio === 'cartao' && !cartao) return falhar('cartao');

  try {
    const { partes } = montarLista(await pagamentos(SERIE.inicio), SERIE.vagas, SERIE.correcoes);
    const parte = parteDaCompra(SERIE, Date.now(), partes);
    if ((partes.get(parte) || []).includes(arroba)) {
      return falhar('repetido', `O @${arroba} já está na lista da Parte ${parte}.`);
    }
    const passe = { parte, arroba, email };
    if (meio === 'pix') return responder(await criarPix(passe));
    if (meio === 'cartao') return responder(await cobrarCartao(passe, cartao));
    return responder(await abrirPagina(passe, site));
  } catch (e) {
    console.error(e);
    return falhar('falha');
  }
};

// The card form's output: a one-time token and what Mercado Pago needs to charge it. The amount
// and the installments are never read from the page.
function lerCartao(c) {
  if (!c || typeof c !== 'object') return null;
  const { token, payment_method_id, issuer_id, identification } = c;
  const documento = {
    type: String(identification?.type || 'CPF').toUpperCase(),
    number: String(identification?.number || '').replace(/\D/g, ''),
  };
  if (typeof token !== 'string' || !/^[\w-]{10,100}$/.test(token)) return null;
  if (typeof payment_method_id !== 'string' || !/^[a-z_]{2,30}$/.test(payment_method_id)) return null;
  if (!/^(CPF|CNPJ)$/.test(documento.type) || !/^\d{11,14}$/.test(documento.number)) return null;
  const emissor = String(issuer_id ?? '');
  return { token, payment_method_id, ...(/^\d{1,10}$/.test(emissor) && { issuer_id: emissor }), identification: documento };
}

// What a pass is, as Mercado Pago shows it to the buyer and in the account.
const item = ({ parte, arroba }) => ({
  id: `passe-aliado-${parte}`,
  title: `Passe de aliado · Parte ${parte}`,
  description: `@${arroba} na Parte ${parte} de A parte que faltou`,
  quantity: 1,
  unit_price: SERIE.preco,
});

// Mercado Pago reads dates with their offset; Brasília has had no daylight saving since 2019.
const horarioDeBrasilia = ms => new Date(ms - 3 * 3600 * 1000).toISOString().replace('Z', '-03:00');

// A Pix the page shows itself: Mercado Pago returns the copy-and-paste code and the QR Code.
// An unpaid Pix holds no place on the list, and it expires in about half an hour.
async function criarPix(passe) {
  const produto = item(passe);
  const pagamento = await mp('/v1/payments', {
    method: 'POST',
    cabecalhos: { 'X-Idempotency-Key': randomUUID() },
    body: {
      transaction_amount: SERIE.preco,
      description: produto.title,
      payment_method_id: 'pix',
      payer: { email: passe.email },
      external_reference: referencia(passe.parte, passe.arroba),
      metadata: { arroba: passe.arroba, parte: passe.parte },
      date_of_expiration: horarioDeBrasilia(Date.now() + PRAZO_PIX),
      additional_info: { items: [produto] },
    },
  });
  const pix = pagamento.point_of_interaction?.transaction_data || {};
  if (!pix.qr_code) throw new Error(`Mercado Pago não devolveu o código do Pix ${pagamento.id}`);
  return {
    meio: 'pix', id: pagamento.id, parte: passe.parte,
    codigo: pix.qr_code, qr: pix.qr_code_base64 || '', expira: pagamento.date_of_expiration,
  };
}

// A card paid in Mercado Pago's card form inside the page. The answer comes at once: approved,
// refused (with the reason) or under review.
async function cobrarCartao(passe, cartao) {
  const produto = item(passe);
  const pagamento = await mp('/v1/payments', {
    method: 'POST',
    cabecalhos: { 'X-Idempotency-Key': randomUUID() },
    body: {
      transaction_amount: SERIE.preco,
      token: cartao.token,
      description: produto.title,
      installments: 1,
      payment_method_id: cartao.payment_method_id,
      ...(cartao.issuer_id && { issuer_id: cartao.issuer_id }),
      payer: { email: passe.email, identification: cartao.identification },
      external_reference: referencia(passe.parte, passe.arroba),
      metadata: { arroba: passe.arroba, parte: passe.parte },
      statement_descriptor: 'GOLPECARTOON',
      additional_info: { items: [produto] },
    },
  });
  const status = situacao(pagamento.status);
  return {
    meio: 'cartao', id: pagamento.id, parte: passe.parte, status,
    ...(status === 'falhou' && { motivo: RECUSAS[pagamento.status_detail] || RECUSA }),
  };
}

// Checkout Pro: a payment page on Mercado Pago's site, with Pix and card.
async function abrirPagina(passe, site) {
  const { parte, arroba, email } = passe;
  // Mercado Pago refuses auto_return when the return address is not public HTTPS (netlify dev).
  const publico = /^https:\/\//.test(site) && !/^https:\/\/(localhost|127\.0\.0\.1|0\.0\.0\.0)(:|\/|$)/.test(site);
  const preferencia = await mp('/checkout/preferences', {
    method: 'POST',
    body: {
      items: [{ ...item(passe), currency_id: 'BRL' }],
      payer: { email },
      external_reference: referencia(parte, arroba),
      metadata: { arroba, parte },
      back_urls: {
        success: `${site}/?pagamento=aprovado&parte=${parte}`,
        pending: `${site}/?pagamento=pendente&parte=${parte}`,
        failure: `${site}/?pagamento=falhou&parte=${parte}`,
      },
      ...(publico ? { auto_return: 'approved' } : {}),
      // Pix and credit cards only: a boleto can take days, past the deadline of the list,
      // and Pix already does what a debit card would.
      payment_methods: { excluded_payment_types: [{ id: 'ticket' }, { id: 'debit_card' }], installments: 1 },
      statement_descriptor: 'GOLPECARTOON',
    },
  });
  return { init_point: preferencia.init_point, parte };
}

export const config = { path: '/api/checkout', method: 'POST' };
