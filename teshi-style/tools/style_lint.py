#!/usr/bin/env python3
"""Lint a draft for 特师体 (大咕咕咕鸡 style) conformance.

Usage:
  python3 style_lint.py draft.md                 # auto-detect genre by length
  python3 style_lint.py draft.md --genre micro   # micro | fiction | poem
  cat draft.txt | python3 style_lint.py - --json

Prints: measured rhythm vs corpus baseline, signature-token inventory with
cargo-cult warnings, layer coverage (物质层/体制层/动物层/抒情层/收尾), anti-pattern
hits, and a 0-100 score with concrete fix suggestions. The score is a heuristic
for an agent's revision loop, not a verdict on quality.
"""
import argparse, json, os, re, statistics, sys

HERE = os.path.dirname(os.path.abspath(__file__))
CORPUS = os.path.join(HERE, "corpus.jsonl")

# ---- signature tokens (family -> regex). Keep roughly in sync with build_index.TOKENS
FAMILIES = {
    "感叹/拟声": r"喷了|嗷|昏古七|惊了|惊呆了|炸裂|炸烈|rou~|wu~|bia唧",
    "完蛋/崩溃": r"完了|完蛋了|崩溃|想通了|惨极了|太惨了|不想活了|[跑爆疯淹死]特了",
    "反问/收束": r"对不对|有没有一定道理|是不是这个道理|大家说|大家讲|你说|你想过没有|发现没|懂了没|服了没",
    "是这样的": r"是这样的|情况是这样的|确实是这样|原来是这样|怎么讲|长话短说",
    "你国/猴/驴": r"你国|贵国|你球|我国人|猴儿|猴|驴|土锤|刚波|郭[东冬]林",
    "一个X+肢体": r"一个(?:狗|猫|驴|熊|猴|鱼|海豹|大闸蟹)|前手|后腿|后手|上肢们|下肢们|舔了一下",
    "大词/文艺腔": r"大型|波澜壮阔|扑面而来|此起彼伏|人文|德味|腔调|严肃|灵魂|仪式感|仪式|陌生化|解构|当代|中产",
    "方言层": r"哪能|册那|一刚|阿拉|晓得伐|侬|伐|个么|一泡污|肥肠|旁友|可不咋地|要得|要西|萨宁|撒宁|乡窝宁|结棍|白相|事体|台型|一天世界|好哇|额$|咋整|老[难好]\S{1,2}了|嘛$",
    "台湾译名/英文": r"行动电话|网际网路|网路|数位|视讯|软体|\b(?:ridiculous|aggressive|situation|upgrade|low|push|infinity|beyond|focus|indeed|amazing|perfect|yeah)\b",
    "钱/职级": r"打钱|月入\s*\d+|支付宝|副科|正科|科员|副主任|编制|借调|组织上|一把手|书记|主任|副总|单位|低保",
    "地理锚": r"保定|廊坊|燕郊|石家庄|河间|唐山|北平|南城|东南雅|加利福尼亚|叶尼塞|苏北|安徽|东北|陕北|湖南|天通苑|回龙观|三里屯|后海|西单|鼓楼|苏州|上海|北京",
    "抒情母题": r"夏天|河流|大河|河边|远方|夜晚|深夜|夜里|月亮|星|啊[！!~～]?\s*(生活|人性|时代|青春|生命)|1[9]\d\d\s*年|20[01]\d\s*年|恍惚",
    "标题标签": r"（(?:温馨感人|励志向上|幸福圆满|惊悚|哈感人|更新好了)）",
}
# Things 特师 never does (modern meme register, emoji, AI-smooth connectors)
ANTI = {
    "当代网络梗(非特师时代)": r"yyds|绝绝子|家人们|泰裤辣|笑死|栓Q|emo了|破防|内卷|躺平|绝了|666|dddd|蚌埠住|芭比Q|有被.*到|绝绝|真的会谢|我不理解|尊嘟|咱就是说|属于是|典中典|乐子",
    "emoji/颜文字": r"[\U0001F300-\U0001FAFF☀-➿]|\(\^|\^_\^|QAQ|orz",
    "AI 连接词/议论文腔": r"综上所述|值得注意的是|不难发现|由此可见|换句话说|与此同时|一方面.{0,30}另一方面|不仅.{0,12}而且|首先.{0,80}其次|总而言之|归根结底",
    "文学化对话标签/镜头": r"(笑道|怒道|叹道|冷冷地说|淡淡地说|轻声说|低声说|喃喃道|沉吟道|正色道|打趣道|幽幽地说|缓缓开口|眼中闪过|嘴角上扬|微微一笑|嘴角勾起|会心一笑|意味深长|若有所思地|温柔地|轻轻地)",
    "作文式铺垫/顿悟": r"像往常一样|气氛有些不同|仿佛发生了|不知不觉|不禁想起|忽然明白|突然明白|终于明白|明白了一个道理|懂得了|我意识到.{0,6}(其实|原来)|回过神来才发现",
    "可爱动物": r"毛茸茸|歪着头|小爪子|软萌|呆萌|圆滚滚|水汪汪|蹭了蹭|摇着尾巴|可爱极了",
    "新闻通稿腔(原文没转掉)": r"据报道|据了解|据悉|记者|相关部门表示|业内人士|有关负责人|平台回应称|回应称|目前，|近日|日前|表示将|引发关注|网友纷纷",
    "鸡汤/升华句": r"愿你|愿我们|每个人都|其实我们都|生活不止|诗和远方|人生就是|活在当下|热爱生活的人|温柔以待|值得被爱|向阳而生|不负韶华",
}
CONNECTORS = r"因为|所以|但是|然而|因此|于是|虽然|尽管|如果|那么|而且|并且|不过|其实|总之|首先|其次|然后|接着|随后|最终|最后|同时|此外"

