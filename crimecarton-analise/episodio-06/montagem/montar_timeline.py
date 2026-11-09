#!/usr/bin/env python3
"""Build Part 6's narration track and its two timelines from the word alignments.

Part 6 is "A recompensa" (../roteiro-ep06-contar.txt), the CONTAR path. The track joins, in the
script's order, the narrator's lines from narracao-ep06-narrador.wav, closing request included;
Ademir's from narracao-ep06-ademir.wav, in the cobrador's voice heard in person (vozes/ademir.wav,
made by ../../episodio-04/montagem/voz_ademir.py); Toninho's two new lines, from
narracao-ep06-toninho.wav (Orus); his offer recorded in Part 5, playing on Zinho's phone
(vozes/toninho-gravacao.wav, made by gravacao_toninho.py); and the pauses the edit opens for the
beats, the options and the newspaper. Each line is found in its recording by its words, and every
cut, graphic and effect is anchored to a word of the script.

From Part 6 on, the creator's rule of 08/11/2026 (../../../CLAUDE.md): after the usual opening
(the vinheta, exactly as in Part 3) and the part's strongest moment, the story starts at once,
with no spoken "Chegou agora?" (a small tag says the earlier parts are on the profile); the last
vote's result and the newspaper "A VOZ DO BAIRRO" come at the end, right before the new question,
with "O seu comentário pode sair no jornal da próxima parte". The phones of this part's drawings
face the camera, straight and big: the screens fitted into them are their own close-ups.

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


SCRIPT = EPISODE / 'roteiro-ep06-contar.txt'
VOICES = {'VINHETA': (HERE / 'vozes' / 'vinheta.wav', TOOLS / 'alinhamento-narracao.json'),
          'NARRADOR': (EPISODE / 'narracao-ep06-narrador.wav', HERE / 'alinhamento-narrador.json'),
          # Ademir in the cobrador's voice, made by voz_ademir.py.
          'ADEMIR': (HERE / 'vozes' / 'ademir.wav', HERE / 'alinhamento-ademir.json'),
          'TONINHO': (EPISODE / 'narracao-ep06-toninho.wav', HERE / 'alinhamento-toninho.json'),
          # Toninho's offer, recorded in Part 5, playing on the phone (gravacao_toninho.py).
          'GRAVACAO': (HERE / 'vozes' / 'toninho-gravacao.wav', HERE / 'alinhamento-toninho-gravacao.json')}
SOURCES = {'VINHETA': SERIE / 'narracao-ep01-zinho.txt', 'NARRADOR': EPISODE / 'narracao-ep06-narrador.txt',
           'ADEMIR': EPISODE / 'narracao-ep06-ademir.txt', 'TONINHO': EPISODE / 'narracao-ep06-toninho.txt',
           'GRAVACAO': HERE / 'gravacao-toninho.txt'}
TEXT = {v: [w for w in path.read_text(encoding='utf-8').split() if norm(w)] for v, path in SOURCES.items()}
AUDIO = EPISODE / 'narracao-ep06.wav'
PART = 6
HANDLE = '@golpecartoon'
# Part 5's vote: CONTAR 5 to 2 on Instagram (the part and the short vote reel), 09/11/2026.
VOTE = [('CONTAR', 71), ('TOPAR', 29)]
VOTO = 'Na parte cinco, vocês escolheram contar.'
# Real comments on Part 5, as readers' letters.
COMENTARIOS = ['Eu contaria, pois o Ademir é perigoso. Isso pode custar mais que dinheiro.', 'Rapaz, eu contaria.',
               'Topar.']
TAIL = 2.0
# Everyone talks beside Zinho, as loud as the narrator; the recording plays on a phone, a little lower.
GAINS = {'VINHETA': 0, 'ADEMIR': 0, 'TONINHO': 0, 'GRAVACAO': -3}
LEAD, TRAIL, SWITCH = .12, .22, .25
WHOOSH_PEAK = .36
# The script's lines another recording says.
GRAVADAS = {'Me ajuda a pegar o dinheiro antes do Ademir, e a gente divide.': 'GRAVACAO'}


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
        voice = GRAVADAS.get(text, voice)
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


def T(p, k=0):
    return 'TONINHO', find('TONINHO', p) + k


def G(p, k=0):
    return 'GRAVACAO', find('GRAVACAO', p) + k


# Silence the edit opens after a word, in seconds. At a voice's last word before another voice,
# it is the silence between the two.
PAUSES = {
    V(16): .35,                              # the stars, before the cold open, as in Part 3
    N('ganhou um preço.', 3): .7,            # the cold open lands
    N('não contou tudo.', 2): .3,
    N('sua mochila.', 1): .4,
    N('vira um problema.', 2): .5,
    N('em silêncio.', 1): .4,
    G('a gente divide.', 2): .6,
    A('de verdade.', 1): .3,
    A('um café?', 1): .5,
    N('O café é horrível.', 3): .4,
    N('mesmo assim.', 1): .8,                # the light moment, before the turn
    N('veio trabalhar.', 1): .3,
    N('tranca o portão.', 2): .6,
    N('Renato esteve.', 1): .6,
    A('o parceiro?', 1): .6,
    N('não fala.', 1): .4,
    N('celular vibra.', 1): .3,
    N('sobre você.', 1): .7,                 # time to read the news
    A('sua cabeça.', 1): .3,
    A('é leal.', 1): .3,
    A('o alicate.', 1): .5,
    N('levanta a cabeça.', 2): .4,
    T('seu dinheiro?', 1): .3,
    T('Dona Célia.', 1): .5,
    N('mãe do Renato.', 2): .6,
    T('pra você?', 1): 1.0,                  # the turn lands
    N('Caixa postal.', 1): .3,
    N('Nada.'): .7,
    N('passos voltam.', 1): .4,
    A('alguma coisa?', 1): .8,
    N('no seu dinheiro.', 2): 3.8,           # option 1's pros and cons, time to read them
    N('é a sua.', 2): 3.8,                   # option 2's
    N('escolheram contar.', 1): 4.0,         # the newspaper, to read the comments
    N('próxima parte.', 1): .5,
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


def hud(start, end, label_, value, color, dy, shake=False):
    v = {'at': round(start, 2), 'text': value, 'color': color}
    if shake:
        v['shake'] = True
    return {'type': 'hud', 'start': round(start, 2), 'end': round(end, 2), 'label': label_, 'dy': dy,
            'values': [v], 'stars': [{'at': round(start, 2), 'count': 5, 'step': 0}]}


def stamp(text, start, end, y, x, color='red', filled=True, angle=-7):
    return {'type': 'stamp', 'start': round(start, 2), 'end': round(end, 2), 'text': text, 'y': y, 'x': x,
            'angle': angle, 'color': color, 'filled': filled}


def polaroid(image, focus, caption, sub, start, end, x, y, size=300, angle=-5):
    return {'type': 'polaroid', 'start': round(start, 2), 'end': round(end, 2), 'image': image, 'focus': focus,
            'caption': caption, 'sub': sub, 'x': x, 'y': y, 'size': size, 'angle': angle}


# Where the screens' details land in the 720 × 1280 frame, measured on the composed scenes.
TRECHO_TELA = (365, 640)         # tela-editar: the red stretch to cut
BOTAO_CORTAR = (360, 743)        # tela-editar: CORTAR TRECHO
VALOR_TELA = (443, 742)          # tela-recompensa: the R$ 50.000 tag
CADEIRA = (470, 900)             # cena-08: the chair under Toninho


def build(ed):
    s, e, cut, L = ed.s, ed.e, ed.cut, ed.L
    END, x = ed.END, L['x']
    v = bool(L['hud_dy'])                       # the vertical version
    story = cut(N('Você foi contar'))
    plan = [
        # The usual opening, first and as in Part 3.
        ('vinheta', 0, art('../episodio-01/cena-01-base.png', .06)),
        ('preto', cut(V(10)), dict(kind='black')),
        # The part's strongest moment: the price on Zinho's face.
        ('frio', cut(N('Hoje, o seu rosto')), art(arte('cartaz.png'), .07)),
        # The story starts at once: no spoken recap (the creator's rule of 08/11/2026).
        ('meio-fio', story, art(desenho('cena-02-meio-fio.png'), .04, direction='out')),
        ('editar', cut(N('Antes de dar')), art(arte('tela-editar.png'), .04)),
        ('cortado', cut(N('Se o Ademir')), art(arte('tela-cortado.png'), .03, direction='out')),
        # 05:00, the São Jorge.
        ('escuta', cut(N('Cinco da manhã,')), art(desenho('cena-04-ademir-escuta.png'), .04)),
        ('socio', cut(A('Agora sim.')), art(desenho('cena-05-socio-de-verdade.png'), .05)),
        ('cafe', cut(A('Aceita um café?')), art(desenho('cena-06-cafe.png'), .04, direction='out')),
        # 06:00, the chair.
        ('portao', cut(N('Às seis,')), art(desenho('cena-07-portao-trancado.png'), .04)),
        ('amarrado', cut(N('Minutos depois,')), art(desenho('cena-08-toninho-amarrado.png'), .04, direction='out')),
        ('onde', cut(A('Onde está')), art(desenho('cena-09-onde-ta.png'), .05)),
        ('calado', cut(N('O Toninho não')), art(desenho('cena-10-toninho-calado.png'), .06)),
        ('recompensa', cut(N('A polícia oferece')), art(arte('tela-recompensa.png'), .04)),
        ('meio-sorriso', cut(A('Cinquenta mil')), art(desenho('cena-12-ademir-meio-sorriso.png'), .05)),
        # The turn.
        ('sai', cut(N('Quando os passos')), art(desenho('cena-13-ademir-sai.png'), .04, direction='out')),
        ('cochicha', cut(T('Quer o seu')), art(desenho('cena-14-toninho-cochicha.png'), .05)),
        ('bolo', cut(T('Ou você acha')), art(desenho('cena-15-bolo-das-quatro.png'), .04, direction='out')),
        ('caixa', cut(N('Você liga pro')), art(arte('tela-caixa-postal.png'), .04)),
        ('alicate', cut(N('Os passos voltam.')), art(desenho('cena-17-alicate.png'), .04)),
        # The choice, then Part 5's vote and the newspaper, then the question.
        ('falar', cut(N('Se você falar,')), art(desenho('cena-18-opcao-falar.png'), .03)),
        ('calar', cut(N('Se você calar,')), art(desenho('cena-19-opcao-calar.png'), .03)),
        ('votos', cut(N(VOTO)), art(f"../episodio-05/montagem/arte/opcoes{L['art']}.png", .02, direction='out',
                                    brightness=.3)),
        ('escolha', cut(N('Falar ou calar?')), art(arte(f"opcoes{L['art']}.png"), .02, direction='out')),
    ]
    plan.sort(key=lambda item: item[1])
    used = [f['asset'] for _, _, f in plan if f.get('asset')]
    repeated = sorted({a for a in used if used.count(a) > 1})
    if repeated:
        raise ValueError(f'drawings used more than once: {repeated}')
    AT = {name: t for name, t, _ in plan}
    nxt = {name: (plan[k+1][1] if k + 1 < len(plan) else END) for k, (name, _, _) in enumerate(plan)}
    scenes = [{'start': t, 'end': nxt[name], **fields} for name, t, fields in plan]
    contar = N(VOTO, 5)
    jornal_at = round(e(contar) + .15, 2)
    winner = max(VOTE, key=lambda o: o[1])[0]
    preco = s(N('A polícia oferece'))
    parceiro = s(T('O seu parceiro'))
    perfil_fim = round(story + 3.5, 2)
    graphics = [
        # ---- the usual opening, element for element as in Part 3
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
        # ---- the cold open: the price on his face
        {'type': 'vignette', 'start': AT['frio'], 'end': AT['meio-fio'], 'color': 'alert', 'strength': .45},
        phrase(AT['frio'] + .05, AT['meio-fio'], 960, [line('O SEU ROSTO', AT['frio'] + .05),
                                                       line('GANHOU UM PREÇO.', s(N('ganhou um preço.')), 'yellow',
                                                            shake=True)], 54, x),
        # ---- the panel and the tags
        tag('PARTES 1 A 5 NO PERFIL', story, perfil_fim, L['tag_y'], 'white', size=20),
        hud(story, preco, 'A SUA PARTE', 'R$ 0', 'red', L['hud_dy']),
        hud(preco, parceiro, 'RECOMPENSA', 'R$ 50 MIL', 'red', L['hud_dy'], shake=True),
        hud(parceiro, AT['falar'], 'O PARCEIRO', 'NA DONA CÉLIA', 'yellow', L['hud_dy']),
        tag('O CORTE · 04:52', perfil_fim, AT['escuta'], L['tag_y']),
        tag('O SÃO JORGE · 05:00', AT['escuta'], AT['portao'], L['tag_y']),
        tag('A CADEIRA · 06:00', AT['portao'], AT['recompensa'], L['tag_y']),
        tag('A RECOMPENSA', AT['recompensa'], AT['cochicha'], L['tag_y'], 'alert'),
        tag('A VIRADA', AT['cochicha'], AT['falar'], L['tag_y'], 'alert'),
        # ---- the cut
        phrase(story + .05, AT['editar'], 960, [line('VOCÊ CONTOU.', s(N('Você foi contar'))),
                                                line('MAS NÃO TUDO.', s(N('Mas não contou')), 'yellow')], 64, x),
        ring(s(N('a parte em que')), AT['cortado'], *TRECHO_TELA, 75, 'red'),
        ring(s(N('você corta')), s(N('a parte em que')), *BOTAO_CORTAR, 105, 'yellow'),
        phrase(AT['editar'] + .05, AT['cortado'], 970, [label('O TRECHO QUE DIZ', s(N('a parte em que'))),
                                                        line('QUEM ENCHEU A MOCHILA', s(N('quem encheu')), size=42)],
               42, x),
        phrase(AT['cortado'] + .05, AT['escuta'], 960, [label('SE ELE SOUBER QUE VOCÊ SABE,', s(N('Se o Ademir'))),
                                                        line('VOCÊ VIRA', s(N('você vira'))),
                                                        line('UM PROBLEMA.', s(N('um problema.')), 'red')], 58, x),
        # ---- 05:00: the recording, the partner, the coffee
        phrase(AT['escuta'] + .05, s(G('Me ajuda')) - .1, 990, [line('05:00', s(N('Cinco da manhã,')), 'yellow', size=80),
                                                                label('ELE ESCUTA TUDO', s(N('escuta tudo')))], 70, x),
        dict(balloon('“Me ajuda a pegar o dinheiro antes do Ademir, e a gente divide.”', s(G('Me ajuda')), AT['socio'],
                     330, (200, 545), y=390 if not v else 420, width=460, L=L), style='light'),
        tag('A GRAVAÇÃO DO CARRO', s(G('Me ajuda')), AT['socio'], 990, 'white', x, 22),
        balloon('Agora sim. Sócio de verdade.', s(A('Agora sim.')), AT['cafe'], 360, (350, 400), y=330 if not v else 360,
                width=520, L=L),
        balloon('Aceita um café?', s(A('Aceita um café?')), s(N('Dessa vez,')), 220, (240, 480), y=400, width=300, L=L),
        stamp('DESSA VEZ, SIM', s(N('Dessa vez,')) - .02, AT['portao'], 960, x, 'green'),
        pop('ECA', s(N('O café é horrível.', 3)) - .1, AT['portao'], 560 if not v else 520, 430, 52, 'white', 8),
        # ---- 06:00: the gate, the chair
        phrase(AT['portao'] + .05, AT['amarrado'], 960, [line('06:00', s(N('Às seis,')), 'yellow', size=80),
                                                         label('ELE VEIO TRABALHAR', s(N('achando que veio')))], 70, x),
        pop('TRANC', s(N('tranca o portão.')), AT['amarrado'], 240, 620, 54, 'white', -8, shake=True),
        polaroid('episodio-04/cena-06-renato-amarrado.png', [0.19, 0.38, 0.79, 0.7175], 'PARTE 4', 'a cadeira',
                 s(N('na mesma cadeira')), AT['onde'], 175, 880, 210, -6),
        callout('A MESMA CADEIRA', s(N('na mesma cadeira')), AT['onde'], 520 if not v else 470, 1000, CADEIRA),
        balloon('Onde está o parceiro?', s(A('Onde está')), AT['calado'], 210, (200, 410), y=330 if not v else 365,
                width=360, L=L),
        phrase(AT['calado'] + .05, AT['recompensa'], 990, [line('ELE NÃO FALA.', s(N('não fala.')), size=56)], 56, x),
        pop('VRRR', s(N('celular vibra.')), AT['recompensa'], 560 if not v else 520, 470, 56, 'white', -6, shake=True),
        # ---- the reward
        ring(s(N('cinquenta mil reais')), AT['meio-sorriso'], *VALOR_TELA, 85, 'yellow'),
        phrase(AT['recompensa'] + .05, AT['meio-sorriso'], 960, [line('R$ 50 MIL', s(N('cinquenta mil reais')), 'yellow',
                                                                      size=80),
                                                                 label('POR INFORMAÇÕES SOBRE VOCÊ', s(N('por informações')))],
               80, x),
        balloon('Cinquenta mil pela sua cabeça.', s(A('Cinquenta mil')), s(A('Ainda bem')), 360, (360, 440),
                y=360 if not v else 395, width=520, L=L),
        balloon('Ainda bem que você é leal.', s(A('Ainda bem')), s(A('Vigia ele.')), 360, (360, 440),
                y=360 if not v else 395, width=520, L=L),
        balloon('Vigia ele. Vou buscar o alicate.', s(A('Vigia ele.')), AT['sai'], 360, (360, 440),
                y=360 if not v else 395, width=520, L=L),
        # ---- the turn
        phrase(AT['sai'] + .05, AT['cochicha'], 990, [label('QUANDO OS PASSOS SOMEM,', s(N('Quando os passos'))),
                                                      line('ELE LEVANTA A CABEÇA.', s(N('levanta a cabeça.')), size=44)],
               44, x),
        balloon('Quer o seu dinheiro?', s(T('Quer o seu')), s(T('O seu parceiro')), 430 if not v else 400, (470, 470),
                y=None, width=420, L=L),
        # Two lines, wide, so the balloon stays above Toninho's hair.
        balloon('O seu parceiro está escondido na casa da Dona Célia.', s(T('O seu parceiro')), AT['bolo'],
                400 if not v else 380, (470, 470), width=520 if not v else 500, L=L),
        polaroid('episodio-05/cena-10-bolo.png', [0.0, 0.36, 0.45, 0.613], 'PARTE 5', 'a mãe do Renato',
                 s(N('A mãe do')), AT['bolo'], x, 880, 210, 5),
        {'type': 'vignette', 'start': AT['bolo'], 'end': AT['caixa'], 'color': 'alert', 'strength': .55},
        # In the vertical version, lower and smaller: clear of the tag and of TikTok's buttons.
        polaroid('episodio-05/cena-10-bolo.png', [0.0, 0.32, 0.8, 0.77], 'PARTE 5', 'o bolo', AT['bolo'] + .05, AT['caixa'],
                 560 if not v else 490, 430 if not v else 450, 190 if not v else 160, 6),
        phrase(AT['bolo'] + .05, AT['caixa'], 930, [label('“OU VOCÊ ACHA QUE ELA FEZ', s(T('Ou você acha'))),
                                                    line('BOLO ÀS 4 DA MANHÃ', s(T('fez bolo')), size=50),
                                                    line('PRA VOCÊ?”', s(T('pra você?')), 'yellow', shake=True)], 56, x),
        stamp('NÃO ATENDE', s(N('Nada.')) - .02, AT['alicate'], 960, x, 'red'),
        balloon('E aí? Ele falou alguma coisa?', s(A('E aí?')), AT['falar'], 360, (360, 515), y=400 if not v else 430,
                width=420, L=L),
        # ---- the vote, illustrated: each option with its pros and cons
        tag('OPÇÃO 1 · FALAR', AT['falar'] + .05, AT['calar'], 300, 'white', x, 24),
        tag('− A DONA CÉLIA NA MIRA DO ALICATE', s(N('vai até a casa')), AT['calar'], 950, 'alert', x, 22),
        tag('+ VOCÊ CHEGA NO SEU DINHEIRO', s(N('E você chega')), AT['calar'], 850, 'green', x, 22),
        tag('+ O ADEMIR CONFIA EM VOCÊ DE VEZ', e(N('no seu dinheiro.', 2)) + .3, AT['calar'], 900, 'green', x, 22),
        tag('− VOCÊ ENTREGA A MÃE DO SEU AMIGO', e(N('no seu dinheiro.', 2)) + .9, AT['calar'], 1000, 'alert', x, 22),
        tag('OPÇÃO 2 · CALAR', AT['calar'] + .05, AT['votos'], 300, 'white', x, 24),
        tag('− MENTE PRO HOMEM DO ANEL', s(N('mente pro')), AT['votos'], 950, 'alert', x, 22),
        tag('+ DESCOBRE O QUE O RENATO ESCONDE', s(N('vai sozinho')), AT['votos'], 850, 'green', x, 22),
        tag('− SE ELE DESCOBRIR, A CADEIRA É SUA', s(N('Se ele descobrir,')), AT['votos'], 1000, 'alert', x, 22),
        tag('+ PROTEGE A DONA CÉLIA', e(N('é a sua.', 2)) + .3, AT['votos'], 900, 'green', x, 22),
        # ---- Part 5's vote and the newspaper, right before the question
        {'type': 'bars', 'start': AT['votos'] + .05, 'end': jornal_at, 'y': 500, 'x': x, 'width': L['bars'],
         'title': f'PARTE {PART - 1} · VOCÊS VOTARAM', 'title_at': round(s(N(VOTO)), 2),
         'items': [{'label': n, 'pct': pct, 'at': round(s(N(VOTO)) + .1 + .15*k, 2), 'winner': n == winner}
                   for k, (n, pct) in enumerate(VOTE)]},
        stamp(winner, s(contar) - .02, jornal_at, 860, x, 'yellow'),
        {'type': 'jornal', 'start': jornal_at, 'end': AT['escolha'], 'y': 340 if v else 300, 'x': x,
         'width': 500 if v else 560, 'title': 'A VOZ DO BAIRRO', 'sub': f'o que vocês comentaram na parte {PART - 1}',
         'items': [{'text': c, 'at': round(jornal_at + .3 + .5*k, 2)} for k, c in enumerate(COMENTARIOS)]},
        phrase(s(N('O seu comentário')) - .05, AT['escolha'], 940, [label('O SEU COMENTÁRIO PODE SAIR', s(N('O seu comentário'))),
                                                                    line('NO JORNAL DA', s(N('no jornal da'))),
                                                                    line('PRÓXIMA PARTE.', s(N('próxima parte.')), 'yellow')],
               56, x),
        # ---- the question
        phrase(AT['escolha'], END, 585, [line('FALAR', s(N('Falar ou calar?'))),
                                         line('OU CALAR?', s(N('ou calar?', 1)), 'yellow')], 76, x),
        {'type': 'buttons', 'start': round(s(N('Comenta uma palavra')) - .05, 2), 'end': END, 'y': 800,
         'x': x - (20 if v else 0),
         'prompt': 'COMENTA UMA PALAVRA', 'prompt_at': round(s(N('Comenta uma palavra')), 2),
         'items': [{'text': 'FALAR', 'at': round(s(N('uma palavra só.', 1)), 2), 'style': 'yellow'},
                   {'text': 'CALAR', 'at': round(s(N('uma palavra só.', 2)), 2), 'style': 'white'}]},
        {'type': 'box', 'start': round(s(N('O que a maioria')), 2), 'end': END, 'y': 940, 'x': x,
         'title': f'PARTE {PART + 1}', 'sub': 'seu comentário pode sair no jornal'},
    ]
    effects = [
        *[sfx('whoosh.wav', AT[n] - WHOOSH_PEAK, -2) for n in ('preto', 'frio', 'meio-fio', 'escuta', 'portao', 'recompensa',
                                                               'cochicha', 'bolo', 'falar', 'votos', 'escolha')],
        sfx('impacto.wav', s(N('ganhou um preço.')) - .04, -5),
        # As in Part 3: the counter's ticks, denser at first; the stars' pops; "jornal".
        *[sfx('tique.wav', s(V(5)) + (e(V(9)) - .3 - s(V(5)))*(1 - (1 - k/14)**(1/3)), -18) for k in range(1, 15)],
        *[sfx('pop.wav', s(V(14)) + .12*k, -16) for k in range(5)],
        sfx('impacto.wav', s(V(16)) - .05, -5),
        sfx('pop.wav', story, -12),
        sfx('pop.wav', s(N('você corta')), -10),
        sfx('impacto-suave.wav', s(N('um problema.')) - .04, -7),
        sfx('pop.wav', s(N('Dessa vez,')), -10),
        sfx('tranca.wav', s(N('tranca o portão.')), -6),
        sfx('pop.wav', s(N('na mesma cadeira')), -12),
        sfx('vibracao.wav', s(N('celular vibra.')) - .1, -8),
        sfx('notificacao.wav', AT['recompensa'] + .1, -12),
        sfx('impacto.wav', s(N('cinquenta mil reais')) - .04, -6),
        sfx('passos.wav', s(N('Quando os passos')), -12),
        sfx('impacto.wav', s(T('Dona Célia.')) - .04, -5),
        sfx('pop.wav', s(N('A mãe do')), -12),
        sfx('impacto.wav', s(T('pra você?')) - .04, -4),
        sfx('chamada.wav', s(N('Você liga pro')) + .1, -14),
        sfx('desliga.wav', s(N('Caixa postal.')), -10),
        sfx('impacto-suave.wav', s(N('Nada.')) - .04, -7),
        sfx('passos.wav', s(N('Os passos voltam.')), -10),
        *[sfx('pop.wav', t, -14) for t in (s(N('vai até a casa')), s(N('E você chega')), s(N('mente pro')),
                                          s(N('vai sozinho')), s(N('Se ele descobrir,')))],
        *[sfx('tique.wav', s(N(VOTO)) + .1 + .1*k, -20) for k in range(8)],
        sfx('impacto.wav', s(contar) - .04, -5),
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
