"""Teaching-only charts and speaker notes; never rewrite statistical outputs."""
from pathlib import Path
import hashlib
import json
import re
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
import analysis

H=Path(__file__).resolve().parent

def main():
    preserved=json.loads((H/'preserved-analysis-sha256.json').read_text())
    assert all(hashlib.sha256((H/name).read_bytes()).hexdigest()==sha for name,sha in preserved.items())
    summary=json.loads((H/'results/summary.json').read_text())
    # Exercise the real existing solver, check against saved assumed results.
    p=summary['assumed_parameters']
    solved=[]
    for rec in summary['model_scenarios']:
        v,L,_,_=analysis.solve_model(rec['w1'],rec['expected_w2'],**p)
        np.testing.assert_allclose(v,[rec['v1'],rec['v2']],rtol=0,atol=1e-12)
        np.testing.assert_allclose(L,[rec['L1'],rec['L2']],rtol=0,atol=1e-12)
        solved.append({'scenario':rec['scenario'],'v':v.tolist(),'L':L.tolist()})
    font=H/'assets/NotoSansJP-Regular.otf'
    font_manager.fontManager.addfont(font)
    plt.rcParams.update({'font.family':font_manager.FontProperties(fname=font).get_name(),
        'font.size':13,'figure.facecolor':'white','axes.facecolor':'white',
        'axes.spines.top':False,'axes.spines.right':False})
    s=summary['primary']
    fig,ax=plt.subplots(figsize=(10.5,2.2))
    ax.axvline(0,color='#777777',ls='--',lw=1)
    ax.errorbar(s['estimate'],0,xerr=[[s['estimate']-s['ci_low']],[s['ci_high']-s['estimate']]],fmt='o',color='black',capsize=9,ms=8,lw=2)
    for x,label,va in [(s['ci_low'],'−7.93','bottom'),(s['estimate'],'−1.56','top'),(s['ci_high'],'4.82','bottom')]:
        ax.text(x,.1 if va=='bottom' else -.1,label,ha='center',va=va,fontsize=16)
    ax.set(xlim=(-10,7),ylim=(-.45,.5),yticks=[],xlabel='早群−晩群の変化（対数差×100）')
    ax.spines['left'].set_visible(False)
    fig.tight_layout(); fig.savefig(H/'figures/teaching_interval.png',dpi=180); plt.close(fig)
    path=pd.read_csv(H/'results/monthly_fixed_group_path.csv')
    x=pd.to_datetime(path.month)
    fig,ax=plt.subplots(figsize=(10.5,3.0))
    ax.axvspan(pd.Timestamp('2025-12-01'),x.max(),color='#eeeeee')
    ax.fill_between(x,path.ci_low,path.ci_high,color='#c9c9c9',alpha=.75)
    ax.plot(x,path.estimate,'o-',color='black',ms=3,lw=1.3)
    ax.axhline(0,color='#666666',lw=.8)
    ax.axvline(pd.Timestamp('2025-11-01'),color='#444444',ls=':',lw=1.3)
    ax.set_ylabel('基準期からの早晩差の変化\n（対数差×100）')
    ticks=pd.to_datetime(['2025-01-01','2025-04-01','2025-07-01','2025-11-01','2026-04-01','2026-08-01'])
    ax.set_xticks(ticks,['2025年1月','4月','7月','11月','2026年4月','8月'])
    ax.text(.98,.97,'12月以降は記述のみ',transform=ax.transAxes,ha='right',va='top',fontsize=12)
    ax.grid(axis='y',alpha=.15)
    fig.tight_layout(); fig.savefig(H/'figures/teaching_path.png',dpi=180); plt.close(fig)
    # Separate the genuine Marp notes from invisible class directives.
    text=(H/'slides.md').read_text()
    pages=re.split(r'^---\s*$',text,flags=re.M)[2:]
    notes=[]
    for i,page in enumerate(pages,1):
        match=re.search(r'^#{1,2} (.+)$',page,re.M)
        assert match is not None,(i,'missing title')
        title=match.group(1)
        comments=[c.strip() for c in re.findall(r'<!--(.*?)-->',page,re.S) if not c.strip().startswith('_')]
        assert len(comments)==1 and len(comments[0])>=60,(i,comments)
        notes.append(f'## {i}頁｜{title}\n\n{comments[0]}\n')
    assert len(notes)==20,len(notes)
    (H/'speaker_notes.md').write_text('# 発表者ノート（20頁）\n\nslides.mdの各頁の非表示ノートを抽出。本文の代わりではなく、説明とつなぎの補助。所要時間は未計測。\n\n'+'\n'.join(notes))
    todo={
        '1_data_comparability':[3,4,15,17,18],
        '2_prior_work_increment':[2,8],
        '3_micro_model':[5,6,7,8,9,10,11,12,13],
        '4_hypothesis_test_mapping':[11,12,14,15,16],
        '5_results_and_model_reality':[13,15,16,17,18],
        '6_conclusion_implications_limits':[18,19],
    }
    report={'pages':20,'speaker_notes':len(notes),'todo_page_map':todo,'assumed_scenarios_recomputed':solved,
        'preserved_hashes_match':all(hashlib.sha256((H/name).read_bytes()).hexdigest()==sha for name,sha in preserved.items())}
    (H/'teaching-verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
