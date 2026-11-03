#!/usr/bin/env python3
"""A kit for making Part 4's drawings and voices without Codex, on a phone.

The Codex hit its usage limit twice in the Part 4 request (02 and 03/11/2026). The same work
can be done by hand at no extra cost: the drawings in ChatGPT's own chat, the same image
generator Codex used, and the voices in Google AI Studio, which has the same TTS voices
(Charon and Algenib) and model. This script writes, into a folder:

- folha-1-personagens.jpg and folha-2-lugares.jpg: two reference sheets to attach once in
  ChatGPT, with the characters and with the places and the light of the earlier parts;
- index.html: a page with the opening message for ChatGPT, the 22 scenes of
  ../pedido-codex-ep04.md as messages with a copy button each, and the three voices of the
  pedido-narracao-*.json files, with their style and text. A box per item marks what is done.

    python kit_sem_codex.py SAIDA
"""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
SERIE = EPISODE.parent
PEDIDO = EPISODE / 'pedido-codex-ep04.md'
FONTES = SERIE / 'fontes'
VOZES = [('Narrador', 'pedido-narracao-ep04.json', 'narracao-ep04-narrador'),
         ('Ademir', 'pedido-narracao-ademir-ep04.json', 'narracao-ep04-ademir'),
         ('Renato', 'pedido-narracao-renato-ep04.json', 'narracao-ep04-renato')]

INICIAL = """Vou te pedir 22 ilustrações para a Parte 4 da minha série de desenho “A parte que faltou”, uma por mensagem. Anexei duas folhas de referência: a folha 1 tem os personagens, e a folha 2 tem os lugares e a luz das partes anteriores. Gere sempre uma imagem por mensagem, seguindo estas regras.

FORMATO: vertical 9:16, no maior tamanho possível.

TRAÇO: o mesmo cartoon 2D das referências. Traço limpo e firme, contorno escuro, cores chapadas com sombra pintada suave e texturas sutis. Luz noturna de cinema, com a luz amarela da lâmpada e dos postes, a luz azulada da lua cheia e reflexos no chão molhado.

COMPOSIÇÃO (o vídeo cobre partes da imagem):
- Os 25% de cima ficam só com fundo calmo: céu, teto, parede ou escuro. Nada de rosto, mão, celular ou objeto importante ali.
- Rostos, mãos e a ação principal ficam entre 30% e 60% da altura, no meio da largura.
- Os 20% de baixo ficam só com chão ou fundo.
- A borda direita (os 20% da direita, entre 45% e 80% da altura) fica sem nada importante.

CORPOS: os personagens não podem sair cortados, fundidos ou atravessados pelo cenário. Quando o plano corta o corpo, o corte é da borda do quadro, nunca de um objeto. Mãos e rostos sem deformação: cinco dedos, olhos alinhados, expressões fortes.

VARIEDADE: cada imagem é um plano diferente, como num storyboard.

SEM TEXTO: nada de letras, números, logotipo ou marca d'água, nem em placas de carro e viaturas. A placa do portão e o calendário ficam em branco. Telas de celular ficam acesas, lisas e em branco, numa cor clara uniforme, com os quatro cantos visíveis.

PERSONAGENS (folha 1):
- Zinho: cabelo preto cacheado no topo, laterais em degradê, sem barba. Jaqueta azul-marinho com capuz vermelho e faixas brancas nas mangas, camiseta preta e jeans.
- Renato: jaqueta verde-oliva aberta e suja, camiseta cinza-escuro, barba curta com bigode e cabelo crespo baixo. Tem o lábio cortado e, depois de solto, os pulsos vermelhos da corda.
- Ademir: é o cobrador da folha 1, agora com o rosto à mostra. Uns 60 anos, alto e corpulento, com mãos grandes. Cabelo branco penteado para trás, bigode branco aparado, rugas fundas e olhar calmo. Jaqueta de couro preta, camisa escura, calça escura e tênis escuros. Anel grosso de ouro no dedo médio da mão direita e uma pequena medalha dourada de São Jorge numa corrente fina.
- O motorista do assalto: uns 35 anos, magro, de boné escuro, barba rala, jaqueta corta-vento cinza e jeans.
- O parceiro dos dez milhões: só aparece de costas, de capuz escuro. O rosto nunca aparece.

LUGARES (folha 2): o ferro-velho São Jorge (chão de cimento rachado e molhado, montes de sucata e carcaças de carro, uma cobertura de zinco com uma única lâmpada, lua cheia), o portão de tela dele, um barracão de alvenaria de paredes bege com a mesa de madeira da foto da divisão, o carro escuro (um sedã preto) e o ônibus abandonado.

Agora responda só “Pronto”. Depois eu mando a cena 1."""

