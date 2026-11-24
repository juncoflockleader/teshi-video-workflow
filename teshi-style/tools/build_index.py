#!/usr/bin/env python3
"""Build a corpus index (JSONL) from the daguguguji GitBook repo.

Usage:
    python3 build_index.py /path/to/daguguguji [-o corpus.jsonl]

Each line: {id, title, section, genre, path, chars, paras, text, tags,
            stats:{...}}  — `text` holds the full body so downstream tools
            (pick_exemplars.py, style_lint.py) work without the repo.
"""
import argparse, json, os, re, sys, statistics

SECTION_GENRE = {
    "parti-xiao-shuo-yu-san-wen": ("I 小说与散文", "fiction"),
    "part-ii-shi-ge": ("II 诗歌", "poem"),
    "part-iii-duan-zi-yu-wei-ping": ("III 段子与微评", "micro"),
    "part-iv-ye-sheng-guo-dong-lin-fang-xie": ("IV 野生郭东林仿写", "imitation"),
    "partv-zhi-hu-wang-yan-su-wen-xue-ping-lun-jia-wen-ping-ji-jin": ("V 文评", "criticism"),
    "part-iv-hou-ji": ("VI 后记", "meta"),
    "part-vii-bu-lu": ("VII 补录", "fiction"),
    "part-vii-shi-yi": ("VII 拾遗", "micro"),
    "part-viii-yinyue": ("VIII 音乐", "meta"),
}
ROOT_META = {"README.md", "SUMMARY.md", "cover.md", "bian-zhe-an.md", "xu.md"}

# Signature tokens used for tagging (kept in sync with style_lint.py)
TOKENS = {
    "喷了": r"喷了", "嗷": r"嗷", "昏古七": r"昏古七", "哪能": r"哪能",
    "你国": r"你国|贵国|你球", "是这样的": r"是这样的|情况是这样的",
    "对不对": r"对不对|有没有一定道理|是不是这个道理", "大家说": r"大家说|大家讲|你说",
    "讲真": r"讲真", "一个狗": r"一个狗", "一个X(动物)": r"一个(猫|驴|熊|猴|鱼|狗熊|海豹)",
    "前手/后腿": r"前手|后腿|后手", "完了": r"完了|完蛋了", "大型": r"大型",
    "波澜壮阔": r"波澜壮阔", "扑面而来": r"扑面而来", "此起彼伏": r"此起彼伏",
    "人文": r"人文", "德味": r"德味", "腔调": r"腔调", "一泡污": r"一泡污",
    "土锤": r"土锤|刚波", "郭东林": r"郭[东冬]林", "打钱": r"打钱",
    "月入": r"月入\s*\d+", "行动电话/网际网路": r"行动电话|网际网路|网路|数位",
    "远方": r"远方", "啊生活": r"啊[！!~～]?\s*生活", "惨": r"惨极了|太惨了|悲惨",
    "特了": r"[跑爆疯淹死]特了", "沪语": r"册那|一刚|阿拉|晓得伐|侬|伊|伐",
    "肥肠": r"肥肠", "不要脸": r"不要脸", "崩溃": r"崩溃", "想通了": r"想通了",
    "仪式感": r"仪式", "陌生化": r"陌生化", "灵魂": r"灵魂", "严肃": r"严肃",
    "当代": r"当代", "中产": r"中产", "保定": r"保定|廊坊|燕郊|石家庄|河间",
    "东南雅": r"东南雅", "老王/老张/老刘": r"老[王张刘]", "小李/小刘/小张": r"小[李刘张王红]",
    "王大锤/李大根/李大猫": r"王大锤|李大根|李大猫|张大锤|马富贵|马福贵",
    "狗熊": r"狗熊", "驴": r"驴", "猫/毛": r"猫|不要脸毛", "土拨鼠/黄鼠狼/海豹": r"土拨鼠|黄鼠狼|海豹",
    "英文夹杂": r"[A-Za-z]{3,}", "精确数字": r"\d+(\.\d+)?\s*(米|厘米|斤|公斤|分钟|秒|元|块|岁|周岁|个|只|条|碗|层|寸|毫升|磅)",
    "年份": r"(19[89]\d|20[012]\d)\s*年", "夏天": r"夏天", "河": r"河流|大河|河边",
    "歌词~": r"~|～", "未闭合括号": r"[（(][^）)]*$",
    "温馨感人": r"温馨感人|励志向上|幸福圆满|惊悚|哈感人",
}

def split_sentences(text):
    # Chinese sentence split on 。！？；… and newlines; keep non-empty
    parts = re.split(r"[。！？；!?\n]+", text)
    return [p.strip() for p in parts if p.strip()]

