#!/usr/bin/env python3
"""Render a narrated, illustrated animatic. No character motion is synthesized.

Needs Pillow, FFmpeg (libass), FFprobe and the Poppins fonts in crimecarton-analise/fontes.
It serves every part of the series: a timeline's assets are found next to its episode
(the parent of the timeline's folder), and its working files, records and its own sound
effects stay in the timeline's folder. Effects it does not have come from Part 1's efeitos/.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import json
import math
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageOps

import graficos
from graficos import FONTS, W, H, place, rgb, text_sprite

HERE = Path(__file__).resolve().parent
EPISODE = HERE.parent
# TikTok and Reels draw their caption and buttons over the lower fifth of the frame;
# subtitles, when a timeline has them, sit above that area.
CAPTION_MARGIN = 290
# Cards start below the HUD and its tag, drawn by graficos.
CARD_TOP = 300
AUDIO_TRACK_Y = 941
EFFECTS = HERE / 'efeitos'
# Set from the timeline's location in main(); Part 1's folders by default.
ROOT = EPISODE
SOUNDS = [EFFECTS]


def run(args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def probe(path):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', path], capture_output=True, text=True)
    return float(json.loads(r.stdout)['format']['duration'])


def painted(im, items):
    # Text applied by the edit onto a blank surface of the artwork, such as a calendar on
    # a wall or a phone's screen, so it moves with the camera. "box" is left, top, right,
    # bottom as fractions of the whole illustration; the text is fitted into it, over an
    # optional rounded "fill", and the whole turns by "angle" degrees about the box centre.
    im = im.convert('RGBA')
    for item in items:
        l, t, r, b = item['box']
        box = (round(l*im.width), round(t*im.height), round(r*im.width), round(b*im.height))
        w, h = box[2] - box[0], box[3] - box[1]
        lines = item['text'].split('\n')
        pad = item.get('pad', 0)
        size = h
        while size > 6:
            f = graficos.font(size, item.get('weight', 'ExtraBold'))
            if max(f.getlength(ln) for ln in lines) <= (w - 2*pad)*.94 and size*1.15*len(lines) <= h - 2*pad:
                break
            size -= 1
        layer = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        if item.get('fill'):
            d.rounded_rectangle((0, 0, w-1, h-1), item.get('radius', 0), fill=tuple(item['fill']))
        for k, ln in enumerate(lines):
            y = h/2 + (k - (len(lines) - 1)/2)*size*1.15
            d.text((w/2, y), ln, font=f, fill=tuple(item.get('color', (40, 34, 30))) + (round(255*item.get('opacity', .9)),),
                   anchor='mm')
        if item.get('angle'):
            layer = layer.rotate(item['angle'], resample=Image.Resampling.BICUBIC, expand=True)
        if item.get('blur'):
            layer = layer.filter(ImageFilter.GaussianBlur(item['blur']))
        im.alpha_composite(layer, (round((box[0] + box[2] - layer.width)/2), round((box[1] + box[3] - layer.height)/2)))
    return im.convert('RGB')


def cover(path, size=(W, H), center=(.5, .5), crop=None, paint=None):
    im = Image.open(path).convert('RGB')
    if paint:
        im = painted(im, paint)
    if crop:
        # Optional framing inside the illustration: left, top, right, bottom as fractions.
        l, t, r, b = crop
        im = im.crop((round(l*im.width), round(t*im.height), round(r*im.width), round(b*im.height)))
    return ImageOps.fit(im, size, method=Image.Resampling.LANCZOS, centering=center)


def label(target, x, y, value, size, fill='white', weight='Bold', align='left', tracking=0):
    # y is the centre of the capital letters; sprites without shadow carry a 4 px pad.
    sprite, ay = text_sprite(value, size, weight, fill, tracking, shadow=False)
    place(target, sprite, x, y, {'left': 4, 'center': sprite.width/2, 'right': sprite.width-4}[align], ay)


def ticks(draw, x, y, fill, count):
    for k in range(count):
        draw.line((x + 7*k, y, x + 7*k + 5, y + 5, x + 7*k + 14, y - 6), fill=fill, width=3, joint='curve')


def wrap(draw, value, max_width, size):
    words, lines, current = value.split(), [], ''
    f = graficos.font(size, 'Bold')
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


def bag_photo():
    # The photo Zinho sends the friend shows only the open backpack full of old clothes.
    return cover(EPISODE / 'cena-03-roupas.png', (340, 310), crop=(0.20, 0.62, 0.95, 0.90))


def backdrop(path, brightness=1, blur=False, crop=None, paint=None):
    im = cover(path, crop=crop, paint=paint)
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(15))
    if brightness != 1:
        im = ImageEnhance.Brightness(im).enhance(brightness)
    return im.convert('RGBA')


def caption_gradient(im):
    # Keep the lower caption region readable without turning the entire scene dark.
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(920, H):
        a = int(95 * ((y-920)/(H-920)))
        d.line((0, y, W, y), fill=(3, 8, 12, a))
    return Image.alpha_composite(im, layer)


def phone(d, top, frame):
    # The phone of the message cards: body, notch and screen.
    d.rounded_rectangle((110, top, 610, top+680), 46, fill=(14, 17, 18, 255), outline=frame, width=3)
    d.rounded_rectangle((270, top+14, 450, top+36), 11, fill=(4, 6, 7))
    d.rounded_rectangle((130, top+50, 590, top+660), 22, fill=(20, 27, 30))


def handset(d, cx, cy, fill, k=1):
    # A round call button with a telephone receiver, drawn as a thick arc.
    d.ellipse((cx-38*k, cy-38*k, cx+38*k, cy+38*k), fill=fill)
    d.arc((cx-20*k, cy-12*k, cx+20*k, cy+26*k), 200, 340, fill=(246, 240, 226), width=9*k)


def make_card(kind, scene, portrait):
    # Dark panels, Poppins and the yellow/green/red accents of the reference video.
    card = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    top, frame = scene.get('card_top', CARD_TOP), (64, 70, 72)
    if kind == 'tv':
        d.rounded_rectangle((45, top, 675, top+660), 30, fill=(14, 17, 18, 255), outline=frame, width=4)
        d.rectangle((70, top+25, 650, top+595), fill=(18, 30, 36))
        rounded_image(card, portrait, (87, top+45, 633, top+452), radius=4)
        d = ImageDraw.Draw(card)
        d.rounded_rectangle((104, top+64, 214, top+98), 8, fill=rgb('alert'))
        label(card, 159, top+81, 'AO VIVO', 17, 'white', align='center', tracking=1)
        d.rectangle((70, top+452, 650, top+595), fill=(16, 22, 26))
        d.rectangle((70, top+452, 80, top+595), fill=rgb('yellow'))
        label(card, 104, top+497, 'ZINHO', 50, 'yellow', 'ExtraBold')
        label(card, 104, top+556, 'PRIMEIRO SUSPEITO IDENTIFICADO', 24)
        label(card, 360, top+628, 'NOTICIÁRIO LOCAL', 15, 'gray', 'Medium', 'center', 3)
    elif kind == 'chat':
        d.rounded_rectangle((110, top, 610, top+680), 46, fill=(14, 17, 18, 255), outline=frame, width=3)
        d.rounded_rectangle((270, top+14, 450, top+36), 11, fill=(4, 6, 7))
        d.rounded_rectangle((130, top+50, 590, top+660), 22, fill=(20, 27, 30))
        d.rounded_rectangle((130, top+50, 590, top+130), 22, fill=(31, 39, 43))
        d.rectangle((130, top+108, 590, top+130), fill=(31, 39, 43))
        d.ellipse((150, top+66, 198, top+114), fill=(70, 82, 88))
        label(card, 216, top+90, 'AMIGO', 24)
        rounded_image(card, bag_photo(), (232, top+160, 572, top+470), radius=16)
        d = ImageDraw.Draw(card)
        if scene.get('status', 'seen') == 'seen':
            blue = (83, 189, 235)
            label(card, 520, top+500, 'Visualizado', 20, blue, 'SemiBold', 'right')
            ticks(d, 530, top+500, blue, 2)
            label(card, 360, top+590, 'Nenhuma resposta.', 24, 'gray', 'Medium', 'center')
        else:
            label(card, 530, top+500, 'Enviada', 20, 'gray', 'SemiBold', 'right')
            ticks(d, 540, top+500, rgb('gray'), 1)
    elif kind == 'comparison':
        for y, name in [(top, 'A FOTO ENVIADA'), (top+352, 'A FOTO NO JORNAL')]:
            d.rounded_rectangle((92, y, 628, y+328), 20, fill=(16, 22, 20, 236), outline=(44, 58, 52), width=2)
            rounded_image(card, portrait, (110, y+62, 610, y+310), radius=12)
            d = ImageDraw.Draw(card)
            label(card, 360, y+34, name, 21, 'yellow', 'Bold', 'center', 2)
    elif kind == 'photo':
        # A photo open on someone's phone: "photo" is the illustration it shows.
        phone(d, top, frame)
        shot = cover(resolve_asset(scene['photo']), (460, 610), crop=scene.get('photo_crop'), paint=scene.get('paint'))
        rounded_image(card, shot, (130, top+50, 590, top+660), radius=22)
    elif kind == 'call':
        # A call placed from Zinho's phone: "status" is calling, answered or ended.
        phone(d, top, frame)
        status = scene.get('status', 'calling')
        d.ellipse((300, top+130, 420, top+250), fill=(70, 82, 88))
        d.ellipse((339, top+152, 381, top+194), fill=(120, 132, 136))
        d.pieslice((318, top+196, 402, top+280), 180, 360, fill=(120, 132, 136))
        label(card, 360, top+310, scene.get('number', ''), 38, 'white', 'Bold', 'center')
        note = {'calling': ('chamando…', 'gray'), 'answered': (scene.get('clock', '00:03'), 'green'),
                'ended': ('chamada encerrada', 'red')}[status]
        label(card, 360, top+366, note[0], 26, note[1], 'Medium', 'center')
        d = ImageDraw.Draw(card)
        if status != 'ended':
            handset(d, 360, top+560, rgb('red'))
    elif kind == 'notification':
        # A message notification, as it lights up a phone's screen: "sender" and "message".
        d.rounded_rectangle((52, top, 668, top+168), 30, fill=(28, 30, 31, 242), outline=frame, width=2)
        d.rounded_rectangle((80, top+30, 152, top+102), 18, fill=rgb('green'))
        d.rounded_rectangle((97, top+48, 135, top+78), 9, fill=(246, 240, 226))
        d.polygon([(104, top+74), (104, top+88), (118, top+76)], fill=(246, 240, 226))
        label(card, 176, top+50, scene.get('sender', ''), 28, 'white', 'Bold')
        label(card, 640, top+50, scene.get('when', 'agora'), 20, 'gray', 'Medium', 'right')
        label(card, 176, top+100, scene.get('message', ''), 32, 'white', 'Medium')
    elif kind == 'audio':
        d.rounded_rectangle((80, 795, 640, 958), 24, fill=(16, 15, 12, 236), outline=frame, width=2)
        label(card, 110, 830, 'ÁUDIO DO AMIGO', 20, 'yellow', tracking=1.5)
        for j in range(55):
            amp = int(9 + 26*abs(math.sin(j*.69)*math.cos(j*.33)))
            x = 112 + j*9
            d.rounded_rectangle((x, 903-amp, x+4, 903+amp), 2, fill=(196, 198, 190))
        d.rounded_rectangle((112, AUDIO_TRACK_Y, 598, AUDIO_TRACK_Y+5), 2, fill=(70, 74, 70))
    if scene.get('card_dx') or scene.get('card_scale'):
        # The vertical versions move the cards sideways, and shrink the widest about their
        # top centre, to keep them clear of the button column.
        k = float(scene.get('card_scale', 1))
        if k != 1:
            card = card.resize((round(W*k), round(H*k)), Image.Resampling.LANCZOS)
        moved = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        graficos.put(moved, card, W/2*(1 - k) + scene.get('card_dx', 0), top*(1 - k))
        card = moved
    return card


def resolve_asset(name):
    p = Path(name)
    if not p.is_absolute():
        p = ROOT / p
    if not p.exists():
        print(f'NOTE: {p.name} missing; using scene 01 as temporary fallback.', flush=True)
        p = EPISODE / 'cena-01-base.png'
    return p


def make_scene_assets(scene, index, work):
    # No series marker: TikTok and Reels cover the top of the frame, so the series
    # name and episode go in the post text instead.
    kind = scene.get('kind', 'art')
    # Card scenes blur and darken the artwork; "brightness" darkens any other scene. A
    # notification lights up over the artwork itself, and "black" is the opening's black card.
    behind = kind in ('tv', 'chat', 'comparison', 'photo', 'call')
    if kind == 'black':
        bg = Image.new('RGBA', (W, H), (11, 10, 9, 255))
    else:
        path = resolve_asset(scene.get('asset', 'cena-01-base.png'))
        bg = backdrop(path, .34 if behind else float(scene.get('brightness', 1)), behind, scene.get('crop'),
                      scene.get('paint'))
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
        graph += f"color=c=0xFDB822:s=10x6:r={fps}:d={duration}[progress];[composed][progress]overlay=x='112+476*min(max(t-{p0:.3f},0)/{travel:.3f},1)':y={AUDIO_TRACK_Y}:enable='gte(t,0.4)':shortest=1,format=yuv420p[v]"
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
    lines = wrap(d, value, 590, 36)
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
Style: Default,Poppins,36,&H00E2F0F6,&H000000FF,&H0010181B,&H8C000000,-1,0,0,0,100,100,0,0,1,3,1,2,58,72,{CAPTION_MARGIN},1
Style: Amigo,Poppins,36,&H0022B8FD,&H000000FF,&H0010181B,&H8C000000,-1,-1,0,0,100,100,0,0,1,3,1,2,58,72,{CAPTION_MARGIN},1

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


def sound_path(name):
    # The timeline's own efeitos/ first, then Part 1's shared ones.
    return next((d / name for d in SOUNDS if (d / name).exists()), SOUNDS[-1] / name)


def sound_mix(sfx, tail, first_input, cmd):
    """Audio filter chains ending in [a]: the normalized voice with each effect from the
    timeline's "sfx" list ("sound", "at" in seconds, "gain" in dB) placed under it.
    Appends one input per distinct sound to `cmd`."""
    voice = 'loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000' + (f',apad=pad_dur={tail}' if tail > 0 else '')
    # The mono mix goes out as stereo, the layout phones and social platforms expect, with
    # the full signal on both sides (a plain -ac 2 would lower each side by 3 dB).
    stereo = 'pan=stereo|c0=c0|c1=c0'
    if not sfx:
        return [f'[1:a]{voice},{stereo}[a]']
    chains, mixed = [f'[1:a]{voice}[voice]'], []
    for k, name in enumerate(sorted({e['sound'] for e in sfx})):
        cmd += ['-i', sound_path(name)]
        events = [e for e in sfx if e['sound'] == name]
        copies = [f'[s{k}_{j}]' for j in range(len(events))]
        chains.append(f'[{first_input + k}:a]aresample=48000,aformat=channel_layouts=mono,asplit={len(events)}' + ''.join(copies))
        for j, e in enumerate(events):
            chains.append(f"{copies[j]}adelay={round(float(e['at'])*1000)}:all=1,volume={float(e.get('gain', 0))}dB[m{k}_{j}]")
            mixed.append(f'[m{k}_{j}]')
    # normalize=0 keeps every level as written; the limiter only catches overlapping peaks.
    # Its 5 ms look-ahead delays the output, so that much is trimmed to keep the voice in sync.
    chains.append(f"[voice]{''.join(mixed)}amix=inputs={len(mixed)+1}:duration=first:normalize=0,"
                  f"alimiter=limit=0.89:level=0:attack=5,atrim=start=0.005,asetpts=PTS-STARTPTS,{stereo}[a]")
    return chains


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
    global W, H, ROOT, SOUNDS
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio', type=Path, help='Narration; defaults to the timeline\'s "audio", next to the episode')
    parser.add_argument('--timeline', type=Path)
    parser.add_argument('--output', type=Path, default=HERE / 'zinho-ep01-animatic.mp4')
    parser.add_argument('--fps', type=int, default=25)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    timeline = json.loads(args.timeline.read_text()) if args.timeline else None
    base = args.timeline.resolve().parent if args.timeline else HERE
    # A timeline may name more effect folders, relative to its own folder.
    extra = [base / d for d in (timeline or {}).get('effects', [])]
    ROOT, SOUNDS = base.parent, list(dict.fromkeys([base / 'efeitos', *extra, EFFECTS]))
    if args.audio is None:
        args.audio = ROOT / (timeline or {}).get('audio', 'narracao-original.wav')
    audio_duration = probe(args.audio)
    work = base / 'work'
    work.mkdir(parents=True, exist_ok=True)
    if timeline is None:
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
    graphics = timeline.get('graphics', [])
    graficos.check(graphics)
    sfx = timeline.get('sfx', [])
    missing = sorted({e['sound'] for e in sfx if not sound_path(e['sound']).exists()})
    if missing:
        raise FileNotFoundError(f'Sound effects missing from {[str(d) for d in SOUNDS]}: {missing}')
    # Each version of the episode keeps its own record: timeline-tiktok.json writes
    # timeline-tiktok-used.json and render-report-tiktok.json.
    variant = args.timeline.stem.removeprefix('timeline') if args.timeline else ''
    used = base / f'timeline{variant}-used.json'
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
    # All inputs share codec/rate. The final pass lays the graphics layer, streamed frame
    # by frame from graficos, over the scenes, burns captions if the timeline has any,
    # normalizes speech gently and mixes the sound effects under it.
    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-f', 'concat', '-safe', '0', '-i', playlist, '-i', args.audio]
    chain = []
    if graphics:
        cmd += ['-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(args.fps), '-i', '-']
        chain.append('overlay=0:0:format=auto')
    if timeline.get('captions'):
        chain.append(f'ass={ass.as_posix()}:fontsdir={FONTS.as_posix()}')
    chain.append('format=yuv420p')
    graph = [('[0:v][2:v]' if graphics else '[0:v]') + ','.join(chain) + '[v]']
    graph += sound_mix(sfx, tail, 3 if graphics else 2, cmd)
    cmd += ['-filter_complex', ';'.join(graph), '-map', '[v]', '-map', '[a]', '-t', str(duration),
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k',
            '-ar', '48000', '-movflags', '+faststart', '-threads', '2', args.output]
    if graphics:
        proc = subprocess.Popen([str(a) for a in cmd], stdin=subprocess.PIPE)
        try:
            for data in graficos.frames(graphics, duration, args.fps):
                proc.stdin.write(data)
        except BrokenPipeError:
            pass
        proc.stdin.close()
        if proc.wait():
            raise subprocess.CalledProcessError(proc.returncode, cmd)
    else:
        run(cmd)
    result = {'output': str(args.output), 'duration': probe(args.output), 'audio_duration': audio_duration, 'tail': tail,
              'scenes': len(scenes), 'captions': len(timeline.get('captions', [])), 'graphics': len(graphics),
              'sound_effects': len(sfx),
              'type': 'illustrated animatic with camera motion and graphics; no generated body animation'}
    (base / f'render-report{variant}.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
