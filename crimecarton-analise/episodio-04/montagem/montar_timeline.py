#!/usr/bin/env python3
"""Build Part 4's narration track and its two timelines from the word alignments.

Part 4 is "O dono do anel" (../roteiro-ep04-trocar.txt), the TROCAR path. The track joins, in
the script's order, the narrator's lines from narracao-ep04-narrador.wav, closing request
included; Renato's from narracao-ep04-renato.wav, in his own voice (Algenib); Ademir's from
narracao-ep04-ademir.wav, in the cobrador's voice from Part 3, heard in person (voz_ademir.py);
and the pauses the edit opens for the newspaper, the beats and the vote. Each line is found in
its recording by its words, and every cut, graphic and effect is anchored to a word of the
script, so the edit follows the voices again if they are re-aligned.

From Part 4 on, the part opens with its strongest moment and a recap of 6 to 8 s, not with the
12 s opening of Part 1 (../../../CLAUDE.md). The edit also uses the ideas taken from
@crimecarton for our story: the screen changes every 1 or 2 s, the lines show in balloons, each
new character gets a name tag, the clues get callouts and rings, the panel changes with the
story, the audience's comments come printed in the newspaper "A VOZ DO BAIRRO", there is one
light moment (Ademir's coffee) and the vote shows each option with its pros and cons.

Every framing keeps faces, hands, the phone and the ring out of the top quarter, where the panel
"A SUA PARTE · SUSPEITA" and the part's tag sit, and the phrases between 65% and 80% of the
height. The positions of balloons, rings and callouts follow the request's composition until
the drawings arrive, and are then set from each drawing.

timeline.json is the Instagram version. timeline-vertical.json, for TikTok and Shorts, moves the
top elements below TikTok's search bar and keeps the rest left of the buttons. Render each with
../../episodio-01/montagem/render_animatic.py --timeline.

--estimar DIR builds everything in DIR, with estimated word timings, a silent stand-in for each
voice that has no alignment yet and, for each drawing Codex has not delivered, its stand-in from
compor_cenas.py --rascunho: a draft to check the edit before the material exists.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
SERIE = EPISODE.parent
TOOLS = SERIE / 'episodio-01' / 'montagem'
sys.path.insert(0, str(TOOLS))
import graficos  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import unicodedata  # noqa: E402

# Instagram's and the vertical version's layouts, as in Part 3. TikTok's search bar covers the
# top 146 px: the HUD, the tags and the cards go below it. Its like, comment and share column
# covers the right of the lower half: there, the vertical version centres everything at
# x = 330, so nothing passes x = 590.
INSTAGRAM = {'name': 'timeline.json', 'art': '', 'hud_dy': 0, 'tag_y': 230, 'x': 360, 'width': 570, 'bars': 540}
VERTICAL = {'name': 'timeline-vertical.json', 'art': '-vertical', 'hud_dy': 67, 'tag_y': 297, 'x': 330, 'width': 520,
            'bars': 500}


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

SCRIPT = EPISODE / 'roteiro-ep04-trocar.txt'
VOICES = {'NARRADOR': (EPISODE / 'narracao-ep04-narrador.wav', HERE / 'alinhamento-narrador.json'),
          'RENATO': (EPISODE / 'narracao-ep04-renato.wav', HERE / 'alinhamento-renato.json'),
          # Ademir in the cobrador's voice, made by voz_ademir.py.
          'ADEMIR': (HERE / 'vozes' / 'ademir.wav', HERE / 'alinhamento-ademir.json')}
SOURCES = {'NARRADOR': EPISODE / 'narracao-ep04-narrador.txt', 'RENATO': EPISODE / 'narracao-ep04-renato.txt',
           'ADEMIR': EPISODE / 'narracao-ep04-ademir.txt'}
TEXT = {v: [w for w in path.read_text(encoding='utf-8').split() if norm(w)] for v, path in SOURCES.items()}
AUDIO = EPISODE / 'narracao-ep04.wav'
PART = 4
HANDLE = '@golpecartoon'
# Part 3's vote. Instagram tied at 4 to 4 on 01/11/2026, and the creator took TROCAR. The
# narration has both lines: "empate" uses "Deu empate. No desempate: trocar.", "maioria" uses
# "Vocês decidiram: trocar." if TikTok and Shorts give TROCAR the majority (then VOTE takes
# the real shares).
RESULTADO = 'empate'
VOTE = [('TROCAR', 50), ('DEIXAR', 50)]
EMPATE = 'Deu empate. No desempate: trocar.'
MAIORIA = 'Vocês decidiram: trocar.'
# Real comments on Part 3, as readers' letters (the long one without its swear word).
COMENTARIOS = ['Trocar.', 'Deixar.',
               '(…) só porque ajudou depois de arrependido faz diferença? Tem que deixar se lascar e ir '
               'proteger a família do cara.']
TAIL = 2.0
# Renato and Ademir talk beside Zinho, as loud as the narrator.
GAINS = {'RENATO': 0, 'ADEMIR': 0}
LEAD, TRAIL, SWITCH = .12, .22, .25
WHOOSH_PEAK = .36
ESTIMATE = False      # set by --estimar: the drawings not delivered yet come from their stand-ins


def find(voice, phrase_, after=0):
    words, target = [norm(w) for w in TEXT[voice]], [norm(w) for w in phrase_.split()]
    for i in range(after, len(words) - len(target) + 1):
        if words[i:i+len(target)] == target:
            return i
    raise ValueError(f'{phrase_!r} is not in the {voice} recording')


def read_script():
    # [(voice, text, first word, last word)] in the script's order. The recap's vote is split
    # off its line, so either version of it can be used.
    lines = []
    for raw in SCRIPT.read_text(encoding='utf-8').splitlines():
        if not raw.strip():
            continue
        voice, text = raw.split(': ', 1)
        parts = [text]
        if EMPATE in text:
            before = text.replace(EMPATE, '').strip()
            parts = [before, EMPATE if RESULTADO == 'empate' else MAIORIA]
        for part in parts:
            first = find(voice, part)
            lines.append((voice, part, first, first + len([w for w in part.split() if norm(w)]) - 1))
    return lines


LINES = read_script()
VOTO = EMPATE if RESULTADO == 'empate' else MAIORIA


def N(p, k=0):
    return 'NARRADOR', find('NARRADOR', p) + k


def R(p, k=0):
    return 'RENATO', find('RENATO', p) + k


def A(p, k=0):
    return 'ADEMIR', find('ADEMIR', p) + k


# Silence the edit opens after a word, in seconds. At a voice's last word before another voice,
# it is the silence between the two. With the real voices, the beats and the reading time of
# the newspaper and the options bring the part to about Part 3's length (2 min 13 s).
PAUSES = {
    N('o rosto.', 1): .8,                    # the cold open lands
    N('no perfil.', 1): .15,
    N(VOTO, len(VOTO.split()) - 1): 4.0,     # the newspaper, to read the comments
    N('pode cancelar.', 1): .6,              # the panel turns into the photo's clock
    N('numa cadeira.', 1): .3,
    R('Por que você veio?', 3): .6,
    N('anel da foto.', 2): .8,
    A('mesa da foto também.', 3): .3,
    N('sem pressa.', 1): .3,
    A('você fica.', 1): .9,                  # a beat, and then the coffee
    A('Acabei de passar.', 2): .6,           # nobody answers
    N('O Renato aceita.', 2): .25,
    R('se tiver.', 1): .9,
    N('carro do assalto.', 2): .8,
    N('esperava ouvir.', 1): .35,
    A('você preso.', 1): .9,
    A('até ele.', 1): .6,
    N('continua sendo.', 1): 1.0,
    N('a foto sair.', 2): 1.2,               # the clock ticks
    N('ficou com tudo.', 2): 3.8,            # option 1's pros and cons, time to read them
    N('Com você dentro.', 2): 3.8,           # option 2's
}
SWITCHES = {}


# Words per second of each voice in Part 3's recordings, pauses included: the narrator, the
# cobrador (Ademir's voice) and Renato. A draft's estimated timings keep these paces.
RATE = {'NARRADOR': 2.62, 'ADEMIR': 1.75, 'RENATO': 2.0}


def estimated_words(voice):
    # Rough timings for a voice that does not exist yet: longer words take longer, with pauses
    # at punctuation and between lines, scaled to the voice's pace in Part 3.
    t, words = .3, []
    ends = {e for v, _, _, e in LINES if v == voice}
    for i, w in enumerate(TEXT[voice]):
        d = .1 + .062*len(norm(w))
        words.append({'i': i, 'text': w, 'start': t, 'end': t + d})
        t += d + (.65 if i in ends else .42 if w[-1] in '.?:!' else .22 if w[-1] == ',' else .04)
    k = len(TEXT[voice])/RATE[voice]/t
    for w in words:
        w['start'], w['end'] = round(w['start']*k, 3), round(w['end']*k, 3)
    return words, t*k + .2


def load_words(estimate=None):
    words, stand_ins = {}, set()
    for voice, (audio, alignment) in VOICES.items():
        if estimate and not alignment.exists():
            est, duration = estimated_words(voice)
            audio = estimate / audio.name
            subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=24000:cl=mono',
                            '-t', f'{duration:.3f}', '-c:a', 'pcm_s16le', audio], check=True)
            words[voice] = (audio, est)
            stand_ins.add(voice)
        elif not alignment.exists():
            raise SystemExit(f'Falta {alignment.name}: alinhe a gravação com alinhar_narracao.py (README.md) '
                             'ou faça um rascunho com --estimar.')
        else:
            words[voice] = (audio, json.loads(alignment.read_text(encoding='utf-8'))['words'])
    for voice, (_, w) in words.items():
        if [norm(x['text']) for x in w] != [norm(x) for x in TEXT[voice]]:
            raise ValueError(f'{voice}: the alignment does not match {SOURCES[voice].name}')
    return words, stand_ins


def segments(words):
    """The track as pieces: ('voice', voice, first, last, src_start, src_end) or ('gap', seconds)."""
    runs = []
    for voice, _, first, end in LINES:
        if runs and runs[-1][0] == voice and runs[-1][2] == first - 1:
            runs[-1][2] = end
        else:
            runs.append([voice, first, end])
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
    files = {v: words[v][0] for v in VOICES}
    ref = None if 'NARRADOR' in stand_ins else loudness(files['NARRADOR'])
    gains = {v: 0 if v in stand_ins or ref is None or v == 'NARRADOR' else ref - loudness(files[v]) for v in VOICES}
    for v, g in GAINS.items():
        gains[v] += g
    order = list(VOICES)
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


def desenho(nome):
    """A drawing of this part, enlarged in ../, or its stand-in in a draft."""
    if (EPISODE / nome).exists():
        return nome
    if ESTIMATE:
        return f'montagem/rascunho/{nome}'
    raise FileNotFoundError(f'{nome}: o desenho do Codex ainda não chegou (use --estimar para um rascunho)')


def arte(nome):
    """An image compor_cenas.py made: a draft's, from the stand-ins, in a draft."""
    if ESTIMATE and (HERE / 'rascunho' / 'arte' / nome).exists():
        return f'montagem/rascunho/arte/{nome}'
    return f'montagem/arte/{nome}'


