#!/usr/bin/env python3
"""Give Renato, in Part 3, the voice he has had since his audio message in Part 1.

His lines, recorded in the narrator's voice as ../narracao-ep03-renato.wav, go through the
same change as in Part 2 (../../episodio-02/montagem/voz_amigo.py): Praat's "Change gender"
with Part 1's settings, without the phone speaker's filter. The result, vozes/renato.wav,
keeps the recording's exact length, so its word alignment holds.

His last line, "Corre! Corre!", is one shout repeated: Codex cut "Zinho", which came out
sounding like "senhor" (see ../narracao-ep03-renato-job.json). The second shout goes a
little higher, so the repetition sounds desperate and not like a loop.

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

SOURCE = EPISODE / 'narracao-ep03-renato.wav'
OUT = HERE / 'vozes' / 'renato.wav'
LAST_SHOUT = 6.67   # the silence between the two shouts of "Corre! Corre!", in seconds
LAST_RISE = 1.08    # the second shout's pitch, against the first


def main():
    OUT.parent.mkdir(exist_ok=True)
    sound = parselmouth.Sound(str(SOURCE))
    length = sound.get_total_duration()

    def change(part, rise=1.0):
        return call(part, 'Change gender', 60, 400, VOICE['formant_shift'], VOICE['pitch_median']*rise,
                    VOICE['pitch_range'], 1.0)

    voiced = parselmouth.Sound.concatenate([change(sound.extract_part(0, LAST_SHOUT)),
                                            change(sound.extract_part(LAST_SHOUT, length), LAST_RISE)])
    # The change can push peaks past full scale; montar_timeline.py sets the level.
    voiced.scale_peak(.5)
    tmp = OUT.with_suffix('.tmp.wav')
    voiced.save(str(tmp), 'WAV')
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(tmp), '-t', f'{length:.4f}',
                    '-af', f'afade=t=in:d=0.02,afade=t=out:st={length - .02:.4f}:d=0.02', '-c:a', 'pcm_f32le', str(OUT)],
                   check=True)
    tmp.unlink()
    print(f'{OUT}: {length:.2f}s, the voice of Part 1’s message ({VOICE})')


if __name__ == '__main__':
    main()
