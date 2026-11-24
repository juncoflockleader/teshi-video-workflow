"""把场景图／视频片段、字幕、标注和配音合成成片。在项目目录运行（或设 PROJ）；默认读 配音/时间轴.json、配音/完整.wav、音乐.mp3，输出名取 分镜.json 的 output。
环境变量 TIMELINE／AUDIO／MUSIC／OUT 可覆盖。片头片尾文字取 分镜.json 的 card。
用法：
  python3 ../工具/合成.py          # 完整成片 → 分镜.json 的 output
  python3 合成.py --previews      # 每镜中点一张静帧 → previews/
  python3 合成.py --range 150 175 # 只渲染一段（秒，含片头 3 秒偏移）→ 片段预览.mp4
"""
import sys, json, subprocess, math, zlib
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

import os
HERE = Path(os.environ.get('PROJ', os.getcwd())).resolve()   # 项目目录：分镜.json、图/、片段/、配音/
SB = json.load(open(HERE / '分镜.json'))
TL = json.load(open(Path(os.environ.get('TIMELINE', HERE / '配音' / '时间轴.json'))))
W, H = SB['size']; FPS = SB['fps']
LEAD = SB['lead_seconds']; TAIL = SB['tail_seconds']
DUR = TL['duration']; TOTAL = LEAD + DUR + TAIL
CLIPS = TL['clips']
FF = '/opt/homebrew/bin/ffmpeg'
AUDIO = Path(os.environ.get('AUDIO', HERE / '配音' / '完整.wav'))
MUSIC = Path(os.environ.get('MUSIC', HERE / '音乐.mp3'))
OUT = Path(os.environ.get('OUT', HERE / SB.get('output', '成片.mp4')))
CARD = SB.get('card', {})
FADE = tuple(CARD.get('fade_color', [0, 0, 0, 255]))   # 片头淡入、片尾淡出用的底色
XFADE = 0.35
KBS = SB.get('kb_scale', 1.2)   # 静帧预放大倍数：越大推拉余量越多、裁掉的边也越多
FONT_SUB = '/System/Library/Fonts/Hiragino Sans GB.ttc'   # index 2 = W6
FONT_TITLE = '/System/Library/Fonts/Supplemental/Songti.ttc'  # index 0 = Black

def font(path, size, index=0):
    return ImageFont.truetype(path, size, index=index)

# ---------- 镜头时间 ----------
def boundary(i):
    if i == 0: return 0.0
    return (CLIPS[i-1]['end'] + CLIPS[i]['start']) / 2
shots = []
for k, s in enumerate(SB['shots']):
    st = LEAD + boundary(s['from_clip'])
    en = LEAD + (boundary(SB['shots'][k+1]['from_clip']) if k+1 < len(SB['shots']) else DUR)
    shots.append(dict(s, start=st, end=en))
    # 标注可以写 clip（第几句开头出现）与 frac（该句内的比例），换算成相对镜头起点的 t0
    for lab in shots[-1].get('labels', []):
        if lab.get('clip') is not None:
            c = CLIPS[lab['clip']]; lab['t0'] = max(0.0, LEAD + c['start'] + lab.get('frac', 0) * (c['end'] - c['start']) - st)
TITLE = dict(id='片头', kind='title', start=0.0, end=LEAD + boundary(0) + 0.4)  # 片头压到第一镜开头
END = dict(id='片尾', kind='end', start=LEAD + DUR, end=TOTAL)

# ---------- 素材 ----------
_cache = {}
def still(id):
    if id not in _cache:
        im = Image.open(HERE / '图' / (id + '.jpg')).convert('RGB')
        # 放大到 1.2 倍画幅，供 Ken Burns 裁切
        _cache[id] = im.resize((int(W*KBS), int(H*KBS)), Image.LANCZOS)
    return _cache[id]

def ease(x):  # ease in-out
    return 0.5 - 0.5*math.cos(math.pi*min(max(x, 0), 1))

