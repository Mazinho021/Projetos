#!/usr/bin/env python3
"""Part 6's images that the edit makes from Codex's drawings.

Writes, in arte/:

- cartaz.png: scene 1, the reward poster on the pole: “RECOMPENSA”, Zinho's face (Part 1's
  portrait, the one the TV showed) and “R$ 50.000”, printed on the blank paper of the drawing;
- tela-editar.png: scene 3, the audio editor with the recording from Part 5's car, the stretch in
  which Toninho says who filled the backpack marked to be cut;
- tela-cortado.png: the same drawing with the stretch already cut;
- tela-recompensa.png: scene 11, the newspaper's news, with the reward and Zinho's face;
- tela-caixa-postal.png: scene 16, the call to Renato that falls in the voicemail;
- opcoes.png and opcoes-vertical.png: scenes 18 and 19 side by side, for the last question.

Since the creator's note of 08/11/2026 (crooked, hard-to-read phones), Codex draws the phones
facing the camera, straight and big: the screens fitted into scenes 3, 11 and 16 are their own
close-ups, with big type. achar_tela (Part 3) finds each blank screen, and encaixar_limpo
(Part 4) fits the new one behind the fingers.

    python compor_cenas.py
"""
from __future__ import annotations

import importlib.util
import math
from pathlib import Path
import random
import sys
import textwrap

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
SERIE = EPISODE.parent