def sents(text):
    return [s.strip() for s in re.split(r"[。！？；!?\n]+", text) if s.strip()]

def measure(text):
    body = text.strip()
    chars = len(re.sub(r"\s", "", body))
    paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
    ss = sents(body); slen = [len(s) for s in ss] or [0]
    cl = [len(c.strip()) for c in re.split(r"[，,。！？；!?\n]+", body) if c.strip()] or [0]
    punct = dict(excl=body.count("！") + body.count("!"), q=body.count("？") + body.count("?"),
                 period=body.count("。"), comma=body.count("，") + body.count(","),
                 tilde=body.count("~") + body.count("～"))
    dialogue = sum(1 for p in paras if re.match(r"^\s*[“\"「]", p) or "说：" in p or "说:" in p or re.match(r"^\s*\S{1,4}[：:]", p))
    lines = [l for l in body.split("\n") if l.strip()]
    last = lines[-1].strip() if lines else ""
    first = lines[0].strip() if lines else ""
    fam = {k: re.findall(v, body, flags=re.M | re.I) for k, v in FAMILIES.items()}
    anti = {k: re.findall(v, body, flags=re.M) for k, v in ANTI.items()}
    conn = len(re.findall(CONNECTORS, body))
    numbers = re.findall(r"\d+(?:\.\d+)?\s*(?:米|厘米|斤|公斤|分钟|秒|元|块|岁|周岁|个|只|条|碗|层|寸|毫升|磅|人|次|平米|平|集|分|mm|cm|kg|ml|g|G|k|K|寸|瓦|流明|度)", body)
    years = re.findall(r"(?<!\d)(?:19[6-9]\d|20[0-2]\d)(?:\s*年|(?![\d多个人块元名条只寸斤米]))", body)
    english = re.findall(r"[A-Za-z]{3,}", body)
    foods = re.findall(r"饺子|卤煮|炸酱面|拍黄瓜|肘子|皮蛋|火腿肠|串儿|烤串|啤酒|扎啤|豆腐脑|煎饼|大排面|生煎|驴肉火烧|驴火|猪头肉|大肠|带鱼|大闸蟹|龙虾|米饭|包子|面皮|关东煮|凉皮|胡辣汤|糊辣汤|馄饨|油条|豆浆|炒肝|麻辣香锅|火锅|罐头|黄瓜|鸡蛋|辣椒|芥末|酱油|香醋|香油|猪油|白糖|排骨|烤肉|羊肉|牛肉|猪肉|烧烤|拌面|蒸饺|面条|大排|奶茶|咖啡|可乐|西红柿|土豆|大蒜|香菜|榨菜|咸菜|泡菜|辣白菜|小龙虾|海鲜|鲫鱼|梭子蟹|红烧肉|炒饭|寿司|酸奶|橙汁|水饺|汤圆|月饼", body)
    scenes = re.findall(r"胡同|小区|菜场|菜市场|动物园|公园|地铁|火车|招待所|办公室|科室|厨房|沙发|阳台|河边|操场|食堂|澡堂|烧烤摊|大排档|饭馆|面馆|单位门口|广场|电梯|出租车|银行|医院|病房|超市|大润发|711|便利店", body)
    TIC_FAMILIES = ("感叹/拟声", "完蛋/崩溃", "反问/收束", "是这样的", "你国/猴/驴", "一个X+肢体", "大词/文艺腔", "方言层", "台湾译名/英文")
    tics_total = sum(len(v) for k, v in fam.items() if k in TIC_FAMILIES)
    # repetition detector: any clause repeated >=3 times (a 特师 move, but also cargo-cult risk)
    cl_counts = {}
    for c in re.split(r"[，,。！？；!?\n]+", body):
        c = c.strip()
        if len(c) >= 3:
            cl_counts[c] = cl_counts.get(c, 0) + 1
    repeats = {c: n for c, n in cl_counts.items() if n >= 3}
    return dict(chars=chars, paras=len(paras), sentences=len(ss),
                sent_len_mean=round(statistics.mean(slen), 1), clause_len_mean=round(statistics.mean(cl), 1),
                short_sent_ratio=round(sum(1 for x in slen if x <= 8) / len(slen), 2),
                excl_per_100=round(100 * punct["excl"] / max(chars, 1), 2), q_per_100=round(100 * punct["q"] / max(chars, 1), 2),
                period_per_100=round(100 * punct["period"] / max(chars, 1), 2), comma_per_100=round(100 * punct["comma"] / max(chars, 1), 2),
                tilde=punct["tilde"], dialogue_para_ratio=round(dialogue / max(len(paras), 1), 2),
                first=first, last=last, families=fam, anti=anti, connectors=conn, connectors_per_100=round(100 * conn / max(chars, 1), 2),
                numbers=numbers, years=years, english=english, foods=foods, scenes=scenes, tics_total=tics_total,
                tic_density_per_1k=round(1000 * tics_total / max(chars, 1), 1), repeats=repeats)

