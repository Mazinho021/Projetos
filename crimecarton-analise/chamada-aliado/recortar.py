#!/usr/bin/env python3
"""Cut Zinho pointing at you out of Codex's two drawings, for the "Vire aliado" video.

Uses the thank-you's cut-out (../agradecimento-100/mais-de-100/recortar.py): isnet-anime, run with
onnxruntime. The model is not in the repository (176 MB); its path is the first argument.

    python recortar.py /caminho/isnet-anime.onnx

Writes recortes/zinho-apontando.png, from zinho-apontando-b.png (the raised eyebrow, for "Vire
aliado"), and recortes/zinho-chamando.png, from zinho-apontando-a.png (the open smile, for the close).
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import sys

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('recortar_agradecimento', HERE.parent / 'agradecimento-100' / 'mais-de-100' / 'recortar.py')
base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(base)

PARTS = {'zinho-apontando': HERE / 'zinho-apontando-b.png', 'zinho-chamando': HERE / 'zinho-apontando-a.png'}


def paper_out_of_the_hair(cut, paper):
    """Clear the bits of paper the model keeps between the curls, which would show as light specks.

    They are small, paper-coloured and at the hair's outer edge; the eyes' whites, the teeth and the
    jacket's stripes, which are paper-coloured too, are larger or further in."""
    arr = np.asarray(cut).copy()
    alpha = arr[..., 3]
    near = (np.abs(arr[..., :3].astype(int) - paper).sum(axis=2) < 60) & (alpha > 0)
    wide = np.asarray(Image.fromarray(near.astype(np.uint8)*255).filter(ImageFilter.MinFilter(15)).filter(ImageFilter.MaxFilter(15))) > 0
    edge = np.asarray(Image.fromarray((alpha > 128).astype(np.uint8)*255).filter(ImageFilter.MinFilter(25))) == 0
    hair = np.arange(arr.shape[0])[:, None] < arr.shape[0]*.3
    arr[near & ~wide & edge & hair, 3] = 0
    return Image.fromarray(arr)


def main():
    session = ort.InferenceSession(sys.argv[1], providers=['CPUExecutionProvider'])
    (HERE / 'recortes').mkdir(exist_ok=True)
    for name, source in PARTS.items():
        drawing = Image.open(source).convert('RGB')
        cut = paper_out_of_the_hair(base.cut_out(session, drawing), drawing.getpixel((4, 4)))
        cut.save(HERE / 'recortes' / f'{name}.png', optimize=True)
        print(name, cut.size)


if __name__ == '__main__':
    main()
