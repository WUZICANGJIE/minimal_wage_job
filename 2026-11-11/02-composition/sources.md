# sources

This file records the exact location of every external claim. Bibliographic claims were checked against the saved PDF, not against search snippets.

## 1. Acemoglu and Autor (2011), CES frame

- Daron Acemoglu and David Autor, "Skills, Tasks and Technologies: Implications for Employment and Earnings," in O. Ashenfelter and D. Card (eds.), *Handbook of Labor Economics*, Vol. 4B, ch.12, pp.1043–1171.
- Saved file: `evidence/Acemoglu_Autor_2011.pdf` (129 pages). SHA-256 recorded in `evidence/source_hashes.txt`.
- Used: section 3.1 "The simple theory of the canonical model", printed pp.1103–1105, physical PDF pp.61–63. Equation (2) is the CES aggregate; equation (5) is the skill premium in levels; equation (6) is its log form; equation (7) gives ∂lnω/∂ln(H/L) = −1/σ. The parent reviewer checked these physical pages directly.
- What I borrowed: the CES aggregator and relative factor-demand relationship. The unit-cost function is derived for this report's parameterization, not quoted from equations (2)–(6).
- What I added (not in the source): per-recruit costs c_j, the revenue term B·Z^β/β, the H = qV conversion, and the two-type part/non-part interpretation. These are my simplifications, flagged in `methods.md`.

## 2. Ohta and Komae (2022), Japanese part-time vacancies

- Souichi Ohta and Kazutomo Komae, "Vacancies, Job Seekers, and Minimum Wages: Evidence from Public Employment Placement Service Data," Keio-IES Discussion Paper Series DP2022-004, 9 March 2022.
- Saved file: `materials/Ohta_Komae_2022_Vacancies_Job_Seekers_Minimum_Wages.pdf` (29 pages). Local, already in the repo.
- Used: abstract (p.2), section 4.3 "Differences in Minimum Wage Effects between Vacancy Types" (printed p.12, PDF p.14), Table 5 (PDF p.21).
- Claim used on the slides: their Table 5 estimates minimum-wage elasticities of new vacancies for part-time and full-time separately, and reports larger absolute elasticities for part-time over 2005–2019. I do **not** claim they studied implementation timing, 2025, or composition shares.

## 3. Kanayama, Miyaji and Otani (2026)

- arXiv:2505.04555v3. Cited on slides only as background for short-run adjustment through posting reductions. Not re-analysed here.

## 4. Kazekami and Abe (2025)

- *Applied Economics*, published online 14 November 2025, DOI 10.1080/00036846.2025.2579945. Cited only as the contrasting "job postings rose" result. Not re-analysed here.

## 5. Vacancy data (Table 12)

- 厚生労働省「一般職業紹介状況（職業安定業務統計）長期時系列表 第12表 都道府県（受理地）別 雇用形態別 新規求人数」
- File: `data/raw/estat_shokugyo_t12_shinki_kyujin.xlsx`, downloaded 2026-10-26 from
  https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040505323&fileKind=0
- Sheets used (order is checked at runtime): index 0 = 第１２表－１（パート含む一般）, index 1 = 第１２表ー２（パート除く一般）, index 2 = 第１２表－３（一般パート）.
- Structure: row 2 (1-based; index 1) holds "全国" plus 47 prefecture names in zero-based columns 3:51; month rows are those with a non-null month label and a `<year>年` first cell; yearly and fiscal-year rows are monthly averages and are excluded.
- Checks performed in `analysis.py`: 164 consecutive months (2013-01..2026-08), 47 unique prefectures, no missing cells, all values positive integers, national column equals the sum of the 47 prefectures every month, and part + nonpart = total every month and prefecture (max residual 0).

## 6. Minimum wage data

- 厚生労働省「地域別最低賃金改定状況」, file `data/raw/mhlw_saitei_chingin_kaitei.xlsx`, downloaded 2026-10-26 from https://www.mhlw.go.jp/content/11200000/001756130.xlsx
- Columns are selected by the fiscal-year header text (`令和６年度`, `令和７年度`), not by position; the column immediately to the right of 改定額(円) is 発効年月日. Rows 3:49 (1-based) are the 47 prefectures.
- Independent cross-check: 厚生労働省「令和７年度 地域別最低賃金額一覧」, https://www.mhlw.go.jp/content/11201250/001729623.pdf, printed page 3. All 47 rows are re-parsed from the PDF text and compared on 2024 wage, 2025 wage, raise and effective date. Result: 47/47 matched (`results/policy_independent_crosscheck.csv`, `verification.json`).

## 7. Definitions (part-time, regular employee, new vacancy)

- 厚生労働省「集計結果（用語の解説）」 https://www.mhlw.go.jp/toukei/list/114-1_yougo.html
  - (4) パートタイム: weekly scheduled hours shorter than ordinary workers at the same establishment.
  - (5) 正社員: among 常用 excluding part-time, those called regular employees. This is why "non-part-time" must not be equated with "regular employee": the non-part-time series also contains 常用 non-regular and 臨時・季節.
  - (10) 新規求人: newly accepted job openings (planned hires), not advertisements and not hires.

## What is not sourced

- The specific part/non-part model with per-recruit costs and a revenue elasticity β is my own classroom simplification. It is not attributed to any paper.
- The numerical illustration in `results/model_illustration_NOT_ESTIMATED.csv` uses assumed parameters only.
- Any statement that the observed difference is caused by the minimum wage is not supported by these sources or this design.
