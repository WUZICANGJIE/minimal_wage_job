# 出典・版・照合箇所

本ファイルはURL発見記録だけではなく、今回読んだ本文の箇所と使用範囲を記録する。日付は実行ログに依存し、課題日2026-11-04を取得日と偽記しない。原資料は`evidence/`、ハッシュ・取得方式は`source-inventory.json`。研究資料の既存アーカイブは変更せず、必要な原本を本成果物へ複写した。以下の番号は独立の`citation-ledger.json`から発行した。

| ID | 資料・版／今回確認した箇所 | 何を支えるか・注意 |
|---|---|---|
| [1] | 厚労省・e-Stat、第12表長期時系列XLSX。第12表-1、-2、-3、2013-01〜2026-08。第3シート名「一般パート」、Excel第2行の県名、第3列の月 | 新受理の採用予定人員・受理地。全164月・47県・全国計・3内訳を再計算。主分析は2023-01〜2026-08。民間媒体・就職件数と異なる。データ辞書はdata/README.mdと既発表資料も照合 |
| [2] | 厚労省「地域別最低賃金改定状況」XLSX、令和5・6・7年度の見出し、行3〜49。0始まり列43/45/47が額、その右が発効日 | 2023/24/25の政策カレンダー。追加された令和8年度を誤って使わない。47県名・20/13/14群・越年日付を照合 |
| [3] | Hamermesh, D.S. (1993), *Labor Demand and the Source of Adjustment Costs*, NBER WP4394, July 1993。III節本文p.3、III.A pp.4–5、式(1)〜(5)（PDF物理pp.5–7） | 本案の直接の基礎。gross/netの二次費用、H=L−L(-1)+Q、期待割引利潤、将来賃金への依存。スキャンなので**原図を視認**。本案は二期・一定q/r・grossだけ・期末価値ゼロ等を追加した独自簡略化 |
| [4] | Hamermesh (1990), *A General Model of Dynamic Labor Demand*, NBER WP3356。II節本文p.2（PDF p.4）を原図で確認。公開ページの表題は"Genral"表記 | 固定費＋二次のnet調整費用という別モデル。理論部分は静的期待。将来賃金の式をこの文献へ誤帰属しない。1992年の公刊版とWPは区別し、公刊版の全文を読んだとは言わない |
| [5] | Kudlyak, M., M. Tasci and D. Tüzemen, *Minimum Wage Increases and Vacancies*, IZA DP15254, **January 2023改訂版**。本文pp.1–4、§2.3、§4.2本文pp.18–19、Figures 7–8（PDF pp.21–24）。公刊情報はLabour Economics 97 (2025), 102765, DOI:10.1016/j.labeco.2025.102765 | 先取り・その後の求人動学は既存論点。2005–18米国職業×county×四半期、職業曝露DDD、HWOL stockとnew(30日未満)。今回の分析的な引用は2023版本文に限定。日本の早遅比較に係数・識別を移さない |
| [6] | Ohta, S. and K. Komae (2022), Keio-IES DP2022-004。§4.3本文p.12、Table 5本文p.19（PDF pp.14,21） | 同じ受理地のpart求人。全期間は負、後期はpart列(5)−.813非有意・(6)−.896が10%有意で、単純に「後期は全部非有意」としない。群差の有意性を係数ごとの有意性から推論しない |
| [7] | Kazekami, S. and M. Abe (2025), *Effects of minimum wage changes on labor demand: analysis using job postings data*, Applied Economics、公刊PDF。§II本文pp.3,7–8、§III、Figure 5以降 | 三大都市圏のpart広告、2019–23改定。賃金帯DID、July/August対September/October。純増も報告する対照的証拠。抽象の割合を本研究の数字として転用しない。求人と雇用を同一視しない |
| [8] | 厚労省2025-08-04「令和7年度地域別最低賃金額改定の目安について」、本文の審議経過・答申ポイント | 目安の公表日、7月11日の諮問・審議開始。これ以前に予期がゼロだったとは支えない |
| [9] | 厚労省2025-09-05「全ての都道府県で地域別最低賃金の答申がなされました」、本文 | 答申の集約と予定発効日。異議・決定前の**予定**と最終発効日を区別。実証の最終日付は[2]を使用 |
| [10] | 中央最低賃金審議会2026-06-23「令和7年度地方最低賃金審議会の審議結果を踏まえた論点と考え方の整理」。§3(1)本文pp.3–4、§3(2)pp.4–6、参考資料1・2 | 引上げ額と発効日の関連、準備・災害・年収の壁、求人賃金の先行変化。未達求人割合は繰返し横断面で、同一企業の賃上げ日ではない。求人件数の先取り減少を直接証明しない。PDFの参考資料1にある「＋16円」等は**目安への上乗せ**で、前年からの総引上げ額と混同しない |
| [11] | 厚労省「令和6年度地域別最低賃金額改定状況」1頁 | 2024全47県の額と日付を[2]とコード照合、全一致。徳島2024-11-01。前年を無政策placeboと呼ばない |
| [12] | Nowcast・連合、余野京登・市川祐衣、2026-07-07共同分析、§§2–4 | 上位10サイト、東北/九州の早遅群平均募集賃金と東京の求人退出。時期研究の最近隣だが、労働者の所得・同一企業の賃上げ・求人数量を分けて読む。本文の全国「＋63円」は目安との混同のおそれがあり、本案の政策値は[2]で再計算し継承しない |