LEMBRETE = ('Siga as regras e as duas folhas da primeira mensagem: vertical 9:16, o traço das referências, '
            'nada importante nos 25% de cima nem na borda direita, e nenhum texto na imagem.')


def font(size, weight='Bold'):
    return ImageFont.truetype(str(FONTES / f'Poppins-{weight}.ttf'), size)


def recorte(path, foco, w, h):
    """The part `foco` (fractions) of an image, widened or narrowed to w:h and resized."""
    im = Image.open(path).convert('RGB')
    l, t, r, b = (foco[0]*im.width, foco[1]*im.height, foco[2]*im.width, foco[3]*im.height)
    cx, cy, bw, bh = (l + r)/2, (t + b)/2, r - l, b - t
    if bw/bh > w/h:
        bh = bw*h/w
    else:
        bw = bh*w/h
    caixa = (max(0, cx - bw/2), max(0, cy - bh/2), min(im.width, cx + bw/2), min(im.height, cy + bh/2))
    return im.crop(tuple(round(v) for v in caixa)).resize((w, h), Image.Resampling.LANCZOS)


def folha(itens, colunas, w, h, titulo, saida):
    """Tiles in a grid, each with its label under it, and the sheet's title on top."""
    gap, faixa, topo = 24, 78, 110
    linhas = (len(itens) + colunas - 1)//colunas
    W = colunas*w + (colunas + 1)*gap
    H = topo + linhas*(h + faixa + gap) + gap
    im = Image.new('RGB', (W, H), (14, 18, 26))
    d = ImageDraw.Draw(im)
    d.text((gap, 34), titulo, font=font(46, 'ExtraBold'), fill=(242, 201, 76))
    for k, (path, foco, rotulo) in enumerate(itens):
        c, r = k % colunas, k//colunas
        x, y = gap + c*(w + gap), topo + r*(h + faixa + gap)
        im.paste(recorte(path, foco, w, h), (x, y))
        d.rectangle((x, y + h, x + w, y + h + faixa), fill=(28, 36, 51))
        d.text((x + 18, y + h + faixa/2), rotulo, font=font(30), fill=(237, 240, 245), anchor='lm')
    im.save(saida, quality=88, optimize=True)


