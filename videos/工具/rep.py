"""Replicate 调用小工具。凭据只在运行时读取，不打印、不落盘到本目录。
先看环境变量 REPLICATE_API_TOKEN；没有就读一个只放 token 的文本文件，路径取环境变量 REPLICATE_TOKEN_FILE，默认 ~/creds/replicate.token。"""
from pathlib import Path
import json, subprocess, time, sys, os

BASE = 'https://api.replicate.com/v1/'

def _key():
    k = os.environ.get('REPLICATE_API_TOKEN')
    if k: return k.strip()
    return Path(os.environ.get('REPLICATE_TOKEN_FILE', '~/creds/replicate.token')).expanduser().read_text().strip()

def request(url, payload=None, method=None, timeout=90):
    if not url.startswith(BASE):
        raise ValueError('Unexpected authentication destination: ' + url)
    key = _key()
    cfg = 'url = ' + json.dumps(url) + '\nheader = "Authorization: Bearer ' + key + '"\n'
    args = ['curl', '--silent', '--show-error', '--fail-with-body', '--max-time', str(timeout), '--config', '-']
    if payload is not None:
        cfg += 'request = "POST"\nheader = "Content-Type: application/json"\nheader = "Prefer: wait=60"\n'
        args += ['--data-binary', '@-']
        data = cfg + '\n'  # curl --config - reads config from stdin; payload must come from a file instead
    if method:
        cfg += 'request = "%s"\n' % method
    if payload is not None:
        import tempfile, os
        tf = tempfile.NamedTemporaryFile('w', suffix='.json', delete=False)
        json.dump(payload, tf, ensure_ascii=False); tf.close()
        args[-1] = '@' + tf.name
    r = subprocess.run(args, input=cfg, text=True, capture_output=True)
    if payload is not None:
        os.unlink(tf.name)
    if r.returncode:
        raise RuntimeError((r.stdout[:1500] + r.stderr[:500]).replace(key, '[REDACTED]'))
    return json.loads(r.stdout) if r.stdout.strip() else {}

def get(path):
    return request(BASE + path.lstrip('/'))

def predict(model, inputs, wait=True, log=True):
    """model 形如 'google/nano-banana'；返回 prediction dict。"""
    d = request(BASE + 'models/%s/predictions' % model, {'input': inputs})
    while wait and d['status'] not in ('succeeded', 'failed', 'canceled'):
        if log: print('  ', model, d['status'], flush=True)
        time.sleep(4)
        d = request(d['urls']['get'])
    return d

def predict_version(model, inputs, wait=True, log=True):
    """非官方模型走 /v1/predictions + version id（官方模型路由 404 时用）。"""
    ver = get('models/' + model)['latest_version']['id']
    d = request(BASE + 'predictions', {'version': ver, 'input': inputs})
    while wait and d['status'] not in ('succeeded', 'failed', 'canceled'):
        if log: print('  ', model, d['status'], flush=True)
        time.sleep(4); d = request(d['urls']['get'])
    return d

def download(url, dest, timeout=300):
    dest = Path(dest); dest.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['curl', '--silent', '--show-error', '--fail', '--location', '--max-time', str(timeout),
                    url, '--output', str(dest)], check=True)
    return dest

def save_record(d, dest):
    """保存 prediction 记录（不含凭据）。"""
    Path(dest).write_text(json.dumps(d, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    acct = get('account')
    print('account:', acct.get('username'), acct.get('type'))
    for m in sys.argv[1:]:
        try:
            info = get('models/' + m)
            lv = info.get('latest_version') or {}
            print('OK  ', m, '|', (info.get('description') or '')[:90], '| run_count', info.get('run_count'))
        except Exception as e:
            print('MISS', m, str(e)[:160])
