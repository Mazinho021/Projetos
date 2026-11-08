#!/usr/bin/env python3
"""Part 5's images that the edit makes from Codex's drawings.

Writes, in arte/:

- perfil.png and perfil-vertical.png: the covers of Parts 1 to 4 side by side, as the profile's
  grid shows them, for "As outras partes estão no perfil";
- lembranca-acordo.png: Part 4's handshake (its scene 21), blurred and dark, behind its polaroid
  ("PARTE 4 · o acordo");
- lembranca-bolsas.png: Part 4's partner with the two bags (its scene 17), the same way, behind
  "PARTE 4 · as bolsas", while Toninho tells he drove him;
- tela-cancelar.png: scene 2, the chat with the newspaper at 03:14, the scheduled photo and the
  button that cancels it, under Zinho's thumb;
- tela-lixeira.png: scene 6, the phone's "Apagados recentemente" with the division's photo;
- tela-audio.png: scene 9, Renato's chat with his audio message;
- tela-gravando.png: scene 14, the recorder running in Zinho's pocket;
- opcoes.png and opcoes-vertical.png: scenes 18 and 19 side by side, for the last question.
- close-cancelar.png, close-lixeira.png, close-audio.png and close-gravando.png, each with its
  -vertical version: the four screens again, straight and big, over their drawing blurred and
  dark. The creator found the screens fitted into the drawings crooked and hard to read
  (08/11/2026): the close-up comes right after each drawing, so the message can be read.

Codex leaves each phone's screen lit and blank; achar_tela, from Part 3's compor_cenas.py, finds it
and encaixar_limpo, from Part 4's, fits the new screen behind the fingers.

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


# Part 4's tools; loading them also loads Part 3's compor_cenas.py as "compor_cenas".
p4 = _modulo('compor_cenas_ep04', SERIE / 'episodio-04' / 'montagem' / 'compor_cenas.py')
p3 = sys.modules['compor_cenas']
font, achar_tela, encaixar_limpo, fundo_escuro = p4.font, p4.achar_tela, p4.encaixar_limpo, p4.fundo_escuro
BALAO, BARRA, CINZA, FUNDO, TEXTO, VERDE = p3.BALAO, p3.BARRA, p3.CINZA, p3.FUNDO, p3.TEXTO, p3.VERDE
barra_de_status = p3.barra_de_status

ARTE = HERE / 'arte'
CAPAS = SERIE / 'capas'
W, H = 1440, 2560
CENTRO = {'': .5, '-vertical': 330/720}
FOTO_DIVISAO = SERIE / 'episodio-02' / 'cena-04-foto-divisao.png'
MINIATURA_DIVISAO = (.08, .1, 1.0, .72)   # the money and the hand with the ring
MENSAGEM = 'Foto da noite da divisão. Procurem o dono do anel.'
AZUL_IOS = (10, 132, 255)
VERMELHO_GRAVA = (232, 64, 52)


def desenho(nome):
    return EPISODE / nome


def foto_divisao(lado):
    foto = Image.open(FOTO_DIVISAO).convert('RGB')
    l, t, r, b = MINIATURA_DIVISAO
    foto = foto.crop((round(l*foto.width), round(t*foto.height), round(r*foto.width), round(b*foto.height)))
    foto = foto.resize((lado, round(lado*foto.height/foto.width)), Image.Resampling.LANCZOS)
    return foto.crop((0, 0, lado, lado))


def arredondar(im, raio):
    mask = Image.new('L', im.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width - 1, im.height - 1), raio, fill=255)
    im.putalpha(mask)
    return im


def barra_de_mensagem(d, w, h):
    d.rounded_rectangle((16, h - 104, w - 104, h - 30), 37, fill=BARRA)
    d.text((54, h - 67), 'Mensagem', font=font(28, 'Regular'), fill=CINZA, anchor='lm')
    d.ellipse((w - 90, h - 104, w - 16, h - 30), fill=VERDE)


# ---------------------------------------------------------------- the phones

def cancelar(w=600, h=1290):
    """Scene 2: the chat with the newsroom at 03:14. The scheduled send is pinned at the top, its
    CANCELAR button on the right, where Zinho's thumb presses."""
    im = Image.new('RGBA', (w, h), FUNDO + (255,))
    d = ImageDraw.Draw(im)
    barra_de_status(d, w, '03:14')
    p4.cabecalho(d, w)
    y = 192
    d.rounded_rectangle((16, y, w - 16, y + 132), 22, fill=BALAO)
    p4.relogio(d, 54, y + 46, 17, TEXTO)
    d.text((86, y + 46), 'Envio agendado', font=font(28, 'Bold'), fill=TEXTO, anchor='lm')
    d.text((86, y + 90), 'hoje, às 03:15', font=font(24, 'Regular'), fill=CINZA, anchor='lm')
    d.rounded_rectangle((w - 210, y + 40, w - 36, y + 96), 28, fill=(232, 88, 76))
    d.text((w - 123, y + 68), 'CANCELAR', font=font(24, 'Bold'), fill=(255, 255, 255), anchor='mm')
    pw = 404
    foto = foto_divisao(pw)
    x0, y0 = w - pw - 46, 356
    linhas = textwrap.wrap(MENSAGEM, 24)
    alto = pw + 24 + 44*len(linhas) + 64
    d.rounded_rectangle((x0 - 8, y0 - 8, w - 22, y0 + alto), 26, fill=(0, 92, 75))
    im.paste(foto, (x0, y0), arredondar(foto.convert('RGBA'), 20))
    for k, linha in enumerate(linhas):
        d.text((x0 + 4, y0 + pw + 22 + 44*k), linha, font=font(30, 'Regular'), fill=TEXTO, anchor='la')
    p4.relogio(d, w - 158, y0 + alto - 30, 11, (190, 214, 206))
    d.text((w - 40, y0 + alto - 30), 'às 03:15', font=font(22, 'Medium'), fill=(190, 214, 206), anchor='rm')
    barra_de_mensagem(d, w, h)
    return arredondar(im, round(w*.09))


