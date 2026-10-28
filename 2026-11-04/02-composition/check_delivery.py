"""End-to-end checks for the delivered artifacts. Run from this directory."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

import nbformat
import pymupdf

BASE = Path(__file__).resolve().parent
PY = sys.executable
report = {'checks': [], 'passed': False}


def check(name, ok, detail=''):
    report['checks'].append({'name': name, 'ok': bool(ok), 'detail': str(detail)})
    print(('PASS ' if ok else 'FAIL ') + name + (f' :: {detail}' if detail else ''))


# 1. tests
proc = subprocess.run([PY, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                      cwd=BASE, capture_output=True, text=True)
(BASE/'evidence'/'test_final.log').write_text(proc.stdout + proc.stderr)
check('unit tests', proc.returncode == 0, proc.stderr.strip().splitlines()[-1] if proc.stderr else '')

# 2. analysis rerun and numeric agreement
proc = subprocess.run([PY, 'analysis.py'], cwd=BASE, capture_output=True, text=True)
(BASE/'evidence'/'run_final.log').write_text(proc.stdout + proc.stderr)
check('analysis.py exit 0', proc.returncode == 0)
v = json.loads((BASE/'verification.json').read_text())
check('analysis status', v['status'] == 'analysis_passed')
check('inputs unchanged', v['inputs_unchanged'] is True)
check('part+nonpart identity residual 0', v['data']['part_plus_nonpart_max_abs_residual'] == 0)
check('47 prefectures x 164 months', v['data']['part']['prefectures'] == 47 and v['data']['part']['months'] == 164)
check('policy 20/13/14', v['policy_group_counts'] == {'early': 20, 'excluded': 13, 'late': 14}, v['policy_group_counts'])
check('independent policy PDF 47/47', v['independent_policy_check']['matched_prefectures'] == 47)
check('model parameters not estimated', v['model']['parameters_estimated'] is False)
check('model relative error < 1e-12', v['model']['max_relative_ratio_error'] < 1e-12, v['model']['max_relative_ratio_error'])
check('model derivative error < 1e-5', v['model']['max_derivative_error'] < 1e-5, v['model']['max_derivative_error'])

res = {(r['metric'], r['baseline_end']): r for r in v['results']}
main = res[('relative', '2025-09')]
check('main relative estimate -2.23', abs(main['estimate'] + 2.227) < 0.01, main['estimate'])
check('relative identity with part-nonpart',
      abs(res[('relative','2025-09')]['estimate']
          - (res[('part','2025-09')]['estimate'] - res[('nonpart','2025-09')]['estimate'])) < 1e-9)
check('all main CIs include zero (null reported honestly)',
      all(res[(k,'2025-09')]['ci_low'] < 0 < res[(k,'2025-09')]['ci_high']
          for k in ['part','nonpart','total','relative','share_pp']))

# 3. notebook: executed, no errors, contains outputs
nb = nbformat.read(BASE/'analysis.ipynb', as_version=4)
code_cells = [c for c in nb.cells if c.cell_type == 'code']
errors = [o for c in code_cells for o in c.get('outputs', []) if o.output_type == 'error']
with_output = [c for c in code_cells if c.get('outputs')]
check('notebook executed (no error outputs)', not errors, len(errors))
check('notebook has stored outputs', len(with_output) == len(code_cells), f'{len(with_output)}/{len(code_cells)}')
check('notebook has no fake Colab link', 'colab.research.google.com/github' not in json.dumps(nb))

# 4. slides: page count, text, links
doc = pymupdf.open(BASE/'slides.pdf')
check('slides.pdf <= 10 pages', len(doc) <= 10, len(doc))
text = '\n'.join(p.get_text() for p in doc)
for needle in ['−1.56', '−2.23', 'パート以外', '無処理の対照', 'Acemoglu']:
    check(f'slides contain {needle}', needle in text)
check('slides disclaim causality', '因果ではない' in text)
check('slides do not call nonpart an untreated control affirmatively',
      '「無処理の対照」とは呼べない' in text)
check('HTML exists and references local assets', (BASE/'slides.html').exists()
      and 'assets/' in (BASE/'slides.html').read_text())
check('figures exist', (BASE/'assets'/'observed_trends.png').exists()
      and (BASE/'assets'/'observed_contrasts.png').exists())

# 5. deliverables present
for name in ['README.md','methods.md','sources.md','verification.json','slides.md']:
    check(f'{name} exists', (BASE/name).exists())
check('results CSVs', len(list((BASE/'results').glob('*.csv'))) >= 8,
      len(list((BASE/'results').glob('*.csv'))))

report['passed'] = all(c['ok'] for c in report['checks'])
(BASE/'verification_log.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
print('\nALL PASS' if report['passed'] else '\nSOME CHECKS FAILED')
sys.exit(0 if report['passed'] else 1)
