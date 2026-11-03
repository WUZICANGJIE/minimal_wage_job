"""Monthly DID using audited inputs from the archived two-period analysis.

Reads the previously audited source CSVs; writes only below this directory.
The balanced panel keeps the original 20 early / 14 late prefectures and
January–September plus November 2025. October is the transition month.
"""
from pathlib import Path
import hashlib
import json
import os
import platform

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
SOURCE = ROOT / "archive/2026-11-11-two-period-did"
RESULTS = BASE / "results"
ASSETS = BASE / "assets"
os.environ.setdefault("MPLCONFIGDIR", str(BASE / ".cache" / "matplotlib"))

import numpy as np
import pandas as pd
import scipy
from scipy import stats
import statsmodels
import statsmodels.api as sm

METRICS = ["part", "nonpart", "total", "relative", "share_pp"]
LABELS = {"part": "パート", "nonpart": "パート以外", "total": "合計",
          "relative": "相対求人（P/N）", "share_pp": "パート比率"}
POST = "2025-11"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_panel():
    metrics = pd.read_csv(SOURCE / "results/metrics_prefecture_month.csv")
    policy = pd.read_csv(SOURCE / "results/policy.csv")
    assert not metrics.duplicated(["metric", "month", "pref"]).any()
    assert policy.pref.is_unique and len(policy) == 47
    assert policy.group.value_counts().to_dict() == {"early": 20, "late": 14, "excluded": 13}
    effective = pd.to_datetime(policy.effective_2025)
    expected = np.where(effective < pd.Timestamp("2025-11-01"), "early",
                        np.where(effective < pd.Timestamp("2025-12-01"), "excluded", "late"))
    assert np.array_equal(expected, policy.group)
    assert effective.min() >= pd.Timestamp("2025-10-01")
    months = [f"2025-{m:02d}" for m in range(1, 12)]
    window = metrics.loc[metrics.month.isin(months)]
    assert len(window) == 47 * 11 * 5
    wide = window.pivot(index=["pref", "month"], columns="metric", values="value").reset_index()
    wide.columns.name = None
    assert np.isfinite(wide[METRICS].to_numpy()).all()
    assert np.allclose(wide.relative, wide.part - wide.nonpart, atol=1e-10)
    wide = wide.merge(policy, on="pref", validate="many_to_one")
    selected = wide.loc[wide.group.isin(["early", "late"])].copy()
    selected["treat"] = (selected.group == "early").astype(int)
    selected["post"] = (selected.month == POST).astype(int)
    selected["did"] = selected.treat * selected.post
    selected = selected.sort_values(["pref", "month"]).reset_index(drop=True)
    panel = selected.loc[selected.month != "2025-10"].reset_index(drop=True)
    assert len(panel) == 340 and panel.pref.nunique() == 34
    assert panel.groupby("pref").size().eq(10).all()
    return panel, selected


def model(panel, metric, pre_end=9, event_study=False):
    pre = [f"2025-{m:02d}" for m in range(1, pre_end + 1)]
    frame = panel.loc[panel.month.isin(pre + [POST])].reset_index(drop=True)
    dummies = pd.get_dummies(frame[["pref", "month"]], drop_first=True, dtype=float)
    x = sm.add_constant(dummies, has_constant="add")
    if event_study:
        for month in pre[:-1] + [POST]:
            x[f"early_x_{month}"] = frame.treat * (frame.month == month).astype(float)
    else:
        x["did"] = frame.did.astype(float)
    rank = np.linalg.matrix_rank(x.to_numpy())
    assert rank == x.shape[1]
    fitted = sm.OLS(frame[metric].astype(float), x).fit(
        cov_type="cluster", cov_kwds={"groups": frame.pref, "use_correction": True,
                                      "df_correction": True}, use_t=True)
    assert fitted.df_resid_inference == 33

    # Independent least-squares / cluster-sandwich calculation, including all FE.
    a, y = x.to_numpy(), frame[metric].to_numpy()
    beta = np.linalg.lstsq(a, y, rcond=None)[0]
    residual = y - a @ beta
    scores = np.stack([a[frame.pref.eq(p)].T @ residual[frame.pref.eq(p)]
                       for p in frame.pref.unique()])
    bread = np.linalg.inv(a.T @ a)
    correction = 34 / 33 * (len(frame) - 1) / (len(frame) - rank)
    covariance = correction * bread @ (scores.T @ scores) @ bread
    cov_error = float(np.max(np.abs(covariance - fitted.cov_params().to_numpy())))
    assert np.max(np.abs(beta - fitted.params.to_numpy())) < 1e-9
    assert cov_error < 1e-8, cov_error
    return fitted, frame, dict(n_obs=len(frame), n_clusters=34, n_early=20, n_late=14,
                              n_pre_months=pre_end, n_post_months=1, model_rank=int(rank),
                              df_inference=33, crv1_correction=correction,
                              covariance_check_max_error=cov_error)


