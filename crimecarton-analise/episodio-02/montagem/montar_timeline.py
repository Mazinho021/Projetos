#!/usr/bin/env python3
"""Build Part 2's narration track and its two timelines from the word alignments.

The track joins, in the order of roteiro-ep02.txt: the series' opening, cut from Part 1's
narration (its first 17 words, the same art and audio in every part); the narrator's
lines from narracao-ep02-narrador.wav; the friend's from narracao-ep02-amigo.wav, in his
own voice; the closing request to comment, FUGIR or FICAR, from narracao-ep02-pedido.wav;
and the pauses the edit opens for sounds, such as the three rings of the call. Each line
is found in its recording by its words, so the script can use them in another order: the
narrator recorded the vote for the friend's name last, and the edit plays it right after
the friend first speaks.
Every cut, graphic and effect is anchored to a word of the script, so the edit follows
the voices again if they are re-aligned.

timeline.json is the Instagram version. timeline-vertical.json, for TikTok and Shorts,
moves the top elements below TikTok's search bar and keeps the rest left of the buttons.
Render each with ../../episodio-01/montagem/render_animatic.py --timeline.

--estimar DIR builds everything in DIR, with estimated word timings and a silent stand-in
for each voice that has no alignment yet, for checking the edit before it exists.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
PART1 = EPISODE.parent / 'episodio-01'
TOOLS = PART1 / 'montagem'
sys.path.insert(0, str(TOOLS))
import graficos  # noqa: E402

SCRIPT = EPISODE / 'roteiro-ep02.txt'
# The opening and the closing request come matched to the narrator by igualar_vozes.py.
VOICES = {'VINHETA': (HERE / 'vozes' / 'vinheta.wav', TOOLS / 'alinhamento-narracao.json'),
          'NARRADOR': (EPISODE / 'narracao-ep02-narrador.wav', HERE / 'alinhamento-narrador.json'),
          # The friend in the voice of his message in Part 1, made by voz_amigo.py.
          'AMIGO': (HERE / 'vozes' / 'amigo.wav', HERE / 'alinhamento-amigo.json'),
          'PEDIDO': (HERE / 'vozes' / 'pedido.wav', HERE / 'alinhamento-pedido.json')}
AUDIO = EPISODE / 'narracao-ep02.wav'
TAIL = 2.0
PART, VOTE = 2, [('ABRIR', 86), ('NÃO ABRIR', 14)]   # Part 1's vote: 6 of 7 comments said ABRIR
HANDLE = '@golpecartoon'
# The friend talks in the room, as loud as the narrator.
FRIEND_GAIN = 0
# Seconds kept before a voice's first word and after its last at a change of voice, and
# the silence between the two voices.
LEAD, TRAIL, SWITCH = .12, .22, .25
WHOOSH_PEAK = .36
# Instagram's and the vertical versions' layouts. TikTok's search bar covers the top
# 146 px: the HUD, the tags and the cards go below it. The like, comment and share column
# covers the right of the lower half: there, the vertical version centres everything at
# x = 330 and moves the cards 25 px left, so nothing passes x = 590.
INSTAGRAM = {'name': 'timeline.json', 'hud_dy': 0, 'tag_y': 230, 'card_top': 300, 'x': 360, 'card_dx': 0,
             'tv_dx': 0, 'tv_scale': 1, 'width': 570, 'bars': 540, 'input': 600}
VERTICAL = {'name': 'timeline-vertical.json', 'hud_dy': 67, 'tag_y': 297, 'card_top': 334, 'x': 330, 'card_dx': -25,
            'tv_dx': -50, 'tv_scale': .88, 'width': 520, 'bars': 500, 'input': 520}


def norm(token):
    t = unicodedata.normalize('NFD', token.lower())
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in t if unicodedata.category(c) != 'Mn'))


def probe(path, entry):
    return subprocess.run(['ffprobe', '-v', 'error', '-show_entries', entry, '-of', 'csv=p=0', path],
                          check=True, capture_output=True, text=True).stdout.split()[0]


def loudness(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128', '-f', 'null', '-'],
                       check=True, capture_output=True, text=True)
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1])


# The text each recording was made from, numbered word by word as the aligner does.
SOURCES = {'VINHETA': EPISODE.parent / 'narracao-ep01-zinho.txt', 'NARRADOR': EPISODE / 'narracao-ep02-narrador.txt',
           'AMIGO': EPISODE / 'narracao-ep02-amigo.txt', 'PEDIDO': EPISODE / 'narracao-ep02-pedido.txt'}
TEXT = {v: [w for w in path.read_text(encoding='utf-8').split() if norm(w)] for v, path in SOURCES.items()}


def find(voice, phrase, after=0):
    # Number of the first word of `phrase` in a voice's recording, from word `after` on.
    words, target = [norm(w) for w in TEXT[voice]], [norm(w) for w in phrase.split()]
    for i in range(after, len(words) - len(target) + 1):
        if words[i:i+len(target)] == target:
            return i
    raise ValueError(f'{phrase!r} is not in the {voice} recording')


def read_script():
    # [(voice, text, first word, last word)] in the script's order, each line located in
    # its recording.
    lines = []
    for raw in SCRIPT.read_text(encoding='utf-8').splitlines():
        if raw.strip():
            voice, text = raw.split(': ', 1)
            first = find(voice, text)
            lines.append((voice, text, first, first + len([w for w in text.split() if norm(w)]) - 1))
    return lines


LINES = read_script()


def N(phrase, k=0):
    return 'NARRADOR', find('NARRADOR', phrase) + k


def A(phrase, k=0):
    return 'AMIGO', find('AMIGO', phrase) + k


def P(phrase, k=0):
    return 'PEDIDO', find('PEDIDO', phrase) + k


def V(i):
    return 'VINHETA', i


# Silence the edit opens after a word, in seconds, for the sounds of the story. Phrases
# point at their first word; the offset picks the word the pause follows. The pause
# replaces the voice's own silence there, except for LEAD and TRAIL around the cut.
PAUSES = {
    N('decidiram: abrir.', 1): .3,      # the vote's stamp lands
    N('a porta.', 1): .9,               # the lock turns and the door opens
    N('na parte três.', 2): .5,         # back to the story after the vote for his name
    N('da sala.', 1): .35,              # the light goes out
    N('sua foto.', 1): .9,              # the stamp "FOI ELE" sinks in
    N('três vezes.', 1): 2.75,          # the second and third rings, then someone answers
    N('dizer nada.', 1): .5,            # the call ends
    N('cima da mesa.', 2): 1.2,         # the phone buzzes twice on the table
    N('"Já tá com ele?"', 3): 1.0,       # the message, under the red alarm
    N('Nem a você.', 2): .8,
    N('ao portão.', 1): 1.4,            # the car stops outside
    N('farol apagado.', 1): 1.0,
}
# Silences at changes of voice other than SWITCH: a breath after the opening, and the
# quick exchange about the debt.
SWITCHES = {V(16): .35, A('Oitenta mil.', 1): .12, N('Para quem?', 1): .12, A('minha mãe mora.', 2): .6}


def estimated_words(voice):
    # Rough timings for a voice that does not exist yet: about 15 characters per second,
    # with pauses at punctuation and between lines.
    t, words = .3, []
    ends = {e for v, _, _, e in LINES if v == voice}
    for i, w in enumerate(TEXT[voice]):
        d = .1 + .062*len(norm(w))
        words.append({'i': i, 'text': w, 'start': round(t, 3), 'end': round(t + d, 3)})
        t += d + (.65 if i in ends else .42 if w[-1] in '.?:!' else .22 if w[-1] == ',' else .04)
    return words, t + .2


def load_words(estimate=None):
    # {voice: (audio, words)} and the voices given silent stand-ins by an estimate.
    words, stand_ins = {}, set()
    for voice, (audio, alignment) in VOICES.items():
        if estimate and not alignment.exists():
            est, duration = estimated_words(voice)
            audio = estimate / audio.name
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono',
                            '-t', f'{duration:.3f}', '-c:a', 'pcm_s16le', audio], check=True)
            words[voice] = (audio, est)
            stand_ins.add(voice)
        else:
            words[voice] = (audio, json.loads(alignment.read_text(encoding='utf-8'))['words'])
    for voice, (_, w) in words.items():
        if [norm(x['text']) for x in w] != [norm(x) for x in TEXT[voice]]:
            raise ValueError(f'{voice}: the alignment does not match {SOURCES[voice].name}')
    return words, stand_ins


def segments(words):
    """The track as pieces: ('voice', voice, first, last, src_start, src_end) or ('gap', seconds).
    A run of one voice is cut where the voice changes and where the edit opens a pause."""
    runs = []
    for voice, _, first, end in LINES:
        if runs and runs[-1][0] == voice and runs[-1][2] == first - 1:
            runs[-1][2] = end
        else:
            runs.append([voice, first, end])
    # Pauses split a run after their word.
    pieces = []
    for voice, first, end in runs:
        cuts = sorted(i for (v, i) in PAUSES if v == voice and first <= i < end)
        start = first
        for i in cuts + [end]:
            pieces.append([voice, start, i])
            start = i + 1
    out = []
    for k, (voice, first, end) in enumerate(pieces):
        w = words[voice][1]
        a = w[first]['start'] - LEAD
        b = w[end]['end'] + TRAIL
        # Never reach into the neighbouring words of the same voice.
        if first > 0:
            a = max(a, (w[first-1]['end'] + w[first]['start'])/2)
        if end + 1 < len(w):
            b = min(b, (w[end]['end'] + w[end+1]['start'])/2)
        out.append(('voice', voice, first, end, max(0, a), b))
        if k + 1 < len(pieces):
            gap = PAUSES.get((voice, end))
            if gap is None:
                gap = SWITCHES.get((voice, end), SWITCH) if pieces[k+1][0] != voice else 0
            if gap:
                out.append(('gap', gap))
    return out


def timing(words, pieces):
    # Where each word lands on the joined track: {(voice, i): (start, end)}.
    at, clock = {}, 0.0
    for p in pieces:
        if p[0] == 'gap':
            clock += p[1]
            continue
        _, voice, first, end, a, b = p
        for i in range(first, end + 1):
            w = words[voice][1][i]
            at[(voice, i)] = (round(clock + w['start'] - a, 3), round(clock + w['end'] - a, 3))
        clock += b - a
    return at, round(clock, 3)


def join(words, pieces, output, stand_ins=()):
    # One mono float track; every voice is matched to the narrator's loudness (the silent
    # stand-ins of an estimate have none to match).
    files = {v: words[v][0] for v in VOICES}
    ref = loudness(files['NARRADOR'])
    gains = {v: 0 if v in stand_ins or v == 'NARRADOR' else ref - loudness(files[v]) for v in VOICES}
    gains['AMIGO'] += FRIEND_GAIN
    order = list(VOICES)
    # The voices' own rate; the renderer resamples the mix to 48 kHz.
    rate = int(probe(files['NARRADOR'], 'stream=sample_rate'))
    fmt = f'aresample={rate},aformat=sample_fmts=flt:sample_rates={rate}:channel_layouts=mono'
    graph, labels = [], []
    for k, p in enumerate(pieces):
        if p[0] == 'gap':
            graph.append(f'aevalsrc=0:d={p[1]}:s={rate},{fmt}[p{k}]')
        else:
            _, voice, _, _, a, b = p
            graph.append(f'[{order.index(voice)}:a]atrim=start={a:.3f}:end={b:.3f},asetpts=PTS-STARTPTS,{fmt},'
                         f'volume={gains[voice]:.2f}dB,afade=t=in:d=0.01,afade=t=out:st={b - a - .012:.3f}:d=0.012[p{k}]')
        labels.append(f'[p{k}]')
    graph.append(f"{''.join(labels)}concat=n={len(labels)}:v=0:a=1[out]")
    cmd = ['ffmpeg', '-y', '-v', 'error']
    for v in order:
        cmd += ['-i', files[v]]
    subprocess.run(cmd + ['-filter_complex', ';'.join(graph), '-map', '[out]', '-c:a', 'pcm_f32le', output], check=True)
    return gains


class Edit:
    """The scenes, graphics and sound effects of one layout, on the joined track's clock."""

    def __init__(self, at, end, layout):
        self.at, self.END, self.L = at, end, layout

    def s(self, ref):
        return self.at[ref][0]

    def e(self, ref):
        return self.at[ref][1]

    def cut(self, ref, lead=.12):
        return round(self.s(ref) - lead, 2)


