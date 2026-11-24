"""把一个项目的「旁白切句 + 逐镜画面」定义生成为 配音/配音.json、分镜.json、脚本.md。不调用付费服务。
由各项目目录下的 出脚本.py 调用：
    import 脚本; 脚本.build(HERE, SRC, meta, SCENES, SHOTS, HINTS, FLAGS, refkeys, todo)
SHOTS 每项为 (首句序号, 中文画面, 英文场景提示词, 其他字段{kind, motion, labels})。
"""
import json, re
from pathlib import Path

INK, RED = [44, 38, 32, 255], [190, 78, 44, 255]
VSTYLE = ' Static camera. Hand-drawn brush-and-ink animation on plain off-white paper, keep the exact drawing style of the input image, limited simple motion, nothing new appears, no text.'
ONE = 'Use EXACTLY the character designs from the reference images, but do not copy their layout or background. Draw each named character exactly once. '
VOICE = {'voice_id': 'Chinese (Mandarin)_Male_Announcer', 'speed': 0.98, 'pitch': 0, 'emotion': 'neutral', 'language_boost': 'Chinese',
         'audio_format': 'mp3', 'sample_rate': 32000, 'bitrate': 256000}

PAPER = [243, 236, 220]
SKY = 'Setting: high in the sky among curled cloud strokes. There are NO trees, NO huts, NO fences, NO villages and NO ground scenery anywhere in the picture; the background is empty paper. '

def lab(text, x, y, size=64, color=INK, t0=None, t1=None, font=None, clip=None, frac=None, box=None):
    """clip=第几句开头出现，frac=该句内的比例（合成时按时间轴换算）；也可直接给 t0 秒。"""
    d = dict(text=text, x=x, y=y, size=size, color=color)
    if clip is not None: d['clip'] = clip
    if frac is not None: d['frac'] = frac
    if font: d['font'] = font   # 'song' = 宋体
    if box: d['box'] = True     # 字后垫半透明深色底
    if t0 is not None: d['t0'] = t0
    if t1 is not None: d['t1'] = t1
    return d

def _style(STYLE, ex):
    """每镜可换掉画风里的背景句（从 'Setting:' 到 'Deadpan' 之前）：ex['sky']=True 换成云中；ex['setting']='Setting: ... ' 换成给定的句子。"""
    rep = SKY if ex.get('sky') else ex.get('setting')
    if not rep: return STYLE
    i0 = STYLE.find('Setting:'); i1 = STYLE.find('Deadpan', i0)
    return STYLE[:i0] + rep + STYLE[i1:] if i0 >= 0 and i1 > i0 else STYLE

def _dark(card):
    """深色底画风：去掉纸色配置，回到合成工具的深色默认值。"""
    for k in ('overlay', 'title_color', 'tag_color', 'end_bg', 'fade_color'): card.pop(k)
    card['credits'] = [[c[0], c[1], col] for c, col in zip(card['credits'], ([255, 243, 210, 255], [230, 230, 240, 230], [200, 205, 225, 220], [160, 165, 195, 200]))]

