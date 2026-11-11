"""Which of two texts the recording fits better: Whisper's own probability for each token.

    python pontuar.py FILE START END "text 1" "text 2"
"""
import math, subprocess, sys
import numpy as np
import ctranslate2
from faster_whisper import WhisperModel
from faster_whisper.tokenizer import Tokenizer

path, a, b = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
candidatos = sys.argv[4:]
for size in ('medium', 'small'):
    model = WhisperModel(size, device='cpu', compute_type='int8')
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(a), '-to', str(b), '-i', path, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'],
                         check=True, capture_output=True).stdout
    audio = np.frombuffer(raw, np.float32)
    feats = model.feature_extractor(audio)
    frames = feats.shape[-1]
    pad = np.zeros((feats.shape[0], 3000), np.float32)
    pad[:, :min(3000, frames)] = feats[:, :3000]
    enc = model.model.encode(ctranslate2.StorageView.from_array(pad[None]), to_cpu=False)
    tok = Tokenizer(model.hf_tokenizer, True, task='transcribe', language='pt')
    for c in candidatos:
        ids = tok.encode(' ' + c)
        res = model.model.align(enc, tok.sot_sequence, [ids], frames)
        probs = res[0].text_token_probs
        print(f'{size:6s} {c!r}: média log-prob {sum(math.log(max(p, 1e-9)) for p in probs)/len(probs):.3f}, '
              f'primeiras {[round(p, 3) for p in probs[:3]]}')
