# -*- coding: utf-8 -*-
"""
短剧出海竞品报告共用库
数据源: iTunes RSS API (iOS免费榜/畅销榜, Entertainment genre=6016, Top200)
被 daily.py(每日采集+日报) 和 weekly.py(周报) 调用
"""
import json
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
BJT = timezone(timedelta(hours=8))


def today_bjt():
    return datetime.now(BJT).date()


# ---------------- 国家与权重 ----------------
COUNTRIES = [
    ("us", "美国",   6.0, "T1"),
    ("gb", "英国",   1.0, "T1"),
    ("de", "德国",   1.0, "T1"),
    ("fr", "法国",   1.0, "T1"),
    ("ca", "加拿大", 1.0, "T1"),
    ("au", "澳洲",   1.0, "T1"),
    ("it", "意大利", 1.0, "T1"),
    ("es", "西班牙", 1.0, "T1"),
    ("nl", "荷兰",   1.0, "T1"),
    ("se", "瑞典",   1.0, "T1"),
    ("no", "挪威",   1.0, "T1"),
    ("dk", "丹麦",   1.0, "T1"),
    ("fi", "芬兰",   1.0, "T1"),
    ("ch", "瑞士",   1.0, "T1"),
    ("at", "奥地利", 1.0, "T1"),
    ("be", "比利时", 1.0, "T1"),
    ("ie", "爱尔兰", 1.0, "T1"),
    ("nz", "新西兰", 1.0, "T1"),
    ("jp", "日本",   0.4, "T1"),
    ("kr", "韩国",   0.3, "T1"),
    ("tw", "台湾",   1.0, "T2"),
    ("hk", "香港",   1.0, "T2"),
    ("sg", "新加坡", 1.0, "T2"),
    ("br", "巴西",   1.0, "T2"),
    ("mx", "墨西哥", 1.0, "T2"),
    ("sa", "沙特",   1.0, "T2"),
    ("ae", "阿联酋", 1.0, "T2"),
    ("pt", "葡萄牙", 1.0, "T2"),
    ("pl", "波兰",   1.0, "T2"),
    ("tr", "土耳其", 0.3, "T3"),
    ("th", "泰国",   0.3, "T3"),
    ("id", "印尼",   0.3, "T3"),
    ("ph", "菲律宾", 0.3, "T3"),
    ("my", "马来",   0.3, "T3"),
    ("vn", "越南",   0.3, "T3"),
    ("in", "印度",   0.3, "T3"),
    ("cl", "智利",   0.3, "T3"),
    ("co", "哥伦比亚", 0.3, "T3"),
    ("ar", "阿根廷", 0.3, "T3"),
    ("za", "南非",   0.3, "T3"),
    ("eg", "埃及",   0.3, "T3"),
]

LIST_WEIGHTS = {"grossing": 0.65, "free": 0.35}

# ---------------- 追踪App清单 ----------------
APPS = [
    {"name": "DramaBox",   "match": ["dramabox"],            "vendor": "点众科技",      "model": "付费"},
    {"name": "ReelShort",  "match": ["reelshort"],           "vendor": "中文在线",      "model": "付费"},
    {"name": "ShortMax",   "match": ["shortmax"],            "vendor": "九州文化",      "model": "付费"},
    {"name": "GoodShort",  "match": ["goodshort"],           "vendor": "新阅时代",      "model": "付费"},
    {"name": "NetShort",   "match": ["netshort"],            "vendor": "安悦网络",      "model": "混合"},
    {"name": "DramaWave",  "match": ["dramawave"],           "vendor": "Nativex/汇量",  "model": "付费"},
    {"name": "MoboReels",  "match": ["moboreels"],           "vendor": "Mobo",          "model": "付费"},
    {"name": "FlexTV",     "match": ["flextv", "flex tv"],   "vendor": "安卓奇迹/嘉书", "model": "付费"},
    {"name": "My Drama",   "match": ["my drama"],            "vendor": "Holywater",     "model": "付费"},
    {"name": "Sereal+",    "match": ["sereal"],              "vendor": "Storymatrix",   "model": "付费"},
    {"name": "Vigloo",     "match": ["vigloo"],              "vendor": "四方游戏",      "model": "付费"},
    {"name": "iDrama",     "match": ["idrama"],              "vendor": "iDrama",        "model": "付费"},
    {"name": "KalosTV",    "match": ["kalos"],               "vendor": "Kalos",         "model": "付费"},
    {"name": "Melolo",     "match": ["melolo"],              "vendor": "字节跳动",      "model": "免费"},
    {"name": "FlareFlow",  "match": ["flareflow"],           "vendor": "爱奇艺",        "model": "混合"},
    {"name": "StardustTV", "match": ["stardust"],            "vendor": "Stardust",      "model": "付费"},
    {"name": "VibeShort",  "match": ["vibeshort"],           "vendor": "VibeShort",     "model": "付费"},
    {"name": "FlickReels", "match": ["flickreels"],          "vendor": "FlickReels",    "model": "付费"},
    {"name": "StoryReel",  "match": ["storyreel"],           "vendor": "StoryReel",     "model": "付费"},
    {"name": "CandyJarTV", "match": ["candyjar"],            "vendor": "CandyJar",      "model": "付费"},
    {"name": "AnyReel",    "match": ["anyreel"],             "vendor": "AnyReel",       "model": "付费"},
    {"name": "Shortical",  "match": ["shortical"],           "vendor": "Shortical",     "model": "付费"},
    {"name": "TopShort",   "match": ["topshort"],            "vendor": "TopShort",      "model": "付费"},
    {"name": "ShortTV",    "match": ["shorttv", "short tv"], "vendor": "山海星辰",      "model": "付费"},
    {"name": "Playlet",    "match": ["playlet"],             "vendor": "Playlet",       "model": "付费"},
    {"name": "MiniEpic",   "match": ["miniepic"],            "vendor": "MiniEpic",      "model": "付费"},
]

