"""审图拼图：把 <项目>/图/ 里的镜头图按 3×2 拼成 1920 宽的对照图，写到 记录/contact/。
  python3 ../工具/拼图.py            全部镜头（按分镜顺序，已出的）
  python3 ../工具/拼图.py 03 12b     指定镜头
  python3 ../工具/拼图.py --片段     每段视频取中段与末帧
"""
import sys, os, json, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
PROJ = Path(os.environ.get('PROJ', os.getcwd())).resolve(); OUT = PROJ / '记录' / 'contact'; OUT.mkdir(parents=True, exist_ok=True)
F = ImageFont.truetype('/System/Library/Fonts/Hiragino Sans GB.ttc', 26, index=2)
def sheet(items, name, cols=3):
    rows = (len(items) + cols - 1) // cols; sh = Image.new('RGB', (640 * cols, 400 * rows), (0, 0, 0))
    for k, (label, im) in enumerate(items):
        x, y = (k % cols) * 640, (k // cols) * 400
        sh.paste(im.convert('RGB').resize((640, 360), Image.LANCZOS), (x, y + 40)); ImageDraw.Draw(sh).text((x + 8, y + 6), label, font=F, fill=(255, 255, 0))
    p = OUT / (name + '.jpg'); sh.save(p, quality=85); print('wrote', p.relative_to(PROJ), [l for l, _ in items])
a = sys.argv[1:]
if a[:1] == ['--片段']:
    items = []
    for clip in sorted((PROJ / '片段').glob('*.mp4')):
        dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(clip)], capture_output=True, text=True).stdout)
        for t in (dur * .45, dur - .3):
            subprocess.run(['/opt/homebrew/bin/ffmpeg', '-y', '-v', 'error', '-ss', '%.2f' % t, '-i', str(clip), '-frames:v', '1', str(OUT / '_f.jpg')], check=True)
            items.append(('%s @%.1fs' % (clip.stem, t), Image.open(OUT / '_f.jpg').copy()))
    for n in range(0, len(items), 6): sheet(items[n:n + 6], 'clips-%02d' % (n // 6))
    sys.exit()
ids = a or [s['id'] for s in json.load(open(PROJ / '分镜.json'))['shots'] if (PROJ / '图' / (s['id'] + '.jpg')).exists()]
items = [(i, Image.open(PROJ / '图' / (i + '.jpg'))) for i in ids]
for n in range(0, len(items), 6): sheet(items[n:n + 6], 'sheet-%02d' % (n // 6) if not a else 'pick-' + '-'.join(ids[:6]))
