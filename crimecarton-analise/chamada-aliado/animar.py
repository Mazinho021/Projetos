#!/usr/bin/env python3
"""The "Vire aliado" call, animated frame by frame and told by the series' narrator.

It invites the audience to buy Part 3's ally pass (R$ 9,90 on the site), in the look of the
"mais de 100 seguidores" thank-you, whose drawing and sound tools it borrows
(../agradecimento-100/mais-de-100/animar.py). 1080 × 1920 at 30 fps, about 27 s:

  "Quer aparecer na parte três?"            Part 3's card spins in and turns to "em breve".
  "Vire aliado do Zinho."                   Zinho points at you over turning caramel rays.
  "O seu arroba entra no episódio:"         "@seuperfil" types itself in.
  "no celular dele, num muro, na TV ou nos créditos."   four quick shots, each with the @.
  "E vai na legenda do post, com o seu número de aliado."   the post's caption, then the ally badge.
  "São só dez vagas, até sexta, às nove da noite."   ten open places light up; the deadline.
  "Nove e noventa no Pix, direto no site."  the site's Pix window, in a phone.
  "O link tá na bio."                       an arrow up to the bio and the site's address.

The picture follows the narration's words (alinhamento-narracao.json). Until Codex delivers
narracao-chamada.wav, the timing is estimated from narracao-chamada.txt, the video has effects
only, and drawn stand-ins replace the wall, the TV and the pointing Zinho.

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
import re
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

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
TEXTO = HERE / 'narracao-chamada.txt'
ARROBA = '@seuperfil'
ATRASO = .3  # the voice starts as the card spins in


def estimadas(txt):
    """Word timings guessed from the text, for drafts made before the narration exists."""
    saida, t = [], 0.0
    for i, w in enumerate(txt.split()):
        silabas = max(1, len(re.findall(r'[aeiouáéíóúâêôãõ]+', w.lower())))
        dur = .08 + .15*silabas
        saida.append({'i': i, 'text': w, 'start': round(t, 3), 'end': round(t + dur, 3)})
        t += dur + (.55 if w[-1] in '.?!' else .2 if w[-1] in ',:' else 0)
    return saida


COM_VOZ = NARRACAO.exists() and ALINHAMENTO.exists()
_PALAVRAS = (json.loads(ALINHAMENTO.read_text(encoding='utf-8'))['words'] if COM_VOZ
             else estimadas(TEXTO.read_text(encoding='utf-8')))
_P = [(w['start'] + ATRASO, w['end'] + ATRASO) for w in _PALAVRAS]
# The words the picture follows, by their place in narracao-chamada.txt.
T = {nome: _P[i][0] for nome, i in (
    ('quer', 0), ('parte', 3), ('vire', 5), ('aliado', 6), ('zinho', 8), ('o_seu', 9), ('arroba', 11),
    ('entra', 12), ('celular', 15), ('muro', 18), ('tv', 20), ('creditos', 23), ('e', 25), ('legenda', 28),
    ('numero', 34), ('sao', 37), ('dez', 39), ('ate', 41), ('nove', 44), ('preco', 47), ('pix', 51),
    ('site', 54), ('o_link', 55), ('bio', 59))}
VOZ_FIM = _P[-1][1]
DURACAO = round((VOZ_FIM + 1.6)*FPS)/FPS

# Cuts, each just ahead of the word that brings the next picture.
C_VIRE = T['vire'] - .15
C_ARROBA = T['o_seu'] - .3
C_CELULAR = T['celular'] - .06
C_MURO = T['muro'] - .06
C_TV = T['tv'] - .06
C_CREDITOS = T['creditos'] - .06
C_LEGENDA = T['e'] - .3
C_VAGAS = T['sao'] - .14
C_PIX = T['preco'] - .3
C_BIO = T['o_link'] - .14
EMPURRA = .14

PHONE_QUAD = [[0.4666, 0.4137], [0.7031, 0.4344], [0.5938, 0.6811], [0.2791, 0.6466]]  # Part 2's phone, scene 6
LOCK = {'state': 'lock', 'date': 'terça-feira, 27 de outubro', 'time': '23:47', 'app': 'MENSAGENS',
        'sender': ARROBA, 'message': 'Tô contigo, Zinho.', 'when': 'agora'}


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
    A['joia'] = base.A['joia']
    apontando = HERE / 'recortes' / 'zinho-apontando.png'
    A['apontando'] = Image.open(apontando).convert('RGBA') if apontando.exists() else base.A['joia']

    # Caramel rays for "Vire aliado" and the bio: the lamp's colour, dark at the edges.
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

    muro = HERE / 'cena-muro.png'
    A['muro'] = cobrir(Image.open(muro).convert('RGB')) if muro.exists() else muro_provisorio()
    A['tv'], A['tv_quad'] = tv()

    A['avatar'] = avatar_redondo(Image.open(SERIE / 'site' / 'img' / 'perfil.jpg'), 104)
    A['janela_pix'] = celular_com(Image.open(HERE / 'janela-pix-site.png').convert('RGB'))
    A['pix'] = Image.open(HERE / 'pix.png').convert('RGBA')


def muro_provisorio():
    """A stand-in for cena-muro.png: worn plaster at night under a street lamp."""
    rng = np.random.default_rng(4)
    yy, xx = np.mgrid[0:H, 0:W]
    manchas = Image.fromarray((rng.random((24, 14))*255).astype(np.uint8)).resize((W, H), Image.Resampling.BICUBIC)
    m = np.asarray(manchas, np.float32)/255
    muro = np.array((158, 146, 128))*(.82 + .18*m)[..., None] + rng.normal(0, 6, (H, W, 1))
    calcada = yy > H*.84
    muro[calcada] = np.array((88, 86, 84)) + rng.normal(0, 5, (int(calcada.sum()), 3))
    luz = np.exp(-(((xx - W*.2)/(W*.9))**2 + ((yy - H*.05)/(H*.7))**2))
    noite = (.28 + .72*luz)[..., None]*np.array((1.0, .86, .62))
    return Image.fromarray(np.clip(muro*noite, 0, 255).astype(np.uint8)).convert('RGBA')


def tv():
    """The TV shot and its screen's corners: Codex's cena-tv.png, or a drawn stand-in."""
    caminho = HERE / 'cena-tv.png'
    quad_arquivo = HERE / 'cena-tv-tela.json'
    if caminho.exists() and quad_arquivo.exists():
        fundo = cobrir(Image.open(caminho).convert('RGB'))
        return fundo, [tuple(p) for p in json.loads(quad_arquivo.read_text())['quad']]
    fundo = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    d = ImageDraw.Draw(fundo)
    for k in range(H):
        f = k/H
        d.line((0, k, W, k), fill=(round(34 - 20*f), round(24 - 14*f), round(20 - 12*f), 255))
    d.rectangle((0, 1380, W, H), fill=(60, 38, 26, 255))
    d.rounded_rectangle((70, 560, 1010, 1400), 60, fill=(48, 42, 40, 255), outline=(16, 12, 10, 255), width=8)
    d.rounded_rectangle((120, 610, 960, 1250), 40, fill=(20, 18, 18, 255))
    for cx in (300, 780):
        d.ellipse((cx - 26, 1300, cx + 26, 1352), fill=(30, 26, 24, 255))
    return fundo, [(140, 630), (940, 630), (940, 1230), (140, 1230)]


def avatar_redondo(im, d):
    im = im.convert('RGB').resize((d, d), Image.Resampling.LANCZOS).convert('RGBA')
    m = Image.new('L', (d, d), 0)
    ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
    im.putalpha(m)
    anel = Image.new('RGBA', (d + 12, d + 12), (0, 0, 0, 0))
    ImageDraw.Draw(anel).ellipse((0, 0, d + 11, d + 11), outline=VERMELHO_TEXTO + (255,), width=4)
    anel.alpha_composite(im, (6, 6))
    return anel


def celular_com(tela, largura=520):
    """A phone with `tela` on its screen."""
    altura = round(largura*tela.height/tela.width)
    borda = 22
    im = Image.new('RGBA', (largura + 2*borda, altura + 2*borda), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, im.width - 1, im.height - 1), 70, fill=(14, 14, 18, 255),
                                         outline=(70, 70, 80, 255), width=3)
    foto = tela.resize((largura, altura), Image.Resampling.LANCZOS).convert('RGBA')
    m = Image.new('L', foto.size, 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, largura - 1, altura - 1), 52, fill=255)
    foto.putalpha(m)
    im.alpha_composite(foto, (borda, borda))
    ImageDraw.Draw(im).rounded_rectangle((im.width/2 - 70, borda + 14, im.width/2 + 70, borda + 46), 16, fill=(0, 0, 0, 255))
    return im


# ---------------------------------------------------------------- pieces

@lru_cache(maxsize=32)
def pilula(valor, tamanho, fundo=VERMELHO, tinta=CREME, labio=VERMELHO_ESCURO, peso='ExtraBold'):
    """A pill with a lip under it, like the site's buttons."""
    s = texto(valor, tamanho, tinta, peso, sombra=False)
    w, h = s.width + round(tamanho*1.6), s.height + round(tamanho*.9)
    im = Image.new('RGBA', (w, h + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if labio:
        d.rounded_rectangle((0, 10, w - 1, h + 9), h//2, fill=labio + (255,))
    d.rounded_rectangle((0, 0, w - 1, h - 1), h//2, fill=fundo + (255,))
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


def raios_caramelo(tela, t, centro=(W/2, 1150)):
    d = ImageDraw.Draw(tela)
    d.rectangle((0, 0, W, H), fill=CARAMELO + (255,))
    giro = math.radians(t*14)
    cx, cy = centro
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
    """"num muro": the @ sprayed on a street wall."""
    tela = A['muro'].copy()
    pich = pichacao()
    p = prog(t, C_MURO + .08, C_MURO + .55)
    if p > 0:
        corte = pich.copy()
        mascara = Image.new('L', pich.size, 0)
        ImageDraw.Draw(mascara).rectangle((0, 0, round(pich.width*p), pich.height), fill=255)
        corte.putalpha(Image.composite(pich.getchannel('A'), Image.new('L', pich.size, 0), mascara))
        colar(tela, corte, W/2, 980, 1, 7)
        if p < 1:
            # The spray: dots around the can's moving edge.
            d = ImageDraw.Draw(tela)
            rnd = random.Random(int(t*FPS))
            borda_x = W/2 - pich.width/2 + pich.width*p
            for _ in range(70):
                x, y = borda_x + rnd.gauss(0, 26), 980 + rnd.gauss(0, 70) - (borda_x - W/2)*math.tan(math.radians(7))
                r = rnd.uniform(1.5, 4.5)
                d.ellipse((x - r, y - r, x + r, y + r), fill=VERMELHO_TEXTO + (rnd.randint(90, 220),))
    lugar(tela, t, C_MURO + .05, 'NUM MURO')
    return tela


@lru_cache(maxsize=1)
def pichacao():
    s = texto(ARROBA, 150, VERMELHO_TEXTO, contorno=10, cor_contorno=CREME, sombra=False)
    sombra = sombra_de(s, 6, 160)
    im = Image.new('RGBA', (sombra.width, sombra.height), (0, 0, 0, 0))
    im.alpha_composite(sombra, (10, 14))
    im.alpha_composite(s, ((im.width - s.width)//2, (im.height - s.height)//2))
    return im


def cena_tv(t):
    """"na TV": the @ on a news report."""
    tela = A['tv'].copy()
    jornal = telejornal(t)
    quad = A['tv_quad']
    w, h = jornal.size
    coef = render_animatic.perspective([(0, 0), (w, 0), (w, h), (0, h)], quad)
    camada = jornal.transform((W, H), Image.Transform.PERSPECTIVE, coef, Image.Resampling.BICUBIC)
    tela.alpha_composite(camada)
    lugar(tela, t, C_TV + .05, 'NA TV')
    return tela


def telejornal(t):
    """A news report, flat, before it is fitted to the TV's screen."""
    w, h = 800, 600
    im = Image.new('RGBA', (w, h), (0, 0, 0, 255))
    d = ImageDraw.Draw(im)
    for k in range(h):
        d.line((0, k, w, k), fill=(round(20 + 20*k/h), round(44 + 30*k/h), round(110 + 40*k/h), 255))
    d.rectangle((40, 40, 300, 104), fill=VERMELHO + (255,))
    s = texto('PLANTÃO', 44, CREME, sombra=False)
    im.alpha_composite(s, (60, 72 - s.height//2))
    p = sai_cubica(prog(t, C_TV + .1, C_TV + .4))
    faixa = Image.new('RGBA', (w - 80, 150), (247, 243, 236, 255))
    fd = ImageDraw.Draw(faixa)
    fd.rectangle((0, 0, 18, 150), fill=VERMELHO + (255,))
    nome = texto(ARROBA, 70, TINTA, sombra=False)
    faixa.alpha_composite(nome, (44, 18))
    sub = texto('aliado do Zinho', 38, (110, 92, 78), 'SemiBold', sombra=False)
    faixa.alpha_composite(sub, (48, 98))
    im.alpha_composite(faixa, (round(40 - (w + 40)*(1 - p)), 340))
    d.rectangle((0, h - 60, w, h), fill=(10, 14, 30, 255))
    rodape = texto('A PARTE QUE FALTOU  •  PARTE 3  •  ALIADOS DO ZINHO  •  ', 30, CREME, 'Bold', sombra=False)
    x = -((t - C_TV)*160) % rodape.width
    for dx in (-rodape.width, 0, rodape.width):
        colar(im, rodape, x + dx, h - 30, ancora=(0, .5))
    # The CRT: scan lines and a soft glow.
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


def cena_pix(t):
    """"Nove e noventa no Pix, direto no site.": the site's Pix window, in a phone."""
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    base.raios(tela, t)
    p = prog(t, C_PIX + .25, C_PIX + .7)
    if p > 0:
        y = 1130 + 1100*(1 - sai_volta(p, 1.15))
        angulo = -4*(1 - p) + 1.2*math.sin((t - C_PIX)*1.8)
        colar(tela, sombra_de(A['janela_pix'], 22, 140), W/2 + 16, y + 30, .9, angulo, .9)
        colar(tela, A['janela_pix'], W/2, y, .9, angulo)
    aparece(tela, texto('R$ 9,90', 150, CREME, contorno=10), W/2, 330, T['preco'], t, tipo='pancada')
    if t >= T['pix'] - .08:
        k = prog(t, T['pix'] - .08, T['pix'] + .2)
        colar(tela, selo_pix(), W/2, 490, .5 + .5*sai_volta(k), alfa=min(1.0, k*3))
    return sacudir(tela, t, T['preco'], 14, cor=VERMELHO_ESCURO)


@lru_cache(maxsize=1)
def selo_pix():
    """'Pix ou cartão, direto no site', with the Pix symbol at the front."""
    s = texto('PIX OU CARTÃO, DIRETO NO SITE', 40, CREME, sombra=False)
    icone = A['pix'].resize((58, 58), Image.Resampling.LANCZOS)
    w, h = s.width + icone.width + 100, max(s.height, icone.height) + 36
    im = Image.new('RGBA', (w, h + 10), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 10, w - 1, h + 9), h//2, fill=(6, 10, 30, 255))
    d.rounded_rectangle((0, 0, w - 1, h - 1), h//2, fill=AZUL_ESCURO + (255,))
    im.alpha_composite(icone, (36, (h - icone.height)//2))
    im.alpha_composite(s, (36 + icone.width + 22, (h - s.height)//2))
    return im


def cena_bio(t):
    """"O link tá na bio.": an arrow up to the bio, the site's address and Zinho pointing."""
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    raios_caramelo(tela, t, (W/2, 1300))
    zinho_sobe(tela, t, C_BIO + .1, 'apontando', .68, 2000)
    if t >= T['o_link'] - .05:
        pulo = 18*abs(math.sin((t - T['o_link'])*5))
        colar(tela, seta(), W/2, 250 - pulo, sai_volta(prog(t, T['o_link'] - .05, T['o_link'] + .25)))
    aparece(tela, texto('LINK NA BIO', 140, CREME, contorno=10), W/2, 480, T['o_link'] + .05, t, tipo='pancada')
    aparece(tela, pilula('golpecartoon.netlify.app', 46, CREME, TINTA, (194, 173, 152), 'Bold'), W/2, 640, T['bio'], t)
    if t >= VOZ_FIM - .1:
        k = prog(t, VOZ_FIM - .1, VOZ_FIM + .2)
        pulsa = 1 + .04*math.sin((t - VOZ_FIM)*7)
        colar(tela, pilula('VIRE ALIADO', 60), W/2, 800, (.5 + .5*sai_volta(k))*pulsa, alfa=min(1.0, k*3))
    return sacudir(tela, t, T['o_link'] + .05, 12, cor=(92, 44, 16))


@lru_cache(maxsize=1)
def seta():
    im = Image.new('RGBA', (200, 170), (0, 0, 0, 0))
    ImageDraw.Draw(im).polygon([(100, 6), (194, 100), (138, 100), (138, 164), (62, 164), (62, 100), (6, 100)],
                               fill=CREME + (255,), outline=TINTA + (255,), width=7)
    return im


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
    (C_PIX, cena_pix, ('faixa', VERMELHO, True)),
    (C_BIO, cena_bio, ('empurra', True)),
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

def spray(dur=.5):
    """A spray can: hissing noise, with a short shake of the ball first."""
    rng = np.random.default_rng(13)
    n = int(dur*SR)
    som = base.ruido_em_faixa(n, 2500, 9000, rng)*np.minimum(1, np.arange(n)/(.03*SR))*np.minimum(1, (n - np.arange(n))/(.08*SR))
    return som.astype(np.float32)


def eventos():
    """Every effect, tied to the narrator's words: time, effect, gain in dB, pan, speed."""
    ev = [
        (.02, 'whoosh', -9, 0, 1), (T['parte'] - .05, 'impacto-suave', -11, 0, 1), (T['parte'] + .05, 'whoosh', -15, 0, 1.6),
        (C_VIRE, 'impacto', -6, 0, 1), (C_VIRE + .02, 'whoosh', -10, 0, 1.05), (T['aliado'], 'impacto-suave', -10, 0, 1),
        (C_ARROBA - .02, 'whoosh', -7, -.6, .9), (T['o_seu'], 'pop', -13, 0, 1), (T['entra'], 'impacto-suave', -11, 0, 1),
        (C_CELULAR, 'whoosh', -14, .4, 1.6), (C_CELULAR + .12, 'notificacao', -11, .2, 1),
        (C_MURO, 'whoosh', -14, .4, 1.6), (C_TV, 'whoosh', -14, .4, 1.6), (C_TV + .1, 'impacto-suave', -14, 0, 1.3),
        (C_CREDITOS, 'whoosh', -14, .4, 1.6),
        (C_LEGENDA - .02, 'whoosh', -8, .6, .9), (C_LEGENDA + .2, 'whoosh', -14, 0, 1.1), (T['legenda'], 'pop', -15, 0, 1.3),
        (T['numero'] - .06, 'impacto', -8, 0, 1),
        (C_VAGAS, 'whoosh', -13, .4, 1.4), (T['dez'], 'impacto-suave', -10, 0, 1),
        (C_PIX - .02, 'whoosh', -8, -.6, .9), (C_PIX + .25, 'whoosh', -13, 0, 1.1), (T['preco'], 'impacto', -8, 0, 1),
        (T['pix'] - .08, 'pop', -12, 0, 1), (T['pix'], 'notificacao', -13, 0, 1),
        (C_BIO, 'whoosh', -13, 0, 1.3), (C_BIO + .1, 'whoosh', -12, 0, 1.05), (T['o_link'] + .05, 'impacto-suave', -10, 0, 1),
        (T['bio'], 'pop', -12, 0, 1), (VOZ_FIM - .1, 'pop', -10, 0, 1), (VOZ_FIM, 'notificacao', -12, 0, 1),
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
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(NARRACAO), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    som = np.frombuffer(pcm, np.float32)
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
    por(C_MURO + .08, spray(), -16, .2)
    brilho = base.brilho_sonoro()
    por(T['parte'] + .45, brilho, -16, 0)
    por(C_CREDITOS + .15, brilho, -18, 0)
    por(VOZ_FIM + .05, brilho, -14, 0)
    if COM_VOZ:
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
        print(' '.join(f'{k}={v:.2f}' for k, v in T.items()), f'fim={DURACAO}', 'com voz' if COM_VOZ else 'sem voz')
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