MODEL_CLS = {"付费": "tag-paid", "免费": "tag-free", "混合": "tag-hybrid"}
APPS_BY = {a["name"]: a for a in APPS}
CC_CN = {cc: cn for cc, cn, _, _ in COUNTRIES}

RSS_URL = "https://itunes.apple.com/{cc}/rss/{feed}/limit=200/genre=6016/json"
FEEDS = {"free": "topfreeapplications", "grossing": "topgrossingapplications"}


# ---------------- 采集 ----------------

def fetch_feed(cc, feed_key):
    url = RSS_URL.format(cc=cc, feed=FEEDS[feed_key])
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            entries = data.get("feed", {}).get("entry", [])
            if isinstance(entries, dict):
                entries = [entries]
            return [(i + 1, e["im:name"]["label"]) for i, e in enumerate(entries)]
        except Exception as exc:
            if attempt == 2:
                print(f"  [FAIL] {cc}/{feed_key}: {exc}")
                return None
            time.sleep(1.5 * (attempt + 1))


def match_app(store_name):
    low = store_name.lower()
    for app in APPS:
        if any(m in low for m in app["match"]):
            return app["name"]
    return None


def collect():
    rankings = {"free": {}, "grossing": {}}
    failed = []
    total = len(COUNTRIES) * 2
    done = 0
    for cc, _, _, _ in COUNTRIES:
        for feed_key in ("free", "grossing"):
            done += 1
            print(f"[{done}/{total}] {cc}/{feed_key} ...")
            rows = fetch_feed(cc, feed_key)
            if rows is None:
                failed.append(f"{cc}/{feed_key}")
                rankings[feed_key][cc] = {}
                continue
            hit = {}
            for rank, store_name in rows:
                name = match_app(store_name)
                if name and name not in hit:
                    hit[name] = rank
            rankings[feed_key][cc] = hit
            time.sleep(0.4)
    return rankings, failed


def compute_scores(rankings):
    raw = {app["name"]: 0.0 for app in APPS}
    for feed_key, lw in LIST_WEIGHTS.items():
        for cc, _, cw, _ in COUNTRIES:
            for name, rank in rankings[feed_key].get(cc, {}).items():
                raw[name] += lw * cw * (201 - rank) / 200
    top = max(raw.values()) if raw and max(raw.values()) > 0 else 1.0
    return {k: round(v / top * 100, 1) for k, v in raw.items()}


def app_stats(rankings, name):
    stats = {"free_countries": 0, "gross_countries": 0,
             "best_gross": None, "best_gross_cc": "", "best_free": None, "best_free_cc": ""}
    for cc, _, _, _ in COUNTRIES:
        g = rankings["grossing"].get(cc, {}).get(name)
        f = rankings["free"].get(cc, {}).get(name)
        if g:
            stats["gross_countries"] += 1
            if stats["best_gross"] is None or g < stats["best_gross"]:
                stats["best_gross"], stats["best_gross_cc"] = g, CC_CN[cc]
        if f:
            stats["free_countries"] += 1
            if stats["best_free"] is None or f < stats["best_free"]:
                stats["best_free"], stats["best_free_cc"] = f, CC_CN[cc]
    return stats


def load_snapshots(days=7, end_date=None):
    """加载截至end_date(默认今天)最近days天内存在的快照, 按日期升序"""
    end = end_date or today_bjt()
    snaps = []
    for i in range(days - 1, -1, -1):
        d = end - timedelta(days=i)
        p = DATA_DIR / f"rankings_{d.strftime('%Y%m%d')}.json"
        if p.exists():
            snaps.append(json.loads(p.read_text(encoding="utf-8")))
    return snaps


