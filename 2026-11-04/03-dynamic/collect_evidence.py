"""Read-only source audit; writes only this deliverable directory."""
from pathlib import Path
import json, subprocess, sys, urllib.request, hashlib, shutil
import pymupdf
H=Path(__file__).resolve().parent
E=H/'evidence'
E.mkdir(exist_ok=True)
S='/opt/data/skills/research/grounded-citations/scripts/sources.py'
ledger=H/'citation-ledger.json'
sources=[
('https://www.e-stat.go.jp/stat-search/file-download?statInfId=000040505323&fileKind=0','一般職業紹介状況 第12表','data/raw/estat_shokugyo_t12_shinki_kyujin.xlsx','Table12.xlsx'),
('https://www.mhlw.go.jp/content/11200000/001756130.xlsx','地域別最低賃金改定状況','data/raw/mhlw_saitei_chingin_kaitei.xlsx','MW.xlsx'),
('https://www.nber.org/system/files/working_papers/w4394/w4394.pdf','Hamermesh 1993 NBER WP4394','/opt/data/cache/scratch/Hamermesh_1993_Labor_Demand_Adjustment_Costs_NBER_WP4394.pdf','Hamermesh1993.pdf'),
('https://www.nber.org/system/files/working_papers/w3356/w3356.pdf','Hamermesh 1990 NBER WP3356','/opt/data/cache/scratch/Hamermesh_1990_Dynamic_Labor_Demand_NBER_WP3356.pdf','Hamermesh1990.pdf'),
('https://docs.iza.org/dp15254.pdf','Kudlyak Tasci Tuzemen IZA DP15254 Jan2023',None,'Kudlyak2023.pdf'),
('https://ies.keio.ac.jp/upload/DPEN_7694_202203091453351.pdf','Ohta Komae 2022 DP2022-004','materials/Ohta_Komae_2022_Vacancies_Job_Seekers_Minimum_Wages.pdf','Ohta2022.pdf'),
('https://www.tandfonline.com/doi/full/10.1080/00036846.2025.2579945','Kazekami Abe 2025 published','materials/Kazekami_Abe_2025_Minimum_Wages_Labor_Demand.pdf','Kazekami2025.pdf'),
('https://www.mhlw.go.jp/stf/newpage_60788.html','2025-08-04目安公表',None,'guideline.html'),
('https://www.mhlw.go.jp/stf/newpage_63030.html','2025-09-05答申まとめ（予定）',None,'recommendations.html'),
('https://www.mhlw.go.jp/content/11201250/001714252.pdf','2026-06-23発効時期の検討','/opt/data/reports/minwage-timing-2025/policy/raw/mhlw_20260623_review.pdf','Review2026.pdf'),
('https://www.mhlw.go.jp/content/11302000/001531874.pdf','2024年度確定一覧','/opt/data/reports/minwage-timing-2025/policy/raw/mhlw_2024_final.pdf','MW2024.pdf'),
('https://nowcast.co.jp/news/20260707','Nowcast 2026-07-07 最低賃金・募集賃金・求人量','/opt/data/reports/minwage-timing-2025/policy/raw/nowcast_20260707.html','Nowcast2026.html'),
]
root=H.parents[1]
subprocess.run([sys.executable,S,'--ledger',str(ledger),'reset'],check=True)
manifest=[]
for url,title,local,name in sources:
    subprocess.run([sys.executable,S,'--ledger',str(ledger),'add',url,'--title',title],check=True)
    target=E/name
    if local:
        p=Path(local); p=p if p.is_absolute() else root/p
        shutil.copyfile(p,target)
        status='archived original; inspected in this task'
    else:
        with urllib.request.urlopen(url,timeout=90) as r: target.write_bytes(r.read())
        status='HTTP retrieved in this task'
    item=dict(url=url,title=title,file=name,status=status,sha256=hashlib.sha256(target.read_bytes()).hexdigest())
    if target.suffix=='.pdf':
        doc=pymupdf.open(target); item['physical_pages']=len(doc)
        txt='\n\n'.join(f'=== PDF PAGE {i+1} ===\n'+pg.get_text() for i,pg in enumerate(doc))
        (E/(target.stem+'.txt')).write_text(txt)
        item['text_characters']=len(txt)
    manifest.append(item)
(H/'source-inventory.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print(json.dumps(manifest,ensure_ascii=False,indent=2))
