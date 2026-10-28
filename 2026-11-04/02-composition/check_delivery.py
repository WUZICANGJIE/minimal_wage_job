"""Read-only statistical replication + 20-page rendering checks.
Writes verification/evidence only; does not invoke analysis.run or rewrite CSVs.
"""
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path
import nbformat
import numpy as np
import pandas as pd
import pymupdf
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
import analysis

BASE=Path(__file__).resolve().parent
report={'checks':[], 'passed':False, 'todo_pages':{
    '1_data_comparison':[3,4,13,14,15,18], '2_literature_increment':[2],
    '3_micro_model':[5,6,7,8,9,10,11], '4_hypothesis_test':[12,13,14],
    '5_results_theory_reality':[15,16,17,18], '6_conclusion_implications_limits':[19]}}

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
source=(BASE/'slides.md').read_text(); body=source.split('---',2)[2]
pages=re.split(r'^---\s*$',body,flags=re.M)
check('Markdown exactly 20 pages',len(pages)==20,len(pages))
check('one Japanese speaker note on every page',all(len(re.findall(r'<!-- notes: .*? -->',p,re.S))==1 for p in pages))
check('speaker_notes.md has 20 page headings',len(re.findall(r'^## \d+頁', (BASE/'speaker_notes.md').read_text(),re.M))==20)
check('no unsupported aligned[t] or Japanese math subscripts',r'\begin{aligned}[t]' not in source and not re.search(r'_\{[ぁ-龥]',source))
check('no Chinese terms in visible body', all(t not in source for t in ['同比','创新','首創']))
doc=pymupdf.open(BASE/'slides.pdf')
check('PDF exactly 20 pages',len(doc)==20,len(doc))
text='\n'.join(p.get_text() for p in doc)
for needle in ['−1.56','−2.23','パート以外','無処理の対照','Acemoglu','規模縮小も排除できない']:
    check('PDF contains '+needle,needle in text)
check('no PDF missing-glyph markers','\ufffd' not in text and '\u25a1' not in text)
for name in ['slides.md','slides.pdf','slides.html','speaker_notes.md','README.md','methods.md','sources.md']:
    check(name+' present',(BASE/name).is_file())
# Rendered HTML: each section, source collision, images, font, display-math size.
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--allow-file-access-from-files'])
    page=browser.new_page(viewport={'width':1440,'height':900})
    page.goto((BASE/'slides.html').as_uri()); page.evaluate('document.fonts.ready'); page.wait_for_timeout(500)
    geometry=page.evaluate('''() => Array.from(document.querySelectorAll('section')).map((s,i)=>{
      const r=s.getBoundingClientRect(), scale=r.width/1280;
      const footer=s.querySelector('.source'), f=footer?.getBoundingClientRect();
      const nodes=[...s.children].filter(e=>!e.classList.contains('source')&&e.tagName!=='SCRIPT');
      const bottom=Math.max(...nodes.map(e=>e.getBoundingClientRect().bottom));
      const beyond=[...s.querySelectorAll('.katex-display, h1, table, img')].filter(e=>{
        const b=e.getBoundingClientRect(); return b.left<r.left-1||b.right>r.right+1||b.bottom>r.bottom-30*scale;
      }).map(e=>e.tagName+':'+e.textContent.slice(0,35));
      return {page:i+1,scrollHeight:s.scrollHeight,clientHeight:s.clientHeight,
        footerGap:f?(f.top-bottom)/scale:null,contentBottom:(bottom-r.top)/scale,beyond,
        mathSizes:[...s.querySelectorAll('.katex-display > .katex')].map(e=>getComputedStyle(e).fontSize)};
    })''')
    report['html_geometry']=geometry
    check('HTML 20 sections',len(geometry)==20)
    check('no vertical overflow',all(g['scrollHeight']<=g['clientHeight']+1 for g in geometry),[(g['page'],g['scrollHeight'],g['clientHeight']) for g in geometry if g['scrollHeight']>g['clientHeight']+1])
    check('no footer collision',all(g['footerGap'] is None or g['footerGap']>=4 for g in geometry),[(g['page'],g['footerGap']) for g in geometry if g['footerGap'] is not None and g['footerGap']<4])
    check('no math/figure/table outside slide',not any(g['beyond'] for g in geometry),[(g['page'],g['beyond']) for g in geometry if g['beyond']])
    check('display math uniformly 30px',all(x=='30px' for g in geometry for x in g['mathSizes']),sum(len(g['mathSizes']) for g in geometry))
    check('no KaTeX errors',page.locator('.katex-error').count()==0)
    visible=page.evaluate("Array.from(document.querySelectorAll('section')).map(s=>s.innerText).join('\\n')")
    check('no literal dollar/TeX leakage in HTML', '$' not in visible and '\\begin{' not in visible and '[t]' not in visible)
    check('all HTML images loaded',page.evaluate('Array.from(document.images).every(i=>i.complete&&i.naturalWidth>0)'))
    check('local Japanese font loaded',page.evaluate('document.fonts.check(\'26px "NotoJP"\')'))
    for number in [5,10,13,14]:
        page.goto((BASE/'slides.html').as_uri()+f'#{number}')
        page.locator('section').nth(number-1).wait_for(state='visible')
        page.locator('section').nth(number-1).screenshot(path=str(BASE/f'evidence/html_slide_{number:02}.png'))
    browser.close()
# All-page PDF evidence plus contact sheet, not in assets.
for i,p in enumerate(doc):
    p.get_pixmap(matrix=pymupdf.Matrix(1.25,1.25),alpha=False).save(BASE/f'evidence/slide_{i+1:02}.png')
sheet=Image.new('RGB',(1600,1000),'#ddd'); draw=ImageDraw.Draw(sheet)
for i in range(len(doc)):
    im=Image.open(BASE/f'evidence/slide_{i+1:02}.png'); im.thumbnail((394,222))
    x=(i%4)*400; y=(i//4)*200
    im.thumbnail((348,176)); sheet.paste(im,(x+24,y+18)); draw.text((x+4,y+2),str(i+1),fill='black')
sheet.save(BASE/'evidence/contact_sheet_20.png')
check('final protected hashes unchanged',all(digest(BASE/p)==h for p,h in protected.items()))
report['passed']=all(c['ok'] for c in report['checks'])
(BASE/'verification_log.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
print('\nALL PASS' if report['passed'] else '\nSOME CHECKS FAILED')
sys.exit(0 if report['passed'] else 1)
