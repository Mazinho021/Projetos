#!/usr/bin/env python3
"""Match the opening lines, cut from Part 1's narration, to the Part 5 narrator.

On 06/11/2026 the creator asked for the usual opening back, in a short version: after the
part's own first line come the three fixed lines in Part 1's voice, "O assalto deu certo. Seu
parceiro ficou com dez milhões. Você ficou com o rosto no jornal." This is Part 3's
../../episodio-03/montagem/igualar_vozes.py, pointed at this part's narrator take: the median
pitch moves to his with Praat's "Change gender", formants and length untouched, and the
long-term spectrum is evened out against his. Writes vozes/vinheta.wav and
vozes/igualar-vozes.json.

Needs praat-parselmouth, NumPy and FFmpeg.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
_spec = importlib.util.spec_from_file_location('igualar_parte3', EPISODE.parent / 'episodio-03' / 'montagem' / 'igualar_vozes.py')
p3 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p3)


def main():
    p3.REFERENCE = EPISODE / 'narracao-ep05-narrador.wav'
    p3.OUT = HERE / 'vozes'
    p3.main()


if __name__ == '__main__':
    main()
