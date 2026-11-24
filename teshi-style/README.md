# teshi-style — 让 agent 写 / 转换 特师体（大咕咕咕鸡 · 张大锤 · 锤片）

基于 [MindFxck/daguguguji](https://github.com/MindFxck/daguguguji)《特师文集》（158 篇原作，约 11.6 万字）做的风格分析 + agent 工具包。

```
teshi-style/
├── SKILL.md                  ← agent 入口：流程、硬规则、lint 循环（Claude Code skill 格式）
├── STYLE_GUIDE.md            ← 完整分析：人设 / 叙事机制 / 语言层 / 四层配方 / 体裁 / 开头结尾 / 靶子 / 时期 / 反模式 / 量化指纹
├── references/
│   ├── lexicon.md            ← 指纹词表：功能 · 原句 · 频次
│   ├── characters.md         ← 老王 / 老张 / 老刘 / 一个狗 / 狗熊 / 驴 / 猫 …的属性与台词
│   ├── templates.md          ← 微博体 15 形 · 小说 10 壳 · 诗 4 形 · 文章→特师体转换配方（含示范）
│   ├── anti-patterns.md      ← 三篇粉丝仿写为什么失败 · LLM 草稿常见病 · 12 条人工检查清单
│   ├── music-culture.md      ← 歌 / 影 / 书引用与歌词插入的 10 种技术
│   └── exemplars/            ← 仓库里只有 agent-samples.md（agent 产出的样本）；按体裁整理的原文范例不入库，用 pick_exemplars.py 现取
├── prompts/
│   ├── write_from_idea.md    ← 从一句话想法写
│   ├── convert_article.md    ← 文章 / 新闻 / 聊天记录 → 特师体
│   └── revise.md             ← 配合 linter 的修订 pass
└── tools/
    ├── build_index.py        ← 从 repo 重建 corpus.jsonl（全文 + 每篇节奏/指纹统计）
    ├── corpus.jsonl          ← 432 条记录（拾遗已拆成单条微博），自带全文；不入库，按下文从子模块生成
    ├── pick_exemplars.py     ← 按体裁 / 主题 / 指纹 / 精选集取 few-shot 范例
    └── style_lint.py         ← 给草稿打分（节奏 · 指纹密度 · 四层覆盖 · 反模式 · 收尾），附修改建议
└── daguguguji/               ← git 子模块：上游《特师文集》原文
```

## 快速开始

**作为 Claude Code / Agent SDK skill**：把整个目录放到 `.claude/skills/teshi-style/`（或任何 skills 目录）。触发词：特师、大咕咕咕鸡、张大锤、锤片、严肃文学、「写成一个狗那种」。

**手动用**：

```bash
# 1. 取范例
python3 tools/pick_exemplars.py --curated micro -n 4
python3 tools/pick_exemplars.py --topic "裁员 开会 领导" -n 3
python3 tools/pick_exemplars.py --genre fiction --tag 狗熊 --min 800 -n 2 --seed 1

# 2. 用 prompts/ 里的模板 + 范例让模型写

# 3. lint → 改 → 再 lint
python3 tools/style_lint.py draft.md
python3 tools/style_lint.py draft.md --genre micro --json
```

Linter 基线：原作在这个 linter 上 fiction 中位 91、micro 中位 100、poem 中位 100；三篇粉丝仿写 70–84；未转换的原始新闻稿 62；典型 LLM 鸡汤稿 32。**≥85 过第一关**，然后走 `anti-patterns.md` 末尾的 12 条人工检查——linter 测不出"好不好笑""惨不惨""叙述者有没有输"，100 只表示没有可检测的机械缺陷。

## 一页纸结论

特师体 = **公文腔 + 器材评测腔 + 市井方言，一本正经地叙述被动物、数字和体制规则入侵的中年失败者日常；笑点靠错位不靠包袱，结尾靠急停不靠点题，段子底下压着一层惨。**

四层配方（仿写通常只做第 3 层）：① 物质层（钱的数字 / 食物 / 地名 / 器材）② 体制层（职级 / 编制 / 专家说 / 一是二是三是）③ 动物层（一个狗 / 狗熊 / 驴 / 前手）④ 抒情层（夏天 / 河 / 远方 / 年份 / 啊生活）。开关：叙述者是输家；最后一句不给意义。

量化指纹：分句均长 7–8 字；微博体句号 1.6/100 字（逗号长流）；指纹词每千字 10–17 个（仿写 40+ 即 cargo cult）；短句占比 0.37（仿写 0.52 太碎）。

## 语料（子模块）

原文不放在这个仓库里，通过 git 子模块引用上游的 [MindFxck/daguguguji](https://github.com/MindFxck/daguguguji)，位置是 `teshi-style/daguguguji/`。`tools/corpus.jsonl` 是从它生成的全文索引，已写进 `.gitignore`。拿到仓库后先生成一次：

```bash
git submodule update --init        # 克隆时没加 --recurse-submodules 的话
cd teshi-style
python3 tools/build_index.py daguguguji -o tools/corpus.jsonl      # 432 条
```

`pick_exemplars.py` 读这个索引，没有它取不了范例；`style_lint.py` 没有索引也能跑。按体裁整理好的原文范例文件同样不入库，需要时现取，例如 `python3 tools/pick_exemplars.py --curated micro -n 4`。

## 版权

语料版权属原作者（大咕咕咕鸡）及《特师文集》整理者；本工具包只做风格分析，范例为引用。给特师打钱。
