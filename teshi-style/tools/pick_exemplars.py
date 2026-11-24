#!/usr/bin/env python3
"""Pick few-shot exemplars from corpus.jsonl for a writing/conversion task.

Usage:
  python3 pick_exemplars.py --genre micro -n 6                 # short weibo-style posts
  python3 pick_exemplars.py --genre fiction --min 600 --max 1500 -n 3
  python3 pick_exemplars.py --genre poem -n 8
  python3 pick_exemplars.py --keyword 狗熊 --keyword 动物园 -n 3
  python3 pick_exemplars.py --tag 一个狗 --tag 对不对 -n 4
  python3 pick_exemplars.py --topic "办公室 领导 开会" -n 4      # crude bag-of-chars similarity
  python3 pick_exemplars.py --ids parti-xiao-shuo-yu-san-wen/zhu-yi-lou-de-hao-chu
  python3 pick_exemplars.py --list --genre fiction             # titles + sizes only
  python3 pick_exemplars.py --curated micro                    # hand-picked canonical set

Options: --format md|json|plain ; --seed N ; --include-imitation (off by default)
Tip: --topic is a crude char-bigram match normalised by length; for a precise hit use
     --keyword 遛狗 --keyword 小区 (substring AND). Combine with --max 1200 to keep few-shot short.
Output is meant to be pasted straight into a prompt as <exemplar> blocks.
"""
import argparse, json, os, random, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_CORPUS = os.path.join(HERE, "corpus.jsonl")

# Hand-curated canonical exemplars per genre (ids relative to repo, no .md)
CURATED = {
    "micro": [
        "part-iii-duan-zi-yu-wei-ping/yuan-fang-2",          # 远方 2：青年美工小李 — 叙事-反转模板
        "part-iii-duan-zi-yu-wei-ping/bing-xiang",           # 冰箱=时光机 — 观察+恍惚
        "part-iii-duan-zi-yu-wei-ping/jiao-zi",              # 饺子 — 观察+总结+一种严肃的生活
        "part-iii-duan-zi-yu-wei-ping/ren-min-zuo-zhu",      # 人民做主 — 伪新闻+政治荒诞
        "part-iii-duan-zi-yu-wei-ping/ru-he-zhi-liao-huai-cai-bu-yu-1",  # 伪科普/偏方
        "part-iii-duan-zi-yu-wei-ping/na-han",               # 呐喊 — 痛斥体+咏叹
        "part-iii-duan-zi-yu-wei-ping/bao-fu-she-hui",       # 报复社会 — 啊生活 结尾
        "part-iii-duan-zi-yu-wei-ping/xi-du-he-pao-bu",      # 吸毒和跑步 — 伪社会新闻
        "part-iii-duan-zi-yu-wei-ping/dong-zhi-men-er",      # 东直门儿 — 复读机对话
        "part-iii-duan-zi-yu-wei-ping/ji-ge-chang-jing-tou-su-cai",  # 清单体
        "part-iii-duan-zi-yu-wei-ping/ba-shi-nian-dai",      # 八十年代 — 一句话时代速写
        "part-iii-duan-zi-yu-wei-ping/zhu-you",              # 猪油 — 抒情+年份+突然的性
    ],
    "fiction": [
        "parti-xiao-shuo-yu-san-wen/wu-han-mou-xing-fu-zhong-chan-jia-ting-li-yi-ge-gou-de-bo-lan-zhuang-kuo-da-ji-hua-li-zhi-xiang-shan",
        "parti-xiao-shuo-yu-san-wen/zhu-yi-lou-de-hao-chu",
        "parti-xiao-shuo-yu-san-wen/da-xue-hou-de-qing-chen-wen-xin-gan-ren",
        "parti-xiao-shuo-yu-san-wen/dong-zhi-lao-gong-beng-kui-le-wen-gan-ren",
        "parti-xiao-shuo-yu-san-wen/de-wei-wo-tu-ran-fa-xian-wo-shi-yong-nuo-ji-ya-de-fang-xiang-wan-quan-cuo-le",
        "parti-xiao-shuo-yu-san-wen/jing-guo-ren-zhen-si-kao-lao-wang-fa-xian-lao-zhang-bu-shi-he-zi-ji",
        "parti-xiao-shuo-yu-san-wen/shuo-yi-shuo-zai-wo-lao-jia-zhuang-jia-de-zhong-zhi-qing-kuang",
        "parti-xiao-shuo-yu-san-wen/wo-jue-de-you-ren-yao-hai-wo",
        "parti-xiao-shuo-yu-san-wen/ya-la-suo-na-jiu-shi-bei-hai-gong-yuan",
        "parti-xiao-shuo-yu-san-wen/xia-li-bai-jiu-38-zhou-sui-le-gan-jue-hen-huang",
        "part-vii-bu-lu/sheng-huo-ji-zhan-chang",
        "part-vii-bu-lu/yi-ge-gou-he-he",
    ],
    "poem": [
        "part-ii-shi-ge/qi-yue", "part-ii-shi-ge/ping-yuan-shang-de-lao-wang", "part-ii-shi-ge/yi-zhong-cao",
        "part-ii-shi-ge/kan-lv-1", "part-ii-shi-ge/an-hui-ren", "part-ii-shi-ge/lao-liu",
        "part-ii-shi-ge/da-xu-shi", "part-ii-shi-ge/ye-wan", "part-ii-shi-ge/ci-yao-de-sheng-huo",
        "part-ii-shi-ge/zai-xia-tian-bi-xu-ren-shi-yi-ge-gu-niang", "part-ii-shi-ge/yao-zi",
        "part-ii-shi-ge/zen-me-tong-yi-di-qiu-shi-yuan-de",
    ],
    "rant": [  # 痛斥体 / 观察体 长微博
        "part-iii-duan-zi-yu-wei-ping/chu-guo", "part-iii-duan-zi-yu-wei-ping/gong-yuan",
        "part-iii-duan-zi-yu-wei-ping/chi-yu-jing-jie", "part-iii-duan-zi-yu-wei-ping/jing-shen-shi-jie",
        "parti-xiao-shuo-yu-san-wen/ni-guo-gou-guan-cha", "part-iii-duan-zi-yu-wei-ping/zhong-chan-jie-ji",
    ],
    "dialogue": [  # 动物/老X 对话剧场
        "parti-xiao-shuo-yu-san-wen/zhu-yi-lou-de-hao-chu",
        "parti-xiao-shuo-yu-san-wen/dong-wu-yuan-li-gu-shi-hen-duo-de-sui-bian-jiang-ji-ge",
        "parti-xiao-shuo-yu-san-wen/huang-pu-jiang-shen-ye-zhi-dian-mou-ling-dao-huang-pu-jiang-you-hua-yao-jiang",
        "part-iii-duan-zi-yu-wei-ping/jing-fen", "part-iii-duan-zi-yu-wei-ping/pi-jiu",
    ],
}

