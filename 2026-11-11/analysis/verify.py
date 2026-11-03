"""Read-only source validation; writes this folder's verification.json only."""
from pathlib import Path
import argparse
import hashlib
import json
import math
import re
import unicodedata

import numpy as np
import pandas as pd
from scipy import stats
from openpyxl import load_workbook

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
OLD = ROOT / "archive/2026-11-11-two-period-did"
METRICS = ["part", "nonpart", "total", "relative", "share_pp"]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def raw_values():
    path = ROOT / "data/raw/estat_shokugyo_t12_shinki_kyujin.xlsx"
    book = load_workbook(path, read_only=True, data_only=True)
    levels = {}
    for sheet_index, metric, sheet_label in [(0, "total", "パート含む一般"),
                                            (1, "nonpart", "パート除く一般"),
                                            (2, "part", "一般パート")]:
        sheet = book.worksheets[sheet_index]
        assert sheet_label in sheet.title
        rows = sheet.iter_rows(values_only=True)
        next(rows)
        names = list(next(rows)[3:51])
        assert names[0] == "全国" and len(set(names[1:])) == 47
        values = {}
        for row in rows:
            year = re.fullmatch(r"(\d{4})年", str(row[0]))
            month = re.fullmatch(r"\s*(\d+)月\s*", unicodedata.normalize("NFKC", str(row[2])))
            if year is None or month is None:
                continue
            date = f"{int(year[1]):04d}-{int(month[1]):02d}"
            cells = [float(x) for x in row[3:51]]
            assert all(x > 0 and x == int(x) for x in cells)
            assert sum(cells[1:]) == cells[0]
            assert date not in values
            values[date] = dict(zip(names[1:], cells[1:]))
        assert len(values) == 164 and min(values) == "2013-01" and max(values) == "2026-08"
        levels[metric] = values
    book.close()
    for date in levels["total"]:
        for pref in names[1:]:
            assert levels["total"][date][pref] == levels["part"][date][pref] + levels["nonpart"][date][pref]
    recomputed = {}
    for month in range(1,12):
        current, previous = f"2025-{month:02d}", f"2024-{month:02d}"
        for pref in names[1:]:
            values = {key: 100 * math.log(levels[key][current][pref] / levels[key][previous][pref])
                      for key in ["part", "nonpart", "total"]}
            values["relative"] = values["part"] - values["nonpart"]
            values["share_pp"] = 100 * (levels["part"][current][pref] / levels["total"][current][pref] -
                                         levels["part"][previous][pref] / levels["total"][previous][pref])
            recomputed[(pref, current)] = values
    return recomputed


def verify_policy():
    policy = pd.read_csv(OLD / "results/policy.csv")
    book = load_workbook(ROOT / "data/raw/mhlw_saitei_chingin_kaitei.xlsx", read_only=True, data_only=True)
    rows = list(book.worksheets[0].iter_rows(values_only=True))
    book.close()
    index = list(rows[0]).index("令和７年度")
    for row, saved in zip(rows[2:49], policy.itertuples()):
        short = "".join(str(row[0]).split())
        assert saved.pref in [short, short+"県", short+"府", short+"都"]
        assert int(row[index]) == saved.mw_2025
        assert str(row[index+1].date()) == saved.effective_2025
    assert len(policy) == 47
    return policy


