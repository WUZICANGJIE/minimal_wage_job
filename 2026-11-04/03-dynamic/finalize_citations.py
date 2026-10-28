"""引用証拠とSourcesブロックを独立ledgerから生成。外部取得はしない。"""
from pathlib import Path
import subprocess,sys,re
from html.parser import HTMLParser
import pandas as pd
import pymupdf
H=Path(__file__).resolve().parent; E=H/'evidence'
S='/opt/data/skills/research/grounded-citations/scripts/sources.py'
def cmd(*args):
    return subprocess.run([sys.executable,S,'--ledger',str(H/'citation-ledger.json'),*map(str,args)],check=True,text=True,capture_output=True).stdout
class Text(HTMLParser):
    def __init__(self): super().__init__(); self.text=[]
    def handle_data(self,s): self.text.append(s)
for stem in ['guideline','recommendations','Nowcast2026']:
    p=E/(stem+'.html'); parser=Text(); parser.feed(p.read_text())
    (E/(stem+'.txt')).write_text('\n'.join(parser.text))
for id_,name in [(1,'Table12.xlsx'),(2,'MW.xlsx')]:
    x=pd.read_excel(E/name,header=None,nrows=4)
    text=x.to_string(index=False,header=False)
    f=E/(Path(name).stem+'_headers.txt'); f.write_text(text)
    # Literal worksheet cells, not a quote of a human-written definition.
    print(cmd('quote',id_,'--text',text[:1000],'--from',f))
specs=[
(3,'Hamermesh_visual_transcription.txt','The first term in (1) reflects the costs of adjusting the level of employment (net costs), while the second measures the costs of hiring (gross costs).'),
(4,'Hamermesh_visual_transcription.txt','In the theoretical derivation I assume that the firm has static expectations about the future paths of product and factor prices.'),
(5,'Kudlyak2023.txt',None),
(6,'Ohta2022.txt',None),
(7,'Kazekami2025.txt',None),
(8,'guideline.txt',None),
(9,'recommendations.txt',None),
(10,'Review2026.txt',None),
(11,'MW2024.txt',None),
(12,'Nowcast2026.txt',None),
]
for id_,name,quote in specs:
    f=E/name; text=f.read_text()
    if id_==5:
        quote=pymupdf.open(E/'Kudlyak2023.pdf')[21].get_text()
    elif id_==6:
        quote=pymupdf.open(E/'Ohta2022.pdf')[13].get_text()
    elif id_==7:
        quote=pymupdf.open(E/'Kazekami2025.pdf')[3].get_text()
    elif id_==8:
        start=text.index('目安は'); quote=text[start:start+2000]
    elif id_==9:
        start=text.index('全ての都道府県'); quote=text[start:start+1800]
    elif id_==10:
        quote=pymupdf.open(E/'Review2026.pdf')[4].get_text()
    elif id_==11:
        quote=text
    elif id_==12:
        start=text.index('テーマ１'); quote=text[start:start+2200]
    print(cmd('quote',id_,'--text',quote,'--from',f))
for name in ['slides.md','methods.md','sources.md']:
    print(cmd('render','--replace-in',H/name))
    print(cmd('verify',H/name,'--strict','--evidence'))
