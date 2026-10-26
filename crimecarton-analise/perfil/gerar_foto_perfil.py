#!/usr/bin/env python3
"""Make the series profile photos from the Codex profile illustrations.

The @crimecarton avatar shows a worried character holding a money bag in a dark,
lamp-lit room. These answer it: Zinho, worried, holding open the backpack that came
with old clothes instead of his share. Version A looks at the camera, version B into
the backpack. The photos are square because Instagram and TikTok crop them to a
circle; previa-circular.png shows that crop large and small for both versions.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
VERSIONS = {  # source illustration -> profile photo
    'ilustracao-perfil.png': 'foto-perfil.png',
    'ilustracao-perfil-b.png': 'foto-perfil-b.png',
}
CROP = (.90, .47)  # side of the centered square and its vertical center, as fractions of the illustration
SIZE = 1080
PREVIEW_SIZES = (360, 150, 77, 40)


def photo(source):
    im = Image.open(source).convert('RGB')
    side, center = CROP
    px = round(side*im.width)
    x0 = (im.width - px)//2
    y0 = min(max(0, round(center*im.height - px/2)), im.height - px)
    return im.crop((x0, y0, x0+px, y0+px)).resize((SIZE, SIZE), Image.Resampling.LANCZOS)


def circle(im, d):
    mask = Image.new('L', (d*4, d*4))
    ImageDraw.Draw(mask).ellipse((0, 0, d*4-1, d*4-1), fill=255)
    out = im.resize((d, d), Image.Resampling.LANCZOS).convert('RGBA')
    out.putalpha(mask.resize((d, d), Image.Resampling.LANCZOS))
    return out


def preview(photos, gap=48):
    """Each photo's circle crop at the preview sizes, on a dark row and a light row."""
    row = PREVIEW_SIZES[0] + 2*gap
    width = sum(PREVIEW_SIZES) + gap*(len(PREVIEW_SIZES)+1)
    sheet = Image.new('RGB', (width*len(photos), 2*row))
    for i, im in enumerate(photos):
        for y, background in ((0, (0, 0, 0)), (row, (255, 255, 255))):
            sheet.paste(background, (i*width, y, (i+1)*width, y+row))
            x = i*width + gap
            for d in PREVIEW_SIZES:
                avatar = circle(im, d)
                sheet.paste(avatar, (x, y + (row-d)//2), avatar)
                x += d + gap
    return sheet


def main():
    photos = []
    for source, target in VERSIONS.items():
        im = photo(HERE / source)
        im.save(HERE / target, optimize=True)
        photos.append(im)
        print(f'{HERE / target} {im.size[0]}x{im.size[1]}')
    preview(photos).save(HERE / 'previa-circular.png', optimize=True)


if __name__ == '__main__':
    main()