def phrase(start, end, y, lines, size=78, x=None):
    el = {'type': 'phrase', 'start': round(start, 2), 'end': round(end, 2), 'y': y, 'size': size, 'lines': lines}
    if x is not None:
        el['x'] = x
    return el


def line(text, at, color='white', **kw):
    return {'text': text, 'at': round(at, 2), 'color': color, **kw}


def label(text, at, **kw):
    return {'style': 'label', 'text': text, 'at': round(at, 2), **kw}


def sfx(sound, at, gain):
    return {'sound': sound, 'at': round(at, 3), 'gain': gain}


def ticking(start, end, n=14, gain=-18):
    # The counter's ticks, denser at first, as the count slows down.
    return [sfx('tique.wav', start + (end - start)*(1 - (1 - k/n)**(1/3)), gain) for k in range(1, n + 1)]


def abertura(ed, part, vote, pointer, profile, decided, winner_word, story):
    """The opening every part repeats, as the reference does (guia-de-estilo-referencia.md):
    the backpack art with the part's tag, the three fixed lines in Part 1's voice, the black
    card with the suspicion stars, the narrated pointer to the profile and the previous
    vote's real result. The other arguments are the narrator's words that open those lines,
    the word that names the winner and when the story starts. Returns scenes, graphics
    and effects."""
    s, e, cut, L = ed.s, ed.e, ed.cut, ed.L
    x = L['x']
    art = '../episodio-01/cena-01-base.png'
    winner = max(vote, key=lambda o: o[1])[0]
    black, point, result = cut(V(10)), cut(pointer), cut(decided)
    scenes = [
        ('opening', 0, dict(kind='art', asset=art, zoom=.06)),
        ('black', black, dict(kind='black')),
        ('pointer', point, dict(kind='art', asset=art, brightness=.5, zoom=.05, direction='out')),
        ('vote', result, dict(kind='black')),
    ]
    graphics = [
        {'type': 'tag', 'start': .15, 'end': story, 'text': f'PARTE {part}', 'y': L['tag_y'], 'size': 32},
        phrase(.2, s(V(4)) - .07, 700, [line('O ASSALTO', s(V(0))), line('DEU CERTO.', s(V(2)), 'yellow')], x=x),
        phrase(s(V(4)) - .07, black, 700, [
            label('SEU PARCEIRO FICOU COM', s(V(4))),
            line('R$ 10.000.000', s(V(4)) + .08, 'green', size=74,
                 count={'from': 0, 'to': 10000000, 'start': s(V(5)), 'end': e(V(9)) - .3}),
            label('EM DINHEIRO VIVO', s(V(8)))], x=x),
        phrase(black + .05, point, 560, [line('VOCÊ FICOU COM', s(V(10))), line('O ROSTO', s(V(14)), 'yellow'),
                                         line('NO JORNAL.', s(V(15)), 'yellow')], 64, x),
        {'type': 'stars', 'start': black + .05, 'end': point, 'y': 790, 'x': x, 'at': s(V(14)), 'step': .12},
        phrase(point + .05, result, 590, [line('CHEGOU AGORA?', s(pointer), 'yellow', size=64),
                                          line(f'A PARTE {part - 1} TÁ', s(profile), size=52),
                                          line('NO PERFIL', s(profile) + .45, size=52)], 72, x),
        {'type': 'pointer', 'start': round(s(profile) + .45, 2), 'end': result, 'y': 800, 'x': x, 'text': HANDLE},
        {'type': 'bars', 'start': result + .05, 'end': story, 'y': 500, 'x': x, 'width': L['bars'],
         'title': f'PARTE {part - 1} · VOCÊS VOTARAM', 'title_at': round(s(decided), 2),
         'items': [{'label': name, 'pct': pct, 'at': round(s(decided) + .1 + .15*k, 2), 'winner': name == winner}
                   for k, (name, pct) in enumerate(vote)]},
        {'type': 'stamp', 'start': round(s(winner_word) - .02, 2), 'end': story, 'text': winner, 'y': 860, 'x': x,
         'angle': -7, 'color': 'yellow', 'filled': True},
    ]
    effects = [
        *[sfx('whoosh.wav', t - WHOOSH_PEAK, -2) for t in (black, point, result)],
        *ticking(s(V(5)), e(V(9)) - .3),
        sfx('impacto.wav', s(V(16)) - .05, -5),
        *[sfx('pop.wav', s(V(14)) + .12*k, -16) for k in range(5)],
        sfx('pop.wav', s(profile) + .45, -10),
        *ticking(s(decided) + .1, s(decided) + .9, 8, -20),
        sfx('impacto.wav', s(winner_word) - .04, -5),
    ]
    return scenes, graphics, effects


