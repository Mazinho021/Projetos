#!/usr/bin/env python3
"""A 21 s call for Part 4, to post while its drawings are not ready.

On 04/11/2026 Codex's usage limit held Part 4's drawings for a day, and the creator was worried
about losing the audience. This call is made only from what already exists:

- the part's own opening, recorded by the narrator for the episode: “Quem sequestrou o seu amigo
  vai mostrar o rosto.”, over Part 3's cobrador in the shadow;
- the recap, also recorded: the profile, Renato caught at the wall and the vote, a tie that
  TROCAR won;
- the audience's comments on Part 3 in the newspaper “A VOZ DO BAIRRO”;
- and a last card: Part 4, “O dono do anel”, comes out tomorrow.

Everything stays left of TikTok's buttons and below its search bar, so one file serves every
app. Writes chamada/ (the profile and the memory, from compor_cenas.py), vozes/chamada.wav and
timeline-chamada.json; render with ../../episodio-01/montagem/render_animatic.py.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
sys.path.insert(0, str(EPISODE.parent / 'episodio-01' / 'montagem'))
import graficos  # noqa: E402

FALA = EPISODE / 'narracao-ep04-narrador.wav'
WORDS = json.loads((HERE / 'alinhamento-narrador.json').read_text(encoding='utf-8'))['words']
AUDIO = HERE / 'vozes' / 'chamada.wav'
ARTE = HERE / 'chamada'
X, TAG_Y, TAIL = 330, 297, 1.4
WHOOSH_PEAK = .36
DOOR13 = [0.05, 0.0, 0.95, 0.9]
COMENTARIOS = ['Trocar.', 'Deixar.',
               '(…) só porque ajudou depois de arrependido faz diferença? Tem que deixar se lascar e ir '
               'proteger a família do cara.']


def norm(t):
    t = unicodedata.normalize('NFD', t.lower())
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in t if unicodedata.category(c) != 'Mn'))


TOKENS = [norm(w['text']) for w in WORDS]


def N(phrase, k=0):
    alvo = [norm(p) for p in phrase.split()]
    for i in range(len(TOKENS)):
        if TOKENS[i:i+len(alvo)] == alvo:
            return i + k
    raise ValueError(phrase)


def s(i):
    return round(WORDS[i]['start'], 2)


def e(i):
    return round(WORDS[i]['end'], 2)


def cut(i):
    return round(s(i) - .12, 2)


def line(text, at, color='white', **kw):
    return {'text': text, 'at': round(at, 2), 'color': color, **kw}


def label(text, at, **kw):
    return {'style': 'label', 'text': text, 'at': round(at, 2), **kw}


def sfx(sound, at, gain):
    return {'sound': sound, 'at': round(at, 3), 'gain': round(gain, 1)}


def arte():
    # The profile's grid and Part 3's memory, made by this part's compor_cenas.py.
    spec = importlib.util.spec_from_file_location('compor_cenas_ep04', HERE / 'compor_cenas.py')
    cc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cc)
    ARTE.mkdir(exist_ok=True)
    cc.ARTE = ARTE
    cc.perfil(330/720, 'perfil-vertical.png', 1030)
    cc.lembranca_parte3()


def main():
    arte()
    trocar = N('desempate: trocar.', 1)
    voz_fim = e(trocar) + .3
    jornal_at = round(e(trocar) + .15, 2)
    card = round(jornal_at + 4.2, 2)
    duracao = card + 4.2
    AUDIO.parent.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', FALA, '-af',
                    f'atrim=0:{voz_fim:.2f},afade=t=out:st={voz_fim - .2:.2f}:d=0.2,apad=whole_dur={duracao:.2f}',
                    '-ac', '1', '-c:a', 'pcm_s16le', AUDIO], check=True)
    end = round(duracao + TAIL, 2)
    perfil_at, pego_at, votos_at = cut(N('Chegou agora?')), cut(N('O Renato foi')), cut(N('Deu empate.'))
    scenes = [
        {'start': 0, 'end': perfil_at, 'kind': 'art', 'asset': '../episodio-03/cena-35-calma.png', 'zoom': .06},
        {'start': perfil_at, 'end': pego_at, 'kind': 'art', 'asset': 'montagem/chamada/perfil-vertical.png', 'zoom': .03,
         'direction': 'out'},
        {'start': pego_at, 'end': votos_at, 'kind': 'art', 'asset': 'montagem/chamada/lembranca-parte3.png', 'zoom': .02},
        {'start': votos_at, 'end': card, 'kind': 'art', 'asset': '../episodio-03/cena-13-decisao.png', 'zoom': .03,
         'crop': DOOR13, 'direction': 'out', 'brightness': .35},
        {'start': card, 'end': end, 'kind': 'black'},
    ]
    graphics = [
        {'type': 'tag', 'start': .15, 'end': end, 'text': 'PARTE 4', 'y': TAG_Y, 'x': 112, 'size': 32},
        {'type': 'vignette', 'start': 0, 'end': perfil_at, 'color': 'alert', 'strength': .55},
        {'type': 'phrase', 'start': 0, 'end': perfil_at, 'y': 900, 'size': 64, 'x': X,
         'lines': [label('QUEM SEQUESTROU O SEU AMIGO', 0), line('VAI MOSTRAR', s(N('vai mostrar'))),
                   line('O ROSTO.', s(N('o rosto.')), 'yellow', shake=True)]},
        {'type': 'phrase', 'start': perfil_at + .05, 'end': pego_at, 'y': 790, 'size': 64, 'x': X,
         'lines': [line('CHEGOU AGORA?', s(N('Chegou agora?')), 'yellow', size=58),
                   line('AS PARTES 1, 2 E 3', s(N('As outras partes')), size=47),
                   line('TÃO NO PERFIL', s(N('no perfil.')), size=47)]},
        {'type': 'pointer', 'start': s(N('no perfil.')), 'end': pego_at, 'y': 940, 'x': X, 'text': '@golpecartoon'},
        {'type': 'polaroid', 'start': pego_at + .05, 'end': votos_at, 'image': 'episodio-03/cena-04-mao-anel.png',
         'focus': [0.0, 0.18, 1.0, 0.62], 'caption': 'PARTE 3', 'sub': 'o muro', 'x': X, 'y': 560, 'size': 300, 'angle': -5},
        {'type': 'phrase', 'start': pego_at + .05, 'end': votos_at, 'y': 900, 'size': 60, 'x': X,
         'lines': [line('O RENATO FOI PEGO', s(N('O Renato foi')), size=47),
                   line('NO SEU LUGAR.', s(N('no seu lugar.')), 'yellow')]},
        {'type': 'bars', 'start': votos_at + .05, 'end': jornal_at, 'y': 500, 'x': X, 'width': 500,
         'title': 'PARTE 3 · VOCÊS VOTARAM', 'title_at': s(N('Deu empate.')),
         'items': [{'label': 'TROCAR', 'pct': 50, 'at': round(s(N('Deu empate.')) + .1, 2), 'winner': False},
                   {'label': 'DEIXAR', 'pct': 50, 'at': round(s(N('Deu empate.')) + .25, 2), 'winner': False}]},
        {'type': 'stamp', 'start': round(s(N('Deu empate.', 1)) - .02, 2), 'end': s(N('No desempate:')), 'text': 'EMPATE',
         'y': 860, 'x': X, 'angle': -7, 'color': 'white'},
        {'type': 'phrase', 'start': s(N('No desempate:')) - .02, 'end': jornal_at, 'y': 770, 'size': 40, 'x': X,
         'lines': [label('NO DESEMPATE', s(N('No desempate:')))]},
        {'type': 'stamp', 'start': round(s(trocar) - .02, 2), 'end': jornal_at, 'text': 'TROCAR', 'y': 860, 'x': X,
         'angle': -7, 'color': 'yellow', 'filled': True},
        {'type': 'jornal', 'start': jornal_at, 'end': card, 'y': 340, 'x': X, 'width': 500, 'title': 'A VOZ DO BAIRRO',
         'sub': 'o que vocês comentaram na parte 3',
         'items': [{'text': c, 'at': round(jornal_at + .3 + .5*k, 2)} for k, c in enumerate(COMENTARIOS)]},
        {'type': 'phrase', 'start': card + .1, 'end': end, 'y': 560, 'size': 64, 'x': X,
         'lines': [label('A PARTE 4', card + .3), line('SAI AMANHÃ.', card + .8, 'yellow', size=64, shake=True)]},
        {'type': 'box', 'start': card + 1.8, 'end': end, 'y': 800, 'x': X, 'title': 'O DONO DO ANEL',
         'sub': 'as partes 1, 2 e 3 estão no perfil'},
        {'type': 'pointer', 'start': card + 2.6, 'end': end, 'y': 960, 'x': X, 'text': '@golpecartoon'},
    ]
    graficos.check(graphics)
    effects = [
        sfx('impacto.wav', s(N('o rosto.')) - .04, -5),
        *[sfx('whoosh.wav', t - WHOOSH_PEAK, -2) for t in (perfil_at, pego_at, votos_at, card)],
        sfx('pop.wav', s(N('no perfil.')), -10),
        *[sfx('tique.wav', s(N('Deu empate.')) + .1 + .1*k, -20) for k in range(8)],
        sfx('impacto.wav', s(trocar) - .04, -5),
        sfx('impacto.wav', card + .76, -6),
        sfx('pop.wav', card + 1.8, -10),
        sfx('pop.wav', card + 2.6, -10),
        *[sfx('tique.wav', card + .3 + .5*k, -16) for k in range(int((end - card - .6)/.5))],
    ]
    timeline = {'timing_status': 'aligned_to_voice', 'style': 'guia-de-estilo-referencia.md',
                'audio': str(AUDIO.relative_to(EPISODE)), 'tail': TAIL, 'scenes': scenes, 'graphics': graphics,
                'sfx': effects, 'captions': [], 'effects': []}
    (HERE / 'timeline-chamada.json').write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'timeline-chamada.json: {len(scenes)} scenes, {len(graphics)} graphics, {len(effects)} sound effects, ends at {end}s')


if __name__ == '__main__':
    main()