def run(before=None):
    raw = raw_values()
    policy = verify_policy()
    panel = pd.read_csv(BASE / "results/monthly_panel.csv")
    assert len(panel) == 340 and panel.pref.nunique() == 34
    assert not panel.duplicated(["pref", "month"]).any()
    assert set(panel.month) == {f"2025-{m:02d}" for m in list(range(1,10))+[11]}
    assert panel.groupby("pref").size().eq(10).all()
    error = max(abs(getattr(row, metric) - raw[(row.pref, row.month)][metric])
                for row in panel.itertuples() for metric in METRICS)
    assert error < 1e-9
    old_metrics = pd.read_csv(OLD / "results/metrics_prefecture_month.csv")
    old_window = old_metrics.loc[old_metrics.month.between("2025-01", "2025-11")]
    assert len(old_window) == 2585
    assert max(abs(row.value-raw[(row.pref,row.month)][row.metric]) for row in old_window.itertuples()) < 1e-9
    estimates = pd.read_csv(BASE / "results/did_estimates.csv")
    pretests = pd.read_csv(BASE / "results/pretrend_tests.csv")
    prefs = policy.loc[policy.group.isin(["early", "late"]), "pref"].tolist()
    treated = policy.set_index("pref").loc[prefs, "group"].eq("early").to_numpy()
    max_se_error, max_f_error = 0., 0.
    for end in [9,7]:
        months = [f"2025-{m:02d}" for m in range(1,end+1)] + ["2025-11"]
        for metric in METRICS:
            # Frisch–Waugh–Lovell, directly from raw XLSX; no design-matrix code reused.
            y = np.array([[raw[(pref, month)][metric] for month in months] for pref in prefs])
            post = np.array([0]*(len(months)-1)+[1])
            x = treated[:,None] * post[None,:]
            yw = y-y.mean(axis=1,keepdims=True)-y.mean(axis=0,keepdims=True)+y.mean()
            xw = x-x.mean(axis=1,keepdims=True)-x.mean(axis=0,keepdims=True)+x.mean()
            beta = float((xw*yw).sum()/(xw*xw).sum())
            residual = yw-beta*xw
            n = y.size; g, t = y.shape
            factor = g/(g-1)*(n-1)/(n-(g+t))
            se = math.sqrt(factor*((xw*residual).sum(axis=1)**2).sum()/(xw*xw).sum()**2)
            saved = estimates.loc[(estimates.metric == metric) &
                                  (estimates.baseline_end == f"2025-{end:02d}")].iloc[0]
            assert abs(beta-saved.estimate) < 1e-9
            assert abs(se-saved.se) < 1e-9
            max_se_error = max(max_se_error, abs(se-saved.se))
            critical = stats.t.ppf(.975,g-1)
            assert abs(saved.ci_low-(beta-critical*se)) < 1e-9
            assert abs(saved.ci_high-(beta+critical*se)) < 1e-9
            assert abs(saved.p_two_sided-2*stats.t.sf(abs(beta/se),g-1)) < 1e-10

            # Joint pretrend test from multivariate county changes to the last pre month.
            z = y[:,:end-1] - y[:,end-1,None]
            early, late = z[treated], z[~treated]
            gap = early.mean(axis=0)-late.mean(axis=0)
            er, lr = early-early.mean(axis=0), late-late.mean(axis=0)
            covariance = er.T@er/len(early)**2 + lr.T@lr/len(late)**2
            event_rank = g+2*t-2
            covariance *= g/(g-1)*(n-1)/(n-event_rank)
            f_value = float(gap@np.linalg.solve(covariance,gap)/(end-1))
            expected = pretests.loc[(pretests.metric==metric) &
                                    (pretests.baseline_end==f"2025-{end:02d}")].iloc[0]
            assert abs(f_value-expected.f_statistic) < 1e-8
            assert abs(stats.f.sf(f_value,end-1,g-1)-expected.p_value) < 1e-9
            max_f_error = max(max_f_error,abs(f_value-expected.f_statistic))
    assert len(estimates) == 10 and len(pretests) == 10
    checks = json.loads((BASE / "analysis_checks.json").read_text())
    for name, expected in checks["source_sha256"].items():
        assert digest(ROOT / name) == expected
    preserved = None
    if before:
        baseline = json.loads(Path(before).read_text())
        changed = [p for p, expected in baseline.items()
                   if not (ROOT / p).exists() or digest(ROOT / p) != expected]
        assert not changed, changed
        preserved = len(baseline)
    record = dict(status="passed", raw_metric_values_checked=2585,
                  regression_input_values_checked=1700, raw_months=164, raw_prefectures=47,
                  policy_rows_matched=47, monthly_observations=340, prefecture_clusters=34,
                  independent_did_and_cluster_se_checks=10, independent_pretrend_checks=10,
                  max_metric_error=error, max_cluster_se_error=max_se_error,
                  max_pretrend_f_error=max_f_error, preexisting_tracked_files_unchanged=preserved,
                  raw_source_sha256={str(p.relative_to(ROOT)): digest(p) for p in
                                     [ROOT / "data/raw/estat_shokugyo_t12_shinki_kyujin.xlsx",
                                      ROOT / "data/raw/mhlw_saitei_chingin_kaitei.xlsx"]})
    (BASE / "verification.json").write_text(json.dumps(record,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(record, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", help="Optional JSON of tracked-file hashes captured before this task")
    run(parser.parse_args().before)
