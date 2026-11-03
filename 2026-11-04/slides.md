---
marp: true
theme: default
size: 16:9
paginate: true
lang: ja
title: 最低賃金の発効時期と採用の構成
description: 課題3 2026-11-04 パート求人だけが弱くなるのか、求人全体が縮むのか
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
  section.title { justify-content: center; }
  section.title h1 { font-size: 44px; margin-bottom: 20px; }
  section.title h2 { font-size: 28px; font-weight: 400; margin-bottom: 26px; }
  section.refs { font-size: 16px; line-height: 1.3; }
  section.refs h1 { font-size: 34px; }
  section.refs p { margin: 8px 0; }
  img { display: block; margin: 8px auto; }
  .katex { font-size: 1.05em; }
  .katex-display { margin: 18px 0; overflow: visible; }
  .katex-display > .katex { font-size: 30px; }
  section.equations { font-size: 24px; line-height: 1.4; }
  section.equations li { margin: 8px 0; }
---

<!-- _class: title -->

# 最低賃金の発効時期と採用の構成

## パート求人だけが弱くなるのか、求人全体が縮むのか

<div class="small">2026年11月4日　ミクロ経済学セッション　課題3<br>SHEN MINGWEI・SUN SHAOHAN・WANG JING</div>

<!-- notes: 今週は、企業がパートとパート以外を何人ずつ採用するかをモデル化し、観測できる求人データで何をどう比較するかを説明します。数値の代入、実際の推定結果とその解釈は、次回十一月十一日の課題四で扱います。 -->

---

# データ：ハローワークの新規求人数

| 系列 | 第12表の区分 | この発表での呼び方 |
|---|---|---|
| 一般パートタイム | 第12表－3 | パート（P） |
| パートを除く一般 | 第12表－2 | パート以外（N） |
| パートを含む一般 | 第12表－1 | 合計（P＋N） |

- 各月に受理した採用予定人数を、都道府県別に集計する。
- パートは所定労働時間で区分し、P＋Nを求人合計とする。

<div class="small">観測単位は県×月。主比較は2025年。</div>

<div class="source">厚生労働省（2026a），第12表-1〜3；厚生労働省（n.d.-b），(4)(5)(10)。</div>

<!-- notes: 使うデータはハローワークが受理した新規求人の人数です。パートをP、パート以外をNとし、両者を足した合計も見ます。 -->

<!-- qa: Q：求人数と採用・雇用は同じか。
A：新規求人数は採用予定人数です。実際に採用できた人数や雇用者数は別の指標です。

Q：Nは正社員を意味するか。
A：Nはパートを除く一般求人で、非正規や臨時・季節の求人も含みます。集計地域はハローワークの受理地です。 -->

---

# 発効時期による比較の設計

2025年11月を比較月とし、発効時期で県を分ける。

| 2025年度の発効時期 | 記号 | 2025年11月の適用状態 |
|---|---|---|
| 10月発効：早期 | $E$、県数 $n_E$ | 全月が新最低賃金 |
| 11月発効 | 主比較から除外 | 月内の適用状態がそろわない |
| 12月以降発効：後期 | $L$、県数 $n_L$ | 全月が旧最低賃金 |

各県を等しく重み付けし、基準期から11月までの変化を比べる。

<div class="source">厚生労働省（2026b）；厚生労働省（n.d.-a），p. 3。</div>

<!-- notes: 十一月には、早期県は全月が新最低賃金、後期県は全月が旧最低賃金になります。この二群について、基準期からの変化を県ごとに計算し、同じ重みで比べます。 -->

<!-- qa: Q：発効時期による比較を因果効果と読めるか。
A：発効時期は無作為ではなく、賃金水準、引上げ幅、需要や先取り調整の違いが残ります。因果解釈には平行トレンドなどの条件の確認が必要です。

Q：11月1日発効県は含めるか。
A：前回からの統一ルールに従い、11月発効県は一括して除外します。 -->

