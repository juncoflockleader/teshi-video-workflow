"""逐句旁白：按 <项目>/配音/配音.json 的句子逐句调用 MiniMax（Replicate），数字转读法、多音字按读音表提示，
掐静音、匹配响度、按标点留间隔拼成完整旁白，产出 时间轴.json、字幕.srt、完整.wav/mp3、试听.html。
在项目目录下运行（或设 PROJ 环境变量）：
  python3 ../工具/配音.py --dry        只打印送入文本
  python3 ../工具/配音.py              合成缺的句子并拼接
  python3 ../工具/配音.py 12 45        强制重做第 12、45 句并拼接
  python3 ../工具/配音.py --组 名      按配音.json 里 groups 定义带上下文整段合成并切句（可加 --只切）
  python3 ../工具/配音.py --拼         只重新拼接
"""
import sys, os, json, subprocess, re, html, time, shutil, wave
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import rep
PROJ = Path(os.environ.get('PROJ', os.getcwd())).resolve()
OUT = PROJ / '配音'; CFG = json.load(open(OUT / '配音.json'))
(OUT / '句').mkdir(exist_ok=True); (OUT / '记录').mkdir(exist_ok=True)
FF = '/opt/homebrew/bin/ffmpeg'; SR = 48000
MODEL = CFG.get('model', 'minimax/speech-2.8-hd'); VOICE = CFG['voice']; GAPS = CFG.get('gaps', {})
CLIPS = [dict(scene=si, text=t) for si, s in enumerate(CFG['scenes']) for t in s['clips']]

def tts_text(t):
    for a, b in CFG.get('numbers', []): t = t.replace(a, b)
    return t
def hinted(t):
    for a, b, *_ in CFG.get('hints', []): t = t.replace(a, b)
    return t
texts = [tts_text(c['text']) for c in CLIPS]; inputs = [hinted(t) for t in texts]
missing_hints = [h[0] for h in CFG.get('hints', []) if not any(h[0] in t for t in texts)]
assert not missing_hints, '读音表有未命中的条目: %s' % missing_hints

def call(payload, model, record):
    for attempt in range(5):
        try:
            d = rep.predict(model, payload, log=False)
            rec = dict(d); rec['input'] = payload; rec['model_used'] = model; rep.save_record(rec, record)
            if d['status'] != 'succeeded': raise RuntimeError(str(d.get('error'))[:200])
            return d['output'] if isinstance(d['output'], str) else d['output'][0]
        except Exception as e:
            print('RETRY', record.name, str(e)[:160], flush=True); time.sleep(10 * (attempt + 1))
    raise SystemExit('FAIL ' + record.name)

def synth(i, force=False):
    out = OUT / '句' / ('%02d.mp3' % i)
    if out.exists() and not force: return
    if out.exists(): backup(i)
    url = call(dict(VOICE, text=inputs[i]), MODEL, OUT / '记录' / ('%02d.json' % i))
    rep.download(url, out); print('OK %02d %s' % (i, inputs[i][:24]), flush=True)

def backup(i):
    bak = OUT / '记录' / '替换前'; bak.mkdir(exist_ok=True)
    src = OUT / '句' / ('%02d.mp3' % i); n = 1
    while (bak / ('%02d-%d.mp3' % (i, n))).exists(): n += 1
    shutil.copy(src, bak / ('%02d-%d.mp3' % (i, n)))

def pcm(path):
    return np.frombuffer(subprocess.check_output([FF, '-v', 'error', '-i', str(path), '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-']), np.float32).astype(np.float64)
