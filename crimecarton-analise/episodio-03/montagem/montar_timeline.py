#!/usr/bin/env python3
"""Build Part 3's narration track and its two timelines from the word alignments.

Part 3 is "O preço" (roteiro-ep03.txt). The track joins, in the script's order: the series'
opening, cut from Part 1's narration (its first 17 words, the same art and audio in every
part); the narrator's lines from narracao-ep03-narrador.wav, closing request included;
Renato's from narracao-ep03-renato.wav, in his own voice (voz_renato.py); the cobrador's
audio message from narracao-ep03-cobranca.wav, lower and through a phone speaker
(voz_cobranca.py); and the pauses the edit opens for sounds, such as the car door and the
replay of the message. Each line is found in its recording by its words. Every cut, graphic
and effect is anchored to a word of the script, so the edit follows the voices again if they
are re-aligned.

Every framing keeps faces, hands, the phone and the ring out of the top quarter, where the
panel "A SUA PARTE · SUSPEITA" and the part's tag sit, and the phrases between 65% and 80%
of the height (see ../../../CLAUDE.md).

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
          'RENATO': (HERE / 'vozes' / 'renato.wav', HERE / 'alinhamento-renato.json'),
          # The cobrador's audio message, made by voz_cobranca.py.
          'COBRANCA': (HERE / 'vozes' / 'cobranca.wav', HERE / 'alinhamento-cobranca.json')}
AUDIO = EPISODE / 'narracao-ep03.wav'
PART, VOTE = 3, [('FUGIR', 77), ('FICAR', 23)]   # Part 2's vote: 10 FUGIR, 3 FICAR
NAME = 'RENATO'                                  # the friend's name, the most liked comment
HANDLE = '@golpecartoon'
ALLIES = HERE / 'aliados-parte-03.json'
# Without allies the video ends 2 s after the voice; with them, the credits take 3.5 s.
TAIL = 3.5 if ALLIES.exists() and json.loads(ALLIES.read_text(encoding='utf-8')) else 2.0
# Renato talks beside Zinho, as loud as the narrator; the message plays a little under him,
# as Part 1's audio message did.
FRIEND_GAIN, MESSAGE_GAIN = 0, -1
# The message heard again, in the pause after "Você escuta outra vez". The renderer mixes
# effects about 4 dB under the voices, so this leaves it some 5 dB under the message itself.
ECHO_GAIN = -1
# Seconds kept before a voice's first word and after its last at a change of voice, and
# the silence between the two voices.
LEAD, TRAIL, SWITCH = .12, .22, .25
WHOOSH_PEAK = .36
# Instagram's and the vertical versions' layouts. TikTok's search bar covers the top
# 146 px: the HUD, the tags and the cards go below it. The like, comment and share column
# covers the right of the lower half: there, the vertical version centres everything at
# x = 330 and moves the cards 25 px left, so nothing passes x = 590.
INSTAGRAM = {'name': 'timeline.json', 'art': '', 'hud_dy': 0, 'tag_y': 230, 'card_top': 300, 'x': 360, 'card_dx': 0,
             'tv_dx': 0, 'tv_scale': 1, 'width': 570, 'bars': 540, 'input': 600}
VERTICAL = {'name': 'timeline-vertical.json', 'art': '-vertical', 'hud_dy': 67, 'tag_y': 297, 'card_top': 334, 'x': 330, 'card_dx': -25,
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
           'RENATO': EPISODE / 'narracao-ep03-renato.txt', 'COBRANCA': EPISODE / 'narracao-ep03-cobranca.txt'}
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


def C(phrase, k=0):
    return 'COBRANCA', find('COBRANCA', phrase) + k


def V(i):
    return 'VINHETA', i


# Silence the edit opens after a word, in seconds, for the sounds of the story. Phrases
# point at their first word; the offset picks the word the pause follows. The pause
# replaces the voice's own silence there, except for LEAD and TRAIL around the cut. At a
# voice's last word before another voice, it is the silence between the two.
PAUSES = {
    N('decidiram: fugir.', 1): .3,          # the vote's stamp lands
    N('a ele: Renato.', 2): .6,             # the name's stamp lands
    N('quem paga é ele.', 3): .45,          # the flash of Renato, caught
    N('do carro.', 1): .45,                 # the car door shuts outside
    N('cai do outro lado.', 3): .55,        # black: the fall on the other side
    N('por trás.', 1): .3,                  # the hand on his collar
    N('foto da divisão.', 2): .5,           # the stamp, before Renato's shout
    N('o ar acaba.', 2): .3,
    N('está sozinho.', 1): .7,              # silence, then the phone buzzes
    N('não é ele.', 2): .4,
    N('um áudio.', 1): .7,                  # the message starts playing
    C('é a próxima.', 2): .8,               # the threat sinks in
    N('outra vez.', 1): 2.9,                # the message again: "Você correu. Ele não."
    N('Calma demais.', 1): .4,
    N('eram moleques.', 1): .4,
    N('duas horas.', 1): .5,                # the clock ticks
    N('pé no muro.', 2): .6,                # before the question
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
    gains['COBRANCA'] += MESSAGE_GAIN
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

    def __init__(self, at, end, layout, gains):
        self.at, self.END, self.L, self.gains = at, end, layout, gains

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
    return {'sound': sound, 'at': round(at, 3), 'gain': round(gain, 1)}


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
        # In the corner: centred, the tag sat on Zinho's head in the backpack art.
        {'type': 'tag', 'start': .15, 'end': story, 'text': f'PARTE {part}', 'y': L['tag_y'], 'x': 112, 'size': 32},
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


# Framings inside the illustrations: left, top, right, bottom as fractions. Equal width and
# height keep the 9:16 shape. Each one is chosen so that, after its zoom, no face, hand,
# phone or ring sits in the top quarter (the panel and the tag) or in the bottom fifth.
MEN01 = [0.05, 0.12, 0.75, 0.82]         # the two men and the torch, through the window
RENATO02 = [0.30, 0.06, 1.0, 0.76]       # Renato in front, at the back door
KITCHEN02 = [0.06, 0.0, 0.94, 0.88]      # the two running, their heads below the tag
BOOST03 = [0.15, 0.15, 0.85, 0.85]       # Renato's hands under Zinho's foot
TOP03 = [0.16, 0.17, 0.76, 0.77]         # Zinho reaching the top of the wall
RING04 = [0.45, 0.19, 1.0, 0.74]         # the ring on the hand at Renato's collar
SCREAM05 = [0.05, 0.0, 0.95, 0.9]        # Renato shouting, his head below the panel
FACE06 = [0.25, 0.195, 0.75, 0.695]      # Zinho running, out of breath
ZINHO07 = [0.14, 0.19, 0.74, 0.79]       # Zinho on the bus floor
POCKET07 = [0.21, 0.255, 0.71, 0.755]    # his hands and the dark phone
PHONE_WIDE = [0.125, 0.13, 0.875, 0.88]  # the phone in his hand, the screen from 29% to 66%
PHONE_CLOSE = [0.20, 0.165, 0.80, 0.765]  # closer: the screen from 30% to 76%, below the tag
SHOULDER09 = [0.30, 0.05, 1.0, 0.75]     # the hand with the ring on Renato's shoulder
FACE10 = [0.2, 0.095, 0.8, 0.695]        # Zinho's face as he listens, his hair below the tag
PHOTO09 = [0.2, 0.04, 1.0, 0.84]         # the photo: the ring left of TikTok's buttons
JUNK12 = [0.16, 0.08, 1.0, 0.92]         # the gate, with the sign left of TikTok's buttons
DOOR13 = [0.05, 0.0, 0.95, 0.9]          # Zinho at the bus door
RING_PHOTO = [0.513, 0.30, 0.953, 0.74]  # the ring in Part 2's photo, the other hand below the tag
# The lit, blank screen of the phone in scene 8 (compor_cenas.TELA08), a little larger so
# the lock screen covers its bright edge. The night of the escape is past midnight of the
# 28th, Part 2's "23:47".
_TELA08 = [(.3889, .3481), (.6153, .3481), (.6132, .6220), (.3868, .6220)]
_MID08 = (sum(x for x, _ in _TELA08)/4, sum(y for _, y in _TELA08)/4)
SCREEN08 = [[round(_MID08[0] + (x - _MID08[0])*1.035, 4), round(_MID08[1] + (y - _MID08[1])*1.035, 4)] for x, y in _TELA08]
NIGHT = 'quinta-feira, 29 de outubro'
LOCK_PHOTO = {'quad': SCREEN08, 'state': 'lock', 'date': NIGHT, 'time': '01:04',
              'app': 'MENSAGENS', 'sender': 'Renato', 'message': 'Foto', 'when': 'agora'}
LOCK_HOUR = {'quad': SCREEN08, 'state': 'lock', 'date': NIGHT, 'time': '01:12',
             'app': 'MENSAGENS', 'sender': 'Renato', 'message': 'Áudio (0:14)', 'when': '7 min'}
# The junkyard's blank sign in scene 12, with the name from Part 2's calendar.
SIGN12 = [{'box': [0.5824, 0.4755, 0.8183, 0.5413], 'text': 'FERRO-VELHO\nSÃO JORGE', 'color': [74, 36, 22],
           'opacity': .86, 'weight': 'ExtraBold', 'pad': 6, 'blur': .6}]


def build(ed):
    s, e, cut, L = ed.s, ed.e, ed.cut, ed.L
    END, x = ed.END, L['x']
    story = cut(N('Mas fugir tem'))
    # The opening's vote gives way to the name the audience chose, then the story starts.
    opening, og, oe = abertura(ed, PART, VOTE, N('Chegou agora?'), N('As partes um'), N('Vocês decidiram:'),
                               N('decidiram: fugir.', 1), cut(N('E deram um')))
    p2 = '../episodio-02/'
    allies = json.loads(ALLIES.read_text(encoding='utf-8')) if ALLIES.exists() else []
    VOICE_END = ed.at[('NARRADOR', len(TEXT['NARRADOR']) - 1)][1]
    plan = opening + [
        # The name the audience gave him, over his portrait from Part 2.
        ('name', cut(N('E deram um')), dict(kind='art', asset=p2 + 'cena-08-retrato-amigo.png', zoom=.05)),
        ('hook', story, dict(kind='art', asset='cena-01-portao.png', zoom=.05)),
        # A flash of what is coming: Renato caught.
        ('flash', cut(N('E esta noite,')), dict(kind='art', asset='cena-05-renato-grita.png', crop=SCREAM05, zoom=.06,
                                                brightness=.6)),
        ('men', cut(N('Lá fora, dois')), dict(kind='art', asset='cena-01-portao.png', crop=MEN01, zoom=.06)),
        ('back', cut(R('Pelos fundos.')), dict(kind='art', asset='cena-02-cozinha.png', crop=RENATO02, zoom=.06)),
        ('kitchen', cut(N('Vocês atravessam a')), dict(kind='art', asset='cena-02-cozinha.png', crop=KITCHEN02, zoom=.04,
                                                       direction='out')),
        ('wall', cut(N('No quintal, o')), dict(kind='art', asset='cena-03-pe-no-muro.png', zoom=.05)),
        ('boost', cut(N('Renato junta as')), dict(kind='art', asset='cena-03-pe-no-muro.png', crop=BOOST03, zoom=.04)),
        ('jump', cut(N('Você sobe, pula')), dict(kind='art', asset='cena-03-pe-no-muro.png', crop=TOP03, zoom=.06)),
        ('fall', round(e(N('cai do outro lado.', 3)) - .02, 2), dict(kind='black')),
        ('grab', cut(N('Quando ele agarra')), dict(kind='art', asset='cena-04-mao-anel.png', zoom=.05)),
        ('ring', cut(N('No dedo, um')), dict(kind='art', asset='cena-04-mao-anel.png', crop=RING04, zoom=.08)),
        ('photo-ring', cut(N('O mesmo anel')), dict(kind='art', asset=p2 + 'cena-04-foto-divisao.png', crop=RING_PHOTO,
                                                    zoom=.1)),
        ('scream', cut(R('Corre! Corre!')), dict(kind='art', asset='cena-05-renato-grita.png', crop=SCREAM05, zoom=.08)),
        ('run', cut(N('Você corre. E')), dict(kind='art', asset='cena-06-zinho-corre.png', zoom=.05)),
        ('breath', cut(N('Só para quando')), dict(kind='art', asset='cena-06-zinho-corre.png', crop=FACE06, zoom=.05)),
        ('bus', cut(N('No fim da')), dict(kind='art', asset='cena-07-onibus.png', zoom=.05, direction='out')),
        ('hide', cut(N('Você se esconde')), dict(kind='art', asset='cena-07-onibus.png', crop=ZINHO07, zoom=.05)),
        ('pocket', cut(N('No bolso, o')), dict(kind='art', asset='cena-07-onibus.png', crop=POCKET07, zoom=.05)),
        ('alone', cut(N('Pela primeira vez')), dict(kind='art', asset='cena-07-onibus.png', zoom=.04, direction='out',
                                                    brightness=.75)),
        # Renato's number, but not Renato: the photo, then the message.
        ('buzz', cut(N('Então o celular')), dict(kind='art', asset='cena-08-celular.png', crop=PHONE_WIDE, zoom=.05,
                                                 screen=LOCK_PHOTO)),
        ('chat-photo', cut(N('Primeiro, uma foto.')), dict(kind='art', asset='montagem/arte/celular-foto.png',
                                                           crop=PHONE_CLOSE, zoom=.05)),
        ('photo', cut(N('Renato numa cadeira,')), dict(kind='art', asset='cena-09-foto-refem.png', crop=PHOTO09, zoom=.05)),
        ('scrap', cut(N('Atrás dele, montes')), dict(kind='art', asset='cena-09-foto-refem.png', crop=PHOTO09, zoom=.04,
                                                     direction='out', brightness=.9)),
        ('shoulder', cut(N('No ombro dele,')), dict(kind='art', asset='cena-09-foto-refem.png', crop=SHOULDER09, zoom=.06)),
        ('chat-audio', cut(N('Depois, um áudio.')), dict(kind='art', asset='montagem/arte/celular-audio.png',
                                                         crop=PHONE_CLOSE, zoom=.05)),
        ('listen', cut(C('Você correu.')), dict(kind='art', asset='cena-10-zinho-escuta.png', zoom=.05)),
        ('trade', cut(C('Vamos trocar:')), dict(kind='art', asset='cena-10-zinho-escuta.png', crop=FACE10, zoom=.06)),
        ('junkyard', cut(C('Três da manhã,')), dict(kind='art', asset='cena-12-ferro-velho.png', crop=JUNK12, zoom=.05,
                                                    paint=SIGN12)),
        ('threat', cut(C('Se chamar a')), dict(kind='art', asset='cena-10-zinho-escuta.png', crop=FACE10, zoom=.04,
                                               direction='out', brightness=.85)),
        ('again', cut(N('Você escuta outra')), dict(kind='art', asset='cena-10-zinho-escuta.png', zoom=.04,
                                                    direction='out', brightness=.8)),
        # The lunch as a memory: the drawing on a card, so Renato as a boy stays left of
        # TikTok's buttons (compor_cenas.py, one card per layout).
        ('mother', cut(N('A mãe dele.')), dict(kind='art', asset=f"montagem/arte/lembranca{L['art']}.png", zoom=.04,
                                               direction='out')),
        ('clock', cut(N('Você olha a')), dict(kind='art', asset='cena-08-celular.png', crop=PHONE_CLOSE, zoom=.06,
                                              screen=LOCK_HOUR)),
        ('price', cut(N('O homem que')), dict(kind='art', asset='cena-09-foto-refem.png', crop=PHOTO09, zoom=.04,
                                              direction='out', brightness=.7)),
        ('help', cut(N('Mas foi esse')), dict(kind='art', asset='cena-03-pe-no-muro.png', crop=BOOST03, zoom=.04,
                                              brightness=.85)),
        # The vote: Zinho at the bus door, dark under the question and the buttons.
        ('choice', cut(N('Trocar ou deixar?')), dict(kind='art', asset='cena-13-decisao.png', crop=DOOR13, zoom=.03,
                                                     direction='out', brightness=.45)),
    ]
    if allies:
        plan.append(('credits', round(VOICE_END + .6, 2), dict(kind='art', asset='montagem/arte/creditos.png', zoom=.03)))
    plan.sort(key=lambda item: item[1])
    AT = {name: t for name, t, _ in plan}
    scenes = [{'start': t, 'end': plan[k+1][1] if k + 1 < len(plan) else END, **fields}
              for k, (_, t, fields) in enumerate(plan)]
    vote_end = AT.get('credits', END + .5)
    graphics = og + [
        {'type': 'hud', 'start': story, 'end': AT['choice'], 'label': 'A SUA PARTE', 'dy': L['hud_dy'],
         'values': [{'at': story, 'text': 'R$ 0', 'color': 'red'}],
         'stars': [{'at': story, 'count': 5, 'step': 0}]},
        {'type': 'tag', 'start': story, 'end': AT['bus'], 'text': 'A FUGA · O MURO', 'y': L['tag_y']},
        {'type': 'tag', 'start': AT['bus'], 'end': AT['buzz'], 'text': 'SOZINHO · O ÔNIBUS', 'y': L['tag_y']},
        {'type': 'tag', 'start': AT['buzz'], 'end': AT['listen'], 'text': 'PISTA · A FOTO', 'y': L['tag_y']},
        {'type': 'tag', 'start': AT['listen'], 'end': AT['mother'], 'text': 'PISTA · O ÁUDIO', 'y': L['tag_y']},
        {'type': 'tag', 'start': AT['mother'], 'end': AT['choice'], 'text': 'O PREÇO', 'y': L['tag_y']},
        # The name, stamped over his face.
        phrase(AT['name'] + .05, story, 760, [line('E O NOME DELE', s(N('E deram um')))], 64, x),
        {'type': 'stamp', 'start': round(s(N('ele: Renato.', 1)) - .02, 2), 'end': story, 'text': NAME, 'y': 900, 'x': x,
         'angle': -7, 'color': 'yellow', 'filled': True},
        # Red alarm: the flash, the capture, the threat and the price.
        {'type': 'vignette', 'start': AT['flash'], 'end': AT['men'], 'color': 'alert', 'strength': .8},
        {'type': 'vignette', 'start': AT['grab'], 'end': AT['run'], 'color': 'alert', 'strength': .8},
        {'type': 'vignette', 'start': AT['listen'], 'end': AT['again'], 'color': 'alert', 'strength': .7},
        {'type': 'vignette', 'start': AT['price'], 'end': AT['choice'], 'color': 'alert', 'strength': .6},
        phrase(AT['hook'] + .05, AT['flash'], 900, [line('FUGIR TEM', s(N('Mas fugir tem'))),
                                                    line('UM PREÇO.', s(N('um preço.')), 'yellow')], 72, x),
        phrase(AT['flash'] + .05, AT['men'], 900, [line('QUEM PAGA', s(N('quem paga é'))),
                                                   line('É ELE.', s(N('quem paga é ele.', 2)), 'red', shake=True)], 72, x),
        phrase(s(N('dois homens')) - .05, AT['back'], 900, [line('DOIS HOMENS.', s(N('dois homens'))),
                                                            line('UMA LANTERNA.', s(N('uma lanterna.')), 'yellow')], 60, x),
        phrase(AT['back'] + .05, AT['kitchen'], 900, [line('“PELOS FUNDOS.', s(R('Pelos fundos.'))),
                                                      line('VAI!”', s(R('Vai!')), 'yellow', shake=True)], 64, x),
        phrase(s(N('mais alto do')) - .05, AT['boost'], 900, [line('MAIS ALTO DO QUE', s(N('mais alto do'))),
                                                              line('VOCÊ LEMBRAVA.', s(N('você lembrava.')), 'yellow')], 54, x),
        phrase(s(N('te dá pé.')) - .05, s(R('Sobe.')) - .1, 900, [line('ELE TE DÁ PÉ.', s(N('te dá pé.')), 'yellow')], 62, x),
        phrase(s(R('Sobe.')) - .1, AT['jump'], 900, [line('“SOBE.', s(R('Sobe.'))),
                                                     line('EU VOU ATRÁS.”', s(R('Eu vou atrás.')), 'yellow')], 62, x),
        phrase(s(N('uma mão puxa')) - .05, AT['ring'], 900, [line('UMA MÃO', s(N('uma mão puxa'))),
                                                             line('POR TRÁS.', s(N('por trás.')), 'red', shake=True)], 76, x),
        phrase(s(N('um anel grosso')) - .05, AT['photo-ring'], 900, [line('UM ANEL', s(N('um anel grosso'))),
                                                                     line('DE OURO.', s(N('de ouro.')), 'yellow')], 76, x),
        {'type': 'stamp', 'start': round(s(N('O mesmo anel')) - .02, 2), 'end': AT['scream'], 'text': 'O MESMO ANEL',
         'y': 900, 'x': x, 'angle': -7},
        phrase(AT['scream'] + .05, AT['run'], 900, [line('“CORRE!', s(R('Corre! Corre!')), 'red', shake=True),
                                                    line('CORRE!”', s(R('Corre! Corre!', 1)), 'red', shake=True)], 80, x),
        phrase(s(N('cada passo pesa')) - .05, AT['breath'], 900, [line('CADA PASSO', s(N('cada passo pesa'))),
                                                                  line('PESA MAIS.', s(N('pesa mais que')), 'yellow')], 72, x),
        phrase(s(N('um ônibus abandonado.')) - .05, AT['hide'], 900, [
            line('UM ÔNIBUS', s(N('um ônibus abandonado.'))),
            line('ABANDONADO.', s(N('um ônibus abandonado.', 2)), 'yellow')], 66, x),
        phrase(s(N('uma casa para')) - .05, AT['alone'], 900, [line('UMA CASA', s(N('uma casa para'))),
                                                               line('SEM VOLTA.', s(N('não pode voltar.')), 'yellow')], 72, x),
        phrase(AT['alone'] + .05, AT['buzz'], 900, [line('VOCÊ ESTÁ', s(N('você está sozinho.'))),
                                                    line('SOZINHO.', s(N('está sozinho.', 1)), 'yellow')], 76, x),
        phrase(s(N('É o número')) - .05, s(N('Mas não é')) - .05, 900, [line('É O NÚMERO', s(N('É o número'))),
                                                                       line('DO RENATO.', s(N('do Renato.')), 'yellow')],
               70, x),
        phrase(s(N('Mas não é')) - .05, AT['chat-photo'], 900, [line('MAS NÃO É ELE.', s(N('Mas não é')), 'red',
                                                                     shake=True)], 64, x),
        phrase(s(N('o lábio cortado.')) - .05, AT['scrap'], 900, [line('COM O LÁBIO', s(N('o lábio cortado.'))),
                                                                  line('CORTADO.', s(N('lábio cortado.', 1)), 'red')], 70, x),
        phrase(AT['scrap'] + .05, AT['shoulder'], 900, [line('MONTES DE', s(N('montes de sucata.'))),
                                                        line('SUCATA.', s(N('montes de sucata.', 2)), 'yellow')], 72, x),
        phrase(s(N('a mão com')) - .05, AT['chat-audio'], 900, [line('A MÃO', s(N('a mão com'))),
                                                                line('COM O ANEL.', s(N('com o anel.', 2)), 'yellow')], 72, x),
        phrase(AT['chat-audio'] + .05, AT['listen'], 900, [line('DEPOIS,', s(N('Depois, um áudio.'))),
                                                           line('UM ÁUDIO.', s(N('um áudio.')), 'yellow')], 72, x),
        phrase(AT['listen'] + .05, AT['trade'], 900, [line('“VOCÊ CORREU.', s(C('Você correu.'))),
                                                      line('ELE NÃO.”', s(C('Ele não.')), 'red')], 64, x),
        phrase(AT['trade'] + .05, AT['junkyard'], 900, [line('“VAMOS TROCAR:', s(C('Vamos trocar:'))),
                                                        line('VOCÊ POR ELE.”', s(C('você por ele.')), 'yellow',
                                                             shake=True)], 62, x),
        phrase(AT['junkyard'] + .05, AT['threat'], 900, [line('“3 DA MANHÃ.', s(C('Três da manhã,'))),
                                                         line('SOZINHO.”', s(C('Sozinho.')), 'red')], 70, x),
        phrase(AT['threat'] + .05, AT['again'], 920, [line('“SE CHAMAR A POLÍCIA,', s(C('Se chamar a')), size=40),
                                                      line('A MÃE DELE', s(C('a mãe dele'))),
                                                      line('É A PRÓXIMA.”', s(C('é a próxima.')), 'red', shake=True)], 66, x),
        phrase(s(N('Calma demais.')) - .05, AT['mother'], 900, [line('CALMA', s(N('Calma demais.'))),
                                                                line('DEMAIS.', s(N('Calma demais.', 1)), 'red')], 80, x),
        phrase(s(N('A mesma que')) - .05, AT['clock'], 900, [line('A MESMA QUE TE', s(N('A mesma que'))),
                                                             line('DAVA ALMOÇO.', s(N('dava almoço')), 'yellow')], 62, x),
        phrase(s(N('Faltam menos')) - .05, AT['price'], 900, [line('FALTAM MENOS', s(N('Faltam menos'))),
                                                              line('DE DUAS HORAS.', s(N('duas horas.')), 'red')], 62, x),
        phrase(AT['price'] + .05, AT['help'], 920, [line('ELE VENDEU O SEU NOME.', s(N('vendeu o seu')), size=40),
                                                    line('AGORA PAGA', s(N('agora paga por')), 'yellow'),
                                                    line('POR ELE.', s(N('paga por ele.', 2)), 'yellow')], 66, x),
        phrase(s(N('te deu pé')) - .05, AT['choice'], 900, [line('MAS ELE', s(N('Mas foi esse'))),
                                                            line('TE DEU PÉ.', s(N('te deu pé')), 'yellow')], 76, x),
        # The vote, with its two buttons, as the other parts ask. The panel is gone by
        # now; the question sits below Zinho's face.
        phrase(AT['choice'], vote_end, 600, [line('TROCAR', s(N('Trocar ou deixar?'))),
                                             line('OU DEIXAR?', s(N('ou deixar?', 1)), 'yellow')], 76, x),
        {'type': 'buttons', 'start': round(s(N('Comenta uma palavra')) - .05, 2), 'end': vote_end, 'y': 790, 'x': x,
         'prompt': 'COMENTA UMA PALAVRA', 'prompt_at': round(s(N('Comenta uma palavra')), 2),
         'items': [{'text': 'TROCAR', 'at': round(s(N('uma palavra só.', 1)), 2), 'style': 'yellow'},
                   {'text': 'DEIXAR', 'at': round(s(N('uma palavra só.', 2)), 2), 'style': 'white'}]},
        {'type': 'box', 'start': round(s(N('O que a maioria')), 2), 'end': vote_end, 'y': 930, 'x': x,
         'title': f'PARTE {PART + 1}', 'sub': 'a maioria decide o próximo passo'},
    ]
    clock = s(N('Você olha a'))
    effects = oe + [
        *[sfx('whoosh.wav', AT[n] - WHOOSH_PEAK, -2) for n in ('name', 'hook', 'men', 'wall', 'grab', 'run', 'bus', 'buzz',
                                                               'listen', 'mother', 'clock', 'choice')],
        sfx('impacto.wav', s(N('ele: Renato.', 1)) - .04, -5),
        sfx('impacto-suave.wav', s(N('quem paga é ele.', 3)) - .04, -7),
        sfx('porta-fecha.wav', e(N('do carro.', 1)) + .05, -12),
        sfx('interruptor.wav', s(N('acende uma lanterna.')) + .05, -10),
        sfx('passos.wav', s(R('Pelos fundos.')) + .3, -12),
        sfx('passos.wav', s(N('Vocês atravessam a')) + .2, -13),
        sfx('impacto-suave.wav', e(N('cai do outro lado.', 3)) + .02, -5),
        sfx('impacto.wav', s(N('uma mão puxa')) - .04, -5),
        sfx('impacto-suave.wav', s(N('um anel grosso')) - .04, -8),
        sfx('impacto.wav', s(N('O mesmo anel')) - .04, -5),
        *[sfx('passos.wav', s(N('Você corre. E')) + .1 + .45*k, -11 - k) for k in range(3)],
        sfx('vibracao.wav', s(N('celular vibra.', 1)) - .1, -8),
        sfx('impacto.wav', s(N('Mas não é')) - .04, -6),
        sfx('notificacao.wav', s(N('Primeiro, uma foto.')) + .1, -10),
        sfx('impacto-suave.wav', s(N('o lábio cortado.')) - .04, -9),
        sfx('notificacao.wav', s(N('Depois, um áudio.')) + .1, -10),
        sfx('impacto-suave.wav', s(C('você por ele.')) - .04, -7),
        sfx('impacto.wav', s(C('é a próxima.')) - .04, -6),
        # The message again, in the pause after "Você escuta outra vez".
        sfx('cobranca-eco.wav', e(N('outra vez.', 1)) + .15, ed.gains['COBRANCA'] + ECHO_GAIN),
        sfx('impacto-suave.wav', s(N('Calma demais.', 1)) - .04, -9),
        *[sfx('tique.wav', clock + .5*k, -15) for k in range(int((e(N('duas horas.', 1)) + .4 - clock)/.5))],
        sfx('impacto-suave.wav', s(N('agora paga por')) - .04, -8),
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
        scenes, graphics, effects = build(Edit(at, end, layout, gains))
        wide = too_wide(graphics, layout['width'])
        if wide:
            raise ValueError(f'Lines wider than the {layout["name"]} layout allows: {wide}')
        graficos.check(graphics)
        timeline = {'timing_status': 'estimated' if args.estimar else 'aligned_to_voice',
                    'style': 'guia-de-estilo-referencia.md', 'script': SCRIPT.name,
                    'alignment': [str(VOICES[v][1].relative_to(EPISODE.parent)) for v in VOICES],
                    'audio': str(audio) if args.estimar else audio.name, 'tail': TAIL,
                    'scenes': scenes, 'graphics': graphics, 'sfx': effects, 'captions': [],
                    # Part 2's sounds (the car door, the steps, the switch, the phone buzzing)
                    # and this part's: the cobrador's message heard again.
                    'effects': ['../../episodio-02/montagem/efeitos', 'efeitos']}
        if args.estimar:
            # Out of place, the timeline names its assets and effects by absolute path.
            for sc in scenes:
                if 'asset' in sc:
                    sc['asset'] = str((EPISODE / sc['asset']).resolve())
            timeline['effects'] = [str((HERE / d).resolve()) for d in timeline['effects']]
        (out / layout['name']).write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f"{layout['name']}: {len(scenes)} scenes, {len(graphics)} graphics, {len(effects)} sound effects, ends at {end}s")
    print(f'{audio.name}: {length}s of voice; gains ' + ', '.join(f'{v} {g:+.1f} dB' for v, g in gains.items()))


if __name__ == '__main__':
    main()