## スキャン本文の確認記録

`h1-p1.png`で1993論文の著者・題名・WP番号・July 1993を確認した。`h1-p5.png`の本文p.3で同質労働・固定工時・裁員なし、`h1-p6.png`の本文p.4で式(1)〜(3)、`h1-p7.png`の本文p.5で将来賃金を含む解を視認した。`h0-p4.png`の1990論文本文p.2は静的期待・固定費・二次net調整費用である。PDFテキスト抽出が空でも、仮のOCRを生成して全文確認済みとは扱わない。`Hamermesh_visual_transcription.txt`は**視認した短い英語部分の手転記**で、全文OCRではない。

## 引用・事実・独自結果

本案の式・比較静学は`methods.md`の独自簡略化、数字は`analysis.py`の実行結果。文献の実証結果・制度事実と区別する。行政資料と刊行論文のネットワーク取得に加え、以前取得された原本も再読した。Hamermesh2本は視認対象ページだけを確認しており、全文通読を主張しない。資料URLと本文証拠の対応は`verify_delivery.py`で検査する。

## Sources

[1] https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040505323&fileKind=0 — 一般職業紹介状況 第12表
[2] https://www.mhlw.go.jp/content/11200000/001756130.xlsx — 地域別最低賃金改定状況
[3] https://www.nber.org/system/files/working_papers/w4394/w4394.pdf — Hamermesh 1993 NBER WP4394
[4] https://www.nber.org/system/files/working_papers/w3356/w3356.pdf — Hamermesh 1990 NBER WP3356
[5] https://docs.iza.org/dp15254.pdf — Kudlyak Tasci Tuzemen IZA DP15254 Jan2023
[6] https://ies.keio.ac.jp/upload/DPEN_7694_202203091453351.pdf — Ohta Komae 2022 DP2022-004
[7] https://www.tandfonline.com/doi/full/10.1080/00036846.2025.2579945 — Kazekami Abe 2025 published
[8] https://www.mhlw.go.jp/stf/newpage_60788.html — 2025-08-04目安公表
[9] https://www.mhlw.go.jp/stf/newpage_63030.html — 2025-09-05答申まとめ（予定）
[10] https://www.mhlw.go.jp/content/11201250/001714252.pdf — 2026-06-23発効時期の検討
[11] https://www.mhlw.go.jp/content/11302000/001531874.pdf — 2024年度確定一覧
[12] https://nowcast.co.jp/news/20260707 — Nowcast 2026-07-07 最低賃金・募集賃金・求人量
