"""A part's drawings (cena-*.png), four per sheet, with lines every 10% of the width and height
and their coordinates in a 720 × 1280 frame, to check the composition rules of CLAUDE.md.

    python grade.py DRAWINGS_DIR OUT_DIR
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
src, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
files = sorted(src.glob('cena-*.png'))
W, H = 360, 640
f = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 13)
for k in range(0, len(files), 4):
    sheet = Image.new('RGB', (W*4 + 30, H + 30), 'white')
    for j, p in enumerate(files[k:k+4]):
        im = Image.open(p).convert('RGB').resize((W, H))
        d = ImageDraw.Draw(im)
        for i in range(1, 10):
            d.line([(0, H*i/10), (W, H*i/10)], fill=(255, 0, 255), width=1)
            d.line([(W*i/10, 0), (W*i/10, H)], fill=(0, 255, 255), width=1)
            d.text((2, H*i/10 - 14), str(i*128), fill=(255, 0, 255), font=f)
            d.text((W*i/10 + 2, 2), str(i*72), fill=(0, 200, 255), font=f)
        sheet.paste(im, (j*(W + 10), 25))
        ImageDraw.Draw(sheet).text((j*(W + 10) + 4, 4), p.stem, fill='black', font=f)
    sheet.save(out / f'grade-{k//4 + 1}.jpg', quality=88)
