// What the site sells right now. Change it when a new part opens its list of allies.
export const SERIE = {
  // Closed since 07/11/2026, by the creator's choice: Part 5 comes out without allies. To open a
  // part's list, set vendas to true, its part and its deadline, and show the form on the page.
  vendas: false,                           // false: /api/checkout sells no pass
  parte: 6,                                // the part whose list opens next
  vagas: 30,                               // places on each part's list
  fecha: null,                             // the list's deadline, e.g. '2026-11-20T21:00:00-03:00';
                                           // after it, a pass counts for the next part
  inicio: '2026-10-28T00:00:00.000-03:00', // first day of sales: the payments search starts here
  preco: 9.9,                              // R$ per pass
  // Fixes to handles on the list: { errado: 'certo' }, or { ofensivo: '' } to leave one out.
  // teste.golpe is the handle for the creator's own test purchases: no place, no number.
  correcoes: { 'teste.golpe': '' },
};
