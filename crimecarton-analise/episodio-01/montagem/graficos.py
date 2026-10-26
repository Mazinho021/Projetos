"""Motion-graphics layer drawn frame by frame over the scenes.

Follows the series' reference video: phrases that pop in line by line, a HUD with
Zinho's share and suspicion level, tags, stacked labels, stamps and the closing call
to action. Every element is timed in absolute seconds of the narration.
"""
from __future__ import annotations

from functools import lru_cache
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = Path(__file__).resolve().parents[2] / 'fontes'
W, H = 720, 1280
# Palette sampled from the reference video.
COLORS = {'white': (246, 240, 226), 'yellow': (253, 184, 34), 'green': (52, 192, 119),
          'red': (235, 88, 76), 'gray': (177, 179, 174), 'ink': (24, 22, 18), 'alert': (182, 52, 36),
          'softred': (233, 137, 136)}
PANEL = (16, 15, 12, 216)


@lru_cache(maxsize=None)
def font(size, weight='Bold'):
    return ImageFont.truetype(str(FONTS / f'Poppins-{weight}.ttf'), size)


def rgb(name):
    return COLORS[name] if isinstance(name, str) else tuple(name)


def ease_out_back(x, s=1.70158):
    x -= 1
    return 1 + (s+1)*x**3 + s*x**2


def popped(age, dur=.22, origin=.62):
    """Scale and opacity of something that appeared `age` seconds ago."""
    if age < 0:
        return 0, 0
    x = min(1, age/dur)
    return origin + (1-origin)*ease_out_back(x), min(1, age/.07)


def fading(t, end, dur=.14):
    return max(0, min(1, (end-t)/dur))


def shake(age, dur=.4, amp=9):
    if age < 0 or age > dur:
        return 0
    return amp * (1-age/dur) * math.sin(age*55)


def put(canvas, sprite, x, y):
    """alpha_composite that accepts positions partly outside the canvas."""
    x, y = round(x), round(y)
    sx, sy = max(0, -x), max(0, -y)
    if sx >= sprite.width or sy >= sprite.height or x >= canvas.width or y >= canvas.height:
        return
    canvas.alpha_composite(sprite, (max(0, x), max(0, y)), (sx, sy))


def place(canvas, sprite, x, y, ax, ay, scale=1, alpha=1):
    """Draw `sprite` with its point (ax, ay) on (x, y), scaled about that point."""
    if alpha <= .01 or scale <= .01:
        return
    if scale != 1:
        sprite = sprite.resize((max(1, round(sprite.width*scale)), max(1, round(sprite.height*scale))),
                               Image.Resampling.BICUBIC)
        ax, ay = ax*scale, ay*scale
    if alpha < 1:
        sprite = sprite.copy()
        sprite.putalpha(sprite.getchannel('A').point(lambda v: round(v*alpha)))
    put(canvas, sprite, x-ax, y-ay)


@lru_cache(maxsize=512)
def text_sprite(value, size, weight='Bold', fill='white', tracking=0, shadow=True):
    """Text on a transparent sprite, with the y of its cap-height centre."""
    f = font(size, weight)
    ascent, descent = f.getmetrics()
    width = sum(f.getlength(c) for c in value) + tracking*(len(value)-1) if tracking else f.getlength(value)
    pad = round(size*.35) if shadow else 4
    sprite = Image.new('RGBA', (math.ceil(width) + 2*pad, ascent + descent + 2*pad), (0, 0, 0, 0))
    mask = Image.new('L', sprite.size, 0)
    d = ImageDraw.Draw(mask)
    if tracking:
        x = pad
        for c in value:
            d.text((x, pad+ascent), c, font=f, fill=255, anchor='ls')
            x += f.getlength(c) + tracking
    else:
        d.text((pad, pad+ascent), value, font=f, fill=255, anchor='ls')
    if shadow:
        # A soft dark shadow keeps light text readable over busy artwork.
        shade = Image.new('RGBA', sprite.size, (0, 0, 0, 0))
        shade.putalpha(mask.filter(ImageFilter.GaussianBlur(size*.09)).point(lambda v: v*.55))
        sprite.alpha_composite(shade, (0, round(size*.04)))
    solid = Image.new('RGBA', sprite.size, rgb(fill) + (255,))
    solid.putalpha(mask)
    sprite.alpha_composite(solid)
    return sprite, pad + ascent + f.getbbox('H', anchor='ls')[1]/2