---

<!-- _class: equations -->
# 企業の利潤最大化問題

新設部門で、パート $H_P$ 人とパート以外 $H_N$ 人を採用する。

$$
\max_{H_P,H_N\geq0}\;\Pi=\frac{B}{\beta}Y^\beta-c_PH_P-c_NH_N
$$

$Y$ は生産量、$B>0$ は収入の規模を表すパラメータ。
$0<\beta<1$ のため収入関数は凹で、限界収入は逓減する。

$$
c_j=h_jw_j+k_j,\qquad w_j=\max\{w_j^0,m\},\quad j=P,N
$$

1人当たり費用 $c_j$ は、労働時間 $h_j$ × 時給 $w_j$ ＋採用経費 $k_j$。
$m$ は最低時給、$w_j^0$ は改定がない場合の時給。

<!-- notes: 新設部門における企業の利潤最大化問題です。賃金と労働時間を所与として、二類型の採用人数を選びます。収入関数は凹で、限界収入が逓減します。最低賃金が拘束的な類型では、一人当たり費用が上昇します。 -->

<!-- qa: Q：既存従業員や補充採用はどう扱うか。
A：新設部門を想定し、既存従業員と補充採用を省略しています。この期間の採用人数を労働投入とする簡略モデルです。

Q：最低賃金が拘束するのはパートだけか。
A：拘束的かどうかは各類型の元の時給によります。両方の費用が上がる場合も比較します。 -->

---

<!-- _class: equations -->
# CES生産関数と代替弾力性

$$
Y=\left[aH_P^\rho+(1-a)H_N^\rho\right]^{1/\rho},\qquad
\rho=\frac{\sigma-1}{\sigma}
$$

- $Y$：二種類の労働による生産量。
- $a$：Pへの重み（$0<a<1$）。
- $\sigma>0$：代替弾力性。大きいほど、相対費用の変化に対して労働投入比率が大きく変わる。

<div class="source">Acemoglu and Autor (2011), pp. 1103-1105, 式(2)-(6).</div>

<!-- notes: 二類型の労働投入をCES生産関数で集計します。シグマは代替弾力性で、相対費用に対する労働投入比率の反応の大きさを表します。シグマが大きいほど、二類型の間で代替が起こりやすくなります。 -->

<!-- qa: Q：aはパート比率か。
A：aは生産関数の重みで、実際の人数比率は費用も含めて決まります。ローはシグマから決まる指数です。シグマが1のときは極限のCobb–Douglas形を使います。 -->

---

<!-- _class: equations -->
# 利潤最大化の一階条件

内点解（$H_P,H_N>0$）では、Pの一階条件は

$$
\frac{\partial\Pi}{\partial H_P}
=BY^{\beta-1}\frac{\partial Y}{\partial H_P}-c_P=0
$$

CESを微分して代入すると、二種類それぞれの条件は

$$
\begin{aligned}
aBY^{\beta-\rho}H_P^{\rho-1}&=c_P,\\[0.5em]
(1-a)BY^{\beta-\rho}H_N^{\rho-1}&=c_N.
\end{aligned}
$$

左辺は労働の限界収入生産物、右辺は1人当たり費用。

<!-- notes: 内点解では、労働の限界収入生産物が一人当たり費用に等しくなります。限界収入生産物は、Yに関する限界収入と、労働の限界生産物の積です。二つの一階条件には企業全体の収入項が共通するため、比を取ると相対労働需要を導けます。 -->

---

<!-- _class: equations -->
# 相対労働需要の導出

共通の $BY^{\beta-\rho}$ を消し、$\rho-1=-1/\sigma$ を使う。

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

$a$ が一定なら、相対費用 $c_P/c_N$ の上昇は、相対労働需要 $H_P/H_N$ を低下させる。

<div class="source">Acemoglu and Autor (2011), pp. 1104-1105, 式(5)-(6).</div>

