#!/usr/bin/env python3
"""Cut Zinho out of his drawings, for the animation of the "mais de 100" video.

Uses isnet-anime, the cartoon-character model that rembg ships, run with onnxruntime:
https://github.com/danielgatis/rembg/releases/download/v0.0.0/isnet-anime.onnx
The model is not in the repository (176 MB); its path is the first argument.

    python recortar.py /caminho/isnet-anime.onnx

Writes, cropped to the drawing: recortes/zinho-corpo.png (the front pose with the backpack),
from the character sheet, and recortes/zinho-joia.png (Zinho happy, thumbs up), from
Codex's zinho-joia-b.png.
"""
from __future__ import annotations

from pathlib import Path
import sys

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
SHEET = HERE.parents[1] / 'zinho-referencia-v3.png'
# The drawing each cut-out comes from and the box on it (left, top, right, bottom), or None for all of it.
PARTS = {
    'zinho-corpo': (SHEET, (0, 8, 500, 1000)),
    'zinho-joia': (HERE / 'zinho-joia-b.png', None),
}


def mask_of(session, im):
    """The model's alpha for `im`, at the image's size (rembg's normalisation for this model)."""
    x = np.asarray(im.convert('RGB').resize((1024, 1024), Image.Resampling.LANCZOS), dtype=np.float32)
    x = x / x.max()
    x = (x - np.array([0.485, 0.456, 0.406], dtype=np.float32)).transpose(2, 0, 1)[None]
    pred = session.run(None, {session.get_inputs()[0].name: x})[0][0, 0]
    pred = (pred - pred.min()) / (pred.max() - pred.min())
    return Image.fromarray((pred*255).astype(np.uint8)).resize(im.size, Image.Resampling.LANCZOS)


def main():
    session = ort.InferenceSession(sys.argv[1], providers=['CPUExecutionProvider'])
    (HERE / 'recortes').mkdir(exist_ok=True)
    for name, (source, box) in PARTS.items():
        part = Image.open(source).convert('RGB')
        part = part.crop(box) if box else part
        # Pad with the sheet's paper colour, so a drawing touching the crop's edge is not cut flat.
        pad = 24
        canvas = Image.new('RGB', (part.width + 2*pad, part.height + 2*pad), part.getpixel((4, 4)))
        canvas.paste(part, (pad, pad))
        alpha = mask_of(session, canvas)
        # A firm edge: the model's soft fringe of paper is pushed out, the line art kept.
        alpha = alpha.point(lambda v: 0 if v < 40 else 255 if v > 215 else round((v - 40) * 255 / 175))
        alpha = alpha.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.7))
        cut = canvas.convert('RGBA')
        cut.putalpha(alpha)
        cut = cut.crop(cut.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())
        cut.save(HERE / 'recortes' / f'{name}.png', optimize=True)
        print(name, cut.size)


if __name__ == '__main__':
    main()
