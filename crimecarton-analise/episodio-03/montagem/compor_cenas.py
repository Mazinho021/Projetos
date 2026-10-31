#!/usr/bin/env python3
"""Part 3's images that the edit makes from Codex's drawings.

Writes, in arte/:

- celular-foto.png and celular-audio.png: Zinho's phone in scene 8, open on the chat with
  Renato's number. First the photo arrives, at 01:04 (Renato on a chair in the junkyard, from
  scene 9), then the cobrador's audio message, 0:14 long, at 01:05;
- creditos.png: the allies with their numbers, when there are any. The places of Part 3
  closed with none, so aliados-parte-03.json is empty and there are no credits.

The phone's lock screens (the photo's notification and the clock at 01:12) and the junkyard's
sign in scene 12 are drawn by the renderer, from the "screen" and "paint" of
montar_timeline.py.

    python compor_cenas.py
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import random
import sys

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
# The lit, blank screen of the phone in scene 8: its corners as fractions of the drawing,
# top left, top right, bottom right and bottom left. montar_timeline.py uses the same.
TELA08 = [(.3889, .3481), (.6153, .3481), (.6132, .6220), (.3868, .6220)]
# The photo's thumbnail in the chat: Renato's face and the hand with the ring, from scene 9.
MINIATURA09 = (.12, .12, .92, .72)

# The messaging app at night, in its dark theme.
FUNDO, BARRA, BALAO = (11, 20, 26), (31, 44, 51), (32, 44, 52)
TEXTO, CINZA, VERDE = (233, 237, 239), (134, 150, 160), (0, 168, 132)


def font(size, weight='ExtraBold'):
    return graficos.font(size, weight)


def tela_clara(im, quad, folga=24):
    """The lit, blank screen near `quad` (fractions): its pixels by colour, closed and softened."""
    a = np.asarray(im.convert('RGB')).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    clara = (r > 150) & (g > 185) & (b > 200) & (b - r > 12)
    xs = [x*im.width for x, _ in quad]
    ys = [y*im.height for _, y in quad]
    perto = np.zeros_like(clara)
    perto[max(0, round(min(ys)) - folga):round(max(ys)) + folga, max(0, round(min(xs)) - folga):round(max(xs)) + folga] = True
    m = Image.fromarray(((clara & perto)*255).astype(np.uint8))
    # Closed, then grown a little past the lit edge, so no bright rim shows around the new screen.
    m = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(7))
    return m.filter(ImageFilter.GaussianBlur(1.2))


def encaixar(fundo, plano, quad, mascara=None, crescer=1.0):
    """`plano` fitted to `quad` (fractions) on `fundo` in perspective, cut to `mascara` when given."""
    quad = [(x*fundo.width, y*fundo.height) for x, y in quad]
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


# ---------------------------------------------------------------- the chat

def barra_de_status(d, w, hora):
    d.text((40, 32), hora, font=font(26, 'SemiBold'), fill=TEXTO, anchor='lm')
    for k in range(4):                                   # signal
        x = w - 150 + k*12
        d.rectangle((x, 40 - 6*(k + 1), x + 7, 42), fill=TEXTO)
    d.rounded_rectangle((w - 88, 22, w - 40, 44), 6, outline=TEXTO, width=3)   # battery
    d.rectangle((w - 84, 26, w - 62, 40), fill=TEXTO)
    d.rectangle((w - 38, 28, w - 34, 38), fill=TEXTO)


def cabecalho(d, w):
    d.rectangle((0, 56, w, 176), fill=BARRA)
    d.line((44, 96, 28, 116, 44, 136), fill=TEXTO, width=5, joint='curve')          # back
    d.ellipse((62, 76, 142, 156), fill=(106, 118, 125))
    d.text((102, 116), 'R', font=font(40, 'Bold'), fill=(236, 240, 242), anchor='mm')
    d.text((164, 98), 'Renato', font=font(42, 'Bold'), fill=TEXTO, anchor='lm')
    d.text((164, 142), 'online', font=font(26, 'Regular'), fill=CINZA, anchor='lm')


def balao_foto(im, d, y, hora):
    foto = Image.open(EPISODE / 'cena-09-foto-refem.png').convert('RGB')
    l, t, r, b = MINIATURA09
    foto = foto.crop((round(l*foto.width), round(t*foto.height), round(r*foto.width), round(b*foto.height)))
    pw, ph = 414, 552
    foto = foto.resize((pw, ph), Image.Resampling.LANCZOS).convert('RGBA')
    # The time sits on a dark fade at the bottom of the photo, as the apps show it.
    sombra = Image.new('RGBA', (pw, 90), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sombra)
    for k in range(90):
        ds.line((0, k, pw, k), fill=(0, 0, 0, round(150*k/90)))
    foto.alpha_composite(sombra, (0, ph - 90))
    ImageDraw.Draw(foto).text((pw - 18, ph - 26), hora, font=font(22, 'Medium'), fill=(240, 240, 240), anchor='rm')
    mask = Image.new('L', (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw - 1, ph - 1), 20, fill=255)
    d.rounded_rectangle((22, y, 22 + pw + 16, y + ph + 16), 26, fill=BALAO)
    im.paste(foto, (30, y + 8), mask)
    return y + ph + 16 + 24


def balao_audio(d, y, duracao, hora):
    w, h = 430, 128
    d.rounded_rectangle((22, y, 22 + w, y + h), 26, fill=BALAO)
    cx, cy = 74, y + 54
    d.polygon([(cx - 13, cy - 18), (cx - 13, cy + 18), (cx + 17, cy)], fill=TEXTO)          # play
    rnd = random.Random(14)
    x = 112
    while x < 22 + w - 30:
        a = 6 + rnd.random()*30*(.55 + .45*math.sin(x/23))
        d.rounded_rectangle((x, cy - a/2, x + 5, cy + a/2), 2, fill=CINZA)
        x += 9
    d.ellipse((104, cy - 10, 124, cy + 10), fill=VERDE)                                      # position
    d.text((112, y + h - 26), duracao, font=font(22, 'Medium'), fill=CINZA, anchor='lm')
    d.text((22 + w - 18, y + h - 26), hora, font=font(22, 'Medium'), fill=CINZA, anchor='rm')
    return y + h + 24


def conversa(com_audio, w=600, h=1290):
    im = Image.new('RGBA', (w, h), FUNDO + (255,))
    d = ImageDraw.Draw(im)
    barra_de_status(d, w, '01:05' if com_audio else '01:04')
    cabecalho(d, w)
    d.rounded_rectangle((w/2 - 52, 196, w/2 + 52, 232), 12, fill=(24, 35, 42))
    d.text((w/2, 214), 'HOJE', font=font(22, 'SemiBold'), fill=CINZA, anchor='mm')
    y = balao_foto(im, d, 250, '01:04')
    if com_audio:
        balao_audio(d, y, '0:14', '01:05')
    # The message bar and the microphone.
    d.rounded_rectangle((16, h - 104, w - 104, h - 30), 37, fill=BARRA)
    d.text((54, h - 67), 'Mensagem', font=font(28, 'Regular'), fill=CINZA, anchor='lm')
    d.ellipse((w - 90, h - 104, w - 16, h - 30), fill=VERDE)
    mx, my = w - 53, h - 67
    d.rounded_rectangle((mx - 8, my - 20, mx + 8, my + 6), 8, fill=(246, 246, 246))
    d.arc((mx - 15, my - 10, mx + 15, my + 14), 20, 160, fill=(246, 246, 246), width=3)
    d.line((mx, my + 14, mx, my + 20), fill=(246, 246, 246), width=3)
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), round(w*.09), fill=255)
    im.putalpha(mask)
    return im


def celular():
    fundo = Image.open(EPISODE / 'cena-08-celular.png').convert('RGB')
    vidro = tela_clara(fundo, TELA08)
    for com_audio, nome in ((False, 'celular-foto.png'), (True, 'celular-audio.png')):
        out = encaixar(fundo, conversa(com_audio), TELA08, vidro, crescer=1.035)
        out.convert('RGB').save(ARTE / nome, optimize=True)


# ---------------------------------------------------------------- the credits

def aliados():
    if not ALIADOS.exists():
        return []
    return json.loads(ALIADOS.read_text(encoding='utf-8'))


def creditos(lista):
    w, h = 941, 1672
    im = Image.new('RGB', (w, h), (8, 7, 6))
    d = ImageDraw.Draw(im)
    d.text((w/2, 520), 'A PARTE QUE FALTOU', font=font(36, 'Bold'), fill=(194, 173, 152), anchor='mm')
    d.text((w/2, 610), 'PARTE 3', font=font(110), fill=(232, 88, 76), anchor='mm')
    d.text((w/2, 710), 'ALIADOS', font=font(44, 'Bold'), fill=(201, 116, 58), anchor='mm')
    colunas = 1 if len(lista) <= 8 else 2
    porcol = math.ceil(len(lista)/colunas)
    tam = 40 if colunas == 1 else 30
    for k, a in enumerate(lista):
        c, r = divmod(k, porcol)
        x = w/2 if colunas == 1 else (w/4 if c == 0 else 3*w/4)
        d.text((x, 800 + r*(tam*1.7)), f"nº {a['numero']:03d}  {a['arroba']}", font=font(tam, 'Bold'),
               fill=(246, 240, 226), anchor='mm')
    im.save(ARTE / 'creditos.png', optimize=True)


def main():
    ARTE.mkdir(exist_ok=True)
    celular()
    lista = aliados()
    if lista:
        creditos(lista)
    elif (ARTE / 'creditos.png').exists():
        (ARTE / 'creditos.png').unlink()
    print(f'{len(lista)} aliados; arte/: ' + ', '.join(sorted(p.name for p in ARTE.glob('*.png'))))


if __name__ == '__main__':
    main()
