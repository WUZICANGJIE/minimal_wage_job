"""Optional next-week statistical replication; does not check slide layout."""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
import nbformat
import numpy as np
import pandas as pd
import analysis

BASE=Path(__file__).resolve().parent
report={'checks':[], 'passed':False}

def check(name, ok, detail: object=''):
    report['checks'].append({'name':name,'ok':bool(ok),'detail':str(detail)})
    print(('PASS ' if ok else 'FAIL ')+name+(f' :: {detail}' if detail else ''))

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

protected=json.loads((BASE/'evidence/protected_hashes_20slides.json').read_text())
check('analysis.py and all original CSV hashes unchanged',
      all(digest(BASE/p)==h for p,h in protected.items()),len(protected))
# Tests use pure functions, never analysis.run().
proc=subprocess.run([sys.executable,'-m','unittest','discover','-s','tests','-v'],
                    cwd=BASE,capture_output=True,text=True)
(BASE/'evidence/test_final.log').write_text(proc.stdout+proc.stderr)
check('unit tests',proc.returncode==0,proc.stderr.strip().splitlines()[-1])
# Recompute from raw in memory, compare EVERY stored contrast and group mean.
v=json.loads((BASE/'verification.json').read_text())
for filename,h in v['input_sha256'].items():
    check('raw hash '+filename,digest(analysis.RAW/filename)==h)
frames,audit=analysis.load_vacancies(analysis.RAW/'estat_shokugyo_t12_shinki_kyujin.xlsx')
policy,_=analysis.load_policy(analysis.RAW/'mhlw_saitei_chingin_kaitei.xlsx',
                             frames['part'].drop(columns='全国').columns.tolist())
levels,metrics,share=analysis.prepare_metrics(frames)
check('47 prefectures x 164 months, no gaps, sums consistent',
      audit['part']['months']==164 and audit['part_plus_nonpart_max_abs_residual']==0)
check('policy 20/13/14',policy.group.value_counts().to_dict()=={'early':20,'late':14,'excluded':13})
stored=pd.read_csv(BASE/'results/contrasts.csv'); storedmeans=pd.read_csv(BASE/'results/group_means.csv')
for end in ['2025-09','2025-07']:
    got,_,means=analysis.estimate(metrics,policy,end)
    expected=stored.query('baseline_end==@end').set_index('metric').loc[got.metric]
    numeric=got.select_dtypes('number').columns
    check('all contrasts/intervals/p values '+end,
          np.allclose(got[numeric],expected[numeric],atol=1e-10,rtol=0))
    exp=storedmeans.query('baseline_end==@end').set_index(['metric','group']).loc[list(zip(means.metric,means.group))]
    check('all group means '+end,np.allclose(means[['baseline','november','change']],exp[['baseline','november','change']],atol=1e-10,rtol=0))
# Recompute the two teaching illustration rows without saving over results.
illustration=pd.read_csv(BASE/'results/model_illustration_NOT_ESTIMATED.csv')
for beta in [.2,.7]:
    b=analysis.ces_choice(1,1,sigma=2,beta=beta,a=.5)
    s=analysis.ces_choice(1.1,1.02,sigma=2,beta=beta,a=.5)
    row=illustration.query('sigma==2 and beta==@beta and a==.5').iloc[0]
    vals=[100*np.log(s[k]/b[k]) for k in ['P','N','total']]
    check('teaching example matches existing model '+str(beta),
          np.allclose(vals,row[['P_change_log100','N_change_log100','total_change_log100']].astype(float),atol=1e-10))
nb=nbformat.read(BASE/'analysis.ipynb',as_version=4)
cells=[c for c in nb.cells if c.cell_type=='code']
check('existing executed notebook has outputs and no errors',
      all(c.get('outputs') for c in cells) and not any(o.output_type=='error' for c in cells for o in c.get('outputs',[])))

report['passed']=all(c['ok'] for c in report['checks'])
(BASE/'verification_analysis_log.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('ALL PASS' if report['passed'] else 'SOME CHECKS FAILED')
sys.exit(0 if report['passed'] else 1)