def lixeira(w=600, h=1290):
    """Scene 6: the photos app's "Apagados recentemente", with the division's photo, 30 days left."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    barra_de_status(d, w, '03:15')
    d.text((30, 112), '‹ Álbuns', font=font(30, 'SemiBold'), fill=AZUL_IOS, anchor='lm')
    d.text((30, 196), 'Apagados', font=font(58, 'ExtraBold'), fill=TEXTO, anchor='lm')
    d.text((30, 262), 'recentemente', font=font(58, 'ExtraBold'), fill=TEXTO, anchor='lm')
    d.text((30, 330), 'Ficam aqui por 30 dias antes de sumir.', font=font(24, 'Regular'), fill=CINZA, anchor='lm')
    lado = w - 60
    foto = foto_divisao(lado).convert('RGBA')
    sombra = Image.new('RGBA', (lado, 110), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sombra)
    for k in range(110):
        ds.line((0, k, lado, k), fill=(0, 0, 0, round(170*k/110)))
    foto.alpha_composite(sombra, (0, lado - 110))
    ImageDraw.Draw(foto).text((24, lado - 40), '30 dias', font=font(34, 'Bold'), fill=(255, 255, 255), anchor='lm')
    im.alpha_composite(arredondar(foto, 18), (30, 380))
    d.text((w/2, 380 + lado + 60), '1 foto', font=font(28, 'SemiBold'), fill=CINZA, anchor='mm')
    d.rounded_rectangle((60, h - 150, w - 60, h - 70), 40, fill=(38, 38, 42))
    d.text((w/2, h - 110), 'Recuperar', font=font(32, 'Bold'), fill=AZUL_IOS, anchor='mm')
    return arredondar(im, round(w*.09))


def audio_renato(w=600, h=1290):
    """Scene 9: Renato's chat, with his audio message from his mother's kitchen."""
    im = Image.new('RGBA', (w, h), FUNDO + (255,))
    d = ImageDraw.Draw(im)
    barra_de_status(d, w, '03:31')
    p3.cabecalho(d, w)
    d.rounded_rectangle((w/2 - 52, 196, w/2 + 52, 232), 12, fill=(24, 35, 42))
    d.text((w/2, 214), 'HOJE', font=font(22, 'SemiBold'), fill=CINZA, anchor='mm')
    # Zinho's own message, a while before.
    texto_z = 'Chegou bem?'
    largura = font(30, 'Regular').getlength(texto_z) + 140
    d.rounded_rectangle((w - 22 - largura, 260, w - 22, 350), 26, fill=(0, 92, 75))
    d.text((w - 22 - largura + 24, 304), texto_z, font=font(30, 'Regular'), fill=TEXTO, anchor='lm')
    d.text((w - 40, 330), '03:24', font=font(20, 'Medium'), fill=(190, 214, 206), anchor='rm')
    p3.balao_audio(d, 380, '0:07', '03:31')
    barra_de_mensagem(d, w, h)
    return arredondar(im, round(w*.09))


def gravando(w=600, h=1290):
    """Scene 14: the recorder, running. The red dot and the time are big: the screen is small."""
    im = Image.new('RGBA', (w, h), (12, 12, 14, 255))
    d = ImageDraw.Draw(im)
    barra_de_status(d, w, '03:41')
    d.text((w/2, 150), 'Gravador', font=font(34, 'Bold'), fill=TEXTO, anchor='mm')
    d.ellipse((w/2 - 150, 300, w/2 - 90, 360), fill=VERMELHO_GRAVA)
    d.text((w/2 - 60, 330), 'Gravando', font=font(48, 'ExtraBold'), fill=VERMELHO_GRAVA, anchor='lm')
    d.text((w/2, 500), '00:03', font=font(130, 'Bold'), fill=TEXTO, anchor='mm')
    rnd = random.Random(5)
    x = 40
    while x < w - 40:
        a = 16 + rnd.random()*150*(.5 + .5*abs(math.sin(x/37)))
        d.rounded_rectangle((x, 760 - a/2, x + 9, 760 + a/2), 4, fill=VERMELHO_GRAVA if x < w/2 else (90, 90, 96))
        x += 17
    d.line((w/2, 640, w/2, 880), fill=TEXTO, width=3)
    d.ellipse((w/2 - 80, h - 300, w/2 + 80, h - 140), outline=TEXTO, width=6)
    d.rounded_rectangle((w/2 - 34, h - 254, w/2 + 34, h - 186), 10, fill=VERMELHO_GRAVA)
    return arredondar(im, round(w*.09))


def na_tela(cena, plano, nome):
    fundo = Image.open(desenho(cena)).convert('RGB')
    quad, _ = achar_tela(fundo)
    encaixar_limpo(fundo, plano, quad).save(ARTE / nome, optimize=True)
    return quad


def telas():
    for cena, plano, nome in (('cena-02-cancelar.png', cancelar(), 'tela-cancelar.png'),
                              ('cena-06-lixeira.png', lixeira(), 'tela-lixeira.png'),
                              ('cena-09-audio-renato.png', audio_renato(), 'tela-audio.png'),
                              ('cena-14-gravar.png', gravando(), 'tela-gravando.png')):
        quad = na_tela(cena, plano, nome)
        print(f'{nome}: tela em ' + ', '.join(f'({x:.3f}, {y:.3f})' for x, y in quad))


# ---------------------------------------------------------------- the screens up close
# On 08/11/2026, after posting Part 5, the creator saw that the messages fitted into the phones of
# the drawings came out crooked and hard to read: those phones are small and tilted, and so is
# what goes on them. Each message now also gets a close-up: the screen straight, big and bright,
# over its drawing blurred and dark, as a cut to the phone. The screen is a card U × U units,
# drawn at K px per unit; CARTAO says where it goes in the 720 × 1280 frame of each version (left,
# top, side): under the tag, above the phrases (830 px) and, in the vertical version, left of
# TikTok's buttons (590 px). Its lower edge fades into the dark, as the rest of the phone.
U, K = 560, 2
CARTAO = {'': (80, 270, 560), '-vertical': (75, 332, 510)}
FALA = (0, 92, 75)                  # Zinho's own messages
CINZA_CLARO = (190, 214, 206)


def f(size, weight='Bold'):
    return font(round(size*K), weight)


def u(*vals):
    return [round(v*K) for v in vals]


def bateria(d, x, y):
    # Signal, wifi and battery at the right of the status bar, (x, y) its right middle.
    for k in range(4):
        d.rectangle(u(x - 92 + k*8, y + 6 - 4*k - 4, x - 87 + k*8, y + 7), fill=TEXTO)
    d.pieslice(u(x - 58, y - 8, x - 34, y + 16), 225, 315, fill=TEXTO)
    d.rounded_rectangle(u(x - 26, y - 7, x - 2, y + 7), 3*K, outline=TEXTO, width=2*K)
    d.rectangle(u(x - 23, y - 4, x - 9, y + 4), fill=TEXTO)
    d.rectangle(u(x - 1, y - 3, x + 1, y + 3), fill=TEXTO)


def cartao(fundo_tela, hora, app):
    """A straight phone screen: bezel, screen, status bar with the hour; app(d, im) draws the rest,
    in units, on the screen (x 10 to 550, y from 56)."""
    s = U*K
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, s - 1, s + 80*K), 42*K, fill=(9, 10, 12, 255), outline=(92, 98, 104, 255), width=3*K)
    d.rounded_rectangle(u(10, 10, U - 10, U + 60), 33*K, fill=fundo_tela + (255,))
    d.rounded_rectangle(u(U/2 - 52, 20, U/2 + 52, 46), 13*K, fill=(4, 5, 6, 255))          # the notch
    d.text(u(44, 33), hora, font=f(19, 'SemiBold'), fill=TEXTO, anchor='lm')
    bateria(d, U - 34, 33)
    app(d, im)
    # The lower edge fades into the dark: the rest of the phone, out of the frame.
    a = im.getchannel('A')
    fade = Image.new('L', (s, s), 255)
    df = ImageDraw.Draw(fade)
    for y in range(s - 90*K, s):
        df.line((0, y, s, y), fill=round(255*(s - y)/(90*K)))
    im.putalpha(Image.fromarray(np.minimum(np.array(a), np.array(fade))))
    return im


def foto_larga(w, h):
    # The division's photo, cropped to w × h px around the money and the hand with the ring.
    foto = Image.open(FOTO_DIVISAO).convert('RGB')
    l, t, r, b = MINIATURA_DIVISAO
    foto = foto.crop((round(l*foto.width), round(t*foto.height), round(r*foto.width), round(b*foto.height)))
    k = max(w/foto.width, h/foto.height)
    foto = foto.resize((round(foto.width*k), round(foto.height*k)), Image.Resampling.LANCZOS)
    x0, y0 = (foto.width - w)//2, (foto.height - h)//2
    return foto.crop((x0, y0, x0 + w, y0 + h))


def cabeca_chat(d, letra, cor, nome, sub, sub_cor=CINZA):
    d.rectangle(u(10, 56, U - 10, 128), fill=BARRA)
    d.line(u(36, 78, 24, 92, 36, 106), fill=TEXTO, width=4*K, joint='curve')
    d.ellipse(u(50, 66, 102, 118), fill=cor)
    d.text(u(76, 92), letra, font=f(26, 'Bold'), fill=(250, 244, 236), anchor='mm')
    d.text(u(118, 80), nome, font=f(25, 'Bold'), fill=TEXTO, anchor='lm')
    d.text(u(118, 108), sub, font=f(17, 'Regular'), fill=sub_cor, anchor='lm')


def app_cancelar(d, im):
    """03:14: the scheduled send, with its CANCELAR button, and the photo waiting to go."""
    cabeca_chat(d, 'J', (214, 64, 56), 'Jornal · Redação', 'redação')
    d.rounded_rectangle(u(22, 140, U - 22, 226), 18*K, fill=BALAO)
    p4.relogio(d, 50*K, 167*K, 11*K, TEXTO)
    d.text(u(70, 168), 'Envio agendado', font=f(23, 'Bold'), fill=TEXTO, anchor='lm')
    d.text(u(70, 202), 'hoje, às 03:15', font=f(19, 'Regular'), fill=CINZA, anchor='lm')
    d.rounded_rectangle(u(352, 156, 524, 210), 27*K, fill=(232, 80, 68))
    d.text(u(438, 183), 'CANCELAR', font=f(20, 'ExtraBold'), fill=(255, 255, 255), anchor='mm')
    d.rounded_rectangle(u(140, 240, U - 22, 524), 20*K, fill=FALA)
    foto = foto_larga(*u(362, 186))
    im.paste(foto, tuple(u(150, 250)), arredondar(foto.convert('RGBA'), 14*K))
    d.text(u(154, 462), 'Foto da noite da divisão.', font=f(19, 'Regular'), fill=TEXTO, anchor='lm')
    d.text(u(154, 488), 'Procurem o dono do anel.', font=f(19, 'Regular'), fill=TEXTO, anchor='lm')
    d.text(u(U - 34, 512), 'às 03:15', font=f(14, 'Medium'), fill=CINZA_CLARO, anchor='rm')


def app_lixeira(d, im):
    """After Ademir watched: the photo is in "Apagados recentemente", 30 days from gone."""
    d.text(u(30, 76), '‹ Álbuns', font=f(19, 'SemiBold'), fill=AZUL_IOS, anchor='lm')
    d.text(u(30, 122), 'Apagados recentemente', font=f(31, 'ExtraBold'), fill=TEXTO, anchor='lm')
    d.text(u(30, 160), 'Ficam aqui por 30 dias antes de sumir.', font=f(17, 'Regular'), fill=CINZA, anchor='lm')
    foto = foto_divisao(260*K).convert('RGBA')
    sombra = Image.new('RGBA', (260*K, 70*K), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sombra)
    for k in range(70*K):
        ds.line((0, k, 260*K, k), fill=(0, 0, 0, round(190*k/(70*K))))
    foto.alpha_composite(sombra, (0, 190*K))
    ImageDraw.Draw(foto).text((130*K, 238*K), '30 dias', font=f(21, 'Bold'), fill=(255, 255, 255), anchor='mm')
    im.alpha_composite(arredondar(foto, 12*K), tuple(u(30, 186)))
    d.text(u(308, 214), 'Apagada às 03:15', font=f(17, 'Regular'), fill=CINZA, anchor='lm')
    d.text(u(308, 244), 'Some em 30 dias', font=f(19, 'SemiBold'), fill=TEXTO, anchor='lm')
    d.rounded_rectangle(u(308, 380, 528, 432), 26*K, fill=(38, 38, 42))
    d.text(u(418, 406), 'Recuperar', font=f(21, 'Bold'), fill=AZUL_IOS, anchor='mm')
    d.text(u(160, 476), '1 foto', font=f(18, 'SemiBold'), fill=CINZA, anchor='mm')


def app_audio(d, im):
    """03:31, in the car: Renato's audio has just come."""
    cabeca_chat(d, 'R', (92, 112, 120), 'Renato', 'online', VERDE)
    d.rounded_rectangle(u(U/2 - 40, 142, U/2 + 40, 168), 9*K, fill=(24, 35, 42))
    d.text(u(U/2, 155), 'HOJE', font=f(15, 'SemiBold'), fill=CINZA, anchor='mm')
    texto = 'Chegou bem?'
    largura = f(22, 'Regular').getlength(texto)/K + 96
    d.rounded_rectangle(u(U - 22 - largura, 184, U - 22, 246), 18*K, fill=FALA)
    d.text(u(U - 22 - largura + 18, 214), texto, font=f(22, 'Regular'), fill=TEXTO, anchor='lm')
    d.text(u(U - 34, 234), '03:24', font=f(13, 'Medium'), fill=CINZA_CLARO, anchor='rm')
    # Renato's audio, bigger than in a real chat: it is what the narration is about.
    y0, y1 = 268, 386
    d.rounded_rectangle(u(22, y0, 470, y1), 22*K, fill=BALAO)
    d.ellipse(u(38, y0 + 18, 102, y0 + 82), fill=(92, 112, 120))
    d.text(u(70, y0 + 50), 'R', font=f(26, 'Bold'), fill=(250, 244, 236), anchor='mm')
    d.ellipse(u(84, y0 + 62, 108, y0 + 86), fill=VERDE)
    d.polygon(u(126, y0 + 30, 126, y0 + 70, 158, y0 + 50), fill=TEXTO)
    rnd = random.Random(7)
    x = 176
    while x < 446:
        a = 6 + rnd.random()*30*(.45 + .55*abs(math.sin(x/23)))
        d.rounded_rectangle(u(x, y0 + 50 - a/2, x + 4, y0 + 50 + a/2), 2*K, fill=(160, 172, 178))
        x += 9
    d.ellipse(u(170, y0 + 42, 186, y0 + 58), fill=VERDE)
    d.text(u(176, y0 + 96), '0:07', font=f(16, 'Medium'), fill=CINZA, anchor='lm')
    d.text(u(456, y0 + 96), '03:31', font=f(14, 'Medium'), fill=CINZA, anchor='rm')