<!-- notes: 二つの一階条件の比から、相対労働需要を導きます。重みaが一定なら、相対費用の上昇に対してP対Nの投入比率は低下し、その弾力性はマイナスシグマです。 -->

<!-- qa: Q：P/Nが下がると、Nの人数は増えるか。
A：両方減ってPの減少率が大きい場合にも、P/Nは下がります。Nの人数は次の生産量の式も合わせて判断します。 -->

---

<!-- _class: equations -->
# 単位費用の導出

生産量 $Y>0$ を固定し、それを満たす最も安い投入の組合せを選ぶ。

$$
\min_{H_P,H_N\geq0}\{c_PH_P+c_NH_N\}
\quad\text{s.t.}\quad
[aH_P^\rho+(1-a)H_N^\rho]^{1/\rho}\geq Y
$$

前頁の最適投入比を $r=H_P/H_N$ と置き、生産制約に代入する。

$$
r=\left(\frac{a}{1-a}\right)^\sigma\left(\frac{c_N}{c_P}\right)^\sigma,\qquad
H_N=\frac{Y}{[ar^\rho+(1-a)]^{1/\rho}},\quad H_P=rH_N
$$

総費用を $Y$ で割ると、単位費用 $C$（生産量1単位当たりの最小費用）を得る。

$$
\begin{aligned}
C&=\frac{c_Pr+c_N}{[ar^\rho+(1-a)]^{1/\rho}}\\[0.4em]
&=\left[a^\sigma c_P^{1-\sigma}+(1-a)^\sigma c_N^{1-\sigma}\right]^{1/(1-\sigma)}.
\end{aligned}
$$

<!-- notes: ここではまず生産量Yを固定し、その量を最も安く生産する組合せを選びます。費用最小化でも前頁と同じ投入比が得られるので、その比をrと置きます。Pの投入をr倍のNで置き換えてCESに代入すると、Nの投入量が求まります。総費用はcP掛けるrとcNの和にNの投入量を掛けたものです。これをYで割ると、生産量一単位当たりの最小費用Cになります。 -->

<!-- qa: Q：利潤最大化で求めた投入比を費用最小化でも使えるのはなぜか。
A：どちらも内点では、二種類の限界生産物の比が費用比に等しくなります。費用最小化の一階条件の比を取ると、前頁と同じrが得られます。

Q：なぜ生産制約を等号で解くか。
A：費用が正なので、必要な量を超えて生産する組合せは最小費用になりません。収穫一定の下で投入を比例的に減らせば、必要な生産量を保ちながら費用を下げられます。

Q：Cは一人当たり費用か。
A：Cは二種類を最適に組み合わせた生産量一単位の費用です。cPとcNは、それぞれの労働一人当たりの費用です。 -->

---

<!-- _class: equations -->
# 最適生産量

CESは規模に関して収穫一定。投入を $k$ 倍にすると、生産量も $k$ 倍になる。
したがって、生産量が $Y$ のとき、最小費用は $CY$。企業は次の問題から生産量を選ぶ。

$$
\max_{Y\geq0}\left\{\frac{B}{\beta}Y^\beta-CY\right\}
$$

一階条件は「限界収入＝限界費用」。

$$
\frac{d\Pi}{dY}=BY^{\beta-1}-C=0
\quad\Longrightarrow\quad BY^{\beta-1}=C
$$

$$
Y^*=\left(\frac{B}{C}\right)^{1/(1-\beta)}
$$

単位費用 $C$ の上昇は最適生産量 $Y^*$ を減少させる。$\beta$ が大きいほど反応は大きい。

<!-- notes: 前頁では生産量一単位当たりの最小費用を求めました。CESは規模に関して収穫一定なので、生産量をY倍にすると必要な投入と費用もY倍になり、最小費用はCYです。次に収入からこの費用を引き、生産量について微分します。限界収入と単位費用が等しい条件を解くと、最適生産量Yスターが得られます。単位費用の上昇は生産量を減少させます。 -->

