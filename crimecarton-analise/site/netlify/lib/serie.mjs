// What the site sells right now. Change it when a new part opens its list of allies.
export const SERIE = {
  // Part 6's list closed on 09/11/2026 at noon, with no allies. Since 10/11/2026 the open list is
  // Part 7's, with no deadline yet. vendas: false makes /api/checkout sell no pass at all.
  vendas: true,
  parte: 7,                                // the part whose list is open
  vagas: 30,                               // places on each part's list
  fecha: null,                             // the list's deadline, e.g. '2026-11-20T12:00:00-03:00';
                                           // after it, a pass counts for the next part
  inicio: '2026-10-28T00:00:00.000-03:00', // first day of sales: the payments search starts here
  preco: 9.9,                              // R$ per pass
  // Fixes to handles on the list: { errado: 'certo' }, or { ofensivo: '' } to leave one out.
  // teste.golpe is the handle for the creator's own test purchases: no place, no number.
  correcoes: { 'teste.golpe': '' },
};
