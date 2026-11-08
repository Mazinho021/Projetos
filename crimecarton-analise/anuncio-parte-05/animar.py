#!/usr/bin/env python3
"""Part 5's announcement: "A parte 5 sai amanhã, às 12h", and the allies' places of Part 6.

Asked by the creator on 07/11/2026, the night Part 5's drawings were being made: Part 5 comes out the
next day at noon, without allies, and the passes sold now go to Part 6 (the site has its list open,
with no deadline yet). Made like Part 3's announcement (../anuncio-parte-03/), with the "Vire aliado"
call's tools and lines the narrator has already recorded there, so it needs no new voice. 1080 × 1920
at 30 fps, about 16 s:

  (no voice)                         Part 1's backpack of old clothes: "PARTE 5 · SAI AMANHÃ · ÀS 12H".
  "Vire aliado do Zinho."            Zinho rises, pointing at you.
  "O seu arroba entra no episódio:   the call's own shots, the phone, the wall, the TV and the
   no celular dele, num muro, na TV   credits, with Part 6 where they said Part 3.
   ou nos créditos."
  "Nove e noventa no Pix, direto no  R$ 9,90, the 30 places of Part 6 and "LINK NA BIO".
   site. O link tá na bio."
  (no voice)                         Zinho calls you in: "PARTE 5 · AMANHÃ, 12H", "VIRE ALIADO DA PARTE 6".

    python animar.py                          # the video, next to this script
    python animar.py --quadros 1.2 3.5 6 12 15  # stills for a look, in work/
"""
from __future__ import annotations

import argparse
import importlib.util
import math
from multiprocessing import Pool
from pathlib import Path
import subprocess
import sys
import wave

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
SERIE = HERE.parent

_spec = importlib.util.spec_from_file_location('animar_chamada', SERIE / 'chamada-aliado' / 'animar.py')
ch = importlib.util.module_from_spec(_spec)
sys.modules['animar_chamada'] = ch
_spec.loader.exec_module(ch)
base = ch.base

from animar_agradecimento import (  # noqa: E402
    W, H, FPS, SR, CREME, VERMELHO, VERMELHO_ESCURO, VERMELHO_TEXTO, AZUL_ESCURO, OURO, prog, sai_volta, texto, colar,
    aparece, passagem)

SAIDA = HERE / 'anuncio-parte-05.mp4'
MOCHILA = SERIE / 'episodio-01' / 'cena-03-roupas.png'
PARTE, ALIADOS = 5, 6

# The call's shots say "Parte 3", the list they were made for. Here the places are Part 6's.
_texto_da_chamada = ch.texto


def _texto_parte_6(valor, *args, **kwargs):
    return _texto_da_chamada(str(valor).replace('PARTE 3', f'PARTE {ALIADOS}').replace('Parte 3', f'Parte {ALIADOS}'),
                             *args, **kwargs)


ch.texto = _texto_parte_6

# The lines, all from the call's first take, cut in the narrator's own pauses: (first word, last
# word, where it is cut before its first word).
_T1 = ch._TOMADA_1
FALAS = [(5, 8, _T1[5]['start'] - .06), (9, 24, (_T1[8]['end'] + _T1[9]['start'])/2),
         (47, 59, (_T1[46]['end'] + _T1[47]['start'])/2)]
ANTES_DA_VOZ = 2.6   # the opening, with no voice
ENTRE = .3           # between lines, where the picture cuts
FIM = 2.8            # the close, with no voice


def _horario():
    """Where each line starts in the video, and the video time of every word the picture follows."""
    inicios, t = [], ANTES_DA_VOZ
    for i, j, corte in FALAS:
        inicios.append(t)
        t += _T1[j]['end'] + .12 - corte + ENTRE
    marcas = {}
    for k, (i, j, corte) in enumerate(FALAS):
        for n in range(i, j + 1):
            marcas[n] = inicios[k] + _T1[n]['start'] - corte
    return inicios, marcas, t - ENTRE


