"""動画用の図を results/*.csv と授業用の仮定値から描く（video/figs/ に出力）。

色：早期＝青、後期＝オレンジ。線種・マーカー形でも区別する（色だけに頼らない）。
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RES = HERE.parent / "results"
OUT = HERE / "figs"

INK, MUTED, GRID = "#1b1f24", "#6b6b66", "#d9d9d4"
EARLY, LATE, HL = "#2a78d6", "#eb6834", "#c2185b"

plt.rcParams.update({
    "font.family": ["Noto Sans CJK JP", "IPAGothic", "sans-serif"],
    "font.size": 22, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "xtick.color": INK, "ytick.color": INK, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 1.2, "axes.unicode_minus": True, "lines.linewidth": 3,
    "savefig.dpi": 100, "savefig.facecolor": "white",
})

# 授業用の仮定値（slides.md 9枚目、analysis.py の desired_employment と同じ式）
SCALE, BETA, HOURS = 3_200_000, 0.5, 160


def vmp(n):
    """追加1人が生む月の売上（円）= pAK^a * beta * N^(beta-1)。"""
    return SCALE * BETA * n ** (BETA - 1)


def n_star(w):
    return (SCALE * BETA / (HOURS * w)) ** (1 / (1 - BETA))


def fmt(v, nd=2):
    """表示用：ハイフンではなく数学のマイナス記号を使う。"""
    return f"{v:.{nd}f}".replace("-", "−")


def save(fig, name):
    fig.savefig(OUT / name, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)


def concave():
    fig, ax = plt.subplots(figsize=(6.4, 4.4))
    n = np.linspace(0, 10, 200)
    ax.plot(n, np.sqrt(n), color=INK)
    for a in [1, 2, 3, 6, 7, 8]:
        ax.plot([a, a + 1], [np.sqrt(a), np.sqrt(a)], color=MUTED, lw=1.5)
        ax.annotate("", xy=(a + 1, np.sqrt(a + 1)), xytext=(a + 1, np.sqrt(a)),
                    arrowprops=dict(arrowstyle="-|>", color=EARLY, lw=2.5))
    ax.text(2.2, 0.55, "最初のほうの1人：増分が大きい", color=INK, fontsize=17)
    ax.text(5.6, 1.95, "後の1人：増分が小さい", color=INK, fontsize=17)
    ax.set_xlabel("人数 N")
    ax.set_ylabel("生産量 Q")
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_title(r"$Q\propto N^{\beta}$（$\beta=0.5$）", fontsize=20, color=INK)
    save(fig, "concave.png")


def demand(name, wages, show_regions):
    fig, ax = plt.subplots(figsize=(10.2, 6.6))
    n = np.linspace(40, 170, 300)
    ax.plot(n, vmp(n) / 1e4, color=INK, label="追加1人が生む売上")
    styles = [(EARLY, "-"), (HL, "--")]
    for (w, (c, ls)) in zip(wages, styles):
        cost = HOURS * w / 1e4
        ns = n_star(w)
        ax.axhline(cost, color=c, ls=ls, lw=2.5)
        up = w != wages[0]
        ax.text(169, cost + (0.25 if up else -0.25), f"時給{w:,}円 → 月給 hw＝{cost:g}万円",
                color=INK, ha="right", va="bottom" if up else "top", fontsize=18)
        ax.plot([ns, ns], [10, cost], color=c, ls=":", lw=2)
        ax.plot(ns, cost, "o", ms=13, color=c, mec="white", mew=2, zorder=5)
        ax.text(ns, 10.4, f"{ns:.2f}人" if ns % 1 else f"{ns:.0f}人", ha="center",
                color=INK, fontsize=19, fontweight="bold")
    if show_regions:
        ax.annotate("売上 > 賃金\n→ 増やすと得", xy=(62, 21.5), fontsize=18, color=INK)
        ax.annotate("売上 < 賃金\n→ 減らすと得", xy=(128, 11.6), fontsize=18, color=INK)
    ax.set_xlim(40, 170); ax.set_ylim(10, 26)
    ax.set_xlabel("人数 N（人）")
    ax.set_ylabel("1人当たり、円／月（万円）")
    ax.grid(axis="y", color=GRID, lw=1)
    ax.legend(loc="upper right", frameon=False, fontsize=18)
    save(fig, name)


def profit_hill():
    fig, ax = plt.subplots(figsize=(10.2, 6.6))
    n = np.linspace(0, 260, 400)
    prof = (SCALE * np.sqrt(n) - HOURS * 1000 * n) / 1e6
    ax.plot(n, prof, color=INK)
    ax.plot([60, 140], [16, 16], color=HL, lw=2.5, ls="--")
    ax.plot(100, 16, "o", ms=14, color=HL, mec="white", mew=2)
    ax.text(100, 16.9, "頂上：傾き π′(N)＝0", ha="center", fontsize=19, color=INK)
    ax.text(28, 9, "傾き＞0\n増やすと利潤↑", fontsize=18, color=INK)
    ax.text(180, 9, "傾き＜0\n減らすと利潤↑", fontsize=18, color=INK)
    ax.set_xlabel("人数 N（人）")
    ax.set_ylabel("利潤（固定費を除く、百万円）")
    ax.set_ylim(0, 19.5); ax.set_xlim(0, 260)
    ax.grid(axis="y", color=GRID, lw=1)
    save(fig, "profit_hill.png")


def trend(name, emphasize):
    mm = pd.read_csv(RES / "monthly_means.csv", index_col=0, encoding="utf-8-sig")
    months = np.arange(1, len(mm) + 1)
    fig, ax = plt.subplots(figsize=(17, 6.6))
    if emphasize:
        ax.axvspan(7.6, 9.4, color="#ececec", zorder=0)
        ax.text(8.5, 1.2, "公表後\n予期に注意", ha="center", fontsize=18, color=INK)
        ax.axvspan(10.6, 11.4, color="#fde7ef", zorder=0)
        ax.text(11, 1.2, "比較月", ha="center", fontsize=18, color=INK)
    ax.axhline(0, color=GRID, lw=1.2)
    ax.plot(months, mm["10月発効"], "-o", color=EARLY, ms=10, mec="white", mew=1.5,
            label="早期（10月発効・20県）")
    ax.plot(months, mm["12月以降発効"], "--s", color=LATE, ms=10, mec="white", mew=1.5,
            label="後期（12月以降発効・14県）")
    ax.set_xticks(months, [f"{m}月" for m in months])
    ax.set_ylabel("前年同月比（対数差×100）")
    ax.set_ylim(-13.5, 2.8)
    ax.legend(loc="lower left", frameon=False, ncol=2, fontsize=20)
    save(fig, name)


def county():
    cc = pd.read_csv(RES / "county_changes.csv", encoding="utf-8-sig")
    cc = cc[cc["baseline"] == "2025-01..09"]
    fig, ax = plt.subplots(figsize=(17, 7.0))
    ax.axhline(0, color=GRID, lw=1.2)
    for x, (grp, c, mk, lab) in enumerate([("10月発効", EARLY, "o", "早期（20県）"),
                                           ("12月以降発効", LATE, "s", "後期（14県）")]):
        d = np.sort(cc.loc[cc["group"] == grp, "d"].to_numpy())
        xs = x + np.linspace(-0.22, 0.22, len(d))
        ax.plot(xs, d, mk, color=c, ms=13, mec="white", mew=1.5, ls="none")
        ax.plot([x - 0.3, x + 0.3], [d.mean()] * 2, color=INK, lw=4)
        ax.text(x + 0.33, d.mean(), f"平均 {fmt(d.mean())}", va="center", fontsize=20,
                color=INK)
    tokyo = cc.loc[cc["pref"] == "東京都", "d"].iloc[0]
    d_e = np.sort(cc.loc[cc["group"] == "10月発効", "d"].to_numpy())
    xt = np.linspace(-0.22, 0.22, len(d_e))[np.argmin(abs(d_e - tokyo))]
    ax.annotate("東京都", xy=(xt, tokyo), xytext=(-0.62, tokyo + 6), fontsize=18,
                arrowprops=dict(arrowstyle="-", color=MUTED))
    ax.set_xticks([0, 1], ["早期（10月発効・20県）", "後期（12月以降発効・14県）"])
    ax.set_xlim(-0.8, 1.8)
    ax.set_ylabel("県内変化 d（11月 − 1〜9月平均）")
    save(fig, "county.png")


def did():
    est = pd.read_csv(RES / "estimates.csv", encoding="utf-8-sig").iloc[0]
    fig, ax = plt.subplots(figsize=(7.6, 6.6))
    x = [0, 1]
    ax.plot(x, [est.pre_early, est.nov_early], "-o", color=EARLY, ms=13, label="早期")
    ax.plot(x, [est.pre_late, est.nov_late], "--s", color=LATE, ms=13, label="後期")
    for yv, va in [(est.pre_early, "bottom"), (est.pre_late, "top")]:
        ax.text(-0.06, yv, fmt(yv), ha="right", va="center", fontsize=18)
    ax.text(1.06, est.nov_early + 0.35, fmt(est.nov_early), fontsize=18, va="center")
    ax.text(1.06, est.nov_late - 0.35, fmt(est.nov_late), fontsize=18, va="center")
    ax.annotate("", xy=(0.12, est.pre_late), xytext=(0.12, est.pre_early),
                arrowprops=dict(arrowstyle="<->", color=INK, lw=1.8))
    ax.text(0.16, (est.pre_early + est.pre_late) / 2, f"差 {fmt(est.pre_gap)}",
            va="center", fontsize=18)
    ax.text(0.62, -11.2, f"差 {fmt(est.nov_gap)}", fontsize=18)
    ax.set_xticks(x, ["基準期\n1〜9月", "11月"])
    ax.set_xlim(-0.45, 1.4); ax.set_ylim(-13, -3)
    ax.set_ylabel("求人の伸び（県平均）")
    ax.legend(frameon=False, loc="upper right", fontsize=18)
    ax.set_title(f"差の変化：{fmt(est.nov_gap)} − {fmt(est.pre_gap)} ＝ {fmt(est.delta)}",
                 fontsize=19, color=INK)
    save(fig, "did.png")


def forest(name, rows, figsize, labels):
    fig, ax = plt.subplots(figsize=figsize)
    ax.axvline(0, color=MUTED, ls="--", lw=2)
    for i, (_, r) in enumerate(rows.iterrows()):
        y = len(rows) - 1 - i
        ax.plot([r.ci_low, r.ci_high], [y, y], color=INK, lw=3)
        for v in (r.ci_low, r.ci_high):
            ax.plot([v, v], [y - 0.12, y + 0.12], color=INK, lw=3)
        ax.plot(r.delta, y, "o", color=EARLY if i == 0 else INK, ms=14, mec="white",
                mew=2, zorder=5)
        ax.text(r.ci_high + 0.4, y, f"{fmt(r.delta)}  [{fmt(r.ci_low)}, {fmt(r.ci_high)}]",
                va="center", fontsize=19)
    ax.set_yticks(range(len(rows))[::-1], labels)
    ax.set_xlim(-10, 11)
    ax.set_ylim(-0.5, len(rows) - 0.5)
    ax.set_xlabel("早期 − 後期（ポイント）、95％ Welch区間")
    save(fig, name)


def main():
    OUT.mkdir(exist_ok=True)
    concave()
    demand("foc.png", [1000], True)
    demand("demand_1.png", [1000], False)
    demand("demand_2.png", [1000, 1100], False)
    profit_hill()
    trend("trend_1.png", False)
    trend("trend_2.png", True)
    county()
    did()
    est = pd.read_csv(RES / "estimates.csv", encoding="utf-8-sig")
    forest("ci.png", est.iloc[:1], (8.6, 2.2), ["基準 1〜9月"])
    forest("sensitivity.png", est, (17, 6.2),
           ["基準 1〜9月（主）", "基準 1〜7月（8・9月除外）", "基準 4〜9月（補足）"])


if __name__ == "__main__":
    main()