# ---------------- HTML公共部分 ----------------

PAGE_CSS = """
:root {
  --color-bg-primary: #0d1117;
  --color-bg-secondary: #161b22;
  --color-bg-tertiary: #1c2129;
  --color-bg-elevated: #21262e;
  --color-text-primary: #e6e9ee;
  --color-text-secondary: #9aa4b2;
  --color-text-muted: #5c6672;
  --color-border-default: #2d333d;
  --color-border-subtle: #21262e;
  --color-accent: #e8a33d;
  --color-accent-hover: #f0b45c;
  --color-accent-subtle: rgba(232,163,61,0.12);
  --color-success: #3fb950;
  --color-warning: #d29922;
  --color-danger: #f85149;
  --color-info: #58a6ff;
  --font-display: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-body: "Segoe UI", "PingFang SC", "Microsoft YaHei", sans-serif;
  --font-mono: "Cascadia Code", Consolas, "SF Mono", monospace;
  --text-xs: 10px; --text-sm: 12px; --text-base: 14px; --text-lg: 16px;
  --text-xl: 20px; --text-2xl: 28px; --text-3xl: 36px;
  --space-1: 4px; --space-2: 8px; --space-3: 12px; --space-4: 16px;
  --space-6: 24px; --space-8: 32px; --space-12: 48px;
  --radius-sm: 4px; --radius-md: 8px; --radius-lg: 12px; --radius-full: 9999px;
  --shadow-md: 0 4px 16px rgba(0,0,0,0.4);
  --duration-fast: 150ms;
  --easing-default: cubic-bezier(0.4, 0, 0.2, 1);
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  background: var(--color-bg-primary);
  color: var(--color-text-primary);
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: 1.6;
  padding: var(--space-8);
}
.container { max-width: 1600px; margin: 0 auto; }
header { margin-bottom: var(--space-12); }
.report-tag {
  display: inline-block; font-size: var(--text-sm); color: var(--color-accent);
  background: var(--color-accent-subtle); border: 1px solid var(--color-accent);
  border-radius: var(--radius-full); padding: 2px 12px; margin-bottom: var(--space-3);
  font-family: var(--font-mono);
}
h1 { font-size: var(--text-3xl); font-weight: 800; letter-spacing: 0.5px; }
.sub { color: var(--color-text-secondary); margin-top: var(--space-2); font-size: var(--text-base); }
.nav-links { margin-top: var(--space-3); font-size: var(--text-sm); }
.nav-links a { color: var(--color-info); text-decoration: none; margin-right: var(--space-4); }
.nav-links a:hover { text-decoration: underline; }
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-4); margin: var(--space-8) 0; }
.kpi {
  background: var(--color-bg-secondary); border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg); padding: var(--space-6);
  transition: border-color var(--duration-fast) var(--easing-default);
}
.kpi:hover { border-color: var(--color-accent); }
.kpi .v { font-size: var(--text-3xl); font-weight: 700; font-family: var(--font-mono); color: var(--color-accent); }
.kpi .k { font-size: var(--text-sm); color: var(--color-text-secondary); margin-top: var(--space-1); }
section { margin-bottom: var(--space-12); }
h2 {
  font-size: var(--text-xl); font-weight: 600; margin-bottom: var(--space-4);
  padding-left: var(--space-3); border-left: 3px solid var(--color-accent);
}
.desc { color: var(--color-text-secondary); font-size: var(--text-sm); margin-bottom: var(--space-4); }
.table-wrap {
  overflow-x: auto; background: var(--color-bg-secondary);
  border: 1px solid var(--color-border-subtle); border-radius: var(--radius-lg);
}
table { border-collapse: collapse; width: 100%; white-space: nowrap; }
th {
  font-size: var(--text-sm); color: var(--color-text-secondary); font-weight: 600;
  text-align: left; padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--color-border-default);
  background: var(--color-bg-tertiary); position: sticky; top: 0;
}
td { padding: var(--space-2) var(--space-4); border-bottom: 1px solid var(--color-border-subtle); font-size: var(--text-base); }
tr:hover td { background: var(--color-bg-tertiary); }
tr:last-child td { border-bottom: none; }
.pos { font-family: var(--font-mono); width: 48px; text-align: center; }
.app-name { font-weight: 600; }
.matrix td.app-name, .matrix th:first-child {
  position: sticky; left: 0; z-index: 2;
  background: var(--color-bg-secondary);
  border-right: 1px solid var(--color-border-default);
}
.matrix th:first-child { background: var(--color-bg-tertiary); z-index: 3; }
.matrix tr:hover td.app-name { background: var(--color-bg-tertiary); }
.vendor { color: var(--color-text-secondary); font-size: var(--text-sm); }
.num { font-family: var(--font-mono); color: var(--color-text-secondary); }
.tag { font-size: var(--text-xs); padding: 2px 8px; border-radius: var(--radius-full); font-weight: 600; }
.tag-paid { background: rgba(88,166,255,0.15); color: var(--color-info); }
.tag-free { background: rgba(63,185,80,0.15); color: var(--color-success); }
.tag-hybrid { background: rgba(210,153,34,0.15); color: var(--color-warning); }
.score-cell { width: 150px; }
.score-wrap { display: flex; align-items: center; gap: var(--space-2); }
.score-track { width: 90px; height: 8px; border-radius: var(--radius-full); background: var(--color-bg-tertiary); overflow: hidden; flex-shrink: 0; }
.score-bar { height: 100%; border-radius: var(--radius-full); background: linear-gradient(90deg, #b87316, var(--color-accent)); min-width: 2px; }
.score-num { font-family: var(--font-mono); font-weight: 700; color: var(--color-accent); }
.cc { text-align: center; font-family: var(--font-mono); padding: var(--space-2) var(--space-2); }
.cc-us { color: var(--color-accent); }
.cell { text-align: center; font-family: var(--font-mono); font-size: var(--text-sm); padding: var(--space-1) var(--space-2); }
.miss { color: var(--color-text-muted); }
.r10  { background: rgba(232,163,61,0.45); color: #fff; font-weight: 700; }
.r30  { background: rgba(232,163,61,0.28); color: var(--color-text-primary); }
.r60  { background: rgba(232,163,61,0.16); }
.r120 { background: rgba(232,163,61,0.08); color: var(--color-text-secondary); }
.r200 { color: var(--color-text-muted); }
.sc80 { background: rgba(232,163,61,0.40); color: #fff; font-weight: 700; }
.sc60 { background: rgba(232,163,61,0.24); }
.sc40 { background: rgba(232,163,61,0.14); }
.sc20 { background: rgba(232,163,61,0.06); color: var(--color-text-secondary); }
.trend-up { color: var(--color-success); font-weight: 700; }
.trend-down { color: var(--color-danger); font-weight: 700; }
.trend-flat { color: var(--color-text-muted); }
.legend { display: flex; gap: var(--space-4); margin-top: var(--space-3); font-size: var(--text-xs); color: var(--color-text-secondary); align-items: center; flex-wrap: wrap; }
.legend .sw { display: inline-block; width: 14px; height: 14px; border-radius: var(--radius-sm); vertical-align: -2px; margin-right: 4px; }
.notes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr)); gap: var(--space-4); }
.note-card {
  background: var(--color-bg-secondary); border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg); padding: var(--space-4) var(--space-6);
  transition: border-color var(--duration-fast) var(--easing-default);
}
.note-card:hover { border-color: var(--color-border-default); }
.note-head { display: flex; align-items: center; gap: var(--space-2); margin-bottom: var(--space-2); }
.note-name { font-weight: 600; font-size: var(--text-lg); }
.note-score { margin-left: auto; font-family: var(--font-mono); color: var(--color-accent); font-weight: 700; }
.note-body { color: var(--color-text-secondary); font-size: var(--text-sm); }
.note-body b { color: var(--color-text-primary); font-family: var(--font-mono); }
.method {
  background: var(--color-bg-secondary); border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg); padding: var(--space-6);
  font-size: var(--text-sm); color: var(--color-text-secondary);
}
.method h3 { color: var(--color-text-primary); font-size: var(--text-base); margin: var(--space-4) 0 var(--space-2); }
.method h3:first-child { margin-top: 0; }
.method ul { padding-left: 20px; }
.method li { margin-bottom: var(--space-1); }
.method code { font-family: var(--font-mono); background: var(--color-bg-tertiary); padding: 1px 6px; border-radius: var(--radius-sm); font-size: var(--text-xs); }
.warn-box {
  border: 1px solid var(--color-warning); border-radius: var(--radius-md);
  background: rgba(210,153,34,0.08); color: var(--color-warning);
  padding: var(--space-3) var(--space-4); margin-top: var(--space-4); font-size: var(--text-sm);
}
.warn-line { color: var(--color-danger); font-size: var(--text-sm); margin-top: var(--space-3); }
footer { color: var(--color-text-muted); font-size: var(--text-xs); text-align: center; padding: var(--space-8) 0; border-top: 1px solid var(--color-border-subtle); }
.index-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--space-4); }
.index-card {
  display: block; text-decoration: none; color: var(--color-text-primary);
  background: var(--color-bg-secondary); border: 1px solid var(--color-border-subtle);
  border-radius: var(--radius-lg); padding: var(--space-6);
  transition: border-color var(--duration-fast) var(--easing-default), transform var(--duration-fast) var(--easing-default);
}
.index-card:hover { border-color: var(--color-accent); transform: translateY(-2px); }
.index-card .t { font-weight: 600; font-size: var(--text-lg); margin-bottom: var(--space-1); }
.index-card .d { color: var(--color-text-secondary); font-size: var(--text-sm); font-family: var(--font-mono); }
.index-card.featured { border-color: var(--color-accent); background: var(--color-accent-subtle); }
"""

