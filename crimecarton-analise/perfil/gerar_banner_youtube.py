#!/usr/bin/env python3
"""Make the YouTube channel banner from the episode 1 illustrations.

YouTube asks for 2560 × 1440, shows the whole image only on TVs, a 2560 × 423 band on
computers and just the middle 1546 × 423 on phones. So the band in the middle carries
everything: Zinho on the phone on the left, the friend at the window on the right and
the channel name between them, in the type and colours of the covers. The rest is the
room at night, blurred, for the TVs. previa-banner-youtube.png shows the three crops.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent / 'episodio-01'
FONTS = HERE.parent / 'fontes'
W, H = 2560, 1440
SAFE = (507, 508, 2053, 931)  # the part phones show
YELLOW, WHITE, SHADE = (253, 184, 34), (246, 240, 226), (9, 9, 11)


def font(weight, size):
    return ImageFont.truetype(str(FONTS / f'Poppins-{weight}.ttf'), size)


def background():
    # The top of the scene 1 room, window and lamp, stretched across and blurred.
    im = Image.open(EPISODE / 'cena-01-base.png').convert('RGB')
    band = im.crop((0, 0, im.width, round(im.height*.36)))
    band = band.resize((W, round(band.height*W/band.width)), Image.Resampling.LANCZOS)
    top = (band.height - H)//2
    band = band.crop((0, top, W, top + H)).filter(ImageFilter.GaussianBlur(22))
    return ImageEnhance.Brightness(band).enhance(.42)


def figure(asset, face, head, at, height, fade_side, keep=(0, 1)):
    """The illustration scaled so the head (`head`, a fraction of its height) is
    `height` px tall, with the face (`face`, fractions) on `at`, edges faded. `keep`
    is the horizontal stretch of the illustration used, as fractions of its width."""
    im = Image.open(EPISODE / asset).convert('RGB')
    left = round(keep[0]*im.width)
    face = ((face[0]*im.width - left) / (round(keep[1]*im.width) - left), face[1])
    im = im.crop((left, 0, round(keep[1]*im.width), im.height))
    scale = height / (head*im.height)
    im = im.resize((round(im.width*scale), round(im.height*scale)), Image.Resampling.LANCZOS)
    x, y = round(at[0] - face[0]*im.width), round(at[1] - face[1]*im.height)
    # The side that faces the title fades over a long stretch, the others over a short one,
    # so the art melts into the room on every screen.
    mask = Image.new('L', im.size, 255)
    alpha = mask.load()
    inner, outer = round(im.width*.42), round(im.width*.22)
    for px in range(im.width):
        from_inner = px if fade_side == 'left' else im.width - 1 - px
        from_outer = im.width - 1 - px if fade_side == 'left' else px
        kx = min(1, from_inner/inner)**1.5 * min(1, from_outer/outer)
        for py in range(im.height):
            ky = min(1, py/(im.height*.12), (im.height - 1 - py)/(im.height*.25))
            alpha[px, py] = round(255*kx*ky)
    return im, mask, (x, y)


def spaced(draw, xy, text, f, fill, spacing):
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += f.getlength(ch) + spacing


def spaced_width(text, f, spacing):
    return sum(f.getlength(ch) for ch in text) + spacing*(len(text) - 1)


def title(canvas):
    layer = Image.new('RGBA', (W, H))
    d = ImageDraw.Draw(layer)
    cx, cy = (SAFE[0] + SAFE[2])/2, (SAFE[1] + SAFE[3])/2
    # Tag with the series name, as on the covers.
    tag, gap = font('SemiBold', 28), 5
    width = spaced_width('A PARTE QUE FALTOU', tag, gap)
    box = tag.getbbox('A')
    ty = cy - 96
    d.rounded_rectangle((cx - width/2 - 28, ty - 29, cx + width/2 + 28, ty + 29), radius=29, fill=(0, 0, 0, 110),
                        outline=YELLOW + (235,), width=4)
    spaced(d, (cx - width/2, ty - (box[1] + box[3])/2), 'A PARTE QUE FALTOU', tag, YELLOW + (245,), gap)
    # Channel name: white and yellow, like "PARTE 1" over the title on the covers.
    big = font('ExtraBold', 96)
    left, right = 'GOLPE ', 'CARTOON'
    total = big.getlength(left + right)
    box = big.getbbox('G')
    y = cy + 8 - (box[1] + box[3])/2
    d.text((cx - total/2, y), left, font=big, fill=WHITE)
    d.text((cx - total/2 + big.getlength(left), y), right, font=big, fill=YELLOW)
    sub, gap = font('SemiBold', 30), 4
    line = 'HISTÓRIAS ANIMADAS DE SUSPENSE'
    width = spaced_width(line, sub, gap)
    box = sub.getbbox('H')
    spaced(d, (cx - width/2, cy + 100 - (box[1] + box[3])/2), line, sub, WHITE + (240,), gap)
    shadow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    shadow.putalpha(layer.split()[3].point(lambda v: round(v*.6)).filter(ImageFilter.GaussianBlur(10)))
    out = canvas.convert('RGBA')
    out.alpha_composite(shadow, (0, 6))
    out.alpha_composite(layer)
    return out.convert('RGB')


def banner():
    canvas = background()
    cy = (SAFE[1] + SAFE[3])/2
    # Zinho on the phone, scene 7, and the friend behind the glass, scene 9, each with
    # the face inside the band phones show and clear of the title.
    # Scene 9 also shows Zinho at the curtain, so only its window is used.
    for asset, face, head, x, height, side, keep in (
            ('cena-07-audio.png', (.55, .29), .33, 700, 330, 'right', (0, 1)),
            ('cena-09-porta.png', (.86, .305), .11, 1885, 290, 'left', (.62, 1))):
        im, mask, xy = figure(asset, face, head, (x, cy + 10), height, side, keep)
        canvas.paste(im, xy, mask)
    # Darker centre behind the title.
    ramp = Image.new('L', (W, 1))
    for x in range(W):
        ramp.putpixel((x, 0), round(150*max(0, 1 - abs(x - W/2)/520)**1.2))
    canvas = Image.composite(Image.new('RGB', (W, H), SHADE), canvas, ramp.resize((W, H)))
    return title(canvas)


def preview(im):
    # Phone, computer and TV, one under the other.
    phone = im.crop(SAFE)
    desktop = im.crop((0, SAFE[1], W, SAFE[3])).resize((1546, round(423*1546/W)))
    tv = im.resize((1546, round(H*1546/W)))
    sheet = Image.new('RGB', (1546 + 40, phone.height + desktop.height + tv.height + 80), (24, 24, 24))
    y = 20
    for part in (phone, desktop, tv):
        sheet.paste(part, (20, y))
        y += part.height + 20
    return sheet


def main():
    im = banner()
    im.save(HERE / 'banner-youtube.jpg', quality=92)
    preview(im).save(HERE / 'previa-banner-youtube.jpg', quality=88)
    print(HERE / 'banner-youtube.jpg', (HERE / 'banner-youtube.jpg').stat().st_size // 1024, 'KB')


if __name__ == '__main__':
    main()
