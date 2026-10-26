#!/usr/bin/env python3
"""Synthesize the episode's sound effects into efeitos/.

Whoosh, counter tick, notification chime and ringback tone are generated here with
the standard library only. The replay snippet is cut from the friend's voice message,
efeitos/audio-amigo.wav, which voz_amigo.py makes from the narration. Wood
knocks, impacts and pops are CC0 recordings by Kenney, kept as WAV in efeitos/.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import random
import subprocess
import wave

HERE = Path(__file__).resolve().parent
OUT = HERE / 'efeitos'
SR = 48000
FRIEND_LINE = (121, 137)   # the friend's voice message, “Eu estava devendo … no meu lugar.”
FRIEND_PAD = .3            # seconds of the pauses around it that go with it into audio-amigo.wav
REPLAY_WORDS = (126, 137)  # “Disseram que a dívida acabava se eu colocasse alguém no meu lugar.”
REPLAY_PAD = (.05, .12)    # seconds kept before the first word and after the last


def save(name, samples, peak_db=-1.0):
    peak = max(abs(s) for s in samples) or 1
    scale = 10**(peak_db/20) / peak * 32767
    with wave.open(str(OUT / name), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b''.join(int(round(s*scale)).to_bytes(2, 'little', signed=True) for s in samples))


def fade(samples, ms=4):
    n = int(SR*ms/1000)
    for i in range(min(n, len(samples))):
        samples[i] *= i/n
        samples[-1-i] *= i/n
    return samples


def whoosh(dur=.55, peak=.65):
    # Noise through a band-pass whose centre rises, then falls, like air rushing past.
    rnd, out, low, band = random.Random(7), [], 0.0, 0.0
    n = int(dur*SR)
    for i in range(n):
        t = i/n
        fc = 250*(2600/250)**(t/peak) if t < peak else 2600*(900/2600)**((t-peak)/(1-peak))
        f = 2*math.sin(math.pi*fc/SR)
        low += f*band
        band += f*(rnd.uniform(-1, 1) - low - .55*band)
        env = (t/peak)**2 if t < peak else (1 - (t-peak)/(1-peak))**1.5
        out.append(band*env)
    return fade(out)


def tick(dur=.035):
    rnd = random.Random(3)
    return fade([(math.sin(2*math.pi*2300*i/SR) + .25*rnd.uniform(-1, 1)) * math.exp(-i/SR/.005)
                 for i in range(int(dur*SR))], 1)


def chime(dur=.55):
    # Two rising notes, as in a phone's message tone.
    out = []
    for i in range(int(dur*SR)):
        t = i/SR
        s = 0.0
        for start, freq, decay in ((0, 1046.5, .09), (.11, 1568.0, .14)):
            if t >= start:
                u = t - start
                s += (math.sin(2*math.pi*freq*u) + .3*math.sin(4*math.pi*freq*u)) * math.exp(-u/decay) * min(1, u/.003)
        out.append(s)
    return fade(out)


def ringback(dur=.42):
    # The 425 Hz tone heard while a call rings unanswered in Brazil.
    return fade([math.sin(2*math.pi*425*i/SR) for i in range(int(dur*SR))], 15)


def replay_snippet():
    # The key sentence of the friend's message, in his voice from audio-amigo.wav (made by
    # voz_amigo.py), for "Você escuta outra vez". Its bounds come from the word alignment.
    words = json.loads((HERE / 'alinhamento-narracao.json').read_text(encoding='utf-8'))['words']
    start = words[REPLAY_WORDS[0]]['start'] - REPLAY_PAD[0]
    length = words[REPLAY_WORDS[1]]['end'] + REPLAY_PAD[1] - start
    offset = start - (words[FRIEND_LINE[0]]['start'] - FRIEND_PAD)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{offset:.3f}', '-t', f'{length:.3f}',
                    '-i', str(OUT / 'audio-amigo.wav'),
                    '-af', f'afade=t=in:d=0.03,afade=t=out:st={length-.15:.3f}:d=0.15',
                    '-ar', str(SR), '-ac', '1', '-c:a', 'pcm_s16le', str(OUT / 'replay-amigo.wav')], check=True)


def main():
    OUT.mkdir(exist_ok=True)
    save('whoosh.wav', whoosh())
    save('tique.wav', tick())
    save('notificacao.wav', chime())
    save('chamada.wav', ringback())
    replay_snippet()
    print('Sound effects written to', OUT)


if __name__ == '__main__':
    main()