def linear_estimate(fit, vector):
    estimate = float(vector @ fit.params.to_numpy())
    variance = float(vector @ fit.cov_params().to_numpy() @ vector)
    assert variance >= -1e-10
    se = np.sqrt(max(variance, 0.))
    critical = stats.t.ppf(.975, fit.df_resid_inference)
    return dict(estimate=estimate, se=float(se), ci_low=float(estimate-critical*se),
                ci_high=float(estimate+critical*se),
                p_two_sided=float(2*stats.t.sf(abs(estimate/se), 33)) if se > 0 else np.nan,
                p_negative=float(stats.t.cdf(estimate/se, 33)) if se > 0 else np.nan)


def estimate_all(panel):
    original = pd.read_csv(SOURCE / "results/contrasts.csv")
    did_rows, monthly_rows, pretest_rows, audit = [], [], [], []
    for pre_end in [9, 7]:
        pre = [f"2025-{m:02d}" for m in range(1, pre_end + 1)]
        reference = pre[-1]
        for metric in METRICS:
            fit, frame, check = model(panel, metric, pre_end)
            v = np.zeros(len(fit.params)); v[fit.params.index.get_loc("did")] = 1
            result = linear_estimate(fit, v)
            old = original.loc[(original.metric == metric) &
                               (original.baseline_end == reference)].iloc[0]
            changes = (frame.loc[frame.month == POST].set_index("pref")[metric] -
                       frame.loc[frame.month.isin(pre)].groupby("pref")[metric].mean())
            groups = frame.drop_duplicates("pref").set_index("pref").group
            early, late = changes[groups == "early"], changes[groups == "late"]
            direct = float(early.mean() - late.mean())
            assert abs(result["estimate"] - direct) < 1e-9
            assert abs(result["estimate"] - old.estimate) < 1e-9
            did_rows.append(dict(metric=metric, baseline_end=reference, **result,
                                 **{k: val for k, val in check.items() if not k.startswith("covariance")},
                                 unit="percentage points" if metric == "share_pp" else "100 log points",
                                 early_change=float(early.mean()), late_change=float(late.mean()),
                                 original_estimate=float(old.estimate), original_welch_se=float(old.se),
                                 original_welch_ci_low=float(old.ci_low), original_welch_ci_high=float(old.ci_high),
                                 original_welch_p_two_sided=float(old.p_two_sided)))
            audit.append(dict(metric=metric, baseline_end=reference, model="monthly_did", **check))

            event, event_frame, event_check = model(panel, metric, pre_end, event_study=True)
            audit.append(dict(metric=metric, baseline_end=reference, model="event_study", **event_check))
            vectors = {}
            for month in pre + [POST]:
                v = np.zeros(len(event.params))
                if month != reference:
                    v[event.params.index.get_loc(f"early_x_{month}")] = 1
                vectors[month] = v
            restriction = np.stack([vectors[m] for m in pre[:-1]])
            test = event.f_test(restriction)
            joint_cov = restriction @ event.cov_params().to_numpy() @ restriction.T
            joint_beta = restriction @ event.params.to_numpy()
            assert np.linalg.matrix_rank(joint_cov) == pre_end - 1
            independent_f = float(joint_beta @ np.linalg.solve(joint_cov, joint_beta) / (pre_end - 1))
            assert abs(float(test.fvalue) - independent_f) < 1e-8
            assert abs(float(test.pvalue) - stats.f.sf(independent_f, pre_end-1, 33)) < 1e-10
            pretest_rows.append(dict(metric=metric, baseline_end=reference, reference_month=reference,
                                     f_statistic=float(test.fvalue), df_num=pre_end-1, df_denom=33,
                                     p_value=float(test.pvalue), n_obs=len(event_frame), n_clusters=34,
                                     null_hypothesis="All pre-period early-by-month coefficients equal zero"))
            if pre_end == 9:
                pre_average = np.mean([vectors[m] for m in pre], axis=0)
                raw_gaps = event_frame.groupby(["month", "group"])[metric].mean().unstack()
                raw_gaps = raw_gaps.early - raw_gaps.late
                for month in pre + [POST]:
                    relative_reference = linear_estimate(event, vectors[month])
                    relative_pre_mean = linear_estimate(event, vectors[month] - pre_average)
                    assert abs(relative_reference["estimate"] - (raw_gaps[month]-raw_gaps[reference])) < 1e-9
                    assert abs(relative_pre_mean["estimate"] - (raw_gaps[month]-raw_gaps[pre].mean())) < 1e-9
                    monthly_rows.append(dict(metric=metric, month=month, reference_month=reference,
                                             is_reference=month == reference, **relative_reference,
                                             **{f"{k}_vs_pre_mean": val for k, val in relative_pre_mean.items()},
                                             n_obs=340, n_clusters=34, df_inference=33))
    return pd.DataFrame(did_rows), pd.DataFrame(monthly_rows), pd.DataFrame(pretest_rows), audit


