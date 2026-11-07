// Grava a abertura em vídeo MP4 ou tira quadros soltos para conferir.
//
// Vídeo:   node exportar_video.js <previa.html> <saida-sem-extensao> <largura> <altura> [fps]
// Quadros: node exportar_video.js <previa.html> <pasta> <largura> <altura> --quadros 0.5,2,4.6
//
// A página é aberta com window.MAT_ABERTURA_EXPORTAR = true: a abertura fica
// parada e cada quadro é posicionado no instante exato com MatAbertura.irPara().
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const [html, saida, larg, alt, ...resto] = process.argv.slice(2);
const largura = parseInt(larg, 10);
const altura = parseInt(alt, 10);
const iq = resto.indexOf('--quadros');
const quadros = iq >= 0 ? resto[iq + 1].split(',').map(Number) : null;
const fps = iq >= 0 ? 30 : parseInt(resto[0] || '30', 10);
const escala = parseFloat(process.env.ESCALA || '1');

async function abrir() {
  const navegador = await chromium.launch();
  const pagina = await navegador.newPage({ viewport: { width: largura, height: altura }, deviceScaleFactor: escala });
  await pagina.addInitScript(() => { window.MAT_ABERTURA_EXPORTAR = true; });
  await pagina.goto('file://' + path.resolve(html));
  await pagina.waitForFunction(() => window.MatAbertura && window.MatAbertura.pronto);
  await pagina.evaluate(() => window.MatAbertura.pronto);
  return { navegador, pagina };
}

async function posicionar(pagina, t) {
  await pagina.evaluate((s) => new Promise((ok) => {
    window.MatAbertura.irPara(s);
    requestAnimationFrame(() => requestAnimationFrame(ok));
  }), t);
}

async function tirarQuadros() {
  fs.mkdirSync(saida, { recursive: true });
  const { navegador, pagina } = await abrir();
  for (const t of quadros) {
    await posicionar(pagina, t);
    const nome = path.join(saida, `quadro-${largura}x${altura}-${t.toFixed(2)}s.png`);
    await pagina.screenshot({ path: nome });
    console.log(nome);
  }
  await navegador.close();
}

async function gravarVideo() {
  const { navegador, pagina } = await abrir();
  const fim = await pagina.evaluate(() => window.MatAbertura.fimDoVideo);
  const total = Math.round(fim * fps);
  const ffmpeg = spawn('ffmpeg', [
    '-y', '-loglevel', 'error',
    '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'png', '-i', '-',
    // MP4 (H.264): toca em qualquer navegador e construtor de sites
    '-map', '0', '-c:v', 'libx264', '-preset', 'slow', '-crf', '27', '-pix_fmt', 'yuv420p',
    '-movflags', '+faststart', '-r', String(fps), saida + '.mp4',
  ], { stdio: ['pipe', 'inherit', 'inherit'] });
  const terminou = new Promise((ok, erro) => ffmpeg.on('close', (c) => (c === 0 ? ok() : erro(new Error('ffmpeg ' + c)))));

  for (let i = 0; i < total; i++) {
    await posicionar(pagina, i / fps);
    const png = await pagina.screenshot({ type: 'png' });
    if (!ffmpeg.stdin.write(png)) await new Promise((ok) => ffmpeg.stdin.once('drain', ok));
    if (i % 30 === 0) process.stdout.write(`quadro ${i}/${total}\n`);
  }
  ffmpeg.stdin.end();
  await terminou;
  await navegador.close();
  console.log('ok', saida + '.mp4', total, 'quadros');
}

(quadros ? tirarQuadros() : gravarVideo()).catch((e) => { console.error(e); process.exit(1); });
