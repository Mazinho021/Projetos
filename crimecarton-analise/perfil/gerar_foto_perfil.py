#!/usr/bin/env python3
"""Make the series profile photo from the scene where Zinho finds the old clothes.

The @crimecarton avatar shows a worried character holding a money bag in a dark,
lamp-lit room. This one answers it: Zinho, worried, holding the old clothes that came
in the backpack instead of his share. The photo is square because Instagram and TikTok
crop it to a circle; previa-circular.png shows that crop large and small.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance

HERE = Path(__file__).resolve().parent
SCENE = HERE.parent / 'episodio-01' / 'cena-03-roupas.png'
CROP = (.04, .13, .84)  # left and top of the square, then its side, as fractions of the scene
SIZE = 1080
PREVIEW_SIZES = (360, 150, 77, 40)


def photo():
    im = Image.open(SCENE).convert('RGB')
    left, top, side = CROP
    x0, y0, px = round(left*im.width), round(top*im.height), round(side*im.width)
    out = im.crop((x0, y0, x0+px, y0+px)).resize((SIZE, SIZE), Image.Resampling.LANCZOS)
    out = ImageEnhance.Contrast(out).enhance(1.06)
    # Darken toward the edge, like the lamp-lit room in the reference avatar.
    ramp = Image.radial_gradient('L').resize((SIZE, SIZE), Image.Resampling.BICUBIC)
    shade = ramp.point(lambda v: round(255*.82*max(0, (v/255-.42)/.58)**1.3))
    return Image.composite(Image.new('RGB', (SIZE, SIZE), (8, 6, 6)), out, shade)


def circle(im, d):
    mask = Image.new('L', (d*4, d*4))
    ImageDraw.Draw(mask).ellipse((0, 0, d*4-1, d*4-1), fill=255)
    out = im.resize((d, d), Image.Resampling.LANCZOS).convert('RGBA')
    out.putalpha(mask.resize((d, d), Image.Resampling.LANCZOS))
    return out


def preview(im, gap=48):
    """The circle crop at each preview size, on a dark row and a light row."""
    row = PREVIEW_SIZES[0] + 2*gap
    width = sum(PREVIEW_SIZES) + gap*(len(PREVIEW_SIZES)+1)
    sheet = Image.new('RGB', (width, 2*row))
    for y, background in ((0, (0, 0, 0)), (row, (255, 255, 255))):
        sheet.paste(background, (0, y, width, y+row))
        x = gap
        for d in PREVIEW_SIZES:
            avatar = circle(im, d)
            sheet.paste(avatar, (x, y + (row-d)//2), avatar)
            x += d + gap
    return sheet


def main():
    im = photo()
    im.save(HERE / 'foto-perfil.png', optimize=True)
    preview(im).save(HERE / 'previa-circular.png', optimize=True)
    print(f'{HERE / "foto-perfil.png"} {im.size[0]}x{im.size[1]}')


if __name__ == '__main__':
    main()
