---
marp: true
theme: default
size: 16:9
paginate: true
lang: ja
title: 最低賃金の発効時期と採用の構成
description: 課題3 2026-11-04 ミクロモデルと統計的な検証方法
math: katex
style: |
  @font-face { font-family: "NotoJP"; src: url("assets/NotoSansJP-Regular.otf") format("opentype"); }
  section { background: #fff; color: #000; font-family: "NotoJP", "Noto Sans CJK JP", sans-serif; font-size: 26px; line-height: 1.48; padding: 40px 56px 54px; justify-content: flex-start; }
  h1, h2, h3, strong { color: #000; }
  h1 { font-size: 36px; margin: 0 0 16px; line-height: 1.25; }
  h2 { font-size: 27px; margin: 12px 0 8px; }
  p { margin: 10px 0; }
  ul { padding-left: 1.05em; margin: 6px 0; }
  li { margin: 9px 0; }
  section table { width: 100% !important; font-size: 23px; margin: 14px 0; border-collapse: collapse; table-layout: fixed; display: table !important; }
  th, td { color: #000; background: #fff !important; border-bottom: 1px solid #777; padding: 8px; }
  th { border-top: 1.5px solid #000; }
  section::after { color: #666; font-size: 14px; right: 26px; bottom: 16px; }
  .source { position: absolute; left: 56px; right: 80px; bottom: 16px; font-size: 14px; line-height: 1.3; color: #333; }
  .small { font-size: 21px; line-height: 1.42; }
  .note { font-size: 22px; background: #f2f2f2; padding: 10px 14px; margin: 14px 0; }
  blockquote { font-size: 22px; color: #000; background: #f2f2f2; padding: 10px 14px; margin: 14px 0; border: 0; }
  section.title { justify-content: center; }
  section.title h1 { font-size: 44px; margin-bottom: 20px; }
  section.title h2 { font-size: 28px; font-weight: 400; margin-bottom: 26px; }
  section.refs { font-size: 16px; line-height: 1.35; }
  section.refs h1 { font-size: 34px; }
  section.refs p { margin: 10px 0; }
  img { display: block; margin: 8px auto; }
  .katex { font-size: 1.05em; }
  .katex-display { margin: 18px 0; overflow: visible; }
  .katex-display > .katex { font-size: 30px; }
  section.equations { font-size: 24px; line-height: 1.4; }
  section.equations li { margin: 8px 0; }
---

<!-- _class: title -->

# 最低賃金の発効時期と採用の構成

## ミクロモデルと統計的な検証方法

企業の採用選択から、求人の規模と構成の予測を導く。
その予測を、県別の早期・後期比較でどう調べるかを定める。

<div class="small">2026年11月4日　ミクロ経済学セッション　課題3<br>SHEN MINGWEI・SUN SHAOHAN・WANG JING</div>

<!-- notes: 今週は、企業がパートとパート以外を何人ずつ採用するかをモデル化し、観測できる求人データで何をどう比較するかを説明します。数値の代入、実際の推定結果とその解釈は、次回十一月十一日の課題四で扱います。 -->

---

# 先行研究に対して、何を追加するのか

- Ohta・Komae（2022）は、2005〜2019年のハローワーク新規求人で最低賃金への弾力性を推定。Table 5ではパートの反応がフルタイムより大きい。
- Kanayamaほか（2026）は改定直後の募集減少を、Kazekami・Abe（2025）は求人広告の純増を報告。媒体・時期が違えば結果も異なる。

<div class="note">本報告の追加の問い：発効時期別のパート求人の差は、合計求人の差を伴うのか、パート以外に対する相対的な差なのか。</div>

賃上げ幅の弾力性ではなく、2025年11月の早期・後期差を記述する。
規模と構成を併記する授業内の拡張で、機序を識別した研究でも、初めて二種類の求人を扱う研究でもない。

<div class="source">Ohta and Komae (2022), 4.3節・Table 5（DP版）；Kanayama et al. (2026), v3；Kazekami and Abe (2025), online版。書誌情報は末尾の参考文献。</div>

<!-- notes: 一番近い先行研究は同じハローワークの求人を使った太田・小前です。彼らは最低賃金の変化に対する弾力性を推定しており、本報告の発効時期の比較とは異なります。二種類の求人を見ること自体を新発見とは呼ばず、前回の問いに規模と構成の区別を加えたと位置付けます。 -->

---

# 数えているのは、新しく受理された採用予定人員

| 系列 | 第12表の区分 | この発表での呼び方 |
|---|---|---|
| 一般パートタイム | 第12表－3 | パート（P） |
| パートを除く一般 | 第12表－2 | パート以外（N） |
| パートを含む一般 | 第12表－1 | 合計（P＋N） |

- 単位は人。広告の件数、実際の採用人数、雇用者数ではない。
- ハローワークの受理地別。勤務地別でも、全媒体の合計でもない。
- パートは所定労働時間による区分。パート以外は正社員だけではなく、非正規や臨時・季節の求人も含む。

<div class="small">観測単位は県×月、主比較は2025年。系列の定義はP＋N＝合計。原表の整合性・欠損・正値は計算時に確認する。</div>

<div class="source">厚生労働省（2026a）第12表－1〜3、同省「集計結果（用語の解説）」(4)(5)(10)。</div>

<!-- notes: まず人数の意味を固定します。求人が十人なら十件の広告という意味でも、十人が採用されたという意味でもありません。また、パート以外を正社員と読み替えるとモデルとデータの対応を誤ります。受理した県と実際の勤務地が一致するとも限りません。 -->

---

# 発効時期による比較の設計

2025年11月を比較月とし、発効時期で県を分ける。

| 2025年度の発効時期 | 記号 | 2025年11月の適用状態 |
|---|---|---|
| 10月発効：早期 | $E$、県数 $n_E$ | 全月が新最低賃金 |
| 11月発効 | 主比較から除外 | 月内の適用状態がそろわない |
| 12月以降発効：後期 | $L$、県数 $n_L$ | 全月が旧最低賃金 |

同じ月・同じ統計・同じ前年同月比で比較する。
各県を等しく重み付けし、全国の求人総数とは区別する。

<div class="note">発効時期は無作為ではない。最低賃金水準・引上げ幅・需要・先取り調整の違いが残るため、群間差をそのまま因果効果とは呼べない。</div>

<div class="source">厚生労働省（2026b）；前回発表（2026-10-28）の分群規則を維持。11月1日発効県も同じ規則で除外。</div>

<!-- notes: ここでは県数を代入せず、早期群をE、後期群をLと書きます。十一月発効県を一括して除外する前回の規則を引き継ぎます。一日発効県もこの規則に含まれます。後期群も改定予定を知っているため、完全に政策の影響を受けていない群とは限りません。 -->

---

<!-- _class: equations -->
# 企業は、二種類を何人ずつ採用するか選ぶ

新しい部門を作る企業を考える。既存従業員・補充採用はなく、
採用人数 $H_P,H_N$ がその期間の労働投入になると仮定する。

$$
\max_{H_P,H_N\geq0}\;\Pi=\frac{B}{\beta}Z^\beta-c_PH_P-c_NH_N
$$

$Z$ は二種類で生む生産サービス、$B>0$ は収入の大きさ。
$0<\beta<1$ なので、$Z$ を増やすほど追加収入は小さくなる。

$$
c_j=h_jw_j+k_j,\qquad w_j=\max\{w_j^0,m\},\quad j=P,N
$$

$c_j$：採用1人の費用（円／人）＝期間労働時間 $h_j$ × 時給 $w_j$ ＋採用経費 $k_j$。$m$ は最低時給、$w_j^0$ は改定がない場合の時給。賃金・時間は所与で、企業は人数を選ぶ。

<div class="source">CESの基礎はAcemoglu and Autor (2011)。新規部門、収入関数、期間賃金＋採用経費は本報告の追加仮定。</div>

<!-- notes: 例えば新しい売場のスタッフを何人ずつ採るかを考えます。目的は売上から期間賃金と採用経費を引いた利潤を最大にすることです。最低賃金が直接費用を上げるのは、それが拘束的な類型です。現実にパートだけが拘束されると決め付けるわけではありません。既存の従業員がいないという強い簡略化は最後まで維持します。 -->

---

<!-- _class: equations -->
# CESは、二種類をどう組み合わせて使えるかを表す

$$
Z=\left[aH_P^\rho+(1-a)H_N^\rho\right]^{1/\rho},\qquad
\rho=\frac{\sigma-1}{\sigma}
$$

- $Z$ は単なる人数の和ではなく、二種類を合成したサービス量。
- $0<a<1$ はPをどれだけ重視するかの重み。人数比率ではない。
- $\sigma>0$ は代替の弾力性。大きいほど、割高になった類型からもう一方へ組合せを変えやすい。
- $\rho$ は $\sigma$ から決まる指数で、独立の行動パラメータではない。

<div class="note">完全に同じ仕事とも、常に一対一で必要とも決めない。CESはその中間を表す標準的な関数である。</div>

<div class="source">Acemoglu and Autor (2011), 式(2)〜(6), pp.1103–1105を二類型に応用。σ＝1は極限のCobb–Douglas形。</div>

<!-- notes: CESという略語を覚えるより、組合せの変えやすさを一定の弾力性で表すと理解してください。どちらを一人増やしても同じサービスが生まれるとは仮定しません。重みaと実際のパート比率は別物です。元の文献は技能別の投入を扱い、ここでのパートとパート以外という読み替えは授業用の応用です。 -->

---

<!-- _class: equations -->
# 追加の1人が生む収入と、費用が等しくなる

両種類を正の人数だけ採る場合（内点解）、「もう1人」の追加収入が $c_j$ と等しくなる。

$$
\frac{\partial\Pi}{\partial H_P}
=BZ^{\beta-1}\frac{\partial Z}{\partial H_P}-c_P=0
$$

CESを微分して代入すると、二種類それぞれの条件は

$$
\begin{aligned}
aBZ^{\beta-\rho}H_P^{\rho-1}&=c_P,\\[0.5em]
(1-a)BZ^{\beta-\rho}H_N^{\rho-1}&=c_N.
\end{aligned}
$$

左辺が費用より大きければ、その類型を増やす余地がある。
同じ企業なので、$B$ と $Z$ の部分は二つの条件に共通する。

<div class="source">前頁のCESとp.5の利潤から導出。正の費用・重みを置いた内点解。完全な条件はmethods.md。</div>

<!-- notes: 一階条件は、追加収入と追加費用を比べるいつもの利潤最大化です。最初の式では収入のZに関する微分と、Zの人数に関する微分を掛けています。二種類には同じ企業全体の収入項が掛かるので、次に二つの条件を割ると人数の比が簡単に求まります。 -->

---

<!-- _class: equations -->
# 二つの条件を割ると、相対需要が分かる

共通の $BZ^{\beta-\rho}$ を消し、$\rho-1=-1/\sigma$ を使う。

$$
\frac{c_P}{c_N}=\frac{a}{1-a}
\left(\frac{H_P}{H_N}\right)^{-1/\sigma}
$$

人数比について解くと

$$
\frac{H_P}{H_N}=\left(\frac{a}{1-a}\right)^\sigma
\left(\frac{c_N}{c_P}\right)^\sigma,\qquad
\frac{\partial\ln(H_P/H_N)}{\partial\ln c_P}=-\sigma
$$

$c_N$ と $a$ が一定なら、Pの費用上昇はP/Nを下げる。

<div class="note">これは「PがNに対して減る」という予測。Nの人数自体が増えるかどうかは、まだ分からない。</div>

<div class="source">Acemoglu and Autor (2011) の相対要素需要の考え方を本報告の費用に適用。</div>

<!-- notes: 割ることで全体の規模が消え、組合せだけが残ります。Pの費用が高くなればP対Nの比は下がりますが、例えば両方減ってPの減り方が大きい場合も同じ結果になります。したがって、この式だけで非パートが増えるとは言えません。 -->

---

<!-- _class: equations -->
# 組合せを決めた後、企業全体の規模を決める

$C$ をサービス1単位の最小費用とする（円／サービス単位）。

$$
C=\left[a^\sigma c_P^{1-\sigma}+(1-a)^\sigma c_N^{1-\sigma}\right]^{1/(1-\sigma)}
$$

最適な組合せなら費用は $CZ$。企業の問題は規模 $Z$ の選択になる。

$$
\max_{Z\geq0}\left\{\frac{B}{\beta}Z^\beta-CZ\right\},\qquad
BZ^{\beta-1}=C
$$

$$
Z^*=\left(\frac{B}{C}\right)^{1/(1-\beta)}
$$

費用 $C$ が上がると最適規模は下がる。$\beta$ が大きいほど、
追加収入が緩やかに低下するため、費用変化への規模反応は大きい。

<div class="source">CESの費用最小化と本報告の収入関数から導出。σ＝1の単位費用はmethods.mdに記載。</div>

<!-- notes: 前頁は比だけでした。ここではその比を使って最も安くサービスを作ったときの単価Cを考えます。企業は追加収入とCが等しくなるまで規模を選びます。Cは一人当たり費用でも求人合計でもありません。この規模の調整が、非パートへの代替を打ち消す可能性があります。 -->

---

<!-- _class: equations -->
# パート以外には、代替と規模縮小が同時に働く

Pの費用 $c_P$ だけが上がり、$c_N$ は一定の場合を考える。

$$
H_N=Z^*(1-a)^\sigma\left(\frac{C}{c_N}\right)^\sigma,\qquad
s_P=\frac{c_PH_P}{c_PH_P+c_NH_N}
$$

$s_P$ は費用に占めるPの割合で、求人の人数比率ではない。
$\partial\ln C/\partial\ln c_P=s_P$ より、

$$
\frac{\partial\ln H_N}{\partial\ln c_P}
=\underbrace{\sigma s_P\vphantom{\frac{s_P}{1-\beta}}}_{\text{Substitution}}
-\underbrace{\frac{s_P}{1-\beta}}_{\text{Scale}}
$$

- 代替：同じサービス量なら、割高なPを避けてNを増やす。
- 規模：サービス量自体を減らせば、Nも減らす。

> $\sigma>1/(1-\beta)$ ならNは増え、逆なら減る。Nは「無処理の対照」とは呼べない。

<!-- notes: 対数を取ると、Nの変化はZの変化と組合せの変化に分かれます。固定した規模での代替はプラスですが、利潤最大化で規模が縮む分はマイナスです。費用が直接変わらないNでも動くため、パート以外を未処理の対照にする解釈は成り立ちません。 -->

---

<!-- _class: equations -->
# 採用のモデルを、観測できる求人の予測につなぐ

求人枠 $V_j$ のうち割合 $q_j$ が採用されると仮定する。

$$
H_j=q_jV_j,\qquad \frac{V_P}{V_N}=\frac{q_N}{q_P}\frac{H_P}{H_N}
$$

$q_P,q_N$ が一定なら、採用比の予測を求人比にも移せる。

| 条件付きの費用変化 | 求人合計 | P/N | N単独 |
|---|---|---|---|
| 両方が同じ率で上昇 | 減る | 不変 | 減る |
| Pだけが上昇 | 規模と構成が変わる | 下がる | 増減どちらも可 |

<div class="small">県集計への適用には、企業構成・需要・充足率・募集媒体が比較可能という追加条件が必要。現実のNにも最低賃金は適用される。費用差や充足率は本データから測れていない。</div>

<div class="note">検証する候補：Pの早期−後期差は負か。さらに、合計とP/Nも見て、その差の形を記述する。</div>

<!-- notes: 現実に見えるのは採用Hではなく募集Vです。充足率が変われば、採用の比が変わらなくても求人の比が変わりえます。モデルを県の統計に移すにはさらに企業構成などの条件が必要です。ここでの表は条件付き予測で、どの条件が現実に成立するかをこの統計だけで特定するものではありません。 -->

---

<!-- _class: equations -->
# 求人を、前年同月比・相対・比率に変換する

県 $i$、月 $t$、系列 $j=P,N,T$（$T=P+N$）について、

$$
y^j_{i,t}=100\left(\ln V^j_{i,t}-\ln V^j_{i,t-12}\right)
$$

人数ではなく増減率の近似。毎年繰り返す季節性をある程度抑える。

$$
y^R_{i,t}=y^P_{i,t}-y^N_{i,t}
=100\,\Delta_{12}\ln(V^P_{i,t}/V^N_{i,t})
$$

相対 $R$ は、PがNより強く減れば負になる。

$$
S_{i,t}=\frac{V^P_{i,t}}{V^P_{i,t}+V^N_{i,t}},\qquad
y^S_{i,t}=100(S_{i,t}-S_{i,t-12})
$$

$\Delta_{12}$ は前年同月との差。比率変化 $y^S$ の単位はポイント。
水準のP/NとSは単調に対応するが、差分・県平均の後は同値ではない。同じ原系列の補助指標で、独立の証拠ではない。

<!-- notes: 前年同月比は通常の増減率と完全に同じではなく対数差の百倍です。相対指標はPの前年同月比からNの前年同月比を引きます。一方、比率は全体に占めるPの割合の前年差です。水準の単調な関係を理由に、差分や平均の後も同じ推定量だとは言えません。 -->

---

<!-- _class: equations -->
# 標準DID回帰：処置群・事後・交互作用

県 $i$、指標 $j=P,N,T,R,S$ について、月次指標を2時点に集約する。
前期は2025年1〜9月の平均、後期は11月の値を使う。

$$
Y_{i0}^j=\bar y^j_{i,\mathcal B},\qquad Y_{i1}^j=y^j_{i,\mathrm{Nov}}
$$

- $\mathrm{Treat}_i=1$：10月発効の早期県。$0$：12月以降発効の後期県。
- $\mathrm{Post}_t=0$：前期（$t=0$）。$1$：後期（$t=1$）。

各県を等しく扱い、指標ごとに次の式をOLSで推定する。

$$
Y_{it}^j=\alpha^j+\beta^j\mathrm{Treat}_i+\gamma^j\mathrm{Post}_t
+\delta^j(\mathrm{Treat}_i\times\mathrm{Post}_t)+\varepsilon_{it}^j
$$

<div class="small">一県につき前期・後期の2観測。11月発効県は除外する。Yは前頁で定義した同比・相対・比率変化であり、求人数の水準ではない。</div>

<!-- notes: 標準的なDIDの形で、処置群の指標、事後の指標、その交互作用を入れます。ここで時点は月をそのまま並べるのではなく、前期と後期の二つです。前期は一月から九月の月次指標の平均、後期は十一月の値とし、一県に二観測を置きます。Treatは十月発効県で一、十二月以降の発効県でゼロ、Postは後期だけ一です。Yには前頁の同比や相対指標を使い、求人数そのものは入れません。回帰のベータは前期の群間差であり、企業モデルの収入曲率ベータとは別の記号です。誤差項は群と時点の平均からの県ごとのずれを表します。 -->

---

<!-- _class: equations -->
# 交互作用の係数が、二群の変化の差を表す

$\alpha^j$ は後期群の前期平均、$\beta^j$ は前期の早期−後期差、
$\gamma^j$ は後期群の前後変化を表す。

| 回帰式が表す平均 | 前期：Post＝0 | 後期：Post＝1 |
|---|---|---|
| 後期発効群（L） | $\alpha^j$ | $\alpha^j+\gamma^j$ |
| 早期発効群（E） | $\alpha^j+\beta^j$ | $\alpha^j+\beta^j+\gamma^j+\delta^j$ |

$$
\widehat{\delta}^j=
(\bar Y_{E1}^j-\bar Y_{E0}^j)-(\bar Y_{L1}^j-\bar Y_{L0}^j)
$$

$\widehat{\delta}^P<0$ は、パートの前後変化が早期群でより低いことを示す。
主仮説は負方向の片側5%検定。$N,T,R,S$ も同じ式で比較する。

$$
H_0:\delta^P\geq0,\qquad H_1:\delta^P<0
$$

<div class="note">因果解釈には、改定がなければ二群のYの変化が同じという平行トレンド等の条件が必要。ここでは平均変化の差として扱う。</div>

<!-- notes: 表の左上を出発点にします。後期群の前期平均がアルファ、前期の群間差がベータ、後期群の前後変化がガンマです。早期群の前後変化はガンマにデルタを足したものなので、二群の変化を引くとデルタが残ります。同じ標本と県の重みを使えば、交互作用係数の推定値は従来の平均変化の差と同じです。主仮説はパートのデルタが負かどうかで、推論は補足のWelch方式を用います。DIDという式にしても平行トレンドが確認されたことにはならず、因果解釈には改定がない場合の同比指標の動きが比較可能という条件などが必要です。棄却できなくても差がないとは言えません。 -->

---

# 次回の計算と、解釈の条件

- 主比較は1〜9月基準。公表後の先取り調整を考慮し、1〜7月基準も感度分析として併記する。
- 各系列の月別推移と県内変化を確認し、回帰係数・信頼区間を示す。パートの係数について主仮説を検証する。
- 合計と相対指標をモデルの条件付き予測と照合する。仮定値のモデル例は、実データの推定と区別する。

<div class="note">モデルから分かるのは条件付きの方向。Nにも代替と規模縮小が及び、Nを「未処理の対照」とは扱えない。</div>

<div class="small">前年同月比には前年の政策も影響する。発効時期・需要・企業構成・充足率・募集媒体の差が残り、求人の変化を採用や雇用の変化と同一視できない。新規部門・既存従業員なしというモデルの簡略化にも注意する。</div>

<!-- notes: 次回はここで定めたDID回帰に数値を入れ、どの予測と整合するか、どこまで判断できないかを報告します。主基準と補助基準を併記し、結果に合わせて比較月や群を選び直さないようにします。理論を足すだけで因果識別が強くなるわけではなく、費用や充足率を観測できていない点が解釈の条件です。 -->

---

<!-- _class: refs -->
# 参考文献・データ

Acemoglu, D. and D. Autor (2011), “Skills, Tasks and Technologies: Implications for Employment and Earnings,” *Handbook of Labor Economics* 4B, ch.12, pp.1043–1171（刊行章；使用箇所pp.1103–1105）. [本文PDF](https://economics.mit.edu/sites/default/files/publications/Skills%2C%20Tasks%20and%20Technologies%20-%20Implications%20for%20.pdf)

Ohta, S. and K. Komae (2022), “Vacancies, Job Seekers, and Minimum Wages: Evidence from Public Employment Placement Service Data,” Keio-IES DP2022-004（2022年3月DP版）, 4.3節・Table 5. https://ies.keio.ac.jp/upload/DPEN_7694_202203091453351.pdf

Kanayama, H., S. Miyaji and S. Otani (2026), “Just After Minimum Wage Hikes: Short-Run Labor-Demand Response and Reallocation,” arXiv v3. https://arxiv.org/pdf/2505.04555v3

Kazekami, S. and M. Abe (2025), “Effects of minimum wage changes on labor demand: analysis using job postings data,” *Applied Economics*（2025年11月14日online版）. https://doi.org/10.1080/00036846.2025.2579945

厚生労働省（2026a）「一般職業紹介状況 長期時系列表 第12表 都道府県（受理地）別 雇用形態別 新規求人数」（2026年10月26日取得）. [e-Stat Excel](https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040505323&fileKind=0)

厚生労働省（2026b）「地域別最低賃金改定状況」（同日取得）. https://www.mhlw.go.jp/content/11200000/001756130.xlsx<br>同省「令和7年度 地域別最低賃金額一覧」p.3. https://www.mhlw.go.jp/content/11201250/001729623.pdf<br>同省「集計結果（用語の解説）」. https://www.mhlw.go.jp/toukei/list/114-1_yougo.html

<!-- notes: データと文献の出所です。CESは刊行章の該当ページ、求人類型別の推定は太田・小前のDP版を参照しています。原文で確かめた範囲と、本報告で追加した仮定の区別はsourcesとmethodsにも残しています。 -->

---

<!-- _class: equations -->
# 補足：回帰係数の標準誤差と検定

県内差 $d_i^j=Y_{i1}^j-Y_{i0}^j$ の式は、$d_i^j=\gamma^j+\delta^j\mathrm{Treat}_i+u_i^j$。
$s_g^2$ は群 $g=E,L$ 内の県内差の不偏分散、$n_g$ は県数。

$$
v_g=\frac{s_g^2}{n_g},\qquad
SE(\widehat{\delta}^j)=\sqrt{v_E+v_L}
$$

$$
\nu=\frac{(v_E+v_L)^2}
{v_E^2/(n_E-1)+v_L^2/(n_L-1)}
$$

主仮説の境界0で左側p値を求め、各指標に両側95%区間を併記する。

$$
t=\frac{\widehat{\delta}^P}{SE(\widehat{\delta}^P)},\qquad
p_{\mathrm{left}}=F_\nu(t)
$$

$$
\widehat{\delta}^j\ \pm\ t_{\nu,\,0.975}\,SE(\widehat{\delta}^j)
$$

<div class="small">県の独立性を置くWelch近似。同じ県の2観測を独立とは扱わず、県内差から推論する。既定のOLS標準誤差・自由度・両側p値とは区別する。</div>

<!-- notes: DID式で同じ県の後期から前期を引くと、アルファとベータが消え、ガンマとデルタTreatが残ります。差分後の切片はアルファではなくガンマ、誤差uは元の誤差の前後差です。これを一県一観測として扱い、従来のWelch方式を維持します。同じ県の二時点を独立とみなすのではありません。各群の県内差の不偏分散を県数で割り、二群分を足して標準誤差を作ります。自由度もWelchの式で求めます。Fはt分布の累積分布関数、区間のtは九十七・五パーセント分位点です。通常のOLS出力の等分散標準誤差や既定の両側p値とは区別します。相対指標は県内でパートから非パートを引き、共分散を保ちます。県どうしの相関や発効時期の内生性は、この推論で解消されません。 -->
