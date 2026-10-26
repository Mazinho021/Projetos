#!/usr/bin/env python3
"""Give the friend's voice message a voice of its own, apart from the narrator's.

The narration reads the friend's audio message (“Eu estava devendo … no meu lugar.”) in
the narrator's deep voice, so the message and its replay sounded like the narrator
again. This script cuts the line from narracao-original.wav, moves it to another voice
with Praat's “Change gender” (higher pitch and a shorter vocal tract than the narrator's
bass) and thins it like a phone speaker. The result, efeitos/audio-amigo.wav, keeps the
line's exact length: montar_timeline.py puts it in the narration in place of the
narrator's reading, and gerar_efeitos.py cuts the replay from it.

Needs praat-parselmouth (pip install praat-parselmouth), NumPy and FFmpeg.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import subprocess
import tempfile
import wave

from gerar_efeitos import FRIEND_LINE, FRIEND_PAD, OUT

HERE = Path(__file__).resolve().parent
NARRATION = HERE.parent / 'narracao-original.wav'
# The narrator's pitch sits around 85 Hz; the friend's goes to an ordinary male register.
VOICE = dict(formant_shift=1.08, pitch_median=112, pitch_range=1.1)
PHONE = 'highpass=f=350,lowpass=f=3200,acompressor=threshold=-24dB:ratio=3:attack=5:release=80'
LEVEL_DB = -.3   # against the narrator's reading of the line: about 1 dB under the narration in the final mix


def bounds(words, rate):
    # First and last sample of the line, padded into the pauses around it.
    return (round((words[FRIEND_LINE[0]]['start'] - FRIEND_PAD) * rate),
            round((words[FRIEND_LINE[1]]['end'] + FRIEND_PAD) * rate))


def loudness(path):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', str(path), '-af', 'ebur128', '-f', 'null', '-'],
                       check=True, capture_output=True, text=True)
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', r.stderr)[-1])


def main():
    import numpy as np
    import parselmouth
    from parselmouth.praat import call

    words = json.loads((HERE / 'alinhamento-narracao.json').read_text(encoding='utf-8'))['words']
    with wave.open(str(NARRATION)) as w:
        rate = w.getframerate()
        samples = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16) / 32768
    first, last = bounds(words, rate)
    line = parselmouth.Sound(samples[first:last], sampling_frequency=rate)
    voiced = call(line, 'Change gender', 60, 400, VOICE['formant_shift'], VOICE['pitch_median'],
                  VOICE['pitch_range'], 1.0)
    with tempfile.TemporaryDirectory() as tmp:
        reading, shifted, phone = (Path(tmp) / n for n in ('reading.wav', 'shifted.wav', 'phone.wav'))
        line.save(str(reading), 'WAV')
        # The voice change can push peaks past full scale; the loudness match below sets the level.
        voiced.scale_peak(.5)
        voiced.save(str(shifted), 'WAV')
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(shifted), '-af', PHONE, '-c:a', 'pcm_f32le', str(phone)],
                       check=True)
        gain = loudness(reading) - loudness(phone) + LEVEL_DB
        length = (last - first) / rate
        subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(phone), '-af',
                        f'volume={gain:.2f}dB,afade=t=in:d=0.02,afade=t=out:st={length - .02:.4f}:d=0.02',
                        '-c:a', 'pcm_f32le', str(OUT / 'audio-amigo.wav')], check=True)
    print(f'{OUT / "audio-amigo.wav"}: {last - first} samples from {first / rate:.3f}s, {gain:+.1f} dB')


if __name__ == '__main__':
    main()
