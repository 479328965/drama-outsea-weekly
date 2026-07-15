# -*- coding: utf-8 -*-
"""
每日采集 + 日报生成
用法:
  python scripts/daily.py                  # 抓取今日数据并生成日报
  python scripts/daily.py --from-snapshot  # 不抓取, 用已有的今日快照重渲染日报
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import report_lib as lib


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    today = lib.today_bjt()
    tag = today.strftime("%Y%m%d")
    snap_path = lib.DATA_DIR / f"rankings_{tag}.json"

    if "--from-snapshot" in sys.argv:
        if not snap_path.exists():
            print(f"快照不存在: {snap_path}")
            sys.exit(1)
        snap = json.loads(snap_path.read_text(encoding="utf-8"))
    else:
        print(f"开始抓取 {len(lib.COUNTRIES)}国 x 2榜 ...")
        rankings, failed = lib.collect()
        scores = lib.compute_scores(rankings)
        snap = {"date": today.strftime("%Y-%m-%d"),
                "countries": [c[0] for c in lib.COUNTRIES],
                "rankings": rankings, "scores": scores, "failed": failed}
        lib.DATA_DIR.mkdir(exist_ok=True)
        snap_path.write_text(json.dumps(snap, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"快照已存: {snap_path}")

    out_dir = lib.DOCS_DIR / "daily"
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"drama_daily_{tag}.html"
    out.write_text(lib.render_daily(snap), encoding="utf-8")
    lib.write_index()
    print(f"日报: {out}")
    top5 = sorted(snap["scores"].items(), key=lambda kv: -kv[1])[:5]
    for n, s in top5:
        print(f"  {n}: {s}")


if __name__ == "__main__":
    main()
