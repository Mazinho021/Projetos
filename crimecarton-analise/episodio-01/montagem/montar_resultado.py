#!/usr/bin/env python3
"""Build the short video that announces the Parte 1 vote, for Instagram Stories.

Same look and voice as the episode, on its own narration, narracao-resultado-ep01.wav:
“A maioria decidiu: abrir. Na parte dois, a porta se abre, e o homem que vendeu seu
nome vai ter que se explicar. Mas dá para acreditar nele?” The door, the answer that
slams in, the whole room, the friend at the window and Zinho's doubt follow the words,
which come from alinhamento-resultado.json. No vote counts are shown.

Writes timeline-resultado.json for render_animatic.py.
"""
from __future__ import annotations

import json
import subprocess

from montar_timeline import (CURTAIN09, DOOR09, EPISODE, FRIEND09, HERE, WHOOSH_PEAK, label, line, phrase, sfx,
                             too_wide)
import graficos

AUDIO = EPISODE / 'narracao-resultado-ep01.wav'
WORDS = json.loads((HERE / 'alinhamento-resultado.json').read_text(encoding='utf-8'))['words']
TAIL = 1.8


def s(i):
    return WORDS[i]['start']


def e(i):
    return WORDS[i]['end']


def cut(i, lead=.12):
    return round(s(i) - lead, 2)


def main():
    duration = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', AUDIO],
                                    check=True, capture_output=True, text=True).stdout)
    end = round(duration + TAIL, 2)
    plan = [(0, dict(asset='cena-09-porta.png', crop=DOOR09, zoom=.06, brightness=.5)),
            (cut(4), dict(asset='cena-09-porta.png', zoom=.04, direction='out', brightness=.45)),
            (cut(11), dict(asset='cena-09-porta.png', crop=FRIEND09, zoom=.06)),
            (cut(23), dict(asset='cena-09-porta.png', crop=CURTAIN09, zoom=.08, brightness=.8))]
    scenes = [{'start': t, 'end': plan[n+1][0] if n+1 < len(plan) else end, 'kind': 'art', **fields}
              for n, (t, fields) in enumerate(plan)]
    graphics = [
        # Drawn first, under the rest: the red alarm while Zinho doubts him.
        {'type': 'vignette', 'start': cut(23), 'end': end + .5, 'color': 'alert', 'strength': .7},
        # The first line is already on screen in the first frame: Stories are tapped through fast.
        phrase(0, cut(4) - .05, 560, [line('A MAIORIA', -.07, size=64), line('DECIDIU:', -.07, size=64),
                                      line('ABRIR', s(3), 'yellow', size=150, shake=True)], 80),
        phrase(cut(4) + .05, cut(11) - .05, 600, [label('NA PARTE 2', s(4)), line('A PORTA', s(7)),
                                                  line('SE ABRE.', s(9), 'yellow')], 80),
        phrase(cut(11) + .05, s(18) - .1, 900, [line('VENDEU', s(15)), line('SEU NOME.', s(16), 'yellow')], 72),
        phrase(s(18) - .1, cut(23) - .05, 900, [line('VAI TER QUE', s(18)), line('SE EXPLICAR.', s(21), 'yellow')], 72),
        # Low, on his chest: his eyes stay visible.
        phrase(cut(23) + .05, end + .5, 860, [line('MAS DÁ PARA', s(24)), line('ACREDITAR', s(26)),
                                              line('NELE?', s(27), 'yellow')], 72),
        {'type': 'box', 'start': round(e(27) + .1, 2), 'end': end + .5, 'y': 1045, 'title': 'PARTE 2', 'sub': 'em breve'},
    ]
    wide = too_wide(graphics)
    if wide:
        raise ValueError(f'Lines wider than the safe area: {wide}')
    graficos.check(graphics)
    effects = [sfx('impacto.wav', s(3) - .02, -5),
               *[sfx('whoosh.wav', cut(i) - WHOOSH_PEAK, -2) for i in (4, 11, 23)],
               sfx('impacto-suave.wav', s(15) - .05, -10),
               sfx('pop.wav', e(27) + .1, -10)]
    timeline = {'timing_status': 'aligned_to_voice', 'style': 'guia-de-estilo-referencia.md',
                'alignment': ['alinhamento-resultado.json'], 'audio': AUDIO.name, 'tail': TAIL,
                'scenes': scenes, 'graphics': graphics, 'sfx': effects, 'captions': []}
    (HERE / 'timeline-resultado.json').write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'timeline-resultado.json: {len(scenes)} scenes, {len(graphics)} graphics, {end}s')


if __name__ == '__main__':
    main()
