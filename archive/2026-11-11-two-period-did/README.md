# 归档：两期DID与模型数值例（原11月11日稿）

本目录由 `2026-11-11/02-composition/` 迁入，保留此前的两期DID、Welch推论及13页结果稿。当前主分析为[月度DID](../../2026-11-11/analysis/README.md)，对应[11月4日的方法稿](../../2026-11-04/README.md)。

这套13页稿承接[11月4日的模型与统计方法](../../2026-11-04/README.md)，用标准DID的交互项系数表述早晚生效县的平均变化差。数值沿用原稿；分周和回归表述调整都没有重新估计。

## 旧稿与配套文件

- [slides.pdf](slides.pdf)、[slides.html](slides.html)、[slides.md](slides.md)：PDF、浏览器翻页版和可编辑源稿。
- [speaker_notes.md](speaker_notes.md)：13页日文逐页讲稿，追问内容单列为“质疑用”。
- [methods.md](methods.md)、[sources.md](sources.md)：计算补充、理论方法入口及来源记录。

| 页码 | 内容 |
|---|---|
| 1–4 | 承接本周问题、数据口径、分组与模型的条件性预测 |
| 5 | 假定参数的模型数值例，与实证估计区分 |
| 6–7 | 指标回顾、标准DID回归、群平均与交互项系数的对应 |
| 8–10 | 月别趋势、兼职主检验、总量与构成结果 |
| 11–13 | 基准期敏感性、结果整理与参考文献 |

## 计算与既有材料

- `analysis.py`、`analysis.ipynb`、`build_notebook.py`、`tests/`、`results/`：从原目录移入的分析程序、已执行notebook、单元测试和结果，内容未改。
- `assets/`：既有结果图、教学区间图和日文字体。
- `check_analysis.py`：从旧交付验证器分离的统计复核入口，按需要在下周执行；不是本周导出流程的一部分。
- `verification.json`、`evidence/ledger.json`：原分析的记录；`evidence/original_20slides/`：拆分前的20页渲染与交付记录。
- `video/`：原约11分钟完整讲解视频，包含数值和结果，页码对应拆分前的20页稿。
- `planning/`：两周的旧TODO快照，链接已更新；其中的Welch方案和完成状态属于旧计划。当前待办见各日期README。
- `verification_log.json`：归档前的交付检查记录；新的交付检查报告写入仓库 `.cache/delivery-check/`。

正文使用经济学和统计学术语，直接报告DID估计值、置信区间和模型对应；解释边界及方法追问放在讲稿的“质疑用”。标准DID式使用相同样本和县等权，沿用既有数值及Welch推论。各结果的95%置信区间均含0。

## 查看与复现

PDF和HTML可直接打开。需要重新提取旧讲稿或检查文件时，在本目录运行：

```bash
python ../../scripts/build_teaching.py slides.md
python ../../scripts/check_delivery.py
```

共用脚本的默认操作和依赖见[scripts/README.md](../../scripts/README.md)。归档源稿、PDF、HTML、数值结果、图表和视频在本次整理中未重新生成。

需要重新核算时，在本目录用装有 `requirements.txt` 所列依赖的环境执行 `python check_analysis.py`；完整重建仍使用 `analysis.py` 与 `build_notebook.py`，会写结果，因此不包含在本次拆分工作中。
