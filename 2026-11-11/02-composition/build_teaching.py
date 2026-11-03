"""Extract Japanese speaker notes for either week's slides; no numerical work."""
from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[1]


def build(source):
    body = source.read_text().split('---', 2)[2]
    pages = re.split(r'^---\s*$', body, flags=re.M)
    out = ['# 逐頁の講解メモ\n\nslides.md内の非表示speaker notesから生成。発表時の補助。\n']
    for i, page in enumerate(pages, 1):
        heading = re.search(r'^# (.+)$', page, re.M)
        notes = re.findall(r'<!-- notes: (.*?) -->', page, re.S)
        if heading is None or len(notes) != 1:
            raise ValueError(f'{source}: slide {i} needs one heading and one note')
        out.append(f'## {i}頁｜{heading.group(1)}\n\n{notes[0]}\n')
    source.with_name('speaker_notes.md').write_text('\n'.join(out))
    print(f'{source.parent}: {len(pages)} page notes; no statistics or figures rebuilt.')


if __name__ == '__main__':
    sources = [Path(p).resolve() for p in sys.argv[1:]] or [
        ROOT / '2026-11-04/02-composition/slides.md', BASE / 'slides.md'
    ]
    for source in sources:
        build(source)
