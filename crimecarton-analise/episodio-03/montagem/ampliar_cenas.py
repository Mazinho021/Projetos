#!/usr/bin/env python3
"""Amplia as ilustrações da Parte 3 com o Real-ESRGAN anime 6B.

O gerador de imagens do Codex entrega no máximo 941 × 1672, abaixo dos 1080 × 1920
pedidos no CLAUDE.md. Este script lê os desenhos originais em ../originais/, amplia
4 vezes com o modelo, reduz para 1440 × 2560 (o dobro do quadro do vídeo) e devolve a
cor média do original, para a IA só acrescentar o traço mais limpo. O resultado vai
para ../, com o mesmo nome, e é o que a montagem usa.

    python crimecarton-analise/episodio-03/montagem/ampliar_cenas.py [cena-01-portao.png ...]

O modelo (18 MB) é baixado na primeira vez para work/modelos/.
"""
import argparse
import subprocess
import time
from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image, ImageFilter

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
ORIGINAIS = EPISODE / 'originais'
MODELO = HERE / 'work' / 'modelos' / 'realesrgan_anime6b.onnx'
URL = 'https://huggingface.co/RekluzLabs/realesrgan_anime6b.onnx/resolve/main/realesrgan_anime6b.onnx'
SAIDA = (1440, 2560)
RAIO_COR = 3  # desfoque, em pixels da saída, que separa a cor média do traço fino


def baixar_modelo():
    if MODELO.exists():
        return
    MODELO.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['curl', '-sSL', '--fail', '--retry', '3', '-o', str(MODELO), URL], check=True)


def ampliar4(arr, sess, tile=320, pad=16):
    """arr: float32 H×W×3 em 0..1. Devolve 4H × 4W × 3, processando em blocos com margem."""
    h0, w0, _ = arr.shape
    out = np.zeros((h0 * 4, w0 * 4, 3), np.float32)
    p = np.pad(arr, ((pad, pad), (pad, pad), (0, 0)), mode='reflect')
    for y in range(0, h0, tile):
        for x in range(0, w0, tile):
            h, w = min(tile, h0 - y), min(tile, w0 - x)
            blk = np.ascontiguousarray(p[y:y + h + 2 * pad, x:x + w + 2 * pad].transpose(2, 0, 1)[None])
            r = sess.run(None, {'input': blk})[0][0].transpose(1, 2, 0)
            out[y * 4:(y + h) * 4, x * 4:(x + w) * 4] = r[pad * 4:(pad + h) * 4, pad * 4:(pad + w) * 4]
    return np.clip(out, 0, 1)


def desfocar(arr):
    im = Image.fromarray((arr * 255 + .5).astype(np.uint8))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(RAIO_COR)), np.float32) / 255


def ampliar(caminho, sess):
    original = Image.open(caminho).convert('RGB')
    arr = np.asarray(original, np.float32) / 255
    ia = Image.fromarray((ampliar4(arr, sess) * 255 + .5).astype(np.uint8)).resize(SAIDA, Image.LANCZOS)
    ia = np.asarray(ia, np.float32) / 255
    base = np.asarray(original.resize(SAIDA, Image.LANCZOS), np.float32) / 255
    # O traço vem da IA e a cor média vem do desenho original.
    final = np.clip(ia + desfocar(base) - desfocar(ia), 0, 1)
    return Image.fromarray((final * 255 + .5).astype(np.uint8))


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('nomes', nargs='*', help='só estas cenas (padrão: todas em originais/)')
    args = ap.parse_args()
    baixar_modelo()
    opts = ort.SessionOptions()
    sess = ort.InferenceSession(str(MODELO), opts, providers=['CPUExecutionProvider'])
    nomes = args.nomes or sorted(p.name for p in ORIGINAIS.glob('cena-*.png'))
    for nome in nomes:
        t = time.time()
        ampliar(ORIGINAIS / nome, sess).save(EPISODE / nome)
        print(f'{nome}: {SAIDA[0]}×{SAIDA[1]} em {time.time() - t:.0f} s', flush=True)


if __name__ == '__main__':
    main()
