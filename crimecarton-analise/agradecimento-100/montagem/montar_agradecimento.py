#!/usr/bin/env python3
"""Build the thank-you video for the profile's first 100 followers.

About 14 seconds, vertical, in the look of the series and with no voice, so it costs no
credits: the sound is the effects Part 1 already has. Writes, in agradecimento-100/:

  zinho-obrigado.png   Zinho's smiling portrait cut to 9:16, with a dark gradient at the
                       bottom so the thanks stay readable
  silencio.wav         the (silent) voice track the renderer expects
  montagem/timeline.json

The beats: the series' hook with the panel at “R$ 0” (“O assalto deu certo.”), the twist
(“Mas a sua parte era outra.”), the counter running up to 100 followers with confetti, the
thanks over the smiling portrait, and a teaser of Part 3 over the car at the gate. Every
text and time is in build() below. Render the result with render_agradecimento.py.

Layout follows the other vertical videos: lines no wider than 570 px, clear of the buttons
on the right, and everything between y = 190 and y = 1010, clear of the bars that Stories,
Reels and TikTok draw over the top and bottom of the frame.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent                      # agradecimento-100/: where the timeline's assets are looked up
SERIES = ROOT.parent                    # crimecarton-analise/
sys.path.insert(0, str(SERIES / 'episodio-01' / 'montagem'))
sys.path.insert(0, str(HERE))

import confete  # noqa: E402,F401  (registers the "confetti" graphics element)
import graficos  # noqa: E402

END = 14.4
TAIL = 1.0                              # the last shot holds, in silence, after the (silent) voice track
WHOOSH_PEAK = .36                       # seconds from the start of whoosh.wav to its loudest point
LIMIT = 570
LAND = 7.55                             # the counter reaches 100: impact, notification, confetti, panel turns green


def portrait():
    """Zinho's smiling portrait (retrato-zinho.png, 3:2) cut to 9:16 around his face, with a
    gradient from the shoulders down: the wall behind him is cream, too light for white text."""
    src = Image.open(SERIES / 'episodio-01' / 'retrato-zinho.png').convert('RGB')
    w, h = src.size
    width = round(h*9/16)
    left = min(max(0, round(w*.485 - width/2)), w - width)
    im = src.crop((left, 0, left + width, h)).resize((1080, 1920), Image.Resampling.LANCZOS).convert('RGBA')
    shade = Image.new('RGBA', im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(shade)
    top, full = round(1920*.46), round(1920*.76)
    for y in range(top, 1920):
        x = min(1, (y - top)/(full - top))
        d.line((0, y, 1080, y), fill=(14, 11, 8, round(235*x*x*(3 - 2*x))))
    out = ROOT / 'zinho-obrigado.png'
    Image.alpha_composite(im, shade).convert('RGB').save(out)
    return out


def silence():
    # The renderer takes the video's length from its voice track. This one is empty.
    out = ROOT / 'silencio.wav'
    subprocess.run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'error', '-f', 'lavfi', '-i', 'anullsrc=r=48000:cl=mono',
                    '-t', str(round(END - TAIL, 2)), '-c:a', 'pcm_s16le', out], check=True)
    return out


def phrase(start, end, y, lines, size=78):
    return {'type': 'phrase', 'start': round(start, 2), 'end': round(end, 2), 'y': y, 'size': size, 'lines': lines}


def line(text, at, color='white', **kw):
    return {'text': text, 'at': round(at, 2), 'color': color, **kw}


def label(text, at, **kw):
    return {'style': 'label', 'text': text, 'at': round(at, 2), **kw}


def sfx(sound, at, gain):
    return {'sound': sound, 'at': round(at, 3), 'gain': gain}


def ticks(start, end, n=22, gain=-16):
    # One tick each time the counter passes a step; it eases out, so the ticks bunch up at the start.
    return [sfx('tique.wav', start + (end - start)*(1 - (1 - k/n)**(1/3)), gain) for k in range(1, n + 1)]


def too_wide(graphics):
    wide = []
    for g in graphics:
        for ln in g['lines'] if g['type'] == 'phrase' else []:
            if ln.get('style') == 'label':
                size = ln.get('size', 22)
                f = graficos.font(size, 'SemiBold')
                width = sum(f.getlength(ch) for ch in ln['text']) + round(size*.22)*(len(ln['text']) - 1)
            else:
                size = ln.get('size', g['size'])
                width = graficos.font(size, ln.get('weight', 'Bold')).getlength(ln['text'])
            if width > LIMIT:
                wide.append((ln['text'], size, round(width)))
    return wide


def build():
    bag, count, thanks, nxt = 2.8, 5.4, 8.9, 11.9      # where each shot starts
    count_from, count_to = 5.65, 7.5                    # the counter's run from 0 to 100
    scenes = [
        # The series' hook, dark enough for the panel and the phrase.
        dict(start=0, end=bag, kind='art', asset='../episodio-01/cena-01-base.png', zoom=.06, brightness=.72),
        # The profile illustration, framed on Zinho and the open backpack: worried, old clothes.
        dict(start=bag, end=count, kind='art', asset='../perfil/ilustracao-perfil.png', crop=[.24, .02, .76, .94],
             zoom=.06, brightness=.7),
        # The black card of the series' opening, for the number.
        dict(start=count, end=thanks, kind='black'),
        # The only smiling Zinho there is, for the thanks.
        dict(start=thanks, end=nxt, kind='art', asset='zinho-obrigado.png', zoom=.05),
        # The car at the gate from the end of Part 2, for the teaser.
        dict(start=nxt, end=END, kind='art', asset='../episodio-02/cena-07-carro.png', zoom=.06, brightness=.5),
    ]
    graphics = [
        # Drawn first, under the rest: the red edge of the teaser, and the confetti.
        {'type': 'vignette', 'start': nxt, 'end': END + .5, 'color': 'alert', 'strength': .6},
        {'type': 'confetti', 'start': LAND, 'end': round(LAND + 3.4, 2), 'x': 360, 'y': 600, 'count': 110},
        # The first line is already on screen in the first frame.
        phrase(0, bag - .08, 700, [line('O ASSALTO', -.07), line('DEU CERTO.', .75, 'yellow')], 78),
        phrase(bag + .08, count - .1, 880, [line('MAS A SUA PARTE', bag + .15),
                                            line('ERA OUTRA.', bag + .9, 'yellow', size=92, shake=True)], 62),
        phrase(count + .05, thanks - .1, 640, [
            label('AGORA SÃO', count + .1, size=28, color='yellow'),
            {'text': '100', 'at': count + .2, 'color': 'green', 'size': 240,
             'count': {'from': 0, 'to': 100, 'start': count_from, 'end': count_to, 'format': '{}'}},
            line('SEGUIDORES.', LAND, size=64)], 64),
        phrase(thanks + .1, nxt - .1, 870, [line('OBRIGADO!', thanks + .2, 'yellow', size=94, shake=True),
                                            line('A CADA UM', thanks + .9, size=56),
                                            line('DE VOCÊS.', thanks + 1.25, size=56)], 56),
        phrase(nxt + .15, END + .5, 850, [label('A PARTE 3', nxt + .2, size=28, color='yellow'),
                                          line('TÁ A CAMINHO.', nxt + .5, size=64)], 64),
        # The panel of the series: Zinho's share, still nothing until the counter lands.
        {'type': 'hud', 'start': -.3, 'end': thanks - .15, 'label': 'A SUA PARTE', 'dy': 100,
         'values': [{'text': 'R$ 0', 'color': 'red', 'at': -.3},
                    {'text': '100 SEGUIDORES', 'color': 'green', 'at': LAND, 'shake': True}]},
    ]
    effects = [
        sfx('impacto.wav', .05, -5),
        sfx('impacto-suave.wav', .77, -10),
        sfx('whoosh.wav', bag - WHOOSH_PEAK, -2),
        sfx('pop.wav', bag + .9, -10),
        sfx('whoosh.wav', count - WHOOSH_PEAK, -2),
        sfx('pop.wav', count + .1, -12),
        *ticks(count_from, count_to),
        sfx('impacto.wav', LAND - .02, -4),
        sfx('notificacao.wav', LAND + .02, -7),
        sfx('whoosh.wav', thanks - WHOOSH_PEAK, -3),
        sfx('pop.wav', thanks + .2, -8),
        sfx('pop.wav', thanks + .9, -12),
        sfx('pop.wav', thanks + 1.25, -12),
        sfx('whoosh.wav', nxt - WHOOSH_PEAK, -2),
        sfx('impacto-suave.wav', nxt + .2, -8),
        sfx('pop.wav', nxt + .5, -12),
    ]
    return {'timing_status': 'designed_without_voice', 'style': '../guia-de-estilo-referencia.md',
            'note': 'Thank-you for the first 100 followers; no voice, so no credits.',
            'audio': 'silencio.wav', 'tail': TAIL, 'scenes': scenes, 'graphics': graphics, 'sfx': effects, 'captions': []}


def main():
    portrait()
    silence()
    timeline = build()
    wide = too_wide(timeline['graphics'])
    if wide:
        raise ValueError(f'Lines wider than the safe area: {wide}')
    graficos.check(timeline['graphics'])
    (HERE / 'timeline.json').write_text(json.dumps(timeline, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f"timeline.json: {len(timeline['scenes'])} scenes, {len(timeline['graphics'])} graphics, "
          f"{len(timeline['sfx'])} effects, {END}s")


if __name__ == '__main__':
    main()
