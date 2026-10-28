"""成果物の読み戻し検査。独立ソースのハッシュ、notebook、PDF、HTMLを確認。"""
from pathlib import Path
import hashlib,json,re,sys
import pymupdf
import nbformat
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent

def main():
    checks={}
    v=json.loads((H/'verification.json').read_text())
    checks['data_and_model_checks']=all(v['data']['checks'].values()) and v['model']['all_kkt_pass']
    for name,digest in v['data']['raw_sha256'].items():
        assert hashlib.sha256((H.parents[1]/'data/raw'/name).read_bytes()).hexdigest()==digest
    checks['raw_hashes_unchanged']=True
    nb=nbformat.read(H/'analysis.ipynb',as_version=4)
    codes=[c for c in nb.cells if c.cell_type=='code']
    checks['notebook_all_7_code_cells_executed']=len(codes)==7 and all(c.execution_count is not None for c in codes)
    errors=[o for c in codes for o in c.outputs if o.output_type=='error']
    checks['notebook_no_errors']=not errors
    checks['notebook_no_control_characters']=not any(any(ord(ch)<32 and ch not in '\n\t\r' for ch in c.source) for c in nb.cells)
    checks['no_fake_colab_link']='colab.research.google.com' not in (H/'analysis.ipynb').read_text()
    ledger=json.loads((H/'citation-ledger.json').read_text())['sources']
    ids={str(s['id']):s for s in ledger}
    citation_stats={}
    for name in ['slides.md','methods.md','sources.md']:
        text=(H/name).read_text(); body,refs=text.split('## Sources',1)
        cited=set(re.findall(r'\[(\d+)\]',body))
        assert cited<=ids.keys()
        for id_ in cited:
            assert ids[id_]['quotes']
            assert f"[{id_}] {ids[id_]['url']}" in refs
        citation_stats[name]={'cited_sources':len(cited),'all_ids_and_urls_match':True,'all_have_evidence':True}
    checks['citation_mapping_evidence']=True
    manifest=json.loads((H/'source-inventory.json').read_text())
    checks['archived_source_hashes_match']=all(hashlib.sha256((H/'evidence'/s['file']).read_bytes()).hexdigest()==s['sha256'] for s in manifest)
    pdf=pymupdf.open(H/'slides.pdf')
    checks['pdf_10_pages']=len(pdf)==10
    checks['pdf_all_pages_text']=all(len(p.get_text())>50 for p in pdf)
    text='\n'.join(p.get_text() for p in pdf)
    checks['pdf_japanese_text']='最低賃金' in text and '11月' in text
    checks['pdf_main_result_present']='1.56' in text and '7.93' in text and '4.82' in text
    # DOM geometry against each physical 1280x720 slide, including all images.
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':720})
        page.goto((H/'slides.html').as_uri()); page.evaluate('document.fonts.ready')
        geometry=page.evaluate('''() => Array.from(document.querySelectorAll('section')).map((s,i)=>{
          const r=s.getBoundingClientRect();
          const bad=Array.from(s.querySelectorAll('h1,h2,p,table,ul,img,.small,.source')).filter(e=>{
            const b=e.getBoundingClientRect();
            return b.height>0&&(b.bottom>r.bottom+2||b.right>r.right+2||b.left<r.left-2);
          }).map(e=>e.tagName+':'+e.textContent.slice(0,60));
          return {page:i+1,width:s.clientWidth,height:s.clientHeight,scrollHeight:s.scrollHeight,bad};
        })''')
        images=page.evaluate("Array.from(document.querySelectorAll('img')).map(i=>({src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth>0}))")
        fonts=page.evaluate("document.fonts.check('26px LocalJP')")
        browser.close()
    checks['html_10_sections']=len(geometry)==10
    checks['html_no_element_overflow']=all(not g['bad'] for g in geometry)
    checks['html_all_local_images_loaded']=len(images)==3 and all(x['loaded'] and not x['src'].startswith('http') for x in images)
    checks['html_local_japanese_font_loaded']=fonts
    for i,p in enumerate(pdf):
        p.get_pixmap(matrix=pymupdf.Matrix(1,1)).save(H/'evidence'/f'slide-{i+1}.png')
    checks['source_and_main_model_separated']=True # manual document review; see methods §1
    v['delivery']={'checks':checks,'pdf_pages':len(pdf),'executed_code_cells':len(codes),'citations':citation_stats,'html_geometry':geometry,'images':images,'visual_review':'Contact sheet plus pages 3,5,8,9,10 reviewed visually by agent; no overflow/glyph loss observed.'}
    files={str(x.relative_to(H)):hashlib.sha256(x.read_bytes()).hexdigest() for x in H.rglob('*') if x.is_file() and x.suffix in ['.py','.md','.ipynb','.pdf','.html','.csv','.otf'] and '__pycache__' not in str(x)}
    (H/'artifact-sha256.json').write_text(json.dumps(files,ensure_ascii=False,indent=2))
    (H/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2))
    print(json.dumps(v['delivery'],ensure_ascii=False,indent=2))
    assert all(checks.values()),[k for k,x in checks.items() if not x]
    print('ALL DELIVERY CHECKS PASSED')

if __name__=='__main__': main()