<!-- qa: Q：なぜ単位費用を一定としてYで微分できるか。
A：cP、cN、a、シグマを所与とすると、前頁のCはYに依存しません。CESが規模に関して収穫一定なので、最小総費用はYに比例します。

Q：ベータが大きいと費用上昇への反応が大きいのはなぜか。
A：最適生産量の費用弾力性はマイナス一割る一マイナスベータです。ベータが大きいほど限界収入の低下が緩やかなので、費用上昇に対応する生産量の減少率が大きくなります。 -->

---

<!-- _class: equations -->
# パート以外の労働需要：代替効果と規模効果

Pの費用 $c_P$ だけが上がり、$c_N$ は一定の場合を考える。

$$
H_N=Y^*(1-a)^\sigma\left(\frac{C}{c_N}\right)^\sigma,\qquad
s_P=\frac{c_PH_P}{c_PH_P+c_NH_N}
$$

$s_P$ はPの費用シェア。
$\partial\ln C/\partial\ln c_P=s_P$ より、

$$
\frac{\partial\ln H_N}{\partial\ln c_P}
=\underbrace{\sigma s_P\vphantom{\frac{s_P}{1-\beta}}}_{\text{Substitution}}
-\underbrace{\frac{s_P}{1-\beta}}_{\text{Scale}}
$$

- 代替効果：生産量を一定とすると、相対的に割高なPからNへ代替する。
- 規模効果：生産量の減少により、Nの労働需要も減少する。

$\sigma>1/(1-\beta)$ なら代替効果が上回りNは増加。逆なら規模効果が上回りNは減少。

<!-- notes: 費用最小化の頁で求めたNの投入量を、単位費用Cで書き直し、前頁の最適生産量Yスターを代入したのが最初の式です。この労働需要の変化を、代替効果と規模効果に分解します。PからNへの代替効果は正、生産量の減少による規模効果は負です。二つの効果の大小関係で、Nの反応の符号が決まります。 -->

<!-- qa: Q：Nを未処理の対照群として使えるか。
A：Nの費用が直接変わらなくても代替と規模調整でNは動きます。本報告の比較群は求人類型ではなく、発効時期で分けた県です。 -->

---

<!-- _class: equations -->
# 求人充足率とモデルの検証可能な予測

求人充足率を $q_j$ とすると、採用人数と求人数の関係は

$$
H_j=q_jV_j,\qquad \frac{V_P}{V_N}=\frac{q_N}{q_P}\frac{H_P}{H_N}
$$

求人充足率が一定なら、相対労働需要の予測を相対求人数にも適用できる。

| 費用の変化 | P単独 | N単独 | 求人合計 | P/N |
|---|---|---|---|---|
| 両方が同率上昇 | 減少 | 減少 | 減少 | 不変 |
| Pだけが上昇 | 減少 | 符号は不定 | 符号は不定 | 低下 |

主仮説：パートのDID係数は負。合計と相対指標で、規模効果・構成変化と照合する。

<!-- notes: 求人充足率qを一定と仮定し、労働需要の比較静学を求人の予測に接続します。表の二つの場合ともPの求人は減少します。Pの費用だけが上がる場合、Nの求人は増加も減少もありえます。Nが減れば合計も減りますが、Nが増える場合はPの減少を上回るかで合計の方向が決まるため、合計も符号は不定です。主仮説はパートのDID係数が負であることです。 -->

<!-- qa: Q：企業モデルの予測を県別データに移す条件は何か。
A：充足率に加え、企業構成、需要、募集媒体などの比較可能性が必要です。充足率が変われば採用が同じでも求人は変わります。現実にはNにも最低賃金が適用され、費用差と充足率は本データから直接測れていません。 -->

---

<!-- _class: equations -->
# アウトカム変数：前年同月比と求人構成

県 $i$、月 $t$。回帰指標は $j\in\{P,N,T,R\}$ の4種類。

