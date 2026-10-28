"""課題3・4: part求人の透明な県等重み差分。rawは読み込みのみ。"""
from pathlib import Path
import hashlib
import json
import unicodedata
import numpy as np
import pandas as pd
from scipy import stats

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RAW = ROOT / 'data' / 'raw'
SEED = 20261104

def load_data():
    """年見出し・全月・全国計・内訳を検証し、partの同比を返す。"""
    f = RAW / 'estat_shokugyo_t12_shinki_kyujin.xlsx'
    with pd.ExcelFile(f) as workbook:
        sheets = workbook.sheet_names
    assert '一般パート' in sheets[2]
    frames = []
    for name in sheets[:3]:
        x = pd.read_excel(f, sheet_name=name, header=None)
        body = x[x[2].notna() & x[0].astype(str).str.match(r'\d{4}年')].copy()
        years = body[0].str.extract(r'(\d{4})')[0].astype(int)
        months = body[2].map(lambda z: unicodedata.normalize('NFKC',str(z))).str.extract(r'(\d+)')[0].astype(int)
        wide = body.iloc[:,3:51].astype(float)
        wide.columns = x.iloc[1,3:51].tolist()
        wide.index = pd.PeriodIndex.from_fields(year=years,month=months,freq='M')
        frames.append(wide)
    total, nonpart, part = frames
    prefs = part.columns.drop('全国').tolist()
    checks = {
        '47_prefectures': len(prefs)==47 and len(set(prefs))==47,
        'monthly_continuity': all(w.index.equals(pd.period_range(w.index.min(),w.index.max(),freq='M')) for w in frames),
        'unique_months': all(w.index.is_unique for w in frames),
        'positive_no_missing': all(w.notna().all().all() and (w>0).all().all() for w in frames),
        'national_equals_pref_sum': all(np.array_equal(w['全国'].to_numpy(),w[prefs].sum(axis=1).to_numpy()) for w in frames),
        'part_plus_nonpart_equals_total': np.array_equal((part+nonpart).to_numpy(), total.to_numpy()),
        'same_months_all_sheets': total.index.equals(part.index) and nonpart.index.equals(part.index),
    }
    x = pd.read_excel(RAW/'mhlw_saitei_chingin_kaitei.xlsx',header=None)
    def names(s):
        z=''.join(str(s).split())
        return next(t for t in [z,z+'県',z+'府',z+'都'] if t in prefs)
    policy = pd.DataFrame({'pref':x.iloc[2:49,0].map(names).to_numpy()})
    columns = {}
    for year,label in [(2023,'令和５年度'),(2024,'令和６年度'),(2025,'令和７年度')]:
        col = x.columns[x.iloc[0]==label]
        assert len(col)==1
        j=int(col[0]); columns[str(year)]={'label':label,'zero_based_column':j}
        policy[f'mw_{year}']=x.iloc[2:49,j].astype(int).to_numpy()
        policy[f'effective_{year}']=pd.to_datetime(x.iloc[2:49,j+1]).to_numpy()
    checks['policy_exact_pref_join'] = policy.pref.tolist()==prefs
    checks['policy_2025_year'] = policy.effective_2025.between('2025-10-01','2026-03-31').all()
    policy['raise_pct']=100*(policy.mw_2025/policy.mw_2024-1)
    m=policy.effective_2025.dt.to_period('M')
    policy['group']=np.select([m==pd.Period('2025-10'),m==pd.Period('2025-11')],['early','excluded'],default='late')
    policy['early']=(policy.group=='early').astype(int)
    checks['group_counts']=policy.group.value_counts().to_dict()=={'early':20,'late':14,'excluded':13}
    checks={k:bool(v) for k,v in checks.items()}
    assert all(checks.values()),checks
    yoy=100*(np.log(part[prefs])-np.log(part[prefs].shift(12)))
    yoy.index.name='month'
    panel=yoy.reset_index().melt(id_vars='month',var_name='pref',value_name='y')
    panel=panel[panel.month.between(pd.Period('2023-01'),pd.Period('2026-08'))].copy()
    checks['analysis_47_by_44_no_missing']=bool(len(panel)==2068 and panel.y.notna().all())
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in RAW.glob('*.xlsx')}
    audit={'checks':checks,'raw_sha256':hashes,'raw_months':len(part),'raw_start':str(part.index.min()),'raw_end':str(part.index.max()),'analysis_observations':len(panel),'policy_columns':columns}
    return panel,policy,audit