KB = {}  # 每镜 Ken Burns 参数，按 id 稳定随机
def kb_params(id):
    if id not in KB:
        rnd = np.random.RandomState(zlib.crc32(id.encode()) % (2**31))
        z0, z1 = (1.0, 1.09) if rnd.rand() < 0.6 else (1.09, 1.0)
        px0, py0 = rnd.uniform(0.3, 0.7), rnd.uniform(0.35, 0.65)
        px1, py1 = px0 + rnd.uniform(-0.08, 0.08), py0 + rnd.uniform(-0.05, 0.05)
        KB[id] = (z0, z1, px0, py0, px1, py1)
    return KB[id]

STATIC = {s['id'] for s in SB['shots'] if s.get('static')}   # 这些镜头不推拉、不裁边（叠字要和画面对齐时用）
def kb_frame(id, u):
    if id in STATIC: return np.asarray(still(id).resize((W, H), Image.BILINEAR))
    im = still(id); z0, z1, px0, py0, px1, py1 = kb_params(id); e = ease(u)
    z = z0 + (z1-z0)*e; px = px0 + (px1-px0)*e; py = py0 + (py1-py0)*e
    cw, ch = im.width / (KBS*z) * 1.0, im.height / (KBS*z) * 1.0
    cw, ch = cw, cw * H / W
    cx = min(max(px*im.width, cw/2), im.width - cw/2); cy = min(max(py*im.height, ch/2), im.height - ch/2)
    box = (cx-cw/2, cy-ch/2, cx+cw/2, cy+ch/2)
    return np.asarray(im.resize((W, H), Image.BILINEAR, box=box))

