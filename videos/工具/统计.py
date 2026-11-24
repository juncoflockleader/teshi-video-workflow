"""统计本目录 记录/ 里各模型的调用次数（成功／失败），供制作说明与对账。"""
import json, glob, collections
from pathlib import Path
c = collections.Counter(); secs = collections.Counter()
for p in sorted(glob.glob('记录/*.json') + glob.glob('配音/记录/*.json') + glob.glob('配音/试验/*.json')):
    d = json.load(open(p))
    if 'model' not in d: continue
    key = (d['model'], d['status'])
    c[key] += 1
    if d['status'] == 'succeeded' and 'duration' in (d.get('input') or {}):
        secs[d['model']] += int(d['input']['duration'])
for (m, st), n in sorted(c.items()): print('%-28s %-10s %3d' % (m, st, n), ('%d s' % secs[m]) if st == 'succeeded' and secs[m] else '')