# Framings inside the new illustrations, left, top, right, bottom as fractions. Equal
# width and height keep the 9:16 shape.
FRIEND02 = [0.40, 0.08, 1.0, 0.68]       # the friend at the door, by the light switch
ZINHO02 = [0.0, 0.12, 0.44, 0.56]        # Zinho in the middle of the room, arms crossed
FRIEND03 = [0.38, 0.10, 0.98, 0.70]      # the friend at the table, telling his version
EYES03 = [0.50, 0.16, 0.86, 0.52]        # his face, close
CALENDAR04 = [0.265, 0.0, 0.665, 0.40]   # the calendar on the wall of the hidden photo
FACE05 = [0.06, 0.12, 0.70, 0.76]        # Zinho on the phone
PHONE06 = [0.185, 0.234, 0.805, 0.854]   # the friend's phone on the table
CAR07 = [0.30, 0.20, 0.88, 0.78]         # the car at the gate
# The junkyard's calendar, printed on the blank sheet of scene 4 (x .31–.62, y .11–.28 of
# the illustration): name, a partly hidden number, the month and its days.
CALENDAR_PAINT = [
    {'text': 'FERRO-VELHO\nSÃO JORGE', 'box': [.335, .128, .593, .178], 'color': [150, 38, 28], 'opacity': .88, 'blur': .3},
    {'text': '(••) 3•••-••47', 'box': [.36, .183, .57, .200], 'color': [55, 42, 34], 'weight': 'Bold', 'blur': .3},
    {'text': 'OUTUBRO', 'box': [.40, .205, .53, .216], 'color': [120, 50, 40], 'weight': 'Bold', 'blur': .3},
    {'text': '1  2  3  4  5  6  7\n8  9  10  11  12  13  14\n15  16  17  18  19  20  21\n22  23  24  25  26  27  28',
     'box': [.335, .220, .593, .268], 'color': [95, 82, 70], 'weight': 'Medium', 'opacity': .75, 'blur': .3},
]
# The friend's phone in scene 6: the corners of its screen, a little outside the lit
# area so the rounded corners are covered. The screen is off until the phone buzzes,
# then it lights up on the lock screen with the message's notification.
_CORNERS = [(.4687, .4199), (.6939, .4396), (.5898, .6746), (.2901, .6417)]
_MIDDLE = (sum(x for x, _ in _CORNERS)/4, sum(y for _, y in _CORNERS)/4)
SCREEN06 = [[round(_MIDDLE[0] + (x - _MIDDLE[0])*1.05, 4), round(_MIDDLE[1] + (y - _MIDDLE[1])*1.05, 4)] for x, y in _CORNERS]
SCREEN_OFF = {'quad': SCREEN06, 'state': 'off'}
# The same phone in scene 9, lying sideways on the table, its top towards the left.
_CORNERS9 = [(.4481, .7287), (.5367, .7191), (.6808, .7566), (.5739, .7669)]
_MIDDLE9 = (sum(x for x, _ in _CORNERS9)/4, sum(y for _, y in _CORNERS9)/4)
SCREEN09 = [[round(_MIDDLE9[0] + (x - _MIDDLE9[0])*1.05, 4), round(_MIDDLE9[1] + (y - _MIDDLE9[1])*1.05, 4)]
            for x, y in _CORNERS9]
