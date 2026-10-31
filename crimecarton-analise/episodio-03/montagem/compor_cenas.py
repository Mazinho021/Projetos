#!/usr/bin/env python3
"""Part 3's images that the edit makes from Codex's drawings.

Every narrated beat has its own drawing (../../../CLAUDE.md), so the phone appears in four
different shots, each with its own screen. Codex leaves the screens lit and blank; this
script finds each one by its colour, fits the screen to it in perspective and keeps the
fingers that cross it. Writes, in arte/:

- tela-notificacao.png: scene 8, the phone in Zinho's hand, locked, with the notification
  from Renato's number at 01:04 ("Foto");
- tela-foto.png: scene 25, the phone over Zinho's shoulder, open on the chat with Renato's
  number: the photo of Renato on a chair in the junkyard (from scene 9);
- tela-audio.png: scene 28, the phone closer, with the photo and the cobrador's audio
  message, 0:14 long, at 01:05;
- tela-hora.png: scene 32, the phone from above, locked, at 01:12, with the audio's
  notification seven minutes old;
- lembranca.png and lembranca-vertical.png: the lunch at Renato's mother's (scene 11) as a
  memory, the drawing on a printed card over its own blurred copy. In the full drawing,
  Renato as a boy sits at the right edge, behind TikTok's buttons; on the card he stays left
  of them. The vertical card sits a little left, under the vertical version's centre;
- perfil.png and perfil-vertical.png: the covers of Parts 1 and 2 side by side, as the
  profile's grid shows them, for "As partes um e dois estão no perfil" in the opening;
- creditos.png: the allies with their numbers, when there are any. The places of Part 3
  closed with none, so aliados-parte-03.json is empty and there are no credits.

The junkyard's sign in scene 12 is painted by the renderer, from montar_timeline.py.

    python compor_cenas.py
"""
from __future__ import annotations

from collections import deque
import json
import math
from pathlib import Path
import random
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageOps

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
SERIE = EPISODE.parent
sys.path.insert(0, str(SERIE / 'episodio-01' / 'montagem'))
import graficos  # noqa: E402
from render_animatic import lock_screen, perspective  # noqa: E402

ARTE = HERE / 'arte'
CAPAS = SERIE / 'capas'
ALIADOS = HERE / 'aliados-parte-03.json'
NOITE = 'quinta-feira, 29 de outubro'   # past midnight of Part 2's "23:47"
# The photo's thumbnail in the chat: Renato's face and the hand with the ring, from scene 9.
MINIATURA09 = (.12, .12, .92, .72)
# The vertical version centres everything at x = 330 of 720, left of TikTok's buttons.
CENTRO = {'': .5, '-vertical': 330/720}

# The messaging app at night, in its dark theme.
FUNDO, BARRA, BALAO = (11, 20, 26), (31, 44, 51), (32, 44, 52)
TEXTO, CINZA, VERDE = (233, 237, 239), (134, 150, 160), (0, 168, 132)


def font(size, weight='ExtraBold'):
    return graficos.font(size, weight)


# ---------------------------------------------------------------- finding a blank screen