def art(asset, zoom=.05, **kw):
    return dict(kind='art', asset=asset, zoom=zoom, **kw)


def ticking(start, end, step=.5, gain=-15):
    return [sfx('tique.wav', start + step*k, gain) for k in range(int((end - start)/step))]


# Framings inside the earlier parts' drawings: left, top, right, bottom as fractions.
DOOR13 = [0.05, 0.0, 0.95, 0.9]          # Part 3's Zinho at the bus door, under the vote
# Where things are in this part's drawings, in the 720 × 1280 frame. Until the drawings come,
# they follow the request's composition (faces between 32% and 42% of the height).
HEAD = 450           # a face's height in the frame
CARD_Y = 880         # name tags, below the faces and above the captions


def balloon(text, start, end, x, tail, y=None, width=440, L=None):
    # A line in a balloon over the speaker's head, below the tag.
    y = y if y is not None else (360 if L is None or not L['hud_dy'] else 405)
    return {'type': 'balloon', 'start': round(start, 2), 'end': round(end, 2), 'text': text, 'x': x, 'y': y,
            'tail': {'x': tail[0], 'y': tail[1]}, 'width': width}


def tag(text, start, end, y, color='yellow', x=None, size=21):
    el = {'type': 'tag', 'start': round(start, 2), 'end': round(end, 2), 'text': text, 'y': y, 'color': color, 'size': size}
    if x is not None:
        el['x'] = x
    return el