def save(x, path):
    subprocess.run([FF, '-y', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-c:a', 'libmp3lame', '-b:a', '256k', str(path)], input=x.astype(np.float32).tobytes(), check=True)
def trim(x, thr_db=-45, pad=.06):
    idx = np.where(np.abs(x) > 10 ** (thr_db / 20))[0]
    if len(idx) == 0: return x
    return x[max(0, idx[0] - int(pad * SR)):min(len(x), idx[-1] + int(pad * SR))]
def gaps(x, thr_db=-40, min_ms=60):
    hop = SR // 100; n = len(x) // hop
    e = np.array([np.sqrt(np.mean(x[i*hop:(i+1)*hop] ** 2)) for i in range(n)]); low = e < 10 ** (thr_db / 20)
    out = []; i = 0
    while i < n:
        if low[i]:
            j = i
            while j < n and low[j]: j += 1
            if (j - i) * 10 >= min_ms: out.append((i * hop / SR, j * hop / SR))
            i = j
        else: i += 1
    return [(a, b) for a, b in out if a > .05 and b < len(x) / SR - .05]

def group(name, only_cut=False):
    """带上下文整段合成：groups[name] = {lines:[...], text:'...', mode:'split'|'middle', model?}"""
    g = CFG['groups'][name]; rec = OUT / '记录' / ('组-%s.mp3' % name)
    if not only_cut or not rec.exists():
        url = call(dict(VOICE, text=g['text']), g.get('model', MODEL), OUT / '记录' / ('组-%s.json' % name)); rep.download(url, rec)
    x = pcm(rec); total = len(x) / SR; gs = gaps(x)
    print('%s: %.2fs gaps %s' % (name, total, ', '.join('%.2f-%.2f' % t for t in gs)))
    if g.get('mode', 'split') == 'middle':
        big = sorted(sorted(gs, key=lambda t: t[1] - t[0], reverse=True)[:2]); mid = [(a + b) / 2 for a, b in big]
        pieces = [x[int(mid[0] * SR):int(mid[1] * SR)]]
    else:
        chars = np.array([len(re.sub(r'[，。？！：]', '', texts[i])) for i in g['lines']], float)
        cum = np.cumsum(chars)[:-1] / chars.sum() * total; cuts = []
        for est in cum:
            cand = [((a + b) / 2, abs((a + b) / 2 - est)) for a, b in gs if abs((a + b) / 2 - est) < 1.2]
            if not cand: raise SystemExit('no gap near %.2f' % est)
            cuts.append(min(cand, key=lambda c: c[1])[0])
        edges = [0.0] + cuts + [total]; pieces = [x[int(edges[k] * SR):int(edges[k + 1] * SR)] for k in range(len(g['lines']))]
        print('  cuts', ', '.join('%.2f' % c for c in cuts), '(est', ', '.join('%.2f' % c for c in cum) + ')')
    for i, p in zip(g['lines'], pieces):
        if (OUT / '句' / ('%02d.mp3' % i)).exists(): backup(i)
        save(p, OUT / '句' / ('%02d.mp3' % i)); print('  -> 句/%02d.mp3 %.2fs  %s' % (i, len(p) / SR, CLIPS[i]['text']))

def active_rms(x):
    act = x[np.abs(x) > .012]; return float(np.sqrt(np.mean(act ** 2))) if len(act) else 1e-6
def gap_after(i):
    t = CLIPS[i]['text']
    if i + 1 < len(CLIPS) and CLIPS[i + 1]['scene'] != CLIPS[i]['scene']: return GAPS.get('scene', .85)
    return GAPS.get('comma', .22) if t.endswith('，') else GAPS.get('period', .45)

def stitch():
    pieces = [trim(pcm(OUT / '句' / ('%02d.mp3' % i))) for i in range(len(CLIPS))]
    rms = np.array([active_rms(p) for p in pieces]); gains = np.clip(np.median(rms) / rms, 10 ** (-4 / 20), 10 ** (4 / 20))
    pieces = [p * g for p, g in zip(pieces, gains)]; peak = max(np.max(np.abs(p)) for p in pieces)
    if peak > .95: pieces = [p * (.95 / peak) for p in pieces]
    lead = CFG.get('lead', .7); t = lead; out = [np.zeros(int(lead * SR))]; clips = []
    for i, p in enumerate(pieces):
        clips.append(dict(scene=CLIPS[i]['scene'], text=CLIPS[i]['text'], start=round(t, 3), end=round(t + len(p) / SR, 3), index=i, tts_text=inputs[i], gain_db=round(20 * np.log10(gains[i]), 2)))
        out.append(p); t += len(p) / SR; g = gap_after(i) if i + 1 < len(pieces) else GAPS.get('tail', 1.2); out.append(np.zeros(int(g * SR))); t += g
    audio = np.concatenate(out); dur = len(audio) / SR
    with wave.open(str(OUT / '完整.wav'), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(np.rint(np.clip(audio, -1, 1 - 1 / 32768) * 32768).astype(np.int16).tobytes())
    subprocess.run([FF, '-y', '-v', 'error', '-i', str(OUT / '完整.wav'), '-c:a', 'libmp3lame', '-b:a', '192k', str(OUT / '完整.mp3')], check=True)
    scenes = []
    for si, s in enumerate(CFG['scenes']):
        cs = [c for c in clips if c['scene'] == si]
        scenes.append(dict(index=si, kind=s['kind'], title=s['title'], text=''.join(s['clips']), start=cs[0]['start'], end=cs[-1]['end']))
    for k in range(len(scenes)):
        scenes[k]['end'] = round((scenes[k]['end'] + scenes[k + 1]['start']) / 2, 3) if k + 1 < len(scenes) else dur
        scenes[k]['start'] = 0.0 if k == 0 else scenes[k - 1]['end']
    json.dump(dict(duration=dur, scenes=scenes, clips=clips, voice=VOICE, model=MODEL, hints=CFG.get('hints'), flags=CFG.get('flags')), open(OUT / '时间轴.json', 'w'), ensure_ascii=False, indent=1)
    ts = lambda x: '%02d:%02d:%06.3f' % (int(x // 3600), int(x % 3600 // 60), x % 60)
    (OUT / '字幕.srt').write_text(''.join('%d\n%s --> %s\n%s\n\n' % (c['index'] + 1, ts(c['start']).replace('.', ','), ts(c['end']).replace('.', ','), c['text']) for c in clips))
    rows = ''.join('<tr><td>%02d</td><td>%d</td><td>%s</td><td class=t>%s</td><td>%.2f</td><td><audio controls preload=none src="句/%02d.mp3"></audio></td></tr>' % (c['index'], c['scene'], html.escape(c['text']), html.escape(c['tts_text']) if c['tts_text'] != tts_text(c['text']) else '', c['end'] - c['start'], c['index']) for c in clips)
    (OUT / '试听.html').write_text('''<!doctype html><meta charset=utf-8><title>%s 逐句旁白 试听</title>
<style>body{font:15px/1.5 -apple-system,"PingFang SC",sans-serif;margin:24px;max-width:1100px}table{border-collapse:collapse;width:100%%}td,th{border-bottom:1px solid #ddd;padding:6px 8px;vertical-align:top;text-align:left}td.t{color:#b00;font-family:monospace}audio{width:230px;height:32px}h1{font-size:20px}p.f{color:#555}</style>
<h1>%s · 逐句旁白（%s · %s）</h1><p>完整拼接：<audio controls src="完整.mp3"></audio> 共 %.1f 秒</p>
<p class=f>红色一列是加了拼音提示的送入文本。未加提示但请留意：%s</p>
<table><tr><th>#</th><th>景</th><th>原文</th><th>送入文本（有提示时）</th><th>秒</th><th>播放</th></tr>%s</table>''' % (CFG['title'], CFG['title'], MODEL, VOICE['voice_id'], dur, '；'.join(CFG.get('flags', [])), rows))
    print('stitched %.2fs, %d clips; gain range %.1f..%.1f dB' % (dur, len(clips), 20 * np.log10(gains.min()), 20 * np.log10(gains.max())))

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--dry']:
        for i, t in enumerate(inputs): print('%02d s%-2d %s' % (i, CLIPS[i]['scene'], t))
        print(len(inputs), 'clips;', sum(len(t) for t in texts), 'chars'); sys.exit()
    if a[:1] == ['--拼']: stitch(); sys.exit()
    if a[:1] == ['--组']:
        only = '--只切' in a; names = [x for x in a[1:] if x != '--只切']
        for n in names: group(n, only)
        stitch(); sys.exit()
    force = [int(x) for x in a]
    with ThreadPoolExecutor(3) as ex: list(ex.map(lambda i: synth(i, force=i in force), range(len(CLIPS))))
    miss = [i for i in range(len(CLIPS)) if not (OUT / '句' / ('%02d.mp3' % i)).exists()]
    if miss: print('MISSING', miss); sys.exit(1)
    stitch()
