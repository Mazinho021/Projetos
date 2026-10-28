// Who the allies are, read from the payments themselves, so there is no list to keep in sync.
// A pass is a payment whose external_reference is "aliado|<part>|<handle>".

const NA_LISTA = new Set(['approved', 'in_mediation']);
// A refunded pass keeps its number, so nobody's number moves when someone gets their money back.
const COM_NUMERO = new Set([...NA_LISTA, 'refunded', 'charged_back']);

export function referencia(parte, arroba) {
  return `aliado|${parte}|${arroba}`;
}

export function montarLista(pagamentos, vagas, correcoes = {}) {
  const passes = [];
  for (const p of pagamentos) {
    let [tipo, parte, arroba] = String(p.external_reference || '').split('|');
    if (arroba && Object.hasOwn(correcoes, arroba)) arroba = correcoes[arroba];
    const quando = Date.parse(p.date_approved || '');
    if (tipo !== 'aliado' || !arroba || !COM_NUMERO.has(p.status) || Number.isNaN(quando)) continue;
    passes.push({ arroba, parte: Number(parte), vale: NA_LISTA.has(p.status), quando });
  }
  passes.sort((a, b) => a.quando - b.quando);

  // Numbers follow each handle's first approved pass, across all parts.
  const numeros = new Map();
  for (const x of passes) if (!numeros.has(x.arroba)) numeros.set(x.arroba, numeros.size + 1);

  // A pass goes on the list of the part it was bought for or, when that list is full, the next one.
  const partes = new Map();
  const lista = n => partes.get(n) ?? partes.set(n, []).get(n);
  for (const x of passes) {
    if (!x.vale) continue;
    let n = x.parte;
    while (lista(n).length >= vagas && !lista(n).includes(x.arroba)) n += 1;
    if (!lista(n).includes(x.arroba)) lista(n).push(x.arroba);
  }
  return { numeros, partes };
}

// The part a pass bought now counts for: the open one, or the next after the deadline or when full.
export function parteDaCompra(serie, agora, partes) {
  let n = agora > Date.parse(serie.fecha) ? serie.parte + 1 : serie.parte;
  while ((partes.get(n) || []).length >= serie.vagas) n += 1;
  return n;
}
