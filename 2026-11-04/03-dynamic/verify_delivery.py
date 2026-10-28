"""Read-back checks for the 20-page teaching deck and preserved analysis."""
from pathlib import Path
import hashlib,json,re
import pymupdf
import nbformat
from PIL import Image,ImageOps,ImageDraw
from playwright.sync_api import sync_playwright
H=Path(__file__).resolve().parent

def main():
    checks={}
    v=json.loads((H/'verification.json').read_text())
    teaching=json.loads((H/'teaching-verification.json').read_text())
    checks['data_and_model_checks']=all(v['data']['checks'].values()) and v['model']['all_kkt_pass']
    for name,digest in v['data']['raw_sha256'].items():
        assert hashlib.sha256((H.parents[1]/'data/raw'/name).read_bytes()).hexdigest()==digest
    checks['raw_hashes_unchanged']=True
    preserved=json.loads((H/'preserved-analysis-sha256.json').read_text())
    checks['analysis_code_csv_and_summary_unchanged']=all(hashlib.sha256((H/name).read_bytes()).hexdigest()==sha for name,sha in preserved.items())
    nb=nbformat.read(H/'analysis.ipynb',as_version=4)
    codes=[c for c in nb.cells if c.cell_type=='code']
    checks['notebook_all_7_code_cells_executed']=len(codes)==7 and all(c.execution_count is not None for c in codes)
    checks['notebook_no_errors']=not [o for c in codes for o in c.outputs if o.output_type=='error']
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
    md=(H/'slides.md').read_text()
    pages=re.split(r'^---\s*$',md,flags=re.M)[2:]
    checks['md_20_pages']=len(pages)==20
    checks['each_page_has_speaker_note']=all(len([c for c in re.findall(r'<!--(.*?)-->',p,re.S) if not c.strip().startswith('_')])==1 for p in pages)
    notes=(H/'speaker_notes.md').read_text()
    checks['speaker_notes_20_pages']=len(re.findall(r'^## \d+頁',notes,re.M))==20
    checks['todo_six_items_with_real_page_numbers']=len(teaching['todo_page_map'])==6 and all(all(1<=p<=len(pages) for p in pp) for pp in teaching['todo_page_map'].values())
    pdf=pymupdf.open(H/'slides.pdf')
    checks['pdf_20_pages']=len(pdf)==20
    checks['pdf_all_pages_text']=all(len(p.get_text())>50 for p in pdf)
    text='\n'.join(p.get_text() for p in pdf)
    checks['pdf_japanese_text']='最低賃金' in text and '11月' in text
    checks['pdf_main_result_present']='1.56' in text and '7.93' in text and '4.82' in text
    checks['pdf_no_replacement_character']='\ufffd' not in text
    checks['pdf_no_raw_math_delimiters']='$' not in text
    # Check rendered content geometry, equation widths, image loading and font sizes.
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path='/usr/bin/chromium',headless=True,args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1280,'height':720})
        page.goto((H/'slides.html').as_uri()); page.evaluate('document.fonts.ready')
        page.wait_for_function("Array.from(document.images).every(i=>i.complete)")
        geometry=page.evaluate('''() => Array.from(document.querySelectorAll('section')).map((s,i)=>{
          const r=s.getBoundingClientRect(); const scale=r.width/s.clientWidth;
          const bad=Array.from(s.querySelectorAll('h1,h2,p,table,li,img,.small,.source,.katex-display .katex-html')).filter(e=>{
            const b=e.getBoundingClientRect();
            return b.height>0&&(b.bottom>r.bottom-32*scale||b.right>r.right-16*scale||b.left<r.left+16*scale);
          }).map(e=>e.tagName+':'+e.textContent.slice(0,80));
          return {page:i+1,width:s.clientWidth,height:s.clientHeight,scrollHeight:s.scrollHeight,scrollWidth:s.scrollWidth,bad};
        })''')
        images=page.evaluate("Array.from(document.querySelectorAll('section img')).map(i=>({src:i.getAttribute('src'),loaded:i.complete&&i.naturalWidth>0}))")
        fonts=page.evaluate("document.fonts.check('26px LocalJP')")
        math=page.evaluate('''() => ({errors:document.querySelectorAll('.katex-error').length,
          displays:document.querySelectorAll('.katex-display').length,
          sizes:Array.from(document.querySelectorAll('.katex-display > .katex')).map(e=>parseFloat(getComputedStyle(e).fontSize)),
          literalAligned:Array.from(document.querySelectorAll('section')).some(s=>s.innerText.includes('aligned[t]'))})''')
        browser.close()
    checks['html_20_sections']=len(geometry)==20
    checks['html_no_element_or_scroll_overflow']=all(not g['bad'] and g['scrollHeight']<=g['height']+1 and g['scrollWidth']<=g['width']+1 for g in geometry)
    checks['html_all_local_images_loaded']=len(images)==2 and all(x['loaded'] and not x['src'].startswith('http') for x in images)
    checks['html_local_japanese_font_loaded']=fonts
    checks['katex_no_error_or_literal_option']=math['errors']==0 and not math['literalAligned']
    checks['display_math_30px']=math['displays']>=10 and all(abs(s-30)<.1 for s in math['sizes'])
    # Regenerate all page images and a 4x5 contact sheet, not an old 10-page grid.
    tiles=[]
    for i,p in enumerate(pdf):
        target=H/'evidence'/f'slide-{i+1}.png'
        p.get_pixmap(matrix=pymupdf.Matrix(1.4,1.4)).save(target)
        im=Image.open(target).convert('RGB'); im.thumbnail((384,216))
        tile=Image.new('RGB',(400,248),'#e6e6e6'); tile.paste(im,((400-im.width)//2,22)); ImageDraw.Draw(tile).text((10,4),str(i+1),fill='black')
        tiles.append(tile)
    sheet=Image.new('RGB',(1600,1240),'white')
    for i,tile in enumerate(tiles):sheet.paste(tile,((i%4)*400,(i//4)*248))
    sheet.save(H/'evidence/slides-contact-sheet.png')
    review=H/'visual-review.json'
    manual=json.loads(review.read_text()) if review.exists() else {'status':'pending'}
    same_pdf=manual.get('pdf_sha256')==hashlib.sha256((H/'slides.pdf').read_bytes()).hexdigest()
    # Marp changes PDF timestamps on rebuild. Preserve approval only when every
    # rendered page is byte-identical to the pixels of the reviewed document.
    pixels=[hashlib.sha256(p.get_pixmap(matrix=pymupdf.Matrix(2,2),alpha=False).samples).hexdigest() for p in pdf]
    same_pixels=manual.get('page_pixels_sha256_2x')==pixels
    checks['visual_review_matches_current_pdf']=(same_pdf or same_pixels) and manual.get('status')=='passed' and manual.get('reviewed_pages')==list(range(1,21))
    visual_match={'exact_pdf_bytes':same_pdf,'exact_reviewed_pixels':same_pixels}
    v['delivery']={'checks':checks,'pdf_pages':len(pdf),'executed_code_cells':len(codes),'citations':citation_stats,'html_geometry':geometry,'images':images,'math':math,'todo_page_map':teaching['todo_page_map'],'visual_review':manual,'visual_match':visual_match}
    files={str(x.relative_to(H)):hashlib.sha256(x.read_bytes()).hexdigest() for x in H.rglob('*') if x.is_file() and x.suffix in ['.py','.md','.ipynb','.pdf','.html','.csv','.otf'] and '__pycache__' not in str(x)}
    (H/'artifact-sha256.json').write_text(json.dumps(files,ensure_ascii=False,indent=2))
    (H/'verification.json').write_text(json.dumps(v,ensure_ascii=False,indent=2))
    print(json.dumps(v['delivery'],ensure_ascii=False,indent=2))
    assert all(checks.values()),[k for k,x in checks.items() if not x]
    print('ALL DELIVERY CHECKS PASSED')

if __name__=='__main__':main()