def panel(size, radius, fill=PANEL, outline=None, width=0):
    sprite = Image.new('RGBA', size, (0, 0, 0, 0))
    ImageDraw.Draw(sprite).rounded_rectangle((0, 0, size[0]-1, size[1]-1), radius, fill=fill, outline=outline, width=width)
    return sprite


@lru_cache(maxsize=None)
def star_sprite(filled, r=16):
    # Drawn at 4x and reduced, since PIL polygons are not antialiased.
    k, side = 4, 2*r + 4
    big = Image.new('RGBA', (side*k, side*k), (0, 0, 0, 0))
    c = side*k/2
    pts = [(c + (r if i % 2 == 0 else r*.42)*k*math.cos(-math.pi/2 + i*math.pi/5),
            c + (r if i % 2 == 0 else r*.42)*k*math.sin(-math.pi/2 + i*math.pi/5)) for i in range(10)]
    d = ImageDraw.Draw(big)
    if filled:
        d.polygon(pts, fill=rgb('yellow') + (255,))
    else:
        d.polygon(pts, outline=rgb('gray') + (200,), width=2*k)
    return big.resize((side, side), Image.Resampling.LANCZOS)


def arrow(draw, x0, x1, y, fill, k=1):
    draw.line((x0, y, x1 - 9*k, y), fill=fill, width=4*k)
    draw.polygon([(x1, y), (x1 - 14*k, y - 9*k), (x1 - 14*k, y + 9*k)], fill=fill)


def counted(line, t):
    c = line['count']
    x = max(0, min(1, (t - c['start'])/(c['end'] - c['start'])))
    value = round(c['from'] + (c['to'] - c['from'])*(1 - (1-x)**3))
    return c.get('format', 'R$ {}').format(f'{value:,}'.replace(',', '.'))


def draw_phrase(canvas, el, t):
    lines = el['lines']
    base = el.get('size', 78)
    sizes = [ln.get('size', 22 if ln.get('style') == 'label' else base) for ln in lines]
    heights = [s*(1.6 if ln.get('style') == 'label' else 1.12) for s, ln in zip(sizes, lines)]
    top = el.get('y', 600) - sum(heights)/2
    out = fading(t, el['end'], el.get('fade', .14))
    for ln, size, h in zip(lines, sizes, heights):
        cy, top = top + h/2, top + h
        at = ln.get('at', el['start'])
        scale, alpha = popped(t - at, origin=el.get('origin', .62))
        if alpha <= 0:
            continue
        value = counted(ln, t) if 'count' in ln else ln['text']
        if ln.get('style') == 'label':
            sprite, ay = text_sprite(value, size, 'SemiBold', ln.get('color', 'white'), round(size*.22))
        else:
            sprite, ay = text_sprite(value, size, ln.get('weight', 'Bold'), ln.get('color', 'white'))
        dx = shake(t - at) if ln.get('shake') else 0
        place(canvas, sprite, el.get('x', W/2) + dx, cy, sprite.width/2, ay, scale, alpha*out)


@lru_cache(maxsize=8)
def hud_base(label):
    base = Image.new('RGBA', (W, 200), (0, 0, 0, 0))
    put(base, panel((636, 106), 16), 42, 87)
    d = ImageDraw.Draw(base)
    d.line((413, 103, 413, 177), fill=(120, 120, 112, 170), width=2)
    sprite, ay = text_sprite(label, 17, 'Medium', 'gray', shadow=False)
    place(base, sprite, 62, 112, 0, ay)
    return base


def stars_filled_at(el):
    times, count = [None]*5, 0
    for key in el.get('stars', []):
        for j in range(count, key['count']):
            times[j] = key['at'] + (j - count)*key.get('step', .12)
        count = max(count, key['count'])
    return times