def make_figures(monthly, pretests, trends, estimates):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager

    font = SOURCE / "assets/NotoSansJP-Regular.otf"
    font_manager.fontManager.addfont(font)
    plt.rcParams.update({"font.family": font_manager.FontProperties(fname=font).get_name(),
                         "font.size": 12, "axes.spines.top": False, "axes.spines.right": False,
                         "figure.facecolor": "white", "axes.facecolor": "white",
                         "axes.unicode_minus": False, "savefig.dpi": 180})
    pre_color, post_color = "#475569", "#245A81"

    def event_panel(ax, metric, annotate=False):
        rows = monthly.loc[monthly.metric == metric].copy()
        for subset, color in [(rows.loc[(rows.month < POST) & ~rows.is_reference], pre_color),
                              (rows.loc[rows.month == POST], post_color)]:
            x = subset.month.str[-2:].astype(int)
            ax.errorbar(x, subset.estimate, yerr=[subset.estimate-subset.ci_low,
                                                subset.ci_high-subset.estimate],
                        fmt="o", color=color, capsize=4, markersize=5, elinewidth=1.4)
        ax.plot(9, 0, "o", color=pre_color, markerfacecolor="white", markersize=6)
        ax.axhline(0, color="#555555", lw=.9, linestyle="--")
        ax.axvspan(9.55, 10.45, color=".94", zorder=0)
        ax.set_xticks(range(1, 12), [f"{i}月" for i in range(1, 12)])
        ax.set_xlim(.55, 11.55)
        ax.grid(axis="y", color=".9", lw=.6)
        ax.set_axisbelow(True)
        p = pretests.loc[(pretests.metric == metric) & (pretests.baseline_end == "2025-09"), "p_value"].iloc[0]
        ax.set_title(f"{LABELS[metric]}  ｜  事前係数の共同検定 p = {p:.3f}", loc="left", fontsize=12)
        ax.set_ylabel("DID係数（100×対数差）")
        if annotate:
            post = rows.loc[rows.month == POST].iloc[0]
            ax.text(.01, .97, f"11月：{post.estimate:+.2f}  ［95%CI {post.ci_low:+.2f}, {post.ci_high:+.2f}］",
                    transform=ax.transAxes, va="top", fontsize=12, color=post_color)

    fig, ax = plt.subplots(figsize=(11.5, 5.8))
    event_panel(ax, "part", annotate=True)
    fig.suptitle("パート求人の月別DID係数", x=.09, ha="left", fontsize=19, y=.97)
    fig.text(.09, .89, "2025年9月 = 0  ｜  早期20県・後期14県  ｜  県・月固定効果", fontsize=11, color=".35")
    fig.text(.09, .045, "県クラスタ標準誤差による点ごとの95%信頼区間。9月は基準月、10月は移行月のため除外。", fontsize=10, color=".35")
    fig.subplots_adjust(left=.09, right=.97, bottom=.14, top=.79)
    fig.savefig(ASSETS / "monthly_did_part.png"); plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.6))
    for ax, key in zip(axes.flat, METRICS[:4]):
        event_panel(ax, key)
    plotted = monthly.loc[monthly.metric.isin(METRICS[:4])]
    lower, upper = float(plotted.ci_low.min()), float(plotted.ci_high.max())
    pad = (upper-lower)*.08
    for ax in axes.flat:
        ax.set_ylim(lower-pad, upper+pad)
    fig.suptitle("月別DID係数：求人の規模と構成", x=.08, ha="left", fontsize=19, y=.97)
    fig.text(.08, .92, "2025年9月 = 0  ｜  34県  ｜  県・月固定効果  ｜  各パネルの縦軸は共通", fontsize=11, color=".35")
    fig.text(.08, .035, "県クラスタ標準誤差による点ごとの95%信頼区間。9月は基準月、灰色の10月は推定から除外。", fontsize=10, color=".35")
    fig.subplots_adjust(left=.08, right=.98, bottom=.11, top=.84, wspace=.23, hspace=.40)
    fig.savefig(ASSETS / "monthly_did_all.png"); plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(13.2, 8.1))
    for ax, metric in zip(axes.flat, METRICS[:4]):
        for group, label, color, style in [("early", "早期：10月発効（20県）", "#245A81", "-"),
                                           ("late", "後期：12月以降発効（14県）", "#6B7280", "--")]:
            rows = trends.loc[(trends.metric == metric) & (trends.group == group)]
            ax.plot(rows.month.str[-2:].astype(int), rows.value, label=label,
                    color=color, linestyle=style, marker="o", markersize=3.5)
        ax.axvspan(9.55, 10.45, color=".94", zorder=0)
        ax.axhline(0, color=".6", lw=.7)
        ax.set_xticks(range(1, 12), [f"{i}月" for i in range(1, 12)])
        ax.set_xlim(.7, 11.3)
        ax.set_title(LABELS[metric], loc="left")
        ax.set_ylabel("前年同月比（100×対数差）")
        ax.grid(axis="y", color=".9", lw=.6)
    limits = [ax.get_ylim() for ax in axes.flat]
    for ax in axes.flat:
        ax.set_ylim(min(x[0] for x in limits), max(x[1] for x in limits))
    fig.suptitle("求人の月別推移（県等ウェイト）", x=.08, ha="left", fontsize=19, y=.98)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.55, .945), ncol=2, frameon=False, fontsize=11)
    fig.text(.08, .035, "2025年1〜11月。灰色の10月は推移のみ表示し、回帰には使用しない。", fontsize=10, color=".35")
    fig.subplots_adjust(left=.08, right=.98, bottom=.11, top=.84, wspace=.23, hspace=.35)
    fig.savefig(ASSETS / "monthly_trends.png"); plt.close(fig)