def callout(text, start, end, x, y, target, color='yellow'):
    return {'type': 'callout', 'start': round(start, 2), 'end': round(end, 2), 'text': text, 'x': x, 'y': y,
            'target': {'x': target[0], 'y': target[1]}, 'color': color}


def ring(start, end, x, y, r=56, color='red'):
    return {'type': 'ring', 'start': round(start, 2), 'end': round(end, 2), 'x': x, 'y': y, 'r': r, 'color': color}


def nametag(name, sub, start, end, x, color='yellow'):
    return {'type': 'nametag', 'start': round(start, 2), 'end': round(end, 2), 'name': name, 'sub': sub,
            'x': x, 'y': CARD_Y, 'color': color}


def pop(text, start, end, x, y, size=56, color='yellow', angle=-8, shake=False):
    el = {'type': 'pop', 'start': round(start, 2), 'end': round(end, 2), 'text': text, 'x': x, 'y': y, 'size': size,
          'color': color, 'angle': angle}
    if shake:
        el['shake'] = True
    return el


def hud(start, end, label_, value, color, dy, shake=False):
    v = {'at': round(start, 2), 'text': value, 'color': color}
    if shake:
        v['shake'] = True
    return {'type': 'hud', 'start': round(start, 2), 'end': round(end, 2), 'label': label_, 'dy': dy,
            'values': [v], 'stars': [{'at': round(start, 2), 'count': 5, 'step': 0}]}


