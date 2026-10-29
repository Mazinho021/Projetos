#!/usr/bin/env python3
"""The "mais de 100 seguidores" thank-you, animated frame by frame.

A new take on the 100-followers video, with its own animation: 1080 × 1920 at 30 fps,
15.6 s, no narration (the sound is the series' effects, plus applause and a riser made here).
It plays with Part 1's backpack, which came back with clothes instead of the money:

  0.0–2.8   "LEMBRA DA MOCHILA?"     Zinho slides in under a spotlight; a red marker rings the bag.
  2.8–6.0   "DESSA VEZ VEIO CHEIA!"  the bag shakes and bursts with followers; a counter rolls to 100.
  6.0–9.2   "MAIS DE 100 SEGUIDORES" the 100 takes the screen over turning rays, confetti cannons fire
                                     and Zinho's surprised face peeks in.
  8.9–12.4  "OBRIGADO, ALIADOS!"     a polaroid of Zinho smiling drops in, hearts rise.
  12.1–15.6 "A PARTE 3 TÁ CHEGANDO." the covers of Parts 1 and 2 fan out, the third card flips to
                                     "em breve" and the follow button closes it.

Every element is a function of time, so frames render in any order, in parallel. The cut-outs
come from recortar.py; the covers from capas/; the polaroid from episodio-01/retrato-zinho.png.

    python animar.py                          # the video, next to this script
    python animar.py --quadros 1.2 6.5 13.9   # stills for a look, in work/
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import json
import math
from multiprocessing import Pool
from pathlib import Path
import random
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
SERIE = HERE.parents[1]
FONTES = SERIE / 'fontes'
EFEITOS = [SERIE / 'episodio-01' / 'montagem' / 'efeitos', SERIE / 'episodio-02' / 'montagem' / 'efeitos']
SAIDA = HERE / 'agradecimento-mais-de-100-seguidores.mp4'
W, H, FPS = 1080, 1920, 30
DURACAO = 15.6
SR = 48000

# Zinho's colours, as on the site: the room at night, the hoodie, the jacket and its stripes, the lamp.
FUNDO = (20, 14, 11)
PAINEL = (36, 25, 20)
LINHA = (59, 42, 32)
CREME = (247, 236, 219)
AREIA = (194, 173, 152)
VERMELHO = (200, 40, 31)
VERMELHO_ESCURO = (110, 11, 11)
VERMELHO_TEXTO = (240, 71, 58)
AZUL = (34, 64, 154)
AZUL_ESCURO = (14, 24, 57)
CARAMELO = (217, 135, 74)
TINTA = (26, 15, 10)
OURO = (246, 196, 83)

# Where things sit. Text stays between y = 280 and 1515 and inside x = 90…990, clear of what
# Reels and TikTok draw over the video.
ZINHO_PES = (575, 1775)       # bottom centre of Zinho in scenes 1–2
ZINHO_ESCALA = 1.12
BOCA_DA_MOCHILA = (75, 640)   # the bag's opening, in the cut-out's pixels
MOCHILA = (2, 570, 150, 860)  # the bag, in the cut-out's pixels
CONTADOR_Y = 430
CEM_Y = 830


# ---------------------------------------------------------------- easing

def limite(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, a, b):
    return limite((t - a) / (b - a))


def suave(x):
    return x*x*(3 - 2*x)


def sai_cubica(x):
    return 1 - (1 - x)**3


def sai_volta(x, s=1.70158):
    x -= 1
    return 1 + (s + 1)*x**3 + s*x**2


def elastico(x):
    if x <= 0 or x >= 1:
        return limite(x)
    return 2**(-10*x) * math.sin((x*10 - .75) * 2*math.pi/3) + 1


def tremor(t, inicio, dur=.4, amp=14):
    """Camera shake: an (x, y) offset that dies out `dur` seconds after `inicio`."""
    idade = t - inicio
    if idade < 0 or idade > dur:
        return 0.0, 0.0
    k = amp * (1 - idade/dur)**2
    return k*math.sin(idade*61), k*math.cos(idade*47)


# ---------------------------------------------------------------- drawing

@lru_cache(maxsize=None)
def fonte(tamanho, peso='ExtraBold'):
    return ImageFont.truetype(str(FONTES / f'Poppins-{peso}.ttf'), tamanho)


@lru_cache(maxsize=256)
def texto(valor, tamanho, cor=CREME, peso='ExtraBold', contorno=0, cor_contorno=TINTA, sombra=True, espaco=0):
    """A line of text as an RGBA sprite, with an optional outline, soft shadow and letter spacing."""
    f = fonte(tamanho, peso)
    largura = sum(f.getlength(c) for c in valor) + espaco*(len(valor) - 1) if espaco else f.getlength(valor)
    folga = contorno + 24
    im = Image.new('RGBA', (math.ceil(largura) + 2*folga, round(tamanho*1.32) + 2*folga), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)

    def escrever(draw, dx, dy, fill, **kw):
        if not espaco:
            draw.text((folga + dx, folga + dy), valor, font=f, fill=fill, **kw)
            return
        x = folga + dx
        for c in valor:
            draw.text((x, folga + dy), c, font=f, fill=fill, **kw)
            x += f.getlength(c) + espaco

    if sombra:
        s = Image.new('RGBA', im.size, (0, 0, 0, 0))
        escrever(ImageDraw.Draw(s), 0, round(tamanho*.06), (0, 0, 0, 150), stroke_width=contorno, stroke_fill=(0, 0, 0, 150))
        im.alpha_composite(s.filter(ImageFilter.GaussianBlur(max(2, tamanho*.05))))
    escrever(d, 0, 0, cor + (255,), stroke_width=contorno, stroke_fill=cor_contorno + (255,))
    return im.crop(im.getchannel('A').getbbox())


def colar(tela, sprite, x, y, escala=1.0, angulo=0.0, alfa=1.0, ancora=(.5, .5), escala_x=1.0):
    """Draw `sprite` with its point `ancora` (fractions of its size) on (x, y), scaled about that
    point and turned `angulo` degrees anticlockwise about it."""
    if alfa <= .004 or escala <= .004 or escala_x <= .004:
        return
    sw, sh = max(1, round(sprite.width*escala*escala_x)), max(1, round(sprite.height*escala))
    s = sprite if (sw, sh) == sprite.size else sprite.resize((sw, sh), Image.Resampling.BICUBIC)
    dx, dy = (ancora[0] - .5)*sw, (ancora[1] - .5)*sh
    if abs(angulo) > .05:
        s = s.rotate(angulo, resample=Image.Resampling.BICUBIC, expand=True)
        a = math.radians(angulo)
        dx, dy = dx*math.cos(a) + dy*math.sin(a), -dx*math.sin(a) + dy*math.cos(a)
    if alfa < .996:
        s = s.copy()
        s.putalpha(s.getchannel('A').point(lambda v: round(v*alfa)))
    px, py = round(x - s.width/2 - dx), round(y - s.height/2 - dy)
    sx, sy = max(0, -px), max(0, -py)
    if sx >= s.width or sy >= s.height or px >= tela.width or py >= tela.height:
        return
    tela.alpha_composite(s, (max(0, px), max(0, py)), (sx, sy))


def retangulo(tamanho, raio, cor, borda=None, largura=0):
    im = Image.new('RGBA', tamanho, (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, tamanho[0] - 1, tamanho[1] - 1), raio, fill=cor, outline=borda, width=largura)
    return im


def sombra_de(sprite, raio=18, opacidade=150):
    s = Image.new('RGBA', (sprite.width + 4*raio, sprite.height + 4*raio), (0, 0, 0, 0))
    preto = Image.new('RGBA', sprite.size, (0, 0, 0, opacidade))
    s.paste(preto, (2*raio, 2*raio), sprite.getchannel('A'))
    return s.filter(ImageFilter.GaussianBlur(raio))


# ---------------------------------------------------------------- assets (loaded once per process)

A = {}


def carregar_assets():
    if A:
        return
    A['corpo'] = Image.open(HERE / 'recortes' / 'zinho-corpo.png').convert('RGBA')
    cabeca = Image.open(HERE / 'recortes' / 'zinho-surpreso.png').convert('RGBA')
    # The sheet's paint strokes around the shoulders go: the face fades out above them.
    alfa = np.asarray(cabeca.getchannel('A'), dtype=np.float32)
    rampa = np.clip((cabeca.height*.93 - np.arange(cabeca.height)) / (cabeca.height*.16), 0, 1)[:, None]
    cabeca.putalpha(Image.fromarray((alfa*rampa).astype(np.uint8)))
    A['cabeca'] = cabeca

    # Scene 1–2 ground: the jacket's navy at night under a spotlight.
    y = np.linspace(0, 1, H)[:, None]
    base = np.array(AZUL_ESCURO)*(1 - .45*y)[..., None] + np.array((4, 6, 16))*(.45*y)[..., None]
    fundo = np.repeat(base, W, axis=1)
    xs = np.arange(W)[None, :]
    cone = np.clip(1 - np.abs(xs - W/2) / (150 + 430*y), 0, 1)**1.6 * (.25 + .75*y)
    piso = np.exp(-(((xs - ZINHO_PES[0])/440)**2 + ((np.arange(H)[:, None] - ZINHO_PES[1] + 10)/90)**2))
    luz = np.clip(cone*.33 + piso*.42, 0, 1)[..., None]
    fundo = fundo*(1 - luz) + np.array(CREME)*luz
    A['holofote'] = Image.fromarray(np.clip(fundo, 0, 255).astype(np.uint8)).convert('RGBA')
    sombra = Image.new('RGBA', (600, 170), (0, 0, 0, 0))
    ImageDraw.Draw(sombra).ellipse((40, 40, 559, 129), fill=(0, 0, 0, 120))
    A['sombra_pes'] = sombra.filter(ImageFilter.GaussianBlur(14))

    # Scene 3: dark edges over the turning rays.
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.hypot((xx - W/2)/W, (yy - CEM_Y)/H)
    v = np.clip((r - .18)/.55, 0, 1)**1.4
    vinheta = np.zeros((H, W, 4), np.uint8)
    vinheta[..., :3] = VERMELHO_ESCURO
    vinheta[..., 3] = (v*215).astype(np.uint8)
    A['vinheta'] = Image.fromarray(vinheta)

    # Scene 4: cream paper with faint grain and pinstripes.
    rng = np.random.default_rng(7)
    papel = np.ones((H, W, 3))*np.array(CREME) + rng.normal(0, 3.2, (H, W, 1))
    listra = ((xx + yy*0.42) % 64) < 3
    papel[listra] -= 7
    A['papel'] = Image.fromarray(np.clip(papel, 0, 255).astype(np.uint8)).convert('RGBA')

    # Grain over everything, to tie flat colour and drawings together.
    grao = np.zeros((H, W, 4), np.uint8)
    grao[..., :3] = 255
    grao[..., 3] = (rng.random((H, W)) < .5) * rng.integers(0, 14, (H, W))
    A['grao'] = Image.fromarray(grao)

    # The polaroid: Zinho smiling, from Part 1's portrait.
    retrato = Image.open(SERIE / 'episodio-01' / 'retrato-zinho.png').convert('RGB').crop((214, 0, 1234, 1060))
    foto = retrato.resize((560, 582), Image.Resampling.LANCZOS)
    pol = Image.new('RGBA', (620, 760), (0, 0, 0, 0))
    ImageDraw.Draw(pol).rounded_rectangle((0, 0, 619, 759), 10, fill=(252, 248, 239, 255))
    pol.paste(foto, (30, 30))
    ImageDraw.Draw(pol).rectangle((30, 30, 589, 611), outline=(0, 0, 0, 40), width=2)
    legenda = texto('valeu demais!', 50, TINTA, 'Bold', sombra=False)
    pol.alpha_composite(legenda, ((620 - legenda.width)//2, 665 - legenda.height//2))
    fita = Image.new('RGBA', (170, 52), (236, 222, 190, 190))
    pol.alpha_composite(fita.rotate(18, expand=True, resample=Image.Resampling.BICUBIC), (-40, -32))
    pol.alpha_composite(fita.rotate(-18, expand=True, resample=Image.Resampling.BICUBIC), (470, -32))
    A['polaroide'] = pol
    A['polaroide_sombra'] = sombra_de(pol, 22, 120)

    # Scene 5 cards: the covers of Parts 1 and 2, and Part 3's back and face.
    for n in (1, 2):
        capa = Image.open(SERIE / 'capas' / f'capa-parte-0{n}.png').convert('RGB').resize((300, 533), Image.Resampling.LANCZOS)
        A[f'carta{n}'] = carta(capa)
    A['verso'] = carta(None, 'verso')
    A['frente'] = carta(None, 'frente')
    A['carta_sombra'] = sombra_de(retangulo((330, 586), 26, (0, 0, 0, 255)), 20, 130)
    A['carimbo'] = carimbo('VOCÊ DECIDE')


def carta(imagem, lado=None, tamanho=(330, 586)):
    w, h = tamanho
    im = Image.new('RGBA', tamanho, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if imagem is not None:
        mascara = Image.new('L', tamanho, 0)
        ImageDraw.Draw(mascara).rounded_rectangle((0, 0, w - 1, h - 1), 26, fill=255)
        foto = imagem.resize(tamanho, Image.Resampling.LANCZOS).convert('RGBA')
        im.paste(foto, (0, 0), mascara)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 26, outline=CREME + (255,), width=6)
        return im
    if lado == 'verso':
        d.rounded_rectangle((0, 0, w - 1, h - 1), 26, fill=AZUL_ESCURO + (255,), outline=CREME + (255,), width=6)
        for dx in (-34, 34):
            d.polygon([(w*.5 + dx - 16 - 140, h), (w*.5 + dx + 16 - 140, h), (w*.5 + dx + 16 + 140, 0), (w*.5 + dx - 16 + 140, 0)],
                      fill=(247, 236, 219, 40))
        q = texto('?', 230, CREME, sombra=False)
        im.alpha_composite(q, ((w - q.width)//2, (h - q.height)//2))
        return im
    d.rounded_rectangle((0, 0, w - 1, h - 1), 26, fill=FUNDO + (255,))
    # The dashed border of the site's "em breve" card.
    passo, traco = 26, 15
    for x in range(26, w - 26, passo):
        d.line((x, 8, min(x + traco, w - 26), 8), fill=AREIA + (255,), width=5)
        d.line((x, h - 9, min(x + traco, w - 26), h - 9), fill=AREIA + (255,), width=5)
    for yv in range(26, h - 26, passo):
        d.line((8, yv, 8, min(yv + traco, h - 26)), fill=AREIA + (255,), width=5)
        d.line((w - 9, yv, w - 9, min(yv + traco, h - 26)), fill=AREIA + (255,), width=5)
    for valor, tam, cor, peso, cy in (('PARTE 3', 74, VERMELHO_TEXTO, 'ExtraBold', .38), ('em breve', 44, CREME, 'Bold', .50)):
        s = texto(valor, tam, cor, peso, sombra=False)
        im.alpha_composite(s, ((w - s.width)//2, round(h*cy - s.height/2)))
    return im


def carimbo(valor):
    s = texto(valor, 38, VERMELHO, 'ExtraBold', sombra=False)
    w, h = s.width + 56, s.height + 34
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((3, 3, w - 4, h - 4), 12, fill=(247, 236, 219, 245), outline=VERMELHO + (255,), width=7)
    im.alpha_composite(s, ((w - s.width)//2, (h - s.height)//2))
    return im


@lru_cache(maxsize=32)
def avatar(diametro, cor):
    """A follower: a coloured disc with a person in it, outlined like the drawings."""
    d = diametro
    im = Image.new('RGBA', (d, d), (0, 0, 0, 0))
    g = ImageDraw.Draw(im)
    g.ellipse((0, 0, d - 1, d - 1), fill=TINTA + (255,))
    b = max(3, d//14)
    g.ellipse((b, b, d - 1 - b, d - 1 - b), fill=cor + (255,))
    pessoa = Image.new('RGBA', (d, d), (0, 0, 0, 0))
    p = ImageDraw.Draw(pessoa)
    tinta = CREME if cor != CREME else AZUL
    p.ellipse((d*.34, d*.18, d*.66, d*.50), fill=tinta + (255,))
    p.ellipse((d*.17, d*.56, d*.83, d*1.12), fill=tinta + (255,))
    disco = Image.new('L', (d, d), 0)
    ImageDraw.Draw(disco).ellipse((b, b, d - 1 - b, d - 1 - b), fill=255)
    im.paste(pessoa, (0, 0), Image.composite(pessoa.getchannel('A'), Image.new('L', (d, d), 0), disco))
    return im


@lru_cache(maxsize=4)
def mais_um(tamanho):
    s = texto('+1', tamanho, CREME, sombra=False)
    w, h = s.width + tamanho, s.height + tamanho//2
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), h//2, fill=VERMELHO + (255,), outline=TINTA + (255,), width=max(3, tamanho//10))
    im.alpha_composite(s, ((w - s.width)//2, (h - s.height)//2))
    return im


@lru_cache(maxsize=8)
def coracao(tamanho):
    k = 4
    s = tamanho*k
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((0, 0, s*.56, s*.56), fill=VERMELHO_TEXTO + (255,))
    d.ellipse((s*.44, 0, s, s*.56), fill=VERMELHO_TEXTO + (255,))
    d.polygon([(s*.04, s*.38), (s*.96, s*.38), (s*.5, s*.95)], fill=VERMELHO_TEXTO + (255,))
    return im.resize((tamanho, tamanho), Image.Resampling.LANCZOS)


@lru_cache(maxsize=64)
def coluna_de_digitos(cor):
    """0–9 and 0 again, stacked, for the rolling counter."""
    altura = 236
    im = Image.new('RGBA', (170, altura*11), (0, 0, 0, 0))
    for i in range(11):
        s = texto(str(i % 10), 236, cor, sombra=False)
        im.alpha_composite(s, ((170 - s.width)//2, i*altura + (altura - s.height)//2))
    return im, altura


# ---------------------------------------------------------------- pieces of the scenes

def onde_no_mundo(px, py, t):
    """A point of Zinho's cut-out, in the scene, as he stands at time t."""
    x0, y0 = zinho_pose(t)[:2]
    c = A['corpo']
    return x0 + (px - c.width/2)*ZINHO_ESCALA, y0 - (c.height - py)*ZINHO_ESCALA