def contrast(panel,policy,month='2025-11',pre_end=9):
    """県内基準差→早群平均－晩群平均。Welch区間、両側/片側p。"""
    pre=panel[(panel.month.dt.year==2025)&(panel.month.dt.month<=pre_end)].groupby('pref').y.mean()
    post=panel[panel.month==pd.Period(month)].set_index('pref').y
    d=policy[policy.group!='excluded'].set_index('pref').copy()
    d['pre']=pre; d['post']=post; d['d']=post-pre
    assert d[['pre','post','d']].notna().all().all()
    e=d.loc[d.early==1,'d']; l=d.loc[d.early==0,'d']
    est=e.mean()-l.mean(); v1=e.var(ddof=1)/len(e); v0=l.var(ddof=1)/len(l)
    se=np.sqrt(v1+v0); df=(v1+v0)**2/(v1**2/(len(e)-1)+v0**2/(len(l)-1))
    t=est/se; q=stats.t.ppf(.975,df)
    result={'month':month,'pre_end':pre_end,'n_early':len(e),'n_late':len(l),'early_pre':d.loc[d.early==1,'pre'].mean(),'late_pre':d.loc[d.early==0,'pre'].mean(),'early_post':d.loc[d.early==1,'post'].mean(),'late_post':d.loc[d.early==0,'post'].mean(),'early_d':e.mean(),'late_d':l.mean(),'estimate':est,'se':se,'df':df,'ci_low':est-q*se,'ci_high':est+q*se,'p_two_sided':2*stats.t.sf(abs(t),df),'p_negative':stats.t.cdf(t,df)}
    return result,d

def solve_model(w1,w2,a=10.,b=1.,q=.8,r=.8,beta=.95,kappa=2.,c=.2,L0=3.):
    """二期の名額v>=0を同時選択。4つのactive setを完全列挙。"""
    assert b>0 and 0<q<=1 and 0<=r<=1 and 0<beta<=1 and kappa>=0 and c>=0 and L0>=0
    B=np.array([[q,0.],[r*q,q]])
    base=np.array([r*L0,r*r*L0]); weights=np.array([1.,beta])
    H=b*B.T@np.diag(weights)@B+kappa*np.diag(weights)
    g=B.T@(weights*(a-np.array([w1,w2])-b*base))-c*weights
    candidates=[]
    for free in [[],[0],[1],[0,1]]:
        v=np.zeros(2)
        if free: v[free]=np.linalg.solve(H[np.ix_(free,free)],g[free])
        if np.all(v>=-1e-10):
            v=np.maximum(v,0.)
            candidates.append((.5*v@H@v-g@v,v))
    v=min(candidates,key=lambda z:z[0])[1]
    return v,base+B@v,H,g

def wage_derivatives(a=10.,b=1.,q=.8,r=.8,beta=.95,kappa=2.,c=.2,L0=3.):
    """内点のみ。列はw1,w2、行はv1,v2。"""
    H=solve_model(4.,4.,a,b,q,r,beta,kappa,c,L0)[2]
    return -np.linalg.solve(H,np.array([[q,beta*r*q],[0.,beta*q]]))

def timing_table(policy):
    rows=[]
    for month in pd.period_range('2025-07','2026-08',freq='M'):
        for group in ['early','late']:
            dates=policy.loc[policy.group==group,'effective_2025']
            full=(dates<=month.start_time).sum()
            untreated=(dates>month.end_time).sum()
            row=dict(month=str(month),group=group,full=int(full),partial=int(len(dates)-full-untreated),untreated=int(untreated))
            for lag in [0,1,2,3,4]:
                row[f'untreated_through_t_plus_{lag}']=int((dates>(month+lag).end_time).sum())
            rows.append(row)
    return pd.DataFrame(rows)

