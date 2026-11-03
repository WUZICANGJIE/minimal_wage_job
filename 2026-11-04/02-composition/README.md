# 本周：模型与统计方法（課題3，11月4日）

本周稿共17页，正文用包含Treat、Post及交互项的标准DID回归说明统计方法，县内差分、标准误与检验公式放在末尾附录。实际数值、模型数值例、结果图、结论及计算材料见[11月11日的課題4](../../2026-11-11/02-composition/README.md)。

## 发表材料

- [slides.pdf](slides.pdf)：发表用PDF。
- [slides.html](slides.html)：浏览器翻页版，需与 `assets/` 一起保存。
- [slides.md](slides.md)：可编辑的Marp源稿。
- [speaker_notes.md](speaker_notes.md)：17页日文讲稿，与slides内备注一致。
- [methods.md](methods.md)：模型推导与统计方法；[sources.md](sources.md)：来源入口。

## 内容顺序

| 页码 | 内容 |
|---|---|
| 1–4 | 研究问题、文献定位、求人口径与早晚生效比较规则 |
| 5–10 | 企业利润、CES、一阶条件、相对需求、规模与替代效应 |
| 11–12 | 採用与求人的对应、指标定义 |
| 13–14 | 标准DID回归、两组两期均值与交互项系数、主假说 |
| 15–16 | 下周计算安排、解释条件与参考文献 |
| 17 | 附录：系数的Welch标准误、自由度、单侧检验与双侧置信区间 |

回归每县有前后两条观测：前期是1—9月平均指标，后期是11月指标。保持相同样本和县等权，交互项系数等于原来的早期减后期平均变化差。对同一县作前后差分后，等价回归的截距对应标准式的γ；推论继续用县内差分的Welch方法，不把同一县的两期当成独立样本。因果解释仍需平行趋势等条件，本次只补充式子及解释。

## 重新导出

在本目录运行，使用本机已有Python、Marp和Chrome。`CHROME_PATH` 可指定本机浏览器路径。

```bash
python ../../2026-11-11/02-composition/build_teaching.py slides.md
npx --yes @marp-team/marp-cli@4.5.1 slides.md --no-config --html --allow-local-files --pdf -o slides.pdf
npx --yes @marp-team/marp-cli@4.5.1 slides.md --no-config --html -o slides.html
python ../../2026-11-11/02-composition/check_delivery.py
```

讲稿脚本只提取备注；交付检查只验证两套稿的结构、PDF文本和保留文件哈希，不执行统计估计。检查需要Poppler的 `pdfinfo` 和 `pdftotext`；导出后还需目视核对公式与版面。
