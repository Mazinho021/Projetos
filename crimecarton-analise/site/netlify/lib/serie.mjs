// What the site sells right now. Change it when a new part opens its list of allies.
export const SERIE = {
  // Since 07/11/2026, by the creator's choice, Part 5 comes out without allies: the open list is
  // Part 6's. On 08/11/2026 he set its deadline: Monday 09/11, at noon. vendas: false makes
  // /api/checkout sell no pass at all.
  vendas: true,
  parte: 6,                                // the part whose list is open
  vagas: 30,                               // places on each part's list
  fecha: '2026-11-09T12:00:00-03:00',      // the list's deadline; after it, a pass counts for the
                                           // next part (null: no deadline)
  inicio: '2026-10-28T00:00:00.000-03:00', // first day of sales: the payments search starts here
  preco: 9.9,                              // R$ per pass
  // Fixes to handles on the list: { errado: 'certo' }, or { ofensivo: '' } to leave one out.
  // teste.golpe is the handle for the creator's own test purchases: no place, no number.
  correcoes: { 'teste.golpe': '' },
};