def app_gravando(d, im):
    """03:41, at the gas station: the recorder, running in Zinho's pocket."""
    d.text(u(U/2, 88), 'Gravador', font=f(22, 'Bold'), fill=TEXTO, anchor='mm')
    d.ellipse(u(152, 132, 186, 166), fill=VERMELHO_GRAVA)
    d.text(u(200, 150), 'Gravando', font=f(34, 'ExtraBold'), fill=VERMELHO_GRAVA, anchor='lm')
    d.text(u(U/2, 262), '00:03', font=f(104, 'Bold'), fill=TEXTO, anchor='mm')
    rnd = random.Random(5)
    x = 34
    while x < U - 34:
        a = 10 + rnd.random()*84*(.5 + .5*abs(math.sin(x/29)))
        d.rounded_rectangle(u(x, 410 - a/2, x + 7, 410 + a/2), 3*K, fill=VERMELHO_GRAVA if x < U/2 else (90, 90, 96))
        x += 13
    d.line(u(U/2, 344, U/2, 476), fill=TEXTO, width=3*K)
    d.ellipse(u(U/2 - 34, 490, U/2 + 34, 558), outline=TEXTO, width=5*K)
    d.rounded_rectangle(u(U/2 - 14, 510, U/2 + 14, 538), 5*K, fill=VERMELHO_GRAVA)


