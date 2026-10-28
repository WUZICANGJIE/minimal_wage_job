#!/usr/bin/env python3
"""20頁の発表資料・数式・講稿・既存結果の不変性を実物で検証する。"""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys
import nbformat
import pymupdf
from PIL import Image, ImageDraw
from playwright.sync_api import sync_playwright
from build_materials import split_slides, notes_for, TODO_PAGES

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
EXPECTED_PAGES=20

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    frozen=json.loads((HERE/'evidence/before_rewrite_sha256.json').read_text())
    after={name:digest(ROOT/name) for name in frozen}
    assert frozen==after, 'Analysis/raw/empirical CSV changed'
    reproduced = {p.name: p.read_bytes()==(HERE/'results/reproduction'/p.name).read_bytes()
                  for p in (HERE/'results').glob('*.csv')}
    assert len(reproduced)==6 and all(reproduced.values()), reproduced
    verification=json.loads((HERE/'results/verification.json').read_text())
    fresh_verification=json.loads((HERE/'results/reproduction/verification.json').read_text())
    assert fresh_verification==verification, 'Reproduced data/model checks differ'
    nb=nbformat.read(HERE/'analysis.ipynb',as_version=4)
    cells=[c for c in nb.cells if c.cell_type=='code']
    assert all(c.execution_count is not None for c in cells)
    assert not any(o.output_type=='error' for c in cells for o in c.outputs)
    images=sum('image/png' in o.get('data',{}) for c in cells for o in c.outputs)
    assert images>=3
    joined='\n'.join(o.get('text','') for c in cells for o in c.outputs)
    assert 'PASS:' in joined and '-1.555410' in joined
    source=(HERE/'slides.md').read_text()
    _,slides=split_slides(source)
    assert len(slides)==EXPECTED_PAGES
    assert all(len(notes_for(s))==1 for s in slides)
    assert len(re.findall(r'^## \d+頁', (HERE/'speaker_notes.md').read_text(),re.M))==EXPECTED_PAGES
    assert 'aligned[t]' not in source and '同比' not in source
    d=pymupdf.open(HERE/'slides.pdf')
    assert len(d)==EXPECTED_PAGES
    assert all(len(pg.get_text().strip())>80 for pg in d)
    text='\n'.join(pg.get_text() for pg in d)
    for token in ['最低賃金','課題3','課題4','1.56','7.93','4.82','0.310','0.620','82.64']:
        assert token in text,token
    assert '\ufffd' not in text
    preview=HERE/'results'/'preview';preview.mkdir(exist_ok=True)
    cols,rows=4,(len(d)+3)//4
    contact=Image.new('RGB',(cols*480,rows*294),'#ddd')
    draw=ImageDraw.Draw(contact)
    for i,pg in enumerate(d):
        target=preview/f'page_{i+1:02d}.png'
        pg.get_pixmap(matrix=pymupdf.Matrix(1280/pg.rect.width,1280/pg.rect.width),alpha=False).save(target)
        x,y=(i%cols)*480,(i//cols)*294
        contact.paste(Image.open(target).resize((480,270)),(x,y+24))
        draw.text((x+10,y+5),str(i+1),fill='black')
    contact.save(preview/'contact_sheet.png')
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox','--allow-file-access-from-files'])
        page=browser.new_page(viewport={'width':1280,'height':720})
        errors=[]
        page.on('pageerror',lambda e:errors.append(str(e)))
        page.goto((HERE/'slides.html').as_uri(),wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        layout=page.evaluate('''() => Array.from(document.querySelectorAll('section')).map((s,i)=>{
            const rect=s.getBoundingClientRect();
            const scale=rect.width/1280;
            const source=s.querySelector('.source');
            const sourceRect=source?.getBoundingClientRect();
            const children=Array.from(s.children).filter(x=>!x.classList.contains('source') && !['STYLE','SCRIPT'].includes(x.tagName));
            const maxBottom=Math.max(...children.map(x=>x.getBoundingClientRect().bottom));
            const content=Array.from(s.querySelectorAll('h1,h2,p,li,table,img,.katex-display,.small')).filter(x=>!x.closest('.source')&&!x.closest('.katex-mathml'));
            const outside=content.filter(x=>{const r=x.getBoundingClientRect();return r.left<rect.left-1||r.right>rect.right+1||r.bottom>rect.bottom-35*scale;}).map(x=>({tag:x.tagName,text:x.innerText?.slice(0,70)}));
            const math=Array.from(s.querySelectorAll('.katex-display > .katex')).map(x=>({fontSize:getComputedStyle(x).fontSize,width:x.getBoundingClientRect().width/scale}));
            return {page:i+1,scrollHeight:s.scrollHeight,clientHeight:s.clientHeight,
                scrollWidth:s.scrollWidth,clientWidth:s.clientWidth,
                bodyBottom:(maxBottom-rect.top)/scale,sourceTop:sourceRect?(sourceRect.top-rect.top)/scale:null,
                contentOutside:outside,displayMath:math,
                imageCount:s.querySelectorAll('img').length,
                brokenImages:Array.from(s.querySelectorAll('img')).filter(im=>!im.complete||im.naturalWidth===0).length};
        })''')
        (preview/'layout.json').write_text(json.dumps(layout,ensure_ascii=False,indent=2)+'\n')
        assert len(layout)==EXPECTED_PAGES
        assert all(v['scrollHeight']<=v['clientHeight']+1 and v['scrollWidth']<=v['clientWidth']+1 for v in layout),layout
        assert all(v['brokenImages']==0 and not v['contentOutside'] for v in layout),layout
        assert all(v['sourceTop'] is None or v['bodyBottom']+4 < v['sourceTop'] for v in layout),layout
        assert page.locator('.katex-error').count()==0
        assert page.locator('.katex-display').count()>=12
        assert page.locator('section .small').evaluate_all("es => es.every(e => !e.innerText.includes('$'))")
        assert not errors,errors
        font_loaded=page.evaluate("document.fonts.check('27px BasicNoto')")
        assert font_loaded
        # Visible HTML must not leak raw TeX; ignore MathML/annotation used by KaTeX for accessibility.
        leaks=page.evaluate(r'''() => Array.from(document.querySelectorAll('section')).flatMap((s,i)=>{
            const c=s.cloneNode(true);c.querySelectorAll('.katex,style,script').forEach(x=>x.remove());
            return /\\(?:frac|begin|max|partial)|\$/.test(c.textContent)?[i+1]:[];})''')
        assert not leaks,leaks
        browser.close()
    test=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE/'tests'),'-v'],cwd=ROOT,text=True,capture_output=True)
    (HERE/'results/test.log').write_text(test.stdout+test.stderr)
    assert test.returncode==0,test.stderr
    count_match=re.search(r'Ran (\d+) tests?',test.stderr)
    assert count_match is not None, test.stderr
    test_count=int(count_match.group(1))
    names=['analysis.py','analysis.ipynb','build_materials.py','verify_artifacts.py','slides.md','slides.pdf','slides.html','speaker_notes.md','methods.md','sources.md','README.md','requirements.txt','citation-ledger.json']
    assert all((HERE/n).is_file() for n in names)
    report={'status':'passed','data_and_model':verification,
            'fresh_analysis_reproduction':{'csv_byte_identity':reproduced,'data_and_model_report_identical':fresh_verification==verification},
            'frozen_inputs':{'unchanged':frozen==after,'sha256':after,'includes':'analysis.py, six empirical CSVs, two raw workbooks'},
            'notebook':{'existing_executed_notebook_preserved':True,'all_code_cells_executed':True,'code_cells':len(cells),'image_outputs':images,'error_outputs':0},
            'slides':{'pdf_pages':len(d),'expected_pages':EXPECTED_PAGES,'speaker_notes':len(slides),'todo_pages':TODO_PAGES,
                      'pdf_text_numeric_checks':True,'html_sections':len(layout),'katex_errors':0,'raw_tex_leaks':leaks,
                      'font_loaded':font_loaded,'browser_page_errors':errors,'html_layout':layout,
                      'visual_preview':'results/preview/contact_sheet.png'},
            'tests':{'returncode':test.returncode,'count':test_count,'log':'results/test.log'},
            'files':{n:{'bytes':(HERE/n).stat().st_size,'sha256':digest(HERE/n)} for n in names},
            'scope':'Only this 01-basic directory was written; no commit/push. Verify via git status.'}
    (HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'passed','pdf_pages':len(d),'notes':len(slides),'csv_and_analysis_and_raw_unchanged':True,
                     'executed_notebook_code_cells':len(cells),'tests':test_count,'layout':layout},ensure_ascii=False,indent=2))

if __name__=='__main__':
    main()
