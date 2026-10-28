# 基础版：20页日文发表材料

`slides.pdf` / `slides.html` / `slides.md` 均为20页；`speaker_notes.md` 是对应20页的自然日文讲稿，亦已放入每页Marp非显示comment。未实测演讲时长。

## 这次改了什么

主线改为：企业选择人数 → 利润目标 → FOC → 劳动需求 → 补充招聘 → 条件性假说 → 县内差分 → 早晚差及不确定性。不用讲稿代替正文解释。

- 逐步定义符号和单位，将目标函数、求导、解和比较静态拆开。
- 用原模型函数实际计算假定例：时薪1,000→1,100时，希望人数100→82.64；明确不是估计或2025年预测。另以离职10%→5%的补充求人说明“求人减≠雇用减”。
- 用真实东京都数据展示县内计算，再以实际两群表解释−1.56比的是什么。三幅图都有轴、点/线和读图解释。
- 文献对照放到正文，解释有限的新增问题；解释不显著不等于零影响，也不能否定规模缩小。

## 六项TODO在正文的位置

| TODO | 页码 |
|---|---|
| 数据口径、早晚比较及可比性边界 | 2–3 |
| 先行研究具体做法、本案多问什么 | 4 |
| 有文献基础的微观模型及推导 | 5–11 |
| 模型→假说→可计算检验 | 12–14、17 |
| 实际结果、理论与现实的对照 | 14–18 |
| 结论、含意、局限 | 19；文献20 |

## 结果和旧文件不变

维持2025年11月、早20/晚14、排除11月13县，一般パート新受理採用予定人員、受理地、县等权、对数前年同月比×100、1–9月主基准及1–7月敏感性。

主差 **−1.555410**，95% Welch区间 **[−7.933878, 4.823057]**，负方向单侧p **0.310082**。只是点估计符合方向，证据不足以支持负方向，不是因果效应或雇用减少率。

`analysis.py`、原六个统计CSV、两份raw Excel SHA-256均保持不变。`analysis.ipynb` 保留原来真实执行的版本（7个代码单元、3幅图），本轮没有伪称重新执行notebook。原分析另输出到 `results/reproduction/` 实际重跑，六个CSV与原文件逐字节相同。

## 重建与验证

`slides.md` 现在是唯一正文编辑源。`build_materials.py` 只维护引用映射、逐页讲稿和教学例子的检算记录，不再用内嵌10页模板覆盖正文，也不改写统计CSV/notebook。改正文后运行以下命令：

```bash
cd /opt/data/projects/minimal_wage_job-worktrees/basic/2026-11-04/01-basic
PY=/opt/data/cache/scratch/minwage-20261104-venv/bin/python
$PY build_materials.py
CHROME_PATH=/usr/bin/chromium npx --yes @marp-team/marp-cli@4.5.1 \
  slides.md --no-config --html --allow-local-files --pdf -o slides.pdf
npx --yes @marp-team/marp-cli@4.5.1 \
  slides.md --no-config --html -o slides.html
$PY verify_artifacts.py
```

单独复算而不覆盖旧结果：

```bash
$PY analysis.py --output results/reproduction --no-figures
$PY -m unittest discover -s tests -v
$PY /opt/data/skills/research/grounded-citations/scripts/sources.py \
  --ledger citation-ledger.json verify slides.md --evidence
```

已运行：20页PDF/HTML及20页notes检查、字体/图片、KaTeX错误和原样TeX、横纵溢出及来源重叠、原数据/CSV/代码hash、6项原测试、引用证据验证。预览网格为4列×5行，位于 `results/preview/contact_sheet.png`；逐页1280×720 PNG和 `layout.json` 同目录。已查看总览，并全尺寸逐页核查全部20页；记录见 `evidence/visual_review.md`。

`verification.json` 为当前自动检查结果；`evidence/before_rewrite_sha256.json`、`reproduction_comparison.json`、`teaching_examples.json` 保存不变性、真实复算、说明例子的依据。`methods.md`、`sources.md` 和原证据继续保留。

HTML使用本地字体及相对图路径，移动时复制整个目录。没有安装依赖或修改共享环境。没有commit/push，没有修改历史发表、主repo或其他worktree。尚未实测真人演讲时间；发效时间内生、预期、受理地错配、缺少企业级变量等识别局限没有因扩页而消失。
