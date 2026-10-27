#!/usr/bin/env python3
"""Build the short video that announces the Parte 1 vote, for Instagram Stories.

Same look and voice as the episode. The narration is put together from lines the
narrator already recorded, since no new voice was generated: “Você deixa ele entrar?”
from the episode, then “abrir.” and “O que a maioria escolher vira a parte dois.” from
the request to comment. The door shot asks the question again, the majority's answer
slams in and the box promises Parte 2. No vote counts are shown.

Writes timeline-resultado.json and narracao-resultado-votacao.wav for render_animatic.py.
"""
from __future__ import annotations

import json
import subprocess

from montar_timeline import (CTA, CTA_WORDS, DOOR09, EPISODE, HERE, MAIN, WHOOSH_PEAK, WORDS, label, line, loudness,
                             phrase, sfx)

AUDIO = EPISODE / 'narracao-resultado-votacao.wav'
TAIL = 1.6
# (source, start, end, where it plays): seconds in the source file and in the video.
QUESTION = (MAIN, WORDS[166]['start'] - .05, WORDS[169]['end'] + .3, .35)
ANSWER_AT = 2.9
# The first “abrir” of the request: the last one runs into “não”.
ANSWER = (CTA, CTA_WORDS[4]['start'] - .05, CTA_WORDS[4]['end'] + .11, ANSWER_AT)
RULE_AT = ANSWER_AT + 1.45
RULE = (CTA, CTA_WORDS[8]['start'] - .05, CTA_WORDS[16]['end'] + .2, RULE_AT)
REVEAL = 2.5


def narration():
    # The request to comment was recorded quieter than the episode: match it, as the episode does.
    gain = loudness(MAIN) - loudness(CTA)
    parts = [QUESTION, ANSWER, RULE]
    graph = []
    for n, (src, a, b, at) in enumerate(parts):
        boost = f',volume={gain:.2f}dB' if src == CTA else ''
        graph.append(f'[{n}:a]aformat=sample_fmts=flt:channel_layouts=mono,aresample=24000,atrim={a:.3f}:{b:.3f},'
                     f'asetpts=PTS-STARTPTS{boost},afade=t=in:d=0.01,afade=t=out:st={b - a - .04:.3f}:d=0.04,'
                     f'adelay={round(at*1000)}:all=1[p{n}]')
    graph.append(f'{"".join(f"[p{n}]" for n in range(len(parts)))}amix=inputs={len(parts)}:normalize=0:duration=longest[out]')
    cmd = ['ffmpeg', '-y', '-v', 'error']
    for src, *_ in parts:
        cmd += ['-i', src]
    subprocess.run(cmd + ['-filter_complex', ';'.join(graph), '-map', '[out]', '-c:a', 'pcm_f32le', AUDIO], check=True)
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', AUDIO],
                                check=True, capture_output=True, text=True).stdout)


def main():
    duration = narration()
    end = round(duration + TAIL, 2)
    q0 = QUESTION[3] - QUESTION[1]                 # source time to video time for the question
    r0 = RULE_AT - RULE[1]
    scenes = [
        {'start': 0, 'end': REVEAL, 'kind': 'art', 'asset': 'cena-09-porta.png', 'crop': DOOR09, 'zoom': .06,
         'brightness': .5},
        {'start': REVEAL, 'end': end, 'kind': 'art', 'asset': 'cena-09-porta.png', 'zoom': .04, 'direction': 'out',
         'brightness': .45},
    ]
    graphics = [
        # The question is already on screen in the first frame: Stories are tapped through fast.
        phrase(0, REVEAL - .05, 420, [line('VOCÊ DEIXA', -.07), line('ELE ENTRAR?', WORDS[168]['start'] + q0, 'yellow')], 76),
        phrase(REVEAL, end + .5, 560, [label('A MAIORIA ESCOLHEU', REVEAL + .05),
                                       line('ABRIR', ANSWER_AT, 'yellow', size=150, shake=True)], 80),
        {'type': 'box', 'start': round(CTA_WORDS[15]['start'] + r0, 2), 'end': end + .5, 'y': 880, 'title': 'PARTE 2',
         'sub': 'em breve'},
    ]
    effects = [sfx('whoosh.wav', REVEAL - WHOOSH_PEAK, -2), sfx('impacto.wav', ANSWER_AT - .02, -5),
               sfx('pop.wav', CTA_WORDS[15]['start'] + r0, -10)]
    timeline = {'timing_status': 'aligned_to_voice', 'style': 'guia-de-estilo-referencia.md', 'audio': AUDIO.name,
                'tail': TAIL, 'scenes': scenes, 'graphics': graphics, 'sfx': effects, 'captions': []}
    (HERE / 'timeline-resultado.json').write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'timeline-resultado.json: {end}s')


if __name__ == '__main__':
    main()
