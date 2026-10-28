"""Build teaching-only figure/notes; never write statistical results."""
from pathlib import Path
import re
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager

BASE = Path(__file__).resolve().parent

def build():
    font = BASE/'assets/NotoSansJP-Regular.otf'
    font_manager.fontManager.addfont(font)
    plt.rcParams.update({'font.family': font_manager.FontProperties(fname=font).get_name(),
                         'font.size': 17, 'axes.spines.top': False,
                         'axes.spines.right': False, 'axes.spines.left': False})
    r = pd.read_csv(BASE/'results/contrasts.csv').query("metric == 'part' and baseline_end == '2025-09'").iloc[0]
    fig, ax = plt.subplots(figsize=(11, 1.8), layout='constrained')
    ax.axvline(0, ls='--', color='.5', lw=1)
    ax.errorbar(r.estimate, 0, xerr=[[r.estimate-r.ci_low], [r.ci_high-r.estimate]],
                fmt='o', color='black', capsize=8, markersize=10, lw=2)
    ax.set_xlim(-10, 7); ax.set_ylim(-.6,.6); ax.set_yticks([])
    ax.set_xticks([-8,-4,0,4]); ax.set_xlabel('早期−後期の変化の差（100×対数差）')
    ax.text(r.estimate,.2,f'{r.estimate:.2f}', ha='center')
    fig.savefig(BASE/'assets/part_interval_teaching.png', dpi=180)
    plt.close(fig)
    source = (BASE/'slides.md').read_text()
    body = source.split('---',2)[2]
    pages = re.split(r'^---\s*$', body, flags=re.M)
    out=['# 逐頁の講解メモ\n\nslides.md内の非表示speaker notesから生成。本文の代わりではなく、発表時の補助。\n']
    for i,page in enumerate(pages,1):
        heading=re.search(r'^# (.+)$',page,re.M)
        assert heading is not None, i
        title=heading.group(1)
        notes=re.findall(r'<!-- notes: (.*?) -->',page,re.S)
        assert len(notes)==1, (i,notes)
        out.append(f'## {i}頁｜{title}\n\n{notes[0]}\n')
    assert len(pages)==20, len(pages)
    (BASE/'speaker_notes.md').write_text('\n'.join(out))
    print(f'Built teaching figure and {len(pages)} page notes; CSVs untouched.')

if __name__=='__main__':
    build()
