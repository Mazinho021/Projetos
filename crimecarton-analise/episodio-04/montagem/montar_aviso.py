#!/usr/bin/env python3
"""A short notice for Stories, TikTok and Shorts: Part 4 comes out tomorrow.

On 04/11/2026, Part 4's voices were ready but its drawings were not: Codex had hit its usage
limit twice. The creator asked for a short video saying the story comes back tomorrow because of
technical problems. It also works as a teaser:

- it opens with the part's own first line, which the narrator already recorded for the episode,
  “Quem sequestrou o seu amigo vai mostrar o rosto.”, over Part 3's cobrador, sitting in the
  shadow and turning the ring;
- then a black card says the part comes back tomorrow, with the clock ticking.

Everything stays left of TikTok's buttons and below its search bar, so the same file serves
every app. Writes vozes/aviso.wav and timeline-aviso.json; render with
../../episodio-01/montagem/render_animatic.py --timeline timeline-aviso.json.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
sys.path.insert(0, str(EPISODE.parent / 'episodio-01' / 'montagem'))
import graficos  # noqa: E402

FALA = EPISODE / 'narracao-ep04-narrador.wav'
WORDS = json.loads((HERE / 'alinhamento-narrador.json').read_text(encoding='utf-8'))['words']
AUDIO = HERE / 'vozes' / 'aviso.wav'
VOZ_FIM = 2.9          # the first line ends at 2.56 s; the next starts at 3.46 s
DURACAO, TAIL = 9.6, 1.4
X = 330                # left of TikTok's buttons, as in the vertical version
WHOOSH_PEAK = .36


def s(i):
    return round(WORDS[i]['start'], 2)


def line(text, at, color='white', **kw):
    return {'text': text, 'at': round(at, 2), 'color': color, **kw}


def label(text, at, **kw):
    return {'style': 'label', 'text': text, 'at': round(at, 2), **kw}


def sfx(sound, at, gain):
    return {'sound': sound, 'at': round(at, 3), 'gain': round(gain, 1)}


def main():
    AUDIO.parent.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', FALA,
                    '-af', f'atrim=0:{VOZ_FIM},afade=t=out:st={VOZ_FIM - .25:.2f}:d=0.25,apad=whole_dur={DURACAO}', '-ac', '1',
                    '-c:a', 'pcm_s16le', AUDIO], check=True)
    end = DURACAO + TAIL
    card = 3.5
    scenes = [
        {'start': 0, 'end': card, 'kind': 'art', 'asset': '../episodio-03/cena-35-calma.png', 'zoom': .06},
        {'start': card, 'end': end, 'kind': 'black'},
    ]
    graphics = [
        {'type': 'tag', 'start': .15, 'end': end, 'text': 'PARTE 4', 'y': 297, 'x': 112, 'size': 32},
        {'type': 'vignette', 'start': 0, 'end': card, 'color': 'alert', 'strength': .55},
        {'type': 'phrase', 'start': 0, 'end': card, 'y': 900, 'size': 70, 'x': X,
         'lines': [label('QUEM SEQUESTROU O SEU AMIGO', 0), line('VAI MOSTRAR', s(5)),
                   line('O ROSTO.', s(8), 'yellow', shake=True)]},
        {'type': 'phrase', 'start': card + .1, 'end': end, 'y': 560, 'size': 64, 'x': X,
         'lines': [label('POR PROBLEMAS TÉCNICOS,', card + .3), line('A HISTÓRIA', card + .8),
                   line('VOLTA AMANHÃ.', card + 1.3, 'yellow', size=60, shake=True)]},
        {'type': 'box', 'start': card + 2.4, 'end': end, 'y': 800, 'x': X, 'title': 'O DONO DO ANEL',
         'sub': 'parte 4 · as outras estão no perfil'},
        {'type': 'pointer', 'start': card + 3.2, 'end': end, 'y': 960, 'x': X, 'text': '@golpecartoon'},
    ]
    graficos.check(graphics)
    effects = [
        sfx('impacto.wav', s(8) - .04, -5),
        sfx('whoosh.wav', card - WHOOSH_PEAK, -2),
        sfx('impacto.wav', card + 1.26, -6),
        sfx('pop.wav', card + 2.4, -10),
        sfx('pop.wav', card + 3.2, -10),
        *[sfx('tique.wav', card + .3 + .5*k, -16) for k in range(int((end - card - .6)/.5))],
    ]
    timeline = {'timing_status': 'aligned_to_voice', 'style': 'guia-de-estilo-referencia.md',
                'audio': str(AUDIO.relative_to(EPISODE)), 'tail': TAIL, 'scenes': scenes, 'graphics': graphics,
                'sfx': effects, 'captions': [], 'effects': []}
    (HERE / 'timeline-aviso.json').write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'timeline-aviso.json: {len(scenes)} scenes, {len(graphics)} graphics, {len(effects)} sound effects, ends at {end}s')


if __name__ == '__main__':
    main()
