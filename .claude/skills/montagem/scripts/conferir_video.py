"""One frame of every scene of a finished video, with the HUD-safe guides, in contact sheets
(folha-N.jpg). Use i for the Instagram version and v for the vertical one.

    python conferir_video.py VIDEO TIMELINE OUT_DIR i|v
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw

video, timeline, out, vertical = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4] == 'v'
out.mkdir(parents=True, exist_ok=True)
scenes = json.loads(timeline.read_text())['scenes']
thumbs = []
for k, sc in enumerate(scenes):
    t = max(sc['start'] + .2, min(sc['end'] - .35, sc['start'] + .85*(sc['end'] - sc['start'])))
    f = out / f'q{k:02d}.png'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.2f}', '-i', str(video), '-frames:v', '1', str(f)], check=True)
    im = Image.open(f).convert('RGB')
    d = ImageDraw.Draw(im, 'RGBA')
    dy = 67 if vertical else 0
    d.rectangle((42, 87 + dy, 678, 193 + dy), outline=(0, 255, 255, 160), width=2)      # the panel
    d.line((0, 320, 720, 320), fill=(255, 0, 255, 120), width=2)                          # top 25%
    d.line((0, 1024, 720, 1024), fill=(255, 0, 255, 120), width=2)                        # bottom 20%
    if vertical:
        d.rectangle((590, 576, 720, 1024), outline=(255, 80, 80, 200), width=3)           # TikTok's buttons
        d.rectangle((0, 0, 720, 146), outline=(255, 160, 0, 160), width=2)                # search bar
    d.text((10, 1240), f'{k} {t:.1f}s {Path(sc.get("asset", sc.get("kind", ""))).name[:40]}', fill=(255, 255, 0))
    thumbs.append(im.resize((240, 427)))
cols = 6
for page in range(0, len(thumbs), 12):
    part = thumbs[page:page + 12]
    rows = (len(part) + cols - 1)//cols
    sheet = Image.new('RGB', (240*cols, 427*rows), 'black')
    for i, t in enumerate(part):
        sheet.paste(t, ((i % cols)*240, (i//cols)*427))
    sheet.save(out / f'folha-{page//12}.jpg', quality=85)
print(len(scenes), 'cenas;', sorted(p.name for p in out.glob('folha-*.jpg')))
