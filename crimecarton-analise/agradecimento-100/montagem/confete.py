"""A confetti burst for the graphics layer, used by the 100-followers thank-you.

Importing this module registers the "confetti" element in graficos, so a timeline can use
it like any other: {"type": "confetti", "start": 7.55, "end": 10.9, "x": 360, "y": 640}.
The pieces are thrown upward in a fan from (x, y) and then drift down against air drag,
each one spinning and flipping like a bit of paper. Everything is seeded, so every frame of
a render sees the same pieces.

Optional fields: count (110), colors (palette names or RGB), gravity (1000 px/s²) and seed.
"""
from __future__ import annotations

import math
import random

from PIL import Image, ImageDraw

import graficos
from graficos import H, W, fading, rgb


def draw_confetti(canvas, el, t):
    age = t - el['start']
    if age < 0:
        return
    rnd = random.Random(el.get('seed', 100))
    x0, y0, g = el.get('x', W/2), el.get('y', 640), el.get('gravity', 1000)
    palette = [rgb(c) for c in el.get('colors', ['yellow', 'yellow', 'white', 'green', 'softred'])]
    alpha = round(255 * min(1, age/.06) * fading(t, el['end'], .6))
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(el.get('count', 110)):
        # Every random value is drawn in the same order on every call, whether or not the piece is on screen.
        angle = rnd.uniform(-math.radians(168), -math.radians(12))
        speed, drag = rnd.uniform(500, 1700), rnd.uniform(2.6, 4.2)
        size, aspect = rnd.uniform(12, 22), rnd.uniform(.45, .8)
        spin, turn, flip = rnd.uniform(-9, 9), rnd.uniform(0, math.tau), rnd.uniform(5, 11)
        sway, sway_rate = rnd.uniform(6, 26), rnd.uniform(3, 7)
        glide = (1 - math.exp(-drag*age))/drag
        x = x0 + speed*math.cos(angle)*glide + sway*math.sin(sway_rate*age + turn)*min(1, age)
        y = y0 + g/drag*age + (speed*math.sin(angle) - g/drag)*glide
        if not (-40 < x < W + 40 and -40 < y < H + 40):
            continue
        color = palette[i % len(palette)] + (alpha,)
        half_w, half_h = size/2, size*aspect/2*max(.15, abs(math.cos(flip*age + turn)))
        if i % 6 == 0:
            d.ellipse((x - half_w*.7, y - half_h*1.4, x + half_w*.7, y + half_h*1.4), fill=color)
            continue
        c, s = math.cos(spin*age + turn), math.sin(spin*age + turn)
        d.polygon([(x + px*c - py*s, y + px*s + py*c)
                   for px, py in ((-half_w, -half_h), (half_w, -half_h), (half_w, half_h), (-half_w, half_h))], fill=color)
    canvas.alpha_composite(layer)


graficos.DRAW['confetti'] = draw_confetti
