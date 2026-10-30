#!/usr/bin/env python3
"""Part 3's announcement: "A parte 3 sai hoje à noite", and the last hours to become an ally.

For the stories and the feed on Friday 30/10/2026, the day the allies' places close at 21h. It is
made with the "Vire aliado" call's tools (../chamada-aliado/animar.py) and lines the narrator has
already recorded there, so it needs no new voice. 1080 × 1920 at 30 fps, about 12 s:

  (no voice)                          Part 2's car at the gate: "PARTE 3 · SAI HOJE À NOITE".
  "Quer aparecer na parte três?"      Part 3's card turns to "hoje à noite".
  "Vire aliado do Zinho."             Zinho rises, pointing at you.
  "São até trinta vagas, até sexta, às nove da noite."   the 30 places and "SÓ ATÉ HOJE, 21H".
  (no voice)                          Zinho calls you in: "PARTE 3 HOJE À NOITE", "VIRE ALIADO ATÉ 21H".

    python animar.py                          # the video, next to this script
    python animar.py --quadros 1 3.5 8 11     # stills for a look, in work/
"""
from __future__ import annotations

import argparse
from functools import lru_cache
import importlib.util
import math
from multiprocessing import Pool
from pathlib import Path
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
SERIE = HERE.parent

_spec = importlib.util.spec_from_file_location('animar_chamada', SERIE / 'chamada-aliado' / 'animar.py')
ch = importlib.util.module_from_spec(_spec)
sys.modules['animar_chamada'] = ch
_spec.loader.exec_module(ch)
base = ch.base

from animar_agradecimento import (  # noqa: E402
    W, H, FPS, SR, FUNDO, CREME, VERMELHO, VERMELHO_ESCURO, VERMELHO_TEXTO, AZUL_ESCURO, TINTA, OURO, prog,
    sai_cubica, sai_volta, texto, colar, retangulo, aparece, passagem)

SAIDA = HERE / 'anuncio-parte-03.mp4'
CARRO = SERIE / 'episodio-02' / 'cena-07-carro.png'

# The three lines, cut from the call's two takes in the narrator's own pauses: (take, first word,
# last word, where it is cut before its first word). The second take's "São" starts at 3.08 s, ahead
# of its mark (see ../chamada-aliado/animar.py).
_T1, _T2 = ch._TOMADA_1, ch._TOMADA_2
FALAS = [(ch.NARRACAO, _T1, 0, 4, 0.0), (ch.NARRACAO, _T1, 5, 8, _T1[5]['start'] - .06),
         (ch.NARRACAO_30, _T2, 12, 21, ch.CORTE_30)]
ANTES_DA_VOZ = 2.6   # the opening, with no voice
ENTRE = .3           # between lines, where the picture cuts
FIM = 2.8            # the close, with no voice


def _horario():
    """Where each line starts in the video, and the video time of every word the picture follows."""
    inicios, t = [], ANTES_DA_VOZ
    for _, palavras, i, j, corte in FALAS:
        inicios.append(t)
        t += palavras[j]['end'] + .12 - corte + ENTRE
    marcas = {}
    for k, (_, palavras, i, j, corte) in enumerate(FALAS):
        for n in range(i, j + 1):
            marcas[(k, n)] = inicios[k] + palavras[n]['start'] - corte
    return inicios, marcas, t - ENTRE


INICIOS, _M, VOZ_FIM = _horario()
T = {'quer': _M[(0, 0)], 'parte': _M[(0, 3)], 'vire': _M[(1, 5)], 'aliado': _M[(1, 6)], 'zinho': _M[(1, 8)],
     'sao': _M[(2, 12)], 'ate_30': _M[(2, 13)], 'trinta': _M[(2, 14)], 'ate': _M[(2, 16)]}
C_PERGUNTA = INICIOS[0] - .2
C_VIRE = INICIOS[1] - .1
C_VAGAS = INICIOS[2] - .1
C_FINAL = VOZ_FIM + .3
DURACAO = round((C_FINAL + FIM)*FPS)/FPS

A = {}


def carregar():
    if A:
        return
    ch.carregar()
    A['carro'] = ch.cobrir(Image.open(CARRO).convert('RGB'))
    A['frente'] = carta_hoje()