METHOD_HTML = """
<section>
  <h2>方法论与数据来源</h2>
  <div class="method">
    <h3>数据来源</h3>
    <ul>
      <li><b>iTunes RSS API</b>：<code>itunes.apple.com/{国家码}/rss/topfreeapplications|topgrossingapplications/limit=200/genre=6016/json</code>，苹果官方免费接口，Entertainment分类</li>
      <li>Google Play免费榜：本版未接入（可用开源库 <code>google-play-scraper</code> 补齐，接入后权重调整为 畅销65/iOS免费20/GP免费15）</li>
      <li>行业收入/下载背景数据：需人工摘录Sensor Tower、点点数据等公开报告，本报告不含</li>
    </ul>
    <h3>计分方法</h3>
    <ul>
      <li>单点得分 = 榜单权重 × 国家权重 × (201 - 排名) / 200</li>
      <li>榜单权重：iOS畅销 0.65、iOS免费 0.35</li>
      <li>国家权重：US=6.0 ｜ 西方发达/T2市场 = 1.0 ｜ 日本0.4 ｜ 韩国/T3市场 = 0.3</li>
      <li>所有产品得分按当期最高分归一化为0-100</li>
    </ul>
    <h3>已知局限</h3>
    <ul>
      <li>榜单是"势能"信号（新增下载+当日IAP流水），不是绝对收入。订阅续费、网页端充值不进榜单</li>
      <li>免费模式产品（如Melolo）靠广告变现，畅销榜天然弱势，看免费榜矩阵更有意义</li>
      <li>产品匹配按商店名称子串，马甲包/本地化改名可能漏匹配，发现后在清单中补match项</li>
    </ul>
  </div>
</section>
"""


