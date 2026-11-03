"""Check the current deck, archived deck and preservation hashes without estimation.

Requires Python standard library plus Poppler's pdfinfo/pdftotext on PATH.
This checks structure and exported text; inspect rendered pages separately.
For current statistical validation, use 2026-11-11/analysis/verify.py instead.
"""
from html.parser import HTMLParser
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent
ARCHIVE = ROOT / 'archive/2026-11-11-two-period-did'
report = {'scope': 'current monthly DID methods and separately preserved two-period results',
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


def inspect_deck(date, count, directory):
    source = (directory / 'slides.md').read_text()
    pages = re.split(r'^---\s*$', source.split('---', 2)[2], flags=re.M)
    check(date + ' Markdown page count', len(pages) == count, len(pages))
    note_groups = [re.findall(r'<!-- notes: (.*?) -->', p, re.S) for p in pages]
    check(date + ' one note per slide', all(len(n) == 1 for n in note_groups))
    notes = (directory / 'speaker_notes.md').read_text()
    check(date + ' notes match source',
          len(re.findall(r'^## \d+頁', notes, re.M)) == count
          and all(len(n) == 1 and n[0] in notes for n in note_groups))
    qa_groups = [re.findall(r'<!-- qa: (.*?) -->', p, re.S) for p in pages]
    compact_notes = ''.join(notes.split())
    check(date + ' Q&A separated and preserved in notes',
          all(len(q) <= 1 for q in qa_groups)
          and len(re.findall(r'^### 質疑用$', notes, re.M)) == sum(bool(q) for q in qa_groups)
          and all(''.join(q[0].split()) in compact_notes for q in qa_groups if q))
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
    check(date + ' Q&A kept off presentation pages', 'Q：' not in text and '質疑用' not in text)
    check(date + ' correct cover date', ('2026年11月4日' if date.endswith('04') else '2026年11月11日') in text)
    if date.endswith('04'):
        forbidden = ['−1.56', '-1.56', '−2.23', '−14.80', '0.310', '0.374', '0.068', '3.26', '6.39%', '7.78%',
                     'observed_trends', 'part_interval_teaching', 'model_illustration_NOT_ESTIMATED']
        check(date + ' no empirical results or numerical illustration',
              not any(token in source or token in text for token in forbidden))
        check(date + ' model and monthly fixed-effects regression present',
              all(token in source for token in ['CES', 'H_0:\\delta^P',
                  'y_{it}^j=\\alpha_i^j+\\lambda_t^j',
                  '\\delta^j(\\mathrm{Treat}_i\\times\\mathrm{Post}_t)',
                  '\\delta^P<0', '# パート求人への影響とその含意',
                  '\\delta^R=\\delta^P-\\delta^N']))
        check(date + ' monthly observations and fixed comparison window',
              '一県×一か月を1観測' in source and '2025年1〜9月と11月' in source
              and '10月は移行月として除く' in source
              and '一県につき前期・後期の2観測' not in source)
        page14_visible = re.sub(r'<!--.*?-->', '', pages[13], flags=re.S)
        check(date + ' part-focused hypothesis and implications on page 14',
              all(token in page14_visible for token in [
                  'H_0:\\delta^P', 'H_1:\\delta^P<0', '\\delta^P<0\\leq\\delta^N',
                  '\\delta^P<\\delta^N<0', '\\delta^N\\leq\\delta^P<0'])
              and '平行トレンド仮定' not in page14_visible and '非有意' not in page14_visible
              and '平行トレンド仮定' in notes)
        deferred = (ROOT / '2026-11-11/analysis/parallel_trends.md').read_text()
        check(date + ' detailed pretrend material moved to next week',
              all(token in deferred for token in [
                  '\\sum_{m\\in\\mathcal K}\\theta_m', '\\theta_9=0',
                  'H_0:\\theta_1=\\cdots=\\theta_8=0', '県クラスタのWald検定',
                  '平行トレンド仮定', '基準月と主DIDの区別']))
        check(date + ' ends with references without supplemental slide',
              '# 参考文献・データ' in pages[-1]
              and '補足：県クラスタ標準誤差と検定' not in source)
    else:
        check(date + ' legacy two-period regression preserved separately',
              'Y_{it}^P=\\alpha^P+\\beta^P\\mathrm{Treat}_i+\\gamma^P\\mathrm{Post}_t' in source
              and '\\delta^P(\\mathrm{Treat}_i\\times\\mathrm{Post}_t)' in source
              and 'H_0:\\delta^P' in source)
        check(date + ' deferred results retained',
              all(token in text for token in ['−1.56', '−2.23', '−14.80', 'Welch']))


for date, count, directory in [('2026-11-04', 15, ROOT / '2026-11-04'),
                               ('archived 2026-11-11', 13, ARCHIVE)]:
    inspect_deck(date, count, directory)

protected = json.loads((ARCHIVE / 'evidence/split_protected_hashes.json').read_text())


def preserved_path(name):
    old_prefix = '2026-11-11/02-composition/'
    return ARCHIVE / name[len(old_prefix):] if name.startswith(old_prefix) else ROOT / name


changed = [p for p, h in protected.items()
           if not preserved_path(p).is_file() or hashlib.sha256(preserved_path(p).read_bytes()).hexdigest() != h]
check('analysis, notebook, CSVs, original figures, video and raw data unchanged', not changed,
      changed if changed else f'{len(protected)} files')
report['passed'] = all(c['ok'] for c in report['checks'])
output = ROOT / '.cache/delivery-check/verification.json'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(f'Report: {output.relative_to(ROOT)}')
print('ALL PASS' if report['passed'] else 'SOME CHECKS FAILED')
sys.exit(0 if report['passed'] else 1)
