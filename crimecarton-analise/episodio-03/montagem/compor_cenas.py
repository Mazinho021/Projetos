#!/usr/bin/env python3
"""Part 3's images that the edit makes from Codex's drawings, most of them with the allies' @.

The ally pass promises the @ "no celular dele, num muro, na TV ou nos créditos"; this script puts
them there. Writes, in arte/:

- beco-pichado.png: the alley of scene 4 with the @ sprayed on its wall, in the wall's
  perspective and light, behind the two men (arte/beco-pessoas.png, their cut-out mask);
- tv-bar-plantao.png and bar-plantao.png: the news on the bar's TV, close (scene 7) and in the
  wide shot (scene 6): the portraits of Zinho and, for the first time, Renato, "PROCURADOS" and
  the viewers' comments, with the @;
- conversa.png: Renato's chat with "Cobrança" on his phone, from "Tô chegando na casa dele." at
  23:31 to "Cadê vocês?";
- celular-notificacoes.png: Zinho's phone (scene 8) full of messages, from the allies and from
  numbers he does not know;
- escolha.png: the junkyard and the mother's house side by side, for the vote;
- creditos.png: the allies with their numbers, for the credits, when there are any.

The allies come from aliados-parte-03.json; --buscar fills it from the site once the places close.
Without allies, the wall, the TV and the phone keep only what is not anyone's @.

    python compor_cenas.py [--buscar]
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import random
import sys
import urllib.request

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
SERIE = EPISODE.parent
sys.path.insert(0, str(SERIE / 'episodio-01' / 'montagem'))
import graficos  # noqa: E402
from render_animatic import perspective  # noqa: E402

ARTE = HERE / 'arte'
ALIADOS = HERE / 'aliados-parte-03.json'
SITE = 'https://golpecartoon.netlify.app/api/aliados'
NOITE = ('quarta-feira, 28 de outubro', '00:09')   # minutes after Part 2's "23:47"

# The alley's wall in scene 4, as a plane: its corners near the camera (left) and where it
# meets the gate (right), top and bottom.
MURO = [(0, 60), (470, 465), (470, 1150), (0, 1280)]
TINTAS = [(214, 52, 44), (24, 22, 20), (38, 74, 168), (236, 182, 36), (36, 128, 72)]
# Where the tags go on the flat wall (1400 × 1000): the middle, the largest size and the turn. They stay
# where the wall shows, from x ≈ 40 to 380 and y ≈ 270 to 900 of the drawing.
LUGARES = [(.20, .44, 92, 4), (.30, .24, 86, -3), (.22, .64, 88, -2), (.48, .52, 74, -5), (.46, .10, 76, 3)]
MENOR = 46          # a tag that only fits smaller than this goes to the TV or the phone instead
MURO_X = (15, 400)  # the tags stay between these x of the drawing
# The wall is seen at a grazing angle, which squeezes a tag to a third of its width. Each tag is
# drawn wider first, by this share of the squeeze, so it keeps the wall's slant and stays readable.
ALARGA = .8
SEM_ALIADOS = ['ZINHO', '@golpecartoon']

# The screens Codex left blank and lit, found by their colour (light blue), and their quads.
TV = [(96, 536), (857, 487), (861, 962), (94, 973)]                 # scene 7, the bar's TV close
TV_BAR = [(598, 348), (872, 296), (872, 452), (598, 486)]          # scene 6, the same TV, high in the wide shot
CELULAR = [(355, 441), (657, 426), (707, 1095), (383, 1110)]       # scene 8, Zinho's phone
COMENTARIOS = ['Ele foi armado.', 'Tô contigo, Zinho.', 'Cadê a parte dele?', 'Corre, Zinho!', 'Isso tá mal contado.']


def font(size, weight='ExtraBold'):
    return graficos.font(size, weight)


def aliados():
    if not ALIADOS.exists():
        return []
    return json.loads(ALIADOS.read_text(encoding='utf-8'))


def buscar():
    """The allies of Part 3 from the site, in the order of their numbers."""
    with urllib.request.urlopen(f'{SITE}?agora=1', timeout=30) as r:
        d = json.load(r)
    if d.get('parte') != 3:
        raise SystemExit(f"o site já mostra a parte {d.get('parte')}: a lista da Parte 3 precisa vir de outro jeito")
    lista = sorted(d.get('aliados', []), key=lambda a: a['numero'])
    ALIADOS.write_text(json.dumps(lista, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{len(lista)} aliados em {ALIADOS.name}')


def tela_azul(im, quad, folga=24):
    """The lit, blank screen near `quad`: its pixels by colour, closed and softened at the edge."""
    a = np.asarray(im.convert('RGB')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    azul = (b > 190) & (g > 160) & (r > 100) & (b - r > 20)
    xs, ys = zip(*quad)
    perto = np.zeros_like(azul)
    perto[max(0, min(ys) - folga):max(ys) + folga, max(0, min(xs) - folga):max(xs) + folga] = True
    m = Image.fromarray(((azul & perto)*255).astype(np.uint8))
    return m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.GaussianBlur(1.2))


def encaixar(fundo, plano, quad, mascara=None, crescer=1.0):
    """`plano` fitted to `quad` on `fundo` in perspective, cut to `mascara` when given."""
    cx, cy = sum(x for x, _ in quad)/4, sum(y for _, y in quad)/4
    quad = [(cx + (x - cx)*crescer, cy + (y - cy)*crescer) for x, y in quad]
    w, h = plano.size
    camada = plano.convert('RGBA').transform(fundo.size, Image.Transform.PERSPECTIVE,
                                             perspective([(0, 0), (w, 0), (w, h), (0, h)], quad), Image.Resampling.BICUBIC)
    if mascara is not None:
        camada.putalpha(Image.fromarray(np.minimum(np.asarray(camada.getchannel('A')), np.asarray(mascara))))
    out = fundo.convert('RGBA')
    out.alpha_composite(camada)
    return out


# ---------------------------------------------------------------- the wall

def pichacao(valor, cor, tamanho):
    """A spray tag: the word slanted, with a dark or light outline and a soft mist of paint."""
    f = font(tamanho)
    w = round(f.getlength(valor)) + 2*tamanho
    h = round(tamanho*2.2)
    contorno = (246, 240, 226) if sum(cor) < 200 else (22, 20, 18)
    im = Image.new('RGBA', (w, h), cor + (0,))
    texto = Image.new('L', (w, h), 0)
    ImageDraw.Draw(texto).text((tamanho, h/2), valor, font=f, fill=255, anchor='lm',
                               stroke_width=max(3, tamanho//14), stroke_fill=255)
    borda = Image.new('L', (w, h), 0)
    ImageDraw.Draw(borda).text((tamanho, h/2), valor, font=f, fill=255, anchor='lm',
                               stroke_width=max(6, tamanho//8), stroke_fill=255)
    nevoa = texto.filter(ImageFilter.GaussianBlur(tamanho/9)).point(lambda v: round(v*.35))
    im.putalpha(nevoa)
    linha = Image.new('RGBA', (w, h), contorno + (255,))
    linha.putalpha(borda)
    im.alpha_composite(linha)
    tinta = Image.new('RGBA', (w, h), cor + (255,))
    tinta.putalpha(texto)
    im.alpha_composite(tinta)
    # Slanted, as a quick hand sprays it.
    return im.transform(im.size, Image.Transform.AFFINE, (1, .22, -.11*h, 0, 1, 0), Image.Resampling.BICUBIC)


def beco(lista):
    fundo = Image.open(EPISODE / 'cena-04-beco.png').convert('RGB')
    pessoas = Image.open(ARTE / 'beco-pessoas.png').convert('L')
    rotulos = [a['arroba'] for a in lista] + [r for r in SEM_ALIADOS if len(lista) < 2]
    rnd = random.Random(3)
    plano = Image.new('RGBA', (1400, 1000), (0, 0, 0, 0))
    coef = perspective(MURO, [(0, 0), (1400, 0), (1400, 1000), (0, 1000)])

    def no_muro(x, y):
        d = coef[6]*x + coef[7]*y + 1
        return (coef[0]*x + coef[1]*y + coef[2])/d, (coef[3]*x + coef[4]*y + coef[5])/d

    pintados, k = [], 0
    for valor in rotulos:
        if k == len(LUGARES):
            break
        u, v, maior, giro = LUGARES[k]
        x, y = u*1400, v*1000
        (x0, y0), (x1, _), (_, y2) = no_muro(x, y), no_muro(x + 10, y), no_muro(x, y + 10)
        escala = (x1 - x0)/10
        aperto = (y2 - y0)/(x1 - x0)
        largura = 2*min(x0 - MURO_X[0], MURO_X[1] - x0)   # what fits, in the drawing, around the tag's middle
        cor = TINTAS[k % len(TINTAS)]
        tamanho = maior
        while tamanho >= MENOR and (font(tamanho).getlength(valor) + 2*tamanho)*(1 + ALARGA*(aperto - 1))*escala > largura:
            tamanho -= 2
        if tamanho < MENOR:
            continue
        pintados.append(valor)
        k += 1
        tag = pichacao(valor, cor, tamanho)
        tag = tag.resize((round(tag.width*(1 + ALARGA*(aperto - 1))), tag.height), Image.Resampling.BICUBIC)
        tag = tag.rotate(giro + rnd.uniform(-1.5, 1.5), resample=Image.Resampling.BICUBIC, expand=True)
        plano.alpha_composite(tag, (round(x - tag.width/2), round(y - tag.height/2)))
    camada = encaixar(Image.new('RGBA', fundo.size, (0, 0, 0, 0)), plano, MURO)
    # In the wall's own light: the paint takes its colour and shade, then the two men pass in front.
    arr = np.asarray(camada).astype(np.float32)
    parede = np.asarray(fundo).astype(np.float32)
    luz = np.clip(parede/np.array((238, 214, 168), np.float32), .3, 1.05)
    arr[..., :3] *= luz
    arr[..., 3] *= 1 - np.asarray(pessoas).astype(np.float32)/255
    out = fundo.convert('RGBA')
    out.alpha_composite(Image.fromarray(arr.clip(0, 255).astype(np.uint8)))
    out.convert('RGB').save(ARTE / 'beco-pichado.png', optimize=True)
    return pintados


# ---------------------------------------------------------------- the TV

def retrato(caminho, tamanho, caixa=None):
    """A portrait cut to `tamanho`, from the box of `caminho` (fractions) when given."""
    im = Image.open(caminho).convert('RGB')
    if caixa:
        im = im.crop(tuple(round(v*(im.width if k % 2 == 0 else im.height)) for k, v in enumerate(caixa)))
    w, h = tamanho
    k = max(w/im.width, h/im.height)
    im = im.resize((math.ceil(im.width*k), math.ceil(im.height*k)), Image.Resampling.LANCZOS)
    return im.crop(((im.width - w)//2, 0, (im.width - w)//2 + w, h))


def plantao(lista, w=1280, h=720):
    """The news report, flat: the portraits of Zinho and Renato, "PROCURADOS" and the viewers' comments."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for k in range(h):
        f = k/h
        d.line((0, k, w, k), fill=(round(16 + 18*f), round(30 + 26*f), round(78 + 40*f), 255))
    listras = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    for x in range(-h, w, 90):
        ImageDraw.Draw(listras).line((x, h, x + h, 0), fill=(255, 255, 255, 10), width=30)
    im.alpha_composite(listras)
    # Zinho, from Part 1's news, and Renato, his face on the news for the first time.
    rw, rh = 290, 380
    for k, (caminho, caixa, nome) in enumerate(((SERIE / 'episodio-01' / 'retrato-zinho.png', None, 'ZINHO'),
                                               (SERIE / 'episodio-02' / 'cena-08-retrato-amigo.png', (.14, .07, .86, .52), 'RENATO'))):
        x = 60 + k*(rw + 30)
        d.rectangle((x, 110, x + rw + 12, 110 + rh + 12), fill=(246, 240, 226, 255))
        im.paste(retrato(caminho, (rw, rh), caixa), (x + 6, 116))
        d.rectangle((x + 6, 116 + rh - 50, x + 6 + rw, 116 + rh), fill=(20, 18, 16, 255))
        d.text((x + 6 + rw/2, 116 + rh - 25), nome, font=font(32), fill=(246, 240, 226), anchor='mm')
    d.rounded_rectangle((60, 34, 330, 94), 8, fill=(196, 40, 32, 255))
    d.text((195, 64), 'PLANTÃO', font=font(40), fill=(246, 240, 226), anchor='mm')
    d.ellipse((350, 52, 374, 76), fill=(232, 60, 50))
    d.text((386, 64), 'AO VIVO', font=font(30, 'Bold'), fill=(246, 240, 226), anchor='lm')
    d.rounded_rectangle((740, 200, 1220, 266), 6, fill=(253, 184, 34, 255))
    d.text((980, 233), 'PROCURADOS', font=font(46), fill=(20, 18, 16), anchor='mm')
    d.text((742, 300), 'Suspeitos do assalto', font=font(36, 'SemiBold'), fill=(214, 220, 236), anchor='lt')
    d.text((742, 346), 'de R$ 10 milhões', font=font(36, 'SemiBold'), fill=(214, 220, 236), anchor='lt')
    d.text((742, 420), 'Novas imagens', font=font(30, 'SemiBold'), fill=(253, 184, 34), anchor='lt')
    # The viewers' comments, along the bottom.
    d.rectangle((0, h - 150, w, h), fill=(246, 240, 226, 255))
    d.rectangle((0, h - 150, 360, h), fill=(196, 40, 32, 255))
    d.text((180, h - 100), 'O PÚBLICO', font=font(36), fill=(246, 240, 226), anchor='mm')
    d.text((180, h - 52), 'COMENTA', font=font(36), fill=(246, 240, 226), anchor='mm')
    x = 390
    itens = [(a['arroba'], COMENTARIOS[k % len(COMENTARIOS)]) for k, a in enumerate(lista[:4])]
    if not itens:
        itens = [(None, c) for c in COMENTARIOS[:3]]
    for quem, frase in itens:
        if quem:
            d.text((x, h - 102), quem, font=font(36), fill=(38, 74, 168), anchor='lm')
            d.text((x, h - 52), frase, font=font(32, 'SemiBold'), fill=(30, 28, 26), anchor='lm')
            x += max(font(36).getlength(quem), font(32, 'SemiBold').getlength(frase)) + 70
        else:
            d.text((x, h - 75), f'“{frase}”', font=font(34, 'SemiBold'), fill=(30, 28, 26), anchor='lm')
            x += font(34, 'SemiBold').getlength(f'“{frase}”') + 70
        if x > w:
            break
    return im