CLOSES = {
    # name: (the drawing behind it, the screen's background, the hour, the app)
    'cancelar': ('tela-cancelar.png', FUNDO, '03:14', app_cancelar),
    'lixeira': ('tela-lixeira.png', (0, 0, 0), '03:16', app_lixeira),
    'audio': ('tela-audio.png', FUNDO, '03:31', app_audio),
    'gravando': ('tela-gravando.png', (12, 12, 14), '03:41', app_gravando),
}


def close_tela(nome):
    atras, fundo_tela, hora, app = CLOSES[nome]
    card = cartao(fundo_tela, hora, app)
    base = Image.open(ARTE / atras).convert('RGB').resize((W, H), Image.Resampling.LANCZOS)
    base = base.filter(ImageFilter.GaussianBlur(28)).point(lambda v: round(v*.4)).convert('RGBA')
    for sufixo, (x, y, lado) in CARTAO.items():
        fundo = base.copy()
        c = card.resize((lado*2, lado*2), Image.Resampling.LANCZOS) if lado*2 != card.width else card
        sombra = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rounded_rectangle((x*2 + 10, y*2 + 34, x*2 + lado*2 - 10, y*2 + lado*2), 80,
                                                 fill=(0, 0, 0, 200))
        fundo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(34)))
        fundo.alpha_composite(c, (x*2, y*2))
        fundo.convert('RGB').save(ARTE / f'close-{nome}{sufixo}.png', optimize=True)


