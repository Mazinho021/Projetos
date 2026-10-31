#!/usr/bin/env python3
"""Give the cobrador, in Part 3, a voice apart from the narrator's.

His threat, recorded in the narrator's voice as ../narracao-ep03-cobranca.wav (about 91 Hz,
like the narrator's 94 Hz), goes through Praat's "Change gender" to a lower, darker and
flatter voice, and then through a phone speaker, because Zinho hears it as an audio message
with the phone at his ear. The result, vozes/cobranca.wav, keeps the recording's exact
length, so its word alignment holds.

It also cuts efeitos/cobranca-eco.wav, the message's first words ("Você correu. Ele não."),
which the edit plays again, low, under "Você escuta outra vez".

Needs praat-parselmouth and FFmpeg.
"""
from __future__ import annotations

from pathlib import Path
import subprocess

import parselmouth
from parselmouth.praat import call

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
SOURCE = EPISODE / 'narracao-ep03-cobranca.wav'
OUT = HERE / 'vozes' / 'cobranca.wav'
ECHO = HERE / 'efeitos' / 'cobranca-eco.wav'
# Lower and darker than the narrator, and with less melody: calm, too calm.
VOICE = dict(formant_shift=.92, pitch_median=78, pitch_range=.8)
PHONE = 'highpass=f=300,lowpass=f=3400,acompressor=threshold=-24dB:ratio=3:attack=5:release=80'
ECHO_SPAN = (0.0, 2.95)   # "Você correu. Ele não." in the recording, in seconds


def main():
    OUT.parent.mkdir(exist_ok=True)
    ECHO.parent.mkdir(exist_ok=True)
    sound = parselmouth.Sound(str(SOURCE))
    voiced = call(sound, 'Change gender', 60, 400, VOICE['formant_shift'], VOICE['pitch_median'], VOICE['pitch_range'], 1.0)
    # The change can push peaks past full scale; montar_timeline.py sets the level.
    voiced.scale_peak(.5)
    tmp = OUT.with_suffix('.tmp.wav')
    voiced.save(str(tmp), 'WAV')
    length = sound.get_total_duration()
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(tmp), '-t', f'{length:.4f}',
                    '-af', f'{PHONE},afade=t=in:d=0.02,afade=t=out:st={length - .02:.4f}:d=0.02',
                    '-c:a', 'pcm_f32le', str(OUT)], check=True)
    tmp.unlink()
    a, b = ECHO_SPAN
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(OUT), '-ss', f'{a:.3f}', '-to', f'{b:.3f}',
                    '-af', f'afade=t=in:d=0.02,afade=t=out:st={b - a - .25:.3f}:d=0.25', '-ar', '48000', '-ac', '1',
                    '-c:a', 'pcm_s16le', str(ECHO)], check=True)
    print(f'{OUT}: {length:.2f}s, {VOICE}, through a phone speaker; {ECHO.name}: {b - a:.2f}s')


if __name__ == '__main__':
    main()
