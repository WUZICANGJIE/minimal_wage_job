# 构成版：招聘总量与兼职构成（20页）

已将10页稿重写为20页日文slides，保留原政策分组、统计口径、主结果和30px KaTeX公式。它是原兼职比较的嵌套扩展，不是新的独立识别路线。

## 阅读顺序

- `slides.md` / `slides.pdf` / `slides.html`：同一正式稿，20页（含封面和参考文献）。
- `video/composition_explainer.mp4`：约11分钟的日语讲解视频（保留公式、逐步展开），字幕、旁白全文与构建脚本见 `video/README.md`。
- `speaker_notes.md`：从slides内20条隐藏Marp notes生成的逐页日文讲解。
- 第5–11页逐步解释目标与费用、CES、FOC、相对需求、规模、代替/规模分解与仮定值例；第12–14页连接到求人、指标和实际差分计算。
- `methods.md` / `sources.md`：完整推导、来源与新增假设；`analysis.py` / `analysis.ipynb` / `results/` 保持原件。
- `build_teaching.py`：仅生成教学用区间图和讲解备注，不写统计CSV。
- `check_delivery.py` / `verification_log.json`：只读重算和交付验证。`evidence/slide_01.png`–`slide_20.png`、`contact_sheet_20.png`为本次真实渲染。

## 结果与边界

2025年11月，早期20县减后期14县，排除11月发效13县；各县等权。先算11月的100×对数同比减2025年1–9月平均，再比较两组。

| 指标 | 点估计 | Welch 95%区间 |
|---|---:|---:|
| 兼职 | −1.56 | [−7.93, 4.82] |
| 非兼职 | +0.67 | [−3.02, 4.37] |
| 总量 | −0.15 | [−4.15, 3.85] |
| 相对（兼职−非兼职） | −2.23 | [−8.05, 3.59] |
| 兼职比率（百分点） | −0.51 | [−1.85, 0.82] |

兼职单侧p=0.310082。区间均含0，不能确认负差，也不能排除总量收缩。非兼职不等于正社员，更非未处理对照。比率和relative在差分、平均后不等价，不是独立验证。模型假定新部门没有既有员工、固定充足率；新增工资费用及收入曲率是课堂简化。第11页例子来自原模型CSV，不是实证估计。

## 复现本次交付（不改统计结果）

在本目录使用已有依赖的Python环境（pandas、matplotlib、pymupdf、playwright、nbformat等；不必安装新依赖）：

```bash
python build_teaching.py
CHROME_PATH=/usr/bin/chromium npx --yes @marp-team/marp-cli@4.5.1 slides.md --no-config --html --allow-local-files --pdf -o slides.pdf
npx --yes @marp-team/marp-cli@4.5.1 slides.md --no-config --html -o slides.html
python check_delivery.py
```

本机已用 `/opt/data/cache/scratch/minwage-20261104-venv/bin/python` 实际执行。更换机器请用自己的Python。HTML须和`assets/`一起移动。验证器直接读取项目根目录的`data/raw/`，在内存中重算两套基准的全部点估计、区间、p值及群均值，不调用会重写CSV的`analysis.run()`。原完整统计重建入口仍为`analysis.py`与`build_notebook.py`，本次不运行其写结果路径。

## TODO在slides正文的位置

| TODO | 页码与可见内容 |
|---|---|
| 数据、口径、早晚比较 | 3–4、13–15、18：数据定义、20/13/14、可比之处与剩余差异 |
| 先行研究与增量 | 2：具体研究、不同estimand、规模/构成的课堂增量 |
| 有文献依据的微观模型 | 5–11：目标、选择、费用约束、CES、推导与例子 |
| 假说转成检验 | 12–14：充足率桥接、指标、县内变化、早晚差、单侧假说 |
| 实际检验与理论现实 | 15–18：趋势、区间、构成、模型对照、基准期敏感性 |
| 结论、implications、局限 | 19；关键限制另在4、12、16–18页 |

原CSV及`analysis.py`的13个文件SHA-256清单保存在`evidence/protected_hashes_20slides.json`。验证器同时检查原始Excel哈希、5个单元测试、20页/20条备注、全页HTML溢出与来源碰撞、图像/字体、KaTeX错误和TeX漏出、显示公式30px，并输出逐页几何记录。视觉复核记录见`evidence/visual_review_20slides.md`。未做真人试讲，不承诺演讲时长；没有commit或push。
