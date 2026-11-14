#!/usr/bin/env python3
"""Repair two overlapping MOSIGO source slides without changing their wording.

The long service-journey and pilot-timeline text boxes extended across other
cards. Later card fills painted over earlier text when PowerPoint/LibreOffice
rendered the editable deck. Only widths and a few text font sizes are changed.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from pptx import Presentation
from pptx.util import Inches, Pt


def text_snapshot(presentation):
    return [
        [shape.text for shape in slide.shapes if shape.has_text_frame]
        for slide in presentation.slides
    ]


def repair(presentation, check: bool = False):
    if len(presentation.slides) != 11:
        raise AssertionError("Expected the reviewed 11-slide editable service deck")
    slides = presentation.slides
    assert slides[4].shapes[2].text == "부모님 병원 동행 예약 여정"
    assert slides[9].shapes[2].text == "운영 지표를 언제 확인할 것인가"

    rules = []
    for indices in (range(11, 15), range(16, 20), range(21, 25), range(26, 30)):
        for i in indices:
            rules.append((4, i, Inches(2.43), None if i == indices.start else Pt(12.3)))
    for i in (11, 17, 23):
        rules.append((9, i, Inches(3.35), None))
    for i in list(range(14, 17)) + list(range(20, 23)) + list(range(26, 29)):
        label = i in (14, 20, 26)
        desc = slides[9].shapes[i].text
        rules.append((9, i, Inches(3.00), Pt(17.5) if label else Pt(11.3) if len(desc) > 17 else None))

    for page, idx, width, font_size in rules:
        shape = slides[page].shapes[idx]
        if not shape.has_text_frame or not shape.text.strip():
            raise AssertionError(f"Unexpected shape or empty text on slide {page+1}, shape {idx}")
        if check:
            assert abs(shape.width - width) < 10000, (
                f"Slide {page+1} textbox {idx} extends beyond its card: {shape.width}"
            )
            if font_size is not None:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        assert run.font.size == font_size, (
                            f"Slide {page+1} font {idx} out of sync"
                        )
        else:
            shape.width = width
            if font_size is not None:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        run.font.size = font_size


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("presentation", type=Path, nargs="?", default=Path("downloads/mosigo_report.pptx"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    p = Presentation(args.presentation)
    before = text_snapshot(p)
    repair(p, check=args.check)
    assert before == text_snapshot(p), "Slide text must not change"
    if not args.check:
        p.save(args.presentation)
        assert before == text_snapshot(Presentation(args.presentation)), "PPTX roundtrip changed text"
    print("PASS: editable deck card text within bounds, exact text preserved, 11 slides")


if __name__ == "__main__":
    main()