@lru_cache(maxsize=1)
def carta_hoje():
    """Part 3's card from the thank-you, its front saying "hoje à noite" instead of "em breve"."""
    w, h = 330, 586
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, w - 1, h - 1), 26, fill=FUNDO + (255,), outline=VERMELHO + (255,), width=8)
    for valor, tam, cor, cy in (('PARTE 3', 74, VERMELHO_TEXTO, .36), ('hoje', 50, CREME, .49), ('à noite', 50, CREME, .58)):
        s = texto(valor, tam, cor, 'ExtraBold' if tam > 60 else 'Bold', sombra=False)
        im.alpha_composite(s, ((w - s.width)//2, round(h*cy - s.height/2)))
    return im


# ---------------------------------------------------------------- scenes

def cena_noite(t):
    """The opening, with no voice: Part 2's car at the gate, and the news."""
    zoom = 1 + .06*t/C_PERGUNTA
    car = A['carro']
    w, h = W/zoom, H/zoom
    tela = car.resize((W, H), Image.Resampling.BICUBIC, box=((W - w)/2, (H - h)*.45, (W + w)/2, (H - h)*.45 + h))
    tela.alpha_composite(Image.new('RGBA', (W, H), (8, 6, 12, 90)))
    aparece(tela, ch.etiqueta('PARTE 3', 78), W/2, 300, .1, t, tipo='pancada', angulo=-3)
    aparece(tela, texto('SAI HOJE', 150, CREME, contorno=10), W/2, 480, .4, t, tipo='pancada')
    aparece(tela, texto('À NOITE', 170, OURO, contorno=11), W/2, 650, .75, t, tipo='pancada')
    return ch.sacudir(tela, t, .75, 14, cor=(8, 6, 12))


def cena_pergunta(t):
    """"Quer aparecer na parte três?": Part 3's card spins in and turns to "hoje à noite"."""
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    base.faixas_da_jaqueta(tela, t)
    entra = prog(t, C_PERGUNTA + .04, C_PERGUNTA + .55)
    escala = (.2 + .8*sai_volta(entra, 1.3))*1.3
    angulo = -24*(1 - sai_cubica(entra)) + 2*math.sin(t*1.8)
    y = 1030 + 10*math.sin(t*2.2)
    vira = prog(t, T['parte'] + .05, T['parte'] + .45)
    face = A['frente'] if vira >= .5 else base.A['verso']
    colar(tela, base.A['carta_sombra'], W/2 + 14, y + 26, escala, angulo, .85)
    colar(tela, face, W/2, y - 30*math.sin(math.pi*vira), escala, angulo, escala_x=max(.02, abs(math.cos(math.pi*vira))))
    base.brilho(tela, t, T['parte'] + .45)
    aparece(tela, texto('QUER APARECER', 100, CREME), W/2, 330, T['quer'], t)
    aparece(tela, texto('NA PARTE 3?', 138, VERMELHO_TEXTO, contorno=8), W/2, 470, T['parte'] - .05, t, tipo='pancada')
    return ch.sacudir(tela, t, T['parte'] - .05, 10, cor=AZUL_ESCURO)


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


def cena_vagas(t):
    """"São até trinta vagas, até sexta, às nove da noite.": the 30 places, and only until tonight."""
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    base.faixas_da_jaqueta(tela, t)
    aparece(tela, texto('ATÉ', 90, CREME), W/2, 300, T['ate_30'] - .02, t)
    aparece(tela, texto('30 VAGAS', 150, VERMELHO_TEXTO, contorno=8), W/2, 440, T['trinta'], t, tipo='pancada')
    for i in range(30):
        coluna, linha = i % 5, i // 5
        aparece(tela, ch.vaga(i + 1), 156 + coluna*192, 640 + linha*112, T['sao'] + .02*i, t)
    if t >= T['ate'] - .05:
        colar(tela, relogio(t), W/2, 1400, sai_volta(prog(t, T['ate'] - .05, T['ate'] + .25)), alfa=prog(t, T['ate'] - .05, T['ate']))
    return ch.sacudir(tela, t, T['trinta'], 12, cor=AZUL_ESCURO)


def relogio(t):
    """'Só até hoje, 21h', with a clock whose hand runs, like the call's deadline."""
    painel = retangulo((860, 150), 75, VERMELHO + (255,), TINTA + (255,), 6)
    d = ImageDraw.Draw(painel)
    cx, cy, r = 92, 75, 46
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=CREME + (255,), outline=TINTA + (255,), width=5)
    a = (t - T['ate'])*5
    d.line((cx, cy, cx + r*.75*math.sin(a), cy - r*.75*math.cos(a)), fill=TINTA + (255,), width=6)
    d.line((cx, cy, cx + r*.5*math.sin(a/12), cy - r*.5*math.cos(a/12)), fill=TINTA + (255,), width=7)
    s = texto('SÓ ATÉ HOJE, 21H', 66, CREME, sombra=False)
    painel.alpha_composite(s, (170, (150 - s.height)//2))
    return painel


def cena_final(t):
    """The close, with no voice: Zinho calls you in; Part 3 tonight, allies until 21h."""
    tela = Image.new('RGBA', (W, H), (0, 0, 0, 255))
    base.raios(tela, t)
    ch.zinho_sobe(tela, t, C_FINAL + .05, 'chamando', .74, 1990)
    aparece(tela, texto('PARTE 3', 120, CREME, contorno=9), W/2, 330, C_FINAL + .3, t, tipo='pancada')
    aparece(tela, texto('HOJE À NOITE', 104, OURO, contorno=8), W/2, 470, C_FINAL + .55, t, tipo='pancada')
    aparece(tela, ch.etiqueta('VIRE ALIADO ATÉ 21H', 66), W/2, 640, C_FINAL + .95, t, angulo=4)
    ch.cintilar(tela, t, C_FINAL + 1.0, ((95, 245), (990, 300), (125, 505), (955, 545), (900, 760)))
    return ch.sacudir(tela, t, C_FINAL + .3, 14, cor=VERMELHO_ESCURO)


ROTEIRO = [
    (0.0, cena_noite, None),
    (C_PERGUNTA, cena_pergunta, ('faixa', VERMELHO, True)),
    (C_VIRE, cena_vire, None),
    (C_VAGAS, cena_vagas, ('empurra', False)),
    (C_FINAL, cena_final, ('faixa', VERMELHO, True)),
]


def quadro(t):
    carregar()
    i = max(k for k, (inicio, _, _) in enumerate(ROTEIRO) if t >= inicio)
    inicio, cena, entrada = ROTEIRO[i]
    if entrada and entrada[0] == 'faixa' and t < inicio + .3:
        tela = passagem(t, inicio, .3, ROTEIRO[i - 1][1], cena, entrada[1], para_direita=entrada[2])
    elif entrada and entrada[0] == 'empurra' and t < inicio + ch.EMPURRA:
        tela = ch.empurra(t, inicio, ch.EMPURRA, ROTEIRO[i - 1][1], cena, vertical=entrada[1])
    else:
        tela = cena(t)
    tela.alpha_composite(base.A['grao'])
    return tela.convert('RGB')


def quadro_bytes(i):
    return quadro(i/FPS).tobytes()


# ---------------------------------------------------------------- sound

def eventos():
    """Every effect: time, effect, gain in dB, pan (-1 left … 1 right), speed."""
    ev = [
        (0.0, 'carro', -16, .3, 1), (.1, 'pop', -12, 0, 1), (.4, 'impacto', -7, 0, 1), (.75, 'impacto-suave', -6, 0, 1),
        (C_PERGUNTA - .02, 'whoosh', -10, -.6, .9), (T['parte'] - .05, 'impacto-suave', -11, 0, 1), (T['parte'] + .05, 'whoosh', -15, 0, 1.6),
        (C_VIRE, 'impacto', -6, 0, 1), (C_VIRE + .02, 'whoosh', -10, 0, 1.05), (T['aliado'], 'impacto-suave', -10, 0, 1),
        (C_VAGAS, 'whoosh', -13, .4, 1.4), (T['trinta'], 'impacto-suave', -10, 0, 1),
        (C_FINAL - .02, 'whoosh', -6, -.6, .9), (C_FINAL + .05, 'whoosh', -9, 0, 1.05), (C_FINAL + .3, 'impacto', -4, 0, 1),
        (C_FINAL + .55, 'impacto-suave', -6, 0, 1), (C_FINAL + .95, 'pop', -7, 0, 1), (C_FINAL + 1.0, 'notificacao', -10, 0, 1),
    ]
    for k, i in enumerate(range(0, 30, 3)):
        ev.append((T['sao'] + .02*i, 'pop', -19, (-1)**k*.4, 1 + .06*k))
    for i in range(6):
        ev.append((T['ate'] + .1 + i*.16, 'tique', -14, 0, 1))
    return ev


def ler(caminho):
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(caminho), '-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32)


def voz(n):
    """The three lines at their places in the video. The second take is brought to the first's level by
    the sentence both say ("E vai na legenda do post, com o seu número de aliado.")."""
    rms = lambda x: np.sqrt(np.mean(x**2))
    tomadas = {ch.NARRACAO: ler(ch.NARRACAO), ch.NARRACAO_30: ler(ch.NARRACAO_30)}
    trecho = lambda som, p, i, j: som[int(p[i]['start']*SR):int(p[j]['end']*SR)]
    ganho = {ch.NARRACAO: 1.0, ch.NARRACAO_30: rms(trecho(tomadas[ch.NARRACAO], _T1, 25, 36))/rms(trecho(tomadas[ch.NARRACAO_30], _T2, 0, 11))}
    fala = np.zeros(n, np.float32)
    curto, queda = int(.01*SR), int(.06*SR)
    for inicio, (arquivo, palavras, i, j, corte) in zip(INICIOS, FALAS):
        parte = tomadas[arquivo][int(corte*SR):int((palavras[j]['end'] + .12)*SR)]*ganho[arquivo]
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
    brilho = base.brilho_sonoro()
    por(T['parte'] + .45, brilho, -16, 0)
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
        for i, dados in enumerate(pool.imap(quadro_bytes, range(total), chunksize=3)):
            ffmpeg.stdin.write(dados)
    ffmpeg.stdin.close()
    if ffmpeg.wait():
        raise SystemExit('ffmpeg falhou')
    print(args.saida)


if __name__ == '__main__':
    main()
