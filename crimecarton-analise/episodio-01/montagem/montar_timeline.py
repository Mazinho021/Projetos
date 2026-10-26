#!/usr/bin/env python3
"""Build timeline.json for episode 1 from alinhamento-narracao.json and alinhamento-cta.json.

Cuts and graphics are anchored to word numbers of the script (the "i" field of the
alignment), so the edit follows the voice again if the narration is re-aligned.
The closing request to comment was voiced separately; it is loudness-matched and
appended to the narration in narracao-ep01-com-cta.wav, the audio this timeline uses.
The look follows the series' reference video; see guia-de-estilo-referencia.md.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess

import graficos

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
MAIN = EPISODE / 'narracao-original.wav'
CTA = EPISODE / 'narracao-cta-ep01.wav'
AUDIO = EPISODE / 'narracao-ep01-com-cta.wav'
TAIL = 1.2


def duration(path):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', path],
                                check=True, capture_output=True, text=True).stdout)


def loudness(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128', '-f', 'null', '-'],
                       check=True, capture_output=True, text=True)
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1])


def join_narration():
    # The closing request came out quieter than the episode's narration: match it and
    # append it. Float samples keep the raised peaks for the final loudness pass.
    gain = loudness(MAIN) - loudness(CTA)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', MAIN, '-i', CTA, '-filter_complex',
                    f'[1:a]volume={gain:.2f}dB[c];[0:a][c]concat=n=2:v=0:a=1[a]', '-map', '[a]', '-c:a', 'pcm_f32le', AUDIO],
                    check=True)
    return gain


WORDS = json.loads((HERE / 'alinhamento-narracao.json').read_text(encoding='utf-8'))['words']
CTA_WORDS = json.loads((HERE / 'alinhamento-cta.json').read_text(encoding='utf-8'))['words']
MAIN_DURATION = duration(MAIN)
END = round(MAIN_DURATION + duration(CTA) + TAIL, 2)


def s(i):
    return WORDS[i]['start']


def e(i):
    return WORDS[i]['end']


def c(i):
    # Start of word i of the closing request, on the joined narration's clock.
    return MAIN_DURATION + CTA_WORDS[i]['start']


def cut(i, lead=.12):
    # Cuts land just before the word that opens the next shot.
    return round(s(i) - lead, 2)


FACE01 = [0.25, 0.03, 0.85, 0.63]
HANDS01 = [0.10, 0.36, 0.75, 1.0]
CLOTHES03 = [0.0, 0.40, 0.60, 1.0]
BAG03 = [0.35, 0.38, 0.95, 0.98]
FACE03 = [0.225, 0.025, 0.775, 0.575]
FACE07 = [0.22, 0.03, 0.82, 0.63]
CURTAIN09 = [0.0, 0.08, 0.60, 0.68]
FRIEND09 = [0.50, 0.11, 1.0, 0.61]
DOOR09 = [0.40, 0.40, 1.0, 1.0]
FRIEND_LINE = (121, 137)  # “Eu estava devendo … no meu lugar.”
# Sound effects sit in the pauses of the voice, as in the reference.
REPLAY_AT = round(e(141) + .04, 2)       # the friend's line restarts after “Você escuta outra vez.”
STAMP_AT = round(e(104) + .08, 2)        # “A MESMA FOTO” lands in the pause after “fotografia.”
KNOCKS = (round(e(148) + .07, 2), round(e(148) + .33, 2))
WHOOSH_PEAK = .36                        # seconds from the start of whoosh.wav to its loudest point

PLAN = [
    (0, dict(kind='art', asset='cena-01-base.png', zoom=.06)),
    (cut(10), dict(kind='art', asset='cena-01-base.png', crop=FACE01, zoom=.05)),
    (cut(17), dict(kind='tv', asset='cena-01-base.png')),
    (cut(25), dict(kind='art', asset='cena-01-base.png', crop=HANDS01, zoom=.04)),
    (cut(37), dict(kind='art', asset='cena-03-roupas.png', crop=CLOTHES03, zoom=.03)),
    (cut(39), dict(kind='art', asset='cena-03-roupas.png', crop=BAG03, zoom=.03)),
    (cut(41), dict(kind='art', asset='cena-03-roupas.png', zoom=.05, direction='out')),
    (cut(51), dict(kind='art', asset='cena-03-roupas.png', crop=FACE03, zoom=.04)),
    (cut(52), dict(kind='art', asset='cena-07-audio.png', zoom=.04)),
    (cut(62), dict(kind='chat', asset='cena-07-audio.png', status='sent')),
    (cut(76), dict(kind='art', asset='cena-07-audio.png', crop=FACE07, zoom=.05)),
    (cut(90), dict(kind='chat', asset='cena-07-audio.png', status='seen')),
    (cut(94), dict(kind='tv', asset='cena-07-audio.png')),
    (cut(102, .08), dict(kind='comparison', asset='cena-07-audio.png')),
    (cut(118), dict(kind='audio', asset='cena-07-audio.png', brightness=.55, play=[s(FRIEND_LINE[0]), e(FRIEND_LINE[1])])),
    # Listening again: the marker restarts at the speed of the real line and is cut off by the knock.
    (cut(138), dict(kind='audio', asset='cena-07-audio.png', crop=FACE07, play='replay')),
    (cut(142), dict(kind='art', asset='cena-09-porta.png', crop=CURTAIN09, zoom=.04)),
    (cut(149), dict(kind='art', asset='cena-09-porta.png', zoom=.05)),
    (cut(155), dict(kind='art', asset='cena-09-porta.png', crop=FRIEND09, zoom=.05)),
    (cut(166), dict(kind='art', asset='cena-09-porta.png', crop=DOOR09, zoom=.06, brightness=.5)),
    # The request to comment opens back onto the whole dilemma: Zinho inside, the friend outside.
    (round(c(0) - .12, 2), dict(kind='art', asset='cena-09-porta.png', zoom=.04, direction='out', brightness=.45)),
]


def phrase(start, end, y, lines, size=78):
    return {'type': 'phrase', 'start': round(start, 2), 'end': round(end, 2), 'y': y, 'size': size, 'lines': lines}


def line(text, at, color='white', **kw):
    return {'text': text, 'at': round(at, 2), 'color': color, **kw}


def label(text, at, **kw):
    return {'style': 'label', 'text': text, 'at': round(at, 2), **kw}


def build():
    scenes = []
    for n, (t, fields) in enumerate(PLAN):
        scene = {'start': t, 'end': PLAN[n+1][0] if n+1 < len(PLAN) else END, **fields}
        if scene.get('play') == 'replay':
            scene['play'] = [REPLAY_AT, round(REPLAY_AT + e(FRIEND_LINE[1]) - s(FRIEND_LINE[0]), 2)]
        scenes.append(scene)
    cuts = [scene['start'] for scene in scenes]
    graphics = [
        phrase(.2, s(4) - .07, 700, [line('O ASSALTO', s(0)), line('DEU CERTO.', s(2), 'yellow')]),
        phrase(s(4) - .07, cuts[1], 700, [
            label('SEU PARCEIRO FICOU COM', s(4)),
            line('R$ 10.000.000', s(4) + .08, 'green', size=74,
                 count={'from': 0, 'to': 10000000, 'start': s(5), 'end': e(9) - .3}),
            label('EM DINHEIRO VIVO', s(8))]),
        phrase(cuts[1] + .05, cuts[2], 880, [line('VOCÊ FICOU COM', s(10)), line('O ROSTO', s(14), 'yellow'),
                                             line('NO JORNAL.', s(15), 'yellow')], 64),
        {'type': 'hud', 'start': round(s(22), 2), 'end': cuts[19], 'label': 'A SUA PARTE',
         'values': [{'at': round(s(22), 2), 'text': 'R$ ?', 'color': 'white'},
                    {'at': round(s(39), 2), 'text': 'R$ 0', 'color': 'red', 'shake': True}],
         'stars': [{'at': round(s(23), 2), 'count': 5, 'step': .12}]},
        {'type': 'tag', 'start': round(s(25), 2), 'end': cuts[9], 'text': 'PISTA 1 · A MOCHILA'},
        phrase(cuts[4], cuts[6], 640, [line('ROUPA VELHA.', s(37)), line('NENHUMA NOTA.', s(39), 'yellow')], 66),
        {'type': 'list', 'start': round(s(41), 2), 'end': cuts[7], 'y': 600, 'items': [
            {'at': round(s(43), 2), 'left': 'BOLSOS', 'right': 'VAZIOS'},
            {'at': round(s(46), 2), 'left': 'FUNDO', 'right': 'VAZIO'},
            {'at': round(s(49), 2), 'left': 'NO CHÃO', 'right': 'SÓ ROUPA'}]},
        phrase(cuts[7], cuts[8], 920, [line('NADA.', s(51), shake=True)], 120),
        phrase(cuts[8], s(59) - .1, 900, [label('HÁ 20 MINUTOS', s(52)), line('VOCÊS ESTAVAM', s(55)),
                                          line('JUNTOS.', s(58), 'yellow')], 64),
        phrase(s(59) - .1, cuts[9], 900, [line('AGORA,', s(59)), line('NINGUÉM ATENDE.', s(60), 'yellow')], 62),
        {'type': 'tag', 'start': round(s(62), 2), 'end': cuts[12], 'text': 'PISTA 2 · O SILÊNCIO'},
        phrase(s(83) - .1, cuts[11], 910, [label('ELE PROMETEU', s(83)), line('“EU GARANTO', s(85)),
                                           line('A SUA PARTE.”', s(87), 'yellow')], 64),
        {'type': 'tag', 'start': round(s(94), 2), 'end': cuts[14], 'text': 'PISTA 3 · A FOTO'},
        {'type': 'stamp', 'start': STAMP_AT, 'end': cuts[14], 'text': 'A MESMA FOTO', 'y': 595, 'angle': -7},
        {'type': 'tag', 'start': round(s(118), 2), 'end': cuts[16], 'text': 'PISTA 4 · O ÁUDIO'},
        phrase(s(121) - .05, s(126) - .1, 560, [line('“EU ESTAVA', s(121)), line('DEVENDO', s(123)),
                                                line('PARA ELES.', s(124), 'yellow')], 60),
        phrase(s(126) - .1, cuts[15], 560, [line('A DÍVIDA ACABAVA', s(126)), line('SE EU COLOCASSE', s(131)),
                                            line('ALGUÉM NO', s(134), 'yellow'), line('MEU LUGAR.”', s(135), 'yellow')], 58),
        phrase(KNOCKS[0] - .05, cuts[17], 880, [line('TOC!', KNOCKS[0], shake=True),
                                                line('TOC!', KNOCKS[1], 'yellow', shake=True)], 96),
        phrase(s(163) - .05, cuts[19], 930, [line('VENDEU', s(163)), line('SEU NOME.', s(164), 'yellow')], 72),
        # The closing block stays on screen to the last frame, as in the reference.
        phrase(cuts[19], END + .5, 420, [line('VOCÊ DEIXA', s(166)), line('ELE ENTRAR?', s(168), 'yellow')], 76),
        # The request to comment: each button and the box enter on their spoken words.
        {'type': 'buttons', 'start': round(c(0) - .05, 2), 'end': END + .5, 'y': 720, 'prompt': 'COMENTA UMA PALAVRA',
         'prompt_at': round(c(0), 2), 'items': [{'text': 'ABRIR', 'at': round(c(4), 2), 'style': 'yellow'},
                                                {'text': 'NÃO ABRIR', 'at': round(c(6), 2), 'style': 'white'}]},
        {'type': 'box', 'start': round(c(15), 2), 'end': END + .5, 'y': 880, 'title': 'PARTE 2',
         'sub': 'a maioria decide o próximo passo'},
    ]
    return scenes, graphics, sound_effects(cuts)


def sfx(sound, at, gain):
    return {'sound': sound, 'at': round(at, 3), 'gain': gain}


def sound_effects(cuts):
    # Whooshes on the chapter changes, ticks while the money counts, impacts on the
    # losses and the stamp, and the concrete sounds the narration mentions.
    count_start, count_end = s(5), e(9) - .3
    ticks = [sfx('tique.wav', count_start + (count_end - count_start)*(1 - (1 - k/14)**(1/3)), -18) for k in range(1, 15)]
    return [
        *[sfx('whoosh.wav', cuts[n] - WHOOSH_PEAK, -2) for n in (2, 3, 9, 12, 19, 20)],
        *ticks,
        sfx('impacto-suave.wav', s(39) - .08, -10),
        sfx('impacto.wav', s(51) - .1, -5),
        sfx('chamada.wav', e(58) + .03, -24),
        sfx('impacto.wav', STAMP_AT - .02, -5),
        sfx('notificacao.wav', e(117) + .18, -8),
        sfx('replay-amigo.wav', REPLAY_AT, -3),
        sfx('batida-1.wav', KNOCKS[0], -2),
        sfx('batida-2.wav', KNOCKS[1], -3),
        *[sfx('pop.wav', at, -10) for at in (c(4), c(6), c(15))],
    ]


def too_wide(graphics, limit=570):
    # Lines must stay clear of the buttons that TikTok and Reels draw on the right.
    wide = []
    for g in graphics:
        for ln in g['lines'] if g['type'] == 'phrase' else []:
            if ln.get('style') == 'label':
                size = ln.get('size', 22)
                f = graficos.font(size, 'SemiBold')
                width = sum(f.getlength(ch) for ch in ln['text']) + round(size*.22)*(len(ln['text'])-1)
            else:
                size = ln.get('size', g['size'])
                width = graficos.font(size, ln.get('weight', 'Bold')).getlength(ln['text'])
            if width > limit:
                wide.append((ln['text'], size, round(width)))
    return wide


def main():
    scenes, graphics, effects = build()
    wide = too_wide(graphics)
    if wide:
        raise ValueError(f'Lines wider than the safe area: {wide}')
    graficos.check(graphics)
    gain = join_narration()
    timeline = {'timing_status': 'aligned_to_voice', 'style': 'guia-de-estilo-referencia.md',
                'alignment': ['alinhamento-narracao.json', 'alinhamento-cta.json'], 'audio': AUDIO.name, 'tail': TAIL,
                'scenes': scenes, 'graphics': graphics, 'sfx': effects, 'captions': []}
    (HERE / 'timeline.json').write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{AUDIO.name}: closing request raised {gain:+.1f} dB to match the narration')
    print(f'{len(scenes)} scenes, {len(graphics)} graphics, {len(effects)} sound effects, ends at {END}s')


if __name__ == '__main__':
    main()
