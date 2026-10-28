#!/usr/bin/env python3
"""実行済notebook・PDF・HTML・テストの機械検証。自作の検証記録を出力。"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import nbformat
import pymupdf
from PIL import Image
from playwright.sync_api import sync_playwright

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    verification=json.loads((HERE/'results/verification.json').read_text())
    nb=nbformat.read(HERE/'analysis.ipynb',as_version=4)
    cells=[c for c in nb.cells if c.cell_type=='code']
    assert all(c.execution_count is not None for c in cells)
    assert not any(o.output_type=='error' for c in cells for o in c.outputs)
    images=sum('image/png' in o.get('data',{}) for c in cells for o in c.outputs)
    assert images>=3
    joined='\n'.join(o.get('text','') for c in cells for o in c.outputs)
    assert 'PASS:' in joined and '-1.555410' in joined
    d=pymupdf.open(HERE/'slides.pdf')
    assert len(d)==10
    assert all(len(pg.get_text().strip())>80 for pg in d)
    text='\n'.join(pg.get_text() for pg in d)
    for token in ['最低賃金','課題3','課題4','1.56','7.93','4.82','0.310','0.620']:
        assert token in text,token
    preview=HERE/'results'/'preview';preview.mkdir(exist_ok=True)
    contact=Image.new('RGB',(1280,1800),'#ddd')
    for i,pg in enumerate(d):
        target=preview/f'page_{i+1:02d}.png'
        pg.get_pixmap(matrix=pymupdf.Matrix(1,1),alpha=False).save(target)
        contact.paste(Image.open(target).resize((640,360)),((i%2)*640,(i//2)*360))
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
            const source=s.querySelector('.source');
            const sourceRect=source?.getBoundingClientRect();
            const children=Array.from(s.children).filter(x=>!x.classList.contains('source') && !['STYLE','SCRIPT'].includes(x.tagName));
            const maxBottom=Math.max(...children.map(x=>x.getBoundingClientRect().bottom));
            return {page:i+1,scrollHeight:s.scrollHeight,clientHeight:s.clientHeight,
                bodyBottom:maxBottom-rect.top,sourceTop:sourceRect?sourceRect.top-rect.top:null,
                imageCount:s.querySelectorAll('img').length,
                brokenImages:Array.from(s.querySelectorAll('img')).filter(im=>!im.complete||im.naturalWidth===0).length};
        })''')
        assert len(layout)==10
        assert all(v['scrollHeight']<=v['clientHeight']+1 for v in layout),layout
        assert all(v['brokenImages']==0 for v in layout)
        assert all(v['sourceTop'] is None or v['bodyBottom'] < v['sourceTop'] for v in layout),layout
        assert page.locator('section .small').evaluate_all("es => es.every(e => !e.innerText.includes('$'))")
        assert not errors,errors
        font_loaded=page.evaluate("document.fonts.check('27px BasicNoto')")
        assert font_loaded
        browser.close()
    test=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(HERE/'tests'),'-v'],cwd=ROOT,text=True,capture_output=True)
    (HERE/'results/test.log').write_text(test.stdout+test.stderr)
    assert test.returncode==0,test.stderr
    names=['analysis.py','analysis.ipynb','build_materials.py','verify_artifacts.py','slides.md','slides.pdf','slides.html','methods.md','sources.md','README.md','requirements.txt','citation-ledger.json']
    assert all((HERE/n).is_file() for n in names)
    report={'status':'passed','data_and_model':verification,
            'notebook':{'all_code_cells_executed':True,'code_cells':len(cells),'image_outputs':images,'error_outputs':0,
                        'primary_numeric_output_checked':True},
            'slides':{'pdf_pages':len(d),'max_pages':10,'pdf_text_numeric_checks':True,'html_sections':len(layout),
                      'font_loaded':font_loaded,'browser_page_errors':errors,'html_layout':layout,
                      'visual_preview':'results/preview/contact_sheet.png'},
            'tests':{'returncode':test.returncode,'count':6,'log':'results/test.log'},
            'files':{n:{'bytes':(HERE/n).stat().st_size,'sha256':digest(HERE/n)} for n in names},
            'scope':'Only this 01-basic directory was written; no commit/push. Verify via git status.'}
    (HERE/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':'passed','pdf_pages':len(d),'executed_code_cells':len(cells),'notebook_images':images,
                       'tests':6,'layout':layout},ensure_ascii=False,indent=2))

if __name__=='__main__': main()