FRIEND09 = [0.015, 0.125, 0.565, 0.675]  # the friend's face in scene 9, looking down, silent
SCREEN_MESSAGE = {'quad': SCREEN06, 'state': 'lock', 'date': 'terça-feira, 27 de outubro', 'time': '23:47',
                  'app': 'MENSAGENS', 'sender': 'Cobrança', 'message': 'Já tá com ele?', 'when': 'agora'}


def build(ed):
    s, e, cut, L = ed.s, ed.e, ed.cut, ed.L
    END, x, top = ed.END, L['x'], L['card_top']
    story = cut(N('Você destranca'))
    opening, og, oe = abertura(ed, PART, VOTE, N('Chegou agora?'), N('A parte um'), N('Vocês decidiram:'),
                               N('decidiram: abrir.', 1), story)
    RINGS = [e(N('seu celular.', 1)) + .1, e(N('três vezes.', 1)) + .2, e(N('três vezes.', 1)) + 1.45]
    PICKUP = e(N('três vezes.', 1)) + 2.5
    plan = opening + [
        ('door', story, dict(kind='art', asset='cena-01-porta-aberta.png', zoom=.05)),
        ('enters', cut(N('Ele entra sem')), dict(kind='art', asset='cena-02-luz-apagada.png', zoom=.04)),
        ('dark', round(s(N('apaga a luz')) + .25, 2), dict(kind='art', asset='cena-02-luz-apagada.png', zoom=.03,
                                                             brightness=.55, crop=FRIEND02)),
        # He has no name in this story yet: the audience gives him one, right after he first speaks.
        ('sold', cut(N('Ele vendeu o')), dict(kind='art', asset='cena-08-retrato-amigo.png', zoom=.05)),
        ('name', cut(N('Comenta um nome.')), dict(kind='art', asset='cena-08-retrato-amigo.png', zoom=.03,
                                                  direction='out', brightness=.5)),
        ('question', cut(N('Você não oferece')), dict(kind='art', asset='cena-03-versao.png', zoom=.04)),
        ('eighty', cut(A('Oitenta mil.')), dict(kind='art', asset='cena-03-versao.png', crop=FRIEND03, zoom=.08)),
        ('whom', cut(N('Para quem?')), dict(kind='art', asset='cena-02-luz-apagada.png', crop=ZINHO02, zoom=.05,
                                            brightness=.6)),
        ('backers', cut(A('Pra quem bancou')), dict(kind='art', asset='cena-03-versao.png', crop=FRIEND03, zoom=.05)),
        # His version: him talking fast, the whole room while the list builds, then Zinho
        # as the blame lands on him.
        ('version', cut(N('Ele fala rápido')), dict(kind='art', asset='cena-03-versao.png', crop=FRIEND03, zoom=.04)),
        ('debt', cut(N('Perdeu um dinheiro')), dict(kind='art', asset='cena-03-versao.png', zoom=.05, direction='out')),
        ('blame', cut(N('Se desse errado,')), dict(kind='art', asset='cena-02-luz-apagada.png', crop=ZINHO02, zoom=.06,
                                                   brightness=.6)),
        ('promise', cut(A('Eles juraram')), dict(kind='art', asset='cena-03-versao.png', crop=FRIEND03, zoom=.06)),
        ('news', cut(N('Mas foi ele')), dict(kind='tv', asset='cena-03-versao.png', card_top=top, card_dx=L['tv_dx'],
                                             card_scale=L['tv_scale'])),
        ('mother', cut(A('Eu não tive')), dict(kind='art', asset='cena-03-versao.png', crop=EYES03, zoom=.08)),
        ('memory', cut(N('Você conhece essa')), dict(kind='art', asset='cena-02-luz-apagada.png', crop=ZINHO02,
                                                     zoom=.04, brightness=.6)),
        ('proof', cut(N('Você pede uma')), dict(kind='art', asset='cena-03-versao.png', zoom=.04)),
        ('shows', cut(N('Ele mostra o')), dict(kind='photo', asset='cena-03-versao.png', photo='cena-04-foto-divisao.png',
                                                paint=CALENDAR_PAINT, card_top=top, card_dx=L['card_dx'])),
        ('split', cut(N('A mesa, o')), dict(kind='art', asset='cena-04-foto-divisao.png', zoom=.06, paint=CALENDAR_PAINT)),
        ('calendar', cut(N('Você amplia a')), dict(kind='art', asset='cena-04-foto-divisao.png', crop=CALENDAR04,
                                                   zoom=.12, paint=CALENDAR_PAINT)),
        ('dial', cut(N('Você liga do')), dict(kind='art', asset='cena-05-ligacao.png', zoom=.04)),
        ('calling', cut(N('Toca três vezes.')), dict(kind='call', asset='cena-05-ligacao.png', status='calling',
                                                     number='(••) 3•••-••47', card_top=top, card_dx=L['card_dx'])),
        ('answered', round(PICKUP, 2), dict(kind='call', asset='cena-05-ligacao.png', status='answered', clock='00:01',
                                            number='(••) 3•••-••47', card_top=top, card_dx=L['card_dx'])),
        ('ended', cut(N('Você desliga sem')), dict(kind='call', asset='cena-05-ligacao.png', status='ended',
                                                   number='(••) 3•••-••47', card_top=top, card_dx=L['card_dx'])),
        ('exists', cut(N('O lugar existe.')), dict(kind='art', asset='cena-05-ligacao.png', crop=FACE05, zoom=.05)),
        # Locked and dark while the narrator speaks; it lights up as it buzzes.
        ('buzz', cut(N('Então o celular')), dict(kind='art', asset='cena-06-celular-mesa.png', zoom=.05, brightness=.8,
                                                  screen=SCREEN_OFF)),
        ('lit', round(e(N('cima da mesa.', 2)) + .05, 2), dict(kind='art', asset='cena-06-celular-mesa.png', zoom=.04,
                                                               screen=SCREEN_MESSAGE)),
        # The message lights up on his phone's screen; it stays there, unanswered.
        ('message', cut(N('Uma mensagem de')), dict(kind='art', asset='cena-06-celular-mesa.png', crop=PHONE06, zoom=.06,
                                                    screen=SCREEN_MESSAGE)),
        # Zinho asks what that is, pointing at the phone; the friend looks down and says nothing.
        ('ask', cut(N('Ele não responde')), dict(kind='art', asset='cena-09-pergunta.png', zoom=.05,
                                                 screen=dict(SCREEN_MESSAGE, quad=SCREEN09))),
        ('silent', cut(N('Nem a você.')), dict(kind='art', asset='cena-09-pergunta.png', crop=FRIEND09, zoom=.06)),
        ('car', cut(N('Lá fora, um')), dict(kind='art', asset='cena-07-carro.png', zoom=.05)),
        ('lights-off', cut(N('De farol apagado.')), dict(kind='art', asset='cena-07-carro.png', crop=CAR07, zoom=.08,
                                                        brightness=.8)),
        # The request to comment, FUGIR or FICAR, over the car that waits at the gate.
        ('choice', cut(P('E agora:')), dict(kind='art', asset='cena-07-carro.png', zoom=.03, direction='out',
                                           brightness=.42)),
    ]
    AT = {name: t for name, t, _ in plan}
    scenes = [{'start': t, 'end': plan[k+1][1] if k + 1 < len(plan) else END, **fields}
              for k, (_, t, fields) in enumerate(plan)]
    for sc in scenes:
        if sc.get('crop') is None:
            sc.pop('crop', None)
        if sc.get('paint') is None:
            sc.pop('paint', None)
        for key in ('card_dx', 'card_scale'):
            if sc.get(key) in (0, 1):
                sc.pop(key)
    lists = [{'at': round(s(N('Perdeu um dinheiro')), 2), 'left': 'A DÍVIDA', 'right': 'R$ 80 MIL'},
             {'at': round(s(N('alguém de fora,')), 2), 'left': 'A SAÍDA', 'right': 'ALGUÉM DE FORA'},
             {'at': round(s(N('essa pessoa.')), 2), 'left': 'A CULPA', 'right': 'VOCÊ'}]
    graphics = og + [
        {'type': 'hud', 'start': story, 'end': AT['choice'], 'label': 'A SUA PARTE', 'dy': L['hud_dy'],
         'values': [{'at': story, 'text': 'R$ 0', 'color': 'red'}],
         'stars': [{'at': story, 'count': 5, 'step': 0}]},
        {'type': 'tag', 'start': AT['question'], 'end': AT['proof'], 'text': 'PISTA 1 · A VERSÃO DELE', 'y': L['tag_y']},
        {'type': 'tag', 'start': AT['proof'], 'end': AT['buzz'], 'text': 'PISTA 2 · A FOTO DA DIVISÃO', 'y': L['tag_y']},
        {'type': 'tag', 'start': AT['buzz'], 'end': AT['car'], 'text': 'PISTA 3 · A MENSAGEM', 'y': L['tag_y']},
        # Red alarm while the message sits on the screen and while the car waits outside.
        {'type': 'vignette', 'start': AT['message'], 'end': AT['car'], 'color': 'alert', 'strength': .8},
        {'type': 'vignette', 'start': AT['lights-off'], 'end': AT['choice'], 'color': 'alert', 'strength': .9},
        phrase(s(A('Eles tão te')) - .05, AT['sold'], 900, [line('“ELES TÃO', s(A('Eles tão te'))),
                                                               line('TE PROCURANDO.”', s(A('te procurando.')), 'yellow')],
               60, x),
        phrase(s(N('quanto ele devia.')) - .05, AT['eighty'], 900, [line('QUANTO', s(N('quanto ele devia.'))),
                                                                    line('ELE DEVIA?', s(N('ele devia.')), 'yellow')],
               70, x),
        phrase(AT['eighty'], AT['whom'], 880, [
            label('A DÍVIDA', s(A('Oitenta mil.'))),
            line('R$ 80.000', s(A('Oitenta mil.')) + .05, 'red', size=96, shake=True,
                 count={'from': 0, 'to': 80000, 'start': s(A('Oitenta mil.')), 'end': e(A('Oitenta mil.', 1))})], 96, x),
        phrase(s(A('Pra quem bancou')) - .05, AT['version'], 900, [line('PRA QUEM BANCOU', s(A('Pra quem bancou'))),
                                                                   line('O ASSALTO.', s(A('o assalto.')), 'yellow')], 58, x),
        {'type': 'list', 'start': round(s(N('Perdeu um dinheiro')) - .05, 2), 'end': AT['promise'], 'y': 560,
         'items': lists, 'x': x},
        phrase(s(A('Eles juraram')) - .05, AT['news'], 900, [line('“NINGUÉM IA VER', s(A('ninguém ia ver'))),
                                                             line('O SEU ROSTO.”', s(A('o seu rosto.')), 'yellow')], 60, x),
        {'type': 'stamp', 'start': round(s(N('entregou a sua')) - .02, 2), 'end': AT['mother'], 'text': 'FOI ELE',
         'y': top + 380, 'x': x + 110, 'angle': -8},
        phrase(s(A('Eles sabiam')) - .05, AT['memory'], 900, [line('“ELES SABIAM ONDE', s(A('Eles sabiam'))),
                                                              line('A MINHA MÃE MORA.”', s(A('a minha mãe')), 'yellow')],
               52, x),
        phrase(s(N('Palavra, ele')) - .05, AT['shows'], 900, [line('PALAVRA,', s(N('Palavra, ele'))),
                                                              line('ELE JÁ GASTOU.', s(N('ele já gastou.')), 'yellow')],
               66, x),
        phrase(s(N('noite da divisão.')) - .05, AT['split'], top + 590, [line('A NOITE', s(N('noite da divisão.'))),
                                                                        line('DA DIVISÃO.', s(N('da divisão.')), 'yellow')],
               56, x),
        phrase(s(N('"Ferro-Velho São Jorge."')) - .05, AT['ended'], top + 465, [
            line('“FERRO-VELHO', s(N('"Ferro-Velho São Jorge."'))),
            line('SÃO JORGE.”', s(N('São Jorge."')), 'yellow')], 50, x),
        # "O lugar existe." gives way to the stamp on “verdade.”, in the same place, clear of his face.
        phrase(AT['exists'], s(N('verdade.')) - .04, 900, [line('O LUGAR', s(N('O lugar existe.'))),
                                                           line('EXISTE.', s(N('existe.')), 'yellow')], 76, x),
        {'type': 'stamp', 'start': round(s(N('verdade.')) - .02, 2), 'end': AT['buzz'], 'text': 'VERDADE', 'y': 900,
         'x': x, 'angle': -6, 'color': 'green'},
        # Zinho's question, on screen only, since he never speaks aloud in the series.
        phrase(AT['ask'] + .05, AT['silent'], 620, [line('“O QUE É ISSO?”', AT['ask'] + .1, shake=True)], 70, x),
        phrase(s(N('Nem a você.')) - .05, AT['car'], 900, [line('NEM A VOCÊ.', s(N('Nem a você.')), 'yellow')], 72, x),
        phrase(AT['lights-off'], AT['choice'], 900, [line('DE FAROL', s(N('De farol apagado.'))),
                                                   line('APAGADO.', s(N('apagado.')), 'red', shake=True)], 80, x),
        phrase(AT['sold'], AT['name'], 820, [line('ELE VENDEU', s(N('Ele vendeu o'))),
                                             line('O SEU NOME.', s(N('o seu nome.')), 'yellow'),
                                             line('AGORA VOCÊ', s(N('Agora você escolhe')), size=58),
                                             line('ESCOLHE O DELE.', s(N('escolhe o dele.')), 'yellow', size=58)], 72, x),
        # The free vote for the friend's name, below his face: no options, only the empty
        # comment box, and the rule in the box of the next part.
        phrase(AT['name'], AT['question'], 660, [line('QUAL É O', s(N('Comenta um nome.'))),
                                                 line('NOME DELE?', s(N('Comenta um nome.')) + .15, 'yellow')], 70, x),
        {'type': 'input', 'start': round(s(N('um nome.')), 2), 'end': AT['question'], 'y': 820, 'x': x,
         'placeholder': 'Comenta o nome dele…', 'width': L['input']},
        {'type': 'box', 'start': round(s(N('O mais curtido')), 2), 'end': AT['question'], 'y': 950, 'x': x,
         'title': f'PARTE {PART + 1}', 'sub': 'o mais curtido vira o nome dele'},
        # The closing vote, with its two buttons, as Part 1 asked ABRIR or NÃO ABRIR.
        phrase(AT['choice'], END + .5, 420, [line('FUGIR OU', s(P('fugir ou ficar?'))),
                                             line('FICAR?', s(P('ficar? Comenta')), 'yellow')], 88, x),
        {'type': 'buttons', 'start': round(s(P('Comenta uma palavra')) - .05, 2), 'end': END + .5, 'y': 660, 'x': x,
         'prompt': 'COMENTA UMA PALAVRA', 'prompt_at': round(s(P('Comenta uma palavra')), 2),
         'items': [{'text': 'FUGIR', 'at': round(s(P('uma palavra só.', 1)), 2), 'style': 'yellow'},
                   {'text': 'FICAR', 'at': round(s(P('uma palavra só.', 2)), 2), 'style': 'white'}]},
        {'type': 'box', 'start': round(s(P('O que a maioria')), 2), 'end': END + .5, 'y': 830, 'x': x,
         'title': f'PARTE {PART + 1}', 'sub': 'a maioria decide o próximo passo'},
    ]
    effects = oe + [
        sfx('impacto-suave.wav', AT['ask'] + .05, -9),
        *[sfx('whoosh.wav', AT[n] - WHOOSH_PEAK, -2) for n in ('door', 'sold', 'question', 'shows', 'dial', 'buzz', 'car',
                                                               'choice')],
        sfx('tranca.wav', e(N('a porta.', 1)) + .05, -6),
        sfx('porta-abre.wav', e(N('a porta.', 1)) + .3, -8),
        sfx('passos.wav', s(N('Ele entra sem')) + .1, -12),
        sfx('porta-fecha.wav', s(N('passa a chave')) - .1, -10),
        sfx('tranca.wav', s(N('chave por dentro')) + .1, -8),
        sfx('interruptor.wav', s(N('apaga a luz')) + .22, -8),
        *ticking(s(A('Oitenta mil.')), e(A('Oitenta mil.', 1)), 8, -18),
        sfx('impacto-suave.wav', e(A('Oitenta mil.', 1)) - .05, -8),
        *[sfx('pop.wav', item['at'], -10) for item in lists],
        sfx('impacto.wav', s(N('entregou a sua')) - .04, -5),
        sfx('impacto-suave.wav', s(N('Ele mostra o')), -12),
        *[sfx('chamada-longa.wav', t, -14) for t in RINGS],
        sfx('atende.wav', PICKUP - .05, -10),
        sfx('desliga.wav', e(N('dizer nada.', 1)) + .05, -10),
        sfx('impacto-suave.wav', s(N('verdade.')) - .04, -8),
        sfx('vibracao.wav', e(N('cima da mesa.', 2)) + .05, -6),
        sfx('notificacao.wav', s(N('Uma mensagem de')) - .05, -8),
        sfx('impacto.wav', s(N('"Já tá com')) - .05, -6),
        sfx('carro.wav', e(N('ao portão.', 1)) - 1.6, -6),
        sfx('impacto.wav', AT['lights-off'] - .02, -5),
        sfx('impacto-suave.wav', s(N('Ele vendeu o')) - .04, -8),
        *[sfx('pop.wav', t, -10) for t in (s(N('Comenta um nome.')), s(N('um nome.')), s(N('O mais curtido')),
                                           s(P('uma palavra só.', 1)), s(P('uma palavra só.', 2)), s(P('O que a maioria')))],
    ]
    # The vertical version's narrower column takes the phrases a little smaller.
    k = L['width']/INSTAGRAM['width']
    for g in graphics if k != 1 else []:
        if g['type'] == 'phrase':
            g['size'] = int(g['size']*k)
            for ln in g['lines']:
                if 'size' in ln:
                    ln['size'] = int(ln['size']*k)
    return scenes, graphics, effects