def stats_for(text):
    body = re.sub(r"^#.*$", "", text, flags=re.M)
    body = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", body)
    paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
    sents = split_sentences(body)
    slen = [len(s) for s in sents] or [0]
    clauses = re.split(r"[，,。！？；!?\n]+", body)
    clen = [len(c.strip()) for c in clauses if c.strip()] or [0]
    chars = len(re.sub(r"\s", "", body))
    punct = {
        "excl": body.count("！") + body.count("!"),
        "q": body.count("？") + body.count("?"),
        "comma": body.count("，") + body.count(","),
        "period": body.count("。"),
        "tilde": body.count("~") + body.count("～"),
        "ellipsis_dots": body.count("。。。") + body.count("..."),
        "quote_open": body.count("“") + body.count('"'),
        "paren_open": body.count("（") + body.count("("),
        "paren_close": body.count("）") + body.count(")"),
    }
    dialogue_lines = sum(1 for p in paras if re.match(r"^\s*[“\"「]", p) or "说：" in p or "说:" in p)
    toks = {k: len(re.findall(v, body, flags=re.M)) for k, v in TOKENS.items()}
    return {
        "chars": chars, "paras": len(paras), "sentences": len(sents),
        "sent_len_mean": round(statistics.mean(slen), 1), "sent_len_median": statistics.median(slen),
        "clause_len_mean": round(statistics.mean(clen), 1), "clause_len_median": statistics.median(clen),
        "para_len_mean": round(chars / max(len(paras), 1), 1),
        "short_sent_ratio": round(sum(1 for s in slen if s <= 8) / max(len(slen), 1), 2),
        "punct": punct,
        "excl_per_100": round(100 * punct["excl"] / max(chars, 1), 2),
        "q_per_100": round(100 * punct["q"] / max(chars, 1), 2),
        "period_per_100": round(100 * punct["period"] / max(chars, 1), 2),
        "comma_per_100": round(100 * punct["comma"] / max(chars, 1), 2),
        "dialogue_para_ratio": round(dialogue_lines / max(len(paras), 1), 2),
        "tokens": toks,
        "token_density_per_1k": round(1000 * sum(v for k, v in toks.items() if k not in ("英文夹杂", "精确数字", "年份", "歌词~", "未闭合括号")) / max(chars, 1), 1),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("-o", "--out", default="corpus.jsonl")
    a = ap.parse_args()
    rows = []
    for dirpath, dirs, files in os.walk(a.repo):
        dirs[:] = [d for d in dirs if d not in ("_book", ".git", "assets", "node_modules")]
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            rel = os.path.relpath(os.path.join(dirpath, f), a.repo)
            top = rel.split(os.sep)[0]
            if rel in ROOT_META:
                section, genre = ("meta", "meta")
            elif top in SECTION_GENRE:
                section, genre = SECTION_GENRE[top]
            else:
                continue
            text = open(os.path.join(dirpath, f), encoding="utf-8").read()
            text = re.sub(r"^---\n.*?\n---\n", "", text, flags=re.S)  # strip frontmatter
            m = re.search(r"^#\s*(.+)$", text, flags=re.M)
            title = m.group(1).strip() if m else os.path.splitext(f)[0]
            base_id = os.path.splitext(rel)[0].replace(os.sep, "/")
            units = [(base_id, title, text)]
            # 拾遗 is one file of many independent weibo posts: split into one record per post
            if f == "te-shi-shi-yi.md":
                body = re.sub(r"^#\s*.+\n", "", text, count=1, flags=re.M)
                body = re.sub(r"^_.*_\s*$", "", body, flags=re.M)
                posts = [p.strip() for p in re.split(r"\n\s*\n", body) if len(p.strip()) >= 12]
                units = [(f"{base_id}#{i:03d}", f"拾遗#{i:03d} " + re.sub(r"\s+", " ", p)[:14] + "…", p)
                         for i, p in enumerate(posts)]
            for uid, utitle, utext in units:
                st = stats_for(utext)
                if genre == "fiction" and st["chars"] < 400:
                    genre_eff = "micro"
                else:
                    genre_eff = genre
                tags = [k for k, v in st["tokens"].items() if v > 0]
                rows.append({
                    "id": uid, "title": utitle,
                    "section": section, "genre": genre_eff, "path": rel,
                    "chars": st["chars"], "paras": st["paras"], "tags": tags,
                    "stats": st, "text": utext.strip(),
                })
    with open(a.out, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"wrote {len(rows)} records to {a.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
