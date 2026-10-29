#!/usr/bin/env python3
"""The "Vire aliado" call, animated frame by frame and told by the series' narrator.

It invites the audience to become allies of Part 3, in the look of the "mais de 100 seguidores"
thank-you, whose drawing and sound tools it borrows (../agradecimento-100/mais-de-100/animar.py).
1080 × 1920 at 30 fps, about 18 s:

  "Quer aparecer na parte três?"            Part 3's card spins in and turns to "em breve".
  "Vire aliado do Zinho."                   Zinho points at you over turning caramel rays.
  "O seu arroba entra no episódio:"         "@seuperfil" types itself in.
  "no celular dele, num muro, na TV ou nos créditos."   four quick shots, each with the @.
  "E vai na legenda do post, com o seu número de aliado."   the post's caption, then the ally badge.
  "São só dez vagas, até sexta, às nove da noite."   ten open places light up; the deadline.
  (no voice)                                Zinho calls you in: "Faça parte da história".

The creator asked for no price, Pix or link on screen: the narration's last two lines ("Nove e
noventa no Pix…" and "O link tá na bio.") are cut, and the video ends on Zinho calling.

The picture follows the narration's words (alinhamento-narracao.json). Codex drew the wall, the TV
and Zinho pointing at you (cut out by recortar.py); the @ is painted on them here.

    python animar.py                          # the video, next to this script
    python animar.py --quadros 1.2 9.8 20     # stills for a look, in work/
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import importlib.util
import json
import math
from multiprocessing import Pool
from pathlib import Path
import random
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
SERIE = HERE.parent


def _modulo(nome, caminho):
    spec = importlib.util.spec_from_file_location(nome, caminho)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[nome] = mod
    spec.loader.exec_module(mod)
    return mod


# The thank-you's tools, and the series' renderer for the phone's lock screen.
base = _modulo('animar_agradecimento', SERIE / 'agradecimento-100' / 'mais-de-100' / 'animar.py')
sys.path.insert(0, str(SERIE / 'episodio-01' / 'montagem'))
import render_animatic  # noqa: E402

from animar_agradecimento import (  # noqa: E402
    W, H, FPS, SR, FUNDO, PAINEL, LINHA, CREME, AREIA, VERMELHO, VERMELHO_ESCURO, VERMELHO_TEXTO, AZUL,
    AZUL_ESCURO, CARAMELO, TINTA, OURO, limite, prog, suave, sai_cubica, sai_volta, tremor, texto, colar,
    retangulo, sombra_de, estrela, aparece, passagem)

SAIDA = HERE / 'chamada-aliado.mp4'
NARRACAO = HERE / 'narracao-chamada.wav'
ALINHAMENTO = HERE / 'alinhamento-narracao.json'
ARROBA = '@seuperfil'
ATRASO = .3  # the voice starts as the card spins in

_PALAVRAS = json.loads(ALINHAMENTO.read_text(encoding='utf-8'))['words']
_P = [(w['start'] + ATRASO, w['end'] + ATRASO) for w in _PALAVRAS]
# The words the picture follows, by their place in narracao-chamada.txt.
T = {nome: _P[i][0] for nome, i in (
    ('quer', 0), ('parte', 3), ('vire', 5), ('aliado', 6), ('zinho', 8), ('o_seu', 9), ('arroba', 11),
    ('entra', 12), ('celular', 15), ('muro', 18), ('tv', 20), ('creditos', 23), ('e', 25), ('legenda', 28),
    ('numero', 34), ('sao', 37), ('dez', 39), ('ate', 41), ('nove', 44))}
# The voice stops after "às nove da noite."; the rest of the narration stays out.
ULTIMA = 46
VOZ_FIM = _P[ULTIMA][1]

# Cuts, each just ahead of the word that brings the next picture.
C_VIRE = T['vire'] - .15
C_ARROBA = T['o_seu'] - .3
C_CELULAR = T['celular'] - .06
C_MURO = T['muro'] - .06
C_TV = T['tv'] - .06
C_CREDITOS = T['creditos'] - .06
C_LEGENDA = T['e'] - .3
C_VAGAS = T['sao'] - .14
C_FINAL = VOZ_FIM + .35        # Zinho calling, once the deadline has been said
DURACAO = round((C_FINAL + 3)*FPS)/FPS
EMPURRA = .14

PHONE_QUAD = [[0.4666, 0.4137], [0.7031, 0.4344], [0.5938, 0.6811], [0.2791, 0.6466]]  # Part 2's phone, scene 6
LOCK = {'state': 'lock', 'date': 'terça-feira, 27 de outubro', 'time': '23:47', 'app': 'MENSAGENS',
        'sender': ARROBA, 'message': 'Tô contigo, Zinho.', 'when': 'agora'}

# The @ sprayed on cena-muro.png's empty plaster, at eye height from x 120 to 880 (the middle of its
# two ends). The wall recedes to the right, its top falling from y 440 to 545 while its foot stays at
# 1400, so the @ is 12% shorter at its right end.
MURO_X, MURO_Y = (120, 880), (854, 871)
MURO_ENCOLHE = .88
REBOCO = np.array((236, 226, 206), np.float32)  # the plaster in full light: the wall over it is the light falling there

# cena-tv.png's screen: the corners of its glass as if they were square (top left, top right, bottom
# right, bottom left), and the colour of its empty glow, which the news report covers.
TV_QUAD = [(207, 800), (913, 778), (913, 1308), (207, 1301)]
TV_BRILHO = (141, 229, 252)


# ---------------------------------------------------------------- assets

A = {}


def cobrir(im, tamanho=(W, H)):
    """Scale `im` to cover `tamanho` and crop the middle."""
    k = max(tamanho[0]/im.width, tamanho[1]/im.height)
    im = im.resize((math.ceil(im.width*k), math.ceil(im.height*k)), Image.Resampling.LANCZOS)
    l, t = (im.width - tamanho[0])//2, (im.height - tamanho[1])//2
    return im.crop((l, t, l + tamanho[0], t + tamanho[1])).convert('RGBA')


def carregar():
    if A:
        return
    base.carregar_assets()
    # Zinho pointing at you, cut from Codex's drawings: one for "Vire aliado", one for the close.
    for nome in ('apontando', 'chamando'):
        A[nome] = Image.open(HERE / 'recortes' / f'zinho-{nome}.png').convert('RGBA')

    # Caramel rays for "Vire aliado": the lamp's colour, dark at the edges.
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W/2)/W, (yy - 1150)/H)
    v = np.clip((r - .15)/.6, 0, 1)**1.3
    vinheta = np.zeros((H, W, 4), np.uint8)
    vinheta[..., :3] = (92, 44, 16)
    vinheta[..., 3] = (v*225).astype(np.uint8)
    A['vinheta_caramelo'] = Image.fromarray(vinheta)

    # The phone of Part 2's scene 6, with and without the ally's message on its lock screen.
    cena = Image.open(SERIE / 'episodio-02' / 'cena-06-celular-mesa.png').convert('RGBA')
    A['cena_celular'] = cena
    sem = dict(LOCK)
    del sem['sender']
    A['bloqueio'] = render_animatic.lock_screen(sem)
    com = render_animatic.lock_screen(LOCK)
    w, h = com.size
    topo, lado = round(h*.40), round(w*.05)
    A['notificacao'] = (com.crop((lado, topo, w - lado, topo + 200)), (lado, topo))
    quad = [(x*cena.width, y*cena.height) for x, y in PHONE_QUAD]
    A['celular_coef'] = render_animatic.perspective([(0, 0), (w, 0), (w, h), (0, h)], quad)

    A['muro'] = cobrir(Image.open(HERE / 'cena-muro.png').convert('RGB'))
    A['muro_luz'] = np.clip(np.asarray(A['muro'].convert('RGB'), np.float32)/REBOCO, .3, 1)
    A['tv'] = cobrir(Image.open(HERE / 'cena-tv.png').convert('RGB'))
    A['tv_vidro'], A['tv_bordas'] = vidro_da_tv(A['tv'])

    A['avatar'] = avatar_redondo(Image.open(SERIE / 'site' / 'img' / 'perfil.jpg'), 104)


def vidro_da_tv(fundo):
    """Where the news shows on cena-tv.png: the screen's glass, with its rounded edge, and the
    shadow that darkens a tube TV's picture towards that edge."""
    rgb = np.asarray(fundo.convert('RGB')).astype(int)
    vidro = np.abs(rgb - TV_BRILHO).sum(axis=2) < 70
    xs, ys = zip(*TV_QUAD)
    perto = np.zeros_like(vidro)
    perto[min(ys) - 20:max(ys) + 20, min(xs) - 20:max(xs) + 20] = True
    m = Image.fromarray((vidro & perto).astype(np.uint8)*255)
    m = m.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    bordas = Image.new('RGBA', fundo.size, (6, 10, 30, 255))
    bordas.putalpha(ImageChops.multiply(m.filter(ImageFilter.GaussianBlur(28)).point(lambda v: round((255 - v)*.55)), m))
    return m.filter(ImageFilter.GaussianBlur(1.2)), bordas


