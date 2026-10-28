#!/usr/bin/env python3
"""課題3・4: 既発表の県別比較を再計算する。原データは読み取り専用。
Run: python 2026-11-04/01-basic/analysis.py
Dependencies: numpy pandas openpyxl scipy matplotlib (see requirements.txt).
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import unicodedata
import urllib.request
import numpy as np
import pandas as pd
from scipy import stats, optimize
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / 'data' / 'raw'
FILES = ['estat_shokugyo_t12_shinki_kyujin.xlsx', 'mhlw_saitei_chingin_kaitei.xlsx']
EARLY, MIDDLE, LATE = '10月発効', '11月発効', '12月以降発効'
SEED = 20261104


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_t12(path, sheet):
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    names = raw.iloc[1, 3:].tolist()
    assert names[0] == '全国' and len(names) == 48
    mask = raw[2].notna() & raw[0].astype(str).str.match(r'^\d{4}年')
    rows = raw.loc[mask]
    years = rows[0].astype(str).str.extract(r'(\d{4})')[0].astype(int)
    months = rows[2].map(lambda x: unicodedata.normalize('NFKC', str(x))).str.extract(r'(\d+)')[0].astype(int)
    result = rows.iloc[:, 3:51].astype(float)
    result.columns = names
    result.index = pd.PeriodIndex.from_fields(year=years, month=months, freq='M')
    result.index.name = 'month'
    assert not result.index.duplicated().any()
    assert result.index.equals(pd.period_range(result.index.min(), result.index.max(), freq='M', name='month'))
    assert result.notna().all().all() and (result > 0).all().all()
    assert np.array_equal(result['全国'].values, result.drop(columns='全国').sum(axis=1).values)
    return result


def load_policy(path, prefs):
    raw = pd.read_excel(path, header=None)
    out = pd.DataFrame(index=pd.Index(prefs, name='pref'))
    columns = {}
    for year, label in [(2024, '令和６年度'), (2025, '令和７年度')]:
        matches = list(raw.columns[raw.iloc[0].eq(label)])
        assert len(matches) == 1, f'年度見出しが一意でない: {label}'
        col = int(matches[0])
        assert raw.iloc[1, col] == '改定額(円)' and raw.iloc[1, col+1] == '発効年月日'
        def match_name(s):
            s = ''.join(str(s).split())
            candidates = [n for n in [s, s+'県', s+'府', s+'都'] if n in prefs]
            assert len(candidates) == 1
            return candidates[0]
        block = raw.iloc[2:49, [0, col, col+1]].copy()
        block.columns = ['pref', 'wage', 'effective']
        block['pref'] = block['pref'].map(match_name)
        assert block['pref'].tolist() == prefs
        out[f'mw_{year}'] = pd.to_numeric(block['wage']).astype(int).values
        out[f'effective_{year}'] = pd.to_datetime(block['effective']).values
        columns[str(year)] = {'label': label, 'excel_wage_column_1based': col+1,
                              'excel_date_column_1based': col+2, 'excel_rows_1based': [3,49]}
    assert out.index.nunique() == 47 and (out.mw_2025 > out.mw_2024).all()
    dates = out.effective_2025
    assert dates.between('2025-10-01', '2026-03-31').all()
    out['group'] = np.select([dates.dt.to_period('M').eq(pd.Period('2025-10')),
                              dates.dt.to_period('M').eq(pd.Period('2025-11'))], [EARLY,MIDDLE], default=LATE)
    assert out.group.value_counts().to_dict() == {EARLY:20, LATE:14, MIDDLE:13}
    assert out.loc[out.group.eq(EARLY),'effective_2025'].lt(pd.Timestamp('2025-11-01')).all()
    assert out.loc[out.group.eq(LATE),'effective_2025'].gt(pd.Timestamp('2025-11-30')).all()
    out['raise_yen'] = out.mw_2025-out.mw_2024
    out['raise_pct'] = 100*out.raise_yen/out.mw_2024
    return out, columns


def welch_difference(early, late):
    a, b = np.asarray(early, dtype=float), np.asarray(late, dtype=float)
    assert len(a)>1 and len(b)>1 and np.isfinite(a).all() and np.isfinite(b).all()
    va, vb = a.var(ddof=1)/len(a), b.var(ddof=1)/len(b)
    se = np.sqrt(va+vb)
    df = (va+vb)**2/(va**2/(len(a)-1)+vb**2/(len(b)-1))
    delta = a.mean()-b.mean()
    t = delta/se
    crit = stats.t.ppf(.975, df)
    lower, upper = delta-crit*se, delta+crit*se
    reference = stats.ttest_ind(a,b,equal_var=False)
    assert np.isclose(t, reference.statistic) and np.isclose(df, reference.df)
    # Group-dummy OLS coefficient is exactly the unweighted mean difference.
    X = np.column_stack([np.ones(len(a)+len(b)), np.r_[np.ones(len(a)),np.zeros(len(b))]])
    ols = np.linalg.lstsq(X, np.r_[a,b], rcond=None)[0][1]
    assert np.isclose(delta, ols)
    return dict(n_early=len(a), n_late=len(b), d_early=float(a.mean()), d_late=float(b.mean()),
                delta=float(delta), se=float(se), df=float(df), t=float(t), ci_low=float(lower), ci_high=float(upper),
                p_one_sided_negative=float(stats.t.cdf(t,df)), p_two_sided=float(reference.pvalue), ols_delta=float(ols))


def desired_employment(w, p=20., A=5., K=10., alpha=.3, beta=.6, hours=160.):
    if w <= 0 or p <= 0 or A <= 0 or K <= 0 or hours <= 0 or not (0<beta<1):
        raise ValueError('positive prices, technology, capital, hours; 0<beta<1 required')
    return (p*A*beta*K**alpha/(hours*w))**(1/(1-beta))


def new_vacancies(target, previous, separation=.1, fill=.8, channel=.3):
    if target<0 or previous<0 or not 0<=separation<=1 or not 0<fill<=1 or not 0<=channel<=1:
        raise ValueError('invalid headcounts, separation, filling or channel share')
    return channel*max(target-(1-separation)*previous,0)/fill


def verify_model():
    """Illustrative parameter grid only. No parameter is estimated from vacancies."""
    max_error = 0.
    count = 0
    for beta in [.25,.5,.75]:
        for w in [.01,.04,.10]:
            params = dict(p=20., A=5., K=10., alpha=.3, beta=beta, hours=160.)
            n = desired_employment(w, **params)
            revenue_scale = params['p']*params['A']*params['K']**params['alpha']
            cost = params['hours']*w
            # Normalize by analytical target to avoid optimizer scale sensitivity.
            obj = lambda x: -(revenue_scale*(x*n)**beta-cost*x*n)
            solution = optimize.minimize_scalar(obj, bounds=(.05,3.),method='bounded')
            error = abs(solution.x-1.)
            max_error = max(max_error,error)
            assert solution.success and error<1e-4
            epsilon = 1e-5
            elasticity = (np.log(desired_employment(w*(1+epsilon),**params))-np.log(desired_employment(w*(1-epsilon),**params)))/(np.log(1+epsilon)-np.log(1-epsilon))
            assert np.isclose(elasticity,-1/(1-beta),rtol=1e-7)
            assert desired_employment(1.1*w,**params)<n
            count += 1
    assert new_vacancies(100,100,separation=.1,fill=.8,channel=.3) == .3*10/.8
    assert new_vacancies(80,100,separation=.1)==0
    assert new_vacancies(100,100,separation=0)==0
    assert new_vacancies(100,100,channel=0)==0
    assert new_vacancies(100,100,fill=.4)>new_vacancies(100,100,fill=.8)
    assert new_vacancies(100,100,separation=.05)<new_vacancies(100,100,separation=.1)
    for fn,args in [(desired_employment,dict(w=0)),(desired_employment,dict(w=1,beta=1)),
                    (new_vacancies,dict(target=100,previous=100,fill=0))]:
        try: fn(**args)
        except ValueError: pass
        else: raise AssertionError('boundary not rejected')
    return dict(grid_cases=count,max_relative_optimizer_error=max_error,
                checked=['FOC optimum','wage elasticity','zero recruitment corner','replacement case',
                         'separation/fill/channel sensitivity','invalid boundary rejection'],
                illustrative_only=True)


def configure_font():
    font = HERE/'assets'/'NotoSansJP-Regular.otf'
    if not font.exists():
        urllib.request.urlretrieve('https://raw.githubusercontent.com/notofonts/noto-cjk/main/Sans/SubsetOTF/JP/NotoSansJP-Regular.otf',font)
    font_manager.fontManager.addfont(font)
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),
                         'font.size':12,'axes.spines.top':False,'axes.spines.right':False,
                         'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white'})


def make_figures(trend, county, estimates, out):
    configure_font()
    fig,ax=plt.subplots(figsize=(10.6,4.1))
    for g,marker,style in [(EARLY,'o','-'),(LATE,'s','--')]:
        s=trend[g]
        ax.plot(range(1,12),s,marker=marker,ls=style,color='black',label=g)
    ax.axvspan(7.7,9.3,color='.93',label='公表・予期の影響に注意')
    ax.axvline(10.5,color='.5',lw=1)
    ax.axhline(0,color='.7',lw=.7)
    ax.set(xticks=range(1,12),xlabel='2025年（月）',ylabel='前年同月比（対数差×100）')
    ax.legend(frameon=False,ncol=3,fontsize=10,loc='lower left')
    fig.tight_layout(); fig.savefig(out/'trend.png',dpi=180); plt.close(fig)
    fig,ax=plt.subplots(figsize=(10.6,4.1))
    s=county.loc[county.baseline.eq('2025-01..09')].sort_values(['group','d'])
    for g,m in [(EARLY,'o'),(LATE,'s')]:
        v=s.loc[s.group.eq(g),'d'].to_numpy()
        x=0 if g==EARLY else 1
        jitter=np.linspace(-.13,.13,len(v))
        ax.scatter(x+jitter,v,marker=m,color='black',s=25,alpha=.65)
        ax.scatter(x,v.mean(),marker='_',s=1500,color='black',linewidths=2)
    ax.axhline(0,color='.6',lw=.8)
    ax.set(xticks=[0,1],xticklabels=[EARLY+'（20県）',LATE+'（14県）'],
           ylabel='県別変化 d（11月 − 基準期平均）',xlim=(-.5,1.5))
    fig.tight_layout(); fig.savefig(out/'county_changes.png',dpi=180); plt.close(fig)
    fig,ax=plt.subplots(figsize=(10.6,4.1))
    for i,r in estimates.iterrows():
        ax.errorbar(r.delta,i,xerr=[[r.delta-r.ci_low],[r.ci_high-r.delta]],fmt='o',color='black',capsize=5)
        ax.text(r.ci_high+.2,i,f'{r.delta:+.2f}  [{r.ci_low:.2f}, {r.ci_high:.2f}]',va='center',fontsize=11)
    ax.axvline(0,color='.4',ls='--')
    ax.set(yticks=range(len(estimates)),yticklabels=estimates.baseline,xlabel='早期 − 後期の県別変化の差（対数差×100）、95% Welch区間')
    ax.set_xlim(min(estimates.ci_low)-1,max(estimates.ci_high)+9)
    ax.invert_yaxis()
    fig.tight_layout(); fig.savefig(out/'sensitivity.png',dpi=180); plt.close(fig)


def run(output=HERE/'results', figures=True):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    np.random.seed(SEED)  # Analysis is deterministic; no simulated empirical observations.
    hashes_before = {f:sha256(RAW/f) for f in FILES}
    sheets = pd.ExcelFile(RAW/FILES[0]).sheet_names
    assert len(sheets)==6
    wide=[load_t12(RAW/FILES[0],s) for s in sheets]
    for total,nonpart,part in [(wide[0],wide[1],wide[2]),(wide[3],wide[4],wide[5])]:
        assert total.index.equals(part.index) and total.columns.equals(part.columns)
        assert np.array_equal(total.values,nonpart.values+part.values)
    part=wide[2].drop(columns='全国')
    policy,columns=load_policy(RAW/FILES[1],part.columns.tolist())
    yoy=100*(np.log(part)-np.log(part.shift(12)))
    # Independent scalar check (not the shifted array used above).
    assert np.isclose(yoy.loc['2025-11','東京都'],100*np.log(part.loc['2025-11','東京都']/part.loc['2024-11','東京都']))
    panel=(part.loc['2023-01':'2026-08'].reset_index().melt(id_vars='month',var_name='pref',value_name='openings'))
    ys=yoy.stack().rename('yoy').rename_axis(['month','pref']).reset_index()
    panel=panel.merge(ys,on=['month','pref'],validate='one_to_one').merge(policy.reset_index(),on='pref',validate='many_to_one')
    assert len(panel)==2068 and panel.yoy.notna().all()
    eligible=policy.loc[policy.group.isin([EARLY,LATE])]
    estimates,rows=[],[]
    for label,start,end in [('2025-01..09','2025-01','2025-09'),('2025-01..07','2025-01','2025-07'),('2025-04..09','2025-04','2025-09')]:
        d=eligible.copy()
        d['baseline']=label
        d['pre_yoy']=yoy.loc[start:end,d.index].mean(axis=0)
        d['nov_yoy']=yoy.loc['2025-11',d.index]
        d['d']=d.nov_yoy-d.pre_yoy
        a,b=d.loc[d.group.eq(EARLY)],d.loc[d.group.eq(LATE)]
        result=welch_difference(a.d,b.d)
        result.update(baseline=label,pre_early=float(a.pre_yoy.mean()),pre_late=float(b.pre_yoy.mean()),
                      nov_early=float(a.nov_yoy.mean()),nov_late=float(b.nov_yoy.mean()),
                      pre_gap=float(a.pre_yoy.mean()-b.pre_yoy.mean()),nov_gap=float(a.nov_yoy.mean()-b.nov_yoy.mean()))
        assert np.isclose(result['delta'],result['nov_gap']-result['pre_gap'])
        estimates.append(result); rows.append(d.reset_index())
    estimates=pd.DataFrame(estimates)
    county=pd.concat(rows,ignore_index=True)
    trend=yoy.loc['2025-01':'2025-11'].T.join(policy.group).groupby('group').mean(numeric_only=True).T
    trend['gap_early_late']=trend[EARLY]-trend[LATE]
    policy.to_csv(output/'policy.csv',encoding='utf-8-sig')
    panel.to_csv(output/'panel.csv',index=False,encoding='utf-8-sig')
    county.to_csv(output/'county_changes.csv',index=False,encoding='utf-8-sig')
    estimates.to_csv(output/'estimates.csv',index=False,encoding='utf-8-sig')
    trend.to_csv(output/'monthly_means.csv',encoding='utf-8-sig')
    summary=policy.groupby('group').agg(n=('mw_2025','size'),mw_2024=('mw_2024','mean'),mw_2025=('mw_2025','mean'),raise_pct=('raise_pct','mean'),raise_yen=('raise_yen','mean'))
    summary.to_csv(output/'group_summary.csv',encoding='utf-8-sig')
    model=verify_model()
    hashes_after={f:sha256(RAW/f) for f in FILES}
    assert hashes_before==hashes_after
    validation={'seed':SEED,'all_checks_passed':True,'raw_sha256':hashes_before,'raw_files_unchanged':True,
                'workbook_year_headers':columns,'raw_first_month':str(part.index.min()),'raw_last_month':str(part.index.max()),
                'raw_months':len(part),'prefectures':47,'sheets_validated':sheets,
                'monthly_continuity':True,'national_equal_sum_all_six_sheets':True,
                'part_plus_nonpart_equal_total_general_and_regular':True,'panel_observations':len(panel),
                'group_counts':policy.group.value_counts().to_dict(),'primary_policy_units':34,
                'comparison_month':'2025-11','welch_checked_against_scipy':True,'mean_difference_checked_against_OLS':True,
                'scalar_log_yoy_checked':True,'model':model,
                'limitations':['Descriptive contrast, not a causal estimate','Prefecture independence is an inference assumption',
                               'Year-on-year changes subtract prior-year policy effects','Receipt location is not work location',
                               'January-July baseline need not be free of anticipation'],
                'software':{'numpy':np.__version__,'pandas':pd.__version__,'scipy':__import__('scipy').__version__,
                            'matplotlib':matplotlib.__version__},'estimates':estimates.to_dict(orient='records')}
    (output/'verification.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n')
    if figures: make_figures(trend,county,estimates,output)
    print(estimates[['baseline','pre_gap','nov_gap','delta','ci_low','ci_high','p_one_sided_negative','p_two_sided']].to_string(index=False,float_format=lambda x:f'{x:.6f}'))
    print('PASS: six-sheet data checks; year headers; 47 prefectures; unchanged raw hashes; Welch/OLS; model grid.')
    return dict(panel=panel,policy=policy,county=county,estimates=estimates,trend=trend,validation=validation)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=HERE/'results')
    parser.add_argument('--no-figures',action='store_true')
    args=parser.parse_args()
    run(args.output,not args.no_figures)