def run():
    RESULTS.mkdir(parents=True, exist_ok=True)
    ASSETS.mkdir(parents=True, exist_ok=True)
    source_paths = [SOURCE / "results" / f for f in ["metrics_prefecture_month.csv", "policy.csv", "contrasts.csv"]]
    hashes = {str(p.relative_to(ROOT)): digest(p) for p in source_paths}
    panel, trends_panel = read_panel()
    estimates, monthly, pretests, audit = estimate_all(panel)
    trends = (trends_panel.melt(id_vars=["pref", "month", "group"], value_vars=METRICS,
                                var_name="metric", value_name="value")
              .groupby(["metric", "month", "group"]).agg(value=("value", "mean"), n_pref=("pref", "nunique")).reset_index())
    panel.to_csv(RESULTS / "monthly_panel.csv", index=False)
    estimates.to_csv(RESULTS / "did_estimates.csv", index=False)
    monthly.to_csv(RESULTS / "monthly_coefficients.csv", index=False)
    pretests.to_csv(RESULTS / "pretrend_tests.csv", index=False)
    trends.to_csv(RESULTS / "group_month_means.csv", index=False)
    make_figures(monthly, pretests, trends, estimates)
    assert all(digest(ROOT / p) == expected for p, expected in hashes.items())
    record = dict(source_sha256=hashes, source_read_only=True, python=platform.python_version(),
                  packages={"numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
                            "statsmodels": statsmodels.__version__},
                  sample=dict(prefectures=34, early=20, late=14, excluded=13, observations=340,
                              pre_months=[f"2025-{i:02d}" for i in range(1,10)], post_months=[POST],
                              omitted_transition_month="2025-10"),
                  original_point_estimates_matched=10, monthly_contrasts_checked=50,
                  original_files_unchanged=True, regression_checks=audit)
    (BASE / "analysis_checks.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n")
    print(estimates.loc[estimates.baseline_end == "2025-09", ["metric", "estimate", "se", "ci_low", "ci_high", "p_two_sided"]].to_string(index=False))
    print("\nPretrend joint tests:")
    print(pretests[["metric", "baseline_end", "f_statistic", "p_value"]].to_string(index=False))


if __name__ == "__main__":
    run()