INICIOS, _M, VOZ_FIM = _horario()
T = {'vire': _M[5], 'aliado': _M[6], 'zinho': _M[8], 'o_seu': _M[9], 'noventa': _M[49], 'pix': _M[51],
     'direto': _M[52], 'link': _M[56], 'bio': _M[59]}
C_VIRE = INICIOS[0] - .1
C_ARROBA = INICIOS[1] - .1
C_PRECO = INICIOS[2] - .1
C_FINAL = VOZ_FIM + .3
DURACAO = round((C_FINAL + FIM)*FPS)/FPS
# The call's clock against this video's: its shots for "O seu arroba…" play with their own timing.
DESVIO = ch.T['o_seu'] - T['o_seu']
_ONDE = [r for r in ch.ROTEIRO if r[1] in (ch.cena_arroba, ch.cena_celular, ch.cena_muro, ch.cena_tv, ch.cena_creditos)]

A = {}


def carregar():
    if A:
        return
    ch.carregar()
    # Only the lower part of the drawing, the hands, the old clothes and the backpack: Zinho's face,
    # at the top, would sit under the news.
    arte = Image.open(MOCHILA).convert('RGB')
    mochila = ch.cobrir(arte.crop((0, round(arte.height*.41), arte.width, arte.height)))
    mochila.alpha_composite(Image.new('RGBA', (W, H), (8, 6, 12, 110)))
    A['mochila'] = mochila


# ---------------------------------------------------------------- scenes

def cena_amanha(t):
    """The opening, with no voice: the backpack of old clothes, and the news."""
    zoom = 1 + .06*t/C_VIRE
    w, h = W/zoom, H/zoom
    tela = A['mochila'].resize((W, H), Image.Resampling.BICUBIC, box=((W - w)/2, (H - h)*.5, (W + w)/2, (H - h)*.5 + h))
    aparece(tela, ch.etiqueta(f'PARTE {PARTE}', 78), W/2, 300, .1, t, tipo='pancada', angulo=-3)
    aparece(tela, texto('SAI AMANHÃ', 150, CREME, contorno=10), W/2, 480, .4, t, tipo='pancada')
    aparece(tela, texto('ÀS 12H', 170, OURO, contorno=11), W/2, 650, .75, t, tipo='pancada')
    aparece(tela, texto('QUEM ENCHEU A SUA MOCHILA?', 62, CREME, contorno=6), W/2, 1430, 1.25, t)
    return ch.sacudir(tela, t, .75, 14, cor=(8, 6, 12))


def cena_vire(t):
    """"Vire aliado do Zinho.": Zinho rises, pointing at you, over caramel rays."""
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    ch.raios_caramelo(tela, t)
    ch.zinho_sobe(tela, t, C_VIRE + .02, 'apontando')
    aparece(tela, texto('VIRE', 120, CREME, contorno=8), W/2, 320, T['vire'], t, tipo='pancada')
    aparece(tela, ch.etiqueta('ALIADO', 150), W/2, 480, T['aliado'], t, tipo='pancada', angulo=4)
    aparece(tela, texto('DO ZINHO', 70, CREME, contorno=6), W/2, 640, T['zinho'] - .08, t)
    ch.flash(tela, t, C_VIRE)
    return ch.sacudir(tela, t, T['aliado'], 16, cor=(92, 44, 16))


def cena_onde(t):
    """"O seu arroba entra no episódio: no celular dele, num muro, na TV ou nos créditos.": the call's
    own shots for the line, on its clock."""
    tc = t + DESVIO
    i = max([k for k, (inicio, _, _) in enumerate(_ONDE) if tc >= inicio] or [0])
    inicio, cena, entrada = _ONDE[i]
    if i > 0 and entrada and entrada[0] == 'empurra' and tc < inicio + ch.EMPURRA:
        return ch.empurra(tc, inicio, ch.EMPURRA, _ONDE[i - 1][1], cena, vertical=entrada[1])
    return cena(tc)


