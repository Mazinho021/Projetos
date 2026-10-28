#!/usr/bin/env python3
"""Match the voices recorded apart to the Part 2 narrator, so the narration does not change
when the edit switches recordings.

The opening comes from Part 1's narration and the closing request from its own recording;
each came out of a separate voice generation, with the same voice but a different pitch
and brightness. This script moves each one's median pitch to the narrator's, with Praat's
"Change gender" (formants and length untouched), and then evens out its long-term
spectrum against the narrator's with a linear-phase filter. Timing does not change, so
the word alignments still hold. Writes vozes/vinheta.wav and vozes/pedido.wav.

Needs praat-parselmouth, NumPy and FFmpeg.
"""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import wave

import numpy as np
import parselmouth
from parselmouth.praat import call

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
PART1 = EPISODE.parent / 'episodio-01'
OUT = HERE / 'vozes'
SR = 24000
REFERENCE = EPISODE / 'narracao-ep02-narrador.wav'
# name: (recording, seconds of it to keep, from the start)
SOURCES = {'vinheta.wav': (PART1 / 'narracao-original.wav', 12.0),
           'pedido.wav': (EPISODE / 'narracao-ep02-pedido.wav', None)}
FRAME = 2048
MAX_DB = 9


def load(path, seconds=None):
    args = ['ffmpeg', '-v', 'error', '-i', str(path)] + (['-t', str(seconds)] if seconds else [])
    r = subprocess.run(args + ['-f', 'f32le', '-ac', '1', '-ar', str(SR), '-'], capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype='<f4').astype(np.float64)


def median_pitch(x):
    f0 = parselmouth.Sound(x, SR).to_pitch(pitch_floor=60, pitch_ceiling=300).selected_array['frequency']
    return float(np.median(f0[f0 > 0]))


def spectrum(x):
    # Mean power spectrum of the frames that carry voice.
    frames = [x[i:i+FRAME] for i in range(0, len(x) - FRAME, FRAME//2)]
    frames = [f for f in frames if np.sqrt(np.mean(f**2)) > 10**(-40/20)]
    return np.mean([np.abs(np.fft.rfft(f*np.hanning(FRAME)))**2 for f in frames], axis=0)


def smoothed_db(power, freqs):
    # One-third-octave smoothing, so the filter follows the voice's colour, not its harmonics.
    out = np.empty_like(power)
    for k, f in enumerate(freqs):
        band = (freqs >= f / 2**(1/6)) & (freqs <= f * 2**(1/6)) if f > 0 else freqs == 0
        out[k] = 10*np.log10(power[band].mean() + 1e-20)
    return out


def matched(x, target_db, freqs):
    gain = np.clip(target_db - smoothed_db(spectrum(x), freqs), -MAX_DB, MAX_DB)
    gain[freqs < 80] = gain[np.searchsorted(freqs, 80)]
    gain -= np.interp(1000, freqs, gain)       # the filter shapes the colour; loudness is set later
    kernel = np.fft.fftshift(np.fft.irfft(10**(gain/20), FRAME)) * np.hanning(FRAME)
    return np.convolve(x, kernel, mode='same')


def save(path, x):
    x = x / max(1e-9, np.abs(x).max()) * .7
    with wave.open(str(path), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x*32767).round().astype('<i2').tobytes())


def main():
    OUT.mkdir(exist_ok=True)
    ref = load(REFERENCE)
    freqs = np.fft.rfftfreq(FRAME, 1/SR)
    target = smoothed_db(spectrum(ref), freqs)
    ref_pitch = median_pitch(ref)
    report = {'reference': REFERENCE.name, 'reference_pitch_hz': round(ref_pitch, 1)}
    for name, (path, seconds) in SOURCES.items():
        x = load(path, seconds)
        before = median_pitch(x)
        sound = call(parselmouth.Sound(x, SR), 'Change gender', 60, 300, 1.0, ref_pitch, 1.0, 1.0)
        y = sound.values[0][:len(x)]
        y = np.pad(y, (0, len(x) - len(y)))
        y = matched(y, target, freqs)
        save(OUT / name, y)
        report[name] = {'source': path.name, 'pitch_before_hz': round(before, 1), 'pitch_after_hz': round(median_pitch(y), 1)}
    (OUT / 'igualar-vozes.json').write_text(json.dumps(report, indent=1), encoding='utf-8')
    print(json.dumps(report, indent=1))


if __name__ == '__main__':
    main()