def depois_do_muro(lista, no_muro, n):
    # The allies who are not on the wall come first, so each one shows somewhere besides the credits.
    fora = [a for a in lista if a['arroba'] not in no_muro]
    return (fora + [a for a in lista if a not in fora])[:n]


def conversa():
    """Renato's phone open on his chat with "Cobrança", over the alley of scene 5, blurred and dark."""
    fundo = Image.open(EPISODE / 'cena-05-chip.png').convert('RGB')
    out = fundo.filter(ImageFilter.GaussianBlur(14)).point(lambda v: round(v*.4)).convert('RGBA')
    w, h = fundo.size
    pw, ph = 640, 1180
    x0, y0 = (w - pw)//2, (h - ph)//2 - 30
    d = ImageDraw.Draw(out)
    d.rounded_rectangle((x0 - 18, y0 - 18, x0 + pw + 18, y0 + ph + 18), 70, fill=(14, 14, 18, 255), outline=(70, 70, 80, 255), width=3)
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), 54, fill=(236, 229, 218, 255))
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + 150), 54, fill=(32, 44, 52, 255))
    d.rectangle((x0, y0 + 100, x0 + pw, y0 + 150), fill=(32, 44, 52, 255))
    d.ellipse((x0 + 36, y0 + 52, x0 + 116, y0 + 132), fill=(110, 120, 128))
    d.text((x0 + 140, y0 + 74), 'Cobrança', font=font(40, 'Bold'), fill=(246, 246, 250), anchor='lm')
    d.text((x0 + 140, y0 + 114), 'visto agora', font=font(26, 'Medium'), fill=(180, 190, 196), anchor='lm')
    d.text((x0 + pw/2, y0 + 200), 'HOJE', font=font(24, 'SemiBold'), fill=(120, 112, 100), anchor='mm')

    def balao(y, texto, hora, enviado):
        f = font(36, 'Medium')
        largura = round(f.getlength(texto)) + 60
        alto = 104
        x = x0 + pw - 30 - largura if enviado else x0 + 30
        d.rounded_rectangle((x, y, x + largura, y + alto), 26, fill=(214, 246, 196) if enviado else (255, 255, 255))
        d.text((x + 30, y + 40), texto, font=f, fill=(24, 24, 26), anchor='lm')
        fim = x + largura - (64 if enviado else 22)
        d.text((fim, y + alto - 22), hora, font=font(22, 'Medium'), fill=(130, 130, 136), anchor='rm')
        if enviado:
            # Read: two blue ticks, as the messaging apps draw them.
            for dx in (0, 11):
                cx, cy = fim + 12 + dx, y + alto - 22
                d.line((cx, cy, cx + 6, cy + 6, cx + 18, cy - 8), fill=(52, 140, 210), width=3)
        return y + alto + 36

    y = balao(y0 + 250, 'Tô chegando na casa dele.', '23:31', True)
    y = balao(y, 'Já tá com ele?', '23:47', False)
    balao(y, 'Cadê vocês?', '00:03', False)
    out.convert('RGB').save(ARTE / 'conversa.png', optimize=True)


