#!/usr/bin/env python3
"""Part 7's images that the edit makes from Codex's drawings.

Writes, in arte/:

- tela-lixeira.png: scene 7, the photos app's "Apagados recentemente" with the division's photo
  (Part 2's) and a big "Recuperar" button, on the phone Zinho hides in the back seat;
- tela-recuperada.png: the same drawing, the photo back in the album, ready to go to the paper;
- tela-soltar.png: scene 25, the phone Zinho holds up to Ademir (sideways), the photo and the
  button that sends it to "A VOZ DO BAIRRO";
- opcoes.png and opcoes-vertical.png: scenes 24 and 25 side by side, for the comment request.

The phones of this part face the camera, straight and big (the rule of 08/11/2026): the screen
fitted into each drawing is its own close-up. achar_tela (Part 3) finds the blank screen, and
encaixar_limpo (Part 4) fits the new one behind the fingers.

    python compor_cenas.py
"""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
SERIE = EPISODE.parent


def _modulo(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


# Part 6's tools; loading them also loads Parts 5, 4 and 3's.
p6 = _modulo('compor_cenas_ep06', SERIE / 'episodio-06' / 'montagem' / 'compor_cenas.py')
p5 = p6.p5
font, achar_tela, encaixar_limpo, fundo_escuro, arredondar = p6.font, p6.achar_tela, p6.encaixar_limpo, \
    p6.fundo_escuro, p6.arredondar
CINZA, TEXTO, AZUL_IOS = p6.CINZA, p6.TEXTO, p6.AZUL_IOS
status = p6.status

ARTE = HERE / 'arte'
W, H = 1440, 2560
CENTRO = {'': .5, '-vertical': 330/720}
JORNAL = (150, 28, 26)


def desenho(nome):
    return EPISODE / nome


def foto(lado):
    # The division's photo of Part 2: the money and the hand with the ring.
    return p5.foto_divisao(lado).convert('RGBA')


# ---------------------------------------------------------------- the screens, with big type

def lixeira(w, h):
    """Scene 7: the deleted photo, still in the bin, and the button that brings it back."""
    k = w/400
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    status(d, w, '07:12', k)
    d.text((20*k, 64*k), 'Apagados recentemente', font=font(round(27*k), 'ExtraBold'), fill=TEXTO, anchor='lm')
    lado = round(min(w - 40*k, h - 220*k))
    f = foto(lado)
    sombra = Image.new('RGBA', (lado, round(60*k)), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sombra)
    for j in range(sombra.height):
        ds.line((0, j, lado, j), fill=(0, 0, 0, round(170*j/sombra.height)))
    f.alpha_composite(sombra, (0, lado - sombra.height))
    ImageDraw.Draw(f).text((14*k, lado - 22*k), '2 dias', font=font(round(20*k), 'Bold'), fill=(255, 255, 255),
                           anchor='lm')
    x0 = round((w - lado)/2)
    im.alpha_composite(arredondar(f, round(12*k)), (x0, round(92*k)))
    d.rounded_rectangle((40*k, h - 84*k, w - 40*k, h - 30*k), 27*k, fill=AZUL_IOS)
    d.text((w/2, h - 57*k), 'Recuperar', font=font(round(26*k), 'ExtraBold'), fill=(255, 255, 255), anchor='mm')
    return arredondar(im, round(16*k))


def recuperada(w, h):
    """The photo back in the album, and the newspaper among the contacts to send it to."""
    k = w/400
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    status(d, w, '07:13', k)
    d.rounded_rectangle((w/2 - 128*k, 46*k, w/2 + 128*k, 84*k), 19*k, fill=(38, 140, 82))
    d.line((w/2 - 104*k, 65*k, w/2 - 96*k, 73*k, w/2 - 82*k, 57*k), fill=(255, 255, 255), width=round(4*k), joint='curve')
    d.text((w/2 + 12*k, 65*k), 'Foto recuperada', font=font(round(21*k), 'Bold'), fill=(255, 255, 255), anchor='mm')
    lado = round(min(w - 40*k, h - 250*k))
    im.alpha_composite(arredondar(foto(lado), round(12*k)), (round((w - lado)/2), round(98*k)))
    y = h - 112*k
    d.rounded_rectangle((20*k, y, w - 20*k, h - 24*k), 16*k, fill=(30, 30, 34))
    d.text((40*k, y + 24*k), 'Enviar para', font=font(round(16*k), 'SemiBold'), fill=CINZA, anchor='lm')
    d.rounded_rectangle((40*k, y + 42*k, 84*k, y + 78*k), 8*k, fill=JORNAL)
    d.text((62*k, y + 60*k), 'J', font=font(round(22*k), 'ExtraBold'), fill=(255, 250, 240), anchor='mm')
    d.text((98*k, y + 60*k), 'A VOZ DO BAIRRO', font=font(round(22*k), 'ExtraBold'), fill=TEXTO, anchor='lm')
    return arredondar(im, round(16*k))


def soltar(w, h):
    """Scene 25, sideways: the photo on the left, the send-to-the-paper button on the right."""
    k = h/220
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    lado = round(h - 24*k)
    im.alpha_composite(arredondar(foto(lado), round(10*k)), (round(12*k), round(12*k)))
    x0 = lado + 26*k
    cx = (x0 + w - 12*k)/2
    d.text((cx, 40*k), 'A VOZ DO', font=font(round(22*k), 'ExtraBold'), fill=TEXTO, anchor='mm')
    d.text((cx, 66*k), 'BAIRRO', font=font(round(22*k), 'ExtraBold'), fill=TEXTO, anchor='mm')
    d.text((cx, 98*k), '1 foto anexada', font=font(round(15*k), 'Medium'), fill=CINZA, anchor='mm')
    d.rounded_rectangle((x0, h - 82*k, w - 14*k, h - 22*k), 30*k, fill=(222, 52, 44))
    d.text((cx, h - 52*k), 'ENVIAR', font=font(round(26*k), 'ExtraBold'), fill=(255, 255, 255), anchor='mm')
    return arredondar(im, round(14*k))


def na_tela(cena, desenhar, nome, busca=(.12, .15, .88, .85)):
    """The screen of `cena`, found by achar_tela, with what `desenhar(w, h)` draws at its size."""
    fundo = Image.open(desenho(cena)).convert('RGB')
    quad, _ = achar_tela(fundo, busca=busca)
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = [(x*W, y*H) for x, y in quad]
    w = round((math.dist((x0, y0), (x1, y1)) + math.dist((x3, y3), (x2, y2)))/2)
    h = round((math.dist((x0, y0), (x3, y3)) + math.dist((x1, y1), (x2, y2)))/2)
    encaixar_limpo(fundo, desenhar(w, h), quad).save(ARTE / nome, optimize=True)
    return quad


def telas():
    for cena, desenhar, nome in (('cena-07-foto-recuperada.png', lixeira, 'tela-lixeira.png'),
                                 ('cena-07-foto-recuperada.png', recuperada, 'tela-recuperada.png'),
                                 ('cena-25-opcao-soltar.png', soltar, 'tela-soltar.png')):
        quad = na_tela(cena, desenhar, nome)
        print(f'{nome}: tela em ' + ', '.join(f'({x:.3f}, {y:.3f})' for x, y in quad))


# ---------------------------------------------------------------- the options

def opcoes(centro_x, nome, largura, borda=14):
    """Scenes 24 and 25 on two printed cards, 3:4 crops of their middle, side by side from 12% of
    the height (below TikTok's search bar), above the buttons."""
    fundo = fundo_escuro().convert('RGBA')
    gap = 36
    cw = round((largura - gap)/2)
    ch = round(cw*4/3)
    x0 = round(centro_x*W - (2*cw + gap)/2)
    y0 = round(.12*H)
    for k, (caminho, meio) in enumerate(((desenho('cena-24-opcao-entregar.png'), .58),
                                         (ARTE / 'tela-soltar.png', .5))):
        arte = Image.open(caminho).convert('RGB').resize((W, H))
        alto = W*4/3
        topo = round(min(max(meio*H - alto/2, 0), H - alto))
        foto_ = arte.crop((0, topo, W, topo + round(alto))).resize((cw, ch), Image.Resampling.LANCZOS)
        x = x0 + k*(cw + gap)
        sombra = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rounded_rectangle((x - borda + 10, y0 - borda + 18, x + cw + borda + 10, y0 + ch + borda + 18),
                                                 12, fill=(0, 0, 0, 170))
        fundo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(16)))
        ImageDraw.Draw(fundo).rounded_rectangle((x - borda, y0 - borda, x + cw + borda, y0 + ch + borda), 10,
                                                fill=(240, 231, 212, 255))
        fundo.paste(foto_, (x, y0))
    fundo.convert('RGB').save(ARTE / nome, optimize=True)


def main():
    ARTE.mkdir(parents=True, exist_ok=True)
    telas()
    for sufixo, centro in CENTRO.items():
        opcoes(centro, f'opcoes{sufixo}.png', 1050 if not sufixo else 1010)
    print('arte/: ' + ', '.join(sorted(p.name for p in ARTE.glob('*.png'))))


if __name__ == '__main__':
    main()
