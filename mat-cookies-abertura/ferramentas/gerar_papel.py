"""Gera a textura de papel antigo (repetível em mosaico) usada na abertura.

Uso: python3 gerar_papel.py <pasta de saída>
"""
import sys, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

out = sys.argv[1]
N = 640
rng = np.random.default_rng(7)

def ruido_espectral(beta, fmin=0.0, fmax=1.0):
    """Ruído periódico (repetível) com espectro 1/f^beta."""
    fx = np.fft.fftfreq(N)[:, None]
    fy = np.fft.fftfreq(N)[None, :]
    f = np.sqrt(fx**2 + fy**2)
    f[0, 0] = 1
    amp = 1 / f**beta
    amp[(f < fmin) | (f > fmax)] = 0
    amp[0, 0] = 0
    fase = np.exp(2j * np.pi * rng.random((N, N)))
    r = np.real(np.fft.ifft2(amp * fase))
    return (r - r.mean()) / r.std()

# manchas grandes e suaves
manchas = ruido_espectral(2.2, fmax=0.06)
# textura média (fibras difusas)
media = ruido_espectral(1.2, fmin=0.02, fmax=0.25)
# grão fino
fino = ruido_espectral(0.3, fmin=0.2)

lum = 238 + 7 * manchas + 3.5 * media + 2.2 * fino

# fibras: linhas curtas e curvas, desenhadas com repetição nas bordas
fib = Image.new('L', (N, N), 128)
d = ImageDraw.Draw(fib)
for _ in range(900):
    x, y = rng.random(2) * N
    ang = rng.random() * np.pi
    comp = rng.uniform(6, 34)
    curv = rng.uniform(-0.08, 0.08)
    pts = []
    for k in range(8):
        t = k / 7 * comp
        a = ang + curv * t
        pts.append((x + np.cos(a) * t, y + np.sin(a) * t))
    tom = 128 + int(rng.choice([-1, 1]) * rng.uniform(10, 30))
    for ox in (-N, 0, N):
        for oy in (-N, 0, N):
            d.line([(px + ox, py + oy) for px, py in pts], fill=tom, width=1)
fib = fib.filter(ImageFilter.GaussianBlur(0.6))
lum += (np.asarray(fib, dtype=np.float32) - 128) * 0.35

# pontinhos escuros (impurezas do papel)
for _ in range(70):
    cx, cy = rng.integers(0, N, 2)
    r = rng.uniform(0.6, 1.8)
    yy, xx = np.ogrid[:N, :N]
    dx = np.minimum(abs(xx - cx), N - abs(xx - cx))
    dy = np.minimum(abs(yy - cy), N - abs(yy - cy))
    lum -= 26 * np.exp(-(dx**2 + dy**2) / (2 * r * r))

lum = np.clip(lum, 0, 255).astype(np.uint8)
img = Image.fromarray(lum, 'L')
img.save(os.path.join(out, 'papel.webp'), quality=80, method=6)
print('papel.webp', os.path.getsize(os.path.join(out, 'papel.webp')), 'media', lum.mean(), 'min', lum.min(), 'max', lum.max())
