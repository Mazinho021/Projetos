#!/usr/bin/env python3
"""A 25 s reel with only Part 5's choice, so the question reaches who does not watch to the end.

Six hours after posting Part 5 (08/11/2026), the reel had 1,602 views and no vote in the comments:
96.6% of the viewers did not follow the profile, only 13% were still watching at 22 s and some 5%
reached "Topar ou contar?". The creator asked for a short reel with the choice alone, made only of
what already exists, with no credits spent: Part 5's recorded voices, cut from narracao-ep05.wav,
and its drawings.

- the twist, over Zinho in shock: “O homem que você acabou de livrar da polícia foi o primeiro a te
  roubar.”;
- Toninho's offer, in his balloons: “Me ajuda a pegar o dinheiro antes do Ademir, e a gente
  divide.”;
- option 1, TOPAR, and option 2, CONTAR, each over its scene, with its pros and cons;
- the question, the buttons and the box: the comments may go to Part 6's newspaper.

“VOCÊ DECIDE A PARTE 6” stays at the top from the first frame. Everything stays left of TikTok's
buttons and below its search bar, so one file serves every app. Writes vozes/votacao.wav and
timeline-votacao.json; render with ../../episodio-01/montagem/render_animatic.py.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
sys.path.insert(0, str(EPISODE.parent / 'episodio-01' / 'montagem'))
import graficos  # noqa: E402

spec = importlib.util.spec_from_file_location('montar_timeline_ep05', HERE / 'montar_timeline.py')
mt = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mt)
N, T = mt.N, mt.T

FAIXA = EPISODE / 'narracao-ep05.wav'        # Part 5's joined voices, made by montar_timeline.py
AUDIO = HERE / 'vozes' / 'votacao.wav'
X, TAG_Y, TAIL = 330, 230, 1.6
WHOOSH_PEAK = .36
# The pieces of Part 5's track, by their first and last words, and the silence after each.
PECAS = [
    ('choque', N('O homem que'), N('te roubar.', 1), .35),
    ('oferta', T('Me ajuda'), T('a gente divide.', 2), .45),
    ('topar', N('Se você topar,'), N('dinheiro embora.', 1), 1.7),     # time to read the pros and cons
    ('contar', N('Se contar pro'), N('paga por isso.', 2), 1.7),
    ('escolha', N('Topar ou contar?'), N('a parte seis.', 2), 0),
]
LEAD, TRAIL = .12, .3


def line(text, at, color='white', **kw):
    return {'text': text, 'at': round(at, 2), 'color': color, **kw}


def label(text, at, **kw):
    return {'style': 'label', 'text': text, 'at': round(at, 2), **kw}


def sfx(sound, at, gain):
    return {'sound': sound, 'at': round(at, 3), 'gain': round(gain, 1)}


def tag(text, start, end, y, color='yellow', size=22):
    return {'type': 'tag', 'start': round(start, 2), 'end': round(end, 2), 'text': text, 'y': y, 'x': X,
            'color': color, 'size': size}


def main():
    words = mt.load_words()
    at, _ = mt.timing(words, mt.segments(words))
    # Each piece of the old track goes to the new one: [old start, old end, new start].
    blocos, relogio = [], 0.0
    for nome, primeira, ultima, pausa in PECAS:
        a, b = at[primeira][0] - LEAD, at[ultima][1] + TRAIL
        blocos.append((nome, a, b, relogio))
        relogio += (b - a) + pausa
    duracao = round(relogio, 2)

    def t(ref):
        # A word's start on the new clock.
        x = at[ref][0]
        for _, a, b, novo in blocos:
            if a <= x <= b:
                return round(novo + x - a, 2)
        raise ValueError(f'{ref} is in no piece of the reel')

    def fim(ref):
        x = at[ref][1]
        for _, a, b, novo in blocos:
            if a <= x <= b:
                return round(novo + x - a, 2)
        raise ValueError(f'{ref} is in no piece of the reel')

    graph, rotulos = [], []
    fmt = 'aformat=sample_fmts=flt:channel_layouts=mono'
    for k, (nome, a, b, novo) in enumerate(blocos):
        graph.append(f'[0:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,{fmt},'
                     f'afade=t=in:d=0.02,afade=t=out:st={b - a - .05:.3f}:d=0.05[v{k}]')
        rotulos.append(f'[v{k}]')
        pausa = PECAS[k][3]
        if pausa:
            graph.append(f'aevalsrc=0:d={pausa}:s=24000,{fmt}[p{k}]')
            rotulos.append(f'[p{k}]')
    graph.append(f"{''.join(rotulos)}concat=n={len(rotulos)}:v=0:a=1[out]")
    AUDIO.parent.mkdir(exist_ok=True)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', FAIXA, '-filter_complex', ';'.join(graph), '-map', '[out]',
                    '-ar', '24000', '-c:a', 'pcm_s16le', AUDIO], check=True)

    inicio = {nome: round(novo - (.12 if novo else 0), 2) for nome, _, _, novo in blocos}
    end = round(duracao + TAIL, 2)
    cortes = [inicio[n] for n in ('choque', 'oferta', 'topar', 'contar', 'escolha')] + [end]
    assets = {'choque': ('cena-16-choque.png', .06, 'in'), 'oferta': ('cena-17-toninho-encara.png', .05, 'in'),
              'topar': ('cena-18-opcao-topar.png', .03, 'in'), 'contar': ('cena-19-opcao-contar.png', .03, 'in'),
              'escolha': ('montagem/arte/opcoes-vertical.png', .02, 'out')}
    scenes = []
    for k, nome in enumerate(('choque', 'oferta', 'topar', 'contar', 'escolha')):
        asset, zoom, direcao = assets[nome]
        scenes.append({'start': 0 if k == 0 else cortes[k], 'end': cortes[k + 1], 'kind': 'art', 'asset': asset,
                       'zoom': zoom, 'direction': direcao})
    divide = t(T('e a gente'))
    graphics = [
        # The vote, from the first frame.
        tag('VOCÊ DECIDE A PARTE 6', .05, inicio['escolha'], TAG_Y, 'yellow', 24),
        # The twist.
        {'type': 'vignette', 'start': 0, 'end': inicio['oferta'], 'color': 'alert', 'strength': .7},
        {'type': 'phrase', 'start': .05, 'end': inicio['oferta'], 'y': 930, 'size': 56, 'x': X,
         'lines': [label('QUEM VOCÊ LIVROU DA POLÍCIA', .05), line('FOI O PRIMEIRO', t(N('foi o primeiro'))),
                   line('A TE ROUBAR.', t(N('a te roubar.')), 'red', shake=True)]},
        # The offer.
        {'type': 'nametag', 'start': round(inicio['oferta'] + .2, 2), 'end': divide, 'name': 'TONINHO',
         'sub': 'o motorista do assalto', 'x': X, 'y': 975, 'color': 'alert'},
        {'type': 'balloon', 'start': t(T('Me ajuda')), 'end': divide, 'text': 'Me ajuda a pegar o dinheiro antes do Ademir,',
         'x': 320, 'y': 370, 'tail': {'x': 300, 'y': 420}, 'width': 440},
        {'type': 'balloon', 'start': divide, 'end': inicio['topar'], 'text': 'e a gente divide.', 'x': 320, 'y': 370,
         'tail': {'x': 300, 'y': 420}, 'width': 440},
        {'type': 'phrase', 'start': round(divide - .05, 2), 'end': inicio['topar'], 'y': 950, 'size': 60, 'x': X,
         'lines': [line('R$ 5 MILHÕES', divide, 'green', size=60), label('PRA CADA UM?', t(T('a gente divide.', 2)))]},
        # Option 1.
        tag('OPÇÃO 1 · TOPAR', inicio['topar'] + .05, inicio['contar'], 300, 'white', 24),
        tag('− TRAI O ADEMIR', t(N('trai o Ademir')), inicio['contar'], 950, 'alert'),
        tag('− CONFIA EM QUEM LEVOU O DINHEIRO', t(N('levou o seu dinheiro')), inicio['contar'], 1000, 'alert'),
        tag('+ ELE SABE ONDE O PARCEIRO ESTÁ', fim(N('dinheiro embora.', 1)) + .3, inicio['contar'], 850, 'green'),
        tag('+ O DINHEIRO ANTES DO ADEMIR', fim(N('dinheiro embora.', 1)) + .8, inicio['contar'], 900, 'green'),
        # Option 2.
        tag('OPÇÃO 2 · CONTAR', inicio['contar'] + .05, inicio['escolha'], 300, 'white', 24),
        tag('+ GANHA A CONFIANÇA DO ADEMIR', t(N('ganha a confiança')), inicio['escolha'], 850, 'green'),
        tag('− O TONINHO PAGA POR ISSO', t(N('E o Toninho paga')), inicio['escolha'], 950, 'alert'),
        tag('+ A GRAVAÇÃO PROVA QUE VOCÊ É LEAL', fim(N('paga por isso.', 2)) + .3, inicio['escolha'], 900, 'green'),
        tag('− FICA COM QUEM TE ROUBOU PRIMEIRO', fim(N('paga por isso.', 2)) + .8, inicio['escolha'], 1000, 'alert'),
        # The question.
        {'type': 'phrase', 'start': inicio['escolha'], 'end': end, 'y': 585, 'size': 69, 'x': X,
         'lines': [line('TOPAR', t(N('Topar ou contar?'))), line('OU CONTAR?', t(N('ou contar?', 1)), 'yellow')]},
        {'type': 'buttons', 'start': round(t(N('Comenta uma palavra')) - .05, 2), 'end': end, 'y': 800, 'x': X - 20,
         'prompt': 'COMENTA UMA PALAVRA', 'prompt_at': t(N('Comenta uma palavra')),
         'items': [{'text': 'TOPAR', 'at': t(N('uma palavra só.', 1)), 'style': 'yellow'},
                   {'text': 'CONTAR', 'at': t(N('uma palavra só.', 2)), 'style': 'white'}]},
        {'type': 'box', 'start': t(N('O que a maioria')), 'end': end, 'y': 940, 'x': X, 'title': 'PARTE 6',
         'sub': 'seu comentário pode sair no jornal'},
    ]
    wide = mt.too_wide(graphics, 520)
    if wide:
        raise ValueError(f'Lines wider than the layout allows: {wide}')
    graficos.check(graphics)
    effects = [
        sfx('impacto.wav', t(N('a te roubar.')) - .04, -4),
        *[sfx('whoosh.wav', c - WHOOSH_PEAK, -2) for c in cortes[1:-1]],
        sfx('pop.wav', inicio['oferta'] + .2, -10),
        sfx('impacto-suave.wav', divide - .04, -7),
        *[sfx('pop.wav', x, -14) for x in (t(N('trai o Ademir')), t(N('levou o seu dinheiro')),
                                         t(N('ganha a confiança')), t(N('E o Toninho paga')))],
        *[sfx('pop.wav', x, -16) for x in (fim(N('dinheiro embora.', 1)) + .3, fim(N('dinheiro embora.', 1)) + .8,
                                         fim(N('paga por isso.', 2)) + .3, fim(N('paga por isso.', 2)) + .8)],
        *[sfx('pop.wav', x, -10) for x in (t(N('uma palavra só.', 1)), t(N('uma palavra só.', 2)), t(N('O que a maioria')))],
    ]
    timeline = {'timing_status': 'aligned_to_voice', 'style': 'guia-de-estilo-referencia.md',
                'audio': str(AUDIO.relative_to(EPISODE)), 'tail': TAIL, 'scenes': scenes, 'graphics': graphics,
                'sfx': effects, 'captions': [], 'effects': ['../../episodio-02/montagem/efeitos']}
    (HERE / 'timeline-votacao.json').write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'timeline-votacao.json: {len(scenes)} scenes, {len(graphics)} graphics, {len(effects)} sound effects, '
          f'ends at {end}s; cuts at {cortes}')


if __name__ == '__main__':
    main()