def validate_model():
    """仮定パラメータ200組：KKT、独立数値最適化、内点の中心差分。"""
    from scipy.optimize import minimize
    rng=np.random.default_rng(SEED)
    err=[]; opt_err=[]; kkt=[]; interior=0
    for _ in range(200):
        p=dict(a=rng.uniform(7,14),b=rng.uniform(.5,2),q=rng.uniform(.4,1),r=rng.uniform(0,1),beta=rng.uniform(.6,1),kappa=rng.uniform(0,4),c=rng.uniform(0,.4),L0=rng.uniform(0,6))
        w=rng.uniform(2,10,2)
        v,L,H,g=solve_model(*w,**p)
        grad=H@v-g
        kkt.append(bool(np.all(grad[v<1e-9]>=-1e-8) and np.max(abs(grad[v>1e-9]),initial=0)<1e-8))
        # Independently evaluate the original profit, not H/g.
        def loss(z):
            l1=p['r']*p['L0']+p['q']*z[0]
            l2=p['r']*l1+p['q']*z[1]
            return -sum(weight*(p['a']*l-.5*p['b']*l*l-wage*l-p['c']*vv-.5*p['kappa']*vv*vv) for l,vv,wage,weight in zip([l1,l2],z,w,[1,p['beta']]))
        numerical=minimize(loss,[1,1],bounds=[(0,None)]*2,method='L-BFGS-B',options={'ftol':1e-14,'gtol':1e-8,'maxiter':1000})
        opt_err.append(abs(loss(v)-numerical.fun))
        if min(v)>1e-3:
            interior+=1; J=wage_derivatives(**p); eps=1e-5
            for j in range(2):
                plus=w.copy(); minus=w.copy(); plus[j]+=eps; minus[j]-=eps
                fd=(solve_model(*plus,**p)[0]-solve_model(*minus,**p)[0])/(2*eps)
                err.append(float(max(abs(fd-J[:,j]))))
                assert J[0,j]<0
            assert J[1,0]>=0 and J[1,1]<0
    assert all(kkt) and max(err)<1e-7 and max(opt_err)<1e-7
    # Zero hiring cost curvature or no persistence: no interior anticipation in v1.
    assert abs(wage_derivatives(kappa=0)[0,1])<1e-12
    assert abs(wage_derivatives(r=0)[0,1])<1e-12
    assert np.all(solve_model(100,100)[0]==0)
    return dict(seed=SEED,draws=200,interior_draws=interior,all_kkt_pass=all(kkt),max_derivative_error=max(err),max_optimizer_objective_error=max(opt_err),zero_kappa_and_zero_persistence_checked=True,zero_hiring_corner_checked=True)

