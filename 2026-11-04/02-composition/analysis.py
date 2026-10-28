"""Recruitment composition: transparent prefecture differences."""
import numpy as np
import pandas as pd
from scipy import stats


def contrast(d, groups):
    """Equal-prefecture early-minus-late mean; Welch descriptive interval."""
    early = d.loc[groups[groups == 'early'].index].dropna().to_numpy()
    late = d.loc[groups[groups == 'late'].index].dropna().to_numpy()
    if len(early) < 2 or len(late) < 2:
        raise ValueError('At least two prefectures per group are required')
    a, b = early.var(ddof=1)/len(early), late.var(ddof=1)/len(late)
    estimate = float(early.mean()-late.mean())
    se = float(np.sqrt(a+b))
    if se == 0:
        raise ValueError('Zero sampling variance')
    df = float((a+b)**2/(a*a/(len(early)-1)+b*b/(len(late)-1)))
    critical = float(stats.t.ppf(.975, df))
    return dict(estimate=estimate, early_mean=float(early.mean()), late_mean=float(late.mean()),
                n_early=len(early), n_late=len(late), se=se, df=df,
                ci_low=estimate-critical*se, ci_high=estimate+critical*se,
                p_negative=float(stats.t.cdf(estimate/se, df)),
                p_two_sided=float(2*stats.t.sf(abs(estimate/se), df)))


def log_yoy(wide):
    if not (wide > 0).all().all():
        raise ValueError('Vacancies must be strictly positive')
    expected = pd.period_range(wide.index.min(), wide.index.max(), freq='M')
    if not wide.index.equals(expected):
        raise ValueError('Months must be consecutive and unique')
    return 100 * (np.log(wide) - np.log(wide.shift(12)))


def ces_choice(cp, cn, sigma=2., beta=.5, a=.5, B=2., qp=1., qn=1.):
    """Illustrative CES recruitment choice, not an estimated model.

    H=qV is an explicit conversion assumption. Cost is per expected recruit.
    Revenue B*Z**beta/beta; CES Z has weights a and 1-a.
    """
    if not (cp > 0 and cn > 0 and sigma > 0 and 0 < beta < 1 and 0 < a < 1
            and B > 0 and 0 < qp <= 1 and 0 < qn <= 1):
        raise ValueError('Invalid CES parameter domain')
    if abs(sigma-1) < 1e-10:
        C = (cp/a)**a * (cn/(1-a))**(1-a)
    else:
        C = (a**sigma*cp**(1-sigma)+(1-a)**sigma*cn**(1-sigma))**(1/(1-sigma))
    Z = (B/C)**(1/(1-beta))
    hp = Z*a**sigma*(C/cp)**sigma
    hn = Z*(1-a)**sigma*(C/cn)**sigma
    return dict(P=float(hp/qp), N=float(hn/qn), H_P=float(hp), H_N=float(hn),
                total=float(hp/qp+hn/qn), Z=float(Z), C=float(C),
                cost=float(cp*hp+cn*hn))


