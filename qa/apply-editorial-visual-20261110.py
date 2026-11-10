#!/usr/bin/env python3
"""Non-destructive MOSIGO slide visual-system pass (2026-11-10).

Keep original text, positions, tables, financial figures and image assets.
Only update table fills and add slender, off-content brand/progress rails.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Inches
FOREST = RGBColor(18, 62, 51)
INK = RGBColor(25, 44, 37)
GREEN = RGBColor(39, 116, 77)
LIME = RGBColor(214, 239, 138)
PALE = RGBColor(239, 247, 239)
ALTERNATE = RGBColor(249, 252, 248)
WHITE = RGBColor(255, 255, 255)
LINE = RGBColor(220, 231, 223)
MARKER = 'MOSIGO_VISUAL_REFRESH_20261110_'

def snapshot(prs):
    rows = []
    for slide in prs.slides:
        current = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                current.append(('text', shape.text))
            if shape.has_table:
                current.append(('table', tuple(tuple(cell.text for cell in row.cells) for row in shape.table.rows)))
        rows.append(tuple(current))
    return tuple(rows)

def apply_color_to_text(frame, color, bold=False):
    for paragraph in frame.paragraphs:
        for run in paragraph.runs:
            if run.text.strip():
                run.font.color.rgb = color
                if bold:
                    run.font.bold = True

def style_table(shape):
    for ri, row in enumerate(shape.table.rows):
        for ci, cell in enumerate(row.cells):
            cell.fill.solid()
            if ri == 0:
                fill, fg, bold = FOREST, WHITE, True
            elif ci == 0:
                fill, fg, bold = PALE, FOREST, True
            else:
                fill, fg, bold = (WHITE if ri % 2 else ALTERNATE), INK, False
            cell.fill.fore_color.rgb = fill
            apply_color_to_text(cell.text_frame, fg, bold)

def rectangle(slide, x, y, w, h, color, name):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, w, h)
    shape.name = name
    shape.fill.solid()
    shape.fill.fore_color.rgb = color
    shape.line.fill.background()

def enhance_slide(slide, index, total, kind, prs):
    if any(s.name.startswith(MARKER) for s in slide.shapes):
        return False
    for shape in slide.shapes:
        if shape.has_table:
            style_table(shape)
    width, height = prs.slide_width, prs.slide_height
    dark = (kind == 'service' and index in (1, 11)) or (kind == 'ir' and index in (1, 12))
    accent = LIME if dark else GREEN
    # Text positions and graphic areas are unchanged; rails occupy page edges.
    rectangle(slide, 0, 0, Inches(.055), height, accent, MARKER + 'left')
    rectangle(slide, 0, height - Inches(.045), width, Inches(.045), LINE if not dark else FOREST, MARKER + 'track')
    rectangle(slide, 0, height - Inches(.045), int(width * index / total), Inches(.045), accent, MARKER + 'progress')
    return True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='*', default=['downloads/mosigo_report.pptx', 'downloads/MOSIGO_IR_Investment_Review_12slides.pptx'])
    args = parser.parse_args()
    for name in args.paths:
        path = Path(name)
        kind = 'ir' if 'IR_Investment_' in path.name else 'service'
        total = 12 if kind == 'ir' else 11
        prs = Presentation(path)
        assert len(prs.slides) == total, f'{path}: unexpected page count'
        original = snapshot(prs)
        touched = sum(enhance_slide(s, i, total, kind, prs) for i, s in enumerate(prs.slides, 1))
        assert snapshot(prs) == original, f'{path}: original slide text changed'
        if touched:
            tmp = path.with_name(path.name + '.visual-tmp')
            prs.save(tmp)
            verified = Presentation(tmp)
            assert len(verified.slides) == total
            assert snapshot(verified) == original, f'{path}: original text changed on save'
            for slide in verified.slides:
                assert sum(s.name.startswith(MARKER) for s in slide.shapes) == 3
            tmp.replace(path)
        print(f'PASS {path}: {total} slides, {touched} refined, all original text and table values preserved')

if __name__ == '__main__':
    main()
