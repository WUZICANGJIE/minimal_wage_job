"""一括再現。全コマンドの実出力をexecution.logへ保存。"""
from pathlib import Path
import subprocess,sys,os,json,importlib.metadata,datetime
H=Path(__file__).resolve().parent; ROOT=H.parents[1]
P=sys.executable
commands=[
    [P,str(H/'analysis.py')],
    [P,'-m','unittest','discover','-s',str(H/'tests'),'-v'],
    [P,str(H/'build_notebook.py')],
    ['npx','--yes','@marp-team/marp-cli@4.5.1',str(H/'slides.md'),'--no-config','--html','--allow-local-files','-o',str(H/'slides.html')],
    ['npx','--yes','@marp-team/marp-cli@4.5.1',str(H/'slides.md'),'--no-config','--html','--pdf','--allow-local-files','-o',str(H/'slides.pdf')],
    [P,str(H/'verify_delivery.py')],
]
versions={name:importlib.metadata.version(name) for name in ['numpy','pandas','openpyxl','scipy','statsmodels','matplotlib','nbformat','nbclient','ipykernel','pymupdf','playwright','pillow']}
(H/'requirements.txt').write_text('\n'.join(f'{name}=={version}' for name,version in versions.items())+'\n')
(H/'environment.json').write_text(json.dumps({'python':sys.version,'versions':versions,'execution_start_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2))
env=dict(os.environ); env['CHROME_PATH']='/usr/bin/chromium'
with (H/'execution.log').open('w') as log:
    for command in commands:
        log.write('\n$ '+' '.join(command)+'\n'); log.flush()
        run=subprocess.run(command,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=300)
        log.write(run.stdout+f'\nEXIT_CODE={run.returncode}\n'); log.flush()
        print(Path(command[1] if command[0]==P else command[0]).name,'exit',run.returncode)
        if command[-1]==str(H/'verify_delivery.py'):
            (H/'verification.log').write_text(run.stdout)
        if run.returncode:
            print(run.stdout); raise SystemExit(run.returncode)
print('All commands completed; log:',H/'execution.log')
