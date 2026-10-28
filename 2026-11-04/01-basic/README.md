# 基础版：把已发表的早晚发效比较完整做完

## 结果先看

维持10月28日发表的定义：2025年11月，10月发效20县与12月以后发效14县比较；排除11月发效13县。指标为一般パート新规求人数的同比对数差×100，各县等权。

主基准2025年1—9月：

- 早组减晚组的同比差，从基准期 **1.621819** 降到11月 **0.066409**。
- 县级变化均值：早组 **−7.808656**、晚组 **−6.253245**；差分 **−1.555410**。
- 95% Welch区间 **[−7.933878, 4.823057]**；负方向单侧p **0.310082**，双侧p **0.620164**。
- 1—7月基准：差分 **−2.179821**，95%区间 **[−8.847660, 4.488018]**；4—9月基准：**−1.048580**，区间 **[−7.314093, 5.216933]**。

点估计符合“差缩小”的方向，但没有足够证据在5%水平支持负方向假说；不是证明差为零，也不是最低工资的因果效应。单位是同比对数差×100之差，近似增长率百分点，**不是最低工资弹性或雇用减少百分比**。

## 文件

| 文件 | 用途 |
|---|---|
| `slides.md` / `slides.pdf` / `slides.html` | 10页日文Marp源稿、PDF、HTML；白底黑字，主文含实数据图和数值 |
| `analysis.py` | 读取现有Excel、验证、县级差分、Welch区间、敏感性、绘图及模型数值检查 |
| `analysis.ipynb` | 日文说明和实际执行结果；包括全部34县中间值、三幅图、独立SciPy检算，无虚构Colab链接 |
| `build_materials.py` | 根据真实结果生成slides和notebook，并用当前Python执行notebook |
| `methods.md` | 日文推导、模型来源与新增假定、招聘与雇用区别、统计假定和边界 |
| `sources.md` / `citation-ledger.json` / `evidence/` | 文献版次、具体页节、URL、逐页提取与原文证据；独立ledger |
| `results/*.csv` / `results/verification.json` | 政策全县、2068行面板、县级差分、月度群平均、估计结果和数据/模型验证 |
| `tests/test_analysis.py` / `results/test.log` | 6项统计、Excel、模型边界测试及实际日志 |
| `verify_artifacts.py` / `verification.json` | notebook执行、10页PDF、HTML加载及页面溢出、数值、测试和产物哈希 |
| `results/preview/` | PDF逐页PNG及总览，供视觉核查 |

HTML使用相对图路径和本地日文字体。移动时应复制整个 `01-basic` 目录，而不是只复制HTML。数据继续从本仓库 `data/raw/` 读取；不覆盖、不重新下载原始Excel。首次运行若本地字体不存在，会从notofonts仓库下载Noto Sans JP到本目录 `assets/`。已附字体时分析可离线运行。

## 精确复现命令

在**包含本方案的仓库根目录**运行；不要在另一个worktree里写结果。本次实际解释器为 `/opt/data/cache/scratch/minwage-20261104-venv/bin/python`，未改共享环境。复制到主仓库后只需改变 `cd`，其余相对路径不变。

```bash
cd /opt/data/projects/minimal_wage_job-worktrees/basic
PY=/opt/data/cache/scratch/minwage-20261104-venv/bin/python
$PY 2026-11-04/01-basic/analysis.py
$PY 2026-11-04/01-basic/build_materials.py
$PY -m unittest discover -s 2026-11-04/01-basic/tests -v
CHROME_PATH=/usr/bin/chromium npx --yes @marp-team/marp-cli@4.5.1 \
  2026-11-04/01-basic/slides.md --no-config --html --allow-local-files \
  --pdf -o 2026-11-04/01-basic/slides.pdf
npx --yes @marp-team/marp-cli@4.5.1 \
  2026-11-04/01-basic/slides.md --no-config --html \
  -o 2026-11-04/01-basic/slides.html
$PY 2026-11-04/01-basic/verify_artifacts.py
```

新机器可在**自己隔离的环境**安装 `requirements.txt`；PDF渲染还需要Node/npm和Chromium。实际已验证的Python库版本见 `results/verification.json`（本次numpy 2.5.4、pandas 3.1.0、scipy 1.18.1、matplotlib 3.11.2），Marp CLI固定4.5.1。notebook执行器只在本目录创建kernel描述，不安装或修改全局kernel；重建时会将其更新为当前Python路径。