def achar_tela(im, busca=(.12, .15, .88, .85), passo=4):
    """The lit, blank screen of a phone in `im`: its corners as fractions (top left, top right,
    bottom right, bottom left) and a mask of its pixels, which leaves out the fingers that
    cross it. The screen is the largest light, nearly grey area inside `busca`; each side is
    a line fitted to the middle of that edge, so the rounded corners do not pull it in."""
    a = np.asarray(im.convert('RGB')).astype(int)
    h, w, _ = a.shape
    clara = (a.mean(axis=2) > 175) & (a.max(axis=2) - a.min(axis=2) < 80)
    l, t, r, b = (round(busca[0]*w), round(busca[1]*h), round(busca[2]*w), round(busca[3]*h))
    dentro = np.zeros_like(clara)
    dentro[t:b, l:r] = True
    clara &= dentro
    # The largest connected area, found on a coarse grid.
    g = clara[::passo, ::passo]
    rotulo = np.zeros(g.shape, int)
    maior, quem, escolhido = 0, 0, 0
    for y0, x0 in zip(*np.nonzero(g)):
        if rotulo[y0, x0]:
            continue
        quem += 1
        fila, n = deque([(y0, x0)]), 0
        rotulo[y0, x0] = quem
        while fila:
            y, x = fila.popleft()
            n += 1
            for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < g.shape[0] and 0 <= xx < g.shape[1] and g[yy, xx] and not rotulo[yy, xx]:
                    rotulo[yy, xx] = quem
                    fila.append((yy, xx))
        if n > maior:
            maior, escolhido = n, quem
    if not maior:
        raise ValueError('nenhuma tela clara encontrada')
    area = np.kron(rotulo == escolhido, np.ones((passo, passo), bool))[:h, :w]
    area = np.pad(area, ((0, h - area.shape[0]), (0, w - area.shape[1])))
    perto = Image.fromarray((area*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2*passo + 1))
    m = clara & (np.asarray(perto) > 0)
    ys, xs = np.nonzero(m)
    y_min, y_max, x_min, x_max = ys.min(), ys.max(), xs.min(), xs.max()

    def reta(pontos, fora):
        # The line v = a*u + b along the outer side of an edge's points. A finger over the
        # screen only moves points inwards, so after each fit the points well inside the line
        # are dropped and the rest fitted again; `fora` is -1 when outside means smaller values.
        u, v = np.array(pontos, float).T
        for _ in range(5):
            a, b = np.polyfit(u, v, 1)
            dentro = (v - (a*u + b))*fora < -1.5
            if dentro.all() or not dentro.any():
                break
            u, v = u[~dentro], v[~dentro]
        return np.polyfit(u, v, 1)

    linhas = range(round(y_min + .15*(y_max - y_min)), round(y_max - .15*(y_max - y_min)))
    colunas = range(round(x_min + .15*(x_max - x_min)), round(x_max - .15*(x_max - x_min)))
    esq = reta([(y, np.nonzero(m[y])[0].min()) for y in linhas if m[y].any()], -1)     # x = a*y + b
    dir_ = reta([(y, np.nonzero(m[y])[0].max()) for y in linhas if m[y].any()], 1)
    topo = reta([(x, np.nonzero(m[:, x])[0].min()) for x in colunas if m[:, x].any()], -1)   # y = a*x + b
    base = reta([(x, np.nonzero(m[:, x])[0].max()) for x in colunas if m[:, x].any()], 1)

    def cruzar(vertical, horizontal):
        # x = a1*y + b1 and y = a2*x + b2.
        a1, b1 = vertical
        a2, b2 = horizontal
        y = (a2*b1 + b2)/(1 - a1*a2)
        return ((a1*y + b1 + .5)/w, (y + .5)/h)

    quad = [cruzar(esq, topo), cruzar(dir_, topo), cruzar(dir_, base), cruzar(esq, base)]
    # The mask: closed, then grown a little past the lit edge, so no bright rim shows.
    mascara = Image.fromarray((m*255).astype(np.uint8))
    mascara = mascara.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(7))
    return quad, mascara.filter(ImageFilter.GaussianBlur(1.2))


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


def na_tela(cena, plano, nome, espelhar=False):
    """Scene `cena`'s blank screen replaced by `plano`, the drawing mirrored first when asked;
    returns the screen's corners."""
    fundo = Image.open(EPISODE / cena).convert('RGB')
    if espelhar:
        fundo = ImageOps.mirror(fundo)
    quad, mascara = achar_tela(fundo)
    encaixar(fundo, plano, quad, mascara, crescer=1.035).convert('RGB').save(ARTE / nome, optimize=True)
    return quad


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


