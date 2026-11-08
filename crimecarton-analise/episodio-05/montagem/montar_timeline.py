#!/usr/bin/env python3
"""Build Part 5's narration track and its two timelines from the word alignments.

Part 5 is "A divisão" (../roteiro-ep05-cancelar.txt), the CANCELAR path. The track joins, in the
script's order, the narrator's lines from narracao-ep05-narrador.wav, closing request included;
Ademir's from narracao-ep05-ademir.wav, in the cobrador's voice from Part 3 heard in person
(vozes/ademir.wav, made by ../../episodio-04/montagem/voz_ademir.py); Renato's audio message from
narracao-ep05-renato.wav, in his own voice (Algenib); Toninho's, the driver, from
narracao-ep05-toninho.wav (Orus); and the pauses the edit opens for the newspaper, the beats and
the vote. Each line is found in its recording by its words, and every cut, graphic and effect is
anchored to a word of the script, so the edit follows the voices again if they are re-aligned.

The part opens as the creator set on 06/11/2026 (../../../CLAUDE.md): first the usual opening,
exactly as in Part 3's video (the three fixed lines in Part 1's voice, VINHETA, matched to this
narrator by igualar_vozes.py, over the backpack art with the R$ 10.000.000 counter, and the black
card with the five suspicion stars); then the part's strongest moment, with its phrase from the
first frame; then a recap of about 8 s. The edit uses the ideas taken from @crimecarton for our
story: the screen changes every 1 or 2 s, the lines show in balloons, each new character gets a
name tag, the clues get callouts and rings, the panel changes with the story, the audience's
comments come printed in the newspaper "A VOZ DO BAIRRO", there is one light moment (Renato's
audio and Dona Célia's cake) and the vote shows each option with its pros and cons.

Every framing keeps faces, hands, the phone and the ring out of the top quarter, where the panel
"A SUA PARTE · SUSPEITA" and the part's tag sit, and the phrases between 65% and 80% of the
height. The positions of balloons, rings and callouts are set from each of Codex's drawings.

timeline.json is the Instagram version. timeline-vertical.json, for TikTok and Shorts, moves the
top elements below TikTok's search bar and keeps the rest left of the buttons. Render each with
../../episodio-01/montagem/render_animatic.py --timeline.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import sys
import unicodedata

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
SERIE = EPISODE.parent
TOOLS = SERIE / 'episodio-01' / 'montagem'
sys.path.insert(0, str(TOOLS))
import graficos  # noqa: E402

# Instagram's and the vertical version's layouts, as in Parts 3 and 4. TikTok's search bar covers
# the top 146 px: the HUD, the tags and the cards go below it. Its like, comment and share column
# covers the right of the lower half: there, the vertical version centres everything at x = 330,
# so nothing passes x = 590.
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
    # Phrase lines and tags must fit the layout's width.
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
        if g['type'] == 'tag':
            width = graficos.tag_sprite(g['text'], g.get('color', 'yellow'), g.get('size', 21)).width
            if width > limit + 40:
                wide.append((g['text'], g['size'], width))
    return wide


SCRIPT = EPISODE / 'roteiro-ep05-cancelar.txt'
VOICES = {'VINHETA': (HERE / 'vozes' / 'vinheta.wav', TOOLS / 'alinhamento-narracao.json'),
          'NARRADOR': (EPISODE / 'narracao-ep05-narrador.wav', HERE / 'alinhamento-narrador.json'),
          # Ademir in the cobrador's voice, made by voz_ademir.py.
          'ADEMIR': (HERE / 'vozes' / 'ademir.wav', HERE / 'alinhamento-ademir.json'),
          'RENATO': (EPISODE / 'narracao-ep05-renato.wav', HERE / 'alinhamento-renato.json'),
          'TONINHO': (EPISODE / 'narracao-ep05-toninho.wav', HERE / 'alinhamento-toninho.json')}
SOURCES = {'VINHETA': SERIE / 'narracao-ep01-zinho.txt', 'NARRADOR': EPISODE / 'narracao-ep05-narrador.txt',
           'ADEMIR': EPISODE / 'narracao-ep05-ademir.txt', 'RENATO': EPISODE / 'narracao-ep05-renato.txt',
           'TONINHO': EPISODE / 'narracao-ep05-toninho.txt'}
TEXT = {v: [w for w in path.read_text(encoding='utf-8').split() if norm(w)] for v, path in SOURCES.items()}
AUDIO = EPISODE / 'narracao-ep05.wav'
PART = 5
HANDLE = '@golpecartoon'
# Part 4's vote: CANCELAR 5 to 0 on Instagram, in the screen recording of 07/11/2026.
VOTE = [('CANCELAR', 100), ('ENVIAR', 0)]
VOTO = 'Vocês decidiram: cancelar.'
# Real comments on Part 4, as readers' letters (the long one as it starts).
COMENTARIOS = ['Cancelar.', 'Cancelar e se livra da polícia.',
               'Cancelar. Você ajudando ou não o Ademir, essa foto atrai problemas para todos.']
TAIL = 2.0
# Everyone talks beside Zinho, as loud as the narrator; Renato's audio too.
GAINS = {'VINHETA': 0, 'ADEMIR': 0, 'RENATO': 0, 'TONINHO': 0}
LEAD, TRAIL, SWITCH = .12, .22, .25
WHOOSH_PEAK = .36


def find(voice, phrase_, after=0):
    words, target = [norm(w) for w in TEXT[voice]], [norm(w) for w in phrase_.split()]
    for i in range(after, len(words) - len(target) + 1):
        if words[i:i+len(target)] == target:
            return i
    raise ValueError(f'{phrase_!r} is not in the {voice} recording')


def read_script():
    # [(voice, text, first word, last word)] in the script's order.
    lines = []
    for raw in SCRIPT.read_text(encoding='utf-8').splitlines():
        if not raw.strip():
            continue
        voice, text = raw.split(': ', 1)
        first = find(voice, text)
        lines.append((voice, text, first, first + len([w for w in text.split() if norm(w)]) - 1))
    return lines


LINES = read_script()


def V(i):
    # A word of the opening's three lines, by its place in Part 1's narration.
    return 'VINHETA', i


def N(p, k=0):
    return 'NARRADOR', find('NARRADOR', p) + k


def A(p, k=0):
    return 'ADEMIR', find('ADEMIR', p) + k


def R(p, k=0):
    return 'RENATO', find('RENATO', p) + k


def T(p, k=0):
    return 'TONINHO', find('TONINHO', p) + k


# Silence the edit opens after a word, in seconds. At a voice's last word before another voice,
# it is the silence between the two. The beats and the reading time of the newspaper and the
# options bring the part to about Part 4's length (2 min 16 s).
PAUSES = {
    V(16): .35,                              # the stars, before the cold open, as in Part 3
    N('roupa velha.', 1): .6,                # the cold open lands
    N('no perfil.', 1): .15,
    N(VOTO, 2): 4.0,                         # the newspaper, to read the comments
    N('aperta cancelar.', 1): .3,
    N('não sai.', 1): .5,
    A('Sócio.'): .35,
    N('mão. Você aperta.', 2): .4,
    A('minha frente.', 1): .3,
    N('Você apaga.', 1): .4,                 # the stamp, before the trash
    N('lixeira do celular.', 2): .6,
    A('te leva.', 1): .2,
    A('a caçada.', 1): .5,
    N('carro do assalto.', 2): .6,
    N('áudio do Renato.', 2): .3,
    R('metade é sua.', 2): .6,
    N('quase ri.', 1): .9,                   # the light moment, before the turn
    N('desliga o rádio.', 2): .3,
    N('posto fechado.', 1): .3,
    N('olhar pra você.', 2): .4,
    T('da divisão?', 1): .4,
    T('O Ademir.', 1): .7,                   # the turn lands
    T('roupa velha.', 1): .6,
    N('aperta gravar.', 1): .5,
    T('te levou.', 1): .3,
    T('nele também.', 1): .5,
    N('te roubar.', 1): 1.0,
    T('duas bolsas.', 1): .4,
    T('ele tá.', 1): .2,
    T('chego perto.', 1): .3,
    T('do Ademir,', 1): .15,
    T('a gente divide.', 2): .8,
    N('dinheiro embora.', 1): 3.8,           # option 1's pros and cons, time to read them
    N('paga por isso.', 2): 3.8,             # option 2's
}
SWITCHES = {}


def load_words():
    words = {}
    for voice, (audio, alignment) in VOICES.items():
        if not alignment.exists():
            raise SystemExit(f'Falta {alignment.name}: alinhe a gravação com alinhar_narracao.py (README.md).')
        words[voice] = (audio, json.loads(alignment.read_text(encoding='utf-8'))['words'])
    for voice, (_, w) in words.items():
        if [norm(x['text']) for x in w] != [norm(x) for x in TEXT[voice]]:
            raise ValueError(f'{voice}: the alignment does not match {SOURCES[voice].name}')
    return words


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


def join(words, pieces, output):
    files = {v: words[v][0] for v in VOICES}
    ref = loudness(files['NARRADOR'])
    gains = {v: 0 if v == 'NARRADOR' else ref - loudness(files[v]) for v in VOICES}
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
    """A drawing of this part, enlarged in ../."""
    if not (EPISODE / nome).exists():
        raise FileNotFoundError(f'{nome}: o desenho ampliado ainda não está em {EPISODE.name}/')
    return nome


def arte(nome):
    """An image compor_cenas.py made."""
    if not (HERE / 'arte' / nome).exists():
        raise FileNotFoundError(f'arte/{nome}: rode compor_cenas.py')
    return f'montagem/arte/{nome}'


def art(asset, zoom=.05, **kw):
    return dict(kind='art', asset=asset, zoom=zoom, **kw)


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


def nametag(name, sub, start, end, x, color='yellow', y=CARD_Y):
    return {'type': 'nametag', 'start': round(start, 2), 'end': round(end, 2), 'name': name, 'sub': sub,
            'x': x, 'y': y, 'color': color}


def pop(text, start, end, x, y, size=56, color='yellow', angle=-8, shake=False):
    el = {'type': 'pop', 'start': round(start, 2), 'end': round(end, 2), 'text': text, 'x': x, 'y': y, 'size': size,
          'color': color, 'angle': angle}
    if shake:
        el['shake'] = True
    return el


def stamp(text, start, end, y, x, color='red', filled=True, angle=-7):
    return {'type': 'stamp', 'start': round(start, 2), 'end': round(end, 2), 'text': text, 'y': y, 'x': x,
            'angle': angle, 'color': color, 'filled': filled}


def polaroid(image, focus, caption, sub, start, end, x, y, size=300, angle=-5):
    return {'type': 'polaroid', 'start': round(start, 2), 'end': round(end, 2), 'image': image, 'focus': focus,
            'caption': caption, 'sub': sub, 'x': x, 'y': y, 'size': size, 'angle': angle}


def hud(start, end, label_, value, color, dy, shake=False):
    v = {'at': round(start, 2), 'text': value, 'color': color}
    if shake:
        v['shake'] = True
    return {'type': 'hud', 'start': round(start, 2), 'end': round(end, 2), 'label': label_, 'dy': dy,
            'values': [v], 'stars': [{'at': round(start, 2), 'count': 5, 'step': 0}]}


# Where the new screens' details land in the 720 × 1280 frame, measured on the composed scenes.
BOTAO_CANCELAR = (405, 553)      # tela-cancelar: the CANCELAR button, under the thumb
FOTO_CHAT = (363, 644)           # tela-cancelar: the division photo in the chat
FOTO_LIXEIRA = (340, 550)        # tela-lixeira: the division photo with its 30 days
AUDIO_TELA = (412, 735)          # tela-audio: Renato's audio message
REC = (385, 640)                 # tela-gravando: the red dot and the time


def build(ed):
    s, e, cut, L = ed.s, ed.e, ed.cut, ed.L
    END, x = ed.END, L['x']
    v = bool(L['hud_dy'])                       # the vertical version
    story = cut(N('Três e catorze.'))
    plan = [
        # The usual opening, first and as in Part 3: the backpack art for the first two lines of
        # Part 1, and the black card with the stars for "Você ficou com o rosto no jornal."
        ('vinheta', 0, art('../episodio-01/cena-01-base.png', .06)),
        ('preto', cut(V(10)), dict(kind='black')),
        # Then the part's strongest moment, with its phrase from the plan's first frame.
        ('frio', cut(N('Hoje você descobre')), art(desenho('cena-01-mochila-sombra.png'), .05)),
        # The recap, in about 8 s: the profile, the deal with the man of the ring, the vote and
        # the newspaper.
        ('perfil', cut(N('Chegou agora?')), art(arte(f"perfil{L['art']}.png"), .03, direction='out')),
        ('acordo', cut(N('O homem do anel')), art(arte('lembranca-acordo.png'), .02)),
        ('votos', cut(N(VOTO)), art('../episodio-04/montagem/arte/tela-0313.png', .03, direction='out',
                                    brightness=.35)),
        # 03:14: the photo does not go out, and the deal.
        ('cancelar', story, art(arte('tela-cancelar.png'), .04)),
        ('socio', cut(A('Sócio.')), art(desenho('cena-03-socio.png'), .04, direction='out')),
        ('aperto', cut(N('mão. Você aperta.', 1)), art(desenho('cena-04-aperto.png'), .05)),
        ('apaga', cut(A('Agora apaga')), art(desenho('cena-05-apaga.png'), .04)),
        ('lixeira', cut(N('O que ele')), art(arte('tela-lixeira.png'), .05)),
        # The driver.
        ('portao', cut(A('O Toninho te')), art(desenho('cena-07-portao-carro.png'), .04, direction='out')),
        ('volante', cut(N('Toninho é o')), art(desenho('cena-08-toninho-volante.png'), .05)),
        # The light moment: Renato's audio and his mother's cake.
        ('audio', cut(N('No caminho,')), art(arte('tela-audio.png'), .04)),
        ('bolo', cut(R('Cheguei.')), art(desenho('cena-10-bolo.png'), .04, direction='out')),
        ('quaseri', cut(N('Pela primeira vez')), art(desenho('cena-11-quase-ri.png'), .05)),
        # The closed gas station and the turn.
        ('posto', cut(N('Aí o Toninho')), art(desenho('cena-12-posto.png'), .04, direction='out')),
        ('perfil-toninho', cut(N('E fala sem')), art(desenho('cena-13-toninho-perfil.png'), .05)),
        ('gravar', cut(N('Devagar, a sua')), art(arte('tela-gravando.png'), .05)),
        ('divisao', cut(T('Ele precisava')), art(desenho('cena-15-noite-da-divisao.png'), .04, direction='out')),
        ('choque', cut(N('O homem que')), art(desenho('cena-16-choque.png'), .06)),
        ('bolsas', cut(T('Fui eu que')), art(arte('lembranca-bolsas.png'), .02)),
        ('encara', cut(T('Eu sei onde')), art(desenho('cena-17-toninho-encara.png'), .05)),
        # The vote: each option with its scene, then both.
        ('topar', cut(N('Se você topar,')), art(desenho('cena-18-opcao-topar.png'), .03)),
        ('contar', cut(N('Se contar pro')), art(desenho('cena-19-opcao-contar.png'), .03)),
        ('escolha', cut(N('Topar ou contar?')), art(arte(f"opcoes{L['art']}.png"), .02, direction='out')),
    ]
    plan.sort(key=lambda item: item[1])
    used = [f['asset'] for _, _, f in plan if f.get('asset')]
    repeated = sorted({a for a in used if used.count(a) > 1})
    if repeated:
        raise ValueError(f'drawings used more than once: {repeated}')
    AT = {name: t for name, t, _ in plan}
    nxt = {name: (plan[k+1][1] if k + 1 < len(plan) else END) for k, (name, _, _) in enumerate(plan)}
    scenes = [{'start': t, 'end': nxt[name], **fields} for name, t, fields in plan]
    jornal_at = round(e(N(VOTO, 2)) + .15, 2)
    winner = max(VOTE, key=lambda o: o[1])[0]
    lixo = s(N('a foto continua'))
    roubou = s(T('O Ademir.'))
    divide = s(T('a gente divide.'))
    # Toninho's lines while he is not on screen show as quotes, as the partner's in Part 4.
    graphics = [
        # ---- the usual opening, element for element as in Part 3 (abertura() in
        # ../../episodio-03/montagem/montar_timeline.py)
        {'type': 'tag', 'start': .15, 'end': story, 'text': f'PARTE {PART}', 'y': L['tag_y'], 'x': 112, 'size': 32},
        phrase(.2, s(V(4)) - .07, 700, [line('O ASSALTO', s(V(0))), line('DEU CERTO.', s(V(2)), 'yellow')], x=x),
        phrase(s(V(4)) - .07, AT['preto'], 700, [
            label('SEU PARCEIRO FICOU COM', s(V(4))),
            line('R$ 10.000.000', s(V(4)) + .08, 'green', size=74,
                 count={'from': 0, 'to': 10000000, 'start': s(V(5)), 'end': e(V(9)) - .3}),
            label('EM DINHEIRO VIVO', s(V(8)))], x=x),
        phrase(AT['preto'] + .05, AT['frio'], 560, [line('VOCÊ FICOU COM', s(V(10))), line('O ROSTO', s(V(14)), 'yellow'),
                                                    line('NO JORNAL.', s(V(15)), 'yellow')], 64, x),
        {'type': 'stars', 'start': round(AT['preto'] + .05, 2), 'end': AT['frio'], 'y': 790, 'x': x, 'at': s(V(14)),
         'step': .12},
        # ---- the cold open: the part's strongest moment
        {'type': 'vignette', 'start': AT['frio'], 'end': AT['perfil'], 'color': 'alert', 'strength': .5},
        phrase(AT['frio'] + .05, AT['perfil'], 920, [label('HOJE VOCÊ DESCOBRE', AT['frio'] + .05),
                                                     line('QUEM ENCHEU', AT['frio'] + .05),
                                                     line('A SUA MOCHILA.', s(N('a sua mochila')), 'yellow', shake=True)],
               66, x),
        callout('ROUPA VELHA', s(N('roupa velha.')), AT['perfil'], 470 if v else 500, 430, (215, 640), 'white'),
        # ---- the recap
        phrase(AT['perfil'] + .05, AT['acordo'], 790, [line('CHEGOU AGORA?', s(N('Chegou agora?')), 'yellow', size=64),
                                                       line('AS PARTES 1 A 4', s(N('As outras partes')), size=52),
                                                       line('TÃO NO PERFIL', s(N('no perfil.')), size=52)], 72, x),
        {'type': 'pointer', 'start': round(s(N('no perfil.')), 2), 'end': AT['acordo'], 'y': 940, 'x': x, 'text': HANDLE},
        polaroid('episodio-04/cena-21-opcao-cancelar.png', [0.05, 0.33, 0.95, 0.836], 'PARTE 4', 'o acordo',
                 AT['acordo'] + .05, AT['votos'], x, 560),
        phrase(AT['acordo'] + .05, AT['votos'], 930, [line('O HOMEM DO ANEL', s(N('O homem do anel')), size=52),
                                                      line('QUER VOCÊ', s(N('quer você de')), size=60),
                                                      line('DE SÓCIO.', s(N('de sócio.')), 'yellow', size=60)], 60, x),
        {'type': 'bars', 'start': AT['votos'] + .05, 'end': jornal_at, 'y': 500, 'x': x, 'width': L['bars'],
         'title': f'PARTE {PART - 1} · VOCÊS VOTARAM', 'title_at': round(s(N(VOTO)), 2),
         'items': [{'label': n, 'pct': pct, 'at': round(s(N(VOTO)) + .1 + .15*k, 2), 'winner': n == winner}
                   for k, (n, pct) in enumerate(VOTE)]},
        stamp(winner, s(N(VOTO, 2)) - .02, jornal_at, 860, x, 'yellow'),
        # The comments on Part 4, printed in the newspaper.
        {'type': 'jornal', 'start': jornal_at, 'end': story, 'y': 340 if v else 300, 'x': x, 'width': 500 if v else 560,
         'title': 'A VOZ DO BAIRRO', 'sub': f'o que vocês comentaram na parte {PART - 1}',
         'items': [{'text': c, 'at': round(jornal_at + .3 + .5*k, 2)} for k, c in enumerate(COMENTARIOS)]},
        # ---- the panel: their share, the photo in the trash, who robbed them, the share again
        hud(story, lixo, 'A SUA PARTE', 'R$ 0', 'red', L['hud_dy']),
        hud(lixo, roubou, 'A FOTO', 'NA LIXEIRA', 'yellow', L['hud_dy']),
        hud(roubou, divide, 'QUEM TE ROUBOU', 'ADEMIR', 'red', L['hud_dy'], shake=True),
        hud(divide, AT['topar'], 'A SUA PARTE', 'R$ 5 MI?', 'green', L['hud_dy']),
        tag('O ACORDO · 03:14', story, AT['portao'], L['tag_y']),
        tag('O MOTORISTA', AT['portao'], AT['audio'], L['tag_y']),
        tag('A CAMINHO · 03:31', AT['audio'], AT['posto'], L['tag_y']),
        tag('O POSTO · 03:40', AT['posto'], AT['divisao'], L['tag_y']),
        tag('A NOITE DA DIVISÃO', AT['divisao'], AT['choque'], L['tag_y'], 'alert'),
        tag('A PROPOSTA', AT['bolsas'], AT['topar'], L['tag_y']),
        # ---- 03:14
        phrase(story + .05, s(N('O seu dedo')) - .05, 960, [line('03:14', s(N('Três e catorze.')), 'yellow', size=90)], 70, x),
        ring(s(N('dedo aperta')), s(N('A foto da')), *BOTAO_CANCELAR, 50, 'yellow'),
        pop('TOC', s(N('aperta cancelar.', 1)), s(N('A foto da')), 560 if not v else 520, 520, 52, 'white', 8),
        ring(s(N('A foto da')), s(N('não sai.')), *FOTO_CHAT, 82, 'red'),
        stamp('NÃO SAI', s(N('não sai.')) - .02, AT['socio'], FOTO_CHAT[1] + 40, FOTO_CHAT[0], 'red'),
        # ---- the deal
        balloon('Sócio.', s(A('Sócio.')), AT['aperto'], 190, (290, 440), L=L),
        ring(s(N('Ele estende')), AT['aperto'], 282, 790, 88, 'yellow'),
        phrase(s(N('Ele estende')) - .05, AT['aperto'], 990, [line('ELE ESTENDE A MÃO.', s(N('Ele estende')), size=50)], 50, x),
        stamp('SÓCIOS', s(N('mão. Você aperta.', 2)) - .02, AT['apaga'], 960, x, 'yellow'),
        balloon('Agora apaga essa foto. Na minha frente.', s(A('Agora apaga')), AT['lixeira'], 430 if v else 440,
                (450, 455), width=400, L=L),
        stamp('APAGADA', s(N('Você apaga.', 1)) - .02, AT['lixeira'], 970, x, 'red'),
        phrase(AT['lixeira'] + .05, AT['portao'], 920, [label('O QUE ELE NÃO SABE:', s(N('O que ele'))),
                                                        line('A FOTO CONTINUA', s(N('a foto continua'))),
                                                        line('NA LIXEIRA.', s(N('na lixeira')), 'yellow')], 60, x),
        ring(lixo, AT['portao'], *FOTO_LIXEIRA, 95, 'yellow'),
        # ---- the driver
        balloon('O Toninho te leva.', s(A('O Toninho te')), s(A('Amanhã a gente')), 250, (150, 560), y=470, width=400, L=L),
        balloon('Amanhã a gente começa a caçada.', s(A('Amanhã a gente')), AT['volante'], 250, (150, 560), y=470,
                width=400, L=L),
        ring(s(A('O Toninho te')), AT['volante'], 466, 712, 92, 'yellow'),
        nametag('TONINHO', 'o motorista do Ademir', s(N('Toninho é o')) + .1, s(N('O mesmo que')), x, 'alert', y=975),
        phrase(s(N('O mesmo que')) - .05, AT['audio'], 975, [label('O MESMO QUE DIRIGIU', s(N('O mesmo que'))),
                                                             line('O CARRO DO ASSALTO.', s(N('carro do assalto.')),
                                                                  'yellow', size=44)], 50, x),
        # ---- Renato's audio
        pop('VRRR', s(N('celular vibra.')), AT['bolo'], 540 if not v else 500, 545, 56, 'white', -6, shake=True),
        callout('ÁUDIO DO RENATO', s(N('áudio do Renato.')), AT['bolo'], 200, 1000, AUDIO_TELA, 'green'),
        balloon('Cheguei. Minha mãe tá fazendo o bolo de fubá às quatro da manhã.', s(R('Cheguei.')),
                s(R('Mandou dizer')), 370 if v else 380, (370, 500), L=L),
        balloon('Mandou dizer que metade é sua.', s(R('Mandou dizer')), AT['quaseri'], 370 if v else 380, (370, 500), L=L),
        nametag('DONA CÉLIA', 'a mãe do Renato', s(R('Minha mãe')) + .1, AT['quaseri'], 150, y=900),
        callout('BOLO DE FUBÁ', s(R('bolo de fubá')), AT['quaseri'], 240, 690, (112, 765)),
        tag('METADE É SUA', s(R('metade é sua.')), AT['quaseri'], 975, 'green', x + 50, 24),
        phrase(AT['quaseri'] + .05, AT['posto'], 950, [label('PELA PRIMEIRA VEZ NA NOITE,', s(N('Pela primeira vez'))),
                                                       line('VOCÊ QUASE RI.', s(N('você quase ri.')), 'yellow')], 58, x),
        # ---- the gas station
        pop('CLIC', s(N('desliga o rádio.')), s(N('Para num posto')), 530 if not v else 500, 640, 50, 'white', 6),
        phrase(s(N('Para num posto')) - .05, AT['perfil-toninho'], 930, [
            line('03:40', s(N('Para num posto')), 'yellow', size=90),
            line('UM POSTO FECHADO.', s(N('posto fechado.')), size=44)], 70, x),
        phrase(AT['perfil-toninho'] + .05, s(T('Sabe quem')) - .05, 950, [label('E FALA', s(N('E fala sem'))),
                                                                       line('SEM OLHAR PRA VOCÊ.', s(N('sem olhar pra')),
                                                                            size=48)], 48, x),
        balloon('Sabe quem montou as mochilas da divisão?', s(T('Sabe quem')), s(T('A sua já')), 380 if not v else 360,
                (430, 520), L=L),
        phrase(roubou - .05, s(T('A sua já')), 940, [line('O ADEMIR.', roubou, 'red', size=96, shake=True)], 96, x),
        balloon('A sua já saiu do São Jorge cheia de roupa velha.', s(T('A sua já')), AT['gravar'], 380 if not v else 360,
                (430, 520), L=L),
        polaroid('episodio-01/cena-03-roupas.png', [0.0, 0.28, 1.0, 0.8425], 'PARTE 1', 'a sua mochila',
                 s(T('cheia de roupa')), AT['gravar'], 200, 860, 200, -6),
        # ---- the recorder
        phrase(AT['gravar'] + .05, AT['divisao'], 940, [label('A MÃO ENTRA NO BOLSO', s(N('a sua mão'))),
                                                         line('APERTA GRAVAR.', s(N('aperta gravar.')), 'red', size=60)],
               60, x),
        ring(s(N('aperta gravar.', 1)), AT['divisao'], *REC, 70, 'red'),
        # ---- the night of the division, in Toninho's words
        callout('A SUA MOCHILA', s(T('de um culpado,')), AT['choque'], 200, 420, (205, 640)),
        phrase(AT['divisao'] + .05, s(T('e o Renato')) - .05, 940, [line('“ELE PRECISAVA', s(T('Ele precisava'))),
                                                                    line('DE UM CULPADO.”', s(T('de um culpado,')),
                                                                         'yellow')], 56, x),
        phrase(s(T('e o Renato')) - .05, s(T('Só que')) - .05, 940, [line('“E O RENATO', s(T('e o Renato'))),
                                                                    line('TE LEVOU.”', s(T('te levou.')), 'yellow')],
               56, x),
        phrase(s(T('Só que')) - .05, AT['choque'], 930, [label('“SÓ QUE O SEU PARCEIRO', s(T('Só que'))),
                                                         line('PASSOU A PERNA', s(T('passou a perna'))),
                                                         line('NELE TAMBÉM.”', s(T('nele também.')), 'green')], 54, x),
        callout('O DINHEIRO', s(T('o seu parceiro')), AT['choque'], 520 if not v else 480, 420, (480, 640), 'green'),
        # ---- the shock
        {'type': 'vignette', 'start': AT['choque'], 'end': AT['bolsas'], 'color': 'alert', 'strength': .7},
        phrase(AT['choque'] + .05, AT['bolsas'], 930, [label('O HOMEM QUE VOCÊ LIVROU', s(N('O homem que'))),
                                                       line('FOI O PRIMEIRO', s(N('foi o primeiro'))),
                                                       line('A TE ROUBAR.', s(N('a te roubar.')), 'red', shake=True)],
               60, x),
        # ---- Toninho's offer
        polaroid('episodio-04/cena-17-parceiro.png', [0.1, 0.33, 0.9, 0.78], 'PARTE 4', 'as bolsas',
                 AT['bolsas'] + .05, AT['encara'], x, 540, 300, 5),
        phrase(AT['bolsas'] + .05, AT['encara'], 930, [line('“FUI EU QUE LEVEI', s(T('Fui eu que')), size=48),
                                                       line('O SEU PARCEIRO.”', s(T('o seu parceiro naquela')), 'yellow',
                                                            size=52),
                                                       label('COM AS DUAS BOLSAS', s(T('Com as duas')))], 52, x),
        balloon('Eu sei onde ele tá.', s(T('Eu sei onde')), s(T('Sozinho,')), 330 if not v else 320, (300, 420),
                y=330 if not v else 370, L=L),
        balloon('Sozinho, eu não chego perto.', s(T('Sozinho,')), s(T('Me ajuda')), 330 if not v else 320, (300, 420),
                y=330 if not v else 370, L=L),
        balloon('Me ajuda a pegar o dinheiro antes do Ademir,', s(T('Me ajuda')), divide, 330 if not v else 320,
                (300, 420), y=330 if not v else 370, L=L),
        balloon('e a gente divide.', divide, AT['topar'], 330 if not v else 320, (300, 420), y=330 if not v else 370, L=L),
        phrase(divide - .05, AT['topar'], 950, [line('R$ 5 MILHÕES', divide, 'green', size=66),
                                                 label('PRA CADA UM?', s(T('a gente divide.', 2)))], 66, x),
        # ---- the vote, illustrated: each option with its pros and cons
        tag('OPÇÃO 1 · TOPAR', AT['topar'] + .05, AT['contar'], 300, 'white', x, 24),
        tag('− TRAI O ADEMIR', s(N('trai o Ademir')), AT['contar'], 950, 'alert', x, 22),
        tag('− CONFIA EM QUEM LEVOU O DINHEIRO', s(N('levou o seu dinheiro')), AT['contar'], 1000, 'alert', x, 22),
        tag('+ ELE SABE ONDE O PARCEIRO ESTÁ', e(N('dinheiro embora.', 1)) + .3, AT['contar'], 850, 'green', x, 22),
        tag('+ O DINHEIRO ANTES DO ADEMIR', e(N('dinheiro embora.', 1)) + .9, AT['contar'], 900, 'green', x, 22),
        tag('OPÇÃO 2 · CONTAR', AT['contar'] + .05, AT['escolha'], 300, 'white', x, 24),
        tag('+ GANHA A CONFIANÇA DO ADEMIR', s(N('ganha a confiança')), AT['escolha'], 850, 'green', x, 22),
        tag('− O TONINHO PAGA POR ISSO', s(N('E o Toninho paga')), AT['escolha'], 950, 'alert', x, 22),
        tag('+ A GRAVAÇÃO PROVA QUE VOCÊ É LEAL', e(N('paga por isso.', 2)) + .3, AT['escolha'], 900, 'green', x, 22),
        tag('− FICA COM QUEM TE ROUBOU PRIMEIRO', e(N('paga por isso.', 2)) + .9, AT['escolha'], 1000, 'alert', x, 22),
        phrase(AT['escolha'], END, 585, [line('TOPAR', s(N('Topar ou contar?'))),
                                         line('OU CONTAR?', s(N('ou contar?', 1)), 'yellow')], 76, x),
        {'type': 'buttons', 'start': round(s(N('Comenta uma palavra')) - .05, 2), 'end': END, 'y': 800,
         'x': x - (20 if v else 0),
         'prompt': 'COMENTA UMA PALAVRA', 'prompt_at': round(s(N('Comenta uma palavra')), 2),
         'items': [{'text': 'TOPAR', 'at': round(s(N('uma palavra só.', 1)), 2), 'style': 'yellow'},
                   {'text': 'CONTAR', 'at': round(s(N('uma palavra só.', 2)), 2), 'style': 'white'}]},
        {'type': 'box', 'start': round(s(N('O que a maioria')), 2), 'end': END, 'y': 940, 'x': x,
         'title': f'PARTE {PART + 1}', 'sub': 'a maioria decide o próximo passo'},
    ]
    effects = [
        *[sfx('whoosh.wav', AT[n] - WHOOSH_PEAK, -2) for n in ('preto', 'frio', 'perfil', 'votos', 'cancelar', 'portao',
                                                               'audio', 'posto', 'divisao', 'choque', 'bolsas', 'topar',
                                                               'escolha')],
        sfx('impacto.wav', s(N('a sua mochila')) - .04, -5),
        # As in Part 3: the counter's ticks, denser at first; the stars' pops; "jornal".
        *[sfx('tique.wav', s(V(5)) + (e(V(9)) - .3 - s(V(5)))*(1 - (1 - k/14)**(1/3)), -18) for k in range(1, 15)],
        *[sfx('pop.wav', s(V(14)) + .12*k, -16) for k in range(5)],
        sfx('impacto.wav', s(V(16)) - .05, -5),
        sfx('pop.wav', s(N('roupa velha.')), -12),
        sfx('pop.wav', s(N('no perfil.')), -10),
        sfx('pop.wav', AT['acordo'] + .05, -12),
        *[sfx('tique.wav', s(N(VOTO)) + .1 + .1*k, -20) for k in range(8)],
        sfx('impacto.wav', s(N(VOTO, 2)) - .04, -5),
        sfx('pop.wav', s(N('aperta cancelar.', 1)), -8),
        sfx('impacto.wav', s(N('não sai.')) - .04, -6),
        sfx('impacto-suave.wav', s(A('Sócio.')) - .04, -8),
        sfx('impacto.wav', s(N('mão. Você aperta.', 2)) - .04, -6),
        sfx('impacto-suave.wav', s(N('Você apaga.', 1)) - .04, -6),
        sfx('notificacao.wav', lixo, -12),
        sfx('passos.wav', s(A('O Toninho te')), -14),
        sfx('pop.wav', s(N('Toninho é o')) + .1, -10),
        sfx('vibracao.wav', s(N('celular vibra.')) - .1, -8),
        sfx('pop.wav', s(R('Minha mãe')) + .1, -12),
        sfx('pop.wav', s(R('metade é sua.')), -12),
        sfx('interruptor.wav', s(N('desliga o rádio.')), -8),
        sfx('impacto.wav', roubou - .04, -4),
        sfx('pop.wav', s(T('cheia de roupa')), -12),
        sfx('pop.wav', s(N('aperta gravar.', 1)), -8),
        sfx('impacto.wav', s(N('a te roubar.')) - .04, -4),
        sfx('pop.wav', AT['bolsas'] + .05, -12),
        sfx('impacto-suave.wav', divide - .04, -7),
        *[sfx('pop.wav', t, -14) for t in (s(N('trai o Ademir')), s(N('levou o seu dinheiro')), s(N('ganha a confiança')),
                                          s(N('E o Toninho paga')))],
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
    words = load_words()
    pieces = segments(words)
    at, length = timing(words, pieces)
    end = round(length + TAIL, 2)
    gains = join(words, pieces, AUDIO)
    for layout in (INSTAGRAM, VERTICAL):
        scenes, graphics, effects = build(Edit(at, end, layout, gains))
        wide = too_wide(graphics, layout['width'])
        if wide:
            raise ValueError(f'Lines wider than the {layout["name"]} layout allows: {wide}')
        graficos.check(graphics)
        timeline = {'timing_status': 'aligned_to_voice', 'style': 'guia-de-estilo-referencia.md', 'script': SCRIPT.name,
                    'alignment': [str(VOICES[v][1].relative_to(SERIE)) for v in VOICES],
                    'audio': AUDIO.name, 'tail': TAIL,
                    'scenes': scenes, 'graphics': graphics, 'sfx': effects, 'captions': [],
                    'effects': ['../../episodio-02/montagem/efeitos']}
        (HERE / layout['name']).write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f"{layout['name']}: {len(scenes)} scenes, {len(graphics)} graphics, {len(effects)} sound effects, ends at {end}s")
    print(f'{AUDIO.name}: {length}s of voice; gains ' + ', '.join(f'{v} {g:+.1f} dB' for v, g in gains.items()))


if __name__ == '__main__':
    main()