若只重新计算、不要图和网络：

```bash
$PY 2026-11-04/01-basic/analysis.py --no-figures
```

完整的文献ledger验证还可用本机已有的工具，不是重算结果的必要依赖：

```bash
S=/opt/data/skills/research/grounded-citations/scripts/sources.py
python "$S" --ledger 2026-11-04/01-basic/citation-ledger.json \
  verify 2026-11-04/01-basic/sources.md --evidence
```

## 六项TODO对应

| 原TODO | 本方案完成内容 |
|---|---|
| 重新检查数据、早晚地区如何比 | 六sheet的全月连续/47县/全国和内部分项校验；年度标题而非列位置识别；固定20对14县的11月比较 |
| 说明创新点 | `sources.md` 对照最近邻：不是首次研究求人，经济增量仅为完成原假说、报告不确定性和基准敏感性 |
| 有文献依据的微观模型 | OpenStax §14.1的利潤最大化/边际产品条件；自设幂函数及补充招聘映射，详见 `methods.md` |
| 按数据模型改进假说及方法 | 保留负方向；补写条件和完整单侧原假设；34县先做县内差分，再用Welch |
| 实际验证、讨论理论与现实 | 三个基准均执行；点估计负但区间含零；不会把统计不显著改写成支持理论 |
| 结论、implications与日文发表 | 10页三格式完整稿+日文notebook；说明求人不等于雇用、内生发效时点、同比去掉去年政策、受理地限制 |

## 为什么是低创新、低难度

只问一个经济问题：原先较高的早组同比，在共同的11月是否相对下降。主模型是一阶条件能解出的固定资本短期劳动需求；补充招聘仅做明确假定的会计映射，不估计结构参数。主检验是34个县级差分的两样本均值差，不加控制变量、IV、复杂DID或动态路径。更高级的构成变化与跨期招聘问题留给其他方案，本案不依赖其输出。

模型中的“条件付き”指资本、价格、技术和人均劳动时间给定，不把它误称为给定产量的成本最小化需求。求人映射允许补充招聘：在雇用不变时，离职减少也会使求人减少。`f`不是从当月充足数/当月新规求人数机械估出来的同批充足概率。

## 与10月21日、28日发表的变化

保留题目、比较月、政策组、一般パート/受理地、对数同比和一县一票；不修改原发表。新增可追溯教材基础、推导与模型边界，实际计算11月差分/区间，补1—7月与4—9月基准，明确反向/不显著也如实报告。将“同比去除季节性”改为抑制重复季节性，将“改定前相近即平行趋势”改为描述而非识别证明。

## 核查、局限与尚未做的事

- 数据原文件执行前后SHA-256一致；一般和常用分别满足part+nonpart=total，全国合计在六sheet都相等。没有向历史data/processed写文件。
- 解析解在9组**假定参数**下与数值最优化一致，最大相对误差约4.9e−7；检查数值弹性、零招聘、补充招聘和非法边界。它只验证推导/实现，不验证企业现实行为。
- 区间假定县间独立等条件；这些县并非随机抽样或随机分配。只有34个政策单位，不能靠增加月份制造精度。
- 不识别因果、具体招聘机制或就业效果；不估计招聘政策的福利与最优性；不把1—7月保证为无预期；不推断12月后的追赶或收敛。
- 官方口径本来区分新规求人、有效求人和就职件数；本案只测前者。媒体份额和受理地错配可能变化。
- 首次执行发现pandas `PeriodIndex.from_fields`不接受`name`参数，已将命名独立设置并通过回归测试。文档/图形使用本地字体，不依赖系统日文字体。
- notebook执行器会提示本机TCP kernel未加密；这不是分析失败。曾试用IPC但本环境kernel未响应，已撤回，最终版使用已成功执行的本机TCP方式。Marp的本地文件访问提示来自读取本地字体/图。
- 本案需要的文件已生成并真实执行；未commit、未push、未修改其他方案及历史材料。可复用经验：先检查年度标题和恒等式，再固定县/月/基准、计算县内差分；原文支持标准FOC，不支持自设求人映射。
