# 文献・制度資料の確認記録

本文の角括弧は本フォルダ固有のcitation-ledger番号。今回取得・参照したURLから機械的に割り当てたため、未引用の補助一覧（台帳番号7）を挟んで定義資料が[8]となる。原資料は既存 `materials/` と `data/raw/` を読み取り専用で利用し、本文抽出を `evidence/` に保存した。外部資料と本報告の仮定を区別する。

| ID | 実際に確認した版・箇所 | 本案で使う根拠と限界 |
|---|---|---|
| [1] | Shapiro, MacDonald and Greenlaw (2022), *Principles of Microeconomics 3e*, OpenStax, §14.1 “Demand for Labor in Perfectly Competitive Output Markets”、図14.2–14.4、Derived Demand。web_extractで本文を取得。 | 資本固定の限界生産物逓減、利潤最大化の賃金＝限界生産物価値。本案のべき関数・求人写像・発効時期仮説は著者の式ではなく、授業用の追加仮定。 |
| [2] | Ohta and Komae (2022), Keio-IES DP2022-004（2022年3月9日）、29 PDF頁。本文p.2＝PDF p.4、§3.1–3.2 本文pp.6–8＝PDF pp.8–10、§4.3 本文p.12＝PDF p.14。 | 同じ公的紹介統計を用いた最も近い研究。採用・離職と雇用の区別、求人の受理地／就業地、パート求人の分析。2005–2019年の対数最低賃金パネル回帰であり、本案の2025年早期／後期・11月比較とは別の比較。§4.3はTable 5のパート結果を記述している。本案は表から未確認の数値を転載しない。 |
| [3] | Kazekami and Abe (2025), *Applied Economics*, DOI 10.1080/00036846.2025.2579945、既存の出版社版PDF、17頁。§II本文p.3＝PDF p.4、§III 本文pp.10–11＝PDF pp.11–12（図5前後の結果本文）。オンライン公表2025年11月14日（PDF先頭書誌頁）。 | 三大都市圏のパート求人広告、2019–2023年改定、賃金帯の欠落・超過を比較する。求人広告の純増を報告しており、一般に負と断定できない理由。本案は全国の受理人数であり、対象・指標・識別は同じでない。原文の大小が異なる集計率は本案で転載しない。 |
| [4] | Kanayama, Miyaji and Otani (2026), “Just After Minimum Wage Hikes: Short-Run Labor-Demand Response and Reallocation,” arXiv:2505.04555v3、59 PDF頁。表紙のCurrent version: March 17, 2026（arXiv印字は16 Mar）、§4 PDF pp.19–21、§5.2と図9 PDF pp.24–25。 | 2023年のTimee、県×月×賃金帯のDID。募集数を直接調べる既存研究。マッチングやスポットの延べ就業を通常雇用者数と同一視しない。§5.2で募集減少が主要な調整経路との著者解釈を確認。本案は労働供給や充足の経路をデータで識別しない。査読済み期刊版とは記さない。 |
| [5] | 厚生労働省「一般職業紹介状況」長期時系列表第12表、既存Excel（2026-10-26取得記録）。第12表-3の1行目タイトル、2行目の全国・47県、月次行を実際に解析。 | 2013年1月〜2026年8月の全164月から同比を計算し、2023年1月〜2026年8月の47県×44月を出力。全国合計・内訳恒等式は6シートを検査。データを再ダウンロードせず版を固定。 |
| [6] | 同「地域別最低賃金改定状況」既存Excel（同日取得記録）、シート先頭行の「令和６年度」「令和７年度」、3〜49行。 | 2024・2025年度の賃金と発効日。令和8年度も含むファイルなので位置を決め打ちせず年度ラベルで選ぶ。2025年度の一部発効日は2026年に及ぶ。列番号・全県日付は results/verification.json と results/policy.csv。 |
| [8] | 厚生労働省「用語の解説」、(4) パートタイム、(9) 就職件数、(10) 新規求人数、(11) 月間有効求人数、(12) 充足数。web_extractで本文を取得。 | 新規求人数＝新たに受理した採用予定人員。求人広告数、雇用者数、就職件数、有効求人数と混ぜない。 |

## 最近隣研究との比較と本案の増分

太田・小前は既に同じ統計のパート求人を分析しているため、「日本の求人を見る」「パートを見る」自体を新規性とはしない。[2] 風神・阿部もパート広告の改定前後比較を行い、純増を報告している。[3] Kanayamaほかも2023年改定後の募集数とマッチングを区別して調べる。[4] 本案は既発表の2025年11月の早期・後期差を県ごとに作って初めて検定し、基準を変えた時の安定性を明示する、授業内の限定的な記述的増分である。先行研究を新たな因果識別として置き換えるものではなく、世界初の主張もしない。

## 保存した根拠

- `evidence/openstax_excerpt.txt`：限界生産物条件の原文抜粋と書誌。
- `evidence/mhlw_definitions.txt`：公式定義の原文抜粋。
- `evidence/*Minimum_Wages*.txt`、`evidence/*Labor_Demand*.txt`：既存3論文のPDF本文を物理頁単位で抽出（図表の画像自体は元PDFを参照）。
- `evidence/workbook_provenance.txt`：実際のExcelの表題・年度列・サンプル行とファイルハッシュ。
- `citation-ledger.json`：URLと根拠原文の対応。補助の月次公表一覧（台帳番号7）は参照したが分析の根拠としては使わない。

以下のSourcesブロックはledgerから機械的に生成する。具体的な節・頁は上表で指定する。

## Sources

[1] https://openstax.org/books/principles-microeconomics-3e/pages/14-1-the-theory-of-labor-markets
[2] https://ies.keio.ac.jp/upload/DPEN_7694_202203091453351.pdf
[3] https://www.tandfonline.com/doi/full/10.1080/00036846.2025.2579945
[4] https://arxiv.org/pdf/2505.04555v3
[5] https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040505323&fileKind=0
[6] https://www.mhlw.go.jp/content/11200000/001756130.xlsx
[8] https://www.mhlw.go.jp/toukei/list/114-1_yougo.html
