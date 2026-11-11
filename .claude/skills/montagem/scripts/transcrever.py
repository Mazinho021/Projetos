"""Plain transcription with faster-whisper medium, no prompt, as CLAUDE.md asks.

    python transcrever.py FILE [FILE ...]
"""
import subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

model = WhisperModel('medium', device='cpu', compute_type='int8')
for path in sys.argv[1:]:
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'],
                         check=True, capture_output=True).stdout
    audio = np.frombuffer(raw, np.float32)
    segs, _ = model.transcribe(audio, language='pt', beam_size=5, initial_prompt=None, vad_filter=False)
    print('==', path.split('/')[-1])
    print(' '.join(s.text.strip() for s in segs), flush=True)