_BASE_CACHE = {}
def baselines(genre):
    """Rhythm baselines = medians over the corpus for this genre (same measure() as the draft)."""
    fb = {
        "fiction": dict(clause_len_mean=7.4, short_sent_ratio=0.37, excl_per_100=0.48, q_per_100=0.21, period_per_100=3.46, comma_per_100=6.0, dialogue_para_ratio=0.08, tic_density_per_1k=22),
        "micro":   dict(clause_len_mean=8.4, short_sent_ratio=0.25, excl_per_100=0.93, q_per_100=0.0,  period_per_100=1.63, comma_per_100=7.3, dialogue_para_ratio=0.0,  tic_density_per_1k=30),
        "poem":    dict(clause_len_mean=7.0, short_sent_ratio=0.33, excl_per_100=0.0,  q_per_100=0.0,  period_per_100=3.4,  comma_per_100=6.0, dialogue_para_ratio=0.0,  tic_density_per_1k=10),
    }
    if genre in _BASE_CACHE:
        return _BASE_CACHE[genre]
    out = dict(fb[genre])
    if os.path.exists(CORPUS):
        try:
            rows = [json.loads(l) for l in open(CORPUS, encoding="utf-8")]
            texts = [re.sub(r"^#\s*.+\n", "", r["text"], count=1) for r in rows if r["genre"] == genre and r["chars"] >= 40]
            ms = [measure(t) for t in texts]
            if ms:
                for k in out:
                    out[k] = round(statistics.median(m[k] for m in ms), 2)
                out["_n"] = len(ms)
                out["_p90"] = {k: round(sorted(m[k] for m in ms)[int(0.9 * len(ms))], 2) for k in ("short_sent_ratio", "excl_per_100", "tic_density_per_1k", "clause_len_mean", "period_per_100")}
        except Exception:
            pass
    _BASE_CACHE[genre] = out
    return out

