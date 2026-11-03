"""構成版の解説動画：場面ごとの画面（HTML＋KaTeX）とナレーション。

各場面は steps のリスト。step k の画面では data-step<=k の要素が表示され、
data-hl=k の要素が強調される。各 step の lines が字幕・ナレーションになる。
数値は results/ のCSVから読み、ナレーション中の丸め値と照合する（build_video.py）。
"""
import csv
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"


def _rows(name):
    with open(RESULTS / name, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


CONTRASTS = {(r["metric"], r["baseline_end"]): r for r in _rows("contrasts.csv")}
GROUPS = {(r["metric"], r["baseline_end"], r["group"]): r for r in _rows("group_means.csv")}
ILLUS = [r for r in _rows("model_illustration_NOT_ESTIMATED.csv")
         if float(r["sigma"]) == 2.0 and float(r["a"]) == 0.5 and float(r["beta"]) in (0.2, 0.7)]


def f2(x, sign=True):
    """表示用の小数2桁（マイナスは全角でなく U+2212）。"""
    v = float(x)
    s = f"{abs(v):.2f}"
    if v < 0:
        return "−" + s
    return ("+" + s) if sign else s


def ci(metric, base="2025-09"):
    r = CONTRASTS[(metric, base)]
    return f2(r["estimate"]), f"[{f2(r['ci_low'], False)}, {f2(r['ci_high'], False)}]"


# ---------------------------------------------------------------- 図（SVG）

def isoquant_svg():
    """a=0.5、Z=1 の等量曲線を σ 別に描く。"""
    W, H, pad = 620, 560, 70
    xmax = 4.0

    def px(x):
        return pad + x / xmax * (W - pad - 20)

    def py(y):
        return H - pad - y / xmax * (H - pad - 20)

    curves = []
    for sigma, col, dash, lab in [(0.25, "#b45309", "", "σ=0.25（補完的）"),
                                  (1.0, "#555", "8 6", "σ=1"),
                                  (4.0, "#1d4ed8", "", "σ=4（代替的）")]:
        pts = []
        for i in range(1, 400):
            hp = 0.3 + i * (xmax - 0.3) / 400
            if abs(sigma - 1) < 1e-9:
                hn = 1 / hp
            else:
                rho = (sigma - 1) / sigma
                inner = (1 - 0.5 * hp ** rho) / 0.5
                if inner <= 0:
                    continue
                hn = inner ** (1 / rho)
            if 0 < hn <= xmax:
                pts.append(f"{px(hp):.1f},{py(hn):.1f}")
        curves.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" '
                      f'stroke-width="5" stroke-dasharray="{dash}"/>')
    labels = (f'<text x="{px(2.2)}" y="{py(1.08)}" fill="#b45309" font-size="26">σ=0.25（補完的）</text>'
              f'<text x="{px(3.3)}" y="{py(0.5)}" fill="#555" font-size="26">σ=1</text>'
              f'<text x="{px(0.2)}" y="{py(0.15)}" fill="#1d4ed8" font-size="26">σ=4（代替的）</text>')
    axes = (f'<line x1="{pad}" y1="{py(0)}" x2="{W-10}" y2="{py(0)}" stroke="#111" stroke-width="2"/>'
            f'<line x1="{pad}" y1="{py(0)}" x2="{pad}" y2="10" stroke="#111" stroke-width="2"/>'
            f'<text x="{W-20}" y="{py(0)+44}" font-size="28" text-anchor="end">パートの人数 H<tspan baseline-shift="sub" font-size="20">P</tspan></text>'
                        f'<text x="{pad+12}" y="34" font-size="28">パート以外 H<tspan baseline-shift="sub" font-size="20">N</tspan></text>')
    return (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="NotoJP">'
            f'{axes}{"".join(curves)}{labels}'
            f'<text x="{W/2}" y="{H-4}" font-size="22" text-anchor="middle" fill="#555">同じサービス量 Z を生む組合せ（a=0.5）</text></svg>')


