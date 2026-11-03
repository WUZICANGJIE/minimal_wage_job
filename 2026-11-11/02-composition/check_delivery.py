"""Check both weekly decks and preservation hashes without numerical estimation.

Requires Python standard library plus Poppler's pdfinfo/pdftotext on PATH.
This checks structure and exported text; inspect rendered pages separately.
For optional statistical replication next week, use check_analysis.py instead.
"""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]
report = {'scope': 'weekly decks with standard DID notation, structure and text',
          'numerical_estimation_executed': False, 'checks': []}


def check(name, ok, detail=''):
    report['checks'].append({'name': name, 'ok': bool(ok), 'detail': str(detail)})
    print(('PASS ' if ok else 'FAIL ') + name + (f': {detail}' if detail else ''))


class SlideHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sections = 0
        self.math_errors = 0

    def handle_starttag(self, tag, attrs):
        self.sections += tag == 'section'
        self.math_errors += 'katex-error' in dict(attrs).get('class', '').split()


def inspect_deck(date, count):
    directory = ROOT / date / '02-composition'
    source = (directory / 'slides.md').read_text()
    pages = re.split(r'^---\s*$', source.split('---', 2)[2], flags=re.M)
    check(date + ' Markdown page count', len(pages) == count, len(pages))
    note_groups = [re.findall(r'<!-- notes: (.*?) -->', p, re.S) for p in pages]
    check(date + ' one note per slide', all(len(n) == 1 for n in note_groups))
    notes = (directory / 'speaker_notes.md').read_text()
    check(date + ' notes match source',
          len(re.findall(r'^## \d+頁', notes, re.M)) == count
          and all(len(n) == 1 and n[0] in notes for n in note_groups))
    local_assets = re.findall(r'!\[[^\]]*\]\(([^)]+)\)', source)
    local_assets += re.findall(r'url\("([^\"]+)"\)', source)
    check(date + ' local assets exist', all((directory / p).is_file() for p in local_assets))
    parser = SlideHTML()
    parser.feed((directory / 'slides.html').read_text())
    check(date + ' HTML page count', parser.sections == count, parser.sections)
    check(date + ' no KaTeX errors', parser.math_errors == 0)
    info = subprocess.check_output(['pdfinfo', str(directory / 'slides.pdf')], text=True)
    pdf_count = int(re.search(r'^Pages:\s+(\d+)', info, re.M).group(1))
    check(date + ' PDF page count', pdf_count == count, pdf_count)
    text = subprocess.check_output(['pdftotext', '-layout', str(directory / 'slides.pdf'), '-'], text=True)
    check(date + ' PDF Japanese text present', '最低賃金' in text and 'パート' in text)
    check(date + ' PDF has no missing-glyph markers', '\ufffd' not in text and '\u25a1' not in text)
    check(date + ' PDF has no literal TeX', '$' not in text and 'mathcal' not in text and '\\begin{' not in text)
    check(date + ' correct cover date', ('2026年11月4日' if date.endswith('04') else '2026年11月11日') in text)
    if date.endswith('04'):
        forbidden = ['−1.56', '-1.56', '−2.23', '−14.80', '0.310', '6.39%', '7.78%',
                     'observed_trends', 'part_interval_teaching', 'model_illustration_NOT_ESTIMATED']
        check(date + ' no empirical results or numerical illustration',
              not any(token in source or token in text for token in forbidden))
        check(date + ' model and regression methods present',
              all(token in source for token in ['CES', 'H_0:\\delta^P',
                  'Y_{it}^j=\\alpha^j+\\beta^j\\mathrm{Treat}_i+\\gamma^j\\mathrm{Post}_t',
                  '\\delta^j(\\mathrm{Treat}_i\\times\\mathrm{Post}_t)',
                  '(\\bar Y_{E1}^j-\\bar Y_{E0}^j)-(\\bar Y_{L1}^j-\\bar Y_{L0}^j)']))
        check(date + ' paired periods and differenced intercept explained',
              '一県につき前期・後期の2観測' in source
              and 'd_i^j=\\gamma^j+\\delta^j\\mathrm{Treat}_i+u_i^j' in pages[-1]
              and '同じ県の2観測を独立とは扱わず' in pages[-1])
        check(date + ' inference formulas in final appendix',
              '補足：回帰係数の標準誤差と検定' in pages[-1]
              and 'SE(\\widehat{\\delta}^j)' in pages[-1]
              and 'F_\\nu(t)' in pages[-1]
              and 'F_\\nu(t)' not in '\n'.join(pages[:-1]))
    else:
        check(date + ' regression notation aligned with current week',
              'Y_{it}^P=\\alpha^P+\\beta^P\\mathrm{Treat}_i+\\gamma^P\\mathrm{Post}_t' in source
              and '\\delta^P(\\mathrm{Treat}_i\\times\\mathrm{Post}_t)' in source
              and 'H_0:\\delta^P' in source)
        check(date + ' deferred results retained',
              all(token in text for token in ['−1.56', '−2.23', '−14.80', 'Welch']))


for date, count in [('2026-11-04', 17), ('2026-11-11', 13)]:
    inspect_deck(date, count)

protected = json.loads((BASE / 'evidence/split_protected_hashes.json').read_text())
changed = [p for p, h in protected.items()
           if not (ROOT / p).is_file() or hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h]
check('analysis, notebook, CSVs, original figures, video and raw data unchanged', not changed,
      changed if changed else f'{len(protected)} files')
report['passed'] = all(c['ok'] for c in report['checks'])
(BASE / 'verification_log.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('ALL PASS' if report['passed'] else 'SOME CHECKS FAILED')
sys.exit(0 if report['passed'] else 1)