def tv(lista):
    jornal = plantao(lista)
    for nome, cena, quad in (('tv-bar-plantao.png', 'cena-07-tv-bar.png', TV), ('bar-plantao.png', 'cena-06-bar.png', TV_BAR)):
        fundo = Image.open(EPISODE / cena).convert('RGB')
        vidro = tela_azul(fundo, quad)
        out = encaixar(fundo, jornal, quad, vidro, crescer=1.04)
        out.convert('RGB').save(ARTE / nome, optimize=True)


# ---------------------------------------------------------------- the phone

def notificacao(app, quem, frase, quando, w):
    card = Image.new('RGBA', (w, 150), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((0, 0, w - 1, 149), 30, fill=(236, 236, 240, 232))
    d.rounded_rectangle((22, 22, 82, 82), 16, fill=(52, 192, 119))
    d.rounded_rectangle((37, 37, 67, 61), 8, fill=(246, 240, 226))
    d.polygon([(42, 58), (42, 70), (54, 60)], fill=(246, 240, 226))
    d.text((100, 36), app, font=font(19, 'SemiBold'), fill=(110, 110, 118), anchor='lm')
    d.text((w - 24, 36), quando, font=font(19, 'Medium'), fill=(110, 110, 118), anchor='rm')
    d.text((100, 76), quem, font=font(29, 'Bold'), fill=(20, 20, 24), anchor='lm')
    d.text((100, 116), frase, font=font(28, 'Regular'), fill=(32, 32, 38), anchor='lm')
    return card


def celular(lista):
    w, h = 600, 1300
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for k in range(h):
        f = k/h
        d.line((0, k, w, k), fill=(round(22 - 12*f), round(30 - 18*f), round(58 - 36*f), 255))
    d.text((w/2, h*.07), NOITE[0], font=font(28, 'Medium'), fill=(246, 246, 250), anchor='mm')
    d.text((w/2, h*.155), NOITE[1], font=font(132, 'Medium'), fill=(246, 246, 250), anchor='mm')
    apoio = [a['arroba'] for a in lista[:3]]
    mensagens = [('(21) 9••••-••13', 'Bandido.', 'agora')]
    mensagens += [(quem, 'Tô contigo, Zinho.' if k == 0 else ('Ele foi armado!' if k == 1 else 'Força, Zinho.'), 'agora')
                  for k, quem in enumerate(apoio)]
    mensagens.insert(2, ('Número desconhecido', 'Cadê o dinheiro?', '1 min'))
    if not apoio:
        mensagens.insert(1, ('Número desconhecido', 'Tô contigo, Zinho.', 'agora'))
    mensagens.append(('(11) 9••••-••58', 'Vai pagar.', '2 min'))
    y = round(h*.27)
    for app_quem in mensagens[:6]:
        card = notificacao('MENSAGENS', *app_quem, w - 40)
        im.alpha_composite(card, (20, y))
        y += card.height + 14
    d.rounded_rectangle((w/2 - 70, h - 34, w/2 + 70, h - 24), 5, fill=(196, 196, 202, 255))
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), round(w*.09), fill=255)
    im.putalpha(mask)
    fundo = Image.open(EPISODE / 'cena-08-celular-zinho.png').convert('RGB')
    vidro = tela_azul(fundo, CELULAR)
    out = encaixar(fundo, im, CELULAR, vidro, crescer=1.03)
    out.convert('RGB').save(ARTE / 'celular-notificacoes.png', optimize=True)


