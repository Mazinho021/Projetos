#!/usr/bin/env python3
"""Make Part 2's own sound effects in efeitos/. Whoosh, impacts, ticks, pops and the
message chime come from Part 1's efeitos/, which the renderer also searches.

The ringback, the pickup and hang-up, the light switch, the phone vibrating on the table
and the car pulling up outside are synthesized here, with numpy and FFmpeg filters. The
lock, the door and the footsteps are CC0 recordings from Kenney's RPG Audio pack
(see efeitos/LICENCA-kenney-rpg-audio.txt): pass the unzipped pack with --kenney to
convert them again; the converted WAVs are kept in efeitos/.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import wave

import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / 'efeitos'
SR = 48000
# efeitos/ name: file of the RPG Audio pack.
KENNEY = {'tranca.wav': 'metalLatch.ogg', 'porta-abre.wav': 'doorOpen_1.ogg', 'porta-fecha.wav': 'doorClose_4.ogg'}
STEPS = ('footstep00.ogg', 'footstep02.ogg')


def save(name, x, peak_db=-1.0):
    x = np.asarray(x, dtype=np.float64)
    x = x / (np.abs(x).max() or 1) * 10**(peak_db/20)
    with wave.open(str(OUT / name), 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x*32767).round().astype('<i2').tobytes())


def filtered(x, af):
    # Runs the signal through an FFmpeg audio filter chain.
    r = subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', af,
                        '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-'],
                       input=np.asarray(x, dtype='<f4').tobytes(), capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype='<f4').astype(np.float64)


def decoded(path):
    r = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-'],
                       capture_output=True, check=True)
    return np.frombuffer(r.stdout, dtype='<f4').astype(np.float64)


def times(dur):
    return np.arange(int(dur*SR))/SR


def faded(x, fade_in=.004, fade_out=.004):
    x = x.copy()
    a, b = int(fade_in*SR), int(fade_out*SR)
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x


def ringback(dur=1.0):
    # One ring of the 425 Hz tone a call makes while it rings in Brazil. The real cadence
    # is 1 s on, 4 s off; the edit spaces the three rings closer.
    t = times(dur)
    return faded(np.sin(2*np.pi*425*t) + .12*np.sin(2*np.pi*850*t), .015, .03)


def click(rng, dur=.003, cutoff=1500):
    burst = rng.uniform(-1, 1, int(.03*SR)) * np.exp(-times(.03)/dur)
    return filtered(burst, f'highpass=f={cutoff}')


def pickup():
    # Someone picks up: a click, then a moment of the line's hiss.
    rng = np.random.default_rng(11)
    out = np.zeros(int(.4*SR))
    c = click(rng)
    out[:len(c)] += c
    hiss = filtered(rng.uniform(-1, 1, len(out)), 'highpass=f=300,lowpass=f=3400') * .05
    return faded(out + hiss*np.minimum(1, times(.4)/.02), 0, .12)


def hang_up():
    # The phone's end-call sound: two short notes going down.
    out = []
    for freq, dur in ((784, .09), (523, .14)):
        t = times(dur)
        out.append(faded((np.sin(2*np.pi*freq*t) + .2*np.sin(4*np.pi*freq*t)) * np.exp(-t/.06), .003, .01))
    return np.concatenate(out)


def switch():
    # A wall light switch: the press and the snap a few milliseconds later, with a little body.
    rng = np.random.default_rng(5)
    out = np.zeros(int(.12*SR))
    for at, gain in ((0, .6), (.011, 1)):
        i = int(at*SR)
        c = click(rng, .0025, 900) * gain
        out[i:i+len(c)] += c[:len(out)-i]
        t = times(.03)
        body = np.sin(2*np.pi*190*t) * np.exp(-t/.008) * .35*gain
        out[i:i+len(body)] += body[:len(out)-i]
    return faded(out, 0, .02)


def vibration():
    # The phone buzzing twice on a wooden table: a 165 Hz motor whose rattle the table
    # amplifies, so phone speakers carry it too.
    rng = np.random.default_rng(23)
    pulses, gap, dur = 2, .2, .42
    out = np.zeros(int((pulses*dur + (pulses-1)*gap + .05)*SR))
    for k in range(pulses):
        t = times(dur)
        phase = 2*np.pi*165*t + .4*np.cumsum(rng.normal(0, .02, len(t)))
        motor = np.sign(np.sin(phase)) * (.75 + .25*np.sin(2*np.pi*33*t)) + .3*rng.uniform(-1, 1, len(t))
        pulse = faded(motor, .015, .03)
        i = int(k*(dur + gap)*SR)
        out[i:i+len(pulse)] += pulse
    return filtered(out, 'highpass=f=90,equalizer=f=230:t=q:w=1.2:g=8,equalizer=f=520:t=q:w=1.5:g=6,'
                         'equalizer=f=1150:t=q:w=2:g=3,lowpass=f=3000')


def car(dur=5.0, stop=1.8):
    # A car pulling up outside, heard through the window: the engine slows from a crawl
    # to idle as the tyres stop rolling, then idles. Firing pulses through a low-pass
    # read as an engine; the band near 120 Hz carries it on small speakers.
    rng = np.random.default_rng(31)
    n = int(dur*SR)
    t = np.arange(n)/SR
    rate = np.where(t < stop, 55 - 23*(t/stop)**.7, 32) * (1 + .03*np.sin(2*np.pi*.7*t))
    phase = np.cumsum(rate/SR)
    fire = np.diff(np.floor(phase), prepend=0) > 0
    pulses = np.zeros(n)
    idx = np.flatnonzero(fire)
    pulses[idx] = rng.uniform(.75, 1, len(idx))
    kernel = np.exp(-times(.012)/.003)
    engine = np.convolve(pulses, kernel)[:n]
    engine = filtered(engine, 'highpass=f=40,equalizer=f=120:t=q:w=1:g=6,lowpass=f=700,lowpass=f=900')
    roll = np.clip(1 - t/stop, 0, 1)**1.5
    tyres = filtered(rng.normal(0, 1, n), 'highpass=f=180,lowpass=f=800') * roll * .35
    env = np.minimum(1, t/1.0) * np.clip((dur - t)/1.2, 0, 1)
    return (engine/np.abs(engine).max() + tyres) * env


def kenney(pack):
    for name, source in KENNEY.items():
        save(name, decoded(pack / source))
    first, second = (decoded(pack / s) for s in STEPS)
    steps = np.zeros(int(.42*SR) + len(second))
    steps[:len(first)] += first
    steps[int(.42*SR):] += second*.8
    save('passos.wav', steps)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kenney', type=Path, help='unzipped RPG Audio pack, to convert its sounds again')
    args = parser.parse_args()
    OUT.mkdir(exist_ok=True)
    if args.kenney:
        files = {p.name: p for p in args.kenney.rglob('*.ogg')}
        kenney(files[KENNEY['tranca.wav']].parent)
    save('chamada-longa.wav', ringback())
    save('atende.wav', pickup())
    save('desliga.wav', hang_up())
    save('interruptor.wav', switch())
    save('vibracao.wav', vibration())
    save('carro.wav', car())
    print('Sound effects written to', OUT)


if __name__ == '__main__':
    main()
