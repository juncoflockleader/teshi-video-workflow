"""用 google/veo-3.1-fast 与 minimax/hailuo-2.3-fast 把场景图转成短片段（图生视频）。在项目目录运行（或设 PROJ）；已存在的片段跳过。Veo 建预测有限流，默认串行（WORKERS=1）。"""
import sys, os, json, base64, time, subprocess
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from PIL import Image
sys.path.insert(0, str(Path(__file__).parent))
import rep

HERE = Path(os.environ.get('PROJ', os.getcwd())).resolve()
TOOLS = Path(__file__).resolve().parent
SB = json.load(open(HERE / '分镜.json'))
IMG, CLIP, REC = HERE / '图', HERE / '片段', HERE / '记录'
CLIP.mkdir(exist_ok=True); REC.mkdir(exist_ok=True)
NEG = 'text, letters, numbers, captions, watermark, photorealistic, 3D render, extra characters, morphing, distortion'

def first_frame_uri(id, size=(1920, 1080)):
    """Veo 建议 16:9 的 1280x720 或 1920x1080；统一重采样后以 data URI 送入。"""
    p = HERE / '记录' / ('首帧-%s.jpg' % id)
    Image.open(IMG / (id + '.jpg')).convert('RGB').resize(size, Image.LANCZOS).save(p, quality=92)
    return 'data:image/jpeg;base64,' + base64.b64encode(p.read_bytes()).decode()

def need_seconds(id):
    out = subprocess.run([sys.executable, str(TOOLS / '合成.py'), '--shots'], capture_output=True, text=True, cwd=str(HERE), env=dict(os.environ, PROJ=str(HERE))).stdout
    for line in out.splitlines():
        parts = line.split()
        if parts and parts[0] == id:
            return float(parts[-1].rstrip('s'))
    return 8.0

def gen(s):
    id, kind = s['id'], s['kind']
    out = CLIP / (id + '.mp4')
    if out.exists(): return
    need = need_seconds(id)
    if kind == 'veo':
        model = 'google/veo-3.1-fast'
        inputs = {'prompt': s['motion'], 'image': first_frame_uri(id), 'duration': 8, 'resolution': '1080p',
                  'aspect_ratio': '16:9', 'generate_audio': False, 'negative_prompt': NEG}
    else:
        model = 'minimax/hailuo-2.3-fast'
        ten = need > 7.5
        inputs = {'prompt': s['motion'], 'first_frame_image': first_frame_uri(id),
                  'duration': 10 if ten else 6, 'resolution': '768p' if ten else '1080p', 'prompt_optimizer': False}
    for attempt in range(6):
        try:
            print('START', id, model, inputs['duration'], 's', flush=True)
            d = rep.predict(model, inputs, log=False)
            rec = dict(d); rec['input'] = {k: (v if k not in ('image', 'first_frame_image') else '<首帧-%s.jpg>' % id) for k, v in inputs.items()}
            rep.save_record(rec, REC / ('视频-%s.json' % id))
            if d['status'] != 'succeeded':
                raise RuntimeError('status %s: %s' % (d['status'], str(d.get('error'))[:300]))
            url = d['output'] if isinstance(d['output'], str) else d['output'][0]
            rep.download(url, out)
            print('OK', id, model, 'predict_time', (d.get('metrics') or {}).get('predict_time'), flush=True)
            return
        except Exception as e:
            print('RETRY' if attempt < 5 else 'FAIL', id, str(e)[:300], flush=True); time.sleep(15 * (attempt + 1))

if __name__ == '__main__':
    only = set(sys.argv[1:])
    todo = [s for s in SB['shots'] if s['kind'] in ('veo', 'hailuo') and (not only or s['id'] in only)]
    workers = int(__import__('os').environ.get('WORKERS', '1'))  # Veo 建预测有限流，默认串行
    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(gen, todo))
    print('DONE; have:', sorted(p.name for p in CLIP.glob('*.mp4')))