class VideoReader:
    """用 ffmpeg 解码片段为 rgb24 帧；拉伸或冻结到镜头时长。"""
    def __init__(self, path, need_sec, fit=False):
        pr = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(path)], capture_output=True, text=True)
        self.src_dur = float(pr.stdout.strip() or 8)
        factor = need_sec / self.src_dur
        vf = 'fps=%d,scale=%d:%d:flags=lanczos' % (FPS, W, H)
        if 1.0 < factor <= 1.6 or (fit and 0.35 <= factor < 1.0):   # fit：片段比镜头长时整体加速塞进去，而不是截断
            vf = 'setpts=%.4f*PTS,' % factor + vf
        vf += ',tpad=stop_mode=clone:stop_duration=%.2f' % (need_sec + 2)
        self.p = subprocess.Popen([FF, '-v', 'error', '-i', str(path), '-vf', vf, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
                                  stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**7)
        self.last = None
    def read(self):
        buf = self.p.stdout.read(W*H*3)
        if len(buf) < W*H*3:
            return self.last
        self.last = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        return self.last
    def close(self):
        try: self.p.stdout.close(); self.p.kill()
        except Exception: pass

# ---------- 文字层 ----------
def text_layer(text, size, color=(255,255,255,255), fpath=FONT_SUB, findex=2, box=True, pad=(28, 14), radius=16, box_alpha=120):
    f = font(fpath, size, findex)
    tmp = ImageDraw.Draw(Image.new('RGBA', (1, 1)))
    l, t, r, b = tmp.textbbox((0, 0), text, font=f)
    w, h = r - l + 2*pad[0], b - t + 2*pad[1]
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if box:
        d.rounded_rectangle((0, 0, w-1, h-1), radius=radius, fill=(12, 14, 40, box_alpha))
    d.text((pad[0]-l, pad[1]-t), text, font=f, fill=color)
    return im

_sub_cache = {}
def sub_layer(text):
    if text not in _sub_cache:
        _sub_cache[text] = text_layer(text, 46)
    return _sub_cache[text]

def paste(frame_rgba, layer, cx, cy, alpha=1.0):
    if alpha < 1.0:
        a = layer.split()[3].point(lambda v: int(v*alpha)); layer = layer.copy(); layer.putalpha(a)
    frame_rgba.alpha_composite(layer, (int(cx - layer.width/2), int(cy - layer.height/2)))

def subtitle_at(t):
    for c in CLIPS:
        if c['start'] + LEAD - 0.05 <= t <= c['end'] + LEAD + 0.15:
            return c['text']
    return None

def card_title():
    bg = CARD.get('background', '01')
    base = Image.fromarray(kb_frame(bg, 0.0)).convert('RGBA') if (HERE/'图'/(bg + '.jpg')).exists() else Image.new('RGBA', (W, H), (26, 28, 70, 255))
    dark = Image.new('RGBA', (W, H), tuple(CARD.get('overlay', [10, 12, 40, 150]))); base.alpha_composite(dark)
    paste(base, text_layer(CARD.get('title', ''), CARD.get('title_size', 190), tuple(CARD.get('title_color', [255, 243, 210, 255])), FONT_TITLE, 0, box=False), W/2, H*CARD.get('title_y', 0.40))
    if CARD.get('subtitle'): paste(base, text_layer(CARD['subtitle'], CARD.get('subtitle_size', 44), tuple(CARD.get('subtitle_color', [255, 255, 255, 235])), FONT_SUB, 2, box=False), W/2, H*CARD.get('subtitle_y', 0.60))
    if CARD.get('tag'): paste(base, text_layer(CARD['tag'], CARD.get('tag_size', 36), tuple(CARD.get('tag_color', [255, 120, 110, 235])), FONT_SUB, 2, box=False), W/2, H*CARD.get('tag_y', 0.68))
    return base

def card_end():
    base = Image.new('RGBA', (W, H), tuple(CARD.get('end_bg', [20, 22, 62, 255])))
    lines = CARD.get('credits', [])
    y = H*0.33
    for txt, sz, col in [(l[0], l[1], tuple(l[2])) for l in lines]:
        paste(base, text_layer(txt, sz, col, FONT_SUB, 2, box=False), W/2, y); y += sz*2.1
    return base


# ---------- 叠加层 ----------
def draw_minimap(img, ov, t_rel, t_abs):
    """战术板小地图：球沿平滑随机路径跑，各队小点追球。ov: x,y,w,h（画幅比例）, teams=[11,11,11], colors, seed"""
    x0, y0 = int(ov.get('x', 0.74) * W), int(ov.get('y', 0.06) * H)
    w, h = int(ov.get('w', 0.22) * W), int(ov.get('h', 0.16) * H)
    teams = ov.get('teams', [11, 11, 11]); cols = ov.get('colors', [[120, 200, 255], [255, 130, 110], [255, 255, 255]])
    seed = ov.get('seed', 7); tt = t_abs * ov.get('speed', 1.0)
    rnd = np.random.RandomState(seed); n = sum(teams)
    ph = rnd.uniform(0, 6.28, (n, 4)); fr = rnd.uniform(0.6, 1.6, (n, 4)); amp = rnd.uniform(0.04, 0.16, (n, 2)); lag = rnd.uniform(0.15, 0.6, n)
    layer = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(layer)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=14, fill=(12, 40, 30, 190), outline=(255, 255, 255, 90), width=2)
    m = 10; px0, py0, px1, py1 = m, m, w - m, h - m
    d.rectangle((px0, py0, px1, py1), outline=(255, 255, 255, 170), width=2)
    cx, cy = (px0 + px1) / 2, (py0 + py1) / 2; r = min(w, h) * 0.14
    d.line((cx, py0, cx, py1), fill=(255, 255, 255, 150), width=2); d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 255, 255, 150), width=2)
    gw, gh = (px1 - px0) * 0.08, (py1 - py0) * 0.42
    d.rectangle((px0, cy - gh / 2, px0 + gw, cy + gh / 2), outline=(255, 255, 255, 150), width=2); d.rectangle((px1 - gw, cy - gh / 2, px1, cy + gh / 2), outline=(255, 255, 255, 150), width=2)
    def ball_at(tau):
        bx = 0.5 + 0.40 * math.sin(0.9 * tau + 0.3) * math.cos(0.23 * tau); by = 0.5 + 0.36 * math.sin(1.7 * tau + 1.1) * math.sin(0.41 * tau + 0.5)
        return bx, by
    bx, by = ball_at(tt); k = 0
    for ti, cnt in enumerate(teams):
        col = tuple(cols[ti % len(cols)])
        for j in range(cnt):
            lx, ly = ball_at(tt - lag[k])
            ox = amp[k, 0] * math.sin(fr[k, 0] * tt + ph[k, 0]) + 0.5 * amp[k, 1] * math.sin(fr[k, 1] * tt + ph[k, 1])
            oy = amp[k, 1] * math.sin(fr[k, 2] * tt + ph[k, 2]) + 0.5 * amp[k, 0] * math.sin(fr[k, 3] * tt + ph[k, 3])
            # 每队留一个守门员站门前
            if j == 0: lx, ly, ox, oy = (0.07 if ti % 2 == 0 else 0.93), 0.5, 0, 0.12 * math.sin(fr[k, 0] * tt + ph[k, 0])
            qx = px0 + (px1 - px0) * min(max(lx + ox, 0.02), 0.98); qy = py0 + (py1 - py0) * min(max(ly + oy, 0.03), 0.97)
            d.ellipse((qx - 5, qy - 5, qx + 5, qy + 5), fill=col + (235,)); k += 1
    qx, qy = px0 + (px1 - px0) * bx, py0 + (py1 - py0) * by
    d.ellipse((qx - 4, qy - 4, qx + 4, qy + 4), fill=(255, 255, 255, 255), outline=(20, 20, 20, 255), width=1)
    a = min(1.0, t_rel / 0.4)
    if a < 1.0: layer.putalpha(layer.split()[3].point(lambda v: int(v * a)))
    img.alpha_composite(layer, (x0, y0))

