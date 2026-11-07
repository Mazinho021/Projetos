/*!
 * Abertura vintage · Mat Cookies & Coffee
 *
 * Como usar: coloque esta linha logo depois da tag <body> do site
 *   <script src="abertura-mat.js"></script>
 *
 * Para mudar textos ou regras sem mexer neste arquivo, defina antes dele:
 *   <script>window.MAT_ABERTURA = { umaVezPorSessao: false, frase: 'Outra frase' };</script>
 *
 * Fontes embutidas: Yesteryear, Fraunces e Josefin Sans (SIL Open Font License 1.1)
 * e Special Elite (Apache License 2.0). As licenças acompanham o projeto, em fonte/fontes/.
 */
(function () {
  'use strict';
  if (window.MatAbertura) return;

  var PADRAO = {
    nome: 'Mat',
    faixa: 'Cookies & Coffee',
    anelTopo: 'Feito com carinho',
    anelBase: 'Quentinho do forno',
    carimbo: ['Fornada', '— do dia —'],
    saudacao: 'Seja bem-vindo',
    frase: 'Pode entrar, o café está passando…',
    umaVezPorSessao: true,
    botaoPular: true
  };
  var config = {};
  var chave;
  for (chave in PADRAO) config[chave] = PADRAO[chave];
  var doUsuario = window.MAT_ABERTURA || {};
  for (chave in doUsuario) config[chave] = doUsuario[chave];

  var ESTILO = "__CSS__";
  var SVG = "__SVG__";
  var DURACAO = 7.1;      // segundos até a abertura sair da tela
  var FIM_DO_VIDEO = 6.6; // íris fechada há 0,35 s: ponto final do vídeo exportado
  var CHAVE_SESSAO = 'mat-abertura-vista';
  var CANTO = '<div class="ma-canto ma-canto-{n}"><svg viewBox="0 0 50 50" aria-hidden="true" focusable="false">' +
    '<path class="ma-canto-arco" pathLength="1" d="M 0,36 A 36,36 0 0 0 36,0"/>' +
    '<path class="ma-canto-arco" pathLength="1" d="M 0,29 A 29,29 0 0 0 29,0"/>' +
    '<path class="ma-canto-losango" d="M 10,3 L 17,10 L 10,17 L 3,10 Z"/></svg></div>';

  var doc = document;
  var raiz = doc.documentElement;
  var exportar = !!window.MAT_ABERTURA_EXPORTAR;
  var forcar = /[?&]abertura(=|&|$)/.test(location.search);
  var reduzido = !!(window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches);
  var atual = null;

  function esc(texto) {
    return String(texto).replace(/[&<>"]/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c];
    });
  }
  function maiusculas(texto) {
    return String(texto).toLocaleUpperCase('pt-BR');
  }
  function jaViu() {
    try { return sessionStorage.getItem(CHAVE_SESSAO) === '1'; } catch (e) { return false; }
  }
  function marcarVisto() {
    try { sessionStorage.setItem(CHAVE_SESSAO, '1'); } catch (e) { /* navegação privada */ }
  }
  // sorteio com semente fixa: a frase "batida à máquina" sai sempre igual
  function sorteio(semente) {
    return function () {
      semente |= 0;
      semente = semente + 0x6D2B79F5 | 0;
      var t = Math.imul(semente ^ semente >>> 15, 1 | semente);
      t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
      return ((t ^ t >>> 14) >>> 0) / 4294967296;
    };
  }

  function injetarEstilo() {
    if (doc.getElementById('mat-abertura-estilo')) return;
    var estilo = doc.createElement('style');
    estilo.id = 'mat-abertura-estilo';
    estilo.textContent = ESTILO;
    (doc.head || raiz).appendChild(estilo);
  }

  function svgPreenchido() {
    var letras = Array.from(String(config.nome)).map(function (letra, i) {
      return '<tspan class="ma-letra" style="--i:' + i + '">' + esc(letra) + '</tspan>';
    }).join('');
    var carimbo = [].concat(config.carimbo);
    var valores = {
      anelTopo: esc(maiusculas(config.anelTopo)),
      anelBase: esc(maiusculas(config.anelBase)),
      nome: esc(config.nome),
      nomeLetras: letras,
      faixa: esc(maiusculas(config.faixa)),
      carimbo1: esc(maiusculas(carimbo[0] || '')),
      carimbo2: esc(maiusculas(carimbo[1] || ''))
    };
    return SVG.replace(/\{\{(\w+)\}\}/g, function (tudo, nome) {
      return nome in valores ? valores[nome] : '';
    });
  }

  function baterFrase(alvo, texto) {
    var rnd = sorteio(20261107);
    var letras = Array.from(String(texto));
    letras.forEach(function (c, i) {
      var s = doc.createElement('span');
      s.className = 'ma-tecla' + (i === letras.length - 1 ? ' ma-ultima' : '');
      s.textContent = c;
      s.style.setProperty('--i', i);
      s.style.setProperty('--y', ((rnd() - 0.5) * 0.08).toFixed(3) + 'em');
      s.style.setProperty('--r', ((rnd() - 0.5) * 3.2).toFixed(2) + 'deg');
      s.style.setProperty('--o', (0.8 + rnd() * 0.2).toFixed(2));
      alvo.appendChild(s);
    });
  }

  function montar() {
    var el = doc.createElement('div');
    el.className = 'mat-abertura';
    if (reduzido && !exportar) el.className += ' ma-reduzido';
    if (exportar) el.className += ' ma-exportar';
    if (!(window.CSS && window.CSS.registerProperty)) el.className += ' ma-sem-iris';
    el.innerHTML =
      '<div class="ma-cena" aria-hidden="true">' +
        '<div class="ma-raios"></div>' +
        '<div class="ma-manchas"></div>' +
        '<div class="ma-linha ma-linha-t"></div><div class="ma-linha ma-linha-b"></div>' +
        '<div class="ma-linha ma-linha-l"></div><div class="ma-linha ma-linha-r"></div>' +
        CANTO.replace('{n}', '1') + CANTO.replace('{n}', '2') + CANTO.replace('{n}', '3') + CANTO.replace('{n}', '4') +
        '<div class="ma-topo"><span>' + esc(config.saudacao) + '</span></div>' +
        svgPreenchido() +
        '<div class="ma-frase"></div>' +
        '<div class="ma-papel-sobre"></div>' +
        '<div class="ma-desgaste"></div>' +
        '<div class="ma-grao"></div>' +
        '<div class="ma-risco ma-risco-1"></div><div class="ma-risco ma-risco-2"></div>' +
        '<div class="ma-poeira ma-poeira-1"></div><div class="ma-poeira ma-poeira-2"></div>' +
        '<div class="ma-luz"></div>' +
        '<div class="ma-vinheta"></div>' +
        '<div class="ma-escuro"></div>' +
      '</div>' +
      '<div class="ma-iris"></div>' +
      (config.botaoPular && !exportar
        ? '<button type="button" class="ma-pular" aria-label="Pular a abertura">Pular <span aria-hidden="true">›</span></button>'
        : '');
    baterFrase(el.querySelector('.ma-frase'), config.frase);
    return el;
  }

  function carregarFontes() {
    if (!doc.fonts || !doc.fonts.load) return Promise.resolve();
    var fontes = ['232px "MatAb Letreiro"', '900 62px "MatAb Faixa"', '700 54px "MatAb Anel"', '28px "MatAb Maquina"'];
    var todas = Promise.all(fontes.map(function (f) {
      return doc.fonts.load(f).catch(function () {});
    }));
    var limite = new Promise(function (ok) { setTimeout(ok, 2500); });
    return Promise.race([todas, limite]);
  }

  function doisQuadros() {
    return new Promise(function (ok) {
      requestAnimationFrame(function () { requestAnimationFrame(ok); });
    });
  }

  function soltarRolagem() {
    raiz.classList.remove('ma-trava');
  }

  function encerrar(el) {
    if (!el || !el.parentNode) return;
    el.parentNode.removeChild(el);
    if (atual === el) atual = null;
    soltarRolagem();
    try { window.dispatchEvent(new CustomEvent('mat-abertura:fim')); } catch (e) { /* navegador antigo */ }
  }

  function sair(el) {
    if (!el || !el.parentNode || el.classList.contains('ma-saindo')) return;
    soltarRolagem();
    el.classList.add('ma-saindo');
    setTimeout(function () { encerrar(el); }, 500);
  }

  function tocar() {
    if (atual) encerrar(atual);
    injetarEstilo();
    raiz.classList.remove('ma-pre-abertura');
    var el = montar();
    atual = el;
    doc.body.appendChild(el);
    if (!exportar) raiz.classList.add('ma-trava');

    var botao = el.querySelector('.ma-pular');
    if (botao) botao.addEventListener('click', function () { sair(el); });

    return carregarFontes().then(doisQuadros).then(function () {
      if (!el.parentNode) return;
      el.classList.add('ma-tocar');

      if (exportar) {
        irPara(0);
        return;
      }
      if (reduzido) {
        setTimeout(function () { sair(el); }, 1800);
        return;
      }
      var iris = el.querySelector('.ma-iris');
      iris.addEventListener('animationstart', function (e) {
        if (e.animationName === 'ma-iris-abre') soltarRolagem();
      });
      iris.addEventListener('animationend', function (e) {
        if (e.animationName === 'ma-iris-abre') encerrar(el);
      });
      el.querySelector('.ma-cena').addEventListener('animationend', function (e) {
        if (e.animationName === 'ma-esmaece') encerrar(el);
      });
      // garantia: nunca deixa o site preso atrás da abertura
      setTimeout(function () { encerrar(el); }, (DURACAO + 2) * 1000);
    });
  }

  // posiciona toda a animação num instante exato (usado para gravar o vídeo)
  function irPara(segundos) {
    if (!atual || !atual.getAnimations) return;
    atual.getAnimations({ subtree: true }).forEach(function (a) {
      a.pause();
      a.currentTime = segundos * 1000;
    });
  }

  var pronto = null;
  function iniciar() {
    if (!exportar) marcarVisto();
    pronto = tocar();
    api.pronto = pronto;
  }

  var api = {
    tocar: function () { pronto = tocar(); api.pronto = pronto; return pronto; },
    pular: function () { if (atual) sair(atual); },
    irPara: irPara,
    duracao: DURACAO,
    fimDoVideo: FIM_DO_VIDEO,
    config: config,
    pronto: null
  };
  window.MatAbertura = api;

  var mostrar = exportar || forcar || !(config.umaVezPorSessao && jaViu());
  if (!mostrar) return;

  injetarEstilo();
  if (doc.body) {
    iniciar();
  } else {
    raiz.classList.add('ma-pre-abertura');
    doc.addEventListener('DOMContentLoaded', iniciar);
  }
})();
