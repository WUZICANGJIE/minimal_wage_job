"""Build and execute 02-composition/analysis.ipynb from this directory."""
import nbformat as nbf
from pathlib import Path
import json
import os
import sys
from nbclient import NotebookClient

BASE = Path(__file__).resolve().parent
nb = nbf.v4.new_notebook()
c = []
md = lambda s: c.append(nbf.v4.new_markdown_cell(s))
code = lambda s: c.append(nbf.v4.new_code_cell(s))

md('''# 2025年度最低賃金の発効時期と採用の構成（課題3・4）

第12表の合計・パート・パート以外の新規求人を使い、2025年11月の「早期−後期」差が**求人全体の縮小**か**パートとパート以外の構成の違い**かを調べる。

- 実行方法：このディレクトリで `python build_notebook.py`（または VS Code / Jupyter で必要なライブラリのあるPythonを選び、上から実行）。
- 依存：pandas, numpy, scipy, matplotlib, openpyxl, pymupdf。乱数は使わない。
- 数値はすべて `data/raw/` の政府統計から再計算する。`results/` の既存CSVは読まない。
- 求人≠採用≠雇用。パート以外は正社員だけではない。因果効果の推定ではない。''')

md('''## 1. データの読み込みと検査

第12表のシートは 1=パート含む一般（合計）、2=パート除く一般、3=一般パート。年・年度別は月平均なので、`月` 列に値がある行だけを使う。''')
code('''import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))
import numpy as np, pandas as pd
import analysis

frames, audit = analysis.load_vacancies(analysis.RAW/'estat_shokugyo_t12_shinki_kyujin.xlsx')
pd.DataFrame(audit).T''')

code('''# 全国＝47県の和、パート＋パート以外＝合計（いずれも最大残差0）
print('47都道府県:', len(frames['part'].columns)-1)
print('月数:', len(frames['part']))
print('パート＋パート以外＝合計 の最大残差:', audit['part_plus_nonpart_max_abs_residual'])''')

md('''## 2. 最低賃金と発効時期グループ

年度見出し（令和6年度・令和7年度）で列を選ぶ。11月発効の13県は主比較から外す。''')
code('''prefs = frames['part'].drop(columns='全国').columns.tolist()
policy, headers = analysis.load_policy(analysis.RAW/'mhlw_saitei_chingin_kaitei.xlsx', prefs)
print(json.dumps(headers, ensure_ascii=False))
policy.groupby('group')[['mw_2024','mw_2025','raise_yen','raise_pct']].agg(['size','mean']).round(2)''')

code('''# 独立の公式PDF（令和7年度 地域別最低賃金額一覧）と47県を照合
analysis.check_policy_pdf(policy)''')

md(r'''## 3. 指標

- 前年同月比：$y_{i,t}=100(\ln V_{i,t}-\ln V_{i,t-12})$
- 11月の差：$d_i=y_{i,\mathrm{Nov}}-\overline{y_{i,\mathrm{Jan..Sep}}}$、$D=\bar d_{\text{早期}}-\bar d_{\text{後期}}$
- 相対：$d^{P/N}=d^{P}-d^{N}$（県内の型別差。非処理の対照ではない）
- パート比率：$100(s_{i,\mathrm{Nov}}-s_{i,\mathrm{Nov}-12})$''')
code('''levels, metrics, share = analysis.prepare_metrics(frames)
print('相対＝パート−パート以外 の恒等性を確認済み')
metrics['part'].loc['2025-01':'2025-11'].mean(axis=0).describe().round(2)''')

md('''## 4. 主結果（基準：2025年1〜9月）''')
code('''summary, deltas, means = analysis.estimate(metrics, policy, '2025-09')
summary[['metric','estimate','ci_low','ci_high','p_negative','p_two_sided','n_early','n_late']].round(3)''')

code('''means.round(2)''')

md('''## 5. 推移（図）''')
code('''analysis.make_figures(metrics, policy, pd.concat([analysis.estimate(metrics, policy, e)[0] for e in ['2025-09','2025-07']], ignore_index=True))
from IPython.display import Image, display
display(Image(filename='assets/observed_trends.png'))
display(Image(filename='assets/observed_contrasts.png'))''')

md('''## 6. 基準期間の変更（1〜7月）''')
code('''alt, _, _ = analysis.estimate(metrics, policy, '2025-07')
alt[['metric','estimate','ci_low','ci_high','p_negative']].round(3)''')

md('''## 7. モデルの数値検算（推定ではない）

CES の相対需要と規模効果の式が実装と一致するか、極限（Leontief, Cobb–Douglas）で破綻しないかを確認する。パラメータは仮定値。新規部門の採用を当期労働投入とし、単価 c は1人の期間賃金と採用経費の合計。既存従業員・補充採用を省く追加仮定を置く。''')
code('''checks = analysis.model_checks()
checks''')

code('''# パート費用だけ10%上げたときの符号（σ, β で変わる）
rows=[]
for sigma in [1.2, 2.0, 8.0]:
    for beta in [0.2, 0.5, 0.9]:
        b=analysis.ces_choice(1,1,sigma=sigma,beta=beta); x=analysis.ces_choice(1.1,1,sigma=sigma,beta=beta)
        rows.append(dict(sigma=sigma,beta=beta,
                         part=100*np.log(x['P']/b['P']), nonpart=100*np.log(x['N']/b['N']),
                         relative=100*np.log((x['P']/x['N'])/(b['P']/b['N']))))
pd.DataFrame(rows).round(2)''')

md('''## 8. まとめ

- 合計の差はほぼ0、相対は負（-2.23）だが区間は0を含む。**構成の方向は仮説と整合するが、統計的には言えない**。
- モデルはパート以外の符号を一意に決めない。したがって nonpart を「対照群」と呼ぶことも、企業内代替の因果的な証拠とすることもできない。
- 限界：発効時期は外生でない、同比は前年の政策効果も引く、受理地統計、求人≠採用≠雇用、20県対14県で検出力が低い。''')

nb['cells'] = c
nb['metadata']['kernelspec'] = {'name': 'composition-local', 'display_name': 'Python (composition local)', 'language': 'python'}
kernel = BASE/'assets'/'kernels'/'composition-local'
kernel.mkdir(parents=True, exist_ok=True)
(kernel/'kernel.json').write_text(json.dumps({'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'], 'display_name': 'Python (composition local)', 'language': 'python'}))
os.environ['JUPYTER_PATH'] = str(BASE/'assets') + os.pathsep + os.environ.get('JUPYTER_PATH', '')
nbf.write(nb, BASE/'analysis.ipynb')
NotebookClient(nb, timeout=300, kernel_name='composition-local', resources={'metadata': {'path': str(BASE)}}).execute()
nbf.write(nb, BASE/'analysis.ipynb')
print('Executed', sum(c.cell_type == 'code' for c in nb.cells), 'code cells:', BASE/'analysis.ipynb')
