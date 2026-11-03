#!/usr/bin/env python3
"""Give Ademir, in Part 4, the cobrador's voice from Part 3, now heard in person.

Ademir is the man with the ring: the cobrador whose threat Zinho heard as an audio message
in Part 3. His lines, recorded in the narrator's voice as ../narracao-ep04-ademir.wav, go
through the same Praat "Change gender" as ../../episodio-03/montagem/voz_cobranca.py, to the
same lower, darker and flatter voice, so whoever heard the message knows him. There is no
phone speaker this time: he talks face to face. The result, vozes/ademir.wav, keeps the
recording's exact length, so its word alignment holds.

The creator heard a test of this voice, made from Part 3's recording, on 02/11/2026.

Needs praat-parselmouth and FFmpeg.

    python voz_ademir.py [--fonte GRAVACAO]
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess

import parselmouth
from parselmouth.praat import call

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
SOURCE = EPISODE / 'narracao-ep04-ademir.wav'
OUT = HERE / 'vozes' / 'ademir.wav'
# The cobrador's voice, as in voz_cobranca.py: lower and darker than the narrator, with less
# melody. Calm, too calm.
VOICE = dict(formant_shift=.92, pitch_median=78, pitch_range=.8)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fonte', type=Path, default=SOURCE, help='recording to change (default: Part 4\'s)')
    parser.add_argument('--saida', type=Path, default=OUT)
    args = parser.parse_args()
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    sound = parselmouth.Sound(str(args.fonte))
    voiced = call(sound, 'Change gender', 60, 400, VOICE['formant_shift'], VOICE['pitch_median'], VOICE['pitch_range'], 1.0)
    # The change can push peaks past full scale; montar_timeline.py sets the level.
    voiced.scale_peak(.5)
    tmp = args.saida.with_suffix('.tmp.wav')
    voiced.save(str(tmp), 'WAV')
    length = sound.get_total_duration()
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(tmp), '-t', f'{length:.4f}',
                    '-af', f'afade=t=in:d=0.02,afade=t=out:st={length - .02:.4f}:d=0.02',
                    '-c:a', 'pcm_f32le', str(args.saida)], check=True)
    tmp.unlink()
    print(f'{args.saida}: {length:.2f}s, {VOICE}, in person (no phone speaker)')


if __name__ == '__main__':
    main()