def decomposition_svg():
    """σ=2、s_P=0.5 のときの代替・規模・合計（弾力性）。"""
    sigma, sp = 2.0, 0.5
    rows = []
    for beta in (0.2, 0.7):
        sub = sigma * sp
        scale = -sp / (1 - beta)
        rows.append((beta, sub, scale, sub + scale))
    W, H = 800, 470
    x0 = 470
    unit = 115  # 1.0 の長さ
    out = [f'<line x1="{x0}" y1="20" x2="{x0}" y2="{H-50}" stroke="#111" stroke-width="2"/>']
    y = 40
    for beta, sub, scale, tot in rows:
        out.append(f'<text x="0" y="{y+30}" font-size="28" font-weight="700">β={beta}</text>')
        for lab, v, col in [("代替", sub, "#1d4ed8"), ("規模", scale, "#c2410c"), ("合計", tot, "#111")]:
            w = abs(v) * unit
            xx = x0 if v >= 0 else x0 - w
            out.append(f'<text x="100" y="{y+30}" font-size="26">{lab}</text>')
            out.append(f'<rect x="{xx:.1f}" y="{y+6}" width="{w:.1f}" height="32" fill="{col}" opacity="{1 if lab!="合計" else 0.85}"/>')
            tx = x0 + w + 10 if v >= 0 else x0 - w - 10
            anchor = "start" if v >= 0 else "end"
            out.append(f'<text x="{tx:.1f}" y="{y+32}" font-size="26" text-anchor="{anchor}">{f"{v:+.3g}".replace("-", "−")}</text>')
            y += 46
        y += 30
    out.append(f'<text x="{x0}" y="{H-14}" font-size="22" text-anchor="middle" fill="#555">∂ln H<tspan baseline-shift="sub" font-size="16">N</tspan>/∂ln c<tspan baseline-shift="sub" font-size="16">P</tspan>（σ=2、s<tspan baseline-shift="sub" font-size="16">P</tspan>=0.5）</text>')
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="NotoJP">{"".join(out)}</svg>'


def forest_svg(highlight_all):
    """早期−後期差と Welch 95%区間（100×対数差の4指標）。"""
    metrics = [("part", "パート（主比較）"), ("nonpart", "パート以外"),
               ("total", "合計"), ("relative", "相対（P−N）")]
    W, H = 1500, 470
    left, right = 380, 1440
    lo, hi = -10.0, 6.0

    def px(v):
        return left + (v - lo) / (hi - lo) * (right - left)

    out = []
    for t in range(-10, 7, 2):
        out.append(f'<line x1="{px(t):.1f}" y1="20" x2="{px(t):.1f}" y2="{H-70}" stroke="#e5e5e5" stroke-width="1.5"/>')
        out.append(f'<text x="{px(t):.1f}" y="{H-36}" font-size="24" text-anchor="middle">{str(t).replace("-", "−")}</text>')
    out.append(f'<line x1="{px(0):.1f}" y1="10" x2="{px(0):.1f}" y2="{H-66}" stroke="#111" stroke-width="2.5" stroke-dasharray="8 6"/>')
    out.append(f'<text x="{(left+right)/2}" y="{H-4}" font-size="24" text-anchor="middle" fill="#444">早期−後期の変化の差（100×対数差）、横線はWelch 95%区間</text>')
    for i, (m, lab) in enumerate(metrics):
        r = CONTRASTS[(m, "2025-09")]
        y = 60 + i * 95
        on = highlight_all or m == "part"
        col = "#111" if on else "#c8c8c8"
        out.append(f'<text x="20" y="{y+9}" font-size="30" fill="{col}">{lab}</text>')
        out.append(f'<line x1="{px(float(r["ci_low"])):.1f}" y1="{y}" x2="{px(float(r["ci_high"])):.1f}" y2="{y}" stroke="{col}" stroke-width="6"/>')
        for e in ("ci_low", "ci_high"):
            out.append(f'<line x1="{px(float(r[e])):.1f}" y1="{y-14}" x2="{px(float(r[e])):.1f}" y2="{y+14}" stroke="{col}" stroke-width="4"/>')
        dot = "#1d4ed8" if on else "#c8c8c8"
        out.append(f'<circle cx="{px(float(r["estimate"])):.1f}" cy="{y}" r="13" fill="{dot}"/>')
        out.append(f'<text x="{px(float(r["estimate"])):.1f}" y="{y-24}" font-size="26" text-anchor="middle" fill="{col}">{f2(r["estimate"])}</text>')
    return f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="NotoJP">{"".join(out)}</svg>'


