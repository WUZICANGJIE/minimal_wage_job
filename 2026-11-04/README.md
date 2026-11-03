# 2026-11-04：模型与统计方法（課題3）

当前发表稿共15页，介绍模型、假说与县×月面板DID方法。第14页以パート求人的主假说检验为中心，通过P与N的系数比较解释影响是否偏向パート，求人合计作为辅助指标。实际估计与[平行趋势的详细说明](../2026-11-11/analysis/parallel_trends.md)放在[下周材料](../2026-11-11/README.md)。旧两期DID稿和模型数值例已移入[归档](../archive/2026-11-11-two-period-did/README.md)。

## 发表材料

- [slides.pdf](slides.pdf)：发表用PDF。
- [slides.html](slides.html)：浏览器翻页版，需与 `assets/` 一起保存。
- [slides.md](slides.md)：可编辑的Marp源稿。
- [speaker_notes.md](speaker_notes.md)：15页日文讲稿；每页区分日常讲解和“质疑用”补充。
- [methods.md](methods.md)：模型推导与统计方法；[sources.md](sources.md)：来源入口。

## 内容顺序

| 页码 | 内容 |
|---|---|
| 1–3 | 研究问题、求人口径与早晚生效比较规则 |
| 4–7 | 企业利润、CES、一阶条件、相对需求 |
| 8–9 | 成本最小化与单位费用推导、总费用CY与最优生产量 |
| 10 | 劳动需求的替代效应与规模效应 |
| 11–12 | 採用与求人的对应、指标定义 |
| 13–14 | 县与月份固定效应的月度DID、パート求人的主假说检验、P与N的系数比较及含意 |
| 15 | 参考文献与数据 |

理论中的生产量统一记为大写 Y，回归的被解释变量记为小写 y。日文材料统一使用“生産量”。正文采用经济学发表的专业术语，并配简短解释；保留模型推导、DID式和系数解释。口径限制、识别条件及统计细节集中到讲稿的“质疑用”和方法文档。

主回归分别估计四个指标：P、N、T的求人同比对数变化，R为P/N的同比对数变化。每县每月一行，使用2025年1–9月和11月，排除移行月10月及11月生效县。相同样本、月份和县等权下，主DID点估计仍对应原来的平均变化差。推论统一使用县聚类CRV1及基于县数的自由度。月度系数图与事前趋势检验下周详细说明。

## 重新导出

在本目录运行，使用本机已有Python、Marp和Chrome。`CHROME_PATH` 可指定本机浏览器路径。

```bash
python ../scripts/build_teaching.py slides.md
npx --yes @marp-team/marp-cli@4.5.1 slides.md --no-config --html --allow-local-files --pdf -o slides.pdf
npx --yes @marp-team/marp-cli@4.5.1 slides.md --no-config --html -o slides.html
python ../scripts/check_delivery.py
```

讲稿脚本提取发言备注及质疑补充；交付检查验证结构、PDF文本和保留文件哈希，不执行统计估计。检查需要Poppler的 `pdfinfo` 和 `pdftotext`，报告写入仓库的 `.cache/delivery-check/verification.json`；导出后还需目视核对公式与版面。

## 待完成

- 组员试讲，确认模型与统计方法的讲解时长。
