#!/usr/bin/env python3
"""Align the approved narration script to the recorded voice, word by word.

Needs faster-whisper (pip install faster-whisper), NumPy and FFmpeg. Recognition only
supplies timings: the words written to the output always come from the script.
"""
from __future__ import annotations

import argparse
from difflib import SequenceMatcher
import json
from pathlib import Path
import re
import subprocess
import unicodedata

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent


def norm(token):
    t = unicodedata.normalize('NFD', token.lower())
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in t if unicodedata.category(c) != 'Mn'))


def recognize(audio, model_name):
    import numpy as np
    from faster_whisper import WhisperModel
    # Decode with FFmpeg: recent PyAV releases reject faster-whisper's own decoder arguments.
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', audio, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'],
                         check=True, capture_output=True).stdout
    model = WhisperModel(model_name, device='cpu', compute_type='int8')
    segments, _ = model.transcribe(np.frombuffer(pcm, dtype=np.float32), language='pt', word_timestamps=True,
                                   beam_size=5, vad_filter=False, condition_on_previous_text=False)
    return [{'text': w.word.strip(), 'start': w.start, 'end': w.end} for s in segments for w in s.words]


def pauses(audio, noise_db, min_dur):
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', audio, '-af', f'silencedetect=noise={noise_db}dB:d={min_dur}',
                        '-f', 'null', '-'], capture_output=True, text=True, check=True)
    starts = [float(v) for v in re.findall(r'silence_start: ([\d.]+)', r.stderr)]
    ends = [float(v) for v in re.findall(r'silence_end: ([\d.]+)', r.stderr)]
    return list(zip(starts, ends))


def align(script_words, heard):
    a, b = [norm(w) for w in script_words], [norm(w['text']) for w in heard]
    times, exact = [None] * len(a), 0
    for op, a0, a1, b0, b1 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == 'equal':
            exact += a1 - a0
        if op == 'equal' or (op == 'replace' and a1-a0 == b1-b0):
            for i, j in zip(range(a0, a1), range(b0, b1)):
                times[i] = [heard[j]['start'], heard[j]['end']]
        elif op == 'replace':
            # Spread the heard span over the script words, proportionally to their length.
            start, end = heard[b0]['start'], heard[b1-1]['end']
            weights = [max(1, len(a[i])) for i in range(a0, a1)]
            edge = start
            for i, wgt in zip(range(a0, a1), weights):
                step = (end-start) * wgt / sum(weights)
                times[i] = [edge, edge+step]
                edge += step
    # Script words the recognizer skipped share the time between their neighbours.
    i = 0
    while i < len(times):
        if times[i] is not None:
            i += 1
            continue
        k = i
        while k < len(times) and times[k] is None:
            k += 1
        left = times[i-1][1] if i else 0.0
        right = times[k][0] if k < len(times) else left + .3*(k-i)
        step = (right-left) / (k-i)
        for n in range(i, k):
            times[n] = [left + step*(n-i), left + step*(n-i+1)]
        i = k
    return times, exact


def snap(times, gaps):
    # Recognizer boundaries drift around pauses; measured silence is more precise.
    # A pause found between two consecutive words becomes the exact edge of both.
    def mid(t):
        return (t[0]+t[1]) / 2
    for s0, s1 in gaps:
        centre = (s0+s1) / 2
        if centre < mid(times[0]) and s1 < times[0][1]:
            times[0][0] = s1
        elif centre > mid(times[-1]) and s0 > times[-1][0]:
            times[-1][1] = s0
        for prev, nxt in zip(times, times[1:]):
            if mid(prev) < centre < mid(nxt) and prev[0] < s0 and s1 < nxt[1]:
                prev[1], nxt[0] = s0, s1
                break
    return times


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio', type=Path, default=EPISODE / 'narracao-original.wav')
    parser.add_argument('--script', type=Path, default=EPISODE.parent / 'narracao-ep01-zinho.txt')
    parser.add_argument('--output', type=Path, default=HERE / 'alinhamento-narracao.json')
    parser.add_argument('--model', default='medium')
    parser.add_argument('--noise-db', type=float, default=-38)
    parser.add_argument('--min-pause', type=float, default=.25)
    args = parser.parse_args()
    script_words = [w for w in args.script.read_text(encoding='utf-8').split() if norm(w)]
    heard = recognize(args.audio, args.model)
    gaps = pauses(args.audio, args.noise_db, args.min_pause)
    times, exact = align(script_words, heard)
    snap(times, gaps)
    result = {'audio': args.audio.name, 'script': args.script.name, 'model': args.model,
              'words_in_script': len(script_words), 'words_matched_exactly': exact,
              'pauses': [[round(s0, 3), round(s1, 3)] for s0, s1 in gaps],
              'words': [{'i': i, 'text': w, 'start': round(t[0], 3), 'end': round(t[1], 3)}
                        for i, (w, t) in enumerate(zip(script_words, times))]}
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{exact}/{len(script_words)} script words matched exactly; wrote {args.output}')


if __name__ == '__main__':
    main()