# Everything written by this script stays inside this deliverable directory.
from pathlib import Path
import hashlib
import json
import re
import unicodedata
import urllib.request
import platform

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
RESULTS = BASE/'results'
ASSETS = BASE/'assets'
RAW = ROOT/'data'/'raw'
TYPES = {'total': 0, 'nonpart': 1, 'part': 2}
LABELS = {'part': 'パート', 'nonpart': 'パート以外', 'total': '合計',
          'relative': '相対求人（P/N）', 'share_pp': 'パート比率（pp）'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_vacancies(path):
    book = pd.ExcelFile(path)
    expected = ['パート含む一般', 'パート除く一般', '一般パート']
    for i, label in enumerate(expected):
        assert label in book.sheet_names[i], (i, book.sheet_names[i])
    frames, audit = {}, {}
    for key, sheet_index in TYPES.items():
        raw = pd.read_excel(book, sheet_name=sheet_index, header=None)
        names = raw.iloc[1, 3:51].tolist()
        assert names[0] == '全国' and len(set(names[1:])) == 47
        rows = raw[raw[2].notna() & raw[0].astype(str).str.fullmatch(r'\d{4}年')].copy()
        years = rows[0].str.extract(r'(\d{4})')[0].astype(int)
        months = rows[2].map(lambda x: unicodedata.normalize('NFKC', str(x))).str.extract(r'(\d+)')[0].astype(int)
        wide = rows.iloc[:, 3:51].astype(float)
        wide.columns = names
        wide.index = pd.PeriodIndex.from_fields(year=years, month=months, freq='M')
        wide.index.name = 'month'
        assert wide.index.is_unique and wide.columns.is_unique
        assert wide.index.equals(pd.period_range('2013-01', '2026-08', freq='M'))
        assert np.isfinite(wide.to_numpy()).all() and (wide > 0).all().all()
        assert np.array_equal(wide.to_numpy(), np.round(wide.to_numpy()))
        residual = wide['全国']-wide.drop(columns='全国').sum(axis=1)
        assert residual.eq(0).all(), f'National sum mismatch: {key}'
        audit[key] = dict(sheet=book.sheet_names[sheet_index], title=str(raw.iloc[0,0]),
                          months=len(wide), prefectures=47, start=str(wide.index.min()),
                          end=str(wide.index.max()), national_max_abs_residual=float(residual.abs().max()),
                          missing_cells=int(wide.isna().sum().sum()))
        frames[key] = wide
    residual = frames['total']-frames['part']-frames['nonpart']
    assert (residual == 0).all().all(), 'Part plus nonpart identity failed'
    audit['part_plus_nonpart_max_abs_residual'] = float(residual.abs().max().max())
    return frames, audit


def load_policy(path, prefs):
    raw = pd.read_excel(path, header=None)
    out = pd.DataFrame(index=pd.Index(prefs, name='pref'))
    provenance = {}
    for label, yr in [('令和６年度', 2024), ('令和７年度', 2025)]:
        cols = raw.columns[raw.iloc[0] == label].tolist()
        assert len(cols) == 1
        j = cols[0]
        assert raw.iloc[1, j] == '改定額(円)' and raw.iloc[1, j+1] == '発効年月日'
        block = raw.iloc[2:49, [0, j, j+1]]
        def name(x):
            s = ''.join(str(x).split())
            candidates = [v for v in [s, s+'県', s+'府', s+'都'] if v in prefs]
            assert len(candidates) == 1
            return candidates[0]
        assert block.iloc[:, 0].map(name).tolist() == prefs
        out[f'mw_{yr}'] = block.iloc[:, 1].astype(int).to_numpy()
        out[f'effective_{yr}'] = pd.to_datetime(block.iloc[:, 2]).to_numpy()
        provenance[str(yr)] = {'header': label, 'zero_based_wage_column': int(j),
                               'zero_based_date_column': int(j+1), 'excel_rows': '3:49'}
    assert out['effective_2025'].between('2025-10-01', '2026-03-31').all()
    out['raise_yen'] = out.mw_2025-out.mw_2024
    out['raise_pct'] = 100*out.raise_yen/out.mw_2024
    out['group'] = out.effective_2025.map(lambda d: 'early' if d < pd.Timestamp('2025-11-01')
                                       else 'excluded' if d < pd.Timestamp('2025-12-01') else 'late')
    assert out.group.value_counts().to_dict() == {'early': 20, 'late': 14, 'excluded': 13}
    assert out.loc[out.group == 'early', 'effective_2025'].max() < pd.Timestamp('2025-11-01')
    assert out.loc[out.group == 'late', 'effective_2025'].min() >= pd.Timestamp('2025-12-01')
    return out, provenance


def check_policy_pdf(policy):
    """Independent official R7 PDF, p4 (printed p3): check all 47 rows."""
    import pymupdf
    path = BASE/'evidence'/'MHLW_2025_wages.pdf'
    with pymupdf.open(path) as doc:
        hits = [(i+1, p.get_text()) for i,p in enumerate(doc) if '地域別最低賃金額一覧' in p.get_text()]
    assert len(hits) == 1
    page, text = hits[0]
    rows = []
    for pref, row in policy.iterrows():
        short = pref if pref == '北海道' else pref[:-1]
        pattern = re.escape(short)+r'\s+([\d,]+)\s+\((\d+)\)\s+(\d+)\s+R[78]\.\d+\.\d+\s+R([78])\.(\d+)\.(\d+)'
        matches = re.findall(pattern, text)
        assert len(matches) == 1, (pref, matches)
        new, old, increase, era, month, day = matches[0]
        date = pd.Timestamp(2018+int(era), int(month), int(day))
        assert int(new.replace(',', '')) == row.mw_2025
        assert int(old) == row.mw_2024
        assert int(increase) == row.raise_yen
        assert date == row.effective_2025
        rows.append(dict(pref=pref, mw_2024=int(old), mw_2025=int(new.replace(',', '')),
                         effective_2025=str(date.date()), source_pdf_page=page, matched=True))
    pd.DataFrame(rows).to_csv(RESULTS/'policy_independent_crosscheck.csv', index=False)
    return dict(pdf_page=page, matched_prefectures=len(rows), source_sha256=digest(path))


def prepare_metrics(frames):
    levels = {k: v.drop(columns='全国') for k,v in frames.items()}
    metrics = {k: log_yoy(v) for k,v in levels.items()}
    # This is the exact within-prefecture type difference, not an untreated control.
    metrics['relative'] = metrics['part']-metrics['nonpart']
    ratio_yoy = log_yoy(levels['part']/levels['nonpart'])
    assert np.allclose(metrics['relative'].iloc[12:], ratio_yoy.iloc[12:], atol=1e-10)
    share = levels['part']/levels['total']
    metrics['share_pp'] = 100*(share-share.shift(12))
    assert ((share > 0) & (share < 1)).all().all()
    return levels, metrics, share


def estimate(metrics, policy, pre_end):
    deltas = pd.DataFrame(index=policy.index)
    summaries, means = [], []
    for key, wide in metrics.items():
        pre = wide.loc['2025-01':pre_end]
        assert len(pre) == int(pre_end[-2:]) and pre.notna().all().all()
        nov = wide.loc['2025-11']
        deltas[key] = nov-pre.mean(axis=0)
        result = contrast(deltas[key], policy.group)
        result.update({'metric': key, 'baseline_end': pre_end, 'measure_unit':
                       'percentage points' if key == 'share_pp' else '100 log points'})
        summaries.append(result)
        for group in ['early', 'late']:
            names = policy.index[policy.group == group]
            means.append(dict(metric=key, baseline_end=pre_end, group=group, n=len(names),
                              baseline=float(pre[names].mean().mean()), november=float(nov[names].mean()),
                              change=float(deltas.loc[names,key].mean())))
    assert np.allclose(deltas.relative, deltas.part-deltas.nonpart, atol=1e-10)
    return pd.DataFrame(summaries), deltas.join(policy), pd.DataFrame(means)


def model_checks():
    probes = []
    max_ratio, max_foc, max_dual, max_deriv, max_scale = 0., 0., 0., 0., 0.
    for sigma in [.05, .5, .99999, 1., 1.00001, 2., 8.]:
        for beta in [.2, .5, .7]:
            for a in [.2, .5, .8]:
                b = ces_choice(1, 1, sigma=sigma, beta=beta, a=a)
                x = ces_choice(1.1, 1.02, sigma=sigma, beta=beta, a=a)
                ratio = (a/(1-a)*1.02/1.1)**sigma
                max_ratio = max(max_ratio, abs(x['P']/x['N']/ratio-1))
                max_dual = max(max_dual, abs(x['cost']/(x['C']*x['Z'])-1))
                # Reconstruct primal CES, independent from dual-cost computation.
                if sigma == 1:
                    z = x['H_P']**a*x['H_N']**(1-a)
                else:
                    rho = (sigma-1)/sigma
                    z = (a*x['H_P']**rho+(1-a)*x['H_N']**rho)**(1/rho)
                max_foc = max(max_foc, abs(z/x['Z']-1))
                e = 1e-5
                plus = ces_choice(np.exp(e), 1, sigma=sigma, beta=beta, a=a)
                minus = ces_choice(np.exp(-e), 1, sigma=sigma, beta=beta, a=a)
                s_p = b['H_P']/(b['H_P']+b['H_N'])
                analytic_n = (sigma-1/(1-beta))*s_p
                finite_n = (np.log(plus['N'])-np.log(minus['N']))/(2*e)
                max_deriv = max(max_deriv, abs(analytic_n-finite_n))
                common = ces_choice(1.1, 1.1, sigma=sigma, beta=beta, a=a)
                max_scale = max(max_scale, abs(common['P']/b['P']-1.1**(-1/(1-beta))))
                probes.append(dict(sigma=sigma, beta=beta, a=a, cp=1.1, cn=1.02,
                                   P_change_log100=100*np.log(x['P']/b['P']),
                                   N_change_log100=100*np.log(x['N']/b['N']),
                                   total_change_log100=100*np.log(x['total']/b['total']),
                                   relative_change_log100=100*np.log((x['P']/x['N'])/(b['P']/b['N']))))
    assert max_ratio < 1e-8 and max_foc < 1e-8 and max_dual < 1e-8
    assert max_deriv < 5e-5 and max_scale < 1e-8
    # Near-Leontief: relative response approaches zero; Cobb-Douglas continuity.
    zero = ces_choice(1.1, 1, sigma=1e-4)
    assert abs(np.log(zero['P']/zero['N'])) < 1e-4
    cd = ces_choice(1.1, 1.02, sigma=1.)
    assert abs(ces_choice(1.1, 1.02, sigma=1.00001)['P']/cd['P']-1) < 1e-4
    pd.DataFrame(probes).to_csv(RESULTS/'model_illustration_NOT_ESTIMATED.csv', index=False)
    return dict(probes=len(probes), max_relative_ratio_error=max_ratio, max_primal_error=max_foc,
                max_dual_error=max_dual, max_derivative_error=max_deriv, max_common_scale_error=max_scale,
                leontief_limit=True, cobb_douglas_limit=True, parameters_estimated=False)


def make_figures(metrics, policy, results):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib import font_manager
    font = ASSETS/'NotoSansJP-Regular.otf'
    if not font.exists():
        part = font.with_suffix('.part')
        urllib.request.urlretrieve('https://github.com/notofonts/noto-cjk/raw/main/Sans/SubsetOTF/JP/NotoSansJP-Regular.otf', part)
        part.replace(font)
    font_manager.fontManager.addfont(font)
    plt.rcParams.update({'font.family': font_manager.FontProperties(fname=font).get_name(),
                         'font.size': 12, 'axes.spines.top': False, 'axes.spines.right': False,
                         'figure.facecolor': 'white', 'axes.facecolor': 'white', 'savefig.dpi': 170})
    fig, axes = plt.subplots(2, 2, figsize=(11.8, 6.2), constrained_layout=True)
    fig.get_layout_engine().set(h_pad=0.06, w_pad=0.04)
    for ax, key in zip(axes.flat, ['part','nonpart','total','relative']):
        for group, label, ls, color in [('early','10月発効（20県）','-','black'),
                                        ('late','12月以降（14県）','--','#666666')]:
            names = policy.index[policy.group == group]
            s = metrics[key].loc['2025-01':'2025-11', names].mean(axis=1)
            ax.plot(s.index.to_timestamp(), s, label=label, linestyle=ls, color=color, marker='o', markersize=3)
        ax.axvspan(pd.Timestamp('2025-10-01'), pd.Timestamp('2025-10-31'), color='.93')
        ax.axvline(pd.Timestamp('2025-11-01'), color='.4', linewidth=.7)
        ax.axhline(0, color='.7', linewidth=.7)
        ax.set_title(LABELS[key], loc='left')
        ax.set_ylabel('前年同月差：100×対数差')
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1,3,5,7,9,11]))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m月'))
    handles, labels = axes[0,0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='outside lower center', ncol=2, frameon=False, fontsize=11)
    fig.savefig(ASSETS/'observed_trends.png', bbox_inches='tight'); plt.close(fig)
    fig, ax = plt.subplots(figsize=(10.8, 4), constrained_layout=True)
    use = results[(results.baseline_end == '2025-09') & (results.metric != 'share_pp')].set_index('metric')
    for i,k in enumerate(['part','nonpart','total','relative']):
        r = use.loc[k]
        ax.errorbar(r.estimate, i, xerr=[[r.estimate-r.ci_low],[r.ci_high-r.estimate]],
                    fmt='o', color='black', capsize=5)
        ax.text(r.ci_high+.2, i, f'{r.estimate:+.2f}  [{r.ci_low:+.2f}, {r.ci_high:+.2f}]', va='center', fontsize=11)
    ax.set_yticks(range(4), [LABELS[k] for k in ['part','nonpart','total','relative']])
    ax.invert_yaxis(); ax.axvline(0, color='.5', linestyle='--')
    ax.set_xlabel('早期−後期：11月の前年比 − 1〜9月の平均前年比（100×対数差）')
    ax.set_xlim(min(use.ci_low)-1, max(use.ci_high)+6)
    fig.savefig(ASSETS/'observed_contrasts.png'); plt.close(fig)


