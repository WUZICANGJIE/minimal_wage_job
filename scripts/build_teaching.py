"""Extract Japanese speaking notes and optional Q&A; no numerical work."""
from pathlib import Path
import re
import sys

BASE = Path(__file__).resolve().parent
ROOT = BASE.parent


def build(source):
    body = source.read_text().split('---', 2)[2]
    pages = re.split(r'^---\s*$', body, flags=re.M)
    out = ['# 逐頁の講解メモ\n\n各頁の本文は発表用。「質疑用」は質問が出たときに参照する補足。\n']
    for i, page in enumerate(pages, 1):
        heading = re.search(r'^# (.+)$', page, re.M)
        notes = re.findall(r'<!-- notes: (.*?) -->', page, re.S)
        qa = re.findall(r'<!-- qa: (.*?) -->', page, re.S)
        if heading is None or len(notes) != 1:
            raise ValueError(f'{source}: slide {i} needs one heading and one note')
        if len(qa) > 1:
            raise ValueError(f'{source}: slide {i} has multiple Q&A blocks')
        out.append(f'## {i}頁｜{heading.group(1)}\n\n{notes[0]}\n')
        if qa:
            qa_text = qa[0].replace('\nA：', '\n\nA：')
            out.append(f'### 質疑用\n\n{qa_text}\n')
    source.with_name('speaker_notes.md').write_text('\n'.join(out))
    print(f'{source.parent}: {len(pages)} page notes with optional Q&A; no statistics or figures rebuilt.')


if __name__ == '__main__':
    sources = [Path(p).resolve() for p in sys.argv[1:]] or [
        ROOT / '2026-11-04/slides.md'
    ]
    for source in sources:
        build(source)
