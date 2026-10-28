#!/usr/bin/env python3
"""Build the Stories teaser that sends people to Part 2: timeline-stories.json and its
voice track, narracao-ep02-stories.wav, in about 14 seconds.

It is a trailer cut from Part 2's own recordings, as montar_timeline.py prepares them:
the friend's first line, the narrator reading the message, the car at the gate and the
closing question. On screen come the part's title, the phone lighting up with the
message, the car with its lights off and, at the end, “FUGIR OU FICAR?” and the call to
watch it on the profile, with room below the handle for a link sticker. Stories cover
the top and bottom of the frame with their own bars, so everything stays between them.
"""
from __future__ import annotations

import json
from pathlib import Path

import montar_timeline as m

HERE = Path(__file__).resolve().parent
AUDIO = m.EPISODE / 'narracao-ep02-stories.wav'
TAIL = 1.8
TITLE = 1.3   # the title card, before the first line
LAYOUT = m.INSTAGRAM


def piece(words, voice, first, last):
    # One stretch of a recording, from just before its first word to just after its last.
    w = words[voice][1]
    a = w[first]['start'] - m.LEAD
    b = w[last]['end'] + m.TRAIL
    if first > 0:
        a = max(a, (w[first-1]['end'] + w[first]['start'])/2)
    if last + 1 < len(w):
        b = min(b, (w[last]['end'] + w[last+1]['start'])/2)
    return ('voice', voice, first, last, max(0, a), b)


def main():
    words, _ = m.load_words()
    ref = {'friend': m.A('Eles tão te'), 'friend_end': m.A('procurando também.', 1),
           'quote': m.N('"Já tá com'), 'quote_end': m.N('com ele?"', 1),
           'car': m.N('Lá fora, um'), 'car_end': m.N('farol apagado.', 1),
           'ask': m.P('E agora:'), 'ask_end': m.P('ou ficar?', 1)}
    pieces = [('gap', TITLE),
              piece(words, *ref['friend'], ref['friend_end'][1]), ('gap', .35),
              # The phone buzzes and lights up before the narrator reads the message.
              ('gap', 1.0), piece(words, *ref['quote'], ref['quote_end'][1]), ('gap', .45),
              piece(words, *ref['car'], ref['car_end'][1]), ('gap', .5),
              piece(words, *ref['ask'], ref['ask_end'][1])]
    at, length = m.timing(words, pieces)
    end = round(length + TAIL, 2)
    gains = m.join(words, pieces, AUDIO)
    ed = m.Edit(at, end, LAYOUT)
    s, e, cut, x = ed.s, ed.e, ed.cut, LAYOUT['x']
    buzz = round(e(ref['friend_end']) + .35 + .05, 2)
    plan = [
        ('title', 0, dict(kind='art', asset='cena-01-porta-aberta.png', zoom=.06, brightness=.55)),
        ('friend', cut(ref['friend']), dict(kind='art', asset='cena-02-luz-apagada.png', crop=m.FRIEND02, zoom=.05,
                                            brightness=.55)),
        ('phone', buzz, dict(kind='art', asset='cena-06-celular-mesa.png', crop=m.PHONE06, zoom=.07,
                             screen=m.SCREEN_MESSAGE)),
        ('car', cut(ref['car']), dict(kind='art', asset='cena-07-carro.png', zoom=.05)),
        ('lights-off', cut(m.N('De farol apagado.')), dict(kind='art', asset='cena-07-carro.png', crop=m.CAR07, zoom=.08,
                                                          brightness=.8)),
        ('end', cut(ref['ask']), dict(kind='art', asset='cena-07-carro.png', zoom=.03, direction='out', brightness=.4)),
    ]
    AT = {name: t for name, t, _ in plan}
    scenes = [{'start': t, 'end': plan[k+1][1] if k + 1 < len(plan) else end, **f} for k, (_, t, f) in enumerate(plan)]
    graphics = [
        {'type': 'vignette', 'start': AT['phone'], 'end': AT['car'], 'color': 'alert', 'strength': .8},
        {'type': 'vignette', 'start': AT['lights-off'], 'end': AT['end'], 'color': 'alert', 'strength': .9},
        {'type': 'tag', 'start': .1, 'end': AT['friend'], 'text': 'PARTE 2', 'y': 470, 'size': 34},
        m.phrase(.15, AT['friend'], 640, [m.line('A DÍVIDA', .2, 'yellow', size=104),
                                          m.line('JÁ TÁ NO AR', .55, size=54)], 104),
        m.phrase(s(ref['friend']) - .05, AT['phone'], 900, [m.line('“ELES TÃO', s(ref['friend'])),
                                                            m.line('TE PROCURANDO.”', s(m.A('te procurando.')), 'yellow')],
                 60),
        m.phrase(s(ref['car']), AT['lights-off'], 900, [m.line('UM CARRO', s(m.N('um carro para'))),
                                                        m.line('NO PORTÃO.', s(m.N('ao portão.')), 'yellow')], 70),
        m.phrase(AT['lights-off'], AT['end'], 900, [m.line('DE FAROL', s(m.N('De farol apagado.'))),
                                                    m.line('APAGADO.', s(m.N('apagado.')), 'red', shake=True)], 80),
        # The call: the question, then where to watch, with room below for a link sticker.
        m.phrase(AT['end'], end + .5, 400, [m.line('FUGIR OU', s(m.P('fugir ou ficar?'))),
                                            m.line('FICAR?', s(m.P('ficar?')), 'yellow')], 88),
        m.phrase(e(ref['ask_end']), end + .5, 640, [m.label('A PARTE 2', e(ref['ask_end']) + .05, size=26, color='yellow'),
                                                    m.line('JÁ TÁ NO PERFIL', e(ref['ask_end']) + .2, size=56)], 56),
        {'type': 'pointer', 'start': round(e(ref['ask_end']) + .45, 2), 'end': end + .5, 'y': 790, 'text': m.HANDLE},
    ]
    effects = [
        m.sfx('impacto.wav', .12, -5),
        *[m.sfx('whoosh.wav', AT[n] - m.WHOOSH_PEAK, -2) for n in ('friend', 'car', 'end')],
        m.sfx('vibracao.wav', buzz - .05, -6),
        m.sfx('notificacao.wav', buzz + .3, -8),
        m.sfx('impacto.wav', s(ref['quote']) - .05, -6),
        m.sfx('carro.wav', e(m.N('ao portão.', 1)) - 1.6, -6),
        m.sfx('impacto.wav', AT['lights-off'] - .02, -5),
        *[m.sfx('pop.wav', t, -10) for t in (s(m.P('ficar?')), e(ref['ask_end']) + .2, e(ref['ask_end']) + .45)],
    ]
    graphics_check = m.too_wide(graphics, LAYOUT['width'])
    if graphics_check:
        raise ValueError(f'Lines wider than the safe area: {graphics_check}')
    m.graficos.check(graphics)
    timeline = {'timing_status': 'aligned_to_voice', 'style': 'guia-de-estilo-referencia.md',
                'note': 'Stories teaser for Part 2, cut from the episode’s own recordings.',
                'audio': AUDIO.name, 'tail': TAIL, 'scenes': scenes, 'graphics': graphics, 'sfx': effects, 'captions': []}
    (HERE / 'timeline-stories.json').write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'timeline-stories.json: {len(scenes)} scenes, ends at {end}s; gains ' +
          ', '.join(f'{v} {g:+.1f} dB' for v, g in gains.items()))


if __name__ == '__main__':
    main()
