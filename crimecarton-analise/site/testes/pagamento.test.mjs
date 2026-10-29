// node --test crimecarton-analise/site/testes/*.test.mjs
import { test, beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { montarLista, parteDaCompra } from '../netlify/lib/aliados.mjs';
import checkout from '../netlify/functions/checkout.mjs';
import aliados from '../netlify/functions/aliados.mjs';
import pagamento from '../netlify/functions/pagamento.mjs';

const SERIE = { parte: 3, vagas: 2, fecha: '2026-10-30T21:00:00-03:00' };
const pago = (arroba, parte, hora, status = 'approved') => ({
  status, external_reference: `aliado|${parte}|${arroba}`, date_approved: `2026-10-29T${hora}:00.000-04:00`,
});

test('numbers follow the first approved pass and survive refunds', () => {
  const { numeros, partes } = montarLista([
    pago('beto', 3, '12:00'),
    pago('ana', 3, '10:00', 'refunded'),
    pago('caio', 3, '11:00'),
    { status: 'approved', external_reference: 'outra-venda', date_approved: '2026-10-29T09:00:00.000-04:00' },
    { status: 'pending', external_reference: 'aliado|3|dani', date_approved: null },
  ], 10);
  assert.deepEqual([...numeros], [['ana', 1], ['caio', 2], ['beto', 3]]);
  assert.deepEqual(partes.get(3), ['caio', 'beto']);
});

test('a full list sends the next pass to the next part, and a repeat pass adds nobody', () => {
  const { partes } = montarLista([
    pago('ana', 3, '10:00'), pago('beto', 3, '10:05'), pago('ana', 3, '10:07'), pago('caio', 3, '10:10'),
  ], 2);
  assert.deepEqual(partes.get(3), ['ana', 'beto']);
  assert.deepEqual(partes.get(4), ['caio']);
});

test('fixes rename a mistyped handle and leave an offensive one out', () => {
  const { numeros, partes } = montarLista([pago('ana.erradx', 3, '10:00'), pago('ofensivo', 3, '10:05')], 10,
    { 'ana.erradx': 'ana.certa', ofensivo: '' });
  assert.deepEqual(partes.get(3), ['ana.certa']);
  assert.deepEqual([...numeros.keys()], ['ana.certa']);
});

test('after the deadline, or with the list full, a pass counts for the next part', () => {
  const antes = Date.parse('2026-10-30T20:59:00-03:00');
  const depois = Date.parse('2026-10-30T21:01:00-03:00');
  assert.equal(parteDaCompra(SERIE, antes, new Map()), 3);
  assert.equal(parteDaCompra(SERIE, depois, new Map()), 4);
  assert.equal(parteDaCompra(SERIE, antes, new Map([[3, ['ana', 'beto']]])), 4);
});

// The functions, with Mercado Pago answered by a fake fetch.
let chamadas, busca, cartaoResponde;
beforeEach(() => {
  process.env.MP_ACCESS_TOKEN = 'TESTE';
  delete process.env.MP_PUBLIC_KEY;
  chamadas = [];
  busca = [];
  cartaoResponde = { status: 'approved', status_detail: 'accredited' };
  globalThis.fetch = async (url, opcoes = {}) => {
    chamadas.push({ url: String(url), opcoes });
    if (String(url).includes('/v1/payments/search')) {
      return Response.json({ paging: { total: busca.length, limit: 50, offset: 0 }, results: busca });
    }
    if (String(url).endsWith('/checkout/preferences')) {
      return Response.json({ id: 'pref-1', init_point: 'https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=pref-1' });
    }
    if (String(url).endsWith('/v1/payments') && opcoes.method === 'POST') {
      const corpo = JSON.parse(opcoes.body);
      if (corpo.payment_method_id === 'pix') {
        return Response.json({
          id: 444, status: 'pending', status_detail: 'pending_waiting_transfer', date_of_expiration: corpo.date_of_expiration,
          point_of_interaction: { transaction_data: { qr_code: '00020126580014br.gov.bcb.pix', qr_code_base64: 'iVBORw0KGgo=' } },
        }, { status: 201 });
      }
      return Response.json({ id: 555, ...cartaoResponde }, { status: 201 });
    }
    const umPagamento = String(url).match(/\/v1\/payments\/(\d+)$/);
    if (umPagamento && pagamentosPorId[umPagamento[1]]) return Response.json(pagamentosPorId[umPagamento[1]]);
    return Response.json({ message: 'not found' }, { status: 404 });
  };
});
const pagamentosPorId = {
  111: { status: 'approved', external_reference: 'aliado|3|ana', payer: { email: 'ana@email.com' } },
  222: { status: 'pending', external_reference: 'aliado|4|beto' },
  333: { status: 'approved', external_reference: 'outra-venda' },
};
const pedido = (corpo, site = 'https://golpecartoon.netlify.app') => new Request(`${site}/api/checkout`,
  { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(corpo) });
const formulario = campos => new Request('https://golpecartoon.netlify.app/api/checkout',
  { method: 'POST', body: new URLSearchParams(campos) });
const volta = id => new Request(`https://golpecartoon.netlify.app/api/pagamento?id=${id}`);

test('checkout opens a Pix-or-card checkout for the open part', async () => {
  const res = await checkout(pedido({ arroba: '@Seu.Perfil', email: 'voce@email.com', autorizo: true }));
  assert.equal(res.status, 200);
  assert.equal((await res.json()).init_point, 'https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=pref-1');
  const criar = chamadas.find(c => c.url.endsWith('/checkout/preferences'));
  const corpo = JSON.parse(criar.opcoes.body);
  assert.equal(criar.opcoes.headers.Authorization, 'Bearer TESTE');
  assert.equal(corpo.external_reference.split('|')[2], 'seu.perfil');
  assert.equal(corpo.items[0].unit_price, 9.9);
  assert.deepEqual(corpo.payment_methods.excluded_payment_types, [{ id: 'ticket' }, { id: 'debit_card' }]);
  assert.equal(corpo.back_urls.success, 'https://golpecartoon.netlify.app/?pagamento=aprovado&parte=3');
  assert.equal(corpo.auto_return, 'approved');
  assert.equal(corpo.payer.email, 'voce@email.com');
});

test('without JavaScript, the posted form goes straight to Mercado Pago or back with an error code', async () => {
  const certo = await checkout(formulario({ arroba: 'ana', email: 'ana@email.com', autorizo: 'sim' }));
  assert.equal(certo.status, 303);
  assert.equal(certo.headers.get('Location'), 'https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=pref-1');
  const errado = await checkout(formulario({ arroba: 'ana', email: 'ana@email.com' }));
  assert.equal(errado.headers.get('Location'), 'https://golpecartoon.netlify.app/?erro=autorizo#aliado');
});

test('checkout leaves auto_return out when the site is not public HTTPS', async () => {
  await checkout(pedido({ arroba: 'ana', email: 'voce@email.com', autorizo: true }, 'http://localhost:8888'));
  const corpo = JSON.parse(chamadas.find(c => c.url.endsWith('/checkout/preferences')).opcoes.body);
  assert.equal(corpo.auto_return, undefined);
  assert.equal(corpo.back_urls.success, 'http://localhost:8888/?pagamento=aprovado&parte=3');
});

test('the return is checked with Mercado Pago and tells only the status and the part', async () => {
  const aprovado = await pagamento(volta(111));
  assert.equal(aprovado.headers.get('Cache-Control'), 'no-store');
  assert.deepEqual(await aprovado.json(), { status: 'aprovado', parte: 3 });
  assert.deepEqual(await (await pagamento(volta(222))).json(), { status: 'pendente', parte: 4 });
  assert.equal((await pagamento(volta(333))).status, 404);
  assert.equal((await pagamento(volta(999))).status, 404);
  assert.equal((await pagamento(volta('1;drop'))).status, 400);
  delete process.env.MP_ACCESS_TOKEN;
  assert.equal((await pagamento(volta(111))).status, 503);
});

test('checkout refuses a bad handle, a missing consent and a handle already on the list', async () => {
  assert.equal((await checkout(pedido({ arroba: 'eu e você', email: 'voce@email.com', autorizo: true }))).status, 400);
  assert.equal((await checkout(pedido({ arroba: 'ana', email: 'voce@email.com' }))).status, 400);
  busca = [{ status: 'approved', external_reference: 'aliado|3|ana', date_approved: new Date().toISOString() }];
  const res = await checkout(pedido({ arroba: 'ana', email: 'voce@email.com', autorizo: true }));
  assert.equal(res.status, 409);
  assert.match((await res.json()).erro, /já está na lista/);
});

test('without the token the page says the payment is not connected yet', async () => {
  delete process.env.MP_ACCESS_TOKEN;
  assert.equal((await checkout(pedido({ arroba: 'ana', email: 'voce@email.com', autorizo: true }))).status, 503);
  const lista = await (await aliados()).json();
  assert.equal(lista.ligado, false);
  assert.equal(chamadas.length, 0);
});

test('the list shows handles and numbers only', async () => {
  busca = [
    { ...pago('ana', 3, '10:00'), payer: { email: 'ana@email.com' } },
    pago('beto', 3, '11:00', 'refunded'),
  ];
  const res = await aliados();
  assert.match(res.headers.get('Netlify-CDN-Cache-Control'), /s-maxage=60/);
  const lista = await res.json();
  assert.deepEqual(lista.aliados, [{ arroba: '@ana', numero: 1 }]);
  assert.equal(lista.proximoNumero, 3);
  assert.ok(!JSON.stringify(lista).includes('email'));
});

test('a Pix for the site itself comes with its QR Code and copy-and-paste code, for about half an hour', async () => {
  const antes = Date.now();
  const res = await checkout(pedido({ arroba: '@Ana', email: 'ana@email.com', autorizo: true, meio: 'pix' }));
  const criar = chamadas.find(c => c.url.endsWith('/v1/payments'));
  const corpo = JSON.parse(criar.opcoes.body);
  assert.equal(corpo.payment_method_id, 'pix');
  assert.equal(corpo.transaction_amount, 9.9);
  assert.equal(corpo.external_reference, 'aliado|3|ana');
  assert.equal(corpo.payer.email, 'ana@email.com');
  assert.match(criar.opcoes.headers['X-Idempotency-Key'], /^[0-9a-f-]{36}$/);
  assert.match(corpo.date_of_expiration, /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d{3}-03:00$/);
  const minutos = (Date.parse(corpo.date_of_expiration) - antes) / 60000;
  assert.ok(minutos > 30 && minutos < 32, `o Pix vale ${minutos} minutos`);
  assert.deepEqual(await res.json(), {
    meio: 'pix', id: 444, parte: 3, codigo: '00020126580014br.gov.bcb.pix', qr: 'iVBORw0KGgo=', expira: corpo.date_of_expiration,
  });
});

test('a card from the card form is charged with the amount and installments of the server', async () => {
  const pedidoCartao = () => pedido({
    arroba: 'ana', email: 'ana@email.com', autorizo: true, meio: 'cartao', transaction_amount: 0.01, installments: 12,
    cartao: {
      token: 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4', payment_method_id: 'visa', issuer_id: '25', installments: 12,
      identification: { type: 'CPF', number: '123.456.789-09' },
    },
  });
  assert.deepEqual(await (await checkout(pedidoCartao())).json(), { meio: 'cartao', id: 555, parte: 3, status: 'aprovado' });
  const criar = chamadas.find(c => c.url.endsWith('/v1/payments'));
  const corpo = JSON.parse(criar.opcoes.body);
  assert.equal(corpo.transaction_amount, 9.9);
  assert.equal(corpo.installments, 1);
  assert.equal(corpo.token, 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4');
  assert.equal(corpo.payment_method_id, 'visa');
  assert.equal(corpo.issuer_id, '25');
  assert.deepEqual(corpo.payer, { email: 'ana@email.com', identification: { type: 'CPF', number: '12345678909' } });
  assert.equal(corpo.external_reference, 'aliado|3|ana');
  assert.ok(criar.opcoes.headers['X-Idempotency-Key']);

  cartaoResponde = { status: 'rejected', status_detail: 'cc_rejected_insufficient_amount' };
  const recusado = await (await checkout(pedidoCartao())).json();
  assert.equal(recusado.status, 'falhou');
  assert.equal(recusado.motivo, 'O cartão não tem limite para esse valor.');
  cartaoResponde = { status: 'in_process', status_detail: 'pending_review_manual' };
  assert.equal((await (await checkout(pedidoCartao())).json()).status, 'pendente');
});

test('a card without its token is refused, and the form without JavaScript still goes to Mercado Pago', async () => {
  const semToken = await checkout(pedido({ arroba: 'ana', email: 'ana@email.com', autorizo: true, meio: 'cartao', cartao: { payment_method_id: 'visa' } }));
  assert.equal(semToken.status, 400);
  assert.equal(chamadas.length, 0);
  const semJs = await checkout(formulario({ arroba: 'ana', email: 'ana@email.com', autorizo: 'sim', meio: 'cartao' }));
  assert.equal(semJs.status, 303);
  assert.equal(semJs.headers.get('Location'), 'https://www.mercadopago.com.br/checkout/v1/redirect?pref_id=pref-1');
});

test('the page gets the public key only when the variable holds one', async () => {
  const chave = ['APP_USR', '8f2c1a9e', '1b2c', '4d3e', '9f4a', '0123456789ab'].join('-');
  process.env.MP_PUBLIC_KEY = chave;
  assert.equal((await (await aliados()).json()).chave, chave);
  process.env.MP_PUBLIC_KEY = ['APP_USR', '1234567890123456', '102812', '0123456789abcdef0123456789abcdef', '123456789'].join('-');
  assert.equal((await (await aliados()).json()).chave, undefined);
});
