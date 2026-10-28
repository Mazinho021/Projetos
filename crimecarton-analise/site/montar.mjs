// Builds dist/ for Netlify: index.html wrapped in a full HTML document, with the tags that
// link previews and browsers read, plus the images. The preview on Claude wraps the page by
// itself, so index.html stays without <html>, <head> and <body>.
// Netlify runs it on every deploy; by hand: node montar.mjs (from this folder).
import { cpSync, mkdirSync, readFileSync, rmSync, writeFileSync } from 'node:fs';

const site = (process.env.URL || 'https://golpecartoon.netlify.app').replace(/\/$/, '');
const pagina = readFileSync('index.html', 'utf8');
const corte = pagina.indexOf('</style>') + '</style>'.length;
const cabeca = pagina.slice(0, corte).replace(/<meta name="claude:viewport-fit-sides"[^>]*>\n?/, '');
const corpo = pagina.slice(corte).trim();
const titulo = cabeca.match(/<title>([^<]*)<\/title>/)[1];
const descricao = cabeca.match(/<meta name="description" content="([^"]*)"/)[1];

const html = `<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#140e0b">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Golpe Cartoon">
<meta property="og:title" content="${titulo}">
<meta property="og:description" content="${descricao}">
<meta property="og:url" content="${site}/">
<meta property="og:image" content="${site}/img/compartilhar.jpg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" sizes="32x32" href="/img/icone-32.png">
<link rel="apple-touch-icon" href="/img/icone-180.png">
<style>:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}img{max-width:100%}[hidden]{display:none!important}</style>
${cabeca}
</head>
<body>
${corpo}
</body>
</html>
`;

rmSync('dist', { recursive: true, force: true });
mkdirSync('dist');
writeFileSync('dist/index.html', html);
cpSync('img', 'dist/img', { recursive: true });
console.log(`dist/index.html, ${html.length} bytes, for ${site}`);
