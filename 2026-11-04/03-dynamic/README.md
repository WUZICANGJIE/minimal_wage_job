# 跨期版：现在招聘，还是以后招聘

日文 **20页** slides（含标题与参考文献），保留原两期模型、原11月主比较和所有统计结果。不是新模型或新的识别路线。未commit/push。

## 文件

- `slides.md` / `slides.pdf` / `slides.html`：唯一正式稿；白底黑字、KaTeX公式。MD为手写单一源稿，没有会覆盖它的生成器。
- `speaker_notes.md`：20页自然日文逐页讲稿，与MD的Marp隐藏notes对应；不承诺未经排练的时长。
- `build_teaching.py`：只生成教学用区间/路径图、提取notes，调用原求解器核对假定参数示例；不写统计CSV。
- `analysis.py` / `analysis.ipynb` / `results/`：原统计与模型计算、已执行notebook、原CSV/JSON。
- `methods.md` / `sources.md`：完整推导与假设、原文版本和阅读页码。Hamermesh 1993是框架来源，课堂二期方程不是他的原方程。
- `verification.json` / `teaching-verification.json` / `visual-review.json`：实际检查与TODO页码；`evidence/slide-*.png`、`slides-contact-sheet.png`为20页渲染预览。
- `preserved-analysis-sha256.json`：改写前的analysis.py、10个CSV与summary.json哈希，用于检查统计未变。

## 正文六项TODO

| 要求 | 实际页码 |
|---|---|
| 数据口径、早晚如何可比和不可比 | 3–4、15、17–18 |
| 先行研究具体做了什么、本次谦虚增量 | 2、8 |
| 文献支撑、企业目标/变量/约束/推导 | 5–13 |
| 模型预测如何转成可计算检验 | 11–12、14–16 |
| 真数据结果与理论/现实对照 | 13、15–18 |
| 结论、implications、局限 | 18–19 |

第5、6页分开讲两期员工存续；第9、10页分别讲二期、一期FOC；第12页解释未来工资效应及零曲率/零存续/零招聘边界。第13页仅是假定值，未估计或校准。第15页用真实均值展示−1.56如何算出，第16页单独读置信区间，第18页的后续路径仅描述。

## 保持的结果与解释边界

- 2025-11，part新受理採用予定人員、受理地；早20/晚14，排除11月13县，县等权。主基准2025-01..09。
- 主差−1.5554104519904133，Welch 95% [−7.933877955930516, 4.823057051949689]；负向单侧p=.310082、双侧p=.620164。
- 1..07敏感性−2.1798208529984056，[−8.847659583025631, 4.48801787702882]。只减少8–9月公表后的基准污染，不保证无预期。
- 后续形状（4–6月早晚差减11月早晚差）−.671188，[−6.158003,4.815627]。12月起晚组陆续处理，后续不是未处理对照，不能识别补充、费用或预期。
- 宽区间表示负差的证据不足，不证明无影响，也不排除求人/雇用规模收缩。同比扣除了前年政策；受理地不等于就業地；两组涨幅与城市构成不同。现有数据不识别模型参数、政策因果效应或福利。
- 200组假定参数的KKT/独立数值优化通过，134内点导数误差约1.20e−10。这检查数学，不是实证验证。

## 复现

在本目录或项目根目录执行（路径自动定位raw；不要修改共享venv）：

```bash
PY=/opt/data/cache/scratch/minwage-20261104-venv/bin/python
D=/opt/data/projects/minimal_wage_job-worktrees/dynamic/2026-11-04/03-dynamic
$PY "$D/build_teaching.py"
CHROME_PATH=/usr/bin/chromium npx --yes @marp-team/marp-cli@4.5.1 "$D/slides.md" --no-config --html --allow-local-files -o "$D/slides.html"
CHROME_PATH=/usr/bin/chromium npx --yes @marp-team/marp-cli@4.5.1 "$D/slides.md" --no-config --html --pdf --allow-local-files -o "$D/slides.pdf"
$PY -m unittest discover -s "$D/tests" -v
$PY "$D/verify_delivery.py"
```

`reproduce.py`另可执行完整分析→测试→notebook→教学图/notes→HTML/PDF→验证，实际stdout在`execution.log`。不运行来源归档辅助脚本，它们不属于核心复现。

验证器检查20页、逐页notes、TODO页码、CSV/代码/原数据哈希、真实图片/字体、KaTeX错误、30px显示公式、滚动高度与页脚安全区，重新生成4×5预览。视觉记录同时保存PDF哈希和逐页2倍渲染像素哈希：仅因PDF时间戳改变、但20页像素完全一致时，沿用已核查版面；任何页面像素变化都需要重新检查并更新记录。版面检查通过不代表因果识别成立。