# ---------------------------------------------------------------- the profile, the memory, the options

def perfil(centro_x, nome, largura):
    """The covers of Parts 1 to 4 as the profile's grid crops them (3:4), side by side, from 27%
    of the height: below the tag, above the phrase and the pointer."""
    fundo = fundo_escuro()
    gap = 20
    tw = round((largura - 3*gap)/4)
    th = round(tw*4/3)
    x0 = round(centro_x*W - (4*tw + 3*gap)/2)
    y0 = round(.266*H)
    for k, n in enumerate((1, 2, 3, 4)):
        capa = Image.open(CAPAS / f'capa-parte-0{n}.png').convert('RGB')
        capa = capa.crop((0, 240, 1080, 1680)).resize((tw, th), Image.Resampling.LANCZOS)
        fundo.paste(capa, (x0 + k*(tw + gap), y0))
    fundo.save(ARTE / nome, optimize=True)


def lembranca(cena, nome):
    # A drawing of Part 4, blurred and dark, behind its polaroid.
    arte = Image.open(SERIE / 'episodio-04' / cena).convert('RGB').resize((W, H))
    arte.filter(ImageFilter.GaussianBlur(30)).point(lambda v: round(v*.42)).save(ARTE / nome, optimize=True)


def opcoes(centro_x, nome, largura, borda=14):
    """Scenes 18 and 19 on two printed cards, 3:4 crops of their middle, side by side from 12% of
    the height (below TikTok's search bar), above the question and the buttons."""
    fundo = fundo_escuro().convert('RGBA')
    gap = 36
    cw = round((largura - gap)/2)
    ch = round(cw*4/3)
    x0 = round(centro_x*W - (2*cw + gap)/2)
    y0 = round(.12*H)
    for k, cena in enumerate(('cena-18-opcao-topar.png', 'cena-19-opcao-contar.png')):
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
    telas()
    for sufixo, centro in CENTRO.items():
        perfil(centro, f'perfil{sufixo}.png', 1250 if not sufixo else 1030)
        opcoes(centro, f'opcoes{sufixo}.png', 1050 if not sufixo else 1010)
    lembranca('cena-21-opcao-cancelar.png', 'lembranca-acordo.png')
    lembranca('cena-17-parceiro.png', 'lembranca-bolsas.png')
    for nome in CLOSES:
        close_tela(nome)
    print('arte/: ' + ', '.join(sorted(p.name for p in ARTE.glob('*.png'))))


if __name__ == '__main__':
    main()
