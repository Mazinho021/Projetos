#!/usr/bin/env python3
"""Toninho's recorded offer, as it plays on Zinho's phone for Ademir.

In Part 6, Zinho plays the recording he made in Part 5's car: “Me ajuda a pegar o dinheiro antes do
Ademir, e a gente divide.” It is not generated again: this cuts the line from Part 5's Toninho take
(../../episodio-05/narracao-ep05-toninho.wav), by its words in Part 5's alignment, and passes it
through the phone speaker of voz_cobranca.py (Part 3), because it is a recording playing on a phone.

Writes vozes/toninho-gravacao.wav, gravacao-toninho.txt (its words) and
alinhamento-toninho-gravacao.json (their times in the cut), for montar_timeline.py.

Needs FFmpeg.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import unicodedata

HERE = Path(__file__).resolve().parent
SERIE = HERE.parent.parent
FONTE = SERIE / 'episodio-05' / 'narracao-ep05-toninho.wav'
ALINHAMENTO = SERIE / 'episodio-05' / 'montagem' / 'alinhamento-toninho.json'
FALA = 'Me ajuda a pegar o dinheiro antes do Ademir, e a gente divide.'
PHONE = 'highpass=f=300,lowpass=f=3400,acompressor=threshold=-24dB:ratio=3:attack=5:release=80'
ANTES, DEPOIS = .12, .25


def norm(t):
    t = unicodedata.normalize('NFD', t.lower())
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in t if unicodedata.category(c) != 'Mn'))


def main():
    palavras = json.loads(ALINHAMENTO.read_text(encoding='utf-8'))['words']
    alvo = [norm(w) for w in FALA.split()]
    tokens = [norm(w['text']) for w in palavras]
    i = next(k for k in range(len(tokens)) if tokens[k:k + len(alvo)] == alvo)
    trecho = palavras[i:i + len(alvo)]
    a = max(0, trecho[0]['start'] - ANTES)
    b = trecho[-1]['end'] + DEPOIS
    if i + len(alvo) < len(palavras):
        b = min(b, (trecho[-1]['end'] + palavras[i + len(alvo)]['start'])/2)
    saida = HERE / 'vozes' / 'toninho-gravacao.wav'
    saida.parent.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', FONTE, '-af',
                    f'atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,{PHONE},'
                    f'afade=t=in:d=0.02,afade=t=out:st={b - a - .05:.3f}:d=0.05',
                    '-ar', '24000', '-ac', '1', '-c:a', 'pcm_s16le', saida], check=True)
    words = [{'i': k, 'text': w['text'], 'start': round(w['start'] - a, 3), 'end': round(w['end'] - a, 3)}
             for k, w in enumerate(trecho)]
    (HERE / 'gravacao-toninho.txt').write_text(FALA + '\n', encoding='utf-8')
    (HERE / 'alinhamento-toninho-gravacao.json').write_text(
        json.dumps({'source': str(FONTE.relative_to(SERIE)), 'cut': [round(a, 3), round(b, 3)], 'words': words},
                   ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{saida.name}: {b - a:.2f} s, de {a:.2f} a {b:.2f} s da gravação da Parte 5')


if __name__ == '__main__':
    main()
