# 本周模型与统计方法的来源

完整的文献页码、原始数据来源与口径说明见[来源记录](../archive/2026-11-11-two-period-did/sources.md)。文献PDF和数据核对记录随原分析归档；本周slides末尾保留参考文献。

- CES与相对需求：Acemoglu and Autor (2011), pp.1103–1105，式(2)–(6)。
- 不同招聘类型的研究动机：Ohta and Komae (2022), 4.3节、Table 5。
- 新规求人、兼职与非兼职口径：厚生劳动省第12表－1〜3及用语解说。
- 新部门、收益函数、每人招聘费用与固定充足率：本报告的课堂简化假设，完整定义见 `methods.md`。
- 统计主规格采用县与月份固定效应的月度DID。固定同一批县、同一窗口、等权且无额外控制变量时，主交互项系数与前后均值DID对应。固定效应与标准DID的联系见 [Duhaut、Kondylis、Loeser和Piza（2021），World Bank](https://blogs.worldbank.org/en/impactevaluations/did-you-see-beta-beta-who-part-1)；本项目平衡月度面板的代数对应见方法文档第6节。
- 平行趋势及事前检验的详细说明与来源见[下周材料](../2026-11-11/analysis/parallel_trends.md)。
- 县聚类推论使用CRV1有限样本校正和县数减一的自由度，保留主假说的左尾p值与双侧95%区间。对应实现选项见 [statsmodels聚类协方差](https://www.statsmodels.org/stable/generated/statsmodels.stats.sandwich_covariance.cov_cluster.html)和[推论自由度说明](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html)。月度误差相关的处理参见 [Bertrand、Duflo和Mullainathan（2004）](https://doi.org/10.1162/003355304772839588)。
- 本周介绍模型和统计方法。月度DID的代码、原始数据复核和实际结果位于[下周独立目录](../2026-11-11/analysis/README.md)。