def avatar_redondo(im, d):
    im = im.convert('RGB').resize((d, d), Image.Resampling.LANCZOS).convert('RGBA')
    m = Image.new('L', (d, d), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    im.putalpha(m)
    anel = Image.new('RGBA', (d + 12, d + 12), (0, 0, 0, 0))
    ImageDraw.Draw(anel).ellipse((0, 0, d + 11, d + 11), outline=VERMELHO_TEXTO + (255,), width=4)
    anel.alpha_composite(im, (6, 6))
    return anel


# ---------------------------------------------------------------- pieces

@lru_cache(maxsize=8)
def pilula(valor, tamanho):
    """A red pill with a lip under it, like the site's buttons."""
    s = texto(valor, tamanho, sombra=False)
    w, h = s.width + round(tamanho*1.6), s.height + round(tamanho*.9)
    im = Image.new('RGBA', (w, h + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 10, w - 1, h + 9), h//2, fill=VERMELHO_ESCURO + (255,))
    d.rounded_rectangle((0, 0, w - 1, h - 1), h//2, fill=VERMELHO + (255,))
    im.alpha_composite(s, ((w - s.width)//2, (h - s.height)//2))
    return im


@lru_cache(maxsize=8)
def etiqueta(valor, tamanho, fundo=VERMELHO, tinta=CREME):
    """The site's brand tag: a block of colour with the word in it."""
    s = texto(valor, tamanho, tinta, sombra=False)
    w, h = s.width + round(tamanho*.7), s.height + round(tamanho*.45)
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), 16, fill=fundo + (255,), outline=TINTA + (255,), width=6)
    im.alpha_composite(s, ((w - s.width)//2, (h - s.height)//2))
    return im


def lugar(tela, t, inicio, valor):
    """The label of each place the @ appears, at the top of the shot."""
    aparece(tela, pilula(valor, 54), W/2, 300, inicio, t)


def raios_caramelo(tela, t):
    d = ImageDraw.Draw(tela)
    d.rectangle((0, 0, W, H), fill=CARAMELO + (255,))
    giro = math.radians(t*14)
    cx, cy = W/2, 1150
    for i in range(20):
        a0 = giro + i*2*math.pi/20
        a1 = a0 + math.pi/20
        d.polygon([(cx, cy), (cx + 2600*math.cos(a0), cy + 2600*math.sin(a0)), (cx + 2600*math.cos(a1), cy + 2600*math.sin(a1))],
                  fill=(201, 116, 58, 255))
    tela.alpha_composite(A['vinheta_caramelo'])


def flash(tela, t, t0, dur=.22, forca=200):
    k = 1 - prog(t, t0, t0 + dur)
    if 0 < k < 1 or (k == 1 and t >= t0):
        tela.alpha_composite(Image.new('RGBA', (W, H), (255, 250, 240, round(forca*k))))


def sacudir(tela, t, t0, amp=16, dur=.4, cor=FUNDO):
    tx, ty = tremor(t, t0, dur, amp)
    if not (tx or ty):
        return tela
    movida = Image.new('RGBA', (W, H), cor + (255,))
    movida.alpha_composite(tela, (round(tx), round(ty)))
    return movida


def zinho_sobe(tela, t, inicio, figura, escala=.72, base_y=1990, x=W/2):
    """Zinho rises from the bottom edge, bounces and sways a little."""
    p = prog(t, inicio, inicio + .38)
    if p <= 0:
        return
    y = base_y + 950*(1 - sai_volta(p, 1.2))
    depois = t - inicio - .38
    angulo = 2*math.sin(depois*2.4) if depois > 0 else -5*(1 - p)
    colar(tela, A[figura], x, y, escala, angulo, ancora=(.5, 1))


# ---------------------------------------------------------------- scenes

def cena_pergunta(t):
    """"Quer aparecer na parte três?": Part 3's card spins in and turns to "em breve"."""
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    base.faixas_da_jaqueta(tela, t)
    entra = prog(t, .04, .55)
    escala = (.2 + .8*sai_volta(entra, 1.3))*1.3
    angulo = -24*(1 - sai_cubica(entra)) + 2*math.sin(t*1.8)
    y = 1030 + 10*math.sin(t*2.2)
    vira = prog(t, T['parte'] + .05, T['parte'] + .45)
    face = base.A['frente'] if vira >= .5 else base.A['verso']
    colar(tela, base.A['carta_sombra'], W/2 + 14, y + 26, escala, angulo, .85)
    colar(tela, face, W/2, y - 30*math.sin(math.pi*vira), escala, angulo, escala_x=max(.02, abs(math.cos(math.pi*vira))))
    base.brilho(tela, t, T['parte'] + .45)
    aparece(tela, texto('QUER APARECER', 100, CREME), W/2, 330, T['quer'], t)
    aparece(tela, texto('NA PARTE 3?', 138, VERMELHO_TEXTO, contorno=8), W/2, 470, T['parte'] - .05, t, tipo='pancada')
    return sacudir(tela, t, T['parte'] - .05, 10, cor=AZUL_ESCURO)


def cena_vire(t):
    """"Vire aliado do Zinho.": Zinho points at you over caramel rays."""
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    raios_caramelo(tela, t)
    zinho_sobe(tela, t, C_VIRE + .02, 'apontando')
    aparece(tela, texto('VIRE', 120, CREME, contorno=8), W/2, 320, T['vire'], t, tipo='pancada')
    aparece(tela, etiqueta('ALIADO', 150), W/2, 480, T['aliado'], t, tipo='pancada', angulo=4)
    aparece(tela, texto('DO ZINHO', 70, CREME, contorno=6), W/2, 640, T['zinho'] - .08, t)
    flash(tela, t, C_VIRE)
    return sacudir(tela, t, T['aliado'], 16, cor=(92, 44, 16))


def cena_arroba(t):
    """"O seu arroba entra no episódio:": the @ types itself in."""
    tela = base.A['holofote'].copy()
    aparece(tela, texto('O SEU', 92, CREME), W/2, 700, T['o_seu'], t)
    caixa = retangulo((880, 190), 95, (13, 9, 7, 240), CARAMELO + (255,), 6)
    entra = prog(t, T['o_seu'] + .05, T['o_seu'] + .3)
    camada = caixa.copy()
    letras = ARROBA[1:]
    k = prog(t, T['arroba'], T['entra'])
    n = math.floor(len(letras)*k + 1e-9)
    escrito = texto('@' + letras[:n], 96, CREME, sombra=False)
    camada.alpha_composite(escrito, (60, (caixa.height - escrito.height)//2))
    if int(t*3) % 2 == 0 or k < 1:
        cursor = retangulo((8, 100), 3, OURO + (255,))
        camada.alpha_composite(cursor, (min(camada.width - 40, 70 + escrito.width), (caixa.height - 100)//2))
    colar(tela, camada, W/2, 960, .7 + .3*sai_volta(entra), alfa=prog(t, T['o_seu'] + .05, T['o_seu'] + .12))
    aparece(tela, texto('ENTRA NO EPISÓDIO', 92, VERMELHO_TEXTO, contorno=8), W/2, 1220, T['entra'], t, tipo='pancada')
    return tela


def cena_celular(t):
    """"no celular dele": the message from the @ lands on Zinho's phone."""
    cena = A['cena_celular'].copy()
    plano = A['bloqueio'].copy()
    cartao, (lado, topo) = A['notificacao']
    p = sai_volta(prog(t, C_CELULAR + .12, C_CELULAR + .42), 1.1)
    if p > 0:
        c = cartao.copy()
        c.putalpha(c.getchannel('A').point(lambda v: round(v*min(1.0, p*2))))
        plano.alpha_composite(c, (lado, max(0, round(topo - 140*(1 - p)))))
    camada = plano.transform(cena.size, Image.Transform.PERSPECTIVE, A['celular_coef'], Image.Resampling.BICUBIC)
    cena.alpha_composite(camada)
    # Close on the phone, so the message reads, and a little closer as the shot goes on.
    zoom = 1.3 + .08*prog(t, C_CELULAR, C_MURO)
    cx, cy = .49*cena.width, .56*cena.height
    w, h = cena.width/zoom, cena.width/zoom*H/W
    tela = cena.resize((W, H), Image.Resampling.BICUBIC, box=(cx - w/2, cy - h/2, cx + w/2, cy + h/2))
    lugar(tela, t, C_CELULAR + .05, 'NO CELULAR DELE')
    return tela


def cena_muro(t):
    """"num muro": the @ sprayed on the street wall, in the light of the street lamp."""
    tela = A['muro'].copy()
    p = prog(t, C_MURO + .05, C_MURO + .38)
    if p > 0:
        pich = pichacao()
        w, h = pich.size
        tinta = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        borda = round(w*p)
        tinta.paste(pich.crop((0, 0, borda, h)))
        if p < 1:
            # The spray: drops around the can's moving edge.
            d = ImageDraw.Draw(tinta)
            rnd = random.Random(int(t*FPS))
            for _ in range(70):
                x, y = borda + rnd.gauss(0, 22), h/2 + rnd.gauss(0, h*.3)
                r = rnd.uniform(1.5, 4.5)
                d.ellipse((x - r, y - r, x + r, y + r), fill=VERMELHO_TEXTO + (rnd.randint(90, 220),))
        coef = render_animatic.perspective([(0, 0), (w, 0), (w, h), (0, h)], quad_do_muro(w, h))
        camada = np.asarray(tinta.transform((W, H), Image.Transform.PERSPECTIVE, coef, Image.Resampling.BICUBIC), np.float32)
        camada[..., :3] *= A['muro_luz']
        tela.alpha_composite(Image.fromarray(camada.astype(np.uint8)))
    lugar(tela, t, C_MURO + .05, 'NUM MURO')
    return tela


def quad_do_muro(w, h):
    """Where a w × h sprite goes on the wall: its corners from the top left, clockwise."""
    (x0, x1), (y0, y1) = MURO_X, MURO_Y
    h0 = h*(x1 - x0)/w*2/(1 + MURO_ENCOLHE)  # the left end, so that the middle keeps the sprite's shape
    h1 = h0*MURO_ENCOLHE
    return [(x0, y0 - h0/2), (x1, y1 - h1/2), (x1, y1 + h1/2), (x0, y0 + h0/2)]


@lru_cache(maxsize=1)
def pichacao():
    """The @ in spray paint: red, a dark outline and a soft mist of red around it."""
    s = texto(ARROBA, 150, VERMELHO_TEXTO, contorno=10, sombra=False)
    margem = 30
    im = Image.new('RGBA', (s.width + 2*margem, s.height + 2*margem), VERMELHO_TEXTO + (0,))
    nevoa = Image.new('L', im.size, 0)
    nevoa.paste(s.getchannel('A'), (margem, margem))
    im.putalpha(nevoa.filter(ImageFilter.GaussianBlur(10)).point(lambda v: round(v*.4)))
    im.alpha_composite(s, (margem, margem))
    return im


def cena_tv(t):
    """"na TV": the @ on a news report, on the TV's glass."""
    tela = A['tv'].copy()
    jornal = telejornal(t)
    w, h = jornal.size
    coef = render_animatic.perspective([(0, 0), (w, 0), (w, h), (0, h)], TV_QUAD)
    camada = jornal.transform((W, H), Image.Transform.PERSPECTIVE, coef, Image.Resampling.BICUBIC)
    camada.putalpha(A['tv_vidro'])
    tela.alpha_composite(camada)
    tela.alpha_composite(A['tv_bordas'])
    lugar(tela, t, C_TV + .05, 'NA TV')
    return tela


def telejornal(t):
    """A news report, flat, before it is fitted to the TV's screen."""
    w, h = 800, 600
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for k in range(h):
        d.line((0, k, w, k), fill=(round(20 + 20*k/h), round(44 + 30*k/h), round(110 + 40*k/h), 255))
    # Everything stays clear of the glass's rounded corners.
    d.rectangle((130, 50, 390, 114), fill=VERMELHO + (255,))
    s = texto('PLANTÃO', 44, CREME, sombra=False)
    im.alpha_composite(s, (150, 82 - s.height//2))
    p = sai_cubica(prog(t, C_TV + .1, C_TV + .4))
    faixa = Image.new('RGBA', (w - 140, 150), (247, 243, 236, 255))
    fd = ImageDraw.Draw(faixa)
    fd.rectangle((0, 0, 18, 150), fill=VERMELHO + (255,))
    nome = texto(ARROBA, 70, TINTA, sombra=False)
    faixa.alpha_composite(nome, (44, 18))
    sub = texto('aliado do Zinho', 38, (110, 92, 78), 'SemiBold', sombra=False)
    faixa.alpha_composite(sub, (48, 98))
    im.alpha_composite(faixa, (round(70 - (w + 70)*(1 - p)), 300))
    d.rectangle((0, h - 60, w, h), fill=(10, 14, 30, 255))
    rodape = texto('A PARTE QUE FALTOU  •  PARTE 3  •  ALIADOS DO ZINHO  •  ', 30, CREME, 'Bold', sombra=False)
    x = -((t - C_TV)*160) % rodape.width
    for dx in (-rodape.width, 0, rodape.width):
        colar(im, rodape, x + dx, h - 30, ancora=(0, .5))
    # The tube's scan lines.
    linhas = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(linhas)
    for k in range(0, h, 4):
        ld.line((0, k, w, k), fill=(0, 0, 0, 40))
    im.alpha_composite(linhas)
    return im


def cena_creditos(t):
    """"nos créditos": the end credits roll with the @ among the allies."""
    tela = Image.new('RGBA', (W, H), (6, 5, 4, 255))
    sobe = (t - C_CREDITOS)*90
    linhas = [('A PARTE QUE FALTOU', 38, AREIA, 'Bold', 10), ('PARTE 3', 96, VERMELHO_TEXTO, 'ExtraBold', 0),
              ('', 30, AREIA, 'Bold', 0), ('ALIADOS', 40, CARAMELO, 'Bold', 12), ('', 20, AREIA, 'Bold', 0),
              (f'nº 001   {ARROBA}', 66, CREME, 'ExtraBold', 0), ('nº 002   vaga aberta', 46, (122, 104, 88), 'SemiBold', 0),
              ('nº 003   vaga aberta', 46, (122, 104, 88), 'SemiBold', 0), ('nº 004   vaga aberta', 46, (122, 104, 88), 'SemiBold', 0)]
    y = 820 - sobe
    for valor, tam, cor, peso, espaco in linhas:
        if valor:
            s = texto(valor, tam, cor, peso, sombra=False, espaco=espaco)
            if ARROBA in valor:
                brilho = s.filter(ImageFilter.GaussianBlur(14))
                colar(tela, brilho, W/2, y, 1.05, alfa=.3)
            colar(tela, s, W/2, y)
        y += tam*1.6
    lugar(tela, t, C_CREDITOS + .05, 'NOS CRÉDITOS')
    return tela


def cena_legenda(t):
    """"E vai na legenda do post, com o seu número de aliado.": the caption, then the badge."""
    tela = base.A['papel'].copy()
    p = sai_volta(prog(t, C_LEGENDA + .2, C_LEGENDA + .6), 1.1)
    if p > 0:
        colar(tela, cartao_do_post(t), W/2, 860 + 500*(1 - p), alfa=min(1.0, p*3))
    if t >= T['numero'] - .06:
        k = prog(t, T['numero'] - .06, T['numero'] + .12)
        colar(tela, sombra_do_cracha(), W/2 + 18, 1310 + 28, 1 + .9*(1 - sai_cubica(k)), -6, k)
        colar(tela, cracha(), W/2, 1310, 1 + .9*(1 - sai_cubica(k)), -6, prog(t, T['numero'] - .06, T['numero'] - .01))
    aparece(tela, texto('NA LEGENDA DO POST', 76, TINTA, sombra=False), W/2, 330, T['e'], t)
    aparece(tela, texto('COM O SEU NÚMERO', 64, VERMELHO, sombra=False), W/2, 440, T['numero'] - .25, t)
    return sacudir(tela, t, T['numero'] + .1, 12, cor=CREME)


def cartao_do_post(t):
    """The post's caption, as the site shows it: avatar, the profile, and the allies with the @."""
    w, h = 900, 400
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=(255, 252, 246, 255), outline=(222, 208, 190, 255), width=3)
    im.alpha_composite(A['avatar'], (40, 40))
    im.alpha_composite(texto('golpecartoon', 46, TINTA, 'Bold', sombra=False), (176, 52))
    im.alpha_composite(texto('legenda do post', 32, (150, 132, 116), 'Medium', sombra=False), (180, 108))
    im.alpha_composite(texto('A parte que faltou · Parte 3', 42, TINTA, 'SemiBold', sombra=False), (44, 196))
    linha = texto('Aliados:', 46, TINTA, 'SemiBold', sombra=False)
    im.alpha_composite(linha, (44, 270))
    nome = texto(ARROBA, 46, AZUL, 'ExtraBold', sombra=False)
    x = 44 + linha.width + 16
    im.alpha_composite(nome, (x, 270))
    marca = prog(t, T['legenda'], T['legenda'] + .35)
    if marca > 0:
        ImageDraw.Draw(im).rectangle((x, 270 + nome.height + 4, x + nome.width*sai_cubica(marca), 270 + nome.height + 12),
                                     fill=VERMELHO_TEXTO + (255,))
    return im


@lru_cache(maxsize=1)
def sombra_do_cracha():
    return sombra_de(cracha(), 20, 120)


@lru_cache(maxsize=1)
def cracha():
    """The ally's badge: number 001 for the first ally of the list."""
    w, h = 640, 380
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 34, fill=AZUL_ESCURO + (255,), outline=CREME + (255,), width=6)
    for dx in (0, 46):
        d.polygon([(w - 230 + dx, h), (w - 204 + dx, h), (w - 74 + dx, 0), (w - 100 + dx, 0)], fill=(247, 236, 219, 46))
    im.alpha_composite(texto('ALIADO', 36, CARAMELO, 'Bold', sombra=False, espaco=10), (48, 44))
    im.alpha_composite(texto('Nº 001', 120, CREME, sombra=False), (40, 90))
    im.alpha_composite(texto(ARROBA, 48, CREME, 'SemiBold', sombra=False), (48, 260))
    tag = etiqueta('GOLPE', 34)
    im.alpha_composite(tag.rotate(-6, expand=True, resample=Image.Resampling.BICUBIC), (w - tag.width - 40, 34))
    return im


def cena_vagas(t):
    """"São só dez vagas, até sexta, às nove da noite.": ten open places, and the deadline."""
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    base.faixas_da_jaqueta(tela, t)
    aparece(tela, texto('SÓ', 90, CREME), W/2, 300, T['sao'] - .02, t)
    aparece(tela, texto('10 VAGAS', 150, VERMELHO_TEXTO, contorno=8), W/2, 440, T['dez'], t, tipo='pancada')
    for i in range(10):
        coluna, linha = i % 2, i // 2
        x, y = (300 if coluna == 0 else 780), 690 + linha*120
        aparece(tela, vaga(i + 1), x, y, T['sao'] + .04*i, t)
    if t >= T['ate'] - .05:
        colar(tela, relogio(t), W/2, 1400, sai_volta(prog(t, T['ate'] - .05, T['ate'] + .25)), alfa=prog(t, T['ate'] - .05, T['ate']))
    return sacudir(tela, t, T['dez'], 12, cor=AZUL_ESCURO)


@lru_cache(maxsize=10)
def vaga(n):
    im = retangulo((440, 96), 48, PAINEL + (235,), LINHA + (255,), 4)
    num = texto(f'{n:02d}', 40, CARAMELO, 'Bold', sombra=False)
    im.alpha_composite(num, (34, (96 - num.height)//2))
    s = texto('vaga aberta', 38, CREME, 'SemiBold', sombra=False)
    im.alpha_composite(s, (110, (96 - s.height)//2))
    return im


def relogio(t):
    """'Até sexta, 21h', with a clock whose hand runs."""
    painel = retangulo((760, 150), 75, VERMELHO + (255,), TINTA + (255,), 6)
    d = ImageDraw.Draw(painel)
    cx, cy, r = 92, 75, 46
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=CREME + (255,), outline=TINTA + (255,), width=5)
    a = (t - T['ate'])*5
    d.line((cx, cy, cx + r*.75*math.sin(a), cy - r*.75*math.cos(a)), fill=TINTA + (255,), width=6)
    d.line((cx, cy, cx + r*.5*math.sin(a/12), cy - r*.5*math.cos(a/12)), fill=TINTA + (255,), width=7)
    s = texto('ATÉ SEXTA, 21H', 66, CREME, sombra=False)
    painel.alpha_composite(s, (170, (150 - s.height)//2))
    return painel


def cena_final(t):
    """The close, with no voice: Zinho calls you in, "Faça parte da história"."""
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    base.raios(tela, t)
    zinho_sobe(tela, t, C_FINAL + .05, 'chamando', .74, 1990)
    aparece(tela, texto('FAÇA PARTE', 120, CREME, contorno=9), W/2, 330, C_FINAL + .3, t, tipo='pancada')
    aparece(tela, texto('DA HISTÓRIA', 104, OURO, contorno=8), W/2, 470, C_FINAL + .55, t, tipo='pancada')
    aparece(tela, etiqueta('VIRE ALIADO', 76), W/2, 640, C_FINAL + .95, t, angulo=4)
    cintilar(tela, t, C_FINAL + 1.0, ((95, 245), (990, 300), (125, 505), (955, 545), (880, 760)))
    return sacudir(tela, t, C_FINAL + .3, 14, cor=VERMELHO_ESCURO)


def cintilar(tela, t, inicio, pontos):
    """Sparkles that come and go one after another at `pontos`, like the thank-you's around Part 3's card."""
    for i, (x, y) in enumerate(pontos):
        desde = t - inicio - i*.12
        if desde < 0:
            continue
        idade = desde % 1.1
        k = math.sin(limite(idade/.7)*math.pi)
        if k > 0:
            colar(tela, estrela(), x, y, .3 + .8*k, idade*90, k)


def empurra(t, t0, dur, antes, depois, vertical=False):
    """A quick push: the next shot slides in and shoves the last one out."""
    p = sai_cubica(prog(t, t0, t0 + dur))
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    if vertical:
        tela.alpha_composite(antes(t), (0, round(-H*p)))
        tela.alpha_composite(depois(t), (0, round(H*(1 - p))))
    else:
        tela.alpha_composite(antes(t), (round(-W*p), 0))
        tela.alpha_composite(depois(t), (round(W*(1 - p)), 0))
    return tela


# Each shot from the time it starts, with the way it comes in.
ROTEIRO = [
    (0.0, cena_pergunta, None),
    (C_VIRE, cena_vire, None),
    (C_ARROBA, cena_arroba, ('faixa', VERMELHO, True)),
    (C_CELULAR, cena_celular, ('empurra', False)),
    (C_MURO, cena_muro, ('empurra', False)),
    (C_TV, cena_tv, ('empurra', False)),
    (C_CREDITOS, cena_creditos, ('empurra', False)),
    (C_LEGENDA, cena_legenda, ('faixa', AZUL_ESCURO, False)),
    (C_VAGAS, cena_vagas, ('empurra', False)),
    (C_FINAL, cena_final, ('faixa', VERMELHO, True)),
]


def quadro(t):
    carregar()
    i = max(k for k, (inicio, _, _) in enumerate(ROTEIRO) if t >= inicio)
    inicio, cena, entrada = ROTEIRO[i]
    if entrada and i > 0:
        anterior = ROTEIRO[i - 1][1]
        if entrada[0] == 'faixa' and t < inicio + .3:
            tela = passagem(t, inicio, .3, anterior, cena, entrada[1], para_direita=entrada[2])
        elif entrada[0] == 'empurra' and t < inicio + EMPURRA:
            tela = empurra(t, inicio, EMPURRA, anterior, cena, vertical=entrada[1])
        else:
            tela = cena(t)
    else:
        tela = cena(t)
    tela.alpha_composite(base.A['grao'])
    return tela.convert('RGB')


def quadro_bytes(i):
    return quadro(i/FPS).tobytes()


# ---------------------------------------------------------------- sound

def spray(dur):
    """A spray can's hiss."""
    rng = np.random.default_rng(13)
    n = int(dur*SR)
    som = base.ruido_em_faixa(n, 2500, 9000, rng)*np.minimum(1, np.arange(n)/(.03*SR))*np.minimum(1, (n - np.arange(n))/(.08*SR))
    return som.astype(np.float32)


def eventos():
    """Every effect, tied to the narrator's words: time, effect, gain in dB, pan, speed."""
    ev = [
        (.02, 'whoosh', -12, 0, 1), (T['parte'] - .05, 'impacto-suave', -11, 0, 1), (T['parte'] + .05, 'whoosh', -15, 0, 1.6),
        (C_VIRE, 'impacto', -6, 0, 1), (C_VIRE + .02, 'whoosh', -10, 0, 1.05), (T['aliado'], 'impacto-suave', -10, 0, 1),
        (C_ARROBA - .02, 'whoosh', -11, -.6, .9), (T['o_seu'], 'pop', -13, 0, 1), (T['entra'], 'impacto-suave', -11, 0, 1),
        (C_CELULAR, 'whoosh', -14, .4, 1.6), (C_CELULAR + .12, 'notificacao', -11, .2, 1),
        (C_MURO, 'whoosh', -14, .4, 1.6), (C_TV, 'whoosh', -14, .4, 1.6), (C_TV + .1, 'impacto-suave', -14, 0, 1.3),
        (C_CREDITOS, 'whoosh', -14, .4, 1.6),
        (C_LEGENDA - .02, 'whoosh', -8, .6, .9), (C_LEGENDA + .2, 'whoosh', -14, 0, 1.1), (T['legenda'], 'pop', -15, 0, 1.3),
        (T['numero'] - .06, 'impacto', -8, 0, 1),
        (C_VAGAS, 'whoosh', -13, .4, 1.4), (T['dez'], 'impacto-suave', -10, 0, 1),
        # The close, with no voice: the effects can be fuller.
        (C_FINAL - .02, 'whoosh', -6, -.6, .9), (C_FINAL + .05, 'whoosh', -9, 0, 1.05), (C_FINAL + .3, 'impacto', -4, 0, 1),
        (C_FINAL + .55, 'impacto-suave', -6, 0, 1), (C_FINAL + .95, 'pop', -7, 0, 1), (C_FINAL + 1.0, 'notificacao', -10, 0, 1),
    ]
    # The @ typing itself, one tick a letter.
    letras = len(ARROBA) - 1
    for k in range(letras):
        ev.append((T['arroba'] + (T['entra'] - T['arroba'])*k/letras, 'tique', -13, 0, 1.2))
    # The ten places popping up, and the clock ticking.
    for i in range(10):
        ev.append((T['sao'] + .04*i, 'pop', -19, (-1)**i*.4, 1 + .06*i))
    for i in range(6):
        ev.append((T['ate'] + .1 + i*.16, 'tique', -14, 0, 1))
    return ev


def voz():
    """The narration up to "às nove da noite.", faded out right after it."""
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(NARRACAO), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    som = np.frombuffer(pcm, np.float32)
    fim = int((_PALAVRAS[ULTIMA]['end'] + .12)*SR)
    som = som[:fim].copy()
    queda = int(.06*SR)
    som[-queda:] *= np.linspace(1, 0, queda, dtype=np.float32)
    return som/np.abs(som).max()*10**(-3/20)


def abaixar_sob_a_voz(fala, n):
    """A gain for the effects that steps them back about 7 dB while the narrator speaks."""
    passo = int(.01*SR)
    blocos = np.abs(fala[:len(fala)//passo*passo]).reshape(-1, passo).max(axis=1)
    segura = np.array([blocos[max(0, j - 25):j + 15].max() for j in range(len(blocos))])
    ganho = np.convolve(1 - .55*np.clip(segura/(.3*segura.max()), 0, 1), np.ones(8)/8, mode='same')
    curva = np.ones(n, np.float32)
    i = int(ATRASO*SR)
    trecho = np.repeat(ganho, passo)[:n - i]
    curva[i:i + len(trecho)] = trecho
    return curva


def mixar(caminho):
    n = int(DURACAO*SR)
    som = np.zeros((n, 2), np.float32)
    cache = {}

    def por(inicio, mono, ganho_db, pan):
        i = int(inicio*SR)
        mono = mono[:n - i]*10**(ganho_db/20)
        a = (pan + 1)*math.pi/4
        som[i:i + len(mono), 0] += mono*math.cos(a)
        som[i:i + len(mono), 1] += mono*math.sin(a)

    for inicio, nome, ganho, pan, velocidade in eventos():
        amostra = cache.setdefault(nome, base.ler_efeito(nome))
        if velocidade != 1:
            amostra = np.interp(np.arange(0, len(amostra) - 1, velocidade), np.arange(len(amostra)), amostra).astype(np.float32)
        por(inicio, amostra, ganho, pan)
    por(C_MURO + .05, spray(.36), -16, .2)
    brilho = base.brilho_sonoro()
    por(T['parte'] + .45, brilho, -16, 0)
    por(C_CREDITOS + .15, brilho, -18, 0)
    por(C_FINAL + 1.0, brilho, -12, 0)
    fala = voz()
    som *= abaixar_sob_a_voz(fala, n)[:, None]
    por(ATRASO, fala, 0, 0)
    som = np.tanh(som*1.1)/np.tanh(1.1)
    with wave.open(str(caminho), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(som, -1, 1)*32767).astype('<i2').tobytes())


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--quadros', type=float, nargs='*', help='only render stills at these times, into work/')
    ap.add_argument('--saida', type=Path, default=SAIDA)
    args = ap.parse_args()
    trabalho = HERE / 'work'
    trabalho.mkdir(exist_ok=True)
    if args.quadros:
        for t in args.quadros:
            quadro(t).save(trabalho / f'quadro-{t:05.2f}.png')
        print(' '.join(f'{k}={v:.2f}' for k, v in T.items()), f'fim={DURACAO}')
        return
    audio, normalizado = trabalho / 'som.wav', trabalho / 'som-normalizado.wav'
    mixar(audio)
    base.normalizar(audio, normalizado)
    total = round(DURACAO*FPS)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-i', str(normalizado), '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR), '-movflags', '+faststart', '-shortest',
           str(args.saida)]
    ffmpeg = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(initializer=carregar) as pool:
        for i, dados in enumerate(pool.imap(quadro_bytes, range(total), chunksize=3)):
            ffmpeg.stdin.write(dados)
            if i % 90 == 0:
                print(f'quadro {i}/{total}', flush=True)
    ffmpeg.stdin.close()
    if ffmpeg.wait():
        raise SystemExit('ffmpeg falhou')
    print(args.saida)


if __name__ == '__main__':
    main()
