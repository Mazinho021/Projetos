#!/usr/bin/env python3
"""Cut the TikTok version of episode 1 into three short teasers.

Each cut is one beat of the story that ends on its own turn: the empty backpack, the
photo on the news, the friend's message and the knock at the door. Together they cover
the whole episode. Every cut has a line on screen from its first frame, since TikTok
viewers decide within a second, and closes on a card pointing to the full Parte 1 on
the profile. Posted between episodes, they show TikTok what the account is about now.

Writes timeline-corte-N.json and narracao-ep01-corte-N.wav for render_animatic.py.
"""
from __future__ import annotations

import json
import subprocess

import graficos
from montar_timeline import (AT, AUDIO_TIKTOK, EPISODE, HERE, HOOK, TAIL, WORDS, label, line, phrase, sfx,
                             shifted, too_wide)

END_CARD = 2.2
# Windows in the Instagram version's seconds; the TikTok version runs HOOK seconds later.
CUTS = [
    dict(n=1, start=0, end=AT['call'], now=True),
    dict(n=2, start=AT['call'], end=AT['audio'], hook=('QUEM VAZOU', 'A SUA FOTO?'), hook_end=2.6),
    dict(n=3, start=AT['audio'], end=AT['choice'], hook=('O ÁUDIO QUE', 'ENTREGOU TUDO.'),
         hook_end=WORDS[121]['start'] - .1 - AT['audio']),
]


def build(c, tl):
    a, b = HOOK + c['start'], HOOK + c['end']
    length = round(b - a, 3)
    scenes = []
    for sc in tl['scenes']:
        if sc['start'] < b - .01 and sc['end'] > a + .01:
            sc = shifted(sc, -a)
            scenes.append(dict(sc, start=max(0, sc['start']), end=min(length, sc['end'])))
    # The end card: the last shot, darkened, under the pointer to the full episode.
    last = scenes[-1]
    scenes.append({'start': length, 'end': round(length + END_CARD, 3), 'kind': 'art', 'asset': last['asset'],
                   **({'crop': last['crop']} if 'crop' in last else {}), 'brightness': .35, 'zoom': .03})
    graphics = []
    for g in tl['graphics']:
        if g['start'] < b - .01 and g['end'] > a + .01:
            # A question asked in the last seconds stays up over the end card.
            keep = g['type'] == 'phrase' and g['end'] > b and g['start'] >= b - 6
            g = shifted(g, -a)
            g = dict(g, start=max(0, g['start']), end=round(length + END_CARD, 3) if keep else min(length, g['end']))
            if c.get('now') and g['type'] == 'phrase' and g['start'] < .5:
                # The opening lines are already on screen in the first frame.
                g = dict(g, start=0, lines=[dict(ln, at=-.07) for ln in g['lines']])
            graphics.append(g)
    if c.get('hook'):
        top, bottom = c['hook']
        graphics.append(phrase(0, c['hook_end'], 560, [line(top, -.07), line(bottom, -.07, 'yellow')], 60))
    graphics.append(phrase(length, length + END_CARD + .5, 720, [
        label('A PARTE QUE FALTOU', length + .05), line('PARTE 1 COMPLETA', length + .12),
        line('NO PERFIL', length + .3, 'yellow')], 52))
    effects = [sfx('impacto.wav', 0, -6), *[shifted(x, -a) for x in tl['sfx'] if a <= x['at'] < b],
               sfx('pop.wav', length + .12, -10)]
    return scenes, graphics, effects, length


def main():
    tl = json.loads((HERE / 'timeline-tiktok.json').read_text(encoding='utf-8'))
    for c in CUTS:
        scenes, graphics, effects, length = build(c, tl)
        wide = too_wide(graphics)
        if wide:
            raise ValueError(f'Lines wider than the safe area: {wide}')
        graficos.check(graphics)
        audio = EPISODE / f'narracao-ep01-corte-{c["n"]}.wav'
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', f'{HOOK + c["start"]:.3f}', '-t', f'{length:.3f}',
                        '-i', AUDIO_TIKTOK, '-c:a', 'pcm_f32le', audio], check=True)
        timeline = {'timing_status': 'aligned_to_voice', 'style': 'guia-de-estilo-referencia.md',
                    'source': 'timeline-tiktok.json', 'window': [round(HOOK + c['start'], 3), round(HOOK + c['end'], 3)],
                    'audio': audio.name, 'tail': END_CARD, 'scenes': scenes, 'graphics': graphics, 'sfx': effects,
                    'captions': []}
        name = f'timeline-corte-{c["n"]}.json'
        (HERE / name).write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'{name}: {len(scenes)} scenes, {len(graphics)} graphics, {len(effects)} sound effects, '
              f'{round(length + END_CARD, 2)}s')


if __name__ == '__main__':
    main()
