#!/usr/bin/env python3
"""Give the friend, in Part 2, the voice of his audio message in Part 1.

In Part 1 his message was the narrator's voice moved to another one with Praat's “Change
gender” (episodio-01/montagem/voz_amigo.py). Here his lines, recorded in the same voice as
narracao-ep02-amigo-charon.wav, go through the same change, so he sounds like the same man.
He is in the room this time, so the phone speaker's filter of Part 1 is left out. The
result, vozes/amigo.wav, keeps the recording's exact length, so its word alignment holds.

Needs praat-parselmouth, NumPy and FFmpeg.
"""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys

import parselmouth
from parselmouth.praat import call

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
sys.path.insert(0, str(EPISODE.parent / 'episodio-01' / 'montagem'))
from voz_amigo import VOICE  # noqa: E402  (Part 1's settings: the same man)

SOURCE = EPISODE / 'narracao-ep02-amigo-charon.wav'
OUT = HERE / 'vozes' / 'amigo.wav'


def main():
    OUT.parent.mkdir(exist_ok=True)
    sound = parselmouth.Sound(str(SOURCE))
    voiced = call(sound, 'Change gender', 60, 400, VOICE['formant_shift'], VOICE['pitch_median'], VOICE['pitch_range'], 1.0)
    # The change can push peaks past full scale; montar_timeline.py sets the level.
    voiced.scale_peak(.5)
    tmp = OUT.with_suffix('.tmp.wav')
    voiced.save(str(tmp), 'WAV')
    length = sound.get_total_duration()
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(tmp), '-t', f'{length:.4f}',
                    '-af', f'afade=t=in:d=0.02,afade=t=out:st={length - .02:.4f}:d=0.02', '-c:a', 'pcm_f32le', str(OUT)],
                   check=True)
    tmp.unlink()
    print(f'{OUT}: {length:.2f}s, the voice of Part 1’s message ({VOICE})')


if __name__ == '__main__':
    main()