def page_shell(title, body):
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>{PAGE_CSS}</style>
</head>
<body>
<div class="container">
{body}
</div>
</body>
</html>"""


def rank_cell(rank):
    if rank is None:
        return '<td class="cell miss">–</td>'
    if rank <= 10:
        cls = "r10"
    elif rank <= 30:
        cls = "r30"
    elif rank <= 60:
        cls = "r60"
    elif rank <= 120:
        cls = "r120"
    else:
        cls = "r200"
    return f'<td class="cell {cls}">{rank}</td>'


def build_matrix(rankings, feed_key, ordered_names):
    header = "".join(
        f'<th class="cc {"cc-us" if cc == "us" else ""}" title="权重{w}">{cn}</th>'
        for cc, cn, w, _ in COUNTRIES)
    rows = []
    for name in ordered_names:
        cells = "".join(rank_cell(rankings[feed_key].get(cc, {}).get(name)) for cc, _, _, _ in COUNTRIES)
        rows.append(f'<tr><td class="app-name">{name}</td>{cells}</tr>')
    return header, "\n".join(rows)


def matrix_section(rankings, ordered_names):
    gh, gr = build_matrix(rankings, "grossing", ordered_names)
    fh, fr = build_matrix(rankings, "free", ordered_names)
    return f"""
<section>
  <h2>iOS畅销榜排名矩阵（Entertainment Top200）</h2>
  <p class="desc">数字为该产品在该国畅销榜的排名，– 表示未进Top200。颜色越深排名越靠前。</p>
  <div class="table-wrap">
  <table class="matrix">
    <thead><tr><th>产品</th>{gh}</tr></thead>
    <tbody>{gr}</tbody>
  </table>
  </div>
  <div class="legend">
    <span><span class="sw" style="background:rgba(232,163,61,0.45)"></span>Top10</span>
    <span><span class="sw" style="background:rgba(232,163,61,0.28)"></span>11-30</span>
    <span><span class="sw" style="background:rgba(232,163,61,0.16)"></span>31-60</span>
    <span><span class="sw" style="background:rgba(232,163,61,0.08)"></span>61-120</span>
    <span>121-200 无底色</span>
  </div>
</section>