def _modulo(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


# Part 5's tools; loading them also loads Part 4's and Part 3's.
p5 = _modulo('compor_cenas_ep05', SERIE / 'episodio-05' / 'montagem' / 'compor_cenas.py')
p4 = p5.p4
font, achar_tela, encaixar_limpo, fundo_escuro, arredondar = p5.font, p5.achar_tela, p5.encaixar_limpo, \
    p5.fundo_escuro, p5.arredondar
BALAO, BARRA, CINZA, FUNDO, TEXTO, VERDE = p5.BALAO, p5.BARRA, p5.CINZA, p5.FUNDO, p5.TEXTO, p5.VERDE
AZUL_IOS, VERMELHO = p5.AZUL_IOS, p5.VERMELHO_GRAVA

ARTE = HERE / 'arte'
W, H = 1440, 2560
CENTRO = {'': .5, '-vertical': 330/720}
RETRATO = SERIE / 'episodio-01' / 'retrato-zinho.png'
TRECHO = '“A sua já saiu do São Jorge cheia de roupa velha.”'


def desenho(nome):
    return EPISODE / nome


def retrato(w, h):
    # Zinho's face from Part 1's portrait, the one the TV and the newspaper showed.
    return ImageOps.fit(Image.open(RETRATO).convert('RGB'), (w, h), Image.Resampling.LANCZOS, centering=(.5, .35))


def status(d, w, hora, k):
    # The phone's status bar, at k px per unit of a 400-unit-wide screen.
    d.text((22*k, 22*k), hora, font=font(round(15*k), 'SemiBold'), fill=TEXTO, anchor='lm')
    x, y = w - 20*k, 22*k
    for j in range(4):
        d.rectangle((x - 70*k + j*7*k, y + 5*k - 3.4*j*k, x - 66*k + j*7*k, y + 6*k), fill=TEXTO)
    d.rounded_rectangle((x - 30*k, y - 6*k, x - 4*k, y + 6*k), 3*k, outline=TEXTO, width=max(1, round(1.6*k)))
    d.rectangle((x - 27*k, y - 3*k, x - 12*k, y + 3*k), fill=TEXTO)


# ---------------------------------------------------------------- the screens, with big type

def editar(w, h, cortado=False):
    """Scene 3: the recording from Part 5's car, in an audio editor. The stretch in which Toninho
    tells who filled the backpack is marked in red, with its words, and the CORTAR button below;
    `cortado` shows it gone."""
    k = w/400
    im = Image.new('RGBA', (w, h), (14, 14, 18, 255))
    d = ImageDraw.Draw(im)
    status(d, w, '04:52', k)
    d.text((24*k, 66*k), 'Gravação de 03:41', font=font(round(26*k), 'Bold'), fill=TEXTO, anchor='lm')
    d.text((24*k, 96*k), '1:05 · no carro' if cortado else '1:12 · no carro', font=font(round(17*k), 'Regular'),
           fill=CINZA, anchor='lm')
    meio = 250*k
    rnd = random.Random(11)
    x0, x1 = 20*k, w - 20*k
    corte = (150*k, 262*k)
    x = x0
    while x < x1:
        a = (8 + rnd.random()*60*(.5 + .5*abs(math.sin(x/(17*k)))))*k
        dentro = corte[0] <= x <= corte[1]
        if not (cortado and dentro):
            xx = x if not (cortado and x > corte[1]) else x - (corte[1] - corte[0]) + 4*k
            cor = (232, 80, 68) if dentro else (170, 176, 184)
            d.rounded_rectangle((xx, meio - a/2, xx + 4*k, meio + a/2), 2*k, fill=cor)
        x += 8*k
    if cortado:
        # Where the marked words were: the notice that they are gone, with a drawn check.
        d.rounded_rectangle((60*k, 130*k, w - 60*k, 182*k), 26*k, fill=(38, 120, 72))
        d.line((w/2 - 92*k, 157*k, w/2 - 84*k, 166*k, w/2 - 70*k, 148*k), fill=(255, 255, 255), width=round(4*k),
               joint='curve')
        d.text((w/2 + 10*k, 156*k), 'Trecho cortado', font=font(round(20*k), 'Bold'), fill=(255, 255, 255), anchor='mm')
        d.rounded_rectangle((w/2 - 90*k, h - 92*k, w/2 + 90*k, h - 44*k), 24*k, fill=AZUL_IOS)
        d.text((w/2, h - 68*k), 'SALVAR', font=font(round(20*k), 'ExtraBold'), fill=(255, 255, 255), anchor='mm')
    else:
        d.rectangle((corte[0] - 4*k, meio - 52*k, corte[1] + 4*k, meio + 52*k), outline=(232, 80, 68), width=round(3*k))
        caixa = (20*k, 126*k, w - 20*k, 186*k)
        d.rounded_rectangle(caixa, 14*k, fill=(70, 22, 20))
        linhas = textwrap.wrap(TRECHO, 34)
        for j, linha in enumerate(linhas[:2]):
            d.text((w/2, 144*k + 24*j*k), linha, font=font(round(17*k), 'SemiBold'), fill=(255, 226, 220), anchor='mm')
        d.rounded_rectangle((w/2 - 110*k, h - 92*k, w/2 + 110*k, h - 44*k), 24*k, fill=(232, 80, 68))
        d.text((w/2, h - 68*k), 'CORTAR TRECHO', font=font(round(20*k), 'ExtraBold'), fill=(255, 255, 255), anchor='mm')
    return arredondar(im, round(16*k))


def recompensa(w, h):
    """Scene 11: the newspaper's news, the one that put the reward on Zinho's face."""
    k = w/400
    im = Image.new('RGBA', (w, h), (246, 243, 236, 255))
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, w, 44*k), fill=(20, 20, 22))
    status(d, w, '06:31', k)
    d.rectangle((0, 44*k, w, 96*k), fill=(150, 28, 26))
    d.text((w/2, 70*k), 'A VOZ DO BAIRRO', font=font(round(24*k), 'ExtraBold'),
           fill=(255, 250, 240), anchor='mm')
    d.rounded_rectangle((20*k, 110*k, 120*k, 136*k), 6*k, fill=(214, 40, 34))
    d.text((70*k, 123*k), 'URGENTE', font=font(round(15*k), 'ExtraBold'), fill=(255, 255, 255), anchor='mm')
    titulo = ['Polícia oferece R$ 50 mil', 'por suspeito do assalto']
    for j, linha in enumerate(titulo):
        d.text((20*k, 162*k + 30*j*k), linha, font=font(round(25*k), 'ExtraBold'), fill=(20, 20, 22), anchor='lm')
    fw, fh = round(w - 40*k), round(h - 262*k)
    foto = retrato(fw, fh)
    im.paste(foto, (round(20*k), round(220*k)))
    d.rounded_rectangle((w - 190*k, h - 92*k, w - 28*k, h - 46*k), 10*k, fill=(253, 184, 34))
    d.text((w - 109*k, h - 69*k), 'R$ 50.000', font=font(round(24*k), 'ExtraBold'), fill=(20, 20, 22), anchor='mm')
    return arredondar(im, round(16*k))