def draw_hud(canvas, el, t):
    age = t - el['start']
    layer = hud_base(el.get('label', 'A SUA PARTE')).copy()
    shown = [v for v in el.get('values', []) if v['at'] <= t]
    if shown:
        v = shown[-1]
        scale, _ = popped(t - v['at'], dur=.28, origin=1.3) if v is not el['values'][0] else (1, 1)
        dx = shake(t - v['at'], .45, 8) if v.get('shake') else 0
        sprite, ay = text_sprite(v['text'], 40, 'Bold', v.get('color', 'green'), shadow=False)
        place(layer, sprite, 62 + dx, 152, 0, ay, scale)
    filled = [ft is not None and ft <= t for ft in stars_filled_at(el)]
    sprite, ay = text_sprite('SUSPEITA', 17, 'Medium', 'softred' if sum(filled) >= 4 else 'gray', shadow=False)
    place(layer, sprite, 435, 112, 0, ay)
    for i, (on, ft) in enumerate(zip(filled, stars_filled_at(el))):
        star = star_sprite(on)
        scale = popped(t - ft, dur=.25, origin=1.7)[0] if on else 1
        place(layer, star, 454 + i*44, 154, star.width/2, star.height/2, scale)
    alpha = min(1, age/.3) * fading(t, el['end'], .25)
    # "dy" moves the whole panel down, below the search bar TikTok draws at the top.
    place(canvas, layer, 0, el.get('dy', 0) - 18*(1 - min(1, age/.3))**2, 0, 0, 1, alpha)


@lru_cache(maxsize=32)
def tag_sprite(value, kind):
    fill, ink = (rgb('yellow'), 'ink') if kind == 'yellow' else (rgb('alert'), 'white')
    sprite, ay = text_sprite(value, 21, 'Bold', ink, 1.5, shadow=False)
    w, h = sprite.width + 30, 42
    tag = panel((w, h), 9, fill + (255,))
    place(tag, sprite, w/2, h/2, sprite.width/2, ay)
    return tag


def draw_tag(canvas, el, t):
    scale, alpha = popped(t - el['start'], origin=.7)
    tag = tag_sprite(el['text'], el.get('color', 'yellow'))
    place(canvas, tag, el.get('x', W/2), el.get('y', 230), tag.width/2, tag.height/2, scale,
          alpha*fading(t, el['end'], .2))


@lru_cache(maxsize=32)
def list_sprite(left, right, column):
    # Arrows and right-hand values line up in one column, `column` px wide.
    w, h, k = 500, 68, 4
    item = panel((w, h), 12)
    sprite, ay = text_sprite(left, 28, 'Bold', 'white', shadow=False)
    place(item, sprite, 20, h/2, 0, ay)
    sprite, ay = text_sprite(right, 28, 'Bold', 'red', shadow=False)
    place(item, sprite, w - 20 - column, h/2, 0, ay)
    head = Image.new('RGBA', (60*k, 30*k), (0, 0, 0, 0))
    arrow(ImageDraw.Draw(head), 4*k, 56*k, 15*k, rgb('red') + (255,), k)
    put(item, head.resize((60, 30), Image.Resampling.LANCZOS), w - 20 - column - 62, h/2 - 15)
    return item


def draw_list(canvas, el, t):
    out, y = fading(t, el['end'], .18), el.get('y', 600)
    column = max(text_sprite(item['right'], 28, 'Bold', 'red', shadow=False)[0].width for item in el['items'])
    for item in el['items']:
        scale, alpha = popped(t - item['at'], origin=.85)
        sprite = list_sprite(item['left'], item['right'], column)
        place(canvas, sprite, W/2, y + sprite.height/2, sprite.width/2, sprite.height/2, scale, alpha*out)
        y += sprite.height + 14


@lru_cache(maxsize=16)
def stamp_sprite(value, angle, kind):
    sprite, ay = text_sprite(value, 54, 'ExtraBold', kind, shadow=False)
    w, h = sprite.width + 30, 86
    stamp = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    # A light, paper-like backing keeps the red legible over photos and artwork.
    ImageDraw.Draw(stamp).rounded_rectangle((3, 3, w-4, h-4), 10, fill=rgb('white') + (232,), outline=rgb(kind) + (255,), width=6)
    place(stamp, sprite, w/2, h/2, sprite.width/2, ay)
    return stamp.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)


