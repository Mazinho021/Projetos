#!/usr/bin/env python3
"""Render a narrated, illustrated animatic. No character motion is synthesized.

Needs Pillow, FFmpeg (libass), FFprobe. All generated working files stay in montagem/.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
REGULAR = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
W, H = 720, 1280
# TikTok draws its caption and buttons over the lower fifth of the frame. Subtitles sit
# above that area, and the TV/phone cards are lifted to leave room for them.
CAPTION_MARGIN = 290
CARD_LIFT = 60
AMBER = (246, 190, 73)
WHITE = (246, 242, 232)
INK = (13, 23, 30)


def run(args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def probe(path):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', path], capture_output=True, text=True)
    return float(json.loads(r.stdout)['format']['duration'])


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else REGULAR, size)


def cover(path, size=(W, H), center=(.5, .5), crop=None):
    im = Image.open(path).convert('RGB')
    if crop:
        # Optional framing inside the illustration: left, top, right, bottom as fractions.
        l, t, r, b = crop
        im = im.crop((round(l*im.width), round(t*im.height), round(r*im.width), round(b*im.height)))
    return ImageOps.fit(im, size, method=Image.Resampling.LANCZOS, centering=center)


def text(draw, xy, value, size=30, fill=WHITE, bold=False, anchor=None):
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor, stroke_width=0)


def wrap(draw, value, max_width, size, bold=False):
    words, lines, current = value.split(), [], ''
    f = font(size, bold)
    for word in words:
        candidate = f'{current} {word}'.strip()
        if current and draw.textlength(candidate, font=f) > max_width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def multiline(draw, xy, value, max_width, size=30, fill=WHITE, bold=False, spacing=10):
    x, y = xy
    for line in wrap(draw, value, max_width, size, bold):
        text(draw, (x, y), line, size, fill, bold)
        y += size + spacing
    return y


def rounded_image(target, image, box, radius=20):
    x0, y0, x1, y1 = box
    resized = ImageOps.fit(image.convert('RGB'), (x1-x0, y1-y0), Image.Resampling.LANCZOS)
    mask = Image.new('L', resized.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, resized.width-1, resized.height-1), radius, fill=255)
    target.paste(resized, (x0, y0), mask)


def face_photo():
    # Exactly the same fictional portrait is used on the TV and in the earlier message.
    # A dedicated frontal portrait, when present, replaces the crop of scene 01.
    portrait = EPISODE / 'retrato-zinho.png'
    if portrait.exists():
        return ImageOps.fit(Image.open(portrait).convert('RGB'), (520, 440), Image.Resampling.LANCZOS, centering=(.5, .4))
    im = Image.open(EPISODE / 'cena-01-base.png').convert('RGB')
    crop = im.crop((int(im.width*.21), int(im.height*.13), int(im.width*.81), int(im.height*.48)))
    return ImageOps.fit(crop, (520, 440), Image.Resampling.LANCZOS)


def backdrop(path, dark=False, blur=False, crop=None):
    im = cover(path, crop=crop)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(15))
    if dark:
        im = ImageEnhance.Brightness(im).enhance(.34)
    return im.convert('RGBA')


def caption_gradient(im):
    # Keep the lower caption region readable without turning the entire scene dark.
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(920, H):
        a = int(95 * ((y-920)/(H-920)))
        d.line((0, y, W, y), fill=(3, 8, 12, a))
    return Image.alpha_composite(im, layer)


def make_card(kind, scene, portrait):
    card = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    if kind == 'tv':
        d.rounded_rectangle((45, 235, 675, 902), 32, fill=(15, 19, 23, 255), outline=(94, 99, 102), width=4)
        d.rectangle((70, 265, 650, 834), fill=(22, 40, 51))
        rounded_image(card, portrait, (87, 288, 633, 710), radius=3)
        d = ImageDraw.Draw(card)
        d.rectangle((70, 706, 650, 836), fill=(21, 33, 41))
        d.rectangle((70, 706, 80, 836), fill=AMBER)
        text(d, (105, 720), 'ZINHO', 45, AMBER, True)
        multiline(d, (105, 775), 'PRIMEIRO SUSPEITO IDENTIFICADO', 515, 24, WHITE, True, 3)
        text(d, (360, 865), 'NOTICIÁRIO LOCAL', 17, (141, 149, 152), anchor='mm')
    elif kind == 'chat':
        d.rounded_rectangle((90, 180, 630, 955), 46, fill=(15, 21, 28, 255), outline=(96, 106, 110), width=3)
        d.rounded_rectangle((257, 194, 463, 218), 12, fill=(3, 7, 10))
        d.rounded_rectangle((115, 240, 605, 922), 20, fill=(29, 43, 50))
        d.rectangle((115, 240, 605, 330), fill=(38, 57, 65))
        d.ellipse((140, 260, 188, 308), fill=(67, 87, 96))
        text(d, (211, 271), 'AMIGO', 25, WHITE, True)
        clothes_path = resolve_asset('cena-03-roupas.png')
        rounded_image(card, Image.open(clothes_path), (155, 375, 570, 725), radius=16)
        d = ImageDraw.Draw(card)
        if scene.get('status', 'seen') == 'seen':
            text(d, (565, 747), 'Visualizado', 23, (128, 192, 211), anchor='ra')
            text(d, (360, 856), 'Nenhuma resposta.', 25, (176, 185, 188), anchor='mm')
        else:
            text(d, (565, 747), 'Enviada', 23, (141, 149, 152), anchor='ra')
    elif kind == 'comparison':
        for y, label in [(180, 'A FOTO ENVIADA'), (580, 'A FOTO NO JORNAL')]:
            d.rounded_rectangle((92, y, 628, y+365), 22, fill=(19, 31, 39, 255), outline=(100, 112, 117), width=2)
            rounded_image(card, portrait, (110, y+62, 610, y+344), radius=10)
            d = ImageDraw.Draw(card)
            text(d, (360, y+32), label, 22, AMBER, True, anchor='mm')
    elif kind == 'audio':
        d.rounded_rectangle((80, 795, 640, 958), 25, fill=(15, 27, 36, 239), outline=(113, 128, 132), width=2)
        text(d, (110, 818), 'ÁUDIO DO AMIGO', 22, AMBER, True)
        for j in range(55):
            amp = int(9 + 26*abs(math.sin(j*.69)*math.cos(j*.33)))
            x = 112 + j*9
            d.rounded_rectangle((x, 903-amp, x+4, 903+amp), 2, fill=(171, 193, 195))
        d.rounded_rectangle((112, 941, 598, 946), 2, fill=(66, 85, 95))
    return card.crop((0, CARD_LIFT, W, H+CARD_LIFT))


def resolve_asset(name):
    p = Path(name)
    if not p.is_absolute():
        p = EPISODE / p
    if not p.exists():
        print(f'NOTE: {p.name} missing; using scene 01 as temporary fallback.', flush=True)
        p = EPISODE / 'cena-01-base.png'
    return p


def make_scene_assets(scene, index, work):
    # No series marker: TikTok and Reels cover the top of the frame, so the series
    # name and episode go in the post text instead.
    kind = scene.get('kind', 'art')
    path = resolve_asset(scene.get('asset', 'cena-01-base.png'))
    bg = backdrop(path, dark=kind in ('tv', 'chat', 'comparison'), blur=kind in ('tv', 'chat', 'comparison'), crop=scene.get('crop'))
    bg = caption_gradient(bg)
    bg_path = work / f'{index:02d}-bg.png'
    bg.convert('RGB').save(bg_path)
    card = make_card(kind, scene, face_photo())
    card_path = work / f'{index:02d}-card.png'
    card.save(card_path)
    return bg_path, card_path


def render_scene(scene, index, work, fps):
    start, end = float(scene['start']), float(scene['end'])
    # Quantize absolute boundaries, preventing small per-scene rounding errors
    # from accumulating into subtitle drift across the assembled episode.
    frames = max(1, round(end*fps) - round(start*fps))
    bg, card = make_scene_assets(scene, index, work)
    out = work / f'{index:02d}.mp4'
    zoom = float(scene.get('zoom', .028 if scene.get('kind', 'art') == 'art' else .012))
    direction = scene.get('direction', 'in')
    expr = f'1+{zoom}*on/{max(frames-1, 1)}' if direction == 'in' else f'1+{zoom}-{zoom}*on/{max(frames-1, 1)}'
    camera = f"scale=1440:2560,zoompan=z='{expr}':x='iw/2-iw/zoom/2':y='ih/2-ih/zoom/2':d={frames}:s={W}x{H}:fps={fps}"
    graph = f'[0:v]{camera}[bg];[1:v]format=rgba,fade=t=in:st=0.12:d=0.28:alpha=1[card];[bg][card]overlay=0:0:shortest=1[composed];'
    if scene.get('kind') == 'audio':
        # A subtle progress marker follows the friend's voice: "play" holds its absolute
        # start and end, and defaults to the scene. The waveform artwork is
        # deliberately illustrative; it is not presented as measured audio data.
        duration = frames/fps
        p0, p1 = (float(v)-start for v in scene.get('play', [start+.4, end]))
        travel = max(.1, p1-p0)
        graph += f"color=c=0xF6BE49:s=10x6:r={fps}:d={duration}[progress];[composed][progress]overlay=x='112+476*min(max(t-{p0:.3f},0)/{travel:.3f},1)':y={941-CARD_LIFT}:enable='gte(t,0.4)':shortest=1,format=yuv420p[v]"
    elif scene.get('kind') == 'tv':
        # Less than one RGB level: a small TV-light modulation, never a flash.
        graph += "[composed]eq=brightness='0.003*sin(2*PI*t*1.7)':eval=frame,format=yuv420p[v]"
    else:
        graph += '[composed]format=yuv420p[v]'
    log = work / f'{index:02d}.log'
    with log.open('w') as err:
        run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-i', bg, '-loop', '1', '-framerate', str(fps), '-i', card,
             '-filter_complex', graph, '-map', '[v]', '-frames:v', str(frames), '-an', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-threads', '2', out], stderr=err)
    print(f'Plan {index+1}: {start:.2f}–{end:.2f}s rendered', flush=True)
    return out


def ass_time(value):
    cs = max(0, round(float(value)*100))
    h, rem = divmod(cs, 360000)
    m, rem = divmod(rem, 6000)
    s, c = divmod(rem, 100)
    return f'{h}:{m:02d}:{s:02d}.{c:02d}'


def ass_text(value):
    value = value.replace('\\', '/').replace('{', '(').replace('}', ')')
    # Explicit line breaks are honoured. Otherwise wrap to a compact two-line block.
    if '\n' in value:
        return value.replace('\n', '\\N')
    d = ImageDraw.Draw(Image.new('RGB', (W, H)))
    lines = wrap(d, value, 590, 36, True)
    return '\\N'.join(lines)


def write_subtitles(captions, path):
    # The friend's lines ("voice": "amigo") use amber italics, since one narrator reads every line.
    header = f'''[Script Info]
ScriptType: v4.00+
PlayResX: 720
PlayResY: 1280
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,36,&H00F7F3EC,&H000000FF,&H0010181B,&H8C000000,-1,0,0,0,100,100,0,0,1,3,1,2,58,72,{CAPTION_MARGIN},1
Style: Amigo,DejaVu Sans,36,&H0049BEF6,&H000000FF,&H0010181B,&H8C000000,-1,-1,0,0,100,100,0,0,1,3,1,2,58,72,{CAPTION_MARGIN},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    lines = [header]
    for cap in captions:
        if cap['end'] <= cap['start']:
            continue
        style = 'Amigo' if cap.get('voice') == 'amigo' else 'Default'
        lines.append(f"Dialogue: 0,{ass_time(cap['start'])},{ass_time(cap['end'])},{style},,0,0,0,,{{\\fad(60,60)}}{ass_text(cap['text'])}\n")
    path.write_text(''.join(lines), encoding='utf-8')


def template(duration):
    spans = [(0, 8, 'art', 'cena-01-base.png'), (8, 14, 'tv', 'cena-01-base.png'),
             (14, 22, 'art', 'cena-03-roupas.png'), (22, 32, 'art', 'cena-07-audio.png'),
             (32, 37, 'chat', 'cena-03-roupas.png'), (37, 46, 'comparison', 'cena-01-base.png'),
             (46, 58, 'audio', 'cena-07-audio.png'), (58, 63, 'art', 'cena-07-audio.png'),
             (63, 71, 'art', 'cena-09-porta.png'), (71, 79, 'art', 'cena-09-porta.png')]
    return {'timing_status': 'provisional_scaled_to_audio', 'duration': duration,
            'scenes': [{'start': round(a/79*duration, 3), 'end': round(b/79*duration, 3), 'kind': k, 'asset': p} for a, b, k, p in spans],
            'captions': []}


def main():
    global W, H
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio', type=Path, required=True)
    parser.add_argument('--timeline', type=Path)
    parser.add_argument('--output', type=Path, default=HERE / 'zinho-ep01-animatic.mp4')
    parser.add_argument('--fps', type=int, default=25)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    audio_duration = probe(args.audio)
    work = HERE / 'work'
    work.mkdir(parents=True, exist_ok=True)
    if args.timeline:
        timeline = json.loads(args.timeline.read_text())
    else:
        timeline = template(audio_duration)
    # "tail" holds the last scene, in silence, for that many seconds after the voice.
    tail = float(timeline.get('tail', 0))
    duration = audio_duration + tail
    scenes = timeline['scenes']
    if not scenes:
        raise ValueError('At least one scene is required')
    # Require contiguous scene windows so assembly does not silently shift captions.
    edge = 0.0
    for scene in scenes:
        if abs(float(scene['start'])-edge) > .045 or float(scene['end']) <= float(scene['start']):
            raise ValueError(f'Non-contiguous or invalid scene: {scene}')
        edge = float(scene['end'])
    if abs(edge-duration) > .15:
        raise ValueError(f'Timeline ends at {edge:.3f}s; audio plus tail is {duration:.3f}s. Adjust timeline first.')
    used = HERE / 'timeline-used.json'
    used.write_text(json.dumps(timeline, ensure_ascii=False, indent=2))
    ass = work / 'captions.ass'
    write_subtitles(timeline.get('captions', []), ass)
    if args.prepare_only:
        for i, s in enumerate(scenes):
            make_scene_assets(s, i, work)
        print(f'Prepared cards and captions in {work}')
        return
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = [pool.submit(render_scene, s, i, work, args.fps) for i, s in enumerate(scenes)]
        parts = [f.result() for f in futures]
    playlist = work / 'concat.txt'
    playlist.write_text(''.join(f"file '{p.as_posix()}'\n" for p in parts))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # All inputs share codec/rate. Final pass burns captions and normalizes speech gently.
    audio_filter = 'loudnorm=I=-16:TP=-1.5:LRA=9' + (f',apad=pad_dur={tail}' if tail > 0 else '')
    run(['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-f', 'concat', '-safe', '0', '-i', playlist,
         '-i', args.audio, '-map', '0:v:0', '-map', '1:a:0', '-vf', f'ass={ass.as_posix()}',
         '-af', audio_filter, '-t', str(duration), '-c:v', 'libx264', '-preset', 'fast',
         '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-movflags', '+faststart',
         '-threads', '2', args.output])
    result = {'output': str(args.output), 'duration': probe(args.output), 'audio_duration': audio_duration, 'tail': tail,
              'scenes': len(scenes), 'captions': len(timeline.get('captions', [])),
              'type': 'illustrated animatic with camera motion and graphics; no generated body animation'}
    (HERE / 'render-report.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
