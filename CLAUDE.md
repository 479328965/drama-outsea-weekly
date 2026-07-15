# 短剧出海竞品周报项目

追踪免费+付费短剧出海App在应用商店榜单的表现，生成HTML竞品周报。参考对象：narku.com/archives/2068 的付费短剧周报。

## 目录结构

```
scripts/
  report_lib.py   # 共用库：国家/App清单、抓取、计分、HTML渲染
  daily.py        # 每日采集+日报（--from-snapshot 跳过抓取重渲染）
  weekly.py       # 周报：滚动7天latest.html每日更新，周一归档上周
data/             # 原始榜单JSON快照，rankings_YYYYMMDD.json
docs/             # GitHub Pages发布目录
  index.html      # 报告中心索引页
  daily/          # 日报 drama_daily_YYYYMMDD.html
  weekly/         # latest.html（滚动） + 归档 drama_weekly_YYYYMMDD.html
.github/workflows/collect.yml  # 每天UTC 01:30（北京09:30）自动采集并commit
CLAUDE.md
```

## 部署

- GitHub Actions每日自动跑 daily.py + weekly.py，产物commit回仓库
- GitHub Pages从main分支 /docs 目录发布
- 时间统一按北京时间（report_lib.today_bjt），周一归档上一周周报

## 数据来源（零成本，不依赖付费账号）

- **iTunes RSS API**：`https://itunes.apple.com/{cc}/rss/topfreeapplications/limit=200/genre=6016/json`（免费榜）和 `topgrossingapplications`（畅销榜），genre=6016为Entertainment分类
- Google Play免费榜：v1未接入（需node环境跑google-play-scraper），报告里注明口径
- 行业背景数据（收入/下载量）：人工摘录公开报告（Sensor Tower等），标注出处

## 评分口径

- 榜单权重：iOS畅销65% + iOS免费35%（接入GP后改为 畅销65/iOS免费20/GP免费15）
- 覆盖41国：西方发达18国+日韩（T1）、台港新/巴墨/中东/葡波（T2）、东南亚/拉美/土印南非埃及（T3）
- 国家权重：US=6.0，日本0.4，韩国0.3，其余T1/T2=1.0，T3=0.3
- 单点得分 = 国家权重 × 榜单权重 × (201-排名)/200，汇总后按当日最高分归一化为0-100
- 报告必须带局限性声明：榜单排名不代表真实收入（老用户自动续费不产生榜单信号）

## App清单schema

`scripts/`内维护清单，每款App字段：`name`（展示名）、`match`（商店名匹配子串列表，大小写不敏感）、`vendor`（厂商）、`model`（付费/免费/混合）。新增竞品只改清单，不动抓取逻辑。

## HTML版式约定

- 单文件HTML，无外部依赖（不引CDN），可直接双击打开
- 遵循 `~/.claude/rules/design_template.md` 的CSS变量体系（色彩/字号/间距/圆角）
- 深色主题数据看板风格，等宽字体展示排名数字
- 板块顺序：核心摘要 → 综合排名表 → 免费榜矩阵 → 畅销榜矩阵 → 产品动态 → 方法论与数据来源声明

## 踩坑记录

（暂无，遇坑追加）