def folhas(saida):
    p2, p3 = SERIE / 'episodio-02', SERIE / 'episodio-03'
    # The two character sheets are 3:2; the scenes below them are cut 3:4.
    personagens = Image.new('RGB', (2120, 1880), (14, 18, 26))
    d = ImageDraw.Draw(personagens)
    d.text((24, 34), 'FOLHA 1 · OS PERSONAGENS', font=font(46, 'ExtraBold'), fill=(242, 201, 76))
    for k, (arq, rotulo) in enumerate([('zinho-referencia-v3.png', 'ZINHO'), ('amigo-referencia-v1.png', 'RENATO')]):
        x = 24 + k*1048
        personagens.paste(Image.open(SERIE / arq).convert('RGB').resize((1024, 683), Image.Resampling.LANCZOS), (x, 110))
        d.rectangle((x, 793, x + 1024, 871), fill=(28, 36, 51))
        d.text((x + 18, 832), rotulo, font=font(30), fill=(237, 240, 245), anchor='lm')
    cenas = [(p3 / 'cena-29-cobrador-grava.png', (.45, .28, 1.0, .9), 'ADEMIR · O COBRADOR, AGORA COM ROSTO'),
             (p3 / 'cena-20-anel-gola.png', (.2, .3, .85, .72), 'O ANEL · DEDO MÉDIO, MÃO DIREITA'),
             (p3 / 'cena-05-renato-grita.png', (.05, .2, .95, .8), 'RENATO NUMA CENA')]
    for k, (path, foco, rotulo) in enumerate(cenas):
        x = 24 + k*699
        personagens.paste(recorte(path, foco, 675, 900), (x, 895))
        d.rectangle((x, 1795, x + 675, 1873), fill=(28, 36, 51))
        d.text((x + 16, 1834), rotulo, font=font(25), fill=(237, 240, 245), anchor='lm')
    personagens.save(saida / 'folha-1-personagens.jpg', quality=88, optimize=True)
    folha([(p3 / 'cena-33-renato-sozinho.png', (0, .2, 1, .8), 'O FERRO-VELHO SÃO JORGE'),
           (p3 / 'cena-12-ferro-velho.png', (.1, .15, 1, .75), 'O PORTÃO · PLACA EM BRANCO'),
           (p2 / 'cena-04-foto-divisao.png', (0, .1, 1, .75), 'A MESA E AS BOLSAS DA FOTO'),
           (p3 / 'cena-24-sozinho.png', (0, .1, 1, .85), 'O ÔNIBUS ABANDONADO'),
           (p3 / 'cena-30-casa-da-mae.png', (0, .25, 1, .8), 'O CARRO ESCURO'),
           (p3 / 'cena-26-sucata.png', (0, .2, 1, .8), 'A SUCATA E A LUZ')],
          3, 640, 853, 'FOLHA 2 · OS LUGARES E A LUZ', saida / 'folha-2-lugares.jpg')


def cenas():
    """[(number, file name, line of the script, message for ChatGPT)] from the request."""
    texto = PEDIDO.read_text(encoding='utf-8')
    texto = texto.split('### As 22 cenas', 1)[1].split('### Onde cada imagem entra', 1)[0]
    blocos = re.split(r'\n(?=\d+\. \*\*`)', texto)
    out = []
    for bloco in blocos:
        m = re.match(r'(\d+)\. \*\*`(cena-[\w-]+\.png)`\*\* — “(.+?)”(.*)', bloco.strip(), re.S)
        if not m:
            continue
        n, nome, fala, resto = int(m[1]), m[2], m[3], m[4]
        linhas = []
        for item in re.findall(r'- \*\*(.+?):\*\* (.+)', resto):
            linhas.append(f'{item[0]}: {item[1]}')
        corpo = '\n'.join(linhas).replace('**', '')
        out.append((n, nome, fala, f'Cena {n} de 22. A fala que ela ilustra: “{fala}”\n\n{corpo}\n\n{LEMBRETE}'))
    if len(out) != 22:
        raise ValueError(f'{PEDIDO.name}: {len(out)} cenas, não 22')
    return out


def vozes():
    out = []
    for quem, arq, saida in VOZES:
        dados = json.loads((EPISODE / arq).read_text(encoding='utf-8'))
        out.append((quem, dados['voice'], dados['style'], dados['text'], saida))
    return out


def bloco_copia(chave, rotulo, texto, ver='Ver o texto'):
    return (f'<button class="copy" type="button" data-copy="{chave}">{html.escape(rotulo)}</button>'
            f'<details><summary>{ver}</summary>'
            f'<textarea id="{chave}" readonly rows="8">{html.escape(texto)}</textarea></details>')