$$
y^j_{i,t}=100\left(\ln V^j_{i,t}-\ln V^j_{i,t-12}\right)
\qquad j\in\{P,N,T\}
$$

$V^T=V^P+V^N$ は求人合計。対数差×100で前年同月比を近似する。

$$
y^R_{i,t}=y^P_{i,t}-y^N_{i,t}
=100\,\Delta_{12}\ln(V^P_{i,t}/V^N_{i,t})
$$

$\Delta_{12}$ は前年同月との差。
相対指標 $R$ は、Pの増加率がNを下回ると負になる。

<!-- notes: 回帰にはP、N、T、Rの四つの指標を使います。P、N、Tは求人数の前年同月比を対数差で表します。RはPとNの対数変化の差で、パートの伸びがパート以外より低いと負になります。四つをそれぞれ月次DIDの被説明変数にします。 -->

---

<!-- _class: equations -->
# 月次DID回帰：県・月固定効果

一県×一か月を1観測とし、2025年1〜9月と11月を使う。
10月は移行月として除く。$y_{it}^j$ は前頁の4指標（$j\in\{P,N,T,R\}$）。

- $\mathrm{Treat}_i$：処置群ダミー（10月発効＝1、12月以降発効＝0）。
- $\mathrm{Post}_t$：事後ダミー（11月＝1、1〜9月＝0）。

$$
y_{it}^j=\alpha_i^j+\lambda_t^j
+\delta^j(\mathrm{Treat}_i\times\mathrm{Post}_t)+\varepsilon_{it}^j
$$

- $\alpha_i^j$：県固定効果。各県に固有で、期間中一定の指標の差。
- $\lambda_t^j$：月固定効果。各月に全県で共通する変動。

県等重みのOLSで推定し、標準誤差は県単位でクラスタ化する。

<div class="source">Duhaut et al. (2021), “When is TWFE okay? Canonical difference-in-differences”.</div>

<!-- notes: 四つの指標をそれぞれ被説明変数とし、県と月のパネルで推定します。県固定効果は各県に固有の安定した差を、月固定効果は各月に共通する変動を吸収します。早期県の十一月だけ一となる交互作用項の係数デルタがDIDです。標準誤差は県単位でクラスタ化します。 -->

<!-- qa: Q：TreatとPostの単独項はどこに入るか。
A：Treatは県固定効果、Postは月固定効果に吸収されます。別々の係数として重ねて入れる必要はありません。

Q：県固定効果は何を調整するか。
A：ここでの被説明変数は同比などの指標です。県固定効果は、その指標における各県の期間中一定の差を調整します。

Q：月別データの全期間を使うか。
A：主比較は一月から九月と十一月です。十一月発効県と、移行月の十月を除きます。十二月以降へ延長するときは、未発効の対照県を改めて定義します。 -->

---

<!-- _class: equations -->
# パート求人への影響とその含意

**主仮説：早期発効県では、パート求人が相対的に弱まる。**

$$
H_0:\delta^P\geq0,\qquad H_1:\delta^P<0
$$

| 想定される係数 | パート求人への含意 |
|---|---|
| $\delta^P<0\leq\delta^N$ | パートだけが弱まる |
| $\delta^P<\delta^N<0$ | 両方が弱まるが、パートへの影響が大きい |
| $\delta^N\leq\delta^P<0$ | パート以外も同程度以上に弱まる |

パートへの偏りは $\delta^R=\delta^P-\delta^N$ で確認する。
求人合計 $T$ は、全体の縮小も伴うかを見るために使う。