# ---------------------------------------------------------------- the vote and the credits

def escolha():
    a = Image.open(EPISODE / 'cena-12-ferro-velho.png').convert('RGB')
    b = Image.open(EPISODE / 'cena-13-casa-mae.png').convert('RGB')
    w, h = a.size
    out = Image.new('RGB', (w, h), (8, 8, 10))
    metade = w//2
    out.paste(a.crop((w//4, 0, w//4 + metade, h)), (0, 0))
    out.paste(b.crop((w//4, 0, w//4 + metade, h)), (metade, 0))
    ImageDraw.Draw(out).rectangle((metade - 4, 0, metade + 4, h), fill=(246, 240, 226))
    out.save(ARTE / 'escolha.png', optimize=True)


def creditos(lista):
    w, h = 941, 1672
    im = Image.new('RGB', (w, h), (8, 7, 6))
    d = ImageDraw.Draw(im)
    d.text((w/2, 250), 'A PARTE QUE FALTOU', font=font(36, 'Bold'), fill=(194, 173, 152), anchor='mm')
    d.text((w/2, 340), 'PARTE 3', font=font(110), fill=(232, 88, 76), anchor='mm')
    d.text((w/2, 440), 'ALIADOS', font=font(44, 'Bold'), fill=(201, 116, 58), anchor='mm')
    colunas = 1 if len(lista) <= 12 else 2
    porcol = math.ceil(len(lista)/colunas)
    tam = 40 if colunas == 1 else 30
    for k, a in enumerate(lista):
        c, r = divmod(k, porcol)
        x = w/2 if colunas == 1 else (w/4 if c == 0 else 3*w/4)
        y = 530 + r*(tam*1.7)
        d.text((x, y), f"nº {a['numero']:03d}  {a['arroba']}", font=font(tam, 'Bold'), fill=(246, 240, 226), anchor='mm')
    im.save(ARTE / 'creditos.png', optimize=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--buscar', action='store_true', help='fill aliados-parte-03.json from the site first')
    args = ap.parse_args()
    if args.buscar:
        buscar()
    ARTE.mkdir(exist_ok=True)
    lista = aliados()
    no_muro = beco(lista)
    na_tv = depois_do_muro(lista, no_muro, 4)
    tv(na_tv)
    celular(depois_do_muro([a for a in lista if a not in na_tv] + na_tv, no_muro, 3))
    conversa()
    escolha()
    if lista:
        creditos(lista)
    elif (ARTE / 'creditos.png').exists():
        (ARTE / 'creditos.png').unlink()
    print(f'{len(lista)} aliados; no muro: {no_muro}')


if __name__ == '__main__':
    main()
