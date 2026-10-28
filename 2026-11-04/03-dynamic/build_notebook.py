"""日本語notebookを生成し、このPythonで実際に全セルを実行する。"""
from pathlib import Path
import sys,json,os
import nbformat as nbf
from nbclient import NotebookClient
H=Path(__file__).resolve().parent
md=nbf.v4.new_markdown_cell; code=nbf.v4.new_code_cell
cells=[
md('# 最低賃金の発効時期とパート求人：二期の採用選択\n課題3（モデル・仮説）と課題4（実データ検証）。既発表の2025年11月・早20県対晩14県を主比較として残す。\n\nこのnotebookはリポジトリ内で実行済み。未公開のColabリンクは使わない。`analysis.py`を唯一の計算本体とし、rawファイルは読むだけである。結果の単位は対数差×100で、求人数はハローワーク新受理の採用予定人数、実際の採用・雇用ではない。'),
code('from pathlib import Path\nimport sys, json\nimport pandas as pd\nfrom IPython.display import display, Image\nH=Path.cwd()\nassert (H/"analysis.py").is_file(), "notebookのある03-dynamicから実行してください"\nsys.path.insert(0,str(H))\nimport analysis as a\nsummary=a.run_all()\nprint("実行完了：rawの書換えなし")'),
md('## 1. 読み込みと検査\n年・年度平均行を除き、月次の164か月を検査。47県、全国合計、一般パート＋一般パートを除く一般＝一般計、前年同月との対応、年度見出しを確認する。分析部分は2023年1月〜2026年8月の2,068県月。2024年の賃金・発効日は別の厚労省PDF全47県と照合する。'),
code('display(pd.Series(summary["data"]["checks"],name="passed"))\nprint(summary["data"]["policy_columns"])\nprint(summary["data"]["raw_sha256"])'),
md('## 2. 比較できる暦月\n11月は早群20県が全月適用、晩群14県は全月未発効。ただし企業が未来の賃金を予想する場合、法的未発効は経済的な未処置を意味しない。8月4日に目安公表、9月5日に全県の答申が集約された。7月以前も完全に予期しない期間とは保証できない（sources.md [8][9]）。\n\nLか月前から反応するなら、t+L月末まで未発効の県だけが候補。以下の数は日付上の必要条件にすぎず、実際の予想開始日は観察しない。12月以降は元の晩群を未処置対照として解釈しない。'),
code('timing=pd.read_csv(H/"results/timing_support.csv")\ndisplay(timing[timing.month.between("2025-10","2026-04")])'),
md('## 3. 一つの主検定\n$y_{it}=100(\\log V_{it}-\\log V_{i,t-12})$、$d_i=y_{i,2025/11}-\\overline y_{i,2025/1:9}$。早群の$d_i$平均から晩群の平均を引く。各県等重み、推論単位は34県である。H1は負方向。Welchの区間・両側pに加え、既発表どおり負方向の片側pも報告する。独立県を仮定した近似的な不確実性で、無作為割付の検定ではない。\n\n同じ点推定は$d_i=\\alpha+\\tau Early_i+u_i$のOLSでも得られる。最低賃金の因果効果や賃金弾力性ではない。'),
code('main=pd.read_csv(H/"results/main_contrasts.csv")\ndisplay(main[["pre_end","estimate","ci_low","ci_high","p_negative","p_two_sided"]])\ndisplay(pd.read_csv(H/"results/prefecture_d_pre9.csv").head())\ndisplay(Image(filename=str(H/"figures/actual_yoy.png")))'),
md('主差は−1.56、95%区間[−7.93, 4.82]。方向は既発表H1と同じだが、明確な負の差とは判断できない。1〜7月基準も併記し、都合のよい基準へ置き換えない。引上げ率を入れた補助OLSは比較可能性を保証しない。2024年の改定の影響も同比から差し引かれる。徳島は2024年11月1日発効で、2025年の晩群に含まれる。'),
code('display(pd.read_csv(H/"results/wage_increment_overlap.csv"))\nprint("引上げ率調整（補助）:",summary["controlled_ols_hc3"])\nprint("前年の同じ暦月差（無政策placeboではない）:",summary["prior_year_diagnostic"])'),
md('## 4. 主モデル：将来も採用を選ぶ企業\nHamermesh (1993), III.A、本文pp.4–5のgross/net調整費用と将来利潤に基づく授業用の二期簡略化（同論文そのものではない）。企業は今期と次期の募集枠$v_1,v_2\\ge0$を選ぶ。$L_1=rL_0+qv_1$, $L_2=rL_1+qv_2$。\n\n$$\\max\\ R(L_1)-w_1L_1-C(v_1)+\\beta\\{R(L_2)-\\bar w_2L_2-C(v_2)\\},\\quad R(L)=aL-\\frac b2L^2,\\ C(v)=cv+\\frac\\kappa2v^2.$$\n\n$\\bar w_2$は既知の予想次期賃金。固定工時、同質労働、外生賃金、一定の残存率$r$・充足率$q$、裁員なし、期末価値ゼロを追加仮定する。資金制約・賃金設定力・マッチング市場均衡は含まない。DMPモデルとは呼ばない。法定時給をそのまま企業の一人当たり期間賃金に置換しない。詳しい解と条件はmethods.md。'),
md('内点では現在賃金の上昇は$v_1$を減らし$v_2$を増やす。後者は、今期の採用を減らした分を次期に相対的に補う効果で、次期の求人数が今期より多くなるという予測ではない。$r>0,\\kappa>0$なら予想次期賃金の上昇は$v_1$も減らす。$\\kappa=0$または$r=0$なら、このモデルの内点で先取り反応は消える。ゼロ募集の角点では内点導関数を適用しない。'),
code('print("すべて仮定値・推定ではない:",summary["assumed_parameters"])\ndisplay(pd.read_csv(H/"results/model_assumed_scenarios.csv"))\ndisplay(Image(filename=str(H/"figures/model_simulation.png")))\nprint(summary["model"])'),
md('## 5. その後の道筋は記述だけ\n両群の需要・離職・充足率・賃上げ幅等が同じなら、今期の賃金だけ高い早群は今期募集が少なく、次期に晩群より多くなる、という条件付き制約がある。ただし実際は晩群の引上げ率が大きく、モデルの2期は特定の月と同一ではない。\n\n4〜6月の早晩差から11月の早晩差を引くと−0.67、95%区間[−6.16, 4.82]。点推定に相対的な補いは見られないが不確実性が大きい。全県発効後の比較であり、catch-upや調整費用の存在を識別しない。'),
code('display(Image(filename=str(H/"figures/actual_gap_path.png")))\nprint(summary["later_shape_diagnostic"])'),
md('## 結論と限界\n今回の追加は、未来の賃金負担と採用を先送りする費用のトレードオフを明示したこと。統計手法を高度化したわけではない。先取り・動学的求人調整は既存研究にもあり、初の発見とは主張しない。実データが検査するのは時序・群間差の制約までで、$q,r,\\kappa$や期待の形成は推定しない。県間の政策時期は内生的、受理地と就業地も一致するとは限らない。需要・他媒体への移行・労働供給・在籍者構成は競合説明となる。'),
]
nb=nbf.v4.new_notebook(cells=cells)
nb.metadata={'kernelspec':{'display_name':'Python (dynamic local)','language':'python','name':'dynamic-local'},'language_info':{'name':'python','version':sys.version.split()[0]}}
k=H/'assets/kernels/dynamic-local'; k.mkdir(parents=True,exist_ok=True)
(k/'kernel.json').write_text(json.dumps({'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Python (dynamic local)','language':'python'}))
os.environ['JUPYTER_PATH']=str(H/'assets')+os.pathsep+os.environ.get('JUPYTER_PATH','')
nbf.write(nb,H/'analysis.ipynb')
client=NotebookClient(nb,timeout=240,kernel_name='dynamic-local',resources={'metadata':{'path':str(H)}})
client.execute()
nbf.write(nb,H/'analysis.ipynb')
print('Executed',sum(c.cell_type=='code' for c in nb.cells),'code cells; zero errors')
