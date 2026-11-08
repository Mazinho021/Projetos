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
    print('arte/: ' + ', '.join(sorted(p.name for p in ARTE.glob('*.png'))))


if __name__ == '__main__':
    main()
