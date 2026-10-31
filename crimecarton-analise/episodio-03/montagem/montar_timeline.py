#!/usr/bin/env python3
"""Build Part 3's narration track and its two timelines from the word alignments.

The track joins, in the order of roteiro-ep03.txt: the series' opening, cut from Part 1's
narration (its first 17 words, the same art and audio in every part); the narrator's
lines from narracao-ep03-narrador.wav, closing request included; Renato's from
narracao-ep03-renato.wav, in his own voice; and the pauses the edit opens for sounds, such
as the car door and the gate. Each line is found in its recording by its words.
Every cut, graphic and effect is anchored to a word of the script, so the edit follows
the voices again if they are re-aligned. The allies' @ come in the images compor_cenas.py
makes, in arte/, and in the credits at the end when there are any.

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

SCRIPT = EPISODE / 'roteiro-ep03.txt'
# The opening comes matched to this narrator by igualar_vozes.py.
VOICES = {'VINHETA': (HERE / 'vozes' / 'vinheta.wav', TOOLS / 'alinhamento-narracao.json'),
          'NARRADOR': (EPISODE / 'narracao-ep03-narrador.wav', HERE / 'alinhamento-narrador.json'),
          # Renato in the voice of his message in Part 1, made by voz_renato.py.
          'RENATO': (HERE / 'vozes' / 'renato.wav', HERE / 'alinhamento-renato.json')}
AUDIO = EPISODE / 'narracao-ep03.wav'
PART, VOTE = 3, [('FUGIR', 77), ('FICAR', 23)]   # Part 2's vote: 10 FUGIR, 3 FICAR at 9h40 of 30/10
NAME = 'RENATO'                                  # the friend's name, the most liked comment
HANDLE = '@golpecartoon'
ALLIES = HERE / 'aliados-parte-03.json'
# Without allies the video ends 2 s after the voice; with them, the credits take 3.5 s.
TAIL = 3.5 if ALLIES.exists() and json.loads(ALLIES.read_text(encoding='utf-8')) else 2.0
# Renato talks beside Zinho, as loud as the narrator.
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
SOURCES = {'VINHETA': EPISODE.parent / 'narracao-ep01-zinho.txt', 'NARRADOR': EPISODE / 'narracao-ep03-narrador.txt',
           'RENATO': EPISODE / 'narracao-ep03-renato.txt'}
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


def R(phrase, k=0):
    return 'RENATO', find('RENATO', phrase) + k


def V(i):
    return 'VINHETA', i


# Silence the edit opens after a word, in seconds, for the sounds of the story. Phrases
# point at their first word; the offset picks the word the pause follows. The pause
# replaces the voice's own silence there, except for LEAD and TRAIL around the cut.
PAUSES = {
    N('decidiram: fugir.', 1): .3,          # the vote's stamp lands
    N('a ele: Renato.', 2): .6,             # the name's stamp lands
    N('carro abre devagar.', 2): .5,        # the car door opens outside
    N('sacode o portão.', 2): .7,           # the gate rattles
    N('de latir.', 1): .4,
    N('"Cadê vocês?"', 1): .7,              # the message lights up his phone
    N('sobe a conversa.', 2): .5,
    N('casa dele."', 1): .9,                # the message he sent before knocking sinks in
    N('fica com você.', 2): .45,            # the chip drops through the grate
    N('o dele.', 1): .5,                    # his face on the news
    N('são procurados.', 1): .4,
    N('pega o celular.', 2): .45,
    N('contigo, Zinho."', 1): .6,           # Zinho's phone keeps buzzing
    N('de uma porta.', 2): .3,
    N('de ouro.', 1): .5,
    N('o dinheiro.', 1): .4,
    N('a mão.', 1): .6,
    N('até amanhecer.', 1): .3,
    N('onde fica.', 1): .5,
}
# Silences at changes of voice other than SWITCH: a breath after the opening.
SWITCHES = {V(16): .35}


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
    gains['RENATO'] += FRIEND_GAIN
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
                                          line(f'A PARTE {part - 1} TÁ' if part == 2 else
                                               f"AS PARTES {', '.join(str(n) for n in range(1, part - 1))} E {part - 1}",
                                               s(profile), size=52),
                                          line('NO PERFIL' if part == 2 else 'TÃO NO PERFIL', s(profile) + .45, size=52)],
               72, x),
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




# Framings inside the illustrations, left, top, right, bottom as fractions. Equal width and
# height keep the 9:16 shape.
GATE01 = [0.26, 0.25, 0.86, 0.85]        # the car and the gate, from the window
RENATO02 = [0.40, 0.12, 0.95, 0.67]      # Renato at the back door
TORCH02 = [0.0, 0.12, 0.55, 0.67]        # the torch's beam in the doorway, Zinho looking back
HANDS03 = [0.335, 0.292, 0.735, 0.692]   # the two hands over the wall
RENATO04 = [0.426, 0.179, 0.786, 0.539]  # Renato's face, running
DRAIN05 = [0.36, 0.52, 0.80, 0.96]       # the chip falling through the grate
MAN06 = [0.60, 0.38, 1.0, 0.78]          # the man at the counter with his phone
FACES09 = [0.08, 0.10, 0.58, 0.60]       # the two of them pressed into the doorway
RING10 = [0.25, 0.40, 0.65, 0.80]        # the ring on the hand at the car window
FACE11 = [0.15, 0.12, 0.75, 0.72]        # Renato looking away
WINDOW13 = [0.0, 0.15, 0.50, 0.65]       # the mother's lit window
CAR13 = [0.60, 0.30, 1.0, 0.70]          # the car waiting down her street
RING_PHOTO = [0.513, 0.342, 0.953, 0.782]  # the ring in Part 2's photo of the division
FIRST_MSG = [0.20, 0.10, 0.80, 0.70]     # Renato's chat: the message he sent at 23:31, close
TV_FACES = [0.02, 0.19, 0.62, 0.79]      # the news: the two faces, Zinho's and, for the first time, Renato's
# Renato's phone in scene 5: the corners of its screen, a little outside the lit area, and
# the message from "Cobrança" on the lock screen, minutes after Part 2's 23:47.
_CORNERS5 = [(.2380, .2362), (.4400, .2500), (.4421, .5161), (.2115, .5048)]
_MIDDLE5 = (sum(x for x, _ in _CORNERS5)/4, sum(y for _, y in _CORNERS5)/4)
SCREEN05 = [[round(_MIDDLE5[0] + (x - _MIDDLE5[0])*1.05, 4), round(_MIDDLE5[1] + (y - _MIDDLE5[1])*1.05, 4)] for x, y in _CORNERS5]
COBRANCA = {'quad': SCREEN05, 'state': 'lock', 'date': 'quarta-feira, 28 de outubro', 'time': '00:03',
            'app': 'MENSAGENS', 'sender': 'Cobrança', 'message': 'Cadê vocês?', 'when': 'agora'}


def build(ed):
    s, e, cut, L = ed.s, ed.e, ed.cut, ed.L
    END, x = ed.END, L['x']
    story = cut(N('Agora você foge'))
    # The opening's vote gives way to the name the audience chose, then the story starts.
    opening, og, oe = abertura(ed, PART, VOTE, N('Chegou agora?'), N('As partes um'), N('Vocês decidiram:'),
                               N('decidiram: fugir.', 1), cut(N('E deram um')))
    p2 = '../episodio-02/'
    allies = json.loads(ALLIES.read_text(encoding='utf-8')) if ALLIES.exists() else []
    VOICE_END = ed.at[('NARRADOR', len(TEXT['NARRADOR']) - 1)][1]
    plan = opening + [
        # The name the audience gave him, over his portrait from Part 2.
        ('name', cut(N('E deram um')), dict(kind='art', asset=p2 + 'cena-08-retrato-amigo.png', zoom=.05)),
        ('hook', story, dict(kind='art', asset='cena-02-cozinha.png', zoom=.05)),
        ('car', cut(N('Lá fora, a')), dict(kind='art', asset='cena-01-porta-do-carro.png', zoom=.05)),
        ('back', cut(R('Pelos fundos.')), dict(kind='art', asset='cena-02-cozinha.png', crop=RENATO02, zoom=.06)),
        ('knows', cut(N('Ele conhece a')), dict(kind='art', asset='cena-02-cozinha.png', crop=TORCH02, zoom=.05)),
        ('wall', cut(N('A cozinha, o')), dict(kind='art', asset='cena-03-muro-quintal.png', zoom=.05)),
        ('gate', cut(N('Atrás de vocês,')), dict(kind='art', asset='cena-01-porta-do-carro.png', crop=GATE01, zoom=.08,
                                                  brightness=.75)),
        ('alley', cut(N('Do outro lado')), dict(kind='art', asset='montagem/arte/beco-pichado.png', zoom=.06)),
        ('debt', cut(N('Então o celular')), dict(kind='art', asset='cena-05-chip.png', zoom=.05, screen=COBRANCA)),
        # Zinho takes the phone and scrolls up: the message Renato sent before he knocked.
        ('chat', cut(N('Você arranca o')), dict(kind='art', asset='montagem/arte/conversa.png', zoom=.04)),
        ('sent', cut(N('Onze e meia')), dict(kind='art', asset='montagem/arte/conversa.png', crop=FIRST_MSG, zoom=.08)),
        ('excuse', cut(R('Eu mandei antes')), dict(kind='art', asset='cena-11-renato.png', crop=FACE11, zoom=.06)),
        ('doubt', cut(N('Você não sabe')), dict(kind='art', asset='cena-05-chip.png', zoom=.04, screen=COBRANCA)),
        ('chip', cut(N('O chip vai')), dict(kind='art', asset='cena-05-chip.png', crop=DRAIN05, zoom=.08)),
        ('bar', cut(N('No bar da')), dict(kind='art', asset='montagem/arte/bar-plantao.png', zoom=.05)),
        ('tv', cut(N('O seu rosto.')), dict(kind='art', asset='montagem/arte/tv-bar-plantao.png', zoom=.06)),
        ('wanted', cut(N('Agora os dois')), dict(kind='art', asset='montagem/arte/tv-bar-plantao.png', crop=TV_FACES, zoom=.06)),
        ('comments', cut(N('Embaixo, os comentários')), dict(kind='art', asset='montagem/arte/tv-bar-plantao.png', zoom=.03,
                                                             direction='out')),
        ('man', cut(N('No balcão, um')), dict(kind='art', asset='montagem/arte/bar-plantao.png', crop=MAN06, zoom=.08)),
        ('phone', cut(N('Na rua, é')), dict(kind='art', asset='montagem/arte/celular-notificacoes.png', zoom=.07)),
        ('avenue', cut(N('Na avenida, o')), dict(kind='art', asset='cena-09-porta-escura.png', zoom=.04)),
        ('still', cut(R('Não se mexe.')), dict(kind='art', asset='cena-09-porta-escura.png', crop=FACES09, zoom=.06)),
        ('window', cut(N('Na janela do')), dict(kind='art', asset='cena-10-anel.png', zoom=.05)),
        ('ring', cut(N('No dedo, um')), dict(kind='art', asset='cena-10-anel.png', crop=RING10, zoom=.1)),
        ('photo', cut(N('É o anel')), dict(kind='art', asset=p2 + 'cena-04-foto-divisao.png', zoom=.05)),
        ('photo-ring', cut(N('A mão que')), dict(kind='art', asset=p2 + 'cena-04-foto-divisao.png', crop=RING_PHOTO,
                                                 zoom=.12)),
        ('him', cut(R('É ele.')), dict(kind='art', asset='cena-11-renato.png', crop=FACE11, zoom=.08)),
        ('one-of-them', cut(N('Pela primeira vez, você')), dict(kind='art', asset='cena-10-anel.png', crop=RING10, zoom=.05,
                                                                direction='out', brightness=.8)),
        ('gone', cut(N('O carro some')), dict(kind='art', asset='cena-09-porta-escura.png', zoom=.04, direction='out',
                                              brightness=.7)),
        ('places', cut(R('Tem dois.')), dict(kind='art', asset='cena-11-renato.png', zoom=.03)),
        ('junkyard', cut(R('O ferro-velho da')), dict(kind='art', asset='cena-12-ferro-velho.png', zoom=.05)),
        ('mother', cut(R('Ou a casa')), dict(kind='art', asset='cena-13-casa-mae.png', zoom=.05)),
        ('theirs', cut(N('O ferro-velho é')), dict(kind='art', asset='cena-12-ferro-velho.png', zoom=.04, direction='out',
                                                   brightness=.8)),
        ('they-know', cut(N('A casa da mãe,')), dict(kind='art', asset='cena-13-casa-mae.png', crop=CAR13, zoom=.08,
                                                     brightness=.85)),
        # The vote: the two places side by side, dark under the buttons.
        ('choice', cut(N('Ferro-velho ou mãe?')), dict(kind='art', asset='montagem/arte/escolha.png', zoom=.03,
                                                       direction='out', brightness=.45)),
    ]
    if allies:
        plan.append(('credits', round(VOICE_END + .6, 2), dict(kind='art', asset='montagem/arte/creditos.png', zoom=.03)))
    plan.sort(key=lambda item: item[1])
    AT = {name: t for name, t, _ in plan}
    scenes = [{'start': t, 'end': plan[k+1][1] if k + 1 < len(plan) else END, **fields}
              for k, (_, t, fields) in enumerate(plan)]
    for sc in scenes:
        for key in ('card_dx', 'card_scale'):
            if sc.get(key) in (0, 1):
                sc.pop(key)
    vote_end = AT.get('credits', END + .5)
    graphics = og + [
        {'type': 'hud', 'start': story, 'end': AT['choice'], 'label': 'A SUA PARTE', 'dy': L['hud_dy'],
         'values': [{'at': story, 'text': 'R$ 0', 'color': 'red'}],
         'stars': [{'at': story, 'count': 5, 'step': 0}]},
        {'type': 'tag', 'start': story, 'end': AT['debt'], 'text': 'FUGA 1 · OS FUNDOS', 'y': L['tag_y']},
        {'type': 'tag', 'start': AT['debt'], 'end': AT['bar'], 'text': 'PISTA · A CONVERSA', 'y': L['tag_y']},
        {'type': 'tag', 'start': AT['bar'], 'end': AT['avenue'], 'text': 'FUGA 2 · O BAR', 'y': L['tag_y']},
        {'type': 'tag', 'start': AT['avenue'], 'end': AT['window'], 'text': 'FUGA 3 · A AVENIDA', 'y': L['tag_y']},
        {'type': 'tag', 'start': AT['window'], 'end': AT['choice'], 'text': 'PISTA · O ANEL', 'y': L['tag_y']},
        # The name, stamped over his face.
        phrase(AT['name'] + .05, story, 760, [line('E O NOME DELE', s(N('E deram um')))], 64, x),
        {'type': 'stamp', 'start': round(s(N('ele: Renato.', 1)) - .02, 2), 'end': story, 'text': NAME, 'y': 900, 'x': x,
         'angle': -7, 'color': 'yellow', 'filled': True},
        # Red alarm on the old message, while the car goes by and at the mother's street.
        {'type': 'vignette', 'start': AT['sent'], 'end': AT['doubt'], 'color': 'alert', 'strength': .8},
        {'type': 'vignette', 'start': AT['avenue'], 'end': AT['photo'], 'color': 'alert', 'strength': .85},
        {'type': 'vignette', 'start': AT['they-know'], 'end': AT['choice'], 'color': 'alert', 'strength': .8},
        phrase(s(N('ao lado do')) - .05, AT['car'], 900, [line('AO LADO DE QUEM', s(N('ao lado do'))),
                                                         line('VENDEU O SEU NOME.', s(N('vendeu o seu')), 'yellow')], 52, x),
        phrase(AT['back'] + .05, AT['knows'], 900, [line('“PELOS FUNDOS.', s(R('Pelos fundos.'))),
                                                    line('AGORA.”', s(R('Agora.')), 'yellow', shake=True)], 66, x),
        phrase(s(N('melhor do que')) - .05, AT['wall'], 900, [line('MELHOR DO QUE', s(N('melhor do que'))),
                                                             line('DEVERIA.', s(N('deveria.')), 'yellow')], 62, x),
        phrase(s(N('alguém sacode')) - .05, AT['alley'], 900, [line('ALGUÉM SACODE', s(N('alguém sacode'))),
                                                               line('O PORTÃO.', s(N('o portão.')), 'red', shake=True)], 64, x),
        phrase(s(N('"Cadê vocês?"')) - .05, AT['chat'], 1000, [line('“CADÊ VOCÊS?”', s(N('"Cadê vocês?"')), 'red',
                                                                    shake=True)], 70, x),
        phrase(s(N('"Tô chegando')) - .05, AT['excuse'], 1010, [line('23:31, ANTES DA PORTA', s(N('Onze e meia')), size=40),
                                                                line('“TÔ CHEGANDO', s(N('"Tô chegando'))),
                                                                line('NA CASA DELE.”', s(N('casa dele."')), 'red', shake=True)],
               62, x),
        phrase(s(R('Antes de ver')) - .05, AT['doubt'], 900, [line('“ANTES DE VER', s(R('Antes de ver'))),
                                                              line('A TUA CARA.”', s(R('tua cara.')), 'yellow')], 64, x),
        phrase(AT['doubt'] + .05, AT['chip'], 900, [line('VOCÊ NÃO SABE', s(N('Você não sabe'))),
                                                    line('SE ACREDITA.', s(N('se acredita.')), 'yellow')], 64, x),
        {'type': 'list', 'start': round(AT['chip'] + .05, 2), 'end': AT['bar'], 'y': 560, 'x': x,
         'items': [{'at': round(s(N('O chip vai')), 2), 'left': 'O CHIP', 'right': 'NO BUEIRO'},
                   {'at': round(s(N('e o celular')), 2), 'left': 'O CELULAR', 'right': 'COM VOCÊ'}]},
        phrase(s(N('pela primeira vez, o')) - .05, AT['wanted'], 1010, [line('PELA PRIMEIRA VEZ,', s(N('pela primeira vez, o'))),
                                                                       line('O DELE.', s(N('o dele.')), 'yellow')], 58, x),
        phrase(AT['wanted'] + .05, AT['comments'], 1000, [line('OS DOIS SÃO', s(N('Agora os dois'))),
                                                          line('PROCURADOS.', s(N('são procurados.')), 'red', shake=True)], 66, x),
        phrase(s(N('E pega o')) - .05, AT['phone'], 900, [line('E PEGA', s(N('E pega o'))),
                                                          line('O CELULAR.', s(N('o celular.', 0)), 'red')], 76, x),
        phrase(s(N('O seu número')) - .05, s(N('Uns te chamam')) - .02, 980,
               [line('O SEU NÚMERO', s(N('O seu número'))), line('VAZOU.', s(N('vazou junto')), 'yellow')], 66, x),
        phrase(s(N('Uns te chamam')) - .02, AT['avenue'], 980, [line('“TÔ CONTIGO,', s(N('"Tô contigo,'))),
                                                                line('ZINHO.”', s(N('contigo, Zinho."', 1)), 'yellow')], 66, x),
        phrase(s(N('farol apagado')) - .05, AT['still'], 900, [line('DE FAROL', s(N('farol apagado'))),
                                                               line('APAGADO.', s(N('apagado vem')), 'red', shake=True)], 80, x),
        phrase(AT['still'] + .05, AT['window'], 900, [line('“NÃO SE MEXE.”', s(R('Não se mexe.')), 'yellow')], 70, x),
        phrase(s(N('anel grosso')) - .05, AT['photo'], 900, [line('UM ANEL', s(N('um anel grosso'))),
                                                             line('DE OURO.', s(N('de ouro.')), 'yellow')], 80, x),
        {'type': 'stamp', 'start': round(s(N('A mão que')) - .02, 2), 'end': AT['him'], 'text': 'O MESMO ANEL', 'y': 900,
         'x': x, 'angle': -7},
        phrase(AT['him'] + .05, AT['one-of-them'], 900, [line('“É ELE.', s(R('É ele.'))),
                                                         line('O HOMEM QUE', s(R('O homem que')), 'yellow'),
                                                         line('ME COBRA.”', s(R('me cobra.')), 'yellow')], 70, x),
        phrase(AT['one-of-them'] + .05, AT['gone'], 900, [line('VOCÊ VÊ UM DELES.', s(N('você vê um'))),
                                                          line('PELO MENOS A MÃO.', s(N('Pelo menos a')), 'red')], 52, x),
        phrase(s(N('um lugar até')) - .05, AT['places'], 900, [line('UM LUGAR', s(N('um lugar até'))),
                                                               line('ATÉ AMANHECER.', s(N('até amanhecer.')), 'yellow')], 64, x),
        phrase(AT['junkyard'] + .05, AT['mother'], 900, [line('O FERRO-VELHO', s(R('O ferro-velho da'))),
                                                         line('DA FOTO', s(R('da foto:')), 'yellow')], 68, x),
        phrase(AT['mother'] + .05, AT['theirs'], 900, [line('A CASA', s(R('Ou a casa'))),
                                                       line('DA MÃE DELE', s(R('minha mãe.')), 'yellow')], 72, x),
        phrase(AT['theirs'] + .05, AT['they-know'], 900, [line('O FERRO-VELHO', s(N('O ferro-velho é'))),
                                                          line('É DELES.', s(N('é deles.')), 'red', shake=True)], 68, x),
        phrase(AT['they-know'] + .05, AT['choice'], 900, [line('ELES SABEM', s(N('eles sabem'))),
                                                          line('ONDE FICA.', s(N('onde fica.')), 'red', shake=True)], 76, x),
        # The vote, with its two buttons, as the other parts ask.
        phrase(AT['choice'], vote_end, 420, [line('FERRO-VELHO', s(N('Ferro-velho ou mãe?'))),
                                             line('OU MÃE?', s(N('ou mãe?')), 'yellow')], 80, x),
        {'type': 'buttons', 'start': round(s(N('Comenta uma palavra')) - .05, 2), 'end': vote_end, 'y': 660, 'x': x,
         'prompt': 'COMENTA UMA PALAVRA', 'prompt_at': round(s(N('Comenta uma palavra')), 2),
         'items': [{'text': 'FERRO-VELHO', 'at': round(s(N('uma palavra só.', 1)), 2), 'style': 'yellow'},
                   {'text': 'MÃE', 'at': round(s(N('uma palavra só.', 2)), 2), 'style': 'white'}]},
        {'type': 'box', 'start': round(s(N('O que a maioria')), 2), 'end': vote_end, 'y': 830, 'x': x,
         'title': f'PARTE {PART + 1}', 'sub': 'a maioria decide o próximo passo'},
    ]
    effects = oe + [
        *[sfx('whoosh.wav', AT[n] - WHOOSH_PEAK, -2) for n in ('name', 'hook', 'alley', 'chat', 'bar', 'phone', 'avenue',
                                                               'window', 'photo', 'junkyard', 'choice')],
        sfx('impacto.wav', s(N('ele: Renato.', 1)) - .04, -5),
        sfx('porta-fecha.wav', e(N('carro abre devagar.', 2)) + .05, -12),
        sfx('passos.wav', s(R('Pelos fundos.')) + .3, -12),
        *[sfx('tranca.wav', e(N('sacode o portão.', 2)) + .05 + .22*k, -8 - 2*k) for k in range(3)],
        sfx('impacto-suave.wav', s(N('o portão.')) - .04, -9),
        *[sfx('passos.wav', s(N('Do outro lado')) + .2 + .33*k, -12) for k in range(3)],
        sfx('vibracao.wav', s(N('o celular dele')) + .05, -8),
        sfx('notificacao.wav', s(N('"Cadê vocês?"')) - .05, -8),
        sfx('impacto-suave.wav', s(N('"Cadê vocês?"')) - .05, -9),
        sfx('impacto.wav', s(N('"Tô chegando')) - .05, -4),
        sfx('pop.wav', e(N('fica com você.', 2)) + .05, -10),
        sfx('impacto-suave.wav', s(N('o dele.')) - .04, -7),
        sfx('impacto.wav', s(N('são procurados.')) - .04, -6),
        sfx('impacto-suave.wav', s(N('E pega o')) - .04, -8),
        *[sfx('notificacao.wav', s(N('Na rua, é')) + .4 + .55*k, -12 - k) for k in range(4)],
        sfx('vibracao.wav', s(N('celular que não')), -10),
        sfx('carro.wav', s(N('farol apagado')) - .5, -8),
        sfx('impacto.wav', s(N('farol apagado')) - .04, -6),
        sfx('impacto-suave.wav', s(N('um anel grosso')) - .04, -8),
        sfx('impacto.wav', s(N('A mão que')) - .04, -5),
        sfx('impacto-suave.wav', s(R('É ele.')) - .04, -7),
        sfx('impacto-suave.wav', s(N('é deles.')) - .04, -8),
        sfx('impacto-suave.wav', s(N('eles sabem')) - .04, -8),
        *[sfx('pop.wav', t, -10) for t in (s(N('uma palavra só.', 1)), s(N('uma palavra só.', 2)), s(N('O que a maioria')))],
    ]
    if allies:
        effects.append(sfx('whoosh.wav', AT['credits'] - WHOOSH_PEAK, -6))
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
                    'scenes': scenes, 'graphics': graphics, 'sfx': effects, 'captions': [],
                    # Part 2's sounds: the car, the steps, the doors and the phone buzzing.
                    'effects': ['../../episodio-02/montagem/efeitos']}
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