def pagina(saida):
    lista = cenas()
    vs = vozes()
    itens_cena = []
    for n, nome, fala, msg in lista:
        itens_cena.append(f'''<li class="card item" data-id="cena-{n}">
  <div class="row"><span class="num">{n}</span><code>{html.escape(nome)}</code>
  <label class="feito"><input type="checkbox" id="feito-cena-{n}"> Feita</label></div>
  <p class="fala">“{html.escape(fala)}”</p>
  {bloco_copia(f"t-cena-{n}", f"Copiar a cena {n}", msg, "Ver a mensagem")}
</li>''')
    itens_voz = []
    for k, (quem, voz, estilo, texto, arquivo) in enumerate(vs, 1):
        itens_voz.append(f'''<li class="card item" data-id="voz-{k}">
  <div class="row"><span class="voz">{html.escape(quem)}</span><span class="chip">voz {html.escape(voz)}</span>
  <label class="feito"><input type="checkbox" id="feito-voz-{k}"> Feita</label></div>
  <p class="meta">Arquivo: <code>{arquivo}.wav</code></p>
  <div class="dupla">{bloco_copia(f"t-estilo-{k}", "Copiar o estilo", estilo, "Ver o estilo")}</div>
  <div class="dupla">{bloco_copia(f"t-texto-{k}", "Copiar o texto", texto)}</div>
</li>''')
    doc = PAGINA.replace('{{INICIAL}}', bloco_copia('t-inicial', 'Copiar a mensagem inicial', INICIAL, 'Ver a mensagem'))
    doc = doc.replace('{{CENAS}}', '\n'.join(itens_cena)).replace('{{VOZES}}', '\n'.join(itens_voz))
    (saida / 'index.html').write_text(doc, encoding='utf-8')


