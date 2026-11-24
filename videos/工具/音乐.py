"""背景音乐：按 <项目>/音乐.json 的候选提示词用 minimax/music-1.5 生成纯器乐段，循环（交叉淡化）到全片长度。
  python3 ../工具/音乐.py            生成所有候选（已有的跳过）并循环 → 音乐-候选-<名>.mp3
  python3 ../工具/音乐.py --用 名    把该候选复制为 音乐.mp3
  python3 ../工具/音乐.py --接 前 后 N  前段候选用到第 N 句开头淡出，第 N 句留空，后段候选从第 N+1 句淡入到片尾 → 音乐.mp3
"""
import sys, os, json, math, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent)); import rep
PROJ = Path(os.environ.get('PROJ', os.getcwd())).resolve(); FF = '/opt/homebrew/bin/ffmpeg'
CFG = json.load(open(PROJ / '音乐.json')); SB = json.load(open(PROJ / '分镜.json')); TL = json.load(open(PROJ / '配音' / '时间轴.json'))
NEED = SB.get('lead_seconds', 3) + TL['duration'] + SB.get('tail_seconds', 4) + 2
LYR = '[intro]\n[instrumental]\n[verse]\n[instrumental]\n[bridge]\n[instrumental]\n[outro]\n[instrumental]'

def dur(p): return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)], capture_output=True, text=True).stdout)
def loop(src, dst, xf=2.0):
    d = dur(src); n = max(1, math.ceil((NEED + xf) / (d - xf)))
    if n == 1: subprocess.run([FF, '-y', '-v', 'error', '-i', str(src), '-t', str(NEED), '-c:a', 'libmp3lame', '-q:a', '2', str(dst)], check=True); return d, 1
    inputs = []; chain = ''; prev = '[0:a]'
    for i in range(n): inputs += ['-i', str(src)]
    for i in range(1, n):
        out = '[a%d]' % i if i < n - 1 else '[out]'; chain += '%s[%d:a]acrossfade=d=%.1f:c1=tri:c2=tri%s;' % (prev, i, xf, out); prev = out
    subprocess.run([FF, '-y', '-v', 'error'] + inputs + ['-filter_complex', chain.rstrip(';'), '-map', '[out]', '-t', str(NEED), '-c:a', 'libmp3lame', '-q:a', '2', str(dst)], check=True); return d, n

if __name__ == '__main__':
    a = sys.argv[1:]
    if a[:1] == ['--用']:
        import shutil; shutil.copy(PROJ / ('音乐-候选-%s.mp3' % a[1]), PROJ / '音乐.mp3'); print('音乐.mp3 <-', a[1]); sys.exit()
    if a[:1] == ['--接']:
        A, B, n = PROJ / ('音乐-候选-%s.mp3' % a[1]), PROJ / ('音乐-候选-%s.mp3' % a[2]), int(a[3]); lead = SB.get('lead_seconds', 3)
        tA = lead + TL['clips'][n]['start'] - 0.2; tB = lead + TL['clips'][n + 1]['start'] - 0.6
        fc = ('[0:a]atrim=0:%.2f,afade=t=out:st=%.2f:d=3,apad[x];[1:a]atrim=0:%.2f,afade=t=in:st=0:d=3,adelay=%d|%d[y];[x][y]amix=inputs=2:duration=longest:normalize=0[out]'
              % (tA, tA - 3, NEED - tB, tB * 1000, tB * 1000))
        subprocess.run([FF, '-y', '-v', 'error', '-i', str(A), '-i', str(B), '-filter_complex', fc, '-map', '[out]', '-t', str(NEED), '-c:a', 'libmp3lame', '-q:a', '2', str(PROJ / '音乐.mp3')], check=True)
        print('音乐.mp3 <- %s 到 %.1fs，%s 从 %.1fs，共 %.1fs' % (a[1], tA, a[2], tB, dur(PROJ / '音乐.mp3'))); sys.exit()
    for name, prompt in CFG['candidates'].items():
        raw = PROJ / ('音乐-候选-%s-原始.mp3' % name); out = PROJ / ('音乐-候选-%s.mp3' % name)
        if not raw.exists():
            d = rep.predict('minimax/music-1.5', {'prompt': prompt, 'lyrics': CFG.get('lyrics_by', {}).get(name, CFG.get('lyrics', LYR)), 'bitrate': 256000, 'sample_rate': 44100, 'audio_format': 'mp3'}, log=False)
            rep.save_record(dict(d, input={'prompt': prompt}), PROJ / '记录' / ('音乐-%s.json' % name))
            if d['status'] != 'succeeded': print('FAIL', name, d.get('error')); continue
            rep.download(d['output'] if isinstance(d['output'], str) else d['output'][0], raw)
        d, n = loop(raw, out); print('%s: 原始 %.1fs，循环 %d 次 → %.1fs' % (name, d, n, dur(out)))
