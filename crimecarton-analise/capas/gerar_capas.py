#!/usr/bin/env python3
"""Make the episode covers in the layout of the @crimecarton covers.

Each cover is 1080 × 1920, the Reels and TikTok frame. The profile grids show only its
middle 3:4 (1080 × 1440), so everything that matters stays inside that area: the art
fills it, and low down, over a dark gradient, come a small outlined tag with the series
name, "PARTE N" in white, the title in yellow and a short line in white. The same
layout on every episode keeps the profile grid in order, as on his profile.
previa-grade.png shows the covers as the grid crops them.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
FONTS = HERE.parent / 'fontes'
W, H = 1080, 1920
GRID = (240, 1680)  # top and bottom of the 3:4 area the profile grids show
YELLOW, WHITE, SHADE = (253, 184, 34), (246, 240, 226), (9, 9, 11)
SERIES = 'A PARTE QUE FALTOU'

# One entry per episode. "art" is the illustration; "focus" (fractions of the art) lands
# at "at" (pixels of the cover), with the art "scale" times the cover width.
COVERS = [
    dict(part=1, title='A MOCHILA', line='CADÊ O DINHEIRO?', art='../perfil/ilustracao-perfil-b.png',
         scale=1.10, focus=(.5, .40), at=(540, 640)),
    dict(part=2, title='A DÍVIDA', line='QUANTO ELE DEVIA?', art='../episodio-02/cena-08-retrato-amigo.png',
         scale=1.10, focus=(.5, .30), at=(540, 660)),
]


def font(weight, size):
    return ImageFont.truetype(str(FONTS / f'Poppins-{weight}.ttf'), size)


def fitted(weight, text, size, width):
    # The largest size up to `size` at which the text fits in `width`.
    while font(weight, size).getlength(text) > width:
        size -= 2
    return font(weight, size)


def art_layer(c):
    art = Image.open(HERE / c['art']).convert('RGB')
    # Backdrop for whatever the art does not reach: the same art, blurred and darkened.
    cover = max(W / art.width, H / art.height)
    back = art.resize((round(art.width*cover), round(art.height*cover)), Image.Resampling.LANCZOS)
    back = back.crop(((back.width - W)//2, (back.height - H)//2, (back.width + W)//2, (back.height + H)//2))
    canvas = ImageEnhance.Brightness(back.filter(ImageFilter.GaussianBlur(28))).enhance(.45)
    side = round(W * c['scale'])
    fg = art.resize((side, round(art.height * side / art.width)), Image.Resampling.LANCZOS)
    x, y = round(c['at'][0] - c['focus'][0]*fg.width), round(c['at'][1] - c['focus'][1]*fg.height)
    # Feather the edges that end inside the cover so the art melts into the backdrop.
    mask = Image.new('L', fg.size, 255)
    draw = ImageDraw.Draw(mask)
    feather = 90
    for i in range(feather):
        a = round(255 * i / feather)
        if y > 0:
            draw.line((0, i, fg.width, i), fill=a)
        if y + fg.height < H:
            draw.line((0, fg.height - 1 - i, fg.width, fg.height - 1 - i), fill=a)
    canvas.paste(fg, (x, y), mask)
    return canvas


def gradient(canvas, start=1000, full=1450, strength=.9):
    # Dark from the middle of the grid area down, as on the reference covers.
    ramp = Image.new('L', (1, H))
    for y in range(H):
        t = min(1, max(0, (y - start) / (full - start)))
        ramp.putpixel((0, y), round(255 * strength * t**1.4))
    return Image.composite(Image.new('RGB', (W, H), SHADE), canvas, ramp.resize((W, H)))


def text_block(canvas, c):
    layer = Image.new('RGBA', (W, H))
    draw = ImageDraw.Draw(layer)
    top = GRID[0]

    def centered(text, f, cy, fill):
        box = f.getbbox(text)
        draw.text((W/2 - f.getlength(text)/2, cy - (box[1] + box[3])/2), text, font=f, fill=fill)

    # Tag: the series name, spaced capitals inside a thin yellow outline.
    tag = font('SemiBold', 30)
    spacing = 5
    width = sum(tag.getlength(ch) for ch in SERIES) + spacing*(len(SERIES) - 1)
    cy = top + 857
    pill = (W/2 - width/2 - 28, cy - 30, W/2 + width/2 + 28, cy + 30)
    draw.rounded_rectangle(pill, radius=30, fill=(0, 0, 0, 90), outline=YELLOW + (230,), width=3)
    x = W/2 - width/2
    box = tag.getbbox(SERIES)
    for ch in SERIES:
        draw.text((x, cy - (box[1] + box[3])/2), ch, font=tag, fill=YELLOW + (240,))
        x += tag.getlength(ch) + spacing
    centered(f'PARTE {c["part"]}', font('Bold', 100), top + 982, WHITE)
    centered(c['title'], fitted('ExtraBold', c['title'], 200, 970), top + 1181, YELLOW)
    centered(c['line'], fitted('Bold', c['line'], 96, 920), top + 1346, WHITE)
    # Soft shadow under the text for legibility on any art.
    alpha = layer.split()[3]
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shadow.putalpha(alpha.point(lambda v: round(v*.55)).filter(ImageFilter.GaussianBlur(8)))
    out = canvas.convert('RGBA')
    out.alpha_composite(shadow, (0, 5))
    out.alpha_composite(layer)
    return out.convert('RGB')


def cover(c):
    return text_block(gradient(art_layer(c)), c)


def grid_preview(covers, tile=360, gap=4):
    # The covers as the profile grid shows them: the middle 3:4, three per row.
    th = round(tile * 4/3)
    rows = (len(covers) + 2)//3
    sheet = Image.new('RGB', (3*tile + 2*gap, rows*th + (rows - 1)*gap), (11, 13, 16))
    for i, im in enumerate(covers):
        crop = im.crop((0, GRID[0], W, GRID[1])).resize((tile, th), Image.Resampling.LANCZOS)
        sheet.paste(crop, ((i % 3)*(tile + gap), (i//3)*(th + gap)))
    return sheet


def main():
    images = []
    for c in COVERS:
        im = cover(c)
        path = HERE / f'capa-parte-{c["part"]:02d}.png'
        im.save(path, optimize=True)
        images.append(im)
        print(path)
    grid_preview(images).save(HERE / 'previa-grade.png', optimize=True)


if __name__ == '__main__':
    main()
