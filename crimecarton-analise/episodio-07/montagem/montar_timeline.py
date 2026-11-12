#!/usr/bin/env python3
"""Build Part 7's narration track and its two timelines from the word alignments.

Part 7 is "A casa da mãe" (../roteiro-ep07-falar.txt), the FALAR path. The track joins, in the
script's order, the narrator's lines from narracao-ep07-narrador.wav; Ademir's, in the cobrador's
voice heard in person (vozes/ademir.wav, made by ../../episodio-04/montagem/voz_ademir.py); Dona
Célia's (Gacrux) and the partner's (Umbriel, vozes/parceiro.wav, with the comma's pause opened
before "Zinho"); and the short beats the edit opens. Each line is found in its recording by its
words, and every cut, graphic and effect is anchored to a word of the script.

From Part 7 on, the creator's rules of 10/11/2026 (../../../CLAUDE.md): the video starts on the
hook, with no vinheta; the tag "PARTE 7" and "PARTES 1 A 6 NO PERFIL" only come after it; Part 6's
vote becomes a stamp when the story shows its consequence; the question comes right at the turn,
before the options; each option has one pro and one con, with no silent pause; the newspaper "A
VOZ DO BAIRRO" comes with the comment request; and the last line asks to follow and share.

Every framing keeps faces, hands, the phone and the ring out of the top quarter, where the panel
and the part's tag sit, and the phrases between 65% and 80% of the height. The positions of
balloons, rings and callouts are set from each of Codex's drawings.

timeline.json is the Instagram version; timeline-vertical.json, for TikTok and Shorts, moves the
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


SCRIPT = EPISODE / 'roteiro-ep07-falar.txt'
VOICES = {'NARRADOR': (EPISODE / 'narracao-ep07-narrador.wav', HERE / 'alinhamento-narrador.json'),
          # Ademir in the cobrador's voice, made by voz_ademir.py.
          'ADEMIR': (HERE / 'vozes' / 'ademir.wav', HERE / 'alinhamento-ademir.json'),
          'DONA CÉLIA': (EPISODE / 'narracao-ep07-celia.wav', HERE / 'alinhamento-celia.json'),
          # The partner's line with the comma's pause opened before "Zinho" (README.md).
          'PARCEIRO': (HERE / 'vozes' / 'parceiro.wav', HERE / 'alinhamento-parceiro.json')}
SOURCES = {'NARRADOR': EPISODE / 'narracao-ep07-narrador.txt', 'ADEMIR': EPISODE / 'narracao-ep07-ademir.txt',
           'DONA CÉLIA': EPISODE / 'narracao-ep07-celia.txt', 'PARCEIRO': HERE / 'vozes' / 'parceiro.txt'}
TEXT = {v: [w for w in path.read_text(encoding='utf-8').split() if norm(w)] for v, path in SOURCES.items()}
AUDIO = EPISODE / 'narracao-ep07.wav'
PART = 7
HANDLE = '@golpecartoon'
# Real comments on Part 6, as readers' letters (plano-ep07.md).
COMENTARIOS = ['Contar, e bola um plano pra se livrar do cara depois.', 'Ficar calado, o cara tá na maldade dos 50 mil.',
               'Melhor falar a verdade, ser leal.']
TAIL = 2.0
GAINS = {'ADEMIR': 0, 'DONA CÉLIA': 0, 'PARCEIRO': 0}
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
    lines, after = [], {}
    for raw in SCRIPT.read_text(encoding='utf-8').splitlines():
        if not raw.strip():
            continue
        voice, text = raw.split(': ', 1)
        first = find(voice, text, after.get(voice, 0))
        last = first + len([w for w in text.split() if norm(w)]) - 1
        after[voice] = last + 1
        lines.append((voice, text, first, last))
    return lines


LINES = read_script()


def N(p, k=0, after=0):
    return 'NARRADOR', find('NARRADOR', p, after) + k


def A(p, k=0):
    return 'ADEMIR', find('ADEMIR', p) + k


def C(p, k=0):
    return 'DONA CÉLIA', find('DONA CÉLIA', p) + k


def P(p, k=0):
    return 'PARCEIRO', find('PARCEIRO', p) + k


# Silence the edit opens after a word, in seconds. No silent pause to read the options (the
# final of 10/11/2026): only short beats.
PAUSES = {
    N('quem ele é.', 2): .7,                 # the hook lands
    N('Uma hora antes.', 2): .35,
    N('no bolso.', 1): .35,
    A('Gostei.'): .45,
    N('no jornal.', 1): .3,
    N('roubou o Ademir.', 2): .5,
    N('Desafinado.'): .7,                    # the light moment, before the turn
    N('ele não vê:', 2): .25,
    N('ao assalto.', 1): .3,
    N('pro jornal.', 1): .6,
    N('melhor amigo.', 1): .35,
    N('infância inteira.', 1): .5,
    N('pela metade.', 1): .45,
    A('Cadê ele?', 1): .4,
    N('quarto dos fundos.', 2): .5,
    N('em casa.', 1): .45,
    C('meu filho.', 1): .55,
    N('velho do Renato.', 2): .6,
    N('eram crianças.', 1): .4,
    P('te contou?', 1): .6,
    N('pro assalto.', 1): .3,
    N('com o dinheiro.', 2): .3,
    N('com a culpa.', 2): .7,
    N('em cima dela.', 2): .35,
    A('pro ferro-velho.', 1): .4,
    N('uma corda.', 1): .3,
    N('já trouxe.', 1): .6,
    N('por cinco milhões?', 2): 1.0,         # the question lands
    N('perde um filho.', 2): .5,
    N('alvo dele.', 1): .5,
    N('ou soltar.', 1): .3,
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


# Where the details land in the 720 × 1280 frame, measured on Codex's drawings (with each scene's crop).
ANEL_MESA = (190, 600)           # cena-01: the ring on the money
ANEL_VOLANTE = (398, 824)        # cena-04 (cropped): the ring on the wheel
ALICATE_BOLSO = (475, 709)       # cena-04 (cropped): the pliers in the jacket
CASA = (360, 520)                # cena-08: Dona Célia's house
MOLETOM = (100, 550)             # cena-10: the partner's hoodie on the chair
PRATOS = ((220, 720), (580, 530))
CORREDOR = (40, 560)             # cena-12: the dark corridor
MENINO = (262, 560)              # cena-16: the older boy in the photo
ALICATE_MESA = (304, 655)        # cena-21 (cropped): the pliers in the jacket
CROP_04 = (.1, .1, 1, 1)         # Ademir away from TikTok's buttons, Zinho kept on the left
CROP_13 = (.15, .3, .85, 1)      # the slippers up from the captions
CROP_21 = (.05, 0, .95, .9)      # Ademir's face down from the panel


def build(ed):
    s, e, cut, L = ed.s, ed.e, ed.cut, ed.L
    END, x = ed.END, L['x']
    v = bool(L['hud_dy'])                       # the vertical version
    hora = cut(N('Uma hora antes.'))
    plan = [
        # The hook, from the first frame: five million on the table (no vinheta, 10/11/2026).
        ('dinheiro', 0, art(desenho('cena-01-dinheiro-na-mesa.png'), .06)),
        ('contraluz', cut(N('você só precisa')), art(desenho('cena-02-homem-na-contraluz.png'), .05, direction='out')),
        # One hour earlier, in Ademir's car.
        ('carro', hora, art(desenho('cena-03-carro-no-bairro.png'), .05)),
        ('dirige', cut(N('Você está no carro')), art(desenho('cena-04-ademir-dirige.png'), .04, crop=CROP_04)),
        ('retrovisor', cut(A('Você me contou')), art(desenho('cena-05-retrovisor.png'), .05)),
        # What the vinheta used to tell, as a memory: Part 4's partner and the face on the news.
        ('lembranca', cut(N('Ele é o seu parceiro')), art('../episodio-04/cena-17-parceiro.png', .04, brightness=.8)),
        ('tv', cut(N('Sumiu com dez')), dict(kind='tv', asset=desenho('cena-03-carro-no-bairro.png'))),
        ('pagode', cut(N('No rádio,')), art(desenho('cena-06-pagode.png'), .05)),
        # The phone is normal-sized in the drawing, and the message is read on a close (12/11/2026).
        ('celular', cut(N('No banco de trás,')), art(desenho('cena-07-foto-recuperada.png'), .05)),
        ('lixeira', cut(N('recupera a única')), art(arte(f"close-lixeira{L['art']}.png"), .03)),
        ('recuperada', cut(N('Se ele te trair,')), art(arte(f"close-recuperada{L['art']}.png"), .03, direction='out')),
        # Dona Célia's house.
        ('casa', cut(N('O carro para')), art(desenho('cena-08-casa-da-mae.png'), .04)),
        ('infancia', cut(N('Você almoçou')), art(desenho('cena-09-infancia.png'), .04, direction='out')),
        ('pratos', cut(N('Hoje, na mesa,')), art(desenho('cena-10-dois-pratos.png'), .05)),
        ('bomdia', cut(A('Bom dia,')), art(desenho('cena-11-bom-dia.png'), .04)),
        ('olhar', cut(N('Ela não responde.')), art(desenho('cena-12-olhar-pro-quarto.png'), .05)),
        ('chinelo', cut(N('De lá sai')), art(desenho('cena-13-chinelo.png'), .04, crop=CROP_13)),
        ('meufilho', cut(C('Não machuca')), art(desenho('cena-14-meu-filho.png'), .04)),
        # The turn.
        ('irmao', cut(N('O homem que')), art(desenho('cena-15-irmao.png'), .06)),
        ('geladeira', cut(N('O filho que sumiu')), art(desenho('cena-16-foto-na-geladeira.png'), .05)),
        ('familia', cut(P('Família primeiro,')), art(desenho('cena-17-familia-primeiro.png'), .04)),
        ('traido', cut(N('O seu melhor amigo te')), art(desenho('cena-18-zinho-traido.png'), .06)),
        # The proposal.
        ('bolsas', cut(N('O Ademir puxa')), art(desenho('cena-19-bolsas.png'), .04)),
        ('virado', cut(N('E vira o dinheiro')), art(desenho('cena-20-dinheiro-virado.png'), .04, direction='out')),
        ('metade', cut(A('Metade é sua,')), art(desenho('cena-21-metade-e-sua.png'), .04, crop=CROP_21)),
        ('cadeira', cut(N('E no ferro-velho')), art(desenho('cena-22-cadeira-e-corda.png'), .05)),
        ('alicate', cut(N('O alicate,')), art('../episodio-06/cena-17-alicate.png', .04, brightness=.85)),
        # The question right at the turn, then the two options, short, with no silent pause.
        ('pergunta', cut(N('Você entregaria')), art(desenho('cena-23-pergunta.png'), .05, brightness=.6)),
        ('entregar', cut(N('Se entregar,')), art(desenho('cena-24-opcao-entregar.png'), .04)),
        ('soltar', cut(N('Se soltar,')), art(desenho('cena-25-opcao-soltar.png'), .04)),
        ('ameaca', cut(N('você ameaça')), art(arte(f"close-soltar{L['art']}.png"), .03)),
        ('escolha', cut(N('Comenta entregar')), art(arte(f"opcoes{L['art']}.png"), .02, direction='out')),
    ]
    plan.sort(key=lambda item: item[1])
    used = [f['asset'] for _, _, f in plan if f.get('asset') and f.get('kind', 'art') == 'art']
    repeated = sorted({a for a in used if used.count(a) > 1})
    if repeated:
        raise ValueError(f'drawings used more than once: {repeated}')
    AT = {name: t for name, t, _ in plan}
    nxt = {name: (plan[k+1][1] if k + 1 < len(plan) else END) for k, (name, _, _) in enumerate(plan)}
    scenes = [{'start': t, 'end': nxt[name], **fields} for name, t, fields in plan]
    perfil_fim = round(hora + 3.2, 2)
    jornal_at = round(s(N('O seu comentário')) - .05, 2)
    segue = s(N('Segue pra ver'))
    ty = L['tag_y']
    graphics = [
        # ---- the hook
        hud(0, hora, 'A SUA PARTE', 'R$ 5 MI?', 'yellow', L['hud_dy']),
        {'type': 'vignette', 'start': 0, 'end': AT['contraluz'], 'color': 'ink', 'strength': .55},
        phrase(0, AT['contraluz'], 960, [line('R$ 5 MILHÕES', 0, 'yellow', size=78),
                                         label('EM DINHEIRO VIVO NA MESA', 0)], 78, x),
        ring(s(N('em cima da mesa.')), AT['contraluz'], *ANEL_MESA, 60, 'yellow'),
        phrase(AT['contraluz'] + .05, hora, 960, [label('PRA FICAR COM ELES,', s(N('Pra ficar'))),
                                                  line('ENTREGUE UM HOMEM.', s(N('entregar um homem.')), size=50),
                                                  line('QUEM É ELE?', s(N('quem ele é.')), 'yellow', shake=True)], 56, x),
        {'type': 'vignette', 'start': AT['contraluz'], 'end': hora, 'color': 'alert', 'strength': .45},
        # ---- one hour earlier: the part's tag only now, after the hook (10/11/2026)
        phrase(hora + .05, AT['dirige'], 960, [line('UMA HORA ANTES', s(N('Uma hora antes.')), size=60)], 60, x),
        {'type': 'tag', 'start': hora + .1, 'end': perfil_fim, 'text': f'PARTE {PART}', 'y': ty, 'x': 112, 'size': 32},
        tag(f'PARTES 1 A {PART - 1} NO PERFIL', hora + .4, perfil_fim, ty + 52, 'white', size=20),
        hud(hora, AT['irmao'], 'A SUA PARTE', 'R$ 0', 'red', L['hud_dy']),
        hud(AT['irmao'], AT['virado'], 'O PARCEIRO É', 'O IRMÃO', 'red', L['hud_dy'], shake=True),
        hud(AT['virado'], AT['escolha'], 'A SUA PARTE', 'R$ 5 MI?', 'yellow', L['hud_dy'], shake=True),
        tag('O CARRO DO ADEMIR · 07:00', perfil_fim, AT['casa'], ty),
        tag('A CASA DA MÃE DO RENATO · 08:00', AT['casa'], AT['irmao'], ty),
        tag('A VIRADA', AT['irmao'], AT['bolsas'], ty, 'alert'),
        tag('A PROPOSTA', AT['bolsas'], AT['metade'], ty, 'alert'),
        # ---- the car
        nametag('ADEMIR', 'o homem mais perigoso do bairro', s(N('O Ademir,')), AT['retrovisor'], x),
        ring(s(N('anel de ouro')), AT['retrovisor'], *ANEL_VOLANTE, 55, 'yellow'),
        callout('UM ALICATE NO BOLSO', s(N('um alicate')), AT['retrovisor'], 250 if not v else 230, 1000 if not v else 980,
                ALICATE_BOLSO, 'alert'),
        balloon('Você me contou onde ele está. Lealdade. Gostei.', s(A('Você me contou')), AT['lembranca'], 360, (360, 600),
                y=700, width=500, L=L),
        phrase(s(A('Lealdade.')) - .05, AT['lembranca'], 900, [label('PARTE 6 · VOCÊS ESCOLHERAM', s(A('Lealdade.')) - .05)], 30, x),
        stamp('FALAR', s(A('Lealdade.')) - .02, AT['lembranca'], 975, x, 'yellow'),
        polaroid('episodio-04/cena-17-parceiro.png', [0.1, 0.25, 0.9, 0.6875], 'PARTE 4', 'o parceiro sumiu',
                 AT['lembranca'] + .05, AT['tv'], 175 if not v else 165, 560, 210, -5),
        phrase(AT['lembranca'] + .05, AT['tv'], 960, [label('O SEU PARCEIRO DO ASSALTO', s(N('Ele é o seu parceiro')))],
               40, x),
        phrase(AT['tv'] + .05, s(N('Roubou você.')) - .05, 1010 if not v else 990,
               [line('R$ 10 MILHÕES PRA ELE.', s(N('dez milhões')), 'green', size=44),
                label('O ROSTO NO JORNAL PRA VOCÊ.', s(N('te deixou só')))], 44, x),
        stamp('ROUBOU VOCÊ', s(N('Roubou você.')) - .02, s(N('E roubou o Ademir.')) - .05, 1010 if not v else 990, x,
              'red', angle=-6),
        stamp('E O ADEMIR', s(N('E roubou o Ademir.')) - .02, AT['pagode'], 1010 if not v else 990, x,
              'red', angle=5),
        # ---- the light moment
        pop('LÁ LAIÁ', s(N('canta junto.')), AT['celular'], 470 if not v else 440, 430, 50, 'yellow', -10),
        stamp('DESAFINADO', s(N('Desafinado.')) - .02, AT['celular'], 960, x, 'yellow'),
        # ---- the photo, on the screen itself (the phone faces the camera)
        phrase(AT['celular'] + .05, AT['lixeira'], 1030 if not v else 1000,
               [label('O QUE ELE NÃO VÊ', s(N('No banco de trás,')))], 40, x),
        tag('A ÚNICA PROVA CONTRA O ADEMIR', s(N('recupera a única')), AT['recuperada'], 960 if not v else 940, 'alert', x, 22),
        stamp('SUA ARMA', s(N('Se ele te trair,')) + .1, AT['casa'], 975 if not v else 955, x, 'red'),
        # ---- the house
        callout('A MÃE DO RENATO', s(N('a da Dona Célia,')), AT['infancia'], 250 if not v else 240, 400 if not v else 430,
                CASA, 'yellow'),
        polaroid('episodio-04/cena-13-renato-aceita.png', [0.15, 0.25, 0.85, 0.64], 'RENATO', 'o seu melhor amigo',
                 s(N('o seu melhor amigo.')), AT['infancia'], 545 if not v else 470, 880 if not v else 860, 200, 5),
        tag('15 ANOS ATRÁS', AT['infancia'] + .1, AT['pratos'], 960, 'white', x, 24),
        phrase(AT['pratos'] + .05, AT['bomdia'], 1000, [line('DOIS PRATOS', s(N('dois pratos')), 'yellow', size=56)], 56, x),
        ring(s(N('dois pratos')), AT['bomdia'], *PRATOS[0], 60, 'yellow'),
        ring(s(N('dois pratos')) + .15, AT['bomdia'], *PRATOS[1], 60, 'yellow'),
        callout('DE QUEM?', s(N('pela metade.')), AT['bomdia'], 260, 400 if not v else 430, MOLETOM, 'alert'),
        balloon('Bom dia, Dona Célia. Cadê ele?', s(A('Bom dia,')), AT['olhar'], 220 if not v else 200, (430, 470), y=600,
                width=360, L=L),
        nametag('DONA CÉLIA', 'a mãe do Renato', AT['olhar'] + .05, AT['chinelo'], x),
        phrase(AT['olhar'] + .05, AT['chinelo'], 1030 if not v else 1010, [label('ELA NÃO RESPONDE', s(N('Ela não responde.')))],
               40, x),
        callout('O QUARTO DOS FUNDOS', s(N('quarto dos fundos.')), AT['chinelo'], 220, 420 if not v else 445, CORREDOR, 'alert'),
        phrase(AT['chinelo'] + .05, AT['meufilho'], 960, [label('O SEU PARCEIRO DO ASSALTO', s(N('De lá sai'))),
                                                          line('DE CHINELO.', s(N('De chinelo,')), 'yellow', size=60)], 60, x),
        pop('PLOC', s(N('De chinelo,')), AT['meufilho'], 520 if not v else 470, 800, 50, 'white', 8),
        balloon('Não machuca ele. Ele é meu filho.', s(C('Não machuca')), AT['irmao'], 520 if not v else 490, (360, 560),
                y=420 if not v else 445, width=330, L=L),
        # ---- the turn
        nametag('O PARCEIRO', 'irmão mais velho do Renato', s(N('irmão mais velho')), AT['geladeira'], x),
        {'type': 'vignette', 'start': AT['irmao'], 'end': AT['familia'], 'color': 'alert', 'strength': .5},
        ring(s(N('O filho que sumiu')) + .2, AT['familia'], *MENINO, 80, 'red'),
        phrase(AT['geladeira'] + .05, AT['familia'], 960, [label('SUMIU DE CASA', s(N('sumiu de casa'))),
                                                           line('QUANDO VOCÊS', s(N('quando vocês')), size=48),
                                                           line('ERAM CRIANÇAS', s(N('eram crianças.')), 'yellow', size=48)],
               48, x),
        balloon('Família primeiro, Zinho.', s(P('Família primeiro,')), s(P('O Renato')), 175, (330, 470),
                y=420 if not v else 445, width=280, L=L),
        balloon('O Renato não te contou?', s(P('O Renato')), AT['traido'], 175, (330, 470), y=420 if not v else 445, width=280,
                L=L),
        polaroid('episodio-04/cena-13-renato-aceita.png', [0.15, 0.25, 0.85, 0.64], 'O SEU AMIGO', 'te levou pro assalto',
                 s(N('O seu melhor amigo te')), AT['bolsas'], 140, 420 if not v else 445, 190, -6),
        polaroid('episodio-04/cena-17-parceiro.png', [0.1, 0.25, 0.9, 0.6875], 'O IRMÃO', 'ficou com o dinheiro',
                 s(N('O irmão dele')), AT['bolsas'], 580 if not v else 470, 800 if not v else 830, 190, 5),
        stamp('SÓ A CULPA', s(N('E você ficou')) + .3, AT['bolsas'], 1000, x - 60, 'red'),
        # ---- the proposal
        pop('TUM', s(N('duas bolsas')), AT['virado'], 520 if not v else 470, 470, 54, 'white', -8),
        phrase(AT['virado'] + .05, AT['metade'], 1040 if not v else 1010,
               [line('R$ 10.000.000', s(N('E vira o dinheiro')), 'green', size=60,
                     count={'from': 0, 'to': 10000000, 'start': s(N('E vira o dinheiro')), 'end': e(N('em cima dela.', 2))})],
               60, x),
        balloon('Metade é sua, sócio. Cinco milhões.', s(A('Metade é sua,')), s(A('Mas ele vem')), 190, (330, 430), y=520,
                width=330, L=L),
        balloon('Mas ele vem comigo pro ferro-velho.', s(A('Mas ele vem')), AT['cadeira'], 190, (330, 430), y=520, width=330,
                L=L),
        ring(s(A('Mas ele vem')), AT['cadeira'], *ALICATE_MESA, 55, 'red'),
        phrase(AT['cadeira'] + .05, AT['alicate'], 1000, [line('UMA CADEIRA.', s(N('uma cadeira')), size=56),
                                                          line('UMA CORDA.', s(N('uma corda.')), 'red', size=56)], 56, x),
        phrase(AT['alicate'] + .05, AT['pergunta'], 1000,
                             [line('O ALICATE,', s(N('O alicate,')), size=56),
                              line('ELE JÁ TROUXE.', s(N('já trouxe.')), 'red', size=56)], 56, x),
        # ---- the question, right at the turn
        {'type': 'vignette', 'start': AT['pergunta'], 'end': AT['entregar'], 'color': 'ink', 'strength': .7},
        phrase(AT['pergunta'] + .05, AT['entregar'], 940 if not v else 930,
               [label('VOCÊ ENTREGARIA', s(N('Você entregaria'))),
                line('O IRMÃO DO SEU', s(N('o irmão do')), size=46),
                line('MELHOR AMIGO', s(N('melhor amigo por')), size=46),
                line('POR R$ 5 MILHÕES?', s(N('cinco milhões?', after=200)), 'yellow', size=50, shake=True)], 50, x),
        # ---- the options: one pro and one con each, while the narrator speaks
        tag('OPÇÃO 1 · ENTREGAR', AT['entregar'] + .05, AT['soltar'], 330 if not v else 360, 'white', x, 26),
        tag('+ R$ 5 MILHÕES NO SEU BOLSO', s(N('o dinheiro é seu,')), AT['soltar'], 960 if not v else 940, 'green', x, 22),
        tag('− A DONA CÉLIA PERDE UM FILHO', s(N('e a Dona Célia')), AT['soltar'], 1015 if not v else 995, 'alert', x, 22),
        tag('OPÇÃO 2 · SOLTAR', AT['soltar'] + .05, AT['escolha'], 330 if not v else 360, 'white', x, 26),
        tag('+ A DONA CÉLIA FICA COM O FILHO', s(N('você ameaça')), AT['escolha'], 960 if not v else 940, 'green', x, 22),
        tag('− VOCÊ VIRA O PRÓXIMO ALVO', s(N('E vira o próximo')), AT['escolha'], 1015 if not v else 995, 'alert', x, 22),
        # ---- the comment request with the newspaper, then follow and share
        {'type': 'buttons', 'start': round(s(N('Comenta entregar')) - .05, 2), 'end': jornal_at, 'y': 800,
         'x': x - (20 if v else 0), 'prompt': 'COMENTA UMA PALAVRA', 'prompt_at': round(s(N('Comenta entregar')), 2),
         'items': [{'text': 'ENTREGAR', 'at': round(s(N('entregar ou soltar.')), 2), 'style': 'yellow'},
                   {'text': 'SOLTAR', 'at': round(s(N('ou soltar.', 1)), 2), 'style': 'white'}]},
        {'type': 'vignette', 'start': jornal_at, 'end': END, 'color': 'ink', 'strength': .75},
        {'type': 'jornal', 'start': jornal_at, 'end': segue, 'y': 340 if v else 300, 'x': x,
         'width': 500 if v else 560, 'title': 'A VOZ DO BAIRRO', 'sub': f'o que vocês comentaram na parte {PART - 1}',
         'items': [{'text': c, 'at': round(jornal_at + .3 + .45*k, 2)} for k, c in enumerate(COMENTARIOS)]},
        phrase(jornal_at, segue, 960, [label('O SEU COMENTÁRIO PODE SAIR', s(N('O seu comentário'))),
                                       line('NO JORNAL DA', s(N('no jornal da'))),
                                       line('PRÓXIMA PARTE.', s(N('próxima parte.')), 'yellow')], 56, x),
        phrase(segue, END, 560, [line('SEGUE', segue, 'yellow', size=76), label('PRA VER A PARTE 8', s(N('a parte oito.')))],
               76, x),
        {'type': 'box', 'start': round(s(N('E manda esse')), 2), 'end': END, 'y': 860, 'x': x,
         'title': 'MANDA PRO AMIGO', 'sub': 'que te entregaria por bem menos'},
    ]
    effects = [
        *[sfx('whoosh.wav', AT[n] - WHOOSH_PEAK, -2) for n in ('contraluz', 'carro', 'lembranca', 'casa', 'irmao', 'traido',
                                                               'bolsas', 'pergunta', 'entregar', 'soltar', 'escolha')],
        sfx('impacto.wav', .05, -6),
        sfx('impacto.wav', s(N('quem ele é.')) - .04, -5),
        sfx('pop.wav', hora + .1, -12),
        sfx('pop.wav', s(N('O Ademir,')), -12),
        sfx('impacto-suave.wav', s(A('Lealdade.')) - .04, -7),
        sfx('impacto.wav', s(N('Roubou você.')) - .04, -7),
        sfx('impacto.wav', s(N('E roubou o Ademir.')) - .04, -7),
        sfx('pop.wav', s(N('um pagode')), -14),
        sfx('pop.wav', s(N('Desafinado.')), -10),
        sfx('notificacao.wav', s(N('recupera a única')), -12),
        sfx('impacto-suave.wav', s(N('Se ele te trair,')) + .1, -7),
        sfx('pop.wav', s(N('a da Dona Célia,')), -12),
        sfx('pop.wav', s(N('o seu melhor amigo.')), -12),
        sfx('pop.wav', s(N('dois pratos')), -12),
        sfx('passos.wav', s(N('De lá sai')), -12),
        sfx('impacto.wav', s(C('meu filho.')) - .04, -5),
        sfx('impacto.wav', s(N('irmão mais velho')) - .04, -4),
        sfx('pop.wav', s(N('O seu melhor amigo te')), -10),
        sfx('pop.wav', s(N('O irmão dele')), -10),
        sfx('impacto.wav', s(N('E você ficou')) + .26, -5),
        sfx('impacto-suave.wav', s(N('duas bolsas')), -6),
        *[sfx('tique.wav', s(N('E vira o dinheiro')) + .08*k, -18) for k in range(14)],
        sfx('impacto-suave.wav', s(N('uma corda.')) - .04, -7),
        sfx('impacto.wav', s(N('cinco milhões?', after=200)) - .04, -4),
        *[sfx('pop.wav', t, -14) for t in (s(N('o dinheiro é seu,')), s(N('e a Dona Célia')), s(N('você ameaça')),
                                          s(N('E vira o próximo')))],
        *[sfx('pop.wav', t, -10) for t in (s(N('entregar ou soltar.')), s(N('ou soltar.', 1)), s(N('E manda esse')))],
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
