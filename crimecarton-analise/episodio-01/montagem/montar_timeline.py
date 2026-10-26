#!/usr/bin/env python3
"""Build timeline.json for episode 1 from alinhamento-narracao.json and alinhamento-cta.json.

Cuts, graphics and sound effects are anchored to word numbers of the script (the "i"
field of the alignment), so the edit follows the voice again if the narration is
re-aligned. The audio this timeline uses, narracao-ep01-com-cta.wav, is the narration
with a pause opened after “Você escuta outra vez.” (the friend's key sentence plays again
and Zinho reacts) and the separately voiced request to comment appended, loudness-matched.
The look follows the series' reference video; see guia-de-estilo-referencia.md.

It also builds timeline-tiktok.json, the TikTok version: the same episode after a short
flash-forward, with the top elements moved below TikTok's search bar.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess

from gerar_efeitos import FRIEND_LINE, FRIEND_PAD, REPLAY_PAD, REPLAY_WORDS
import graficos

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
MAIN = EPISODE / 'narracao-original.wav'
FRIEND = HERE / 'efeitos' / 'audio-amigo.wav'
CTA = EPISODE / 'narracao-cta-ep01.wav'
AUDIO = EPISODE / 'narracao-ep01-com-cta.wav'
AUDIO_TIKTOK = EPISODE / 'narracao-ep01-com-cta-tiktok.wav'
TAIL = 1.2
# The TikTok version opens on a flash-forward, since most TikTok viewers of the first
# upload left within a second: Zinho's face as the friend's message plays, with the
# betrayal on screen from the first frame. The episode follows HOOK seconds later.
HOOK = 3.3
# TikTok's search bar covers the top 11.4% of the frame (146 px here), so on TikTok the
# HUD, the tags, the cards and the stamp over them move down below it.
TIKTOK_LAYOUT = {'hud_dy': 67, 'tag_y': 297, 'card_top': 334, 'stamp_y': 629}


def probe(path, entry):
    return subprocess.run(['ffprobe', '-v', 'error', '-show_entries', entry, '-of', 'csv=p=0', path],
                          check=True, capture_output=True, text=True).stdout.split()[0]


def loudness(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128', '-f', 'null', '-'],
                       check=True, capture_output=True, text=True)
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1])


WORDS = json.loads((HERE / 'alinhamento-narracao.json').read_text(encoding='utf-8'))['words']
CTA_WORDS = json.loads((HERE / 'alinhamento-cta.json').read_text(encoding='utf-8'))['words']
MAIN_DURATION = float(probe(MAIN, 'format=duration'))

# The pause opened after “Você escuta outra vez.”: a short breath, the replayed sentence,
# then Zinho's reaction. Everything the narration says afterwards moves later by GAP.
INSERT_AT = round(WORDS[141]['end'] + .34, 2)
REPLAY_LEN = round(WORDS[REPLAY_WORDS[1]]['end'] + REPLAY_PAD[1] - WORDS[REPLAY_WORDS[0]]['start'] + REPLAY_PAD[0], 2)
REACTION = 1.5
GAP = round(.15 + REPLAY_LEN + REACTION, 2)
END = round(MAIN_DURATION + GAP + float(probe(CTA, 'format=duration')) + TAIL, 2)


def later(t):
    return t + GAP if t >= INSERT_AT else t


def s(i):
    return later(WORDS[i]['start'])


def e(i):
    return later(WORDS[i]['end'])


def c(i):
    # Start of word i of the closing request, on the joined narration's clock.
    return MAIN_DURATION + GAP + CTA_WORDS[i]['start']


def cut(i, lead=.12):
    # Cuts land just before the word that opens the next shot.
    return round(s(i) - lead, 2)


REPLAY_AT = round(INSERT_AT + .15, 2)
REACT_AT = round(REPLAY_AT + REPLAY_LEN - REPLAY_PAD[1] + .02, 2)


def replayed(i):
    # When word i of the friend's line sounds again in the replay.
    return REPLAY_AT + REPLAY_PAD[0] + WORDS[i]['start'] - WORDS[REPLAY_WORDS[0]]['start']


def join_narration():
    # The friend's message plays in his own voice, audio-amigo.wav from voz_amigo.py, in
    # place of the narrator's reading; it has the same length, so the timing holds. The
    # closing request came out quieter than the episode's narration: match it. Float
    # samples keep the raised peaks for the final loudness pass.
    gain = loudness(MAIN) - loudness(CTA)
    rate = int(probe(MAIN, 'stream=sample_rate'))
    first = round((WORDS[FRIEND_LINE[0]]['start'] - FRIEND_PAD) * rate)
    last = first + int(probe(FRIEND, 'stream=duration_ts'))
    fmt = f'aformat=sample_fmts=flt:sample_rates={rate}:channel_layouts=mono'
    graph = (f'[0:a]{fmt},asplit=3[m1][m2][m3];[m1]atrim=end_sample={first}[a1];[2:a]{fmt}[friend];'
             f'[m2]atrim=start_sample={last}:end={INSERT_AT},asetpts=PTS-STARTPTS[a2];'
             f'[m3]atrim=start={INSERT_AT},asetpts=PTS-STARTPTS[b];aevalsrc=0:d={GAP}:s={rate}:c=mono,{fmt}[g];'
             f'[1:a]{fmt},volume={gain:.2f}dB[cta];[a1][friend][a2][g][b][cta]concat=n=6:v=0:a=1[out]')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', MAIN, '-i', CTA, '-i', FRIEND, '-filter_complex', graph,
                    '-map', '[out]', '-c:a', 'pcm_f32le', AUDIO], check=True)
    return gain


FACE01 = [0.25, 0.03, 0.85, 0.63]
HANDS01 = [0.10, 0.36, 0.75, 1.0]
CLOTHES03 = [0.0, 0.40, 0.60, 1.0]
BAG03 = [0.35, 0.38, 0.95, 0.98]
FACE03 = [0.225, 0.025, 0.775, 0.575]
FACE07 = [0.22, 0.03, 0.82, 0.63]
EYES07 = [0.34, 0.16, 0.74, 0.56]
CURTAIN09 = [0.0, 0.08, 0.60, 0.68]
FRIEND09 = [0.50, 0.11, 1.0, 0.61]
DOOR09 = [0.40, 0.40, 1.0, 1.0]
# Sound effects sit in the pauses of the voice, as in the reference.
STAMP_AT = round(e(104) + .08, 2)        # “A MESMA FOTO” lands in the pause after “fotografia.”
KNOCKS = (round(e(148) + .07, 2), round(e(148) + .33, 2))
WHOOSH_PEAK = .36                        # seconds from the start of whoosh.wav to its loudest point

# (name, start, scene fields). Each shot runs until the next one starts.
PLAN = [
    ('opening', 0, dict(kind='art', asset='cena-01-base.png', zoom=.06)),
    ('face', cut(10), dict(kind='art', asset='cena-01-base.png', crop=FACE01, zoom=.05)),
    ('tv', cut(17), dict(kind='tv', asset='cena-01-base.png')),
    ('hands', cut(25), dict(kind='art', asset='cena-01-base.png', crop=HANDS01, zoom=.04)),
    ('clothes', cut(37), dict(kind='art', asset='cena-03-roupas.png', crop=CLOTHES03, zoom=.03)),
    ('bag', cut(39), dict(kind='art', asset='cena-03-roupas.png', crop=BAG03, zoom=.03)),
    ('mess', cut(41), dict(kind='art', asset='cena-03-roupas.png', zoom=.05, direction='out')),
    ('nothing', cut(51), dict(kind='art', asset='cena-03-roupas.png', crop=FACE03, zoom=.04)),
    ('call', cut(52), dict(kind='art', asset='cena-07-audio.png', zoom=.04)),
    ('sent', cut(62), dict(kind='chat', asset='cena-07-audio.png', status='sent')),
    ('promise', cut(76), dict(kind='art', asset='cena-07-audio.png', crop=FACE07, zoom=.05)),
    ('seen', cut(90), dict(kind='chat', asset='cena-07-audio.png', status='seen')),
    ('tv-again', cut(94), dict(kind='tv', asset='cena-07-audio.png')),
    ('photos', cut(102, .08), dict(kind='comparison', asset='cena-07-audio.png')),
    ('audio', cut(118), dict(kind='audio', asset='cena-07-audio.png', brightness=.55, play=[s(FRIEND_LINE[0]), e(FRIEND_LINE[1])])),
    # Listening again: the marker runs with the replayed sentence, then the shot closes in on him.
    ('replay', cut(138), dict(kind='audio', asset='cena-07-audio.png', crop=FACE07, brightness=.6,
                              play=[REPLAY_AT, round(REPLAY_AT + REPLAY_LEN, 2)])),
    ('reaction', REACT_AT, dict(kind='art', asset='cena-07-audio.png', crop=EYES07, zoom=.1)),
    ('curtain', cut(142), dict(kind='art', asset='cena-09-porta.png', crop=CURTAIN09, zoom=.04)),
    ('window', cut(149), dict(kind='art', asset='cena-09-porta.png', zoom=.05)),
    ('friend', cut(155), dict(kind='art', asset='cena-09-porta.png', crop=FRIEND09, zoom=.05)),
    ('door', cut(166), dict(kind='art', asset='cena-09-porta.png', crop=DOOR09, zoom=.06, brightness=.5)),
    # The request to comment opens back onto the whole dilemma: Zinho inside, the friend outside.
    ('choice', round(c(0) - .12, 2), dict(kind='art', asset='cena-09-porta.png', zoom=.04, direction='out', brightness=.45)),
]
AT = {name: t for name, t, _ in PLAN}


def phrase(start, end, y, lines, size=78):
    return {'type': 'phrase', 'start': round(start, 2), 'end': round(end, 2), 'y': y, 'size': size, 'lines': lines}


def line(text, at, color='white', **kw):
    return {'text': text, 'at': round(at, 2), 'color': color, **kw}


def label(text, at, **kw):
    return {'style': 'label', 'text': text, 'at': round(at, 2), **kw}


def build():
    scenes = [{'start': t, 'end': PLAN[n+1][1] if n+1 < len(PLAN) else END, **fields}
              for n, (_, t, fields) in enumerate(PLAN)]
    graphics = [
        # Drawn first, under the rest: the red alarm while Zinho takes in what he heard.
        {'type': 'vignette', 'start': AT['reaction'], 'end': AT['curtain'], 'color': 'alert', 'strength': .9},
        phrase(.2, s(4) - .07, 700, [line('O ASSALTO', s(0)), line('DEU CERTO.', s(2), 'yellow')]),
        phrase(s(4) - .07, AT['face'], 700, [
            label('SEU PARCEIRO FICOU COM', s(4)),
            line('R$ 10.000.000', s(4) + .08, 'green', size=74,
                 count={'from': 0, 'to': 10000000, 'start': s(5), 'end': e(9) - .3}),
            label('EM DINHEIRO VIVO', s(8))]),
        phrase(AT['face'] + .05, AT['tv'], 880, [line('VOCÊ FICOU COM', s(10)), line('O ROSTO', s(14), 'yellow'),
                                                 line('NO JORNAL.', s(15), 'yellow')], 64),
        {'type': 'hud', 'start': round(s(22), 2), 'end': AT['door'], 'label': 'A SUA PARTE',
         'values': [{'at': round(s(22), 2), 'text': 'R$ ?', 'color': 'white'},
                    {'at': round(s(39), 2), 'text': 'R$ 0', 'color': 'red', 'shake': True}],
         'stars': [{'at': round(s(23), 2), 'count': 5, 'step': .12}]},
        {'type': 'tag', 'start': round(s(25), 2), 'end': AT['sent'], 'text': 'PISTA 1 · A MOCHILA'},
        phrase(AT['clothes'], AT['mess'], 640, [line('ROUPA VELHA.', s(37)), line('NENHUMA NOTA.', s(39), 'yellow')], 66),
        {'type': 'list', 'start': round(s(41), 2), 'end': AT['nothing'], 'y': 600, 'items': [
            {'at': round(s(43), 2), 'left': 'BOLSOS', 'right': 'VAZIOS'},
            {'at': round(s(46), 2), 'left': 'FUNDO', 'right': 'VAZIO'},
            {'at': round(s(49), 2), 'left': 'NO CHÃO', 'right': 'SÓ ROUPA'}]},
        phrase(AT['nothing'], AT['call'], 920, [line('NADA.', s(51), shake=True)], 120),
        phrase(AT['call'], s(59) - .1, 900, [label('HÁ 20 MINUTOS', s(52)), line('VOCÊS ESTAVAM', s(55)),
                                             line('JUNTOS.', s(58), 'yellow')], 64),
        phrase(s(59) - .1, AT['sent'], 900, [line('AGORA,', s(59)), line('NINGUÉM ATENDE.', s(60), 'yellow')], 62),
        {'type': 'tag', 'start': round(s(62), 2), 'end': AT['tv-again'], 'text': 'PISTA 2 · O SILÊNCIO'},
        phrase(s(83) - .1, AT['seen'], 910, [label('ELE PROMETEU', s(83)), line('“EU GARANTO', s(85)),
                                             line('A SUA PARTE.”', s(87), 'yellow')], 64),
        {'type': 'tag', 'start': round(s(94), 2), 'end': AT['audio'], 'text': 'PISTA 3 · A FOTO'},
        {'type': 'stamp', 'start': STAMP_AT, 'end': AT['audio'], 'text': 'A MESMA FOTO', 'y': 595, 'angle': -7},
        {'type': 'tag', 'start': round(s(118), 2), 'end': AT['curtain'], 'text': 'PISTA 4 · O ÁUDIO'},
        phrase(s(121) - .05, s(126) - .1, 560, [line('“EU ESTAVA', s(121)), line('DEVENDO', s(123)),
                                                line('PARA ELES.', s(124), 'yellow')], 60),
        phrase(s(126) - .1, AT['replay'], 560, [line('A DÍVIDA ACABAVA', s(126)), line('SE EU COLOCASSE', s(131)),
                                                line('ALGUÉM NO', s(134), 'yellow'), line('MEU LUGAR.”', s(136), 'yellow')], 58),
        # The replay brings back the words that matter, on their sounds.
        phrase(REPLAY_AT, AT['reaction'], 540, [line('“SE EU COLOCASSE', replayed(131)), line('ALGUÉM NO', replayed(134), 'yellow'),
                                                line('MEU LUGAR.”', replayed(136), 'yellow')], 60),
        phrase(KNOCKS[0] - .05, AT['window'], 880, [line('TOC!', KNOCKS[0], shake=True),
                                                    line('TOC!', KNOCKS[1], 'yellow', shake=True)], 96),
        phrase(s(163) - .05, AT['door'], 930, [line('VENDEU', s(163)), line('SEU NOME.', s(164), 'yellow')], 72),
        # The closing block stays on screen to the last frame, as in the reference.
        phrase(AT['door'], END + .5, 420, [line('VOCÊ DEIXA', s(166)), line('ELE ENTRAR?', s(168), 'yellow')], 76),
        # The request to comment: each button and the box enter on their spoken words.
        {'type': 'buttons', 'start': round(c(0) - .05, 2), 'end': END + .5, 'y': 720, 'prompt': 'COMENTA UMA PALAVRA',
         'prompt_at': round(c(0), 2), 'items': [{'text': 'ABRIR', 'at': round(c(4), 2), 'style': 'yellow'},
                                                {'text': 'NÃO ABRIR', 'at': round(c(6), 2), 'style': 'white'}]},
        {'type': 'box', 'start': round(c(15), 2), 'end': END + .5, 'y': 880, 'title': 'PARTE 2',
         'sub': 'a maioria decide o próximo passo'},
    ]
    return scenes, graphics, sound_effects()


def sfx(sound, at, gain):
    return {'sound': sound, 'at': round(at, 3), 'gain': gain}


def sound_effects():
    # Whooshes on the chapter changes, ticks while the money counts, impacts on the
    # losses, the stamp and Zinho's reaction, and the concrete sounds the narration mentions.
    count_start, count_end = s(5), e(9) - .3
    ticks = [sfx('tique.wav', count_start + (count_end - count_start)*(1 - (1 - k/14)**(1/3)), -18) for k in range(1, 15)]
    return [
        *[sfx('whoosh.wav', AT[name] - WHOOSH_PEAK, -2) for name in ('tv', 'hands', 'sent', 'tv-again', 'door', 'choice')],
        *ticks,
        sfx('impacto-suave.wav', s(39) - .08, -10),
        sfx('impacto.wav', s(51) - .1, -5),
        sfx('chamada.wav', e(58) + .03, -24),
        sfx('impacto.wav', STAMP_AT - .02, -5),
        sfx('notificacao.wav', e(117) + .18, -8),
        sfx('replay-amigo.wav', REPLAY_AT, 2),
        sfx('impacto.wav', AT['reaction'] - .02, -4),
        sfx('batida-1.wav', KNOCKS[0], -2),
        sfx('batida-2.wav', KNOCKS[1], -3),
        *[sfx('pop.wav', at, -10) for at in (c(4), c(6), c(15))],
    ]


TIME_KEYS = {'start', 'end', 'at', 'prompt_at'}


def shifted(item, by):
    # The same scenes, graphics or effects, every time in them `by` seconds later.
    if isinstance(item, list):
        return [shifted(v, by) for v in item]
    if not isinstance(item, dict):
        return item
    return {k: round(v + by, 3) if k in TIME_KEYS else [round(p + by, 3) for p in v] if k == 'play' else shifted(v, by)
            for k, v in item.items()}


def tiktok_version(scenes, graphics, effects):
    hook_scene = {'start': 0, 'end': HOOK, 'kind': 'art', 'asset': 'cena-07-audio.png', 'crop': EYES07, 'zoom': .1}
    scenes = [hook_scene] + [dict(s, card_top=TIKTOK_LAYOUT['card_top']) if s['kind'] in ('tv', 'chat', 'comparison') else s
                             for s in shifted(scenes, HOOK)]
    moved = {'hud': {'dy': TIKTOK_LAYOUT['hud_dy']}, 'tag': {'y': TIKTOK_LAYOUT['tag_y']}, 'stamp': {'y': TIKTOK_LAYOUT['stamp_y']}}
    hook = [
        {'type': 'vignette', 'start': 0, 'end': HOOK, 'color': 'alert', 'strength': .9},
        # Both lines "entered" just before the first frame, so they are already there.
        phrase(0, HOOK - .1, 900, [line('SEU AMIGO', -.07), line('TE VENDEU.', -.07, 'yellow', shake=True)], 84),
    ]
    graphics = hook + [dict(g, **moved.get(g['type'], {})) for g in shifted(graphics, HOOK)]
    effects = [sfx('impacto.wav', 0, -4), sfx('replay-amigo.wav', .3, 2), sfx('whoosh.wav', HOOK - WHOOSH_PEAK, -2),
               *shifted(effects, HOOK)]
    return scenes, graphics, effects


def tiktok_audio():
    # The same narration, HOOK seconds later: the flash-forward plays over silence.
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', AUDIO, '-af', f'adelay={round(HOOK*1000)}:all=1',
                    '-c:a', 'pcm_f32le', AUDIO_TIKTOK], check=True)


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
    # timeline.json is the Instagram version; timeline-tiktok.json, the TikTok one.
    versions = {'timeline.json': (scenes, graphics, effects, AUDIO, 0),
                'timeline-tiktok.json': (*tiktok_version(scenes, graphics, effects), AUDIO_TIKTOK, HOOK)}
    for _, g, _, _, _ in versions.values():
        wide = too_wide(g)
        if wide:
            raise ValueError(f'Lines wider than the safe area: {wide}')
        graficos.check(g)
    gain = join_narration()
    tiktok_audio()
    for name, (sc, g, ef, audio, hook) in versions.items():
        timeline = {'timing_status': 'aligned_to_voice', 'style': 'guia-de-estilo-referencia.md',
                    'alignment': ['alinhamento-narracao.json', 'alinhamento-cta.json'], 'audio': audio.name, 'tail': TAIL,
                    'opening_hook_seconds': hook, 'pause_after_listen_again': {'at': round(INSERT_AT + hook, 3), 'seconds': GAP},
                    'scenes': sc, 'graphics': g, 'sfx': ef, 'captions': []}
        (HERE / name).write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f'{name}: {len(sc)} scenes, {len(g)} graphics, {len(ef)} sound effects, ends at {round(END + hook, 2)}s')
    print(f'{AUDIO.name}: {GAP}s pause at {INSERT_AT}s; closing request raised {gain:+.1f} dB to match the narration')


if __name__ == '__main__':
    main()
