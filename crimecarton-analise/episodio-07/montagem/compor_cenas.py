#!/usr/bin/env python3
"""Part 7's images that the edit makes from Codex's drawings.

Writes, in arte/, for each layout (no suffix: Instagram; -vertical: TikTok and Shorts):

- close-lixeira.png: scene 7's phone up close, the photos app's "Apagados recentemente" with the
  division's photo (Part 2's) and the "Recuperar" button;
- close-recuperada.png: the same phone, the photo back and the newspaper among the contacts;
- close-soltar.png: scene 25's phone, the photo and the button that sends it to "A VOZ DO BAIRRO";
- opcoes.png: scenes 24 and 25 side by side, for the comment request.

The creator's rule of 12/11/2026: the phones in the drawings are normal-sized, in the hand, and
the message is read on a close of the phone of medium size, over the drawing blurred and dark
(the first cut of Part 7 had the screens fitted into tablet-sized phones, and he found it odd).

    python compor_cenas.py
"""
from __future__ import annotations

import importlib.util
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
font, fundo_escuro, arredondar = p6.font, p6.fundo_escuro, p6.arredondar
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
    im.alpha_composite(arredondar(f, round(12*k)), (x0, round((h - lado)/2 - 20*k)))
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
    im.alpha_composite(arredondar(foto(lado), round(12*k)), (round((w - lado)/2), round((h - lado)/2 - 40*k)))
    y = h - 112*k
    d.rounded_rectangle((20*k, y, w - 20*k, h - 24*k), 16*k, fill=(30, 30, 34))
    d.text((40*k, y + 24*k), 'Enviar para', font=font(round(16*k), 'SemiBold'), fill=CINZA, anchor='lm')
    d.rounded_rectangle((40*k, y + 42*k, 84*k, y + 78*k), 8*k, fill=JORNAL)
    d.text((62*k, y + 60*k), 'J', font=font(round(22*k), 'ExtraBold'), fill=(255, 250, 240), anchor='mm')
    d.text((98*k, y + 60*k), 'A VOZ DO BAIRRO', font=font(round(22*k), 'ExtraBold'), fill=TEXTO, anchor='lm')
    return arredondar(im, round(16*k))


def soltar(w, h):
    """Scene 25: the photo, ready to go to the newspaper, and the button that sends it."""
    k = w/400
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    status(d, w, '08:21', k)
    d.rounded_rectangle((20*k, 52*k, 64*k, 88*k), 8*k, fill=JORNAL)
    d.text((42*k, 70*k), 'J', font=font(round(22*k), 'ExtraBold'), fill=(255, 250, 240), anchor='mm')
    d.text((78*k, 70*k), 'A VOZ DO BAIRRO', font=font(round(24*k), 'ExtraBold'), fill=TEXTO, anchor='lm')
    lado = round(min(w - 40*k, h - 250*k))
    im.alpha_composite(arredondar(foto(lado), round(12*k)), (round((w - lado)/2), round(106*k)))
    d.text((w/2, 106*k + lado + 26*k), '1 foto anexada', font=font(round(18*k), 'Medium'), fill=CINZA, anchor='mm')
    d.rounded_rectangle((40*k, h - 84*k, w - 40*k, h - 30*k), 27*k, fill=(222, 52, 44))
    d.text((w/2, h - 57*k), 'ENVIAR', font=font(round(28*k), 'ExtraBold'), fill=(255, 255, 255), anchor='mm')
    return arredondar(im, round(16*k))


# Each close: the drawing behind it, the screen, and the phone's width and top in the 720 × 1280 frame.
CLOSES = {'lixeira': ('cena-07-foto-recuperada.png', lixeira, 280, 335),
          'recuperada': ('cena-07-foto-recuperada.png', recuperada, 280, 335),
          'soltar': ('cena-25-opcao-soltar.png', soltar, 250, 385)}


def celular(tela):
    """A phone of normal proportions (9:19.5) around a screen."""
    borda = round(tela.width*.045)
    w, h = tela.width + 2*borda, tela.height + 2*borda
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), round(w*.13), fill=(18, 18, 20, 255), outline=(70, 70, 76, 255),
                        width=max(2, round(w*.006)))
    im.alpha_composite(tela, (borda, borda))
    d.rounded_rectangle((w/2 - w*.12, borda + w*.025, w/2 + w*.12, borda + w*.07), round(w*.025), fill=(0, 0, 0, 255))
    return im


def close(nome):
    cena, desenhar, largura, topo = CLOSES[nome]
    base = Image.open(desenho(cena)).convert('RGB').resize((W, H), Image.Resampling.LANCZOS)
    base = base.filter(ImageFilter.GaussianBlur(24)).point(lambda v: round(v*.45)).convert('RGBA')
    sw = round(largura*2*.91)
    fone = celular(desenhar(sw, round(sw*19.5/9)))
    for sufixo, centro in CENTRO.items():
        fundo = base.copy()
        x, y = round(centro*W - fone.width/2), topo*2
        sombra = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sombra).rounded_rectangle((x + 10, y + 30, x + fone.width - 10, y + fone.height + 20), 70,
                                                 fill=(0, 0, 0, 200))
        fundo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(30)))
        fundo.alpha_composite(fone, (x, y))
        fundo.convert('RGB').save(ARTE / f'close-{nome}{sufixo}.png', optimize=True)
    print(f'close-{nome}: celular de {largura} px de largura, de y = {topo} a {topo + round(fone.height/2)}')


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
                                         (desenho('cena-25-opcao-soltar.png'), .45))):
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
    for nome in CLOSES:
        close(nome)
    for sufixo, centro in CENTRO.items():
        opcoes(centro, f'opcoes{sufixo}.png', 1050 if not sufixo else 1010)
    print('arte/: ' + ', '.join(sorted(p.name for p in ARTE.glob('*.png'))))


if __name__ == '__main__':
    main()