def draw_stamp(canvas, el, t):
    # Slams down from a larger size, like an ink stamp.
    age = t - el['start']
    x = min(1, max(0, age)/.16)
    sprite = stamp_sprite(el['text'], el.get('angle', -7), el.get('color', 'red'))
    place(canvas, sprite, el.get('x', W/2), el.get('y', 640), sprite.width/2, sprite.height/2,
          1.9 - .9*x*x, min(1, max(0, age)/.06) * .94 * fading(t, el['end'], .2))


@lru_cache(maxsize=16)
def button_sprite(value, style):
    sprite, ay = text_sprite(value, 38, 'Bold', 'ink', shadow=False)
    w, h = sprite.width + 62, 100
    button = panel((w, h), 24, rgb('yellow' if style == 'yellow' else 'white') + (255,))
    place(button, sprite, w/2, h/2, sprite.width/2, ay)
    return button


def draw_buttons(canvas, el, t):
    out, y = fading(t, el['end'], .2), el.get('y', 700)
    if el.get('prompt'):
        scale, alpha = popped(t - el.get('prompt_at', el['start']), origin=.8)
        sprite, ay = text_sprite(el['prompt'], 28, 'SemiBold', 'yellow', 4)
        place(canvas, sprite, W/2, y - 96, sprite.width/2, ay, scale, alpha*out)
    sprites = [button_sprite(b['text'], b.get('style', 'yellow')) for b in el['items']]
    x = (W - sum(s.width for s in sprites) - 34*(len(sprites)-1)) / 2
    for b, sprite in zip(el['items'], sprites):
        scale, alpha = popped(t - b['at'], origin=.7)
        place(canvas, sprite, x + sprite.width/2, y, sprite.width/2, sprite.height/2, scale, alpha*out)
        x += sprite.width + 34


@lru_cache(maxsize=8)
def box_sprite(title, sub):
    w, h = 440, 120
    box = panel((w, h), 14, (16, 15, 12, 200), rgb('yellow') + (255,), 3)
    sprite, ay = text_sprite(title, 36, 'Bold', 'yellow', shadow=False)
    place(box, sprite, w/2, 46, sprite.width/2, ay)
    if sub:
        sprite, ay = text_sprite(sub, 19, 'Regular', 'white', shadow=False)
        place(box, sprite, w/2, 88, sprite.width/2, ay)
    return box


def draw_box(canvas, el, t):
    scale, alpha = popped(t - el['start'], origin=.8)
    box = box_sprite(el['title'], el.get('sub', ''))
    place(canvas, box, W/2, el.get('y', 860), box.width/2, box.height/2, scale, alpha*fading(t, el['end'], .2))


@lru_cache(maxsize=4)
def vignette_sprite(color, strength):
    # Clear centre, edges tinted towards `color`: the reference's red alarm around a character.
    ramp = Image.radial_gradient('L').resize((W, H), Image.Resampling.BICUBIC)
    sprite = Image.new('RGBA', (W, H), color + (0,))
    sprite.putalpha(ramp.point(lambda v: round(255*strength*max(0, (v/255 - .3)/.7)**1.4)))
    return sprite


def draw_vignette(canvas, el, t):
    alpha = min(1, max(0, t - el['start'])/.12) * fading(t, el['end'], .3)
    place(canvas, vignette_sprite(rgb(el.get('color', 'alert')), el.get('strength', .85)), 0, 0, 0, 0, 1, alpha)


DRAW = {'phrase': draw_phrase, 'hud': draw_hud, 'tag': draw_tag, 'list': draw_list, 'stamp': draw_stamp,
        'buttons': draw_buttons, 'box': draw_box, 'vignette': draw_vignette}


def check(elements):
    for el in elements:
        if el.get('type') not in DRAW:
            raise ValueError(f'Unknown graphics element: {el}')
        if float(el['end']) <= float(el['start']):
            raise ValueError(f'Graphics element ends before it starts: {el}')


def still(elements, t):
    canvas = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for el in elements:
        if el['start'] <= t < el['end']:
            DRAW[el['type']](canvas, el, t)
    return canvas


def frames(elements, duration, fps):
    """Raw RGBA frames of the whole layer, for FFmpeg's rawvideo input."""
    check(elements)
    blank = bytes(W*H*4)
    for i in range(round(duration*fps)):
        t = i/fps
        yield still(elements, t).tobytes() if any(el['start'] <= t < el['end'] for el in elements) else blank