def build(HERE, SRC, meta, SCENES, SHOTS, HINTS, FLAGS, refkeys, todo=()):
    """meta: title, tag, source, output, card_background, style_note；refkeys: [(提示词里的关键词, 参照图名), ...]，按顺序匹配，最多取 3 张。"""
    HERE = Path(HERE); art = json.load(open(HERE / '画风.json')); STYLE = art['style']
    CLIPS = [t for _, cs in SCENES for t in cs]
    norm = lambda s: re.sub(r'\s', '', s)
    body = Path(SRC).read_text().split('\n', 1)[1]
    assert norm(''.join(CLIPS)) == norm(body), '切句与正文不一致'
    starts = [s[0] for s in SHOTS]
    assert starts == sorted(set(starts)) and starts[0] == 0 and starts[-1] < len(CLIPS), '镜头首句序号有误'
    for h in HINTS: assert any(h[0] in t for t in CLIPS), '读音表未命中: %s' % h[0]

    (HERE / '配音').mkdir(exist_ok=True)
    json.dump({'title': meta['title'], 'subtitle': meta['tag'], 'source': meta['source'], 'voice': VOICE, 'lead': 0.7, 'numbers': meta.get('numbers', []), 'hints': HINTS, 'flags': FLAGS,
               'gaps': {'comma': 0.22, 'period': 0.45, 'scene': 0.85, 'tail': 1.2},
               'scenes': [{'kind': 's%02d' % i, 'title': t, 'clips': cs} for i, (t, cs) in enumerate(SCENES)]},
              open(HERE / '配音' / '配音.json', 'w'), ensure_ascii=False, indent=1)

    def refs_for(en):
        out = []
        for key, name in refkeys:
            if key in en and name not in out: out.append(name)
        return out[:3]
    shots = []
    for k, (c, cn, en, ex) in enumerate(SHOTS):
        refs = ex.get('refs', refs_for(en))
        s = {'id': '%02d' % (k + 1), 'from_clip': c, 'kind': ex.get('kind', 'still'), 'refs': refs, 'cn': cn,
             'prompt': (ONE if refs else '') + 'Scene: ' + en + ' ' + _style(STYLE, ex), 'motion': (ex['motion'] + meta.get('vstyle', VSTYLE)) if ex.get('motion') else None}
        for key in ('labels', 'overlays', 'fit', 'static'):
            if ex.get(key): s[key] = ex[key]
        shots.append(s)
    card = {'background': meta.get('card_background', '01'), 'title': meta['title'], 'title_size': meta.get('title_size', 96), 'title_y': 0.42,
            'tag': meta['tag'], 'tag_size': 56, 'tag_y': 0.56,
            # 白纸画风：纸色罩在背景图上，墨色字；片头片尾从纸色淡入淡出
            'overlay': PAPER + [215], 'title_color': INK, 'tag_color': RED, 'end_bg': PAPER + [255], 'fade_color': PAPER + [255],
            'credits': [[meta['source'], 54, INK], ['原文：' + meta['credit_src'], 36, [90, 82, 72, 255]],
                        ['配音 MiniMax Speech 2.8 HD   ·   画面 Nano Banana · Veo 3.1   ·   音乐 MiniMax Music 1.5', 32, [120, 112, 100, 255]], [meta.get('credit_note', '人物、情节为戏说'), 30, [150, 142, 130, 255]]]}
    if meta.get('dark'): _dark(card)
    card.update(meta.get('card', {}))
    json.dump({'style': STYLE, 'cast': art['cast'], 'sheets': art['sheets'], 'shots': shots, 'card': card, 'output': meta['output'],
               'lead_seconds': 3.0, 'tail_seconds': 4.0, 'size': [1920, 1080], 'fps': 24, 'kb_scale': 1.06}, open(HERE / '分镜.json', 'w'), ensure_ascii=False, indent=1)

    nchar = len(norm(''.join(CLIPS))); est = nchar / 5.16   # 《上天问》实测：1198 字 232 秒
    scene_of = [si for si, (_, cs) in enumerate(SCENES) for _ in cs]
    nvid = sum(s['kind'] != 'still' for s in shots)
    L = ['# 视频脚本：%s%s' % (meta['title'], meta['tag']), '',
         '%s。旁白即定稿全文，一字未改。本文件由 `出脚本.py` 生成，要改请改那个文件里的 SCENES / SHOTS。' % meta['source'], '',
         '## 概况', '',
         '- 旁白 %d 句、%d 字；画面 %d 镜，其中 %d 镜做成动画，其余是静帧加缓慢推拉。' % (len(CLIPS), nchar, len(shots), nvid),
         '- 预计正片约 %d 分 %02d 秒（按《上天问》的语速折算），另加片头 3 秒、片尾 4 秒。' % (est // 60, est % 60),
         '- 画风：%s' % meta['style_note'],
         '- 配音：沿用《上天问》的男声播音音色，语速 0.98。', '']
    cur = -1
    for k, s in enumerate(shots):
        si = scene_of[s['from_clip']]
        if si != cur:
            cur = si; L += ['', '## %d. %s' % (si + 1, SCENES[si][0]), '', '| 镜 | 旁白 | 画面 | 叠字 |', '|---|---|---|---|']
        end = shots[k + 1]['from_clip'] if k + 1 < len(shots) else len(CLIPS)
        L.append('| %s%s | %s | %s | %s |' % (s['id'], '' if s['kind'] == 'still' else ' 动', '<br>'.join(CLIPS[s['from_clip']:end]), s['cn'],
                                           '；'.join(l['text'] for l in s.get('labels', []))))
    L += ['', '## 读音', '', '已加拼音提示的（送入配音时替换）：', ''] + ['- %s：%s' % (h[0], h[2]) for h in HINTS]
    L += ['', '没加提示、试听时要留意的：', ''] + ['- ' + f for f in FLAGS]
    L += ['', '## 待定', ''] + ['- ' + t for t in todo] + ['']
    (HERE / '脚本.md').write_text('\n'.join(L))
    print('clips %d, chars %d, shots %d (动画 %d), est %.0fs, 最长句 %d 字' % (len(CLIPS), nchar, len(shots), nvid, est, max(len(t) for t in CLIPS)))
    used = {}
    for s in shots:
        for r in s['refs']: used[r] = used.get(r, 0) + 1
    print('参照用量:', used); print('无参照镜:', [s['id'] for s in shots if not s['refs']])
    miss = sorted({r for s in shots for r in s['refs'] if not (HERE / '图' / (r + '.jpg')).exists()})
    if miss: print('缺参照图:', miss)


def build_visual(HERE, meta, SHOTS, refkeys, todo=()):
    """只重做画面：旁白、时间轴沿用 HERE/配音/时间轴.json。写 分镜.json 与 脚本.md，不动配音。
    SHOTS 同 build；其他字段另支持 overlays。meta 另需 title, tag, source, credit_src, output, card_background, style_note。"""
    HERE = Path(HERE); art = json.load(open(HERE / '画风.json')); STYLE = art['style']
    tl = json.load(open(HERE / '配音' / '时间轴.json')); CLIPS = [c['text'] for c in tl['clips']]
    starts = [s[0] for s in SHOTS]
    assert starts == sorted(set(starts)) and starts[0] == 0 and starts[-1] < len(CLIPS), '镜头首句序号有误'
    def refs_for(en):
        out = []
        for key, name in refkeys:
            if key in en and name not in out: out.append(name)
        return out[:3]
    shots = []
    for k, (c, cn, en, ex) in enumerate(SHOTS):
        refs = ex.get('refs', refs_for(en))
        st = _style(STYLE, ex)
        s = {'id': '%02d' % (k + 1), 'from_clip': c, 'kind': ex.get('kind', 'still'), 'refs': refs, 'cn': cn,
             'prompt': (ONE if refs else '') + 'Scene: ' + en + ' ' + st, 'motion': (ex['motion'] + meta.get('vstyle', VSTYLE)) if ex.get('motion') else None}
        for key in ('labels', 'overlays', 'fit', 'static'):
            if ex.get(key): s[key] = ex[key]
        shots.append(s)
    card = {'background': meta.get('card_background', '01'), 'title': meta['title'], 'title_size': meta.get('title_size', 96), 'title_y': 0.42,
            'tag': meta['tag'], 'tag_size': 56, 'tag_y': 0.56,
            'overlay': PAPER + [215], 'title_color': INK, 'tag_color': RED, 'end_bg': PAPER + [255], 'fade_color': PAPER + [255],
            'credits': [[meta['source'], 54, INK], ['原文：' + meta['credit_src'], 36, [90, 82, 72, 255]],
                        ['配音 MiniMax Speech 2.8 HD   ·   画面 Nano Banana · Veo 3.1   ·   音乐 MiniMax Music 1.5', 32, [120, 112, 100, 255]], ['人物、情节为戏说', 30, [150, 142, 130, 255]]]}
    if meta.get('dark'): _dark(card)
    json.dump({'style': STYLE, 'cast': art['cast'], 'sheets': art['sheets'], 'shots': shots, 'card': card, 'output': meta['output'],
               'lead_seconds': 3.0, 'tail_seconds': 4.0, 'size': [1920, 1080], 'fps': 24, 'kb_scale': 1.06}, open(HERE / '分镜.json', 'w'), ensure_ascii=False, indent=1)
    nvid = sum(s['kind'] != 'still' for s in shots)
    L = ['# 画面脚本（毛笔版）：%s%s' % (meta['title'], meta['tag']), '', '旁白、配音、音乐沿用旧版，只重做画面。本文件由 `出分镜.py` 生成。', '',
         '- 旁白 %d 句，%.0f 秒；画面 %d 镜，其中 %d 镜是 Veo 动画。' % (len(CLIPS), tl['duration'], len(shots), nvid),
         '- 画风：%s' % meta['style_note'], '', '| 镜 | 旁白 | 画面 | 叠字 |', '|---|---|---|---|']
    for k, s in enumerate(shots):
        end = shots[k + 1]['from_clip'] if k + 1 < len(shots) else len(CLIPS)
        L.append('| %s%s | %s | %s | %s |' % (s['id'], '' if s['kind'] == 'still' else ' 动', '<br>'.join(CLIPS[s['from_clip']:end]), s['cn'], '；'.join(l['text'] for l in s.get('labels', []))))
    L += ['', '## 待定', ''] + ['- ' + x for x in todo] + ['']
    (HERE / '脚本.md').write_text('\n'.join(L))
    print('clips %d, shots %d (动画 %d)' % (len(CLIPS), len(shots), nvid))
    used = {}
    for s in shots:
        for r in s['refs']: used[r] = used.get(r, 0) + 1
    print('参照用量:', used); print('无参照镜:', [s['id'] for s in shots if not s['refs']])
    miss = sorted({r for s in shots for r in s['refs'] if not (HERE / '图' / (r + '.jpg')).exists()})
    if miss: print('缺参照图:', miss)
