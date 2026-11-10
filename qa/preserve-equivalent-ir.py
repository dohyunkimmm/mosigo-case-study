#!/usr/bin/env python3
"""Prevent metadata-only IR asset updates without hiding real changes.

Both the editable slide package contents and every rendered PDF page must match
before replacing new outputs with the repository's existing, reviewed bytes.
"""
from __future__ import annotations

import argparse
import io
import subprocess
import tempfile
from pathlib import Path
from zipfile import ZipFile

ROOT = Path('downloads')
PPTX = 'MOSIGO_IR_Investment_Review_12slides.pptx'
PDF = 'MOSIGO_IR_Investment_Review_12slides.pdf'


def repository_bytes(path: Path) -> bytes | None:
    result = subprocess.run(['git', 'show', 'HEAD:' + path.as_posix()], capture_output=True)
    return result.stdout if result.returncode == 0 else None


def same_pptx_payload(old: bytes, new: bytes) -> bool:
    with ZipFile(io.BytesIO(old)) as left, ZipFile(io.BytesIO(new)) as right:
        if left.testzip() or right.testzip():
            raise ValueError('Damaged PowerPoint archive')
        left_names, right_names = sorted(left.namelist()), sorted(right.namelist())
        return left_names == right_names and all(left.read(n) == right.read(n) for n in left_names)


def check_pdf_pages(old: bytes, new: bytes, pages: int = 12) -> bool:
    with tempfile.TemporaryDirectory(prefix='mosigo-ir-compare-') as tmp:
        a, b = Path(tmp) / 'before.pdf', Path(tmp) / 'after.pdf'
        a.write_bytes(old)
        b.write_bytes(new)
        def output(*cmd):
            return subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        def page_count(file):
            import re
            info = output('pdfinfo', str(file)).decode('utf-8', 'replace')
            m = re.search(r'^Pages:\s*(\d+)\s*$', info, flags=re.MULTILINE)
            if not m:
                raise ValueError(f'Cannot determine PDF page count for {file}')
            return int(m.group(1))
        if page_count(a) != pages or page_count(b) != pages:
            return False
        if output('pdftotext', '-layout', str(a), '-') != output('pdftotext', '-layout', str(b), '-'):
            return False
        for page in range(1, pages + 1):
            image_a = Path(tmp) / 'before-page'
            image_b = Path(tmp) / 'after-page'
            for src, stem in ((a, image_a), (b, image_b)):
                subprocess.run([
                    'pdftoppm', '-f', str(page), '-l', str(page),
                    '-scale-to', '1200', '-gray', '-singlefile', str(src), str(stem)
                ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            if image_a.with_suffix('.pgm').read_bytes() != image_b.with_suffix('.pgm').read_bytes():
                return False
        return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseline-dir', type=Path)
    parser.add_argument('--generated-dir', type=Path, default=ROOT)
    args = parser.parse_args()
    pptx = args.generated_dir / PPTX
    pdf = args.generated_dir / PDF
    if not pptx.is_file() or not pdf.is_file():
        raise FileNotFoundError('Regenerated IR deliverables must both exist')
    before_pptx = ((args.baseline_dir / PPTX).read_bytes() if args.baseline_dir else repository_bytes(ROOT / PPTX))
    before_pdf = ((args.baseline_dir / PDF).read_bytes() if args.baseline_dir else repository_bytes(ROOT / PDF))
    if before_pptx is None or before_pdf is None:
        print('No checked-in IR baseline available; keeping generated deliverables.')
        return
    equal_packages = same_pptx_payload(before_pptx, pptx.read_bytes())
    if not equal_packages:
        print('IR editable slide content changed; preserving regenerated deliverables for review.')
        return
    equal_pages = check_pdf_pages(before_pdf, pdf.read_bytes())
    if not equal_pages:
        print('IR PDF page text or rendered appearance changed; preserving generated deliverables for review.')
        return
    pptx.write_bytes(before_pptx)
    pdf.write_bytes(before_pdf)
    print('PASS IR: 12 PDF pages and all editable slide package payloads identical; restored original bytes.')


if __name__ == '__main__':
    main()
