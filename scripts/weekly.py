# -*- coding: utf-8 -*-
"""
周报生成: 汇总最近7天的数据快照
用法: python scripts/weekly.py
行为:
  - 每次运行都重新生成 docs/weekly/latest.html (滚动最近7天, 每日更新)
  - 北京时间周一运行时, 额外归档上一周(周一~周日)为 docs/weekly/drama_weekly_YYYYMMDD.html
    (文件名日期 = 上周日, 即该周报覆盖周期的最后一天)
"""
import sys
from datetime import timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import report_lib as lib


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    today = lib.today_bjt()
    out_dir = lib.DOCS_DIR / "weekly"
    out_dir.mkdir(parents=True, exist_ok=True)

    # 滚动7天周报(每日更新)
    snaps = lib.load_snapshots(days=7)
    if not snaps:
        print("没有可用的数据快照, 先运行 daily.py")
        sys.exit(1)
    latest = out_dir / "latest.html"
    latest.write_text(lib.render_weekly(snaps), encoding="utf-8")
    print(f"滚动周报({snaps[0]['date']} ~ {snaps[-1]['date']}, {len(snaps)}天): {latest}")

    # 周一归档上一周
    if today.weekday() == 0:
        last_sunday = today - timedelta(days=1)
        week_snaps = lib.load_snapshots(days=7, end_date=last_sunday)
        if week_snaps:
            tag = last_sunday.strftime("%Y%m%d")
            archive = out_dir / f"drama_weekly_{tag}.html"
            archive.write_text(lib.render_weekly(week_snaps), encoding="utf-8")
            print(f"归档上周周报: {archive}")

    lib.write_index()


if __name__ == "__main__":
    main()
