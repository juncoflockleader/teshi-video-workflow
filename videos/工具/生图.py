"""用 google/nano-banana 出角色设定图与各镜场景图。在项目目录运行（或设 PROJ）；已存在的文件跳过；记录写入 <项目>/记录/，不含凭据。
  python3 ../工具/生图.py            出缺的图
  python3 ../工具/生图.py 03a 12b    强制重出
  python3 ../工具/生图.py --去字 03a 只去文字
"""
import sys, os, json, base64, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, str(Path(__file__).parent))
import rep

HERE = Path(os.environ.get('PROJ', os.getcwd())).resolve()
SB = json.load(open(HERE / '分镜.json'))
IMG = HERE / '图'; REC = HERE / '记录'
IMG.mkdir(exist_ok=True); REC.mkdir(exist_ok=True)
MODEL = 'google/nano-banana'

def data_uri(p):
    return 'data:image/jpeg;base64,' + base64.b64encode(Path(p).read_bytes()).decode()

def gen(name, prompt, refs=(), aspect='16:9', force=False):
    out = IMG / (name + '.jpg')
    if out.exists() and not force:
        return out
    inputs = {'prompt': prompt, 'aspect_ratio': aspect, 'output_format': 'jpg'}
    if refs:
        inputs['image_input'] = [data_uri(IMG / (r + '.jpg')) for r in refs]
    for attempt in range(3):
        try:
            d = rep.predict(MODEL, inputs, log=False)
            rec = dict(d); rec['input'] = {k: (v if k != 'image_input' else ['<%s>' % r for r in refs]) for k, v in inputs.items()}
            rep.save_record(rec, REC / ('图-%s.json' % name))
            if d['status'] != 'succeeded':
                raise RuntimeError('status %s: %s' % (d['status'], d.get('error')))
            url = d['output'] if isinstance(d['output'], str) else d['output'][0]
            rep.download(url, out)
            print('OK', name, flush=True)
            return out
        except Exception as e:
            print('RETRY' if attempt < 2 else 'FAIL', name, str(e)[:200], flush=True)
            time.sleep(5)
    return None

def strip_text(name):
    """用 nano-banana 对已有图做编辑：只去掉文字，其余不变。原图另存为 图/原-<name>.jpg。"""
    src = IMG / (name + '.jpg'); bak = IMG / ('原-' + name + '.jpg')
    if not bak.exists(): bak.write_bytes(src.read_bytes())
    inputs = {'prompt': 'Remove every piece of text, every letter, word, caption and name label from this image. Keep everything else exactly the same: same characters, same colors, same composition, same style. Fill the removed areas with the surrounding flat background.',
              'image_input': [data_uri(bak)], 'aspect_ratio': 'match_input_image', 'output_format': 'jpg'}
    d = rep.predict(MODEL, inputs, log=False)
    rec = dict(d); rec['input'] = dict(inputs, image_input=['<原-%s>' % name]); rep.save_record(rec, REC / ('图-去字-%s.json' % name))
    if d['status'] != 'succeeded': print('FAIL strip', name, d.get('error')); return
    rep.download(d['output'] if isinstance(d['output'], str) else d['output'][0], src); print('STRIPPED', name, flush=True)

if __name__ == '__main__':
    if sys.argv[1:2] == ['--去字']:
        with ThreadPoolExecutor(4) as ex: list(ex.map(strip_text, sys.argv[2:]))
        sys.exit()
    only = set(sys.argv[1:])
    force = bool(only)
    # 1. 角色设定图（顺序出，后面的场景图要用）
    for name, prompt in SB['sheets'].items():
        if only and name not in only: continue
        gen(name, prompt, aspect='16:9', force=force)
    # 2. 场景图（并行 4 路）
    todo = [s for s in SB['shots'] if (not only or s['id'] in only)]
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(lambda s: gen(s['id'], s['prompt'], s['refs'], force=force), todo))
    missing = [s['id'] for s in SB['shots'] if not (IMG / (s['id'] + '.jpg')).exists()]
    print('DONE; missing:', missing)