def build(ed):
    s, e, cut, L = ed.s, ed.e, ed.cut, ed.L
    END, x = ed.END, L['x']
    v = bool(L['hud_dy'])                       # the vertical version
    right = 470 if v else 540                   # labels on the right stay left of TikTok's buttons
    story = cut(N('Mas você não'))
    p3 = '../episodio-03/'
    plan = [
        # The cold open: the part's strongest moment, with the phrase from the first frame.
        ('frio', 0, art(desenho('cena-01-passo-na-luz.png'), .05)),
        # The recap, in about 8 s: the profile, Renato caught, the vote and the newspaper.
        ('perfil', cut(N('Chegou agora?')), art(arte(f"perfil{L['art']}.png"), .03, direction='out')),
        ('pego', cut(N('O Renato foi')), art(arte('lembranca-parte3.png'), .02)),
        ('votos', cut(N(VOTO)), art(p3 + 'cena-13-decisao.png', .03, crop=DOOR13, direction='out', brightness=.35)),
        # The plan in the bus.
        ('onibus', story, art(desenho('cena-02-onibus-decidido.png'))),
        ('agendar', cut(N('No ônibus, você')), art(arte('tela-agendar.png'), .04)),
        # The junkyard.
        ('portao', cut(N('Duas e cinquenta')), art(desenho('cena-04-portao-aberto.png'), .04)),
        ('chegada', cut(N('Lá dentro, uma')), art(desenho('cena-05-chegada.png'), .04, direction='out')),
        ('renato', cut(R('Você veio?')), art(desenho('cena-06-renato-amarrado.png'))),
        ('ademir', cut(N('Da sombra sai')), art(desenho('cena-07-ademir-sai-da-sombra.png'), .04, direction='out')),
        ('anel', cut(N('No dedo, o')), art(desenho('cena-08-anel-canivete.png'), .07)),
        ('mesa', cut(A('Pode me chamar')), art(desenho('cena-09-mesa-da-foto.png'))),
        ('corda', cut(N('Ele corta a')), art(desenho('cena-10-corda.png'), .06)),
        ('fica', cut(A('Combinado é combinado.')), art(desenho('cena-11-voce-fica.png'), .04, direction='out')),
        # The light moment: the coffee.
        ('cafe', cut(A('Aceita um café?')), art(desenho('cena-12-cafe.png'))),
        ('aceita', cut(N('Você não aceita.')), art(desenho('cena-13-renato-aceita.png'))),
        # The driver and the turn.
        ('isqueiro', cut(N('No fundo do')), art(desenho('cena-14-isqueiro.png'), .04)),
        ('motorista', cut(N('Você conhece aquele')), art(desenho('cena-15-motorista.png'), .06)),
        ('inclina', cut(N('E aí o')), art(desenho('cena-16-ademir-inclina.png'), .05)),
        ('parceiro', cut(A('O seu parceiro')), art(desenho('cena-17-parceiro.png'), .04, direction='out')),
        ('ombro', cut(A('E você vai')), art(desenho('cena-18-mao-no-ombro.png'), .05)),
        ('isca', cut(N('Você nunca foi')), art(desenho('cena-19-isca.png'), .06)),
        ('celular', cut(N('O celular vibra')), art(arte('tela-0313.png'), .05)),
        # The vote: each option with its scene, then both.
        ('cancelar', cut(N('Se você cancelar,')), art(desenho('cena-21-opcao-cancelar.png'), .03)),
        ('enviar', cut(N('Se deixar sair,')), art(desenho('cena-22-opcao-enviar.png'), .03)),
        ('escolha', cut(N('Cancelar ou enviar?')), art(arte(f"opcoes{L['art']}.png"), .02, direction='out')),
    ]
    plan.sort(key=lambda item: item[1])
    used = [f['asset'] for _, _, f in plan if f.get('asset')]
    repeated = sorted({a for a in used if used.count(a) > 1})
    if repeated:
        raise ValueError(f'drawings used more than once: {repeated}')
    AT = {name: t for name, t, _ in plan}
    nxt = {name: (plan[k+1][1] if k + 1 < len(plan) else END) for k, (name, _, _) in enumerate(plan)}
    scenes = [{'start': t, 'end': nxt[name], **fields} for name, t, fields in plan]
    jornal_at = round(e(N(VOTO, len(VOTO.split()) - 1)) + .15, 2)
    winner = max(VOTE, key=lambda o: o[1])[0]
    clock = s(N('Só você pode'))
    graphics = [
        # ---- the cold open
        {'type': 'tag', 'start': .15, 'end': story, 'text': f'PARTE {PART}', 'y': L['tag_y'], 'x': 112, 'size': 32},
        {'type': 'vignette', 'start': 0, 'end': AT['perfil'], 'color': 'alert', 'strength': .5},
        phrase(0, AT['perfil'], 900, [label('QUEM SEQUESTROU O SEU AMIGO', 0), line('VAI MOSTRAR', 0),
                                      line('O ROSTO.', s(N('o rosto.')), 'yellow', shake=True)], 76, x),
        # ---- the recap
        phrase(AT['perfil'] + .05, AT['pego'], 790, [line('CHEGOU AGORA?', s(N('Chegou agora?')), 'yellow', size=64),
                                                     line('AS PARTES 1, 2 E 3', s(N('As outras partes')), size=52),
                                                     line('TÃO NO PERFIL', s(N('no perfil.')), size=52)], 72, x),
        {'type': 'pointer', 'start': round(s(N('no perfil.')), 2), 'end': AT['pego'], 'y': 940, 'x': x, 'text': HANDLE},
        {'type': 'polaroid', 'start': AT['pego'] + .05, 'end': AT['votos'], 'image': 'episodio-03/cena-04-mao-anel.png',
         'focus': [0.0, 0.18, 1.0, 0.62], 'caption': 'PARTE 3', 'sub': 'o muro', 'x': x, 'y': 560, 'size': 300, 'angle': -5},
        phrase(AT['pego'] + .05, AT['votos'], 900, [line('O RENATO FOI PEGO', s(N('O Renato foi')), size=52),
                                                    line('NO SEU LUGAR.', s(N('no seu lugar.')), 'yellow')], 66, x),
        {'type': 'bars', 'start': AT['votos'] + .05, 'end': jornal_at, 'y': 500, 'x': x, 'width': L['bars'],
         'title': f'PARTE {PART - 1} · VOCÊS VOTARAM', 'title_at': round(s(N(VOTO)), 2),
         'items': [{'label': n, 'pct': pct, 'at': round(s(N(VOTO)) + .1 + .15*k, 2),
                    'winner': RESULTADO != 'empate' and n == winner} for k, (n, pct) in enumerate(VOTE)]},
    ]
    if RESULTADO == 'empate':
        graphics += [
            {'type': 'stamp', 'start': round(s(N('Deu empate.', 1)) - .02, 2), 'end': round(s(N('No desempate:')), 2),
             'text': 'EMPATE', 'y': 860, 'x': x, 'angle': -7, 'color': 'white'},
            phrase(s(N('No desempate:')) - .02, jornal_at, 770, [label('NO DESEMPATE', s(N('No desempate:')))], 40, x),
            {'type': 'stamp', 'start': round(s(N('desempate: trocar.', 1)) - .02, 2), 'end': jornal_at, 'text': winner,
             'y': 860, 'x': x, 'angle': -7, 'color': 'yellow', 'filled': True},
        ]
    else:
        graphics.append({'type': 'stamp', 'start': round(s(N('decidiram: trocar.', 1)) - .02, 2), 'end': jornal_at,
                         'text': winner, 'y': 860, 'x': x, 'angle': -7, 'color': 'yellow', 'filled': True})
    graphics += [
        # The comments on Part 3, printed in the newspaper.
        {'type': 'jornal', 'start': jornal_at, 'end': story, 'y': 340 if v else 300, 'x': x, 'width': 500 if v else 560,
         'title': 'A VOZ DO BAIRRO', 'sub': f'o que vocês comentaram na parte {PART - 1}',
         'items': [{'text': c, 'at': round(jornal_at + .3 + .5*k, 2)} for k, c in enumerate(COMENTARIOS)]},
        # ---- the panel: their share, then the photo's clock
        hud(story, clock, 'A SUA PARTE', 'R$ 0', 'red', L['hud_dy']),
        hud(clock, s(A('O seu parceiro')), 'A FOTO SAI ÀS', '3:15', 'yellow', L['hud_dy']),
        hud(s(A('O seu parceiro')), s(N('Você nunca foi')), 'A SUA PARTE', 'R$ 0', 'red', L['hud_dy'], shake=True),
        hud(s(N('Você nunca foi')), s(N('Três e treze.')), 'A FOTO SAI ÀS', '3:15', 'yellow', L['hud_dy']),
        hud(s(N('Três e treze.')), AT['cancelar'], 'FALTAM', '2 MIN', 'red', L['hud_dy'], shake=True),
        tag('O PLANO · A FOTO', story, AT['portao'], L['tag_y']),
        tag('A TROCA · 02:59', AT['portao'], AT['ademir'], L['tag_y']),
        tag('O DONO DO ANEL', AT['ademir'], AT['isqueiro'], L['tag_y']),
        tag('O MOTORISTA', AT['isqueiro'], AT['inclina'], L['tag_y']),
        tag('A VIRADA', AT['inclina'], AT['celular'], L['tag_y']),
        tag('O RELÓGIO · 03:13', AT['celular'], AT['cancelar'], L['tag_y'], 'alert'),
        # ---- the bus
        phrase(story + .05, AT['agendar'], 900, [line('VOCÊ NÃO VAI', s(N('Mas você não'))),
                                                 line('DE MÃOS VAZIAS.', s(N('de mãos vazias.')), 'yellow')], 62, x),
        callout('PARA O JORNAL', s(N('para o jornal')), clock, 470 if v else 520, 340 if v else 330, (390, 425), 'white'),
        callout('A FOTO DA DIVISÃO', s(N('a foto da divisão.')), clock, 190, 960, (381, 560)),
        callout('SÓ VOCÊ CANCELA', clock, AT['portao'], right, 980, (360, 823), 'alert'),
        # ---- the junkyard
        phrase(AT['portao'] + .05, AT['chegada'], 900, [line('02:59', s(N('Duas e cinquenta')), 'yellow', size=90),
                                                        line('O PORTÃO ESTÁ ABERTO.', s(N('O portão do')), size=44)], 70, x),
        phrase(AT['chegada'] + .05, AT['renato'], 900, [line('UMA LÂMPADA SÓ.', s(N('uma lâmpada só.')), size=48),
                                                        line('E O RENATO,', s(N('E o Renato,')), 'yellow'),
                                                        line('AMARRADO.', s(N('amarrado numa cadeira.')), 'red')], 62, x),
        ring(s(N('E o Renato,')), AT['renato'], 380, 560, 56),
        balloon('Você veio? Por que você veio?', s(R('Você veio?')), AT['ademir'], 330, (360, HEAD - 20), L=L),
        nametag('RENATO', 'seu amigo de infância · pego no seu lugar', s(R('Você veio?')) + .4, AT['ademir'], x),
        # ---- the man with the ring
        phrase(AT['ademir'] + .05, s(N('cabelo branco,')) - .05, 900, [line('DA SOMBRA,', s(N('Da sombra sai'))),
                                                                       line('UM HOMEM.', s(N('um homem de')), 'yellow')],
               70, x),
        callout('CABELO BRANCO', s(N('cabelo branco,')), AT['anel'], 200, 340 if v else 330, (360, HEAD - 10)),
        callout('JAQUETA DE COURO', s(N('jaqueta de couro.')), AT['anel'], 200, 900, (370, 650), 'white'),
        ring(s(N('o anel da')), AT['mesa'], 400, 640, 50),
        callout('O ANEL DA FOTO', s(N('anel da foto.')), AT['mesa'], 200, 900, (395, 650)),
        balloon('Pode me chamar de Ademir. O São Jorge é meu.', s(A('Pode me chamar')), s(A('E aquela mesa')),
                330, (290, HEAD - 20), L=L),
        balloon('E aquela mesa da foto também.', s(A('E aquela mesa')), AT['corda'], 330, (290, HEAD - 20), L=L),
        nametag('ADEMIR', 'dono do Ferro-Velho São Jorge', s(A('de Ademir.', 1)) + .2, AT['corda'], x, 'alert'),
        callout('A MESA DA FOTO', s(A('aquela mesa da')), AT['corda'], 470, 990, (470, 740)),
        pop('ZÁS', s(N('com um canivete,')), AT['fica'], 480, 560, 64, 'white', 8),
        phrase(s(N('sem pressa.')) - .05, AT['fica'], 900, [line('SEM PRESSA.', s(N('sem pressa.')), 'yellow')], 72, x),
        balloon('Combinado é combinado. Ele sai, você fica.', s(A('Combinado é combinado.')), AT['cafe'], 360,
                (360, HEAD - 20), L=L),
        tag('ELE SAI', s(A('Ele sai,')), AT['cafe'], 700, 'green', 190, 24),
        tag('VOCÊ FICA', s(A('você fica.')), AT['cafe'], 700, 'alert', right, 24),
        # ---- the coffee
        balloon('Aceita um café? Acabei de passar.', s(A('Aceita um café?')), AT['aceita'], 330, (330, HEAD - 20), L=L),
        tag('NÃO', s(N('não aceita.')), AT['isqueiro'], 660, 'alert', 210, 26),
        tag('SIM', s(N('O Renato aceita.', 2)), AT['isqueiro'], 660, 'green', 470, 26),
        balloon('Com açúcar, se tiver.', s(R('Com açúcar,')), AT['isqueiro'], 400, (465, HEAD - 20), width=300, L=L),
        pop('SLURP', s(R('se tiver.')) + .3, AT['isqueiro'], 500, 600, 44, 'white', 6),
        # ---- the driver
        ring(s(N('um homem acende')), AT['motorista'], 360, 560, 70),
        pop('CLIC', s(N('acende um cigarro.')), AT['motorista'], 380, 470, 50, 'yellow', -6),
        phrase(s(N('um homem acende')) - .05, AT['motorista'], 900, [line('UM HOMEM', s(N('um homem acende'))),
                                                                     line('ACENDE UM CIGARRO.', s(N('acende um cigarro.')),
                                                                          'yellow', size=48)], 60, x),
        {'type': 'vignette', 'start': AT['motorista'], 'end': AT['inclina'], 'color': 'alert', 'strength': .6},
        phrase(AT['motorista'] + .05, s(N('Foi ele que')) - .05, 900, [line('VOCÊ CONHECE', s(N('Você conhece aquele'))),
                                                                       line('ESSE ROSTO.', s(N('aquele rosto.')), 'yellow')],
               70, x),
        nametag('O MOTORISTA', 'dirigiu o carro do assalto', s(N('Foi ele que')), AT['inclina'], x, 'alert'),
        # ---- the turn
        phrase(AT['inclina'] + .05, s(A('Eu não quero')) - .05, 900, [
            label('A ÚLTIMA COISA QUE', s(N('a última coisa'))),
            line('VOCÊ ESPERAVA', s(N('você esperava ouvir.'))),
            line('OUVIR.', s(N('esperava ouvir.', 1)), 'yellow')], 66, x),
        balloon('Eu não quero você preso.', s(A('Eu não quero')), AT['parceiro'], 360, (360, HEAD - 30), L=L),
        phrase(AT['parceiro'] + .05, s(A('Com a minha')) - .05, 900, [line('“SUMIU COM OS', s(A('O seu parceiro'))),
                                                                       line('10 MILHÕES.”', s(A('dez milhões.')), 'green')],
               70, x),
        phrase(s(A('Com a minha')) - .05, AT['ombro'], 900, [line('“COM A MINHA', s(A('Com a minha'))),
                                                             line('PARTE TAMBÉM.”', s(A('parte também.')), 'yellow')], 62, x),
        callout('AS BOLSAS DA DIVISÃO', s(A('Com a minha')), AT['ombro'], 200, 340 if v else 330, (420, 620), 'white'),
        balloon('E você vai me levar até ele.', s(A('E você vai')), AT['isca'], 400, (470, HEAD - 20), width=320, L=L),
        callout('A MESMA MÃO', s(A('me levar até')), AT['isca'], 200, 900, (330, 600)),
        {'type': 'vignette', 'start': AT['isca'], 'end': AT['celular'], 'color': 'alert', 'strength': .7},
        phrase(AT['isca'] + .05, AT['celular'], 900, [label('VOCÊ NUNCA FOI O CULPADO.', s(N('Você nunca foi'))),
                                                      line('E CONTINUA SENDO.', s(N('E continua sendo.')), 'red')], 56, x),
        {'type': 'stamp', 'start': round(s(N('Foi a isca.', 2)) - .02, 2), 'end': AT['celular'], 'text': 'ISCA', 'y': 740,
         'x': x, 'angle': -7, 'color': 'red', 'filled': True},
        # ---- the clock
        pop('VRRR', s(N('celular vibra')), s(N('Três e treze.')), 200, 600, 56, 'white', -6, shake=True),
        phrase(s(N('Faltam dois minutos')) - .05, AT['cancelar'], 960, [
            line('FALTAM 2 MINUTOS', s(N('Faltam dois minutos')), 'red', size=52),
            line('PARA A FOTO SAIR.', s(N('para a foto sair.')), size=44)], 60, x),
        # ---- the vote, illustrated: each option with its pros and cons
        tag('OPÇÃO 1 · CANCELAR', AT['cancelar'] + .05, AT['enviar'], 360, 'white', x, 24),
        tag('− VIRA SÓCIO DE UM SEQUESTRADOR', s(N('vira sócio do')), AT['enviar'], 920, 'alert', x, 22),
        tag('+ ACHA O PARCEIRO COM O ADEMIR', s(N('contra o parceiro')), AT['enviar'], 820, 'green', x, 22),
        tag('+ CHANCE DE PEGAR A SUA PARTE', e(N('ficou com tudo.', 2)) + .3, AT['enviar'], 870, 'green', x, 22),
        tag('− CONTINUA SENDO A ISCA', e(N('ficou com tudo.', 2)) + .9, AT['enviar'], 970, 'alert', x, 22),
        tag('OPÇÃO 2 · ENVIAR', AT['enviar'] + .05, AT['escolha'], 360, 'white', x, 24),
        tag('+ O ROSTO DO ADEMIR NO JORNAL', s(N('a foto chega')), AT['escolha'], 820, 'green', x, 22),
        tag('− A POLÍCIA TE ACHA COM ELES', s(N('a polícia chega')), AT['escolha'], 920, 'alert', x, 22),
        tag('+ A FOTO VIRA PROVA', e(N('Com você dentro.', 2)) + .3, AT['escolha'], 870, 'green', x, 22),
        tag('− A SUSPEITA SOBE', e(N('Com você dentro.', 2)) + .9, AT['escolha'], 970, 'alert', x, 22),
        phrase(AT['escolha'], END, 585, [line('CANCELAR', s(N('Cancelar ou enviar?'))),
                                         line('OU ENVIAR?', s(N('ou enviar?', 1)), 'yellow')], 76, x),
        # CANCELAR is a long word: in the vertical version the pair moves a little left, so ENVIAR
        # stays clear of TikTok's buttons.
        {'type': 'buttons', 'start': round(s(N('Comenta uma palavra')) - .05, 2), 'end': END, 'y': 800,
         'x': x - (20 if v else 0),
         'prompt': 'COMENTA UMA PALAVRA', 'prompt_at': round(s(N('Comenta uma palavra')), 2),
         'items': [{'text': 'CANCELAR', 'at': round(s(N('uma palavra só.', 1)), 2), 'style': 'yellow'},
                   {'text': 'ENVIAR', 'at': round(s(N('uma palavra só.', 2)), 2), 'style': 'white'}]},
        {'type': 'box', 'start': round(s(N('O que a maioria')), 2), 'end': END, 'y': 940, 'x': x,
         'title': f'PARTE {PART + 1}', 'sub': 'a maioria decide o próximo passo'},
    ]
    effects = [
        *[sfx('whoosh.wav', AT[n] - WHOOSH_PEAK, -2) for n in ('perfil', 'votos', 'onibus', 'portao', 'ademir', 'cafe',
                                                               'isqueiro', 'inclina', 'isca', 'celular', 'cancelar',
                                                               'escolha')],
        sfx('impacto.wav', s(N('o rosto.')) - .04, -5),
        sfx('pop.wav', s(N('no perfil.')), -10),
        *[sfx('tique.wav', s(N(VOTO)) + .1 + .1*k, -20) for k in range(8)],
        sfx('impacto.wav', s(N(VOTO, len(VOTO.split()) - 1)) - .04, -5),
        sfx('notificacao.wav', s(N('agenda uma mensagem')), -12),
        sfx('passos.wav', s(N('O portão do')), -12),
        sfx('porta-abre.wav', s(N('está aberto.')), -12),
        sfx('impacto.wav', s(N('Da sombra sai')) - .04, -6),
        sfx('impacto-suave.wav', s(N('anel da foto.')) - .04, -8),
        sfx('pop.wav', s(A('de Ademir.', 1)) + .2, -10),
        sfx('impacto-suave.wav', s(N('com um canivete,')) - .04, -7),
        sfx('pop.wav', s(N('não aceita.')), -10),
        sfx('pop.wav', s(N('O Renato aceita.', 2)), -10),
        sfx('interruptor.wav', s(N('acende um cigarro.')), -10),
        sfx('impacto.wav', s(N('Foi ele que')) - .04, -5),
        sfx('impacto.wav', s(A('Eu não quero')) - .04, -6),
        sfx('impacto.wav', s(N('Foi a isca.', 2)) - .04, -5),
        sfx('vibracao.wav', s(N('celular vibra')) - .1, -8),
        *ticking(s(N('Três e treze.')), e(N('a foto sair.', 2)) + .6),
        *[sfx('pop.wav', t, -14) for t in (s(N('vira sócio do')), s(N('contra o parceiro')), s(N('a foto chega')),
                                          s(N('a polícia chega')))],
        *[sfx('pop.wav', t, -10) for t in (s(N('uma palavra só.', 1)), s(N('uma palavra só.', 2)), s(N('O que a maioria')))],
    ]
    k = L['width']/INSTAGRAM['width']
    for g in graphics if k != 1 else []:
        if g['type'] == 'phrase':
            g['size'] = int(g['size']*k)
            for ln in g['lines']:
                if 'size' in ln:
                    ln['size'] = int(ln['size']*k)
    return scenes, graphics, effects


def main():
    global ESTIMATE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--estimar', type=Path, metavar='DIR', help='build a draft from estimated timings into DIR')
    args = parser.parse_args()
    ESTIMATE = bool(args.estimar)
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
                    'alignment': [str(VOICES[v][1].relative_to(SERIE)) for v in VOICES],
                    'audio': str(audio) if args.estimar else audio.name, 'tail': TAIL,
                    'scenes': scenes, 'graphics': graphics, 'sfx': effects, 'captions': [],
                    'effects': ['../../episodio-02/montagem/efeitos']}
        if args.estimar:
            for sc in scenes:
                if 'asset' in sc:
                    sc['asset'] = str((EPISODE / sc['asset']).resolve())
            timeline['effects'] = [str((HERE / d).resolve()) for d in timeline['effects']]
        (out / layout['name']).write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f"{layout['name']}: {len(scenes)} scenes, {len(graphics)} graphics, {len(effects)} sound effects, ends at {end}s")
    print(f'{audio.name}: {length}s of voice; ' + ('estimated: ' + ', '.join(sorted(stand_ins)) if stand_ins else
                                                    'gains ' + ', '.join(f'{v} {g:+.1f} dB' for v, g in gains.items())))


if __name__ == '__main__':
    main()
