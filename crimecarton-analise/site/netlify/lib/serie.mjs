// What the site sells right now. Change it when a new part opens its list of allies.
export const SERIE = {
  parte: 3,                                // the part whose list is open
  vagas: 10,                               // places on each part's list
  fecha: '2026-10-30T21:00:00-03:00',      // after this, a pass counts for the next part
  inicio: '2026-10-28T00:00:00.000-03:00', // first day of sales: the payments search starts here
  preco: 9.9,                              // R$ per pass
  // Fixes to handles on the list: { errado: 'certo' }, or { ofensivo: '' } to leave one out.
  // teste.golpe is the handle for the creator's own test purchases: no place, no number.
  correcoes: { 'teste.golpe': '' },
};