def caixa_postal(w, h):
    """Scene 16: Zinho calls Renato, twice. Voicemail."""
    k = w/400
    im = Image.new('RGBA', (w, h), (18, 22, 26, 255))
    d = ImageDraw.Draw(im)
    for y in range(h):
        f = y/h
        d.line((0, y, w, y), fill=(round(28 - 14*f), round(36 - 18*f), round(42 - 20*f)))
    status(d, w, '06:34', k)
    d.ellipse((w/2 - 52*k, 70*k, w/2 + 52*k, 174*k), fill=(92, 112, 120))
    d.text((w/2, 122*k), 'R', font=font(round(50*k), 'Bold'), fill=(250, 244, 236), anchor='mm')
    d.text((w/2, 214*k), 'Renato', font=font(round(40*k), 'Bold'), fill=TEXTO, anchor='mm')
    d.text((w/2, 262*k), 'Caixa postal', font=font(round(28*k), 'ExtraBold'), fill=(240, 90, 76), anchor='mm')
    d.text((w/2, 300*k), '2 chamadas sem resposta', font=font(round(18*k), 'Medium'), fill=CINZA, anchor='mm')
    d.ellipse((w/2 - 38*k, h - 110*k, w/2 + 38*k, h - 34*k), fill=(222, 64, 56))
    d.arc((w/2 - 20*k, h - 84*k, w/2 + 20*k, h - 56*k), 200, 340, fill=(255, 255, 255), width=round(7*k))
    return arredondar(im, round(16*k))


def na_tela(cena, desenhar, nome):
    """The screen of `cena`, found by achar_tela, with what `desenhar(w, h)` draws at its size."""
    fundo = Image.open(desenho(cena)).convert('RGB')
    quad, _ = achar_tela(fundo)
    (x0, y0), (x1, y1), (x2, y2), (x3, y3) = [(x*W, y*H) for x, y in quad]
    w = round((math.dist((x0, y0), (x1, y1)) + math.dist((x3, y3), (x2, y2)))/2)
    h = round((math.dist((x0, y0), (x3, y3)) + math.dist((x1, y1), (x2, y2)))/2)
    encaixar_limpo(fundo, desenhar(w, h), quad).save(ARTE / nome, optimize=True)
    return quad


def telas():
    for cena, desenhar, nome in (('cena-03-editar-audio.png', editar, 'tela-editar.png'),
                                 ('cena-03-editar-audio.png', lambda w, h: editar(w, h, True), 'tela-cortado.png'),
                                 ('cena-11-celular-recompensa.png', recompensa, 'tela-recompensa.png'),
                                 ('cena-16-caixa-postal.png', caixa_postal, 'tela-caixa-postal.png')):
        quad = na_tela(cena, desenhar, nome)
        print(f'{nome}: tela em ' + ', '.join(f'({x:.3f}, {y:.3f})' for x, y in quad))


# ---------------------------------------------------------------- the poster

