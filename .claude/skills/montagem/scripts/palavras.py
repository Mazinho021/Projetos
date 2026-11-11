"""Word timings and probabilities from faster-whisper, no prompt.

    python palavras.py FILE START END [medium small]
"""
import subprocess, sys
import numpy as np
from faster_whisper import WhisperModel
path, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
for size in sys.argv[4:] or ['medium']:
    model = WhisperModel(size, device='cpu', compute_type='int8')
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(a), '-to', str(b), '-i', path, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'],
                         check=True, capture_output=True).stdout
    audio = np.frombuffer(raw, np.float32)
    segs, _ = model.transcribe(audio, language='pt', beam_size=5, word_timestamps=True, vad_filter=False)
    print('==', size)
    for s in segs:
        print(' '.join(f'{w.word.strip()}[{a + w.start:.2f}-{a + w.end:.2f} p{w.probability:.2f}]' for w in s.words))
