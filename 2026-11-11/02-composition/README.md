# 下周：计算结果与解释（課題4，11月11日）

这套13页稿承接[11月4日的模型与统计方法](../../2026-11-04/02-composition/README.md)，用标准DID的交互项系数表述早晚生效县的平均变化差。数值沿用原稿；分周和回归表述调整都没有重新估计。

## 发表材料

- [slides.pdf](slides.pdf)、[slides.html](slides.html)、[slides.md](slides.md)：PDF、浏览器翻页版和可编辑源稿。
- [speaker_notes.md](speaker_notes.md)：13页日文逐页讲稿。
- [methods.md](methods.md)、[sources.md](sources.md)：计算补充、理论方法入口及来源记录。

| 页码 | 内容 |
|---|---|
| 1–4 | 承接本周问题、数据口径、分组与模型的条件性预测 |
| 5 | 假定参数的模型数值例，与实证估计区分 |
| 6–7 | 指标回顾、标准DID回归、群平均与交互项系数的对应 |
| 8–10 | 月别趋势、兼职主检验、总量与构成结果 |
| 11–13 | 基准期敏感性、结论与局限、参考文献 |

## 计算与既有材料

- `analysis.py`、`analysis.ipynb`、`build_notebook.py`、`tests/`、`results/`：从原目录移入的分析程序、已执行notebook、单元测试和结果，内容未改。
- `assets/`：既有结果图、教学区间图和日文字体。
- `check_analysis.py`：从旧交付验证器分离的统计复核入口，按需要在下周执行；不是本周导出流程的一部分。
- `verification.json`、`evidence/ledger.json`：原分析的记录；`evidence/original_20slides/`：拆分前的20页渲染与交付记录。
- `video/`：原约11分钟完整讲解视频，包含数值和结果，页码对应拆分前的20页稿。

各县等权、两期样本相同、只含截距、Treat、Post及交互项的标准DID式，其交互项系数等于原来的平均变化差，因此直接沿用既有数值。推论基于每县的前后差分，不把同一县的两期当成独立观测；标准误、Welch自由度、左尾p值和双侧95%区间均维持原口径。原稿结果的区间均含0，不能确认负差，也不能排除总量收缩。非兼职不是未处理对照，求人不等于採用或雇用。

## 导出两周材料（不重新计算）

在本目录运行，使用本机已有Python、Marp和Chrome。`CHROME_PATH` 可指定本机浏览器路径。

```bash
python build_teaching.py
npx --yes @marp-team/marp-cli@4.5.1 slides.md --no-config --html --allow-local-files --pdf -o slides.pdf
npx --yes @marp-team/marp-cli@4.5.1 slides.md --no-config --html -o slides.html
python check_delivery.py
```

本周稿需另在其目录导出。`build_teaching.py` 默认更新两套讲稿，仅用Python标准库，不读取结果CSV或重建图表。`check_delivery.py` 检查两套稿的结构、PDF文本、资源路径及保留文件哈希，需要Poppler的 `pdfinfo` 和 `pdftotext`。它不执行统计估计，也不能替代导出后的视觉检查。

需要重新核算时，在本目录用装有 `requirements.txt` 所列依赖的环境执行 `python check_analysis.py`；完整重建仍使用 `analysis.py` 与 `build_notebook.py`，会写结果，因此不包含在本次拆分工作中。
