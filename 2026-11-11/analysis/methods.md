# 月度 DID 的估计口径

## 1. 数据、分组与窗口

观测单位为都道府县×月。早期组为 2025 年 10 月生效的 20 个县；后期组为 2025 年 12 月及以后生效的 14 个县。11 月生效的 13 个县排除。样本县在各月保持不变，县与县等权。

主样本为 2025 年 1–9 月和 11 月：34 县 × 10 月 = 340 行。10 月是早期组的政策移行月，仅在原始趋势图中显示。敏感性样本为 1–7 月和 11 月：272 行，沿用原分析预先使用的窗口。

求人数量的原始月度序列涵盖 2013 年 1 月至 2026 年 8 月，本次使用上述窗口。

设求人量为 \(V_{it}^{P}\)、\(V_{it}^{N}\)，合计为 \(V_{it}^{T}=V_{it}^{P}+V_{it}^{N}\)。沿用原来的五个 outcome：

$$
Y_{it}^{j}=100[\log V_{it}^{j}-\log V_{i,t-12}^{j}],
\quad j\in\{P,N,T\},
$$

$$
Y_{it}^{R}=Y_{it}^{P}-Y_{it}^{N},\qquad
Y_{it}^{S}=100\left[
\frac{V_{it}^{P}}{V_{it}^{T}}-
\frac{V_{i,t-12}^{P}}{V_{i,t-12}^{T}}
\right].
$$

前三项和 R 的单位为 100×对数差；S 的单位为百分点。N 指非兼职求人。

## 2. 月度 DID 主回归

从标准 DID 的

$$
Y_{it}=\alpha+\beta Treat_i+\gamma Post_t
+\delta(Treat_i\times Post_t)+\varepsilon_{it}
$$

扩展为县固定效应和月份固定效应：

$$
Y_{it}^{j}=\alpha_i^{j}+\lambda_t^{j}
+\delta^{j}(Treat_i\times Post_t)+\varepsilon_{it}^{j}.
$$

Treat = 1 表示早期组，Post = 1 表示 11 月。Treat 主效应由县固定效应吸收，Post 主效应由月份固定效应吸收。保留的交互项系数为 DID。

在当前平衡面板和等权 OLS 下，

$$
\widehat{\delta}^{j}
=\left(\bar Y^{j}_{E,11}-\frac{1}{9}\sum_{m=1}^{9}\bar Y^{j}_{E,m}\right)
-\left(\bar Y^{j}_{L,11}-\frac{1}{9}\sum_{m=1}^{9}\bar Y^{j}_{L,m}\right).
$$

因此，月度回归与原来“前期均值对 11 月”的 DID 点估计完全对应。1–7 月敏感性分析将 9 换为 7。没有增加新的观察月份。

## 3. 月度交互项回归与事前趋势

另估计月度交互项，以 2025 年 9 月为基期：

$$
Y_{it}^{j}=\alpha_i^{j}+\lambda_t^{j}
+\sum_{m\in\{1,\ldots,8,11\}}\theta_m^{j}
\left(Treat_i\times\mathbf{1}\{t=m\}\right)+\varepsilon_{it}^{j}.
$$

图中 \(\theta_9^{j}=0\) 是基期归一化。每个其他月份的系数表示“该月早晚组差距，相比 9 月差距变化了多少”。

平行趋势诊断使用：

$$
H_0:\theta_1^{j}=\cdots=\theta_8^{j}=0.
$$

对这 8 个限制做县聚类稳健 Wald F 检验，参考 \(F(8,33)\)。1–7 月敏感性分析以 7 月为基期，联合检验 1–6 月，参考 \(F(6,33)\)。各 outcome 单独报告，p 值未做多重检验调整。

主样本的联合检验 p 值：P = 0.374，N = 0.156，T = 0.579，R = 0.068，S = 0.070。用于判断已观察的事前系数是否偏离 0；不拒绝零假设本身不等于证明平行趋势。

月度系数 CSV 同时提供：

$$
\widetilde{\theta}_m^{j}
=\theta_m^{j}-\frac{1}{9}\sum_{s=1}^{9}\theta_s^{j}.
$$

这些带有 “vs_pre_mean” 后缀的列把 1–9 月平均归一化为 0。其 11 月点估计与主 DID 一致。协方差按同一线性变换计算；月度交互项模型与主回归的参数数目不同，有限样本校正后的标准误可以略有不同。

## 4. 标准误与区间

县为聚类单位，允许同一县的误差跨月相关。采用 CRV1：

$$
\widehat V
=\frac{G}{G-1}\frac{n-1}{n-K}
(X'X)^{-1}
\left[\sum_{i=1}^{G}X_i'\hat u_i\hat u_i'X_i\right]
(X'X)^{-1}.
$$

\(G=34\)，\(n=340\)，主回归 \(K=44\)，月度交互项模型 \(K=52\)。K 包含截距、县和月份虚拟变量及交互项；采用显式虚拟变量 OLS 的校正口径。敏感性分析 \(n=272\)，对应 \(K=42\) 与 \(K=48\)。

置信区间使用 \(t_{33}\) 临界值；输出双侧 p 值，并保留与原先负向备择对应的单侧 p 值。图中是逐点 95% 区间。实现为 statsmodels 的 cluster covariance，启用 use_correction、df_correction 和 use_t。[聚类协方差说明](https://www.statsmodels.org/stable/generated/statsmodels.stats.sandwich_covariance.cov_cluster.html)及[推论自由度说明](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html)记录了对应选项。

原版对县内变化使用 Welch 推论。本版改用月度面板的县聚类 CRV1，因此在同一点估计下，标准误和自由度发生变化。

## 5. 后续扩展月份

原后期组在 12 月起陆续生效。若要求对照县在整个比较月份保持未处理，则 11 月有 14 个，12 月有 6 个，2026 年 1–2 月各有 2 个。进一步延长政策后窗口时，需要据实际生效日期重新定义 not-yet-treated 对照组，并同时报告各月对照组规模。

## 6. 来源与复核

本次只读以下已有文件：

- [metrics_prefecture_month.csv](../../archive/2026-11-11-two-period-did/results/metrics_prefecture_month.csv)：指标月度长表。
- [policy.csv](../../archive/2026-11-11-two-period-did/results/policy.csv)：生效日、最低工资与分组。
- [contrasts.csv](../../archive/2026-11-11-two-period-did/results/contrasts.csv)：原版点估计及 Welch 推论，用于对照。

原始来源为厚生劳动省的[一般职业介绍状况长时序表第 12 表](https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040505323&fileKind=0)与[地区最低工资改定状况](https://www.mhlw.go.jp/content/11200000/001756130.xlsx)，使用仓库 2026-10-26 下载的 Excel 快照。详细表号和范围见[原来源记录](../../archive/2026-11-11-two-period-did/sources.md)。

[analysis_checks.json](analysis_checks.json) 保存输入 SHA-256、运行版本及矩阵校验；[verification.json](verification.json) 记录从原始 Excel 独立重建 outcome、使用 FWL 双向去均值复核 DID/聚类 SE、以县内差分协方差复核联合 F 检验的结果。验证还检查全国加总、P+N=T、47 县政策信息和主回归面板完整性。