<section>
  <h2>iOS免费榜排名矩阵（Entertainment Top200）</h2>
  <p class="desc">免费榜反映新增下载势能，是买量投放力度的间接信号。</p>
  <div class="table-wrap">
  <table class="matrix">
    <thead><tr><th>产品</th>{fh}</tr></thead>
    <tbody>{fr}</tbody>
  </table>
  </div>
</section>"""


def score_rank_table(rankings, listed):
    medal = {1: "🥇", 2: "🥈", 3: "🥉"}
    rows = []
    for i, (name, score) in enumerate(listed, 1):
        app = APPS_BY[name]
        st = app_stats(rankings, name)
        bg = f'#{st["best_gross"]} ({st["best_gross_cc"]})' if st["best_gross"] else "–"
        bf = f'#{st["best_free"]} ({st["best_free_cc"]})' if st["best_free"] else "–"
        rows.append(f"""<tr>
<td class="pos">{medal.get(i, i)}</td>
<td class="app-name">{name}</td>
<td class="vendor">{app["vendor"]}</td>
<td><span class="tag {MODEL_CLS[app["model"]]}">{app["model"]}</span></td>
<td class="num">{st["gross_countries"]}/{len(COUNTRIES)}</td>
<td class="num">{st["free_countries"]}/{len(COUNTRIES)}</td>
<td class="num">{bg}</td>
<td class="num">{bf}</td>
<td class="score-cell"><div class="score-wrap"><div class="score-track"><div class="score-bar" style="width:{score}%"></div></div><span class="score-num">{score}</span></div></td>
</tr>""")
    return "".join(rows)


def notes_section(rankings, listed, top_n=8):
    notes = []
    for name, score in listed[:top_n]:
        st = app_stats(rankings, name)
        parts = []
        if st["best_gross"]:
            parts.append(f'畅销榜最佳排名 <b>#{st["best_gross"]}</b>（{st["best_gross_cc"]}），共{st["gross_countries"]}国上榜')
        if st["best_free"]:
            parts.append(f'免费榜最佳 <b>#{st["best_free"]}</b>（{st["best_free_cc"]}），{st["free_countries"]}国上榜')
        if not parts:
            continue
        notes.append(f"""<div class="note-card">
<div class="note-head"><span class="note-name">{name}</span><span class="tag {MODEL_CLS[APPS_BY[name]["model"]]}">{APPS_BY[name]["model"]}</span><span class="note-score">{score}分</span></div>
<div class="note-body">{'；'.join(parts)}。</div>
</div>""")
    return "".join(notes)


# ---------------- 日报 ----------------

def render_daily(snap):
    rankings, scores, failed = snap["rankings"], snap["scores"], snap.get("failed", [])
    date_cn = snap["date"]
    date_tag = date_cn.replace("-", "")
    ranked = sorted(scores.items(), key=lambda kv: -kv[1])
    listed = [(n, s) for n, s in ranked if s > 0]
    hidden = len(ranked) - len(listed)
    ordered_names = [n for n, _ in listed]
    total_points = sum(len(v) for feed in rankings.values() for v in feed.values())
    fail_note = f'<p class="warn-line">本期抓取失败的榜单：{"、".join(failed)}（该榜按空数据计）。</p>' if failed else ""

    body = f"""
<header>
  <span class="report-tag">DRAMA DAILY · {date_tag}</span>
  <h1>短剧出海竞品日报</h1>
  <p class="sub">数据日期 {date_cn} ｜ iOS免费榜 + iOS畅销榜（Entertainment分类 Top200）｜ 覆盖{len(COUNTRIES)}国 ｜ 免费 + 付费短剧App</p>
  <p class="nav-links"><a href="../index.html">← 报告中心</a></p>
</header>

<div class="kpi-row">
  <div class="kpi"><div class="v">{len(APPS)}</div><div class="k">追踪产品数</div></div>
  <div class="kpi"><div class="v">{len(listed)}</div><div class="k">当日上榜产品数</div></div>
  <div class="kpi"><div class="v">{len(COUNTRIES)}</div><div class="k">覆盖国家/地区</div></div>
  <div class="kpi"><div class="v">{total_points}</div><div class="k">采集到的排名数据点</div></div>
</div>

<section>
  <h2>综合得分排名</h2>
  <p class="desc">口径：iOS畅销65% + iOS免费35%，按国家权重加权（US=6.0，西方发达/T2=1.0，日本0.4，韩国/T3=0.3），归一化为0-100分。{f"{hidden}款产品当日全榜未命中，自动隐藏。" if hidden else ""}</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th>#</th><th>产品</th><th>厂商</th><th>模式</th><th>畅销上榜国</th><th>免费上榜国</th><th>畅销最佳</th><th>免费最佳</th><th>综合分</th></tr></thead>
    <tbody>{score_rank_table(rankings, listed)}</tbody>
  </table>
  </div>
  <div class="warn-box">⚠️ 本排名基于榜单信号，不代表真实收入排名。短剧产品老用户自动续费占真实收入比重较大，而续费不产生下载/畅销榜新增信号。</div>
  {fail_note}
