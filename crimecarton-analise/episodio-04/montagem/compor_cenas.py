#!/usr/bin/env python3
"""Part 4's images that the edit makes from Codex's drawings.

Writes, in arte/:

- perfil.png and perfil-vertical.png: the covers of Parts 1, 2 and 3 side by side, as the
  profile's grid shows them, for "As outras partes estão no perfil". The vertical grid sits
  left of TikTok's buttons;
- lembranca-parte3.png: Part 3's scene 4, the hand with the ring pulling Renato off the wall,
  blurred and dark, behind its own polaroid ("PARTE 3 · pego no seu lugar");
- tela-agendar.png: scene 3, the chat with the newspaper's newsroom: the photo of the
  division, scheduled for 03:15, with the button that cancels it;
- tela-0313.png: scene 20, the phone at 03:13, locked, with the reminder of the send;
- opcoes.png and opcoes-vertical.png: scenes 21 and 22 side by side, for the last question.

Codex leaves each phone's screen lit and blank; achar_tela, from Part 3's compor_cenas.py,
finds it and the screen is fitted to it in perspective.

--rascunho first draws, in rascunho/, a stand-in card for each drawing Codex has not
delivered yet: its number, its name and the line of the script it shows. The stand-ins of
the phone scenes have a blank lit screen where the drawing will have one, so the screens
are fitted already. A draft's images go to rascunho/arte/, never to arte/, and only a draft
uses them (montar_timeline.py --estimar).

    python compor_cenas.py [--rascunho]
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import textwrap

from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
SERIE = EPISODE.parent
sys.path.insert(0, str(SERIE / 'episodio-01' / 'montagem'))
sys.path.insert(0, str(SERIE / 'episodio-03' / 'montagem'))
import graficos  # noqa: E402
from render_animatic import lock_screen  # noqa: E402
from compor_cenas import (BALAO, BARRA, CINZA, FUNDO, TEXTO, VERDE, achar_tela, barra_de_status,  # noqa: E402
                          encaixar)

ARTE = HERE / 'arte'
RASCUNHO = HERE / 'rascunho'
CAPAS = SERIE / 'capas'
PEDIDO = EPISODE / 'pedido-codex-ep04.md'
# Part 3's night went past midnight on Thursday; the exchange happens the same night.
NOITE = 'quinta-feira, 29 de outubro'
CONTATO = 'Jornal · Redação'
MENSAGEM = 'Foto da noite da divisão. Procurem o dono do anel.'
# The vertical version centres everything at x = 330 of 720, left of TikTok's buttons.
CENTRO = {'': .5, '-vertical': 330/720}
W, H = 1440, 2560
# The division's photo in the chat's thumbnail: the money and the hand with the ring.
MINIATURA_DIVISAO = (.08, .1, 1.0, .72)
# Where the stand-ins draw the phones' blank screens, as the request places them:
# left, top, right, bottom as fractions.
TELAS_RASCUNHO = {'cena-03-agendar.png': (.33, .30, .67, .70), 'cena-20-celular-escondido.png': (.44, .50, .58, .65)}


def font(size, weight='ExtraBold'):
    return graficos.font(size, weight)


def desenho(nome):
    """A drawing of this part: Codex's, once delivered and enlarged, or its stand-in."""
    real = EPISODE / nome
    return real if real.exists() else RASCUNHO / nome


# ---------------------------------------------------------------- stand-ins

def cenas_pedidas():
    """[(name, line of the script)] of the 22 drawings, as the request lists them."""
    texto = PEDIDO.read_text(encoding='utf-8')
    return re.findall(r'\*\*`(cena-\d\d-[a-z-]+\.png)`\*\* — “(.+?)”', texto)


def rascunho(nome, fala):
    im = Image.new('RGB', (W, H))
    d = ImageDraw.Draw(im)
    for k in range(H):
        f = k/H
        d.line((0, k, W, k), fill=(round(24 - 14*f), round(28 - 17*f), round(40 - 26*f)))
    # The bands the HUD and the captions cover, faintly.
    for y in (.25*H, .8*H):
        d.line((0, y, W, y), fill=(52, 58, 74), width=3)
    numero = int(nome[5:7])
    tela = TELAS_RASCUNHO.get(nome)
    topo = .27 if not tela or tela[1] > .45 else .735
    d.text((W/2, topo*H), f'CENA {numero}', font=font(120), fill=(120, 130, 150), anchor='mt')
    d.text((W/2, topo*H + 150), nome[8:-4].replace('-', ' '), font=font(54, 'SemiBold'), fill=(150, 158, 176), anchor='mt')
    linhas = textwrap.wrap(f'“{fala}”', 26)
    for k, linha in enumerate(linhas[:6]):
        d.text((W/2, topo*H + 270 + k*74), linha, font=font(56, 'Medium'), fill=(222, 226, 234), anchor='mt')
    d.rounded_rectangle((W/2 - 330, .935*H, W/2 + 330, .935*H + 78), 39, fill=(40, 46, 62))
    d.text((W/2, .935*H + 39), 'DESENHO A CAMINHO · CODEX', font=font(34, 'Bold'), fill=(242, 201, 76), anchor='mm')
    if tela:
        l, t, r, b = (tela[0]*W, tela[1]*H, tela[2]*W, tela[3]*H)
        borda = .06*(r - l)
        d.rounded_rectangle((l - borda, t - 2*borda, r + borda, b + 2*borda), round(3*borda), fill=(18, 18, 22))
        d.rounded_rectangle((l, t, r, b), round(1.5*borda), fill=(226, 228, 232))
    RASCUNHO.mkdir(exist_ok=True)
    im.save(RASCUNHO / nome, optimize=True)