PAGINA = r'''<title>Kit da Parte 4</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=JetBrains+Mono:wght@500&family=Poppins:wght@700;800&display=swap">
<style>
/* One column for a phone: the series' yellow tags mark each step; every scene is a card with one big copy button. */
:root {
  --bg: #0e121a; --surface: #151b26; --raised: #1d2534; --line: #283246;
  --fg: #edf0f5; --muted: #9aa3b6; --tag: #f2c94c; --tag-ink: #1b1507;
  --accent-text: #f2c94c; --ok: #3fbf7f; --alert: #e8584c;
  --display: 'Poppins', 'Avenir Next', 'Segoe UI', sans-serif;
  --body: 'Atkinson Hyperlegible', 'Segoe UI', system-ui, sans-serif;
  --mono: 'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, monospace;
  color-scheme: dark;
}
@media (prefers-color-scheme: light) {
  :root:not([data-theme="dark"]) {
    --bg: #f2f3f6; --surface: #ffffff; --raised: #f6f7fa; --line: #d8dce5;
    --fg: #151922; --muted: #586174; --accent-text: #8a6400; --ok: #1d8a55; --alert: #c43c30;
    color-scheme: light;
  }
}
:root[data-theme="light"] {
  --bg: #f2f3f6; --surface: #ffffff; --raised: #f6f7fa; --line: #d8dce5;
  --fg: #151922; --muted: #586174; --accent-text: #8a6400; --ok: #1d8a55; --alert: #c43c30;
  color-scheme: light;
}
body { background: var(--bg); color: var(--fg); font-family: var(--body); font-size: 17px; line-height: 1.5; }
.wrap { max-width: 680px; margin: 0 auto; padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px)); padding-block: 28px 56px; display: grid; gap: 34px; }
header { display: grid; gap: 12px; }
.tag { justify-self: start; background: var(--tag); color: var(--tag-ink); font-family: var(--display); font-weight: 800;
  font-size: 13px; letter-spacing: .06em; text-transform: uppercase; padding: 5px 11px; border-radius: 7px; }
h1 { font-family: var(--display); font-weight: 800; font-size: clamp(30px, 8vw, 42px); line-height: 1.08; margin: 0; text-wrap: balance; }
h2 { font-family: var(--display); font-weight: 700; font-size: 22px; line-height: 1.2; margin: 0; text-wrap: balance; }
p { margin: 0; }
.lead { color: var(--muted); max-width: 60ch; }
.progresso { display: grid; gap: 6px; font-variant-numeric: tabular-nums; }
.barra { height: 8px; background: var(--raised); border: 1px solid var(--line); border-radius: 99px; overflow: hidden; }
.barra span { display: block; height: 100%; width: 0; background: var(--ok); }
section { display: grid; gap: 14px; }
.passo { font-family: var(--display); font-weight: 800; color: var(--accent-text); font-size: 13px; letter-spacing: .08em; text-transform: uppercase; }
ol.como { margin: 0; padding-left: 1.3em; display: grid; gap: 8px; }
ul.lista { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 12px; padding: 14px 16px; display: grid; gap: 10px; min-width: 0; }
.row { display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
.num { flex: none; width: 34px; height: 34px; border-radius: 50%; background: var(--tag); color: var(--tag-ink);
  display: grid; place-items: center; font-family: var(--display); font-weight: 800; font-size: 15px; }
code { font-family: var(--mono); font-size: 13px; color: var(--muted); overflow-wrap: anywhere; min-width: 0; }
.voz { font-family: var(--display); font-weight: 800; font-size: 18px; }
.chip { font-size: 13px; border: 1px solid var(--line); background: var(--raised); padding: 2px 9px; border-radius: 99px; color: var(--muted); }
.feito { margin-left: auto; display: flex; align-items: center; gap: 6px; font-size: 15px; color: var(--muted); }
.feito input { width: 22px; height: 22px; accent-color: var(--ok); }
.fala { font-size: 18px; }
.meta { font-size: 15px; color: var(--muted); }
.copy { width: 100%; min-height: 48px; border-radius: 10px; border: 1px solid var(--line); background: var(--raised);
  color: var(--fg); font-family: var(--display); font-weight: 700; font-size: 16px; cursor: pointer; }
.copy:focus-visible, summary:focus-visible, .feito input:focus-visible { outline: 3px solid var(--tag); outline-offset: 2px; }
.copy.ok { border-color: var(--ok); color: var(--ok); }
.copy.aviso { border-color: var(--alert); color: var(--alert); }
details summary { cursor: pointer; color: var(--muted); font-size: 15px; padding-block: 2px; }
textarea { width: 100%; box-sizing: border-box; margin-top: 8px; background: var(--bg); color: var(--fg); border: 1px solid var(--line);
  border-radius: 8px; padding: 10px; font-family: var(--body); font-size: 15px; line-height: 1.45; resize: vertical; }
.item.done { opacity: .55; }
.item.done .num { background: var(--ok); }
.dupla { display: grid; gap: 6px; }
.folhas { display: grid; gap: 14px; }
.folhas figure { margin: 0; display: grid; gap: 6px; }
.folhas img { width: 100%; max-width: 100%; height: auto; border-radius: 10px; border: 1px solid var(--line); }
figcaption { font-size: 15px; color: var(--muted); }
.nota { font-size: 15px; color: var(--muted); }
@media (prefers-reduced-motion: no-preference) { .copy, .item { transition: opacity .2s, border-color .2s, color .2s; } }
</style>

<div class="wrap">
<header>
  <span class="tag">Parte 4 · O dono do anel</span>
  <h1>Kit da Parte 4</h1>
  <p class="lead">O Codex só volta na quinta. Com este kit, você faz os 22 desenhos no ChatGPT e as 3 vozes no Google AI Studio, sem custo extra, e me manda tudo na conversa.</p>
  <div class="progresso"><span id="contagem">Cenas 0 de 22 · Vozes 0 de 3</span><div class="barra"><span id="barra"></span></div></div>
</header>

<section>
  <span class="passo">Como fazer</span>
  <ol class="como">
    <li>Salve as duas folhas de referência abaixo. Também mandei as duas na conversa.</li>
    <li>No ChatGPT, abra uma conversa nova, anexe as duas folhas e cole a mensagem inicial.</li>
    <li>Mande as 22 cenas, uma por vez, na mesma conversa. Salve cada imagem.</li>
    <li>No Google AI Studio, gere as 3 vozes.</li>
    <li>Mande as imagens e os áudios para o Claude, na conversa da série.</li>
  </ol>
</section>

<section>
  <span class="passo">1 · As referências</span>
  <h2>Duas folhas para anexar no ChatGPT</h2>
  <div class="folhas">
    <figure><img src="folha-1-personagens.jpg" alt="Folha 1: Zinho, Renato, o cobrador, o anel e o Renato numa cena da Parte 3"><figcaption>Folha 1 · os personagens</figcaption></figure>
    <figure><img src="folha-2-lugares.jpg" alt="Folha 2: o ferro-velho, o portão, a mesa da foto, o ônibus, o carro escuro e a sucata"><figcaption>Folha 2 · os lugares e a luz</figcaption></figure>
  </div>
  <p class="nota">Para salvar, toque e segure na imagem.</p>
</section>

<section>
  <span class="passo">2 · A mensagem inicial</span>
  <h2>Cole com as duas folhas anexadas</h2>
  <div class="card">{{INICIAL}}</div>
</section>

<section>
  <span class="passo">3 · As 22 cenas</span>
  <h2>Uma mensagem por imagem</h2>
  <p class="nota">Se a imagem sair com texto, com o corpo cortado ou com o rosto lá no alto, peça de novo no ChatGPT, dizendo o que corrigir.</p>
  <ul class="lista">
{{CENAS}}
  </ul>
</section>

<section>
  <span class="passo">4 · As vozes</span>
  <h2>No Google AI Studio</h2>
  <ol class="como">
    <li>Abra aistudio.google.com e entre com a sua conta Google.</li>
    <li>Abra a parte de gerar fala, chamada “Generate speech” ou “Speech”.</li>
    <li>Deixe uma voz só e escolha a voz de cada cartão. Se der para escolher o modelo, use o Gemini 3.8 Flash TTS.</li>
    <li>Cole o estilo no campo de instruções e o texto no campo do texto. Gere, ouça e baixe o áudio.</li>
  </ol>
  <ul class="lista">
{{VOZES}}
  </ul>
</section>

<section>
  <span class="passo">5 · Me mandar</span>
  <h2>De volta para o Claude</h2>
  <p>Mande as imagens na conversa da série, na ordem, dizendo os números, por exemplo “cenas 1 a 5”. Pode mandar várias por mensagem. Depois, mande os 3 áudios dizendo qual é qual. Eu confiro tudo, salvo no GitHub e monto a Parte 4.</p>
</section>
</div>

<script>
(function () {
  var CHAVE = 'kit-parte-4-feito';
  var feitos = {};
  try { feitos = JSON.parse(localStorage.getItem(CHAVE) || '{}') || {}; } catch (e) { feitos = {}; }
  function salvar() { try { localStorage.setItem(CHAVE, JSON.stringify(feitos)); } catch (e) {} }
  function atualizar() {
    var cenas = 0, vozes = 0;
    document.querySelectorAll('.item').forEach(function (li) {
      var id = li.getAttribute('data-id');
      var marcado = !!feitos[id];
      li.classList.toggle('done', marcado);
      if (marcado) { if (id.indexOf('cena') === 0) cenas++; else vozes++; }
    });
    document.getElementById('contagem').textContent = 'Cenas ' + cenas + ' de 22 · Vozes ' + vozes + ' de 3';
    document.getElementById('barra').style.width = Math.round(100 * (cenas + vozes) / 25) + '%';
  }
  document.querySelectorAll('.item').forEach(function (li) {
    var id = li.getAttribute('data-id');
    var caixa = li.querySelector('.feito input');
    caixa.checked = !!feitos[id];
    caixa.addEventListener('change', function () { feitos[id] = caixa.checked; salvar(); atualizar(); });
  });
  document.querySelectorAll('.copy').forEach(function (botao) {
    var original = botao.textContent;
    botao.addEventListener('click', function () {
      var area = document.getElementById(botao.getAttribute('data-copy'));
      function mostrar(texto, classe) {
        botao.textContent = texto; botao.classList.add(classe);
        setTimeout(function () { botao.textContent = original; botao.classList.remove(classe); }, 2200);
      }
      function manual() {
        area.closest('details').open = true; area.focus(); area.select();
        mostrar('Texto selecionado: toque em Copiar', 'aviso');
      }
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(area.value).then(function () { mostrar('Copiado ✓', 'ok'); }, manual);
      } else { manual(); }
    });
  });
  atualizar();
})();
</script>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('saida', type=Path)
    args = parser.parse_args()
    args.saida.mkdir(parents=True, exist_ok=True)
    folhas(args.saida)
    pagina(args.saida)
    print(f'{args.saida}: index.html, folha-1-personagens.jpg, folha-2-lugares.jpg')


if __name__ == '__main__':
    main()