def too_wide(graphics, limit):
    # Phrase lines must fit the layout's width.
    wide = []
    for g in graphics:
        for ln in g['lines'] if g['type'] == 'phrase' else []:
            size = ln.get('size', 22 if ln.get('style') == 'label' else g['size'])
            if ln.get('style') == 'label':
                f = graficos.font(size, 'SemiBold')
                width = sum(f.getlength(ch) for ch in ln['text']) + round(size*.22)*(len(ln['text'])-1)
            else:
                width = graficos.font(size, ln.get('weight', 'Bold')).getlength(ln['text'])
            if width > limit:
                wide.append((ln['text'], size, round(width)))
    return wide


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--estimar', type=Path, metavar='DIR', help='build from estimated timings into DIR')
    args = parser.parse_args()
    out = args.estimar.resolve() if args.estimar else HERE
    out.mkdir(parents=True, exist_ok=True)
    words, stand_ins = load_words(out if args.estimar else None)
    pieces = segments(words)
    at, length = timing(words, pieces)
    end = round(length + TAIL, 2)
    audio = out / AUDIO.name if args.estimar else AUDIO
    gains = join(words, pieces, audio, stand_ins)
    for layout in (INSTAGRAM, VERTICAL):
        scenes, graphics, effects = build(Edit(at, end, layout))
        wide = too_wide(graphics, layout['width'])
        if wide:
            raise ValueError(f'Lines wider than the {layout["name"]} layout allows: {wide}')
        graficos.check(graphics)
        timeline = {'timing_status': 'estimated' if args.estimar else 'aligned_to_voice',
                    'style': 'guia-de-estilo-referencia.md', 'script': SCRIPT.name,
                    'alignment': [str(VOICES[v][1].relative_to(EPISODE.parent)) for v in VOICES],
                    'audio': str(audio) if args.estimar else audio.name, 'tail': TAIL,
                    'scenes': scenes, 'graphics': graphics, 'sfx': effects, 'captions': []}
        if args.estimar:
            # Out of place, the timeline names its assets and effects by absolute path.
            for sc in scenes:
                if 'asset' in sc:
                    sc['asset'] = str((EPISODE / sc['asset']).resolve())
                if 'photo' in sc:
                    sc['photo'] = str((EPISODE / sc['photo']).resolve())
            timeline['effects'] = [str(HERE / 'efeitos')]
        (out / layout['name']).write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f"{layout['name']}: {len(scenes)} scenes, {len(graphics)} graphics, {len(effects)} sound effects, ends at {end}s")
    print(f'{audio.name}: {length}s of voice; gains ' + ', '.join(f'{v} {g:+.1f} dB' for v, g in gains.items()))


if __name__ == '__main__':
    main()
