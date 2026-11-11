"""Stills of a part's timeline at given times, without rendering: the backdrop (with its zoom at
that moment), the caption gradient and the graphics layer, with the HUD and TikTok guides, in one
sheet. --v marks the vertical layout's guides; --guias draws them.

    python previa_quadros.py TIMELINE OUT.jpg t1 t2 ... [--v] [--guias]
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

TOOLS = Path(__file__).resolve().parents[4] / 'crimecarton-analise' / 'episodio-01' / 'montagem'
sys.path.insert(0, str(TOOLS))
import graficos  # noqa: E402
import render_animatic as ra  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith('--')]
flags = {a for a in sys.argv[1:] if a.startswith('--')}
timeline_path, out = Path(args[0]), Path(args[1])
times = [float(t) for t in args[2:]]
timeline = json.loads(timeline_path.read_text())
ra.ROOT = timeline_path.resolve().parent.parent
vertical = '--v' in flags
W, H = graficos.W, graficos.H
cache = {}


def backdrop(scene):
    key = json.dumps(scene, sort_keys=True)
    if key not in cache:
        if scene.get('kind') == 'black':
            bg = Image.new('RGBA', (W, H), (11, 10, 9, 255))
        else:
            bg = ra.backdrop(ra.resolve_asset(scene['asset']), float(scene.get('brightness', 1)), False,
                             scene.get('crop'), scene.get('paint'), scene.get('screen'))
            bg = ra.caption_gradient(bg)
        cache[key] = bg
    return cache[key]


def frame(t):
    scene = next(s for s in timeline['scenes'] if s['start'] <= t < s['end'])
    bg = backdrop(scene)
    zoom = float(scene.get('zoom', .028))
    p = (t - scene['start'])/max(.01, scene['end'] - scene['start'])
    z = 1 + zoom*p if scene.get('direction', 'in') == 'in' else 1 + zoom - zoom*p
    cw, ch = W/z, H/z
    im = bg.crop((round((W - cw)/2), round((H - ch)/2), round((W + cw)/2), round((H + ch)/2))).resize((W, H))
    im = Image.alpha_composite(im, graficos.still(timeline['graphics'], t)).convert('RGB')
    if '--guias' in flags:
        d = ImageDraw.Draw(im, 'RGBA')
        dy = 67 if vertical else 0
        d.rectangle((42, 87 + dy, 678, 193 + dy), outline=(0, 255, 255, 140), width=2)
        if vertical:
            d.rectangle((590, 576, 719, 1024), outline=(255, 80, 80, 200), width=3)
            d.rectangle((0, 0, 719, 146), outline=(255, 160, 0, 150), width=2)
        d.line((0, 1024, 720, 1024), fill=(255, 0, 255, 110), width=2)
    ImageDraw.Draw(im).text((8, 1258), f'{t:.2f}s {Path(scene.get("asset", "black")).name[:44]}', fill=(255, 255, 0))
    return im


thumbs = [frame(t).resize((360, 640), Image.LANCZOS) for t in times]
cols = min(len(thumbs), 5)
rows = (len(thumbs) + cols - 1)//cols
sheet = Image.new('RGB', (360*cols, 640*rows), 'black')
for i, th in enumerate(thumbs):
    sheet.paste(th, ((i % cols)*360, (i//cols)*640))
sheet.save(out, quality=88)
print(out)