OVERLAYS = {'minimap': draw_minimap}

# ---------- 主循环 ----------
def frame_at(t, state):
    """返回 t 秒的 RGBA 帧。state 保存视频读取器与上一镜末帧。"""
    if t < END['start']:
        k = max(i for i, s in enumerate(shots) if s['start'] <= t) if t >= shots[0]['start'] else -1
        cur = shots[k] if k >= 0 else None
    else:
        cur = None
    if cur is None and t < END['start']:  # 第一镜之前：片头
        tc = state.setdefault('title_card', card_title())
        return Image.blend(Image.new('RGBA', (W, H), FADE), tc, ease(t/0.6)) if t < 0.6 else tc.copy()
    if cur is None:
        img = state.setdefault('end_card', card_end()).copy()
        u = (t - END['start']) / TAIL
        if u > 0.75:  # 淡出到黑
            img = Image.blend(img, Image.new('RGBA', (W, H), FADE), ease((u-0.75)/0.25))
        return img
    sid = cur['id']
    if state.get('cur') != sid:  # 镜头切换
        if state.get('reader'): state['reader'].close(); state['reader'] = None
        state['prev_frame'] = state.get('last_rgb')
        state['cur'] = sid; state['cur_start'] = cur['start']
        clip = HERE / '片段' / (sid + '.mp4')
        if cur['kind'] in ('veo', 'hailuo') and clip.exists():
            state['reader'] = VideoReader(clip, cur['end'] - cur['start'], fit=cur.get('fit', False))
    u = (t - cur['start']) / max(cur['end'] - cur['start'], 0.01)
    rgb = state['reader'].read() if state.get('reader') else kb_frame(sid, u)
    if rgb is None: rgb = kb_frame(sid, u)
    state['last_rgb'] = rgb
    img = Image.fromarray(rgb).convert('RGBA')
    # 叠化
    dt = t - cur['start']
    if dt < XFADE and state.get('prev_frame') is not None:
        img = Image.blend(Image.fromarray(state['prev_frame']).convert('RGBA'), img, ease(dt / XFADE))
    # 片头压在第一镜上
    if t < TITLE['end']:
        tc = state.setdefault('title_card', card_title())
        if t < 0.6: tc2 = Image.blend(Image.new('RGBA', (W, H), FADE), tc, ease(t/0.6)); img = tc2
        elif t < TITLE['end'] - 0.6: img = tc
        else: img = Image.blend(tc, img, ease((t - (TITLE['end'] - 0.6)) / 0.6))
    # 标注
    for lab in cur.get('labels', []):
        if lab.get('t0', 0) <= dt <= lab.get('t1', 1e9):
            a = min(1.0, (dt - lab.get('t0', 0)) / 0.3)
            song = lab.get('font') == 'song'
            paste(img, text_layer(lab['text'], lab.get('size', 64), tuple(lab.get('color', [255, 230, 120, 255])), FONT_TITLE if song else FONT_SUB, 0 if song else 2, box=lab.get('box', False)), lab['x']*W, lab['y']*H, a)
    # 叠加层（小地图等），时间以该叠加层首次出现的镜头起点计
    for ov in cur.get('overlays', []):
        if ov.get('t0', 0) <= dt <= ov.get('t1', 1e9):
            OVERLAYS[ov['type']](img, ov, dt - ov.get('t0', 0), t - ov.get('since', cur['start']))
    # 字幕
    txt = subtitle_at(t)
    if txt and t >= TITLE['end'] - 0.6:
        paste(img, sub_layer(txt), W/2, H - 86)
    return img