def lint(text, genre=None):
    m = measure(text)
    if genre is None:
        lines = [l for l in text.strip().split("\n") if l.strip()]
        avg_line = m["chars"] / max(len(lines), 1)
        genre = "poem" if (m["chars"] < 200 and len(lines) >= 3 and avg_line < 16) else ("micro" if m["chars"] < 450 else "fiction")
    b = baselines(genre)
    notes, score = [], 100

    def ding(pts, msg):
        nonlocal score; score -= pts; notes.append((pts, msg))

    # --- rhythm (thresholds ≈ corpus p90-p95; see baselines()["_p90"])
    p90 = b.get("_p90", {})
    if m["clause_len_mean"] > max(12.5, p90.get("clause_len_mean", 10) * 1.3):
        ding(12, f"分句太长（均 {m['clause_len_mean']} 字，语料中位 ~{b['clause_len_mean']}，p90 {p90.get('clause_len_mean','-')}）。拆成逗号/句号短切片，删定语和从句：「老张睡觉的时候占据双人床右侧，掌控台灯」式的并列短句。")
    if m["short_sent_ratio"] > max(0.72, p90.get("short_sent_ratio", 0.66) * 1.1) and m["chars"] > 300:
        ding(6, f"短句比例 {m['short_sent_ratio']} 过高——仿写通病（原作中位 ~{b['short_sent_ratio']}，极少超过 0.7）。特师是长短交错：一段长逗号流之后才甩一个「完了。」")
    if genre == "micro" and m["period_per_100"] > 6 and m["chars"] > 150:
        ding(6, f"句号太多（{m['period_per_100']}/100字，微博体语料中位 ~{b['period_per_100']}）。微博体是一口气的逗号长流，句号留给最后一击。")
    excl_cap = 4.5 if genre == "micro" else 2.6
    if m["excl_per_100"] > excl_cap:
        ding(8, f"感叹号过密（{m['excl_per_100']}/100字，语料中位 {b['excl_per_100']}，p90 {p90.get('excl_per_100','-')}）。感叹号集中在情绪爆点，不要每句都喊。")
    if m["connectors_per_100"] > 0.8 and m["connectors"] >= 3:
        ding(10, f"连接词太多（因为/所以/但是/然而… {m['connectors']} 处）。特师省略连接词，靠并置和跳切：删掉，直接换行或「。」")
    tagverbs = re.findall(r"[\u4e00-\u9fa5]{1,4}(说道|笑道|怒道|叹道|问道|答道|喊道|嚷道|说|讲|问|答|喊|叹)[：:，,。\s“\"]", text)
    fancy = [v for v in tagverbs if v not in ("说", "讲", "问", "喊")]
    if len(tagverbs) >= 6 and len(fancy) / len(tagverbs) > 0.3:
        ding(8, f"对话标签花哨（{len(fancy)}/{len(tagverbs)} 是 说道/笑道/叹道…）。原作只用单调的「X说」「X讲」，一篇里「狗熊说」可以出现 30 次，靠重复造节奏。")
    if genre == "fiction" and m["dialogue_para_ratio"] > 0.9 and m["paras"] > 10 and not re.search(r"舔|停顿|点头|半蹲|捧心|托腮|挠|叉腰|抱胸|一个箭步|面无表情", text):
        ding(3, "全是对话、没有一个动作短句。原作对话之间会插入「舔了一下左前手。」「停顿，」「双前手叉腰。」这种舞台指示。")

    # rhythm info (no deduction): print where the draft sits vs corpus
    info = []
    for k, label in (("period_per_100", "句号/100字"), ("comma_per_100", "逗号/100字"), ("clause_len_mean", "分句均长"), ("short_sent_ratio", "短句占比")):
        bv = b.get(k)
        if bv and m[k] > bv * 1.8:
            info.append(f"[info] {label} {m[k]} 是语料中位 {bv} 的 {m[k]/bv:.1f} 倍（p90 {p90.get(k,'-')}）——不扣分，但读一遍看是否太碎/太密。")
        elif bv and m[k] < bv * 0.5 and k != "short_sent_ratio":
            info.append(f"[info] {label} {m[k]} 只有语料中位 {bv} 的一半——不扣分，看是否太长/太平。")
    for x in info:
        notes.append((0, x))

    # --- tic inventory / cargo cult
    fam = m["families"]
    used = {k: len(v) for k, v in fam.items() if v}
    heavy = max(60, p90.get("tic_density_per_1k", 40) * 1.5); light = max(40, p90.get("tic_density_per_1k", 40))
    if m["tic_density_per_1k"] > heavy:
        ding(15, f"指纹词密度 {m['tic_density_per_1k']}/千字（语料中位 ~{b['tic_density_per_1k']}，p90 {p90.get('tic_density_per_1k','-')}）——Cargo cult。序言原话：「肥肠、一个狗、保定、驴、老王、狗熊、嗷、昏古七这些都不过是指纹」。删掉一半，用事件本身的荒诞替代。")
    elif m["tic_density_per_1k"] > light:
        ding(7, f"指纹词密度 {m['tic_density_per_1k']}/千字偏高（语料中位 ~{b['tic_density_per_1k']}）。保留 3-5 个最有效的。")
    for k, v in fam.items():
        if k not in ("感叹/拟声", "完蛋/崩溃", "反问/收束", "是这样的", "大词/文艺腔", "方言层"):
            continue  # subjects like 一个狗/老王/狗熊 are *meant* to repeat (复读机节奏)
        c = {}
        for x in v:
            c[x] = c.get(x, 0) + 1
        for x, n in c.items():
            if n >= 4 and x not in ("驴", "猴", "说", "北京", "上海", "单位", "严肃", "当代", "灵魂") and genre != "poem" and m["chars"] / n < 250:
                ding(4, f"「{x}」出现 {n} 次，每 {int(m['chars']/n)} 字一次——除非是刻意的复读机段落，否则稀释掉。")
    if genre != "poem" and m["chars"] > 200 and (m["tics_total"] < 2 or m["tic_density_per_1k"] < 3):
        ding(8, "几乎没有任何特师指纹（是这样的/对不对/喷了/嗷的一下/一个狗/你国/完了…）。至少在开头框架句和结尾各放一个。")

    # --- layer coverage (the part imitators miss). Not every original has every layer,
    #     but originals almost always have >=4 of these 8; imitations and LLM drafts have 1-2.
    layers = {}
    if genre != "poem" and m["chars"] > 150:
        layers = {
            "精确数字": bool(m["numbers"]),
            "钱/职级": bool(fam["钱/职级"]) or bool(re.search(r"\d+\s*(元|块|钱|万)", text)),
            "具体食物": bool(m["foods"]),
            "地名锚": bool(fam["地理锚"]),
            "场景物件": bool(m["scenes"]),
            "抒情母题": len(fam["抒情母题"]) >= (2 if m["chars"] > 600 else 1),
            "动物/猴驴": bool(fam["一个X+肢体"]) or bool(re.search(r"狗熊|驴|猫|海豹|土拨鼠|黄鼠狼|猩猩|大闸蟹|猴", text)),
            "框架/背书句": bool(fam["是这样的"]) or bool(fam["反问/收束"]) or bool(re.search(r"(平台|客服|专家|领导|老师|组织上|街道|单位|物业|医生|护士|老板)(说|讲|回应|表示|回复)|属于正常|正常的|按规定|规定是|经.{0,6}认定|一是.{0,40}二是", text)),
        }
        have = sum(layers.values()); need = 4 if m["chars"] > 600 else 3
        missing = [k for k, v in layers.items() if not v]
        hints = {
            "精确数字": "「一米三，跳起来一米三一」「燃烧时间最长235分钟」「总共搓了25颗」",
            "钱/职级": "月入2300 / 副主任科员 / 5000块 / 低保3000 / AA 200 / 编制 / 借调——特师的所有痛苦都有价签",
            "具体食物": "肘子/皮蛋/拍黄瓜/串儿/扎啤/炸酱面/带鱼——抒情句后面要接一个掉价的吃的",
            "地名锚": "保定/廊坊/燕郊/天通苑/后海/苏北/东南雅/加利福尼亚老家——高蹈句必须被一个县城拽回来",
            "场景物件": "胡同/菜场/动物园/科室/厨房/沙发/阳台/河边/711",
            "抒情母题": "夏天/河/远方/夜晚/年份/恍惚/啊生活——只有段子没有惨，就不是锤片",
            "动物/猴驴": "一个狗/狗熊/驴/猫/前手——动物以人的身份出现并比人更体面",
            "框架/背书句": "是这样的 / 情况是这样的 / 对不对 / 大家说 / 有没有一定道理",
        }
        if have < need:
            ding(6 * (need - have), f"物质层覆盖 {have}/8，太薄（原作长篇通常 ≥4）。缺：" + "；".join(f"{k}（{hints[k]}）" for k in missing))
        elif have < need + 1 and m["chars"] > 800:
            ding(4, f"物质层覆盖 {have}/8 刚及格。可补：" + "；".join(f"{k}（{hints[k]}）" for k in missing[:3]))
        if not fam["抒情母题"] and m["chars"] > 800:
            ding(6, "长篇却没有抒情层（夏天/河/远方/夜晚/年份/恍惚/啊生活）。在中后段插一句不搞笑的句子：「夏天在 25 岁就结束了。」")

    # --- ending
    last = m["last"]
    last_sent = [x for x in re.split(r"[。！？；!?]", last) if x.strip()]
    last_sent = last_sent[-1].strip() if last_sent else last
    if genre != "poem":
        ok_end = (len(last_sent) <= 24) or re.search(r"啊[！!~～]?\s*(生活|人性|时代)", last) or re.search(r"(点|分|半)[。]?$|此刻|早晨|晚上|夜里|夜色", last) \
                 or re.search(r"[（(][^）)]*$", last) or re.search(r"打钱|支付宝", last) or re.search(r"~|～", last)
        if not ok_end:
            ding(10, f"结尾「…{last[-30:]}」不是特师式收尾。用：①急停短句（「没有抬头。」「他已经秃了。」「北京又迎来了新的一天。」）②「啊生活」③时间戳④未闭合括号「（可以打钱了」⑤歌词拖腔⑥同一句重复三遍。")
        tail = text.strip()[-120:]
        if re.search(r"(圆满|完美)?(解决|搞定|成功|胜利|松了一口气|皆大欢喜|心满意足|如释重负|大功告成)", tail) and not re.search(r"打钱|一刚|喷了|完了|崩溃|惨|没钱|秃|被骗|被打|死了", tail):
            ding(8, "结尾是「问题解决了/大家松了一口气」——特师的第一人称从不赢；赢也是误会（防火墙是自己关的、辣椒喷雾没喷出来反被打一顿）。让结果掉价：只给20块、第二天就回来了、其实是前列腺炎。")
        if re.search(r"(明白了|懂得了|意识到|其实|原来).{0,20}(道理|意义|珍贵|重要|幸福)", last) or m["anti"]["鸡汤/升华句"]:
            ding(12, "结尾/正文在升华、点题、讲道理。特师从不解释笑点，也不给意义；删掉最后的「道理」，让最后一句是一个动作或一个数字。")
    # --- opening
    first = m["first"]
    if genre == "fiction" and len(first) > 60 and not re.search(r"是这样的|情况是这样的|长话短说|喷了|惊了|震惊|刚才|刚刚|今天|下午|昨晚|大家都知道|低调看|[！!]", first[:40]):
        ding(3, "开头是一段长铺垫。特师三种起手：①标题即首句+感叹（「我们一个同事是猩猩，今天被北京动物园的抓走了，大家都震惊了！」）②无主语名词句速写（「下午三点。莫文蔚。」）③「是这样的/情况是这样的/长话短说」。")

    # --- anti-patterns
    for k, v in m["anti"].items():
        if v:
            ding(8, f"反模式[{k}]：{'、'.join(sorted(set(v))[:6])}")
    if m["english"] and len(m["english"]) > max(6, m["chars"] / 120):
        ding(4, "英文夹杂偏多。特师一篇只插 1-3 个小写营销词（ridiculous / situation / upgrade），不翻译，不解释。")

    score = max(0, min(100, score))
    return dict(genre=genre, score=score, layers=layers, measured={k: m[k] for k in ("chars", "paras", "sentences", "sent_len_mean", "clause_len_mean", "short_sent_ratio", "excl_per_100", "q_per_100", "period_per_100", "comma_per_100", "dialogue_para_ratio", "connectors_per_100", "tic_density_per_1k")},
                baseline=b, tics_used=used, numbers=m["numbers"][:8], years=m["years"][:6], foods=sorted(set(m["foods"]))[:10],
                repeats={k: v for k, v in list(m["repeats"].items())[:6]}, first=first[:60], last=last[-60:], notes=sorted(notes, key=lambda x: -x[0]))

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="draft path or - for stdin")
    ap.add_argument("--genre", choices=["micro", "fiction", "poem"])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    text = sys.stdin.read() if a.file == "-" else open(a.file, encoding="utf-8").read()
    text = re.sub(r"^---\n.*?\n---\n", "", text.strip(), flags=re.S)   # frontmatter
    text = re.sub(r"^(#\s*.+|《.+》)\s*\n", "", text.strip(), count=1)  # leading title line
    r = lint(text, a.genre)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1)); return
    print(f"== 特师体 lint ==  genre={r['genre']}  score={r['score']}/100")
    mm, bb = r["measured"], r["baseline"]
    print("rhythm (draft vs corpus median):")
    for k in ("clause_len_mean", "short_sent_ratio", "excl_per_100", "period_per_100", "comma_per_100", "dialogue_para_ratio", "tic_density_per_1k"):
        print(f"  {k:20s} {mm[k]:>6}   ~{bb.get(k, '-')}")
    print(f"  connectors_per_100   {mm['connectors_per_100']:>6}   ~0.3")
    print("tics used:", ", ".join(f"{k}×{v}" for k, v in r["tics_used"].items()) or "(none)")
    print("numbers(first 8):", " ".join(r["numbers"]) or "(none)", "| years:", " ".join(r["years"]) or "(none)", "| foods:", " ".join(r["foods"]) or "(none)")
    if r["layers"]:
        print("layers:", "  ".join(("✓" if v else "✗") + k for k, v in r["layers"].items()))
    if r["repeats"]:
        print("repeated clauses (≥3):", "; ".join(f"「{k}」×{v}" for k, v in r["repeats"].items()))
    print("first:", r["first"]); print("last :", r["last"])
    print("notes:")
    for pts, msg in r["notes"]:
        print(f"  -{pts:2d}  {msg}" if pts else f"   ·   {msg}")
    if not [n for n in r["notes"] if n[0] > 0]:
        print("  (no detectable defects — 100 means 'nothing mechanical is wrong', not 'good'. Now run the 12-item manual checklist in references/anti-patterns.md: is it actually funny, actually sad, does the narrator lose.)")

if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        pass