def load(path):
    return [json.loads(l) for l in open(path, encoding="utf-8")]

def body_of(r):
    t = re.sub(r"^#\s*.+\n", "", r["text"], count=1)
    return t.strip()

def fmt(r, how):
    if how == "json":
        return json.dumps({"id": r["id"], "title": r["title"], "genre": r["genre"], "text": body_of(r)}, ensure_ascii=False)
    if how == "plain":
        return f"《{r['title']}》\n{body_of(r)}\n"
    matched = (" matched=\"" + "/".join(r["_matched"][:6]) + "\"") if r.get("_matched") else ""
    return f"<exemplar id=\"{r['id']}\" genre=\"{r['genre']}\" chars=\"{r['chars']}\"{matched}>\n《{r['title']}》\n\n{body_of(r)}\n</exemplar>\n"

import math
def topic_grams(topic):
    toks = [t for t in re.split(r"[\s,，、/]+", topic) if t]
    g = set()
    for t in toks:
        if len(t) == 1:
            g.add(t)
        g.update(t[i:i+2] for i in range(len(t) - 1))
    return g

def topic_score(r, topic):
    """Overlap of topic bigrams (and single chars for 1-char tokens) with the text,
    weighted by how many times they occur, penalised by document length so a
    2700-char rant that mentions 小区 once doesn't beat a 300-char post about 小区."""
    g = topic_grams(topic)
    if not g:
        return 0, []
    body = re.sub(r"\s", "", r["text"])
    hits = {x: body.count(x) for x in g if x in body}
    if not hits:
        return 0, []
    coverage = len(hits) / len(g)
    density = sum(min(n, 5) for n in hits.values()) / max(1, math.log(len(body) + 20))
    return coverage * 3 + density, sorted(hits, key=lambda k: -hits[k])

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--corpus", default=DEFAULT_CORPUS)
    ap.add_argument("--genre", choices=["micro", "fiction", "poem", "all"], default="all")
    ap.add_argument("--curated", choices=list(CURATED.keys()))
    ap.add_argument("--keyword", action="append", default=[], help="substring that must appear in text")
    ap.add_argument("--tag", action="append", default=[], help="signature tag that must be present (see build_index TOKENS)")
    ap.add_argument("--topic", help="free text; rank by char-bigram overlap")
    ap.add_argument("--ids", nargs="*", help="explicit ids")
    ap.add_argument("--min", type=int, default=0, help="min chars")
    ap.add_argument("--max", type=int, default=10**9, help="max chars")
    ap.add_argument("-n", type=int, default=5)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--format", choices=["md", "json", "plain"], default="md")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--include-imitation", action="store_true")
    a = ap.parse_args()

    rows = load(a.corpus)
    rows = [r for r in rows if r["genre"] not in ("meta", "criticism")]
    rows = [r for r in rows if not (r["chars"] < 30 and "twitter.com" in r["text"])]
    if not a.include_imitation:
        rows = [r for r in rows if r["genre"] != "imitation"]
    byid = {r["id"]: r for r in rows}

    if a.ids:
        out = [byid[i] for i in a.ids if i in byid]
    elif a.curated:
        out = [byid[i] for i in CURATED[a.curated] if i in byid][: a.n if a.n else None]
    else:
        cand = rows
        if a.genre != "all":
            cand = [r for r in cand if r["genre"] == a.genre]
        cand = [r for r in cand if a.min <= r["chars"] <= a.max]
        for k in a.keyword:
            cand = [r for r in cand if k in r["text"]]
        for t in a.tag:
            cand = [r for r in cand if t in r["tags"]]
        if a.topic:
            scored = [(topic_score(r, a.topic), r) for r in cand]
            scored = [(sc, r) for sc, r in scored if sc[0] > 0]
            scored.sort(key=lambda x: -x[0][0])
            for sc, r in scored[: a.n]:
                r["_matched"] = sc[1]
            cand = [r for sc, r in scored]
        else:
            random.Random(a.seed).shuffle(cand)
        out = cand[: a.n]

    if a.list:
        for r in out:
            extra = ("  matched: " + "/".join(r["_matched"][:6])) if r.get("_matched") else ""
            print(f"{r['chars']:5d}  {r['genre']:8s} {r['id']}  《{r['title']}》{extra}")
        return
    for r in out:
        print(fmt(r, a.format))

if __name__ == "__main__":
    main()