def telas():
    bloqueio = {'state': 'lock', 'date': NOITE, 'app': 'MENSAGENS', 'sender': 'Renato'}
    quads = {
        'tela-notificacao.png': na_tela('cena-08-celular.png',
                                        lock_screen({**bloqueio, 'time': '01:04', 'message': 'Foto', 'when': 'agora'}),
                                        'tela-notificacao.png'),
        'tela-foto.png': na_tela('cena-25-por-cima-do-ombro.png', conversa(False), 'tela-foto.png'),
        'tela-audio.png': na_tela('cena-28-play.png', conversa(True), 'tela-audio.png'),
        'tela-hora.png': na_tela('cena-32-hora.png',
                                 lock_screen({**bloqueio, 'time': '01:12', 'message': 'Áudio (0:14)', 'when': '7 min'}),
                                 'tela-hora.png'),
    }
    for nome, quad in quads.items():
        print(f'{nome}: tela em ' + ', '.join(f'({x:.3f}, {y:.3f})' for x, y in quad))


# ---------------------------------------------------------------- the memory and the profile

def lembranca(centro_x, nome, largura=.74, borda=18):
    """Scene 11 on a printed card, centred at `centro_x` (a fraction of the width)."""
    arte = Image.open(EPISODE / 'cena-11-almoco.png').convert('RGB')
    w, h = arte.size
    fundo = arte.filter(ImageFilter.GaussianBlur(30)).point(lambda v: round(v*.42)).convert('RGBA')
    cw = round(w*largura)
    ch = round(cw*h/w)
    foto = arte.resize((cw, ch), Image.Resampling.LANCZOS)
    x0 = round(centro_x*w - cw/2)
    y0 = round((h - ch)/2)
    sombra = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).rounded_rectangle((x0 - borda + 14, y0 - borda + 22, x0 + cw + borda + 14, y0 + ch + borda + 22),
                                             16, fill=(0, 0, 0, 170))
    fundo.alpha_composite(sombra.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(fundo)
    d.rounded_rectangle((x0 - borda, y0 - borda, x0 + cw + borda, y0 + ch + borda), 12, fill=(240, 231, 212, 255))
    fundo.paste(foto, (x0, y0))
    fundo.convert('RGB').save(ARTE / nome, optimize=True)


def perfil(centro_x, nome, w=1440, h=2560):
    """The covers of Parts 1 and 2 as the profile's grid crops them (3:4), side by side, between
    27% and 53% of the height: below the opening's tag, above the phrase and the pointer."""
    fundo = Image.new('RGB', (w, h), (11, 11, 13))
    d = ImageDraw.Draw(fundo)
    for k in range(h):          # a little light from the top, as the profile page has
        f = max(0, 1 - k/(.6*h))
        d.line((0, k, w, k), fill=(round(11 + 16*f), round(11 + 14*f), round(13 + 12*f)))
    th = round(.266*h)          # 3:4 tiles
    tw = round(th*3/4)
    gap = 28
    x0 = round(centro_x*w - (2*tw + gap)/2)
    y0 = round(.266*h)
    for k, n in enumerate((1, 2)):
        capa = Image.open(CAPAS / f'capa-parte-0{n}.png').convert('RGB')
        capa = capa.crop((0, 240, 1080, 1680)).resize((tw, th), Image.Resampling.LANCZOS)
        fundo.paste(capa, (x0 + k*(tw + gap), y0))
    fundo.save(ARTE / nome, optimize=True)


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
    telas()
    for sufixo, centro in CENTRO.items():
        lembranca(centro, f'lembranca{sufixo}.png')
        perfil(centro, f'perfil{sufixo}.png')
    lista = aliados()
    if lista:
        creditos(lista)
    elif (ARTE / 'creditos.png').exists():
        (ARTE / 'creditos.png').unlink()
    print(f'{len(lista)} aliados; arte/: ' + ', '.join(sorted(p.name for p in ARTE.glob('*.png'))))


if __name__ == '__main__':
    main()
