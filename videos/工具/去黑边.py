"""检查 <项目>/图/ 里的镜头图有没有模型自带的边框；有就裁掉再铺满原尺寸。原图存到 记录/黑边-<名>.jpg。
  python3 ../工具/去黑边.py            检查全部镜头图，只裁纯黑边（最暗的深色画风背景也不会被当成黑边）
  python3 ../工具/去黑边.py 03 12      只处理指定镜头
  python3 ../工具/去黑边.py --浅边     另外也裁米白/白色的边框（只用于深色底画风；白纸画风不要加）
判定：一整行（列）里 97% 以上的像素都接近纯黑（或开了 --浅边 时接近白），才算边。
"""
import os, sys, json
from pathlib import Path
import numpy as np
from PIL import Image
PROJ = Path(os.environ.get('PROJ', os.getcwd())).resolve()
args = sys.argv[1:]; LIGHT = '--浅边' in args; args = [a for a in args if a != '--浅边']
ids = args or [s['id'] for s in json.load(open(PROJ / '分镜.json'))['shots']]
for i in ids:
    p = PROJ / '图' / (i + '.jpg')
    if not p.exists(): continue
    im = Image.open(p).convert('RGB'); a = np.asarray(im).astype(int); H, W = a.shape[:2]
    dark = a.max(2) < 22; light = a.min(2) > 195
    def edge(mask, axis):
        frac = mask.mean(axis); n = 0
        while n < len(frac) // 3 and frac[n] > .97: n += 1
        return n
    def edges(mask): return [edge(mask, 1), edge(mask[::-1], 1), edge(mask, 0), edge(mask[:, ::-1], 0)]
    t, b, l, r = edges(dark)
    if LIGHT and max(t, b, l, r) < 4:
        t, b, l, r = edges(light)
        t, b, l, r = [(v + 10 if v else 0) for v in (t, b, l, r)]     # 浅色画框常带圆角，多裁一点
    if max(t, b, l, r) < 4: continue
    im.save(PROJ / '记录' / ('黑边-%s.jpg' % i), quality=95)
    c = im.crop((l + 2 if l else 0, t + 2 if t else 0, W - (r + 2 if r else 0), H - (b + 2 if b else 0)))
    s = max(W / c.width, H / c.height); c = c.resize((round(c.width * s), round(c.height * s)), Image.LANCZOS)
    x, y = (c.width - W) // 2, (c.height - H) // 2
    c.crop((x, y, x + W, y + H)).save(p, quality=95); print('去边', i, dict(top=t, bottom=b, left=l, right=r))
print('checked', len(ids))
