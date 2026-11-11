// The series site at phone width (390 px): screenshots of the top, the vote, the allies and the
// chapters, plus the page width (wider than 390 means horizontal scroll) and any page errors.
//   node site-shot.cjs /absolute/path/to/built/index.html OUT_DIR
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 390, height: 844 }, deviceScaleFactor: 1 });
  const erros = [];
  p.on('pageerror', e => erros.push(String(e)));
  p.on('console', m => { if (m.type() === 'error') erros.push(m.text()); });
  await p.goto('file://' + process.argv[2], { waitUntil: 'load' });
  await p.waitForTimeout(800);
  for (const [id, nome] of [['#inicio', 'topo'], ['#votacao', 'votacao'], ['#aliado', 'aliado'], ['#capitulos', 'capitulos']]) {
    const el = await p.$(id);
    await el.screenshot({ path: process.argv[3] + '/site-' + nome + '.png' });
  }
  const largura = await p.evaluate(() => document.documentElement.scrollWidth);
  console.log('largura da página:', largura, 'erros:', JSON.stringify(erros.filter(e => !e.includes('api/aliados') && !e.includes('ERR_FILE'))));
  await b.close();
})();