def cena_preco(t):
    """"Nove e noventa no Pix, direto no site. O link tá na bio.": the price, Part 6's 30 places, the link."""
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    base.faixas_da_jaqueta(tela, t)
    aparece(tela, texto('R$ 9,90', 170, OURO, contorno=10), W/2, 330, T['noventa'] - .1, t, tipo='pancada')
    aparece(tela, texto('NO PIX, DIRETO NO SITE', 64, CREME, contorno=6), W/2, 470, T['pix'] - .05, t)
    aparece(tela, ch.etiqueta(f'PARTE {ALIADOS} · 30 VAGAS', 62), W/2, 610, T['direto'] - .05, t, angulo=-3)
    for i in range(30):
        coluna, linha = i % 5, i // 5
        aparece(tela, ch.vaga(i + 1), 156 + coluna*192, 770 + linha*112, T['direto'] + .02*i, t)
    aparece(tela, ch.etiqueta('LINK NA BIO', 90), W/2, 1520, T['link'] - .05, t, tipo='pancada', angulo=3)
    return ch.sacudir(tela, t, T['noventa'] - .1, 12, cor=AZUL_ESCURO)


def cena_final(t):
    """The close, with no voice: Zinho calls you in; Part 5 tomorrow at noon, allies for Part 6."""
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    base.raios(tela, t)
    ch.zinho_sobe(tela, t, C_FINAL + .05, 'chamando', .74, 1990)
    aparece(tela, texto(f'PARTE {PARTE}', 120, CREME, contorno=9), W/2, 330, C_FINAL + .3, t, tipo='pancada')
    aparece(tela, texto('AMANHÃ, 12H', 110, OURO, contorno=8), W/2, 470, C_FINAL + .55, t, tipo='pancada')
    aparece(tela, ch.etiqueta(f'VIRE ALIADO DA PARTE {ALIADOS}', 60), W/2, 640, C_FINAL + .95, t, angulo=4)
    ch.cintilar(tela, t, C_FINAL + 1.0, ((95, 245), (990, 300), (125, 505), (955, 545), (900, 760)))
    return ch.sacudir(tela, t, C_FINAL + .3, 14, cor=VERMELHO_ESCURO)


ROTEIRO = [
    (0.0, cena_amanha, None),
    (C_VIRE, cena_vire, None),
    (C_ARROBA, cena_onde, ('faixa', VERMELHO, True)),
    (C_PRECO, cena_preco, ('faixa', AZUL_ESCURO, False)),
    (C_FINAL, cena_final, ('faixa', VERMELHO, True)),
]


def quadro(t):
    carregar()
    i = max(k for k, (inicio, _, _) in enumerate(ROTEIRO) if t >= inicio)
    inicio, cena, entrada = ROTEIRO[i]
    if entrada and entrada[0] == 'faixa' and t < inicio + .3:
        tela = passagem(t, inicio, .3, ROTEIRO[i - 1][1], cena, entrada[1], para_direita=entrada[2])
    else:
        tela = cena(t)
    tela.alpha_composite(base.A['grao'])
    return tela.convert('RGB')


def quadro_bytes(i):
    return quadro(i/FPS).tobytes()


# ---------------------------------------------------------------- sound

def eventos():
    """Every effect: time, effect, gain in dB, pan (-1 left … 1 right), speed. The call's own effects
    for its shots of "O seu arroba…" come along, moved to this video's clock."""
    ev = [
        (.1, 'pop', -12, 0, 1), (.4, 'impacto', -7, 0, 1), (.75, 'impacto-suave', -6, 0, 1), (1.25, 'pop', -14, 0, 1),
        (C_VIRE, 'impacto', -6, 0, 1), (C_VIRE + .02, 'whoosh', -10, 0, 1.05), (T['aliado'], 'impacto-suave', -10, 0, 1),
        (C_ARROBA - .02, 'whoosh', -10, -.6, .9),
        (C_PRECO - .02, 'whoosh', -10, .6, .9), (T['noventa'] - .1, 'impacto-suave', -9, 0, 1),
        (T['link'] - .05, 'impacto-suave', -10, 0, 1), (T['link'], 'pop', -9, 0, 1),
        (C_FINAL - .02, 'whoosh', -6, -.6, .9), (C_FINAL + .05, 'whoosh', -9, 0, 1.05), (C_FINAL + .3, 'impacto', -4, 0, 1),
        (C_FINAL + .55, 'impacto-suave', -6, 0, 1), (C_FINAL + .95, 'pop', -7, 0, 1), (C_FINAL + 1.0, 'notificacao', -10, 0, 1),
    ]
    for k, i in enumerate(range(0, 30, 3)):
        ev.append((T['direto'] + .02*i, 'pop', -19, (-1)**k*.4, 1 + .06*k))
    inicio, fim = _ONDE[0][0], ch.C_LEGENDA
    for quando, nome, ganho, pan, velocidade in ch.eventos():
        if inicio + .05 <= quando < fim - .05:
            ev.append((quando - DESVIO, nome, ganho, pan, velocidade))
    return ev