def impresso(w, h):
    """The reward poster as printed: black and red ink on white, which multiplies the paper."""
    k = w/400
    im = Image.new('RGB', (w, h), (255, 255, 255))
    d = ImageDraw.Draw(im)
    d.text((w/2, 44*k), 'RECOMPENSA', font=font(round(56*k), 'ExtraBold'), fill=(24, 22, 22), anchor='mm')
    d.text((w/2, 92*k), 'POR INFORMAÇÕES SOBRE O SUSPEITO', font=font(round(17*k), 'Bold'), fill=(40, 38, 38), anchor='mm')
    fw = round(w - 110*k)
    fh = round(h - 260*k)
    foto = ImageOps.grayscale(retrato(fw, fh)).convert('RGB')
    foto = Image.eval(foto, lambda v: round(40 + v*.8))
    im.paste(foto, (round((w - fw)/2), round(118*k)))
    d.rectangle(((w - fw)/2, 118*k, (w + fw)/2, 118*k + fh), outline=(24, 22, 22), width=round(3*k))
    d.text((w/2, h - 100*k), 'R$ 50.000', font=font(round(60*k), 'ExtraBold'), fill=(196, 30, 28), anchor='mm')
    d.text((w/2, h - 44*k), 'SIGILO GARANTIDO · LIGUE PARA A POLÍCIA', font=font(round(14*k), 'Bold'), fill=(40, 38, 38),
           anchor='mm')
    return im


def cartaz():
    fundo = Image.open(desenho('cena-01-cartaz-recompensa.png')).convert('RGB')
    quad, _ = achar_tela(fundo, busca=(.1, .1, .9, .8))
    pts = [(x*W, y*H) for x, y in quad]
    w = round(math.dist(pts[0], pts[1]))
    h = round(math.dist(pts[0], pts[3]))
    arte = impresso(w, h)
    coef = p4.perspective([(0, 0), (w, 0), (w, h), (0, h)], pts)
    camada = arte.transform((W, H), Image.Transform.PERSPECTIVE, coef, Image.Resampling.BICUBIC, fillcolor=(255, 255, 255))
    mascara = Image.new('L', (W, H), 0)
    ImageDraw.Draw(mascara).polygon(pts, fill=255)
    mascara = mascara.filter(ImageFilter.GaussianBlur(1.2))
    # Multiply: the ink darkens the paper, and the paper's light and creases stay.
    tinta = Image.fromarray((np.asarray(fundo).astype(float)*np.asarray(camada).astype(float)/255).astype(np.uint8))
    Image.composite(tinta, fundo, mascara).save(ARTE / 'cartaz.png', optimize=True)
    print('cartaz.png: papel em ' + ', '.join(f'({x:.3f}, {y:.3f})' for x, y in quad))


# ---------------------------------------------------------------- the options

def opcoes(centro_x, nome, largura, borda=14):
    """Scenes 18 and 19 on two printed cards, 3:4 crops of their middle, side by side from 12% of
    the height (below TikTok's search bar), above the question and the buttons."""
    fundo = fundo_escuro().convert('RGBA')
    gap = 36
    cw = round((largura - gap)/2)
    ch = round(cw*4/3)
    x0 = round(centro_x*W - (2*cw + gap)/2)
    y0 = round(.12*H)
    for k, cena in enumerate(('cena-18-opcao-falar.png', 'cena-19-opcao-calar.png')):
        arte = Image.open(desenho(cena)).convert('RGB').resize((W, H))
        corte = round((H - W*4/3)/2)
        foto = arte.crop((0, corte, W, H - corte)).resize((cw, ch), Image.Resampling.LANCZOS)
        x = x0 + k*(cw + gap)
        sombra = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rounded_rectangle((x - borda + 10, y0 - borda + 18, x + cw + borda + 10, y0 + ch + borda + 18),
                                                 12, fill=(0, 0, 0, 170))
        fundo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(16)))
        ImageDraw.Draw(fundo).rounded_rectangle((x - borda, y0 - borda, x + cw + borda, y0 + ch + borda), 10,
                                                fill=(240, 231, 212, 255))
        fundo.paste(foto, (x, y0))
    fundo.convert('RGB').save(ARTE / nome, optimize=True)


def main():
    ARTE.mkdir(parents=True, exist_ok=True)
    cartaz()
    telas()
    for sufixo, centro in CENTRO.items():
        opcoes(centro, f'opcoes{sufixo}.png', 1050 if not sufixo else 1010)
    print('arte/: ' + ', '.join(sorted(p.name for p in ARTE.glob('*.png'))))


if __name__ == '__main__':
    main()