def _rows(frame):
    """Plain float/str records for JSON (avoids mixed-type dict updates)."""
    keys = ['estimate','early_mean','late_mean','n_early','n_late','se','df',
            'ci_low','ci_high','p_negative','p_two_sided']
    return [{**{k: float(row[k]) for k in keys},
             'metric': str(row['metric']), 'baseline_end': str(row['baseline_end']),
             'measure_unit': str(row['measure_unit'])} for _, row in frame.iterrows()]


def run():
    RESULTS.mkdir(exist_ok=True); ASSETS.mkdir(exist_ok=True)
    paths = [RAW/'estat_shokugyo_t12_shinki_kyujin.xlsx', RAW/'mhlw_saitei_chingin_kaitei.xlsx']
    hashes = {p.name: digest(p) for p in paths}
    frames, data_audit = load_vacancies(paths[0])
    prefs = frames['part'].drop(columns='全国').columns.tolist()
    policy, headers = load_policy(paths[1], prefs)
    policy.to_csv(RESULTS/'policy.csv')
    pdf_check = check_policy_pdf(policy)
    levels, metrics, share = prepare_metrics(frames)
    for key in TYPES:
        frames[key].to_csv(RESULTS/f'level_{key}_all_months.csv')
    stacked = (pd.concat({k: v.rename_axis(index='month', columns='pref')
                          for k, v in metrics.items()}, names=['metric'])
               .stack().rename('value').reset_index())
    stacked.to_csv(RESULTS/'metrics_prefecture_month.csv', index=False)
    share.to_csv(RESULTS/'share_part.csv')
    output, groupmeans = [], []
    for end in ['2025-09','2025-07']:
        summary, deltas, means = estimate(metrics, policy, end)
        deltas.to_csv(RESULTS/f'prefecture_changes_pre_{end}.csv')
        output.append(summary); groupmeans.append(means)
    results = pd.concat(output, ignore_index=True)
    results.to_csv(RESULTS/'contrasts.csv', index=False)
    pd.concat(groupmeans, ignore_index=True).to_csv(RESULTS/'group_means.csv', index=False)
    # Exact D(relative)=D(part)-D(nonpart), including the county covariance.
    for end in ['2025-09','2025-07']:
        r = results[results.baseline_end == end].set_index('metric')
        assert np.isclose(r.loc['relative','estimate'], r.loc['part','estimate']-r.loc['nonpart','estimate'])
    model = model_checks()
    make_figures(metrics, policy, results)
    assert {p.name: digest(p) for p in paths} == hashes
    verification = dict(status='analysis_passed', fixed_seed=20261104, randomization_used=False,
                        python=platform.python_version(), pandas=pd.__version__, numpy=np.__version__,
                        input_sha256=hashes, inputs_unchanged=True, data=data_audit,
                        wage_headers=headers, independent_policy_check=pdf_check,
                        policy_group_counts=policy.group.value_counts().to_dict(),
                        model=model, type_difference_identity=True,
                        weighting='equal prefectures; no population or vacancy weights',
                        inference='Welch t interval: independent-prefecture descriptive approximation, not causal inference',
                        results=_rows(results))
    (BASE/'verification.json').write_text(json.dumps(verification, ensure_ascii=False, indent=2))
    print(results[['metric','baseline_end','estimate','ci_low','ci_high','p_negative','p_two_sided']].to_string(index=False))
    print('Data, policy, model and identity checks passed. Inputs unchanged.')
    return verification


if __name__ == '__main__':
    run()