</section>

{matrix_section(rankings, ordered_names)}

<section>
  <h2>当日头部产品动态</h2>
  <div class="notes-grid">{notes_section(rankings, listed)}</div>
</section>

{METHOD_HTML}

<footer>短剧出海竞品日报 · 数据快照 data/rankings_{date_tag}.json · 参考版式 narku.com/archives/2068</footer>"""
    return page_shell(f"短剧出海竞品日报 · {date_cn}", body)


# ---------------- 周报 ----------------

def score_heat_cell(score):
    if score is None:
        return '<td class="cell miss">–</td>'
    if score >= 80:
        cls = "sc80"
    elif score >= 60:
        cls = "sc60"
    elif score >= 40:
        cls = "sc40"
    else:
        cls = "sc20"
    return f'<td class="cell {cls}">{score}</td>'


def render_weekly(snaps):
    """snaps: 按日期升序的快照列表(1-7天)"""
    latest = snaps[-1]
    dates = [s["date"] for s in snaps]
    start_cn, end_cn = dates[0], dates[-1]
    end_tag = end_cn.replace("-", "")

    # 周均分与趋势
    week = {}
    for app in APPS:
        name = app["name"]
        daily = [s["scores"].get(name, 0.0) for s in snaps]
        avg = round(sum(daily) / len(daily), 1)
        diff = round(daily[-1] - daily[0], 1)
        week[name] = {"daily": daily, "avg": avg, "latest": daily[-1], "diff": diff}

    listed = sorted([(n, w) for n, w in week.items() if w["avg"] > 0],
                    key=lambda kv: -kv[1]["avg"])
    ordered_names = [n for n, _ in listed]

    def trend_html(diff):
        if len(snaps) < 2:
            return '<span class="trend-flat">–</span>'
        if diff > 2:
            return f'<span class="trend-up">📈 +{diff}</span>'
        if diff < -2:
            return f'<span class="trend-down">📉 {diff}</span>'
        return f'<span class="trend-flat">→ {diff:+}</span>'

    medal = {1: "🥇", 2: "🥈", 3: "🥉"}
    rank_rows = []
    for i, (name, w) in enumerate(listed, 1):
        app = APPS_BY[name]
        st = app_stats(latest["rankings"], name)
        bg = f'#{st["best_gross"]} ({st["best_gross_cc"]})' if st["best_gross"] else "–"
        rank_rows.append(f"""<tr>
<td class="pos">{medal.get(i, i)}</td>
<td class="app-name">{name}</td>
<td class="vendor">{app["vendor"]}</td>
<td><span class="tag {MODEL_CLS[app["model"]]}">{app["model"]}</span></td>
<td class="score-cell"><div class="score-wrap"><div class="score-track"><div class="score-bar" style="width:{w["avg"]}%"></div></div><span class="score-num">{w["avg"]}</span></div></td>
<td class="num">{w["latest"]}</td>
<td>{trend_html(w["diff"])}</td>
<td class="num">{st["gross_countries"]}/{len(COUNTRIES)}</td>
<td class="num">{bg}</td>
</tr>""")

    # 每日得分趋势矩阵
    date_heads = "".join(f'<th class="cc">{d[5:]}</th>' for d in dates)
    trend_rows = []
    for name in ordered_names:
        cells = "".join(score_heat_cell(s if s > 0 else None) for s in week[name]["daily"])
        trend_rows.append(f'<tr><td class="app-name">{name}</td>{cells}<td>{trend_html(week[name]["diff"])}</td></tr>')

    total_points = sum(
        len(v) for s in snaps for feed in s["rankings"].values() for v in feed.values())

    body = f"""
<header>
  <span class="report-tag">DRAMA WEEKLY · {end_tag}</span>
  <h1>短剧出海竞品周报</h1>
  <p class="sub">周期 {start_cn} ~ {end_cn}（{len(snaps)}天数据）｜ iOS免费榜 + iOS畅销榜（Entertainment Top200）｜ 覆盖{len(COUNTRIES)}国 ｜ 免费 + 付费短剧App</p>
  <p class="nav-links"><a href="../index.html">← 报告中心</a></p>
</header>