def zinho_pose(t):
    """Where Zinho's feet are, his tilt and his squash (x scale, y scale) in scenes 1–2."""
    x, y = ZINHO_PES
    # He starts out of the frame, so the first frame is the empty stage.
    entrada = prog(t, .05, .55)
    x += -920*(1 - sai_volta(entrada, 1.1))
    angulo = 9*(1 - sai_cubica(entrada))
    sx = sy = 1.0
    pouso = t - .55
    if 0 <= pouso < .35:
        k = math.sin(pouso/.35*math.pi)*(1 - pouso/.35)
        sx, sy = 1 + .05*k, 1 - .06*k
    # Breathing while he waits.
    y += 3*math.sin(t*2*math.pi*.8)
    # The bag starts to rumble, then the burst throws him up a little.
    if 3.0 <= t < 3.6:
        a = prog(t, 3.0, 3.6)
        x += 9*a*math.sin(t*78)
        angulo += 1.2*a*math.sin(t*53)
    pulo = t - 3.6
    if 0 <= pulo < .5:
        y -= 46*math.sin(pulo/.5*math.pi)
        k = max(0.0, 1 - pulo/.18)
        sx, sy = 1 + .05*k, 1 - .07*k
    return x, y, angulo, sx, sy


def desenhar_zinho(tela, t):
    x, y, angulo, sx, sy = zinho_pose(t)
    colar(tela, A['sombra_pes'], x, ZINHO_PES[1] + 8, 1 + .12*(y - ZINHO_PES[1])/60, alfa=.9)
    colar(tela, A['corpo'], x, y, ZINHO_ESCALA*sy, angulo, ancora=(.5, 1), escala_x=sx/sy)


