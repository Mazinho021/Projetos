#!/usr/bin/env python3
"""Match the opening, cut from Part 1's narration, to the Part 3 narrator.

The same as Part 2's ../../episodio-02/montagem/igualar_vozes.py, whose functions it uses:
the median pitch moves to the narrator's with Praat's "Change gender", formants and length
untouched, and the long-term spectrum is evened out against his. The Part 3 narrator came out
lower than Part 2's (about 91 Hz against 104 Hz), so Part 2's vozes/vinheta.wav would not
match him. Writes vozes/vinheta.wav and vozes/igualar-vozes.json.

Needs praat-parselmouth, NumPy and FFmpeg.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
_spec = importlib.util.spec_from_file_location('igualar_parte2', EPISODE.parent / 'episodio-02' / 'montagem' / 'igualar_vozes.py')
p2 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(p2)

OUT = HERE / 'vozes'
REFERENCE = EPISODE / 'narracao-ep03-narrador.wav'
SOURCES = {'vinheta.wav': (EPISODE.parent / 'episodio-01' / 'narracao-original.wav', 12.0)}


def main():
    OUT.mkdir(exist_ok=True)
    ref = p2.load(REFERENCE)
    freqs = np.fft.rfftfreq(p2.FRAME, 1/p2.SR)
    target = p2.smoothed_db(p2.spectrum(ref), freqs)
    ref_pitch = p2.median_pitch(ref)
    report = {'reference': REFERENCE.name, 'reference_pitch_hz': round(ref_pitch, 1)}
    for name, (path, seconds) in SOURCES.items():
        x = p2.load(path, seconds)
        before = p2.median_pitch(x)
        sound = p2.call(p2.parselmouth.Sound(x, p2.SR), 'Change gender', 60, 300, 1.0, ref_pitch, 1.0, 1.0)
        y = sound.values[0][:len(x)]
        y = np.pad(y, (0, len(x) - len(y)))
        y = p2.matched(y, target, freqs)
        p2.save(OUT / name, y)
        report[name] = {'source': path.name, 'pitch_before_hz': round(before, 1), 'pitch_after_hz': round(p2.median_pitch(y), 1)}
    (OUT / 'igualar-vozes.json').write_text(json.dumps(report, indent=1), encoding='utf-8')
    print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