def timeline_html():
    cells = [("10月発効", "早期群 E", "20県", "11月は新しい最低賃金", "e"),
             ("11月発効", "除外", "13県", "11月の途中で切替", "x"),
             ("12月以降発効", "後期群 L", "14県", "11月は古い最低賃金", "l")]
    out = []
    for when, name, n, state, cls in cells:
        out.append(f'<div class="tl {cls}"><div class="tl-when">{when}</div>'
                   f'<div class="tl-name">{name}</div><div class="tl-n">{n}</div>'
                   f'<div class="tl-state">{state}</div></div>')
    return '<div class="tlrow">' + "".join(out) + "</div>"


# ---------------------------------------------------------------- 場面

pm = {g: GROUPS[("part", "2025-09", g)] for g in ("early", "late")}
part_b = float(pm["early"]["baseline"]) - float(pm["late"]["baseline"])
part_n = float(pm["early"]["november"]) - float(pm["late"]["november"])
part_c = float(pm["early"]["change"]) - float(pm["late"]["change"])
p_part = float(CONTRASTS[("part", "2025-09")]["p_negative"])
ill = {float(r["beta"]): r for r in ILLUS}


def S(n, html):
    return f'<div data-step="{n}">{html}</div>'


SCENES = [
    dict(
        chapter="はじめに", title=None, cls="title",
        steps=[
            dict(html=r"""
<div class="bigtitle">最低賃金の発効時期と採用の構成</div>
<div class="subtitle-l">パート求人だけが弱くなるのか、求人全体が縮むのか</div>
<div class="meta">課題3・4　構成版　解説動画</div>""",
                 lines=["この動画では、最低賃金の発効時期と、求人の構成についての私たちの報告を、約10分で説明します。",
                        "前回は、パートの求人だけを見て、最低賃金が早く上がった県で、パート求人が相対的に弱くなったかを調べました。",
                        "今回はそこに、パート以外の求人と、その合計を加えます。"]),
            dict(html=S(1, r"""
<div class="two">
  <div class="card blue"><div class="card-h">規模</div>求人全体が縮む</div>
  <div class="card orange"><div class="card-h">構成</div>パートからパート以外へ<br>組合せが変わる</div>
</div>"""),
                 lines=["知りたいのは、パート求人の差が、求人全体の縮小なのか、それとも組合せの変化なのか、という区別です。",
                        "先に結論を言うと、データの精度が足りず、どちらとも確定できません。ただ、その途中で、モデルから大事な注意点が一つ分かります。"]),
        ]),
    dict(
        chapter="1 データと比較", title="数えているのは、新しく受理された採用予定人員",
        steps=[
            dict(html=r"""
<table class="tbl">
<tr><th>系列</th><th>厚労省 第12表</th><th>この動画での記号</th></tr>
<tr><td>一般パートタイム</td><td>第12表－3</td><td>パート（P）</td></tr>
<tr><td>パートを除く一般</td><td>第12表－2</td><td>パート以外（N）</td></tr>
<tr><td>パートを含む一般</td><td>第12表－1</td><td>合計（P＋N）</td></tr>
</table>""",
                 lines=["使うのは、ハローワークの新規求人数です。都道府県別・月別に、パート、パート以外、その合計の三つの系列があります。",
                        "記号では、パートをP、パート以外をN、合計をP足すNと書きます。"]),
            dict(html=S(1, r"""
<ul class="pts">
<li data-hl="1">単位は<b>人</b>。広告の件数でも、実際の採用人数でもない。</li>
<li data-hl="1">パート以外（N）≠ 正社員。契約・臨時・季節の求人も含む。</li>
</ul>"""),
                 lines=["注意点が二つあります。一つ目に、単位は人で、求人広告の件数でも、実際に採用された人数でもありません。",
                        "二つ目に、パート以外は正社員とは限りません。契約社員や、臨時・季節の求人も含みます。"]),
        ]),
    dict(
        chapter="1 データと比較", title="11月なら、発効済みと未発効を同じ月で比べられる",
        steps=[
            dict(html=timeline_html(),
                 lines=["2025年度の最低賃金は、県によって発効する月が違いました。",
                        "10月に発効した20県を早期群E、12月以降に発効した14県を後期群Lと呼び、11月に発効した13県は除外します。",
                        "すると2025年11月には、早期群はすでに新しい最低賃金、後期群はまだ古い最低賃金という状態を、同じ月で比べられます。"]),
            dict(html=S(1, r"""<div class="note" data-hl="1">ただし時期は無作為ではない：早期群は最低賃金の水準が高く、引上げ率は低い（6.39% 対 7.78%）。差 ≠ 因果効果。</div>"""),
                 lines=["ただし、発効時期は無作為に決まったわけではありません。早期群は最低賃金の水準が高く、引上げ率は6.39%で、後期群の7.78%より低いです。",
                        "ですから、この比較の差を、そのまま因果効果とは読みません。"]),
        ]),
    dict(
        chapter="2 モデル", title="企業は、二種類を何人ずつ採用するか選ぶ",
        steps=[
            dict(html=r"""
<div class="eq">$$\max_{H_P,\,H_N\ge 0}\ \Pi=\underbrace{\htmlClass{hl1}{\frac{B}{\beta}Z^{\beta}}}_{\text{収入}}-\underbrace{\htmlClass{hl2}{(c_PH_P+c_NH_N)}}_{\text{費用}}$$</div>""",
                 lines=["ここからがモデルです。新しい売場を作る企業が、パートを何人、パート以外を何人採るかを決める、と考えます。",
                        "採用人数をH_P、H_Nと書きます。既存の従業員はいない、という強い単純化を置いています。"]),
            dict(html=S(1, r"""<div class="exp" data-hl="1">$Z$：二種類の人を組み合わせて生むサービス量　／　$0<\beta<1$：$Z$ を増やすほど追加収入は小さくなる</div>"""),
                 lines=["利潤Πは、収入から費用を引いたものです。収入は、Zのβ乗に比例します。",
                        "Zは二種類の人を組み合わせて生まれるサービスの量です。βは0と1の間なので、Zを増やすほど、追加の収入は小さくなります。"]),
            dict(html=S(2, r"""<div class="eq" data-hl="2">$$c_j=h_j\,w_j+k_j,\qquad w_j=\max\{w_j^0,\ m\},\quad j=P,N$$</div>
<div class="exp">$c_j$：1人の費用＝期間の労働時間 $h_j$ × 時給 $w_j$ ＋ 採用経費 $k_j$　／　$m$：最低時給</div>"""),
                 lines=["費用の方は、一人当たりの費用cに、人数を掛けたものです。",
                        "一人当たりの費用は、期間の労働時間かける時給に、採用経費を足したものです。",
                        "時給は、もともとの時給と、最低賃金mの大きい方になります。つまり、最低賃金が費用を直接上げるのは、それが拘束的な類型だけです。"]),
        ]),
    dict(
        chapter="2 モデル", title="CESは、二種類の「組み合わせやすさ」を表す",
        steps=[
            dict(html=r"""
<div class="split"><div class="left">
<div class="eq">$$Z=\left[a\,H_P^{\rho}+(1-a)\,H_N^{\rho}\right]^{1/\rho}$$</div>
<div class="eq sm">$$\rho=\frac{\sigma-1}{\sigma}$$</div>
<ul class="pts sm"><li>$a$：パートの重み（人数比率ではない）</li><li>$\sigma$：代替の弾力性</li></ul>
</div><div class="right">""" + S(1, isoquant_svg()) + "</div></div>",
                 lines=["サービス量Zは、CESという関数で作られると仮定します。",
                        "aはパートの重みで、実際のパート比率とは別物です。ρは、σから決まる指数にすぎません。"]),
            dict(html="",
                 lines=["大事なのはσ、代替の弾力性です。右の図は、同じサービス量を生む人数の組合せを、σ別に描いたものです。",
                        "σが小さいと曲線はL字に近く、二種類はセットで必要です。σが大きいと直線に近く、片方が高くなれば、もう片方に乗り換えやすくなります。"]),
        ]),
    dict(
        chapter="2 モデル", title="追加の1人が生む収入と、その費用が等しくなる",
        steps=[
            dict(html=r"""
<div class="eq">$$\frac{\partial\Pi}{\partial H_P}=BZ^{\beta-1}\,\frac{\partial Z}{\partial H_P}-c_P=0$$</div>""",
                 lines=["企業は利潤を最大にするので、もう一人採ったときの追加収入が、一人当たりの費用と等しくなるところまで採用します。これが一階条件です。",
                        "追加収入は、収入をZで微分したものと、Zを人数で微分したものの積です。"]),
            dict(html=S(1, r"""
<div class="eq">$$\begin{aligned}a\,\htmlClass{hl1}{BZ^{\beta-\rho}}\,H_P^{\rho-1}&=c_P\\[0.4em](1-a)\,\htmlClass{hl1}{BZ^{\beta-\rho}}\,H_N^{\rho-1}&=c_N\end{aligned}$$</div>"""),
                 lines=["CESを微分して整理すると、パートとパート以外について、この二本の式になります。",
                        "黄色の部分は同じ企業全体の収入から来るので、二本の式に共通です。これが次のステップの鍵です。"]),
        ]),
    dict(
        chapter="2 モデル", title="二つの条件を割ると、相対需要が分かる",
        steps=[
            dict(html=r"""
<div class="eq">$$\frac{c_P}{c_N}=\frac{a}{1-a}\left(\frac{H_P}{H_N}\right)^{-1/\sigma}$$</div>""",
                 lines=["二本の式を割り算すると、共通部分が消えて、人数の比だけが残ります。"]),
            dict(html=S(1, r"""
<div class="eq" data-hl="1">$$\frac{H_P}{H_N}=\left(\frac{a}{1-a}\right)^{\sigma}\left(\frac{c_N}{c_P}\right)^{\sigma},\qquad\frac{\partial\ln(H_P/H_N)}{\partial\ln c_P}=-\sigma$$</div>"""),
                 lines=["人数の比について解くと、この式になります。対数を取って微分すると、パートの費用に対する比の弾力性は、マイナスσです。"]),
            dict(html=S(2, r"""<div class="note" data-hl="2">例：$\sigma=2$、パートの費用だけ10%上昇 → $H_P/H_N$ は約20%低下。<br>ただしこれは<b>比</b>の話。パート以外が増えるかは、まだ分からない。</div>"""),
                 lines=["例えば、σが2で、パートの費用だけが10%上がると、パート対パート以外の比は、およそ20%下がります。",
                        "ただし、これは比の話です。比が下がるのは、パート以外が増える場合でも、両方減ってパートがより大きく減る場合でも起こります。この式だけでは、パート以外が増えるかは分かりません。"]),
        ]),
    dict(
        chapter="2 モデル", title="組合せを決めた後、企業全体の規模を決める",
        steps=[
            dict(html=r"""
<div class="eq">$$C=\left[a^{\sigma}c_P^{1-\sigma}+(1-a)^{\sigma}c_N^{1-\sigma}\right]^{1/(1-\sigma)}$$</div>
<div class="exp">$C$：最適な組合せでサービスを1単位つくる最小費用</div>""",
                 lines=["そこで規模を考えます。最適な組合せでサービスを一単位作るときの最小費用を、Cと書きます。",
                        "Cは二つの費用の一種の平均で、パートの費用が上がれば、Cも上がります。"]),
            dict(html=S(1, r"""
<div class="eq">$$\max_{Z\ge0}\left\{\frac{B}{\beta}Z^{\beta}-CZ\right\}\ \Rightarrow\ \htmlClass{hl1}{Z^*=\left(\frac{B}{C}\right)^{1/(1-\beta)}}$$</div>"""),
                 lines=["すると企業の問題は、規模Zだけを選ぶ問題になり、最適な規模はこの式になります。",
                        "Cが上がると、規模は小さくなります。βが1に近いほど指数が大きくなり、規模は費用に敏感に反応します。"]),
        ]),
    dict(
        chapter="2 モデル", title="パート以外には、代替と規模縮小が同時に働く",
        steps=[
            dict(html=r"""
<div class="eq sm">$$H_N=Z^*\,(1-a)^{\sigma}\left(\frac{C}{c_N}\right)^{\sigma},\qquad s_P=\frac{c_PH_P}{c_PH_P+c_NH_N}$$</div>""",
                 lines=["いよいよ、パート以外の採用がどう動くかです。パートの費用だけが上がり、パート以外の費用は変わらないとします。",
                        "パート以外の人数は、規模Zと、組合せの部分の積で書けます。"]),
            dict(html=r"""<div class="split"><div class="left">""" + S(1, r"""
<div class="eq">$$\frac{\partial\ln H_N}{\partial\ln c_P}=\underbrace{\htmlClass{blue}{\sigma\,s_P}}_{\text{代替}\,(+)}\ -\ \underbrace{\htmlClass{orange}{\frac{s_P}{1-\beta}}}_{\text{規模}\,(-)}$$</div>""")
                 + S(3, r"""<div class="note" data-hl="3">$\sigma>\dfrac{1}{1-\beta}$ なら N は増え、逆なら減る。<br>→ パート以外は「影響を受けない対照群」ではない。</div>""")
                 + '</div><div class="right wide">' + S(2, decomposition_svg()) + "</div></div>",
                 lines=["対数を取って微分すると、弾力性は二つの項に分かれます。",
                        "第一項のσ掛けるs_Pは代替効果です。規模が同じなら、割高になったパートを避けて、パート以外を増やします。",
                        "第二項は規模効果です。費用が上がって規模自体が縮めば、パート以外も減らします。",
                        "s_Pは費用に占めるパートの割合で、人数の比率ではありません。"]),
            dict(html="",
                 lines=["数字を入れてみます。σが2、s_Pが0.5なら、代替効果はプラス1です。",
                        "βが0.2なら規模効果はマイナス0.625で、合計はプラス、パート以外は増えます。",
                        "βが0.7なら規模効果はマイナス1.67で、合計はマイナス、パート以外は減ります。"]),
            dict(html="",
                 lines=["一般に、σが、1マイナスβ分の1より大きければ増え、小さければ減ります。",
                        "つまり、パート以外は、最低賃金の影響を受けない対照群とは言えません。これがモデルから得られる、一番大事な注意点です。"]),
        ]),
    dict(
        chapter="2 モデル", title="スライドp.11の数値例（仮定値の計算、推定ではない）",
        steps=[
            dict(html=f"""
<div class="exp">$c_P:1\\to1.10,\\ c_N:1\\to1.02$、$\\sigma=2,\\ a=0.5$ を固定し、$\\beta$ だけ変える（100×対数変化）</div>
<table class="tbl num">
<tr><th>収入の曲率</th><th>P</th><th>N</th><th>合計</th><th>P/N</th></tr>
<tr><td>$\\beta=0.2$</td><td>{f2(ill[0.2]['P_change_log100'])}</td><td class="hlcell">{f2(ill[0.2]['N_change_log100'])}</td><td>{f2(ill[0.2]['total_change_log100'])}</td><td>{f2(ill[0.2]['relative_change_log100'])}</td></tr>
<tr><td>$\\beta=0.7$</td><td>{f2(ill[0.7]['P_change_log100'])}</td><td class="hlcell">{f2(ill[0.7]['N_change_log100'])}</td><td>{f2(ill[0.7]['total_change_log100'])}</td><td>{f2(ill[0.7]['relative_change_log100'])}</td></tr>
</table>""",
                 lines=["スライドの数値例も、同じことを示しています。パートの費用が10%、パート以外の費用が2%上がる仮定のもとで、βだけを変えています。",
                        f"P対Nの比の変化はどちらも{f2(ill[0.2]['relative_change_log100'])}で同じですが、パート以外の変化は{f2(ill[0.2]['N_change_log100'])}と{f2(ill[0.7]['N_change_log100'])}で、符号が逆になります。"]),
        ]),
    dict(
        chapter="3 検証の方法", title="採用のモデルを、観測できる求人につなぐ",
        steps=[
            dict(html=r"""
<div class="eq">$$H_j=q_j\,V_j\qquad\Rightarrow\qquad\frac{V_P}{V_N}=\frac{q_N}{q_P}\,\frac{H_P}{H_N}$$</div>""",
                 lines=["ただし、データで見えるのは採用ではなく求人です。そこで、求人Vのうち一定の割合qが採用になる、と仮定します。",
                        "qが一定なら、採用の比についての予測を、そのまま求人の比に移せます。"]),
            dict(html=S(1, r"""
<table class="tbl">
<tr><th>費用の変化</th><th>合計</th><th>P/N</th><th>N単独</th></tr>
<tr><td>両方が同じ率で上昇</td><td>減る</td><td>不変</td><td>減る</td></tr>
<tr><td>Pだけが上昇</td><td>規模と構成が変化</td><td>下がる</td><td class="hlcell">増減どちらも</td></tr>
</table>"""),
                 lines=["まとめると、二つの費用が同じ率で上がるなら、比は変わらず、合計が減ります。パートの費用だけが上がるなら、比は下がり、パート以外はどちらの方向もありえます。",
                        "だから、パートだけでなく、合計と比を一緒に見る必要があります。"]),
        ]),
    dict(
        chapter="3 検証の方法", title="求人を前年同月比にし、早期と後期を比べる",
        steps=[
            dict(html=r"""
<div class="eq sm">$$y^j_{i,t}=100\left(\ln V^j_{i,t}-\ln V^j_{i,t-12}\right),\qquad y^R_{i,t}=y^P_{i,t}-y^N_{i,t}$$</div>""",
                 lines=["検証では、まず各県・各月の求人を、前年同月比に変えます。対数の差の100倍で、毎年くり返す季節性を、ある程度取り除けます。",
                        "相対指標は、パートの前年同月比から、パート以外の前年同月比を引いたもので、パートがより強く減れば負になります。"]),
            dict(html=S(1, r"""
<div class="eq sm">$$d_i^j=y^j_{i,\mathrm{Nov}}-\underbrace{\frac{1}{9}\sum_{t=1}^{9}y^j_{i,t}}_{\text{1〜9月の平均}},\qquad \htmlClass{hl1}{D^j=\frac{1}{20}\sum_{i\in E}d_i^j-\frac{1}{14}\sum_{i\in L}d_i^j}$$</div>"""),
                 lines=["次に県ごとに、11月の値から、2025年1月から9月の平均を引きます。これで県ごとの普段の水準をならします。",
                        "最後に、早期20県の平均から後期14県の平均を引いたものが、主な比較Dです。各県を同じ重みで扱います。"]),
        ]),
    dict(
        chapter="3 検証の方法", title=f"{f2(part_c)}は、県内の変化の「早期−後期」差",
        steps=[
            dict(html=f"""
<table class="tbl num">
<tr><th>パート：群平均</th><th>1〜9月の平均</th><th>11月</th><th>県内の変化</th></tr>
<tr><td>早期20県（E）</td><td>{f2(pm['early']['baseline'])}</td><td>{f2(pm['early']['november'])}</td><td>{f2(pm['early']['change'])}</td></tr>
<tr><td>後期14県（L）</td><td>{f2(pm['late']['baseline'])}</td><td>{f2(pm['late']['november'])}</td><td>{f2(pm['late']['change'])}</td></tr>
<tr class="hlrow"><td>早期−後期</td><td>{f2(part_b)}</td><td>{f2(part_n)}</td><td><b>{f2(part_c)}</b></td></tr>
</table>
<div class="exp">仮説（前回と同じ）：$H_0: D^P\\ge 0$、$H_1: D^P<0$（片側）</div>""",
                 lines=[f"パートについて、実際の数字を見ます。早期群は、基準期の{f2(pm['early']['baseline'])}から、11月には{f2(pm['early']['november'])}に下がりました。",
                        f"後期群も、{f2(pm['late']['baseline'])}から{f2(pm['late']['november'])}に下がっていますが、下がり幅は小さめです。",
                        f"その下がり幅の差が、{f2(part_c)}です。11月だけを比べると両群はほぼ同じで、基準期にあった早期群の優位が縮んだ、というのが中身です。",
                        "仮説は前回と同じく、Dが負である、という片側の仮説です。"]),
        ]),
    dict(
        chapter="4 結果", title="どの指標も、95%区間が0をまたぐ",
        steps=[
            dict(html='<div class="center" data-only="0">' + forest_svg(False) + '</div><div class="center" data-from="1">' + forest_svg(True) + "</div>",
                 lines=[f"結果です。パートの差は{ci('part')[0]}で、前回の仮説と同じ方向ですが、95%区間は{f2(CONTRASTS[('part','2025-09')]['ci_low'])}から{f2(CONTRASTS[('part','2025-09')]['ci_high'])}まで広がり、0をまたいでいます。",
                        f"片側のp値は{p_part:.2f}で、5%水準では棄却できません。効果がないと証明したのではなく、負の差を確認する精度がない、と読みます。"]),
            dict(html="",
                 lines=[f"合計は{ci('total')[0]}でほぼ0ですが、区間はマイナス4程度まで含むので、規模の縮小は否定できません。",
                        f"相対は{ci('relative')[0]}で、パートの費用上昇の予測と方向は合いますが、やはり0を含みます。",
                        f"パート以外は{ci('nonpart')[0]}ですが、これも企業内で代替が起きた証拠にはなりません。",
                        f"なお、相対の{ci('relative')[0]}は、パートからパート以外を引いた計算上の恒等式で、独立した証拠ではありません。"]),
        ]),
    dict(
        chapter="4 結果", title="基準期を1〜7月にしても、結論は変わらない",
        steps=[
            dict(html=f"""
<table class="tbl num">
<tr><th>指標</th><th>1〜9月基準</th><th>1〜7月基準</th></tr>
<tr><td>パート</td><td>{' '.join(ci('part'))}</td><td>{' '.join(ci('part','2025-07'))}</td></tr>
<tr><td>合計</td><td>{' '.join(ci('total'))}</td><td>{' '.join(ci('total','2025-07'))}</td></tr>
<tr><td>相対</td><td>{' '.join(ci('relative'))}</td><td>{' '.join(ci('relative','2025-07'))}</td></tr>
</table>""",
                 lines=["8月と9月には、改定額が公表された後の先取り調整がありえるので、基準期を1月から7月にした結果も確認しました。",
                        "点推定はやや負の方向に動きますが、どの区間も0を含み、結論は変わりません。"]),
        ]),
    dict(
        chapter="5 まとめ", title="分かったことと、次に必要なこと",
        steps=[
            dict(html='''<ul class="pts">
<li><b>データ</b>：パート求人が守られたとも、組合せだけが変わったとも言えない（すべての区間が0を含む）。</li>
<li data-step="1" data-hl="1"><b>モデル</b>：パート以外にも代替と規模縮小が同時に働く。<br>→ パート以外を対照群にする読み方は退けられる。</li>
<li data-step="2"><b>次に必要</b>：職種・賃金帯、企業内の募集構成、実際の採用・充足の情報。</li></ul>''',
                 lines=["まとめます。データからは、パートの求人が守られたとも、組合せだけが変わったとも言えません。"]),
            dict(html="",
                 lines=["一方でモデルからは、パート以外の求人にも代替と規模縮小が同時に働くので、パート以外を対照群として使う読み方は退けられます。"]),
            dict(html="",
                 lines=["次に必要なのは、職種や賃金帯、企業内の募集の構成、そして実際の採用や充足の情報です。それがあって初めて、代替と規模縮小の区別に近づけます。",
                        "説明は以上です。詳しい導出と出典は、同じフォルダの資料にまとめてあります。"]),
        ]),
]

