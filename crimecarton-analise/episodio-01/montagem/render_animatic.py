#!/usr/bin/env python3
"""Render a narrated, illustrated animatic. No character motion is synthesized.

Needs Pillow, FFmpeg (libass), FFprobe and the Poppins fonts in crimecarton-analise/fontes.
All generated working files stay in montagem/.
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


def run(args, **kwargs):
    return subprocess.run([str(a) for a in args], check=True, **kwargs)


def probe(path):
    r = run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', path], capture_output=True, text=True)
    return float(json.loads(r.stdout)['format']['duration'])


def cover(path, size=(W, H), center=(.5, .5), crop=None):
    im = Image.open(path).convert('RGB')
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


def backdrop(path, brightness=1, blur=False, crop=None):
    im = cover(path, crop=crop)
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


def make_card(kind, scene, portrait):
    # Dark panels, Poppins and the yellow/green/red accents of the reference video.
    card = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    top, frame = CARD_TOP, (64, 70, 72)
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
        rounded_image(card, Image.open(resolve_asset('cena-03-roupas.png')), (232, top+160, 572, top+470), radius=16)
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
    elif kind == 'audio':
        d.rounded_rectangle((80, 795, 640, 958), 24, fill=(16, 15, 12, 236), outline=frame, width=2)
        label(card, 110, 830, 'ÁUDIO DO AMIGO', 20, 'yellow', tracking=1.5)
        for j in range(55):
            amp = int(9 + 26*abs(math.sin(j*.69)*math.cos(j*.33)))
            x = 112 + j*9
            d.rounded_rectangle((x, 903-amp, x+4, 903+amp), 2, fill=(196, 198, 190))
        d.rounded_rectangle((112, AUDIO_TRACK_Y, 598, AUDIO_TRACK_Y+5), 2, fill=(70, 74, 70))
    return card


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
    # Card scenes blur and darken the artwork; "brightness" darkens any other scene.
    behind = kind in ('tv', 'chat', 'comparison')
    bg = backdrop(path, .34 if behind else float(scene.get('brightness', 1)), behind, scene.get('crop'))
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


def sound_mix(sfx, tail, first_input, cmd):
    """Audio filter chains ending in [a]: the normalized voice with each effect from the
    timeline's "sfx" list ("sound", "at" in seconds, "gain" in dB) placed under it.
    Appends one input per distinct sound to `cmd`."""
    voice = 'loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000' + (f',apad=pad_dur={tail}' if tail > 0 else '')
    if not sfx:
        return [f'[1:a]{voice}[a]']
    chains, mixed = [f'[1:a]{voice}[voice]'], []
    for k, name in enumerate(sorted({e['sound'] for e in sfx})):
        cmd += ['-i', EFFECTS / name]
        events = [e for e in sfx if e['sound'] == name]
        copies = [f'[s{k}_{j}]' for j in range(len(events))]
        chains.append(f'[{first_input + k}:a]aresample=48000,aformat=channel_layouts=mono,asplit={len(events)}' + ''.join(copies))
        for j, e in enumerate(events):
            chains.append(f"{copies[j]}adelay={round(float(e['at'])*1000)}:all=1,volume={float(e.get('gain', 0))}dB[m{k}_{j}]")
            mixed.append(f'[m{k}_{j}]')
    # normalize=0 keeps every level as written; the limiter only catches overlapping peaks.
    # Its 5 ms look-ahead delays the output, so that much is trimmed to keep the voice in sync.
    chains.append(f"[voice]{''.join(mixed)}amix=inputs={len(mixed)+1}:duration=first:normalize=0,"
                  "alimiter=limit=0.89:level=0:attack=5,atrim=start=0.005,asetpts=PTS-STARTPTS[a]")
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
    graphics = timeline.get('graphics', [])
    graficos.check(graphics)
    sfx = timeline.get('sfx', [])
    missing = sorted({e['sound'] for e in sfx if not (EFFECTS / e['sound']).exists()})
    if missing:
        raise FileNotFoundError(f'Sound effects missing from {EFFECTS}: {missing}')
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
    (HERE / 'render-report.json').write_text(json.dumps(result, indent=2))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