# ---------------------------------------------------------------- the phones

def cabecalho(d, w):
    d.rectangle((0, 56, w, 176), fill=BARRA)
    d.line((44, 96, 28, 116, 44, 136), fill=TEXTO, width=5, joint='curve')          # back
    d.ellipse((62, 76, 142, 156), fill=(214, 64, 56))
    d.text((102, 116), 'J', font=font(44, 'Bold'), fill=(250, 244, 236), anchor='mm')
    d.text((164, 98), CONTATO, font=font(38, 'Bold'), fill=TEXTO, anchor='lm')
    d.text((164, 142), 'redação', font=font(26, 'Regular'), fill=CINZA, anchor='lm')


def relogio(d, cx, cy, r, cor):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=cor, width=3)
    d.line((cx, cy, cx, cy - .6*r), fill=cor, width=3)
    d.line((cx, cy, cx + .45*r, cy + .2*r), fill=cor, width=3)


def agendar(w=600, h=1290):
    """The chat with the newsroom: Zinho's message with the photo, not sent yet, for 03:15."""
    im = Image.new('RGBA', (w, h), FUNDO + (255,))
    d = ImageDraw.Draw(im)
    barra_de_status(d, w, '02:41')
    cabecalho(d, w)
    # His own message, on the right, with the photo and the scheduled time.
    foto = Image.open(SERIE / 'episodio-02' / 'cena-04-foto-divisao.png').convert('RGB')
    l, t, r, b = MINIATURA_DIVISAO
    foto = foto.crop((round(l*foto.width), round(t*foto.height), round(r*foto.width), round(b*foto.height)))
    pw, ph = 404, 404
    foto = foto.resize((pw, round(pw*foto.height/foto.width)), Image.Resampling.LANCZOS).crop((0, 0, pw, ph))
    x0, y0 = w - pw - 46, 236
    linhas = textwrap.wrap(MENSAGEM, 24)
    alto = ph + 24 + 44*len(linhas) + 64
    VERDE_ESCURO = (0, 92, 75)
    d.rounded_rectangle((x0 - 8, y0 - 8, w - 22, y0 + alto), 26, fill=VERDE_ESCURO)
    mask = Image.new('L', (pw, ph), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, pw - 1, ph - 1), 20, fill=255)
    im.paste(foto, (x0, y0), mask)
    for k, linha in enumerate(linhas):
        d.text((x0 + 4, y0 + ph + 22 + 44*k), linha, font=font(30, 'Regular'), fill=TEXTO, anchor='la')
    relogio(d, w - 158, y0 + alto - 30, 11, (190, 214, 206))
    d.text((w - 40, y0 + alto - 30), 'às 03:15', font=font(22, 'Medium'), fill=(190, 214, 206), anchor='rm')
    # The scheduled send, with the button that stops it.
    y = h - 330
    d.rounded_rectangle((22, y, w - 22, y + 190), 26, fill=BALAO)
    relogio(d, 70, y + 52, 18, TEXTO)
    d.text((104, y + 52), 'Envio agendado', font=font(30, 'Bold'), fill=TEXTO, anchor='lm')
    d.text((104, y + 92), 'hoje, às 03:15', font=font(26, 'Regular'), fill=CINZA, anchor='lm')
    d.rounded_rectangle((44, y + 122, w - 44, y + 172), 25, outline=(232, 88, 76), width=3)
    d.text((w/2, y + 147), 'CANCELAR ENVIO', font=font(26, 'Bold'), fill=(232, 88, 76), anchor='mm')
    d.rounded_rectangle((16, h - 104, w - 104, h - 30), 37, fill=BARRA)
    d.text((54, h - 67), 'Mensagem', font=font(28, 'Regular'), fill=CINZA, anchor='lm')
    d.ellipse((w - 90, h - 104, w - 16, h - 30), fill=VERDE)
    mask = Image.new('L', (w, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, w - 1, h - 1), round(w*.09), fill=255)
    im.putalpha(mask)
    return im