def render(t0, t1, out, with_audio=True):
    n = int(round((t1 - t0) * FPS))
    cmd = [FF, '-y', '-v', 'warning', '-f', 'rawvideo', '-pixel_format', 'rgb24', '-video_size', '%dx%d' % (W, H),
           '-framerate', str(FPS), '-i', '-']
    if with_audio:
        cmd += ['-i', str(AUDIO)]
        trim = 'atrim=start=%.3f:end=%.3f,asetpts=PTS-STARTPTS' % (t0, t1)
        voice = '[1:a]adelay=%d|%d,apad,%s[v]' % (LEAD*1000, LEAD*1000, trim)
        if MUSIC.exists():
            cmd += ['-i', str(MUSIC)]
            fc = voice + ';[2:a]volume=0.13,afade=t=in:d=2,afade=t=out:st=%.1f:d=4,apad,%s[m];[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.97:level=false[a]' % (TOTAL-4, trim)
        else:
            fc = voice.replace('[v]', '[a]')
        cmd += ['-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-c:a', 'aac', '-b:a', '192k', '-shortest']
    cmd += ['-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(out)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    state = {}
    for f in range(n):
        t = t0 + f / FPS
        img = frame_at(t, state)
        p.stdin.write(img.convert('RGB').tobytes())
        if f % (FPS*10) == 0: print('  %.1fs / %.1fs' % (t, t1), flush=True)
    if state.get('reader'): state['reader'].close()
    p.stdin.close(); p.wait()
    print('WROTE', out)

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--previews']:
        pv = HERE / 'previews'; pv.mkdir(exist_ok=True)
        for s in [TITLE] + shots + [END]:
            state = {}
            t = (s['start'] + s['end']) / 2 if s['id'] != '片头' else 1.5
            img = frame_at(t, state)
            if state.get('reader'): state['reader'].close()
            img.convert('RGB').resize((960, 540), Image.LANCZOS).save(pv / ('%s.jpg' % s['id']), quality=88)
        print('previews written', len(shots)+2)
    elif a[:1] == ['--range']:
        render(float(a[1]), float(a[2]), HERE / '片段预览.mp4')
    elif a[:1] == ['--混音']:   # --混音 音乐文件 输出文件：用现成成片的视频流 + 旁白 + 指定音乐重混，不重渲染
        music, dest = Path(a[1]), Path(a[2])
        trim = 'atrim=start=0:end=%.3f,asetpts=PTS-STARTPTS' % TOTAL
        fc = ('[1:a]adelay=%d|%d,apad,%s[v];[2:a]volume=%s,afade=t=in:d=2,afade=t=out:st=%.1f:d=4,apad,%s[m];'
              '[v][m]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.97:level=false[a]') % (LEAD*1000, LEAD*1000, trim, os.environ.get('MUSIC_GAIN', '0.13'), TOTAL-4, trim)
        subprocess.run([FF, '-y', '-v', 'error', '-i', str(OUT), '-i', str(AUDIO), '-i', str(music), '-filter_complex', fc, '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', str(dest)], check=True)
        print('MIXED', dest)
    elif a[:1] == ['--shots']:
        for s in shots: print('%-4s %-6s %7.2f %7.2f  %5.2fs' % (s['id'], s['kind'], s['start'], s['end'], s['end']-s['start']))
        print('TOTAL', TOTAL)
    else:
        render(0.0, TOTAL, OUT)