def ler(caminho):
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(caminho), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32)


def voz(n):
    """The three lines at their places in the video."""
    tomada = ler(ch.NARRACAO)
    fala = np.zeros(n, np.float32)
    curto, queda = int(.01*SR), int(.06*SR)
    for inicio, (i, j, corte) in zip(INICIOS, FALAS):
        parte = tomada[int(corte*SR):int((_T1[j]['end'] + .12)*SR)].copy()
        parte[:curto] *= np.linspace(0, 1, curto, dtype=np.float32)
        parte[-queda:] *= np.linspace(1, 0, queda, dtype=np.float32)
        k = int(inicio*SR)
        fala[k:k + len(parte)] += parte[:n - k]
    return fala/np.abs(fala).max()*10**(-3/20)


def abaixar_sob_a_voz(fala):
    """A gain for the effects that steps them back about 7 dB while the narrator speaks."""
    passo = int(.01*SR)
    blocos = np.abs(fala[:len(fala)//passo*passo]).reshape(-1, passo).max(axis=1)
    segura = np.array([blocos[max(0, j - 25):j + 15].max() for j in range(len(blocos))])
    ganho = np.convolve(1 - .55*np.clip(segura/(.3*segura.max()), 0, 1), np.ones(8)/8, mode='same')
    curva = np.ones(len(fala), np.float32)
    trecho = np.repeat(ganho, passo)
    curva[:len(trecho)] = trecho
    return curva


def mixar(caminho):
    n = int(DURACAO*SR)
    som = np.zeros((n, 2), np.float32)

    def por(inicio, mono, ganho_db, pan):
        i = int(inicio*SR)
        if i >= n or i < 0:
            return
        mono = mono[:n - i]*10**(ganho_db/20)
        a = (pan + 1)*math.pi/4
        som[i:i + len(mono), 0] += mono*math.cos(a)
        som[i:i + len(mono), 1] += mono*math.sin(a)

    cache = {}
    for inicio, nome, ganho, pan, velocidade in eventos():
        amostra = cache.setdefault(nome, base.ler_efeito(nome))
        if velocidade != 1:
            amostra = np.interp(np.arange(0, len(amostra) - 1, velocidade), np.arange(len(amostra)), amostra).astype(np.float32)
        por(inicio, amostra, ganho, pan)
    # The call's spray on the wall and the shine of its credits, on this video's clock.
    por(ch.C_MURO + .05 - DESVIO, ch.spray(.36), -16, .2)
    brilho = base.brilho_sonoro()
    por(ch.C_CREDITOS + .15 - DESVIO, brilho, -18, 0)
    por(C_FINAL + 1.0, brilho, -12, 0)
    fala = voz(n)
    som *= abaixar_sob_a_voz(fala)[:, None]
    por(0, fala, 0, 0)
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
        print(' '.join(f'{k}={v:.2f}' for k, v in T.items()), f'final={C_FINAL:.2f}', f'fim={DURACAO}')
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
        for dados in pool.imap(quadro_bytes, range(total), chunksize=3):
            ffmpeg.stdin.write(dados)
    ffmpeg.stdin.close()
    if ffmpeg.wait():
        raise SystemExit('ffmpeg falhou')
    print(args.saida)


if __name__ == '__main__':
    main()