<div class="kpi-row">
  <div class="kpi"><div class="v">{len(snaps)}</div><div class="k">本周采集天数</div></div>
  <div class="kpi"><div class="v">{len(listed)}</div><div class="k">本周上榜产品数</div></div>
  <div class="kpi"><div class="v">{len(COUNTRIES)}</div><div class="k">覆盖国家/地区</div></div>
  <div class="kpi"><div class="v">{total_points}</div><div class="k">本周排名数据点</div></div>
</div>

<section>
  <h2>本周综合得分排名（按周均分）</h2>
  <p class="desc">周均分 = 本周各日综合分的平均值；周趋势 = 最新一日与本周首日的分差（±2以内视为持平）。</p>
  <div class="table-wrap">
  <table>
    <thead><tr><th>#</th><th>产品</th><th>厂商</th><th>模式</th><th>周均分</th><th>最新分</th><th>周趋势</th><th>畅销上榜国</th><th>畅销最佳</th></tr></thead>
    <tbody>{"".join(rank_rows)}</tbody>
  </table>
  </div>
  <div class="warn-box">⚠️ 本排名基于榜单信号，不代表真实收入排名。短剧产品老用户自动续费占真实收入比重较大，而续费不产生下载/畅销榜新增信号。</div>
</section>

<section>
  <h2>每日综合得分趋势</h2>
  <p class="desc">每格为该产品当日综合分（0-100），颜色越深得分越高。</p>
  <div class="table-wrap">
  <table class="matrix">
    <thead><tr><th>产品</th>{date_heads}<th>周趋势</th></tr></thead>
    <tbody>{"".join(trend_rows)}</tbody>
  </table>
  </div>
</section>

{matrix_section(latest["rankings"], ordered_names).replace("排名矩阵（Entertainment Top200）", f"排名矩阵（{end_cn}，Entertainment Top200）")}

<section>
  <h2>本周头部产品动态</h2>
  <div class="notes-grid">{notes_section(latest["rankings"], [(n, w["avg"]) for n, w in listed])}</div>
</section>

{METHOD_HTML}

<footer>短剧出海竞品周报 · 周期 {start_cn} ~ {end_cn} · 参考版式 narku.com/archives/2068</footer>"""
    return page_shell(f"短剧出海竞品周报 · {end_cn}", body)


# ---------------- 索引页 ----------------

def render_index():
    def scan(subdir, prefix):
        d = DOCS_DIR / subdir
        if not d.exists():
            return []
        items = []
        for p in sorted(d.glob(f"{prefix}_*.html"), reverse=True):
            tag = p.stem.replace(f"{prefix}_", "")
            if len(tag) == 8 and tag.isdigit():
                date_cn = f"{tag[:4]}-{tag[4:6]}-{tag[6:]}"
                items.append((date_cn, f"{subdir}/{p.name}"))
        return items

    weeklies = scan("weekly", "drama_weekly")
    dailies = scan("daily", "drama_daily")
    has_latest_weekly = (DOCS_DIR / "weekly" / "latest.html").exists()

    featured = ""
    if has_latest_weekly:
        featured += '<a class="index-card featured" href="weekly/latest.html"><div class="t">📊 最新周报（滚动7天）</div><div class="d">每日自动更新</div></a>'
    if dailies:
        featured += f'<a class="index-card featured" href="{dailies[0][1]}"><div class="t">📅 最新日报</div><div class="d">{dailies[0][0]}</div></a>'

    weekly_cards = "".join(
        f'<a class="index-card" href="{href}"><div class="t">周报</div><div class="d">截至 {d}</div></a>'
        for d, href in weeklies) or '<p class="desc">暂无归档周报（每周一自动归档上一周）。</p>'
    daily_cards = "".join(
        f'<a class="index-card" href="{href}"><div class="t">日报</div><div class="d">{d}</div></a>'
        for d, href in dailies) or '<p class="desc">暂无日报。</p>'

    body = f"""
<header>
  <span class="report-tag">DRAMA REPORTS</span>
  <h1>短剧出海竞品报告中心</h1>
  <p class="sub">每日自动采集 iOS 免费榜 + 畅销榜（41国，Entertainment Top200），追踪{len(APPS)}款免费/付费短剧App。</p>
</header>

<section>
  <h2>快速入口</h2>
  <div class="index-grid">{featured}</div>
</section>

<section>
  <h2>周报归档</h2>
  <div class="index-grid">{weekly_cards}</div>
</section>

<section>
  <h2>日报归档</h2>
  <div class="index-grid">{daily_cards}</div>
</section>

<footer>数据来源 iTunes RSS API · 自动更新 · 参考版式 narku.com/archives/2068</footer>"""
    return page_shell("短剧出海竞品报告中心", body)


def write_index():
    DOCS_DIR.mkdir(exist_ok=True)
    (DOCS_DIR / "index.html").write_text(render_index(), encoding="utf-8")