def na_tela(cena, plano, nome):
    fundo = Image.open(desenho(cena)).convert('RGB')
    quad, mascara = achar_tela(fundo)
    encaixar(fundo, plano, quad, mascara, crescer=1.035).convert('RGB').save(ARTE / nome, optimize=True)
    return quad


def telas():
    quads = {
        'tela-agendar.png': na_tela('cena-03-agendar.png', agendar(), 'tela-agendar.png'),
        'tela-0313.png': na_tela('cena-20-celular-escondido.png',
                                 lock_screen({'state': 'lock', 'date': NOITE, 'time': '03:13', 'app': 'MENSAGENS',
                                              'sender': CONTATO, 'message': 'Envio agendado: sai às 03:15',
                                              'when': 'agora'}),
                                 'tela-0313.png'),
    }
    for nome, quad in quads.items():
        print(f'{nome}: tela em ' + ', '.join(f'({x:.3f}, {y:.3f})' for x, y in quad))


# ---------------------------------------------------------------- the profile, the memory, the options

def fundo_escuro():
    fundo = Image.new('RGB', (W, H), (11, 11, 13))
    d = ImageDraw.Draw(fundo)
    for k in range(H):          # a little light from the top, as the profile page has
        f = max(0, 1 - k/(.6*H))
        d.line((0, k, W, k), fill=(round(11 + 16*f), round(11 + 14*f), round(13 + 12*f)))
    return fundo


def perfil(centro_x, nome, largura):
    """The covers of Parts 1 to 3 as the profile's grid crops them (3:4), side by side, from
    27% of the height: below the tag, above the phrase and the pointer."""
    fundo = fundo_escuro()
    gap = 24
    tw = round((largura - 2*gap)/3)
    th = round(tw*4/3)
    x0 = round(centro_x*W - (3*tw + 2*gap)/2)
    y0 = round(.266*H)
    for k, n in enumerate((1, 2, 3)):
        capa = Image.open(CAPAS / f'capa-parte-0{n}.png').convert('RGB')
        capa = capa.crop((0, 240, 1080, 1680)).resize((tw, th), Image.Resampling.LANCZOS)
        fundo.paste(capa, (x0 + k*(tw + gap), y0))
    fundo.save(ARTE / nome, optimize=True)


def lembranca_parte3():
    arte = Image.open(SERIE / 'episodio-03' / 'cena-04-mao-anel.png').convert('RGB').resize((W, H))
    arte.filter(ImageFilter.GaussianBlur(30)).point(lambda v: round(v*.42)).save(ARTE / 'lembranca-parte3.png', optimize=True)


def opcoes(centro_x, nome, largura, borda=14):
    """Scenes 21 and 22 on two printed cards, 3:4 crops of their middle, side by side from 12%
    of the height (below TikTok's search bar), above the question and the buttons."""
    fundo = fundo_escuro().convert('RGBA')
    gap = 36
    cw = round((largura - gap)/2)
    ch = round(cw*4/3)
    x0 = round(centro_x*W - (2*cw + gap)/2)
    y0 = round(.12*H)
    for k, cena in enumerate(('cena-21-opcao-cancelar.png', 'cena-22-opcao-enviar.png')):
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
    global ARTE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rascunho', action='store_true', help='draw stand-ins for the drawings not delivered yet')
    args = parser.parse_args()
    if args.rascunho:
        ARTE = RASCUNHO / 'arte'
    ARTE.mkdir(parents=True, exist_ok=True)
    pedidas = cenas_pedidas()
    if len(pedidas) != 22:
        raise ValueError(f'{PEDIDO.name} lists {len(pedidas)} drawings, not 22')
    faltam = [(n, f) for n, f in pedidas if not (EPISODE / n).exists()]
    if faltam and not args.rascunho:
        raise SystemExit(f'Faltam {len(faltam)} desenhos do Codex; use --rascunho para uma prévia.')
    for nome, fala in faltam:
        rascunho(nome, fala)
    telas()
    # The vertical grid and cards stay left of x = 590 of 720.
    for sufixo, centro in CENTRO.items():
        perfil(centro, f'perfil{sufixo}.png', 1250 if not sufixo else 1030)
        opcoes(centro, f'opcoes{sufixo}.png', 1050 if not sufixo else 1010)
    lembranca_parte3()
    print(f'{len(pedidas) - len(faltam)} desenhos do Codex, {len(faltam)} provisórios; {ARTE.relative_to(HERE)}/: '
          + ', '.join(sorted(p.name for p in ARTE.glob('*.png'))))


if __name__ == '__main__':
    main()