def run_all():
    import statsmodels.api as sm
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    import urllib.request
    import re
    import pymupdf
    R=HERE/'results'; F=HERE/'figures'; A=HERE/'assets'
    for p in [R,F,A]: p.mkdir(exist_ok=True)
    font=A/'NotoSansJP-Regular.otf'
    if not font.exists():
        urllib.request.urlretrieve('https://github.com/notofonts/noto-cjk/raw/main/Sans/SubsetOTF/JP/NotoSansJP-Regular.otf',font)
    font_manager.fontManager.addfont(font)
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),'font.size':12,'axes.spines.top':False,'axes.spines.right':False,'figure.facecolor':'white','axes.facecolor':'white','axes.grid':True,'grid.alpha':.2})
    panel,policy,audit=load_data()
    # Second official source: 2024 final PDF, all 47 date and level pairs.
    pdf=HERE/'evidence'/'MW2024.pdf'
    text=pymupdf.open(pdf)[0].get_text()
    matched=0
    for row in policy.itertuples():
        base=row.pref if row.pref=='北海道' else row.pref[:-1]
        pattern=r'\s*'.join(base)+r'\s*([\d,]+)\s*令和6\s*年(\d+)\s*月(\d+)\s*日'
        found=re.search(pattern,text)
        assert found,(row.pref,pattern)
        amount,month,day=found.groups()
        assert int(amount.replace(',',''))==row.mw_2024
        assert row.effective_2024==pd.Timestamp(2024,int(month),int(day))
        matched+=1
    audit['checks']['official_2024_pdf_47_matches']=matched==47
    table=[]
    for pre_end in [9,7]:
        result,d=contrast(panel,policy,'2025-11',pre_end)
        table.append(result)
        d.to_csv(R/f'prefecture_d_pre{pre_end}.csv',encoding='utf-8-sig')
    primary=table[0]
    # Basic OLS only: unadjusted reproduces mean difference; HC3 interval auxiliary.
    result,d=contrast(panel,policy)
    ols=sm.OLS(d.d,sm.add_constant(d[['early']])).fit(cov_type='HC3',use_t=True)
    assert abs(ols.params['early']-primary['estimate'])<1e-12
    controlled=sm.OLS(d.d,sm.add_constant(d[['early','raise_pct']])).fit(cov_type='HC3',use_t=True)
    controls=dict(estimate=float(controlled.params['early']),ci_low=float(controlled.conf_int().loc['early',0]),ci_high=float(controlled.conf_int().loc['early',1]),p=float(controlled.pvalues['early']),note='auxiliary association only; wage-increase control does not solve endogenous timing or overlap')
    overlap=policy[policy.group!='excluded'].groupby('group').raise_pct.agg(['min','max','mean'])
    overlap.to_csv(R/'wage_increment_overlap.csv')
    pd.DataFrame(table).to_csv(R/'main_contrasts.csv',index=False)
    timing=timing_table(policy); timing.to_csv(R/'timing_support.csv',index=False)
    policy.to_csv(R/'policy_2023_2025.csv',index=False,encoding='utf-8-sig')
    panel.assign(month=panel.month.astype(str)).to_csv(R/'part_yoy_panel.csv',index=False,encoding='utf-8-sig')
    # Fixed original groups throughout, not rolling untreated controls.
    paths=pd.DataFrame([contrast(panel,policy,str(m),9)[0] for m in pd.period_range('2025-01','2026-08',freq='M')])
    paths['interpretation']='descriptive fixed-cohort gap; not a causal event study'
    paths.to_csv(R/'monthly_fixed_group_path.csv',index=False)
    # Explicit non-policy placebo diagnostic: prior annual reform remains present.
    placebo=panel[panel.month.dt.year==2024].copy()
    placebo['month']=placebo.month+12
    old=contrast(placebo,policy,'2025-11',9)[0]
    old['month']='2024-11'; old['baseline_year']=2024
    old['note']='2024 same-cohort calendar diagnostic; 2024 policy is present, not no-policy placebo'
    # Later gap minus November gap: a path shape check, not a mechanism estimate.
    later=panel[panel.month.between(pd.Period('2026-04'),pd.Period('2026-06'))].groupby('pref').y.mean()
    nov=panel[panel.month==pd.Period('2025-11')].set_index('pref').y
    shaped=d.copy(); shaped['d']=later-nov
    e=shaped.loc[shaped.early==1,'d']; l=shaped.loc[shaped.early==0,'d']
    tt=stats.ttest_ind(e,l,equal_var=False); est=float(e.mean()-l.mean())
    se=np.sqrt(e.var()/len(e)+l.var()/len(l)); ci=stats.t.ppf(.975,tt.df)*se
    shape=dict(contrast='(early-late Apr-Jun2026 mean y) minus (early-late Nov2025 y)',estimate=est,ci_low=float(est-ci),ci_high=float(est+ci),p_two_sided=float(tt.pvalue),not_causal=True)
    # Assumed parameters, no calibration or estimation.
    params=dict(a=10.,b=1.,q=.8,r=.8,beta=.95,kappa=2.,c=.2,L0=3.)
    sim=[]
    for label,w1,w2 in [('no_hike',4.,4.),('late_anticipated',4.,4.5),('early_anticipated',4.5,4.5),('larger_future_hike',4.,5.)]:
        v,L,H,g=solve_model(w1,w2,**params)
        sim.append(dict(scenario=label,w1=w1,expected_w2=w2,v1=v[0],v2=v[1],L1=L[0],L2=L[1],parameters='assumed_not_estimated'))
    pd.DataFrame(sim).to_csv(R/'model_assumed_scenarios.csv',index=False)
    sensitivity=[]
    for k in [0,.5,2.,5.]:
        for r in [0.,.5,.8,1.]:
            for beta in [.8,.95,1.]:
                p={**params,'kappa':k,'r':r,'beta':beta}; J=wage_derivatives(**p)
                sensitivity.append(dict(kappa=k,r=r,beta=beta,dv1_dw1=J[0,0],dv1_dEw2=J[0,1],dv2_dw1=J[1,0],dv2_dEw2=J[1,1]))
    pd.DataFrame(sensitivity).to_csv(R/'model_derivative_grid.csv',index=False)
    model=validate_model()
    # Charts with common units and fully explicit descriptive time support.
    fig,ax=plt.subplots(figsize=(9.5,3.5))
    trend=panel.merge(policy[['pref','group']],on='pref').query('group!="excluded"').groupby(['month','group']).y.mean().unstack()
    trend=trend.loc['2025-01':'2026-08']
    for g,c,lbl in [('early','#111111','10月発効20県'),('late','#666666','12月以降14県（固定群）')]:
        ax.plot(trend.index.to_timestamp(),trend[g],label=lbl,color=c,linestyle='-' if g=='early' else '--',marker='o',ms=3)
    ax.axvspan(pd.Timestamp('2025-11-01'),pd.Timestamp('2025-11-30'),color='#dddddd',alpha=.6)
    ax.set_ylabel('対数差×100'); ax.legend(frameon=False,ncol=2); ax.set_title('実データ：パート新規求人数の前年同月比',loc='left')
    fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(F/'actual_yoy.png',dpi=170); plt.close(fig)
    fig,ax=plt.subplots(figsize=(9.5,3.4))
    xx=pd.to_datetime(paths.month); ax.plot(xx,paths.estimate,color='black',marker='o',ms=3)
    ax.fill_between(xx,paths.ci_low,paths.ci_high,color='#dddddd',label='各月の95%区間（多重比較未補正）')
    ax.axhline(0,color='black',lw=.7); ax.axvline(pd.Timestamp('2025-11-01'),color='gray',ls=':')
    ax.axvspan(pd.Timestamp('2025-12-01'),xx.max(),color='#eeeeee',alpha=.6)
    ax.set_ylabel('早群−晩群の基準差'); ax.set_title('実データ：固定2群の差の推移（12月以降は記述のみ）',loc='left'); ax.legend(frameon=False,fontsize=10)
    fig.autofmt_xdate(); fig.tight_layout(); fig.savefig(F/'actual_gap_path.png',dpi=170); plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9.5,3.6))
    for rec,ls in zip(sim[:3],[':','--','-']):
        lbl={'no_hike':'改定なし','late_anticipated':'晩群：今期低・次期高','early_anticipated':'早群：両期高'}[rec['scenario']]
        axes[0].plot([1,2],[rec['v1'],rec['v2']],color='black',ls=ls,marker='o',label=lbl)
    axes[0].set_xticks([1,2],['今期','次期']); axes[0].set_ylabel('募集枠（仮想単位）'); axes[0].legend(fontsize=9,frameon=False)
    for k in [0.,.5,2.,5.]:
        ws=np.linspace(4,6,30); vv=[solve_model(4,w,kappa=k)[0][0] for w in ws]
        axes[1].plot(ws,vv,label=f'κ={k:g}')
    axes[1].set_xlabel('予想する次期賃金（仮想単位）'); axes[1].set_ylabel('今期の募集枠'); axes[1].legend(fontsize=9,frameon=False)
    fig.suptitle('数値例：全パラメータは仮定値（推定・較正ではない）',fontsize=13)
    fig.tight_layout(); fig.savefig(F/'model_simulation.png',dpi=170); plt.close(fig)
    output={'data':audit,'primary':primary,'sensitivity_pre7':table[1],'controlled_ols_hc3':controls,'prior_year_diagnostic':old,'later_shape_diagnostic':shape,'model':model,'assumed_parameters':params,'model_scenarios':sim,'inference_scope':'Prefecture-independent sampling approximation, not random assignment; no mechanism or model parameters identified.'}
    (R/'summary.json').write_text(json.dumps(output,ensure_ascii=False,indent=2))
    (HERE/'verification.json').write_text(json.dumps({'analysis_run':True,**output},ensure_ascii=False,indent=2))
    return output

if __name__=='__main__':
    print(json.dumps(run_all(),ensure_ascii=False,indent=2))