<!-- notes: この発表の主な問いは、最低賃金の早期発効がパート求人に負の影響を与えるかです。まずパートの係数が負かを、県クラスタ標準誤差による片側五パーセント検定で確かめます。そのうえで、負の影響がパートに偏るのかをパート以外との比較で読みます。表の一つ目はパートだけが弱まる場合、二つ目は両方が弱まるもののパートへの影響が大きい場合です。三つ目はパート以外も同程度以上に弱まり、パートに偏った影響とはいえない場合です。型間の差は、相対指標Rの回帰係数から確認します。求人合計Tは、パート求人の弱まりが全体の縮小も伴うかを調べる補助指標です。ここでは想定される結果とその含意を示し、実際の推定値は次回報告します。 -->

<!-- qa: Q：主仮説はどう検定するか。
A：$H_0:\delta^P\geq0$、$H_1:\delta^P<0$ とし、県クラスタ標準誤差を用いて片側5%で検定します。TとRは同じ標本・仕様で推定し、規模と構成を補足します。

Q：Pが有意でNが有意でなければ、パートへの影響のほうが大きいといえるか。
A：個別の有意性の違いだけでは型間の差を判断できません。同じ標本と仕様で作るRの係数はPとNの係数の差になるため、R自身の標準誤差と信頼区間で確認します。

Q：構成変化があれば、企業内でPからNへ代替したといえるか。
A：この表はモデルの予測との対応であり、代替効果を直接識別するものではありません。求人充足率、企業構成、需要、募集経路なども変わりえます。因果解釈には、改定がなければ二群の指標の平均変化は等しいという平行トレンド仮定などの条件が必要で、その詳しい確認は次回示します。

Q：前の二期DIDと係数は変わるか。
A：同じ県、同じ月、等しい重みを使い、追加の統制変数を入れない今回の仕様では、点推定値は一致します。標準誤差は県クラスタ方式で計算します。

Q：ほかの指標も同じように推定するか。
A：N、T、Rも同じ標本と仕様で推定し、規模と構成の変化を補足します。Rは県ごとにPからNを引いて作るため、両者の共分散も保持します。

Q：係数が負なら求人数そのものが減ったといえるか。
A：被説明変数は前年同月比の対数変化です。負の係数は、その指標の変化が早期群で相対的に低いことを示し、求人数の絶対的な減少を意味しません。 -->

---

<!-- _class: refs -->
# 参考文献・データ

Acemoglu, D. and D. Autor (2011) “Skills, Tasks and Technologies: Implications for Employment and Earnings,” in O. Ashenfelter and D. Card (eds.), *Handbook of Labor Economics*, Vol. 4B, ch. 12, Elsevier, pp. 1043-1171. <https://doi.org/10.1016/S0169-7218(11)02410-5>

Duhaut, A., F. Kondylis, J. Loeser and C. Piza (2021) “DiD you see Beta? Beta who? Part 1,” *Development Impact*, World Bank, 2 November. https://blogs.worldbank.org/en/impactevaluations/did-you-see-beta-beta-who-part-1 （2026年11月4日閲覧）.

厚生労働省（2026a）「一般職業紹介状況（職業安定業務統計）長期時系列表 第12表 都道府県（受理地）別 雇用形態別 新規求人数」e-Stat. https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040505323&fileKind=0 （2026年10月26日取得）.

厚生労働省（2026b）「地域別最低賃金改定状況」. https://www.mhlw.go.jp/content/11200000/001756130.xlsx （2026年10月26日取得）.

厚生労働省（n.d.-a）「目安答申後の地方最低賃金審議会における審議の流れ」資料No.1，p. 3. https://www.mhlw.go.jp/content/11201250/001729623.pdf （2026年11月4日閲覧）.

厚生労働省（n.d.-b）「一般職業紹介状況（職業安定業務統計）：集計結果（用語の解説）」. https://www.mhlw.go.jp/toukei/list/114-1_yougo.html （2026年11月4日閲覧）.

<!-- notes: データと文献の出所です。CESはAcemoglu・Autorの刊行章、DIDはDuhautほか、データと用語は厚生労働省の資料を参照しています。原文で確かめた範囲と、本報告で追加した仮定の区別はsourcesとmethodsにも残しています。 -->