def poeira(tela, t):
    """Dust drifting in the spotlight."""
    d = ImageDraw.Draw(tela)
    rnd = random.Random(3)
    for _ in range(46):
        x0, y0 = rnd.uniform(260, 820), rnd.uniform(200, 1700)
        vx, vy, fase = rnd.uniform(-9, 9), rnd.uniform(-22, -6), rnd.uniform(0, 6.3)
        r = rnd.uniform(1.4, 3.6)
        x = x0 + vx*t + 14*math.sin(t*.9 + fase)
        y = (y0 + vy*t) % 1700 + 120
        luz = max(0.0, 1 - abs(x - W/2)/(160 + .25*y))
        if luz > .05:
            d.ellipse((x - r, y - r, x + r, y + r), fill=CREME + (round(150*luz),))


def marcador(tela, t):
    """A red marker ring drawn around the bag, by hand."""
    p = prog(t, 1.70, 2.15)
    if p <= 0:
        return
    alfa = 1 - prog(t, 2.80, 3.05)
    if alfa <= 0:
        return
    l, tp, r, b = MOCHILA
    (x0, y0), (x1, y1) = onde_no_mundo(l, tp, t), onde_no_mundo(r, b, t)
    cx, cy, rx, ry = (x0 + x1)/2, (y0 + y1)/2, (x1 - x0)/2 + 34, (y1 - y0)/2 + 30
    camada = Image.new('RGBA', tela.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    volta = sai_cubica(p)*1.12
    pontos = []
    for i in range(int(90*volta) + 1):
        a = -math.pi*.62 + (i/90)*2*math.pi
        oscila = 1 + .04*math.sin(3*a + 1) + .03*(i/90)
        pontos.append((cx + rx*oscila*math.cos(a), cy + ry*oscila*math.sin(a)))
    if len(pontos) > 1:
        d.line(pontos, fill=VERMELHO_TEXTO + (round(255*alfa),), width=11, joint='curve')
    tela.alpha_composite(camada)


def seguidores_da_mochila(tela, t):
    """Followers bursting out of the bag: discs with a person in them and '+1' tags."""
    if t < 3.6:
        return
    bx, by = onde_no_mundo(*BOCA_DA_MOCHILA, t)
    rnd = random.Random(11)
    nascidos = 0.0
    cores = (VERMELHO, AZUL, CARAMELO, CREME, AZUL)
    for i in range(170):
        # Births speed up from 30 to 90 a second as the counter climbs.
        nascidos += 1/(30 + 60*min(1.0, i/120))
        nasce = 3.6 + nascidos
        # Up and to the left, away from his face.
        angulo = math.radians(rnd.uniform(-142, -84))
        vel, g = rnd.uniform(1100, 1900), rnd.uniform(1100, 1500)
        giro, tam = rnd.uniform(-260, 260), rnd.choice((54, 62, 70, 80, 90))
        tipo, cor = rnd.random(), cores[i % len(cores)]
        idade = t - nasce
        if idade < 0 or nasce > 6.0:
            continue
        x = bx + vel*math.cos(angulo)*idade
        y = by + vel*math.sin(angulo)*idade + .5*g*idade*idade
        if y > H + 120 or y < -200 or x < -150 or x > W + 150:
            continue
        sprite = mais_um(max(30, tam//2)) if tipo < .22 else avatar(tam, cor)
        colar(tela, sprite, x, y, min(1.0, .3 + idade*5), giro*idade if tipo >= .22 else giro*idade*.15)


def estouro(tela, t):
    """The ring of the burst at the bag's mouth."""
    idade = t - 3.6
    if not 0 <= idade < .45:
        return
    x, y = onde_no_mundo(*BOCA_DA_MOCHILA, t)
    r = 30 + 360*sai_cubica(idade/.45)
    camada = Image.new('RGBA', tela.size, (0, 0, 0, 0))
    ImageDraw.Draw(camada).ellipse((x - r, y - r, x + r, y + r), outline=CREME + (round(220*(1 - idade/.45)),), width=10)
    tela.alpha_composite(camada)


def contador(tela, t):
    """The followers counter, rolling like an odometer from 0 to 100."""
    if t < 4.35:
        return
    entra = prog(t, 4.35, 4.62)
    valor = 100*sai_cubica(prog(t, 4.45, 5.92))
    escala = .6 + .4*sai_volta(entra)
    painel = painel_do_contador()
    camada = Image.new('RGBA', (painel.width, painel.height), (0, 0, 0, 0))
    camada.alpha_composite(painel)
    rotulo = texto('SEGUIDORES', 38, CARAMELO, 'Bold', sombra=False, espaco=9)
    camada.alpha_composite(rotulo, ((painel.width - rotulo.width)//2, 34))
    velocidade = 100*3*(1 - prog(t, 4.45, 5.92))**2/1.47
    for coluna, casa in enumerate((100, 10, 1)):
        rolo = valor/casa
        if casa > 1:
            # The column turns over only during the last unit before it, as the ones roll from 9 to 0.
            rolo = valor//casa + max(0.0, valor % casa - (casa - 1))
        posicao = rolo % 10
        # Leading zeros stay dark; a digit lights up as soon as it is half rolled in.
        cor = CREME if (casa == 1 or rolo >= .5) else LINHA
        tira, alt = coluna_de_digitos(cor)
        janela = tira.crop((0, round(posicao*alt), tira.width, round(posicao*alt) + alt))
        borrao = min(14.0, velocidade/casa*.06)
        if borrao > .6:
            janela = janela.filter(ImageFilter.BoxBlur(borrao))
        camada.alpha_composite(janela, (60 + coluna*170, 92))
    colar(tela, camada, W/2, CONTADOR_Y, escala, alfa=prog(t, 4.35, 4.45))


@lru_cache(maxsize=1)
def painel_do_contador():
    p = retangulo((630, 352), 40, PAINEL + (238,), LINHA + (255,), 5)
    ImageDraw.Draw(p).rounded_rectangle((26, 82, 603, 330), 24, fill=(13, 9, 7, 255))
    return p


def raios(tela, t):
    """Turning rays in the hoodie's red, centred on the 100."""
    d = ImageDraw.Draw(tela)
    d.rectangle((0, 0, W, H), fill=VERMELHO + (255,))
    giro = math.radians(t*12)
    for i in range(18):
        a0 = giro + i*2*math.pi/18
        a1 = a0 + math.pi/18
        d.polygon([(W/2, CEM_Y), (W/2 + 2600*math.cos(a0), CEM_Y + 2600*math.sin(a0)),
                   (W/2 + 2600*math.cos(a1), CEM_Y + 2600*math.sin(a1))], fill=(178, 31, 24, 255))
    tela.alpha_composite(A['vinheta'])


def confete(tela, t, inicio=6.0):
    """Two cannons of confetti, from the bottom corners."""
    idade = t - inicio
    if idade < 0:
        return
    camada = Image.new('RGBA', tela.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(camada)
    cores = (CREME, OURO, AZUL, CARAMELO, (255, 255, 255), (127, 160, 255))
    rnd = random.Random(21)
    for i in range(320):
        lado = -1 if i % 2 else 1
        x0 = -30 if lado == 1 else W + 30
        angulo = math.radians(rnd.uniform(-82, -52))
        vel, arrasto = rnd.uniform(1700, 3300), rnd.uniform(1.8, 3.2)
        tam, prop = rnd.uniform(16, 30), rnd.uniform(.4, .75)
        giro, fase, vira = rnd.uniform(-10, 10), rnd.uniform(0, 6.3), rnd.uniform(5, 12)
        atraso = rnd.uniform(0, .12)
        a = idade - atraso
        if a < 0:
            continue
        g = 1300
        planar = (1 - math.exp(-arrasto*a))/arrasto
        x = x0 + lado*vel*math.cos(angulo)*planar + 18*math.sin(4*a + fase)*min(1, a)
        y = H + 30 + g/arrasto*a + (vel*math.sin(angulo) - g/arrasto)*planar
        if not (-40 < x < W + 40 and -40 < y < H + 40):
            continue
        cor = cores[i % len(cores)]
        meio_w, meio_h = tam/2, tam*prop/2*max(.15, abs(math.cos(vira*a + fase)))
        c, s = math.cos(giro*a + fase), math.sin(giro*a + fase)
        d.polygon([(x + px*c - py*s, y + px*s + py*c) for px, py in ((-meio_w, -meio_h), (meio_w, -meio_h), (meio_w, meio_h), (-meio_w, meio_h))],
                  fill=cor + (255,))
    tela.alpha_composite(camada)


def coracoes(tela, t):
    if t < 9.9:
        return
    rnd = random.Random(5)
    for i in range(26):
        nasce = 9.9 + i*.11
        idade = t - nasce
        lado = -1 if i % 2 else 1
        x0 = W/2 + lado*rnd.uniform(240, 420)
        y0 = rnd.uniform(1050, 1300)
        if idade < 0:
            continue
        y = y0 - idade*rnd.uniform(240, 360)
        x = x0 + 26*math.sin(idade*3 + i)
        alfa = min(1.0, idade*4)*limite(1 - (idade - 1.6)/.6)
        colar(tela, coracao(rnd.choice((34, 44, 54))), x, y, .6 + .4*min(1.0, idade*3), 12*math.sin(idade*2 + i), alfa)


def faixas_da_jaqueta(tela, t):
    d = ImageDraw.Draw(tela)
    d.rectangle((0, 0, W, H), fill=AZUL + (255,))
    camada = Image.new('RGBA', tela.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(camada)
    desliza = (t*90) % 400
    for base in (-400, 0, 400, 800, 1200):
        x = base + desliza
        for dx in (0, 70):
            g.polygon([(x + dx, H), (x + dx + 34, H), (x + dx + 34 + 900, 0), (x + dx + 900, 0)], fill=CREME + (24,))
    tela.alpha_composite(camada)
    escuro = Image.new('RGBA', tela.size, AZUL_ESCURO + (0,))
    mascara = Image.linear_gradient('L').resize((W, H)).point(lambda v: round(v*.62))
    escuro.putalpha(mascara)
    tela.alpha_composite(escuro)


# ---------------------------------------------------------------- text animations

def aparece(tela, sprite, x, y, inicio, t, sai=None, tipo='pop', angulo=0.0):
    """Text that pops (or slams) in at `inicio` and slides up and out at `sai`."""
    idade = t - inicio
    if idade < 0:
        return
    if tipo == 'pop':
        escala, alfa = .4 + .6*sai_volta(prog(idade, 0, .26)), prog(idade, 0, .08)
    elif tipo == 'pancada':
        escala, alfa = 1 + .9*(1 - sai_cubica(prog(idade, 0, .17))), prog(idade, 0, .06)
    else:  # 'sobe': rises into place
        escala, alfa = 1.0, prog(idade, 0, .1)
        y += 160*(1 - sai_volta(prog(idade, 0, .32)))
    if sai is not None and t >= sai:
        k = prog(t, sai, sai + .18)
        y -= 140*suave(k)
        alfa *= 1 - k
    colar(tela, sprite, x, y, escala, angulo, alfa)


# ---------------------------------------------------------------- scenes

def cena_mochila(t):
    mundo = A['holofote'].copy()
    poeira(mundo, t)
    desenhar_zinho(mundo, t)
    marcador(mundo, t)
    estouro(mundo, t)
    seguidores_da_mochila(mundo, t)
    # The camera leans into the bag once it starts to move.
    zoom = 1 + .16*suave(prog(t, 2.8, 3.5))
    if zoom > 1.001:
        # A fixed point near the bag, rather than the bag itself, so the frame does not shake with it.
        ax, ay = ZINHO_PES[0] - 190, ZINHO_PES[1] - 370
        w, h = W/zoom, H/zoom
        l, tp = ax - (ax/W)*w, ay - (ay/H)*h
        mundo = mundo.resize((W, H), Image.Resampling.BICUBIC, box=(l, tp, l + w, tp + h))
    tx, ty = tremor(t, .92, .35, 10)
    bx, by = tremor(t, 3.6, .5, 18)
    tela = Image.new('RGBA', (W, H), FUNDO + (255,))
    tela.alpha_composite(mundo, (round(tx + bx), round(ty + by)) if (tx or bx or ty or by) else (0, 0))
    aparece(tela, texto('LEMBRA DA', 84, CREME, contorno=0), W/2, 330, .62, t, sai=2.80)
    aparece(tela, texto('MOCHILA?', 150, VERMELHO_TEXTO, contorno=8), W/2, 470, .92, t, sai=2.82, tipo='pancada')
    aparece(tela, texto('DESSA VEZ', 84, CREME), W/2, 330, 2.95, t, sai=4.30)
    aparece(tela, texto('VEIO CHEIA!', 140, OURO, contorno=8), W/2, 470, 3.15, t, sai=4.32, tipo='pancada')
    contador(tela, t)
    return tela


def cena_cem(t):
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    raios(tela, t)
    confete(tela, t)
    # Zinho's surprised face peeks in from the bottom left and wobbles.
    entra = prog(t, 6.85, 7.22)
    if entra > 0:
        y = 2380 - 390*sai_volta(entra, 1.3)
        balanco = 4*math.sin((t - 7.22)*9)*math.exp(-max(0.0, t - 7.22)*1.6) if t > 7.22 else 0
        colar(tela, A['cabeca'], 250, y, 1.9, -11 + balanco, ancora=(.5, 1))
    # The 100 comes from the counter and takes the middle of the screen.
    k = sai_volta(prog(t, 6.0, 6.32), 1.4)
    pulso = 1 + .025*math.sin((t - 6.32)*2*math.pi*1.6) if t > 6.32 else 1
    cem = texto('100', 400, CREME, contorno=16)
    y = CONTADOR_Y + 40 + (CEM_Y - CONTADOR_Y - 40)*k
    colar(tela, cem, W/2, y, (.62 + .38*k)*pulso)
    aparece(tela, texto('MAIS DE', 118, CREME, contorno=9), W/2, 535, 6.14, t, tipo='pancada')
    etiqueta = etiqueta_seguidores()
    aparece(tela, etiqueta, W/2, 1110, 6.36, t, tipo='sobe', angulo=3)
    # The white flash of the cut.
    flash = 1 - prog(t, 6.0, 6.25)
    if flash > 0:
        tela.alpha_composite(Image.new('RGBA', (W, H), (255, 250, 240, round(200*flash))))
    tx, ty = tremor(t, 6.0, .5, 24)
    if tx or ty:
        movida = Image.new('RGBA', (W, H), VERMELHO_ESCURO + (255,))
        movida.alpha_composite(tela, (round(tx), round(ty)))
        tela = movida
    return tela


@lru_cache(maxsize=1)
def etiqueta_seguidores():
    s = texto('SEGUIDORES', 104, CREME, sombra=False)
    w, h = s.width + 88, s.height + 50
    im = Image.new('RGBA', (w, h + 14), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 14, w - 1, h + 13), 22, fill=AZUL_ESCURO + (255,))
    d.rounded_rectangle((0, 0, w - 1, h - 1), 22, fill=AZUL + (255,), outline=TINTA + (255,), width=6)
    im.alpha_composite(s, ((w - s.width)//2, (h - s.height)//2))
    return im


def cena_obrigado(t):
    tela = A['papel'].copy()
    coracoes(tela, t)
    queda = prog(t, 9.20, 9.62)
    x, y = W/2, -520 + (965 + 520)*sai_volta(queda, 1.05)
    angulo = 14 - 18*sai_cubica(queda) + (1.2*math.sin((t - 9.62)*2.2) if t > 9.62 else 0)
    if queda > 0:
        colar(tela, A['polaroide_sombra'], x + 14, y + 26, 1, angulo, .9)
        colar(tela, A['polaroide'], x, y, 1, angulo)
    tx, ty = tremor(t, 9.62, .3, 9)
    if tx or ty:
        movida = A['papel'].copy()
        movida.alpha_composite(tela, (round(tx), round(ty)))
        tela = movida
    aparece(tela, texto('OBRIGADO,', 116, TINTA, sombra=False), W/2, 318, 9.15, t)
    aparece(tela, texto('ALIADOS!', 150, VERMELHO, sombra=False), W/2, 458, 9.36, t, tipo='pancada')
    aparece(tela, texto('Cada um de vocês faz parte', 46, (107, 90, 74), 'SemiBold', sombra=False), W/2, 1418, 10.15, t, tipo='sobe')
    aparece(tela, texto('dessa história.', 46, (107, 90, 74), 'SemiBold', sombra=False), W/2, 1478, 10.28, t, tipo='sobe')
    return tela


def cena_parte3(t):
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    faixas_da_jaqueta(tela, t)
    cartas = (('carta1', 12.40, (300, 1000, 11), (330, 2350, 34)),
              ('carta2', 12.55, (780, 1000, -11), (750, 2350, -34)),
              ('meio', 12.70, (540, 960, 0), (540, 2450, 0)))
    for nome, inicio, (xf, yf, af), (xi, yi, ai) in cartas:
        p = prog(t, inicio, inicio + .42)
        if p <= 0:
            continue
        k = sai_volta(p, 1.2)
        x, y, a = xi + (xf - xi)*k, yi + (yf - yi)*k, ai + (af - ai)*sai_cubica(p)
        escala = 1.08 if nome == 'meio' else 1.0
        colar(tela, A['carta_sombra'], x + 12, y + 22, escala, a, .85)
        if nome != 'meio':
            colar(tela, A[nome], x, y, escala, a)
            continue
        vira = prog(t, 13.35, 13.75)
        largura = abs(math.cos(math.pi*vira))
        face = A['frente'] if vira >= .5 else A['verso']
        colar(tela, face, x, y - 30*math.sin(math.pi*vira), escala, a, escala_x=max(.02, largura))
        if t >= 13.95:
            pk = prog(t, 13.95, 14.12)
            colar(tela, A['carimbo'], x + 4, y + 170, 1 + 1.1*(1 - sai_cubica(pk)), 9, prog(t, 13.95, 14.0))
    brilho(tela, t)
    tx, ty = tremor(t, 13.95, .3, 12)
    if tx or ty:
        movida = Image.new('RGBA', (W, H), AZUL_ESCURO + (255,))
        movida.alpha_composite(tela, (round(tx), round(ty)))
        tela = movida
    aparece(tela, texto('A PARTE 3', 118, CREME), W/2, 318, 12.36, t)
    aparece(tela, texto('TÁ CHEGANDO.', 112, VERMELHO_TEXTO, contorno=8), W/2, 452, 12.56, t, tipo='pancada')
    aparece(tela, botao_seguir(), W/2, 1440, 14.35, t)
    return tela


def brilho(tela, t):
    """Sparkles around Part 3's card once it turns."""
    if t < 13.75:
        return
    for i, (dx, dy) in enumerate(((-205, -250), (210, -205), (-220, 120), (225, 230), (0, -355))):
        idade = (t - 13.75 - i*.12) % 1.1
        if t - 13.75 - i*.12 < 0:
            continue
        k = math.sin(limite(idade/.7)*math.pi)
        if k > 0:
            colar(tela, estrela(), 540 + dx, 960 + dy, .3 + .8*k, idade*90, k)


@lru_cache(maxsize=1)
def estrela():
    s = 120
    im = Image.new('RGBA', (s, s), (0, 0, 0, 0))
    pontos = []
    for i in range(8):
        r = s/2 if i % 2 == 0 else s*.12
        a = i*math.pi/4 - math.pi/2
        pontos.append((s/2 + r*math.cos(a), s/2 + r*math.sin(a)))
    ImageDraw.Draw(im).polygon(pontos, fill=OURO + (255,))
    return im


@lru_cache(maxsize=1)
def botao_seguir():
    s = texto('SEGUE @GOLPECARTOON', 52, CREME, sombra=False)
    w, h = s.width + 96, s.height + 54
    im = Image.new('RGBA', (w, h + 12), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 12, w - 1, h + 11), 26, fill=VERMELHO_ESCURO + (255,))
    d.rounded_rectangle((0, 0, w - 1, h - 1), 26, fill=VERMELHO + (255,))
    im.alpha_composite(s, ((w - s.width)//2, (h - s.height)//2))
    return im


def passagem(t, t0, dur, antes, depois, cor, para_direita=True):
    """A slanted band in `cor` that sweeps across the screen, from the scene `antes` to `depois`."""
    p = suave(prog(t, t0, t0 + dur))
    tela = antes(t)
    nova = depois(t)
    inclina = .36*H
    # The band's top edge, from just off the left of the screen to where its bottom has left the right.
    frente = -260 + (W + inclina + 520)*p
    if not para_direita:
        frente = W - frente
    mascara = Image.new('L', (W, H), 0)
    m = ImageDraw.Draw(mascara)
    sinal = 1 if para_direita else -1
    lado = -9999*sinal
    m.polygon([(lado, 0), (frente, 0), (frente - sinal*inclina, H), (lado, H)], fill=255)
    tela.paste(nova, (0, 0), mascara)
    faixa = ImageDraw.Draw(tela)
    for largura, c in ((150, cor), (26, CREME)):
        meio = frente - sinal*75
        faixa.polygon([(meio - largura/2, 0), (meio + largura/2, 0), (meio + largura/2 - sinal*inclina, H), (meio - largura/2 - sinal*inclina, H)],
                      fill=c + (255,))
    return tela


def quadro(t):
    carregar_assets()
    if t < 6.0:
        tela = cena_mochila(t)
    elif t < 8.86:
        tela = cena_cem(t)
    elif t < 9.16:
        tela = passagem(t, 8.86, .30, cena_cem, cena_obrigado, VERMELHO)
    elif t < 12.06:
        tela = cena_obrigado(t)
    elif t < 12.36:
        tela = passagem(t, 12.06, .30, cena_obrigado, cena_parte3, AZUL_ESCURO, para_direita=False)
    else:
        tela = cena_parte3(t)
    tela.alpha_composite(A['grao'])
    return tela.convert('RGB')


def quadro_bytes(i):
    return quadro(i/FPS).tobytes()


# ---------------------------------------------------------------- sound

def ler_efeito(nome):
    for pasta in EFEITOS:
        caminho = pasta / f'{nome}.wav'
        if caminho.exists():
            with wave.open(str(caminho)) as w:
                assert w.getframerate() == SR and w.getnchannels() == 1 and w.getsampwidth() == 2, caminho
                return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32)/32768
    raise FileNotFoundError(nome)


def ruido_em_faixa(n, baixo, alto, rng):
    espectro = np.fft.rfft(rng.normal(0, 1, n))
    f = np.fft.rfftfreq(n, 1/SR)
    espectro[(f < baixo) | (f > alto)] = 0
    s = np.fft.irfft(espectro, n)
    return s/np.abs(s).max()


def aplausos(dur, rng):
    """Applause: a few dozen people clapping, each clap a short burst of band-limited noise."""
    n = int(dur*SR)
    som = np.zeros(n, np.float32)
    palma = ruido_em_faixa(int(.05*SR), 700, 5200, rng)*np.exp(-np.arange(int(.05*SR))/(SR*.009))
    for _ in range(34):
        t = rng.uniform(0, .25)
        ritmo = rng.uniform(.18, .3)
        while t < dur:
            i = int(t*SR)
            pedaco = palma[:n - i]*rng.uniform(.25, 1)
            som[i:i + len(pedaco)] += pedaco
            t += ritmo*rng.uniform(.85, 1.15)
    envelope = np.minimum(1, np.arange(n)/(.25*SR))*np.minimum(1, (n - np.arange(n))/(.9*SR))
    return som*envelope/np.abs(som).max()


def subida(dur, rng):
    """A riser: noise that climbs in pitch and loudness up to the reveal."""
    n = int(dur*SR)
    som = np.zeros(n, np.float32)
    passo = int(.05*SR)
    for i in range(0, n, passo):
        k = i/n
        bloco = ruido_em_faixa(passo*2, 300 + 5000*k**2, 1200 + 9000*k**2, rng)[:min(passo, n - i)]
        som[i:i + len(bloco)] += bloco*(.1 + .9*k**2)
    t = np.arange(n)/SR
    som += .35*np.sin(2*np.pi*(180*t + 420*t**2/dur))*(t/dur)**2
    return som/np.abs(som).max()


def brilho_sonoro():
    """A sparkle: four bell notes going up, for the thank-you line and Part 3's card."""
    dur = 1.1
    n = int(dur*SR)
    t = np.arange(n)/SR
    som = np.zeros(n, np.float32)
    for k, f in enumerate((1318.5, 1661.2, 1975.5, 2637.0)):  # E6, G#6, B6, E7
        a = t - k*.065
        nota = np.where(a >= 0, 1.0, 0.0)*np.exp(-np.clip(a, 0, None)/.22)
        som += (np.sin(2*np.pi*f*a) + .35*np.sin(2*np.pi*f*2.76*a)*np.exp(-np.clip(a, 0, None)/.06))*nota*(.8 + .1*k)
    som *= np.minimum(1, t/.004)
    return som/np.abs(som).max()


def tiques():
    """One tick for each number the counter shows, while they come at most every 55 ms."""
    tempos, ultimo = [], -1.0
    for n in range(1, 101):
        p = 1 - (1 - n/100)**(1/3)
        t = 4.45 + 1.47*p
        if t - ultimo >= .055:
            tempos.append(t)
            ultimo = t
    return tempos


def eventos():
    ev = [  # time, effect, gain in dB, pan (-1 left … 1 right), speed
        (.02, 'whoosh', -4, -.4, 1), (.53, 'impacto-suave', -9, 0, 1), (.62, 'pop', -6, 0, 1), (.92, 'impacto', -3, 0, 1),
        (1.68, 'whoosh', -13, -.3, 1.5), (2.78, 'whoosh', -9, 0, 1), (2.95, 'pop', -6, 0, 1.1), (3.15, 'impacto-suave', -3, 0, 1),
        (3.0, 'vibracao', -7, -.3, 1), (3.6, 'impacto', -2, -.3, 1), (3.6, 'pop', -4, -.3, .8),
        (3.75, 'notificacao', -11, .2, 1), (4.05, 'notificacao', -13, -.2, 1.12), (4.32, 'whoosh', -11, 0, 1.2),
        (6.0, 'impacto', 0, 0, 1), (6.0, 'pop', -3, -.85, .7), (6.02, 'pop', -3, .85, .75), (6.05, 'notificacao', -7, 0, 1),
        (6.14, 'impacto-suave', -6, 0, 1), (6.36, 'pop', -5, 0, 1), (6.85, 'whoosh', -10, -.5, 1.1), (7.2, 'pop', -8, -.5, 1.3),
        (8.84, 'whoosh', -4, -.6, .9), (9.15, 'pop', -6, 0, 1), (9.2, 'whoosh', -11, 0, .8), (9.36, 'impacto-suave', -4, 0, 1),
        (9.62, 'impacto-suave', -1, 0, .85), (10.15, 'pop', -14, 0, 1.4), (12.04, 'whoosh', -4, .6, .9), (12.36, 'pop', -6, 0, 1),
        (12.40, 'whoosh', -11, -.4, 1.2), (12.55, 'whoosh', -11, .4, 1.25), (12.56, 'impacto-suave', -4, 0, 1),
        (12.70, 'whoosh', -10, 0, 1.15), (13.35, 'whoosh', -13, 0, 1.7), (13.95, 'impacto', -3, 0, 1),
        (14.35, 'pop', -4, 0, 1), (14.40, 'notificacao', -8, 0, 1),
    ]
    rnd = random.Random(2)
    for i in range(12):
        ev.append((3.68 + i*.19 + rnd.uniform(-.05, .05), 'pop', -15, rnd.uniform(-.7, .3), rnd.uniform(.9, 1.5)))
    # Little pops for the hearts as they rise.
    for i in range(8):
        ev.append((9.95 + i*.22, 'pop', -20, (-1)**i*.5, rnd.uniform(1.6, 1.95)))
    ev += [(t, 'tique', -9, 0, 1) for t in tiques()]
    return ev


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
        base = cache.setdefault(nome, ler_efeito(nome))
        if velocidade != 1:
            base = np.interp(np.arange(0, len(base) - 1, velocidade), np.arange(len(base)), base).astype(np.float32)
        por(inicio, base, ganho, pan)
    rng = np.random.default_rng(9)
    por(5.05, subida(.95, rng), -13, 0)
    palmas = aplausos(2.9, rng)
    por(6.05, palmas, -15, -.25)
    por(6.09, np.roll(palmas, 4100), -15, .25)
    brilho = brilho_sonoro()
    por(10.12, brilho, -14, .15)
    por(13.72, brilho, -13, 0)
    por(14.38, brilho, -16, -.15)
    # Soft limit, then 16-bit.
    som = np.tanh(som*1.1)/np.tanh(1.1)
    with wave.open(str(caminho), 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(som, -1, 1)*32767).astype('<i2').tobytes())


def normalizar(entrada, saida):
    """-16 LUFS for Reels and TikTok, in two passes, so the gain is one steady change, with 2 dB
    of headroom for the AAC encoder's overshoot."""
    alvo = 'I=-16:TP=-2:LRA=11'
    medida = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(entrada), '-af', f'loudnorm={alvo}:print_format=json', '-f', 'null', '-'],
                            capture_output=True, text=True, check=True).stderr
    m = json.loads(medida[medida.rindex('{'):medida.rindex('}') + 1])
    filtro = (f"loudnorm={alvo}:linear=true:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}")
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(entrada), '-af', filtro, '-ar', str(SR), str(saida)], check=True)


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
            print(trabalho / f'quadro-{t:05.2f}.png')
        return
    audio = trabalho / 'som.wav'
    mixar(audio)
    normalizado = trabalho / 'som-normalizado.wav'
    normalizar(audio, normalizado)
    total = round(DURACAO*FPS)
    cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
           '-i', str(normalizado), '-map', '0:v', '-map', '1:a', '-c:v', 'libx264', '-preset', 'slow', '-crf', '18',
           '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', str(SR),
           '-movflags', '+faststart', '-shortest', str(args.saida)]
    ffmpeg = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(initializer=carregar_assets) as pool:
        for i, dados in enumerate(pool.imap(quadro_bytes, range(total), chunksize=3)):
            ffmpeg.stdin.write(dados)
            if i % 60 == 0:
                print(f'quadro {i}/{total}', flush=True)
    ffmpeg.stdin.close()
    if ffmpeg.wait():
        raise SystemExit('ffmpeg falhou')
    print(args.saida)


if __name__ == '__main__':
    main()
