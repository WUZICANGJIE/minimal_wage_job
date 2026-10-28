#!/usr/bin/env python3
"""slides.mdを唯一の編集元として、講稿と授業用の数値検算を更新する。

This presentation-only build never regenerates the empirical CSVs or notebook.
Render slides.md with the pinned Marp command in README.md after running this.
"""
from pathlib import Path
import json
import re
import numpy as np
import pandas as pd
import analysis

HERE = Path(__file__).resolve().parent
TODO_PAGES = {
    '1_data_and_comparability': [2, 3],
    '2_prior_work_and_increment': [4],
    '3_micro_model_and_derivation': [5, 6, 7, 8, 9, 10, 11],
    '4_hypothesis_and_calculable_test': [12, 13, 14, 17],
    '5_results_and_theory_reality': [14, 15, 16, 17, 18],
    '6_conclusion_implications_limits': [19],
}

def split_slides(text):
    assert text.startswith('---\n')
    _, frontmatter, body = text.split('---\n', 2)
    return frontmatter, re.split(r'\n---\n', body)

def notes_for(slide):
    # Marp directives and the citation URL map are not spoken notes.
    return [s.strip() for s in re.findall(r'<!--(.*?)-->', slide, re.S)
            if s.strip() and not s.strip().startswith(('_', 'Machine-readable'))]

def main():
    path = HERE / 'slides.md'
    source = path.read_text()
    # Maintain the citation map without introducing a visible extra slide.
    clean = re.sub(r'\n<!-- Machine-readable.*?-->\s*$', '', source, flags=re.S)
    ledger = json.loads((HERE / 'citation-ledger.json').read_text())
    cited = {int(n) for n in re.findall(r'\[(\d+)\]', clean)}
    url_map = '## Sources\n\n' + '\n'.join(
        f"[{s['id']}] {s['url']}" for s in ledger['sources'] if s['id'] in cited)
    source = clean.rstrip() + '\n\n<!-- Machine-readable citation map.\n' + url_map + '\n-->\n'
    if path.read_text() != source:
        path.write_text(source)
    _, slides = split_slides(source)
    assert len(slides) == 20
    notes = ['# 基礎案：逐頁発表ノート\n\nslides.md の非表示コメントから出力。時間は未計測。\n']
    for i, slide in enumerate(slides, 1):
        heading = re.search(r'^# (.+)$', slide, re.M)
        assert heading is not None, f'Missing heading on slide {i}'
        title = heading.group(1)
        spoken = notes_for(slide)
        assert len(spoken) == 1, (i, spoken)
        notes.append(f'## {i}頁｜{title}\n\n{spoken[0]}\n')
    (HERE / 'speaker_notes.md').write_text('\n'.join(notes))

    est = pd.read_csv(HERE / 'results/estimates.csv')
    county = pd.read_csv(HERE / 'results/county_changes.csv')
    r = est.iloc[0]
    assert np.isclose(r.delta, -1.5554104519904133)
    assert np.isclose(r.delta, r.nov_gap-r.pre_gap)
    params = dict(p=3200000., A=1., K=1., alpha=.3, beta=.5, hours=160.)
    targets = [analysis.desired_employment(w, **params) for w in (1000., 1100.)]
    assert np.allclose(targets, [100., 82.64462809917354])
    # FOC in the same units: marginal revenue equals period wage bill.
    assert all(np.isclose(params['p']*.5*n**(-.5),160*w)
               for n,w in zip(targets,[1000.,1100.]))
    replacement = [analysis.new_vacancies(100,100,separation=s,fill=1,channel=1)
                   for s in [.10,.05]]
    assert replacement == [10.,5.]
    tokyo = county.query("baseline == '2025-01..09' and pref == '東京都'").iloc[0]
    assert np.isclose(tokyo.d, tokyo.nov_yoy-tokyo.pre_yoy)
    example = {
        'illustrative_only': True, 'parameters_not_estimated': params,
        'wages_yen_per_hour': [1000.,1100.], 'desired_employment_people': targets,
        'employment_change_percent': 100*(targets[1]/targets[0]-1),
        'replacement_example': {'target':100,'previous':100,'fill':1,'channel':1,
                                'separations':[.10,.05],'vacancies':replacement},
        'tokyo_actual': {k:float(tokyo[k]) for k in ['pre_yoy','nov_yoy','d']},
        'primary_actual': {k:float(r[k]) for k in ['delta','ci_low','ci_high','p_one_sided_negative']},
        'todo_pages': TODO_PAGES,
    }
    (HERE / 'evidence/teaching_examples.json').write_text(json.dumps(example,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'slides':len(slides),'speaker_notes':len(notes)-1,
                      'model_example_people':targets,'replacement_vacancies':replacement,
                      'empirical_delta':float(r.delta),'canonical_source':'slides.md',
                      'empirical_csvs_and_notebook':'read-only / not rebuilt'},ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
