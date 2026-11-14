#!/usr/bin/env python3
"""Expand unexplained investor shorthand in the editable IR without changing figures.

Preserves the source slide count, shapes and all numeric assumptions. Makes a
small label-font adjustment where expansion needs room. Idempotent and checkable.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt


MAPPING = {
    "경제적 BEP": "경제적 손익분기점",
    "현금 BEP": "현금 손익분기점",
    "월 BEP": "월 손익분기점",
    "BEP": "손익분기점",
    "P0": "0단계",
    "P1": "1단계",
    "P2": "2단계",
    "P3": "3단계",
}
BAD = re.compile(r"R\s*-\s*0[1-6]|\b[GP][0-3]\b|\b(?:BEP|CAC)\b")


def all_text(presentation):
    return "\n".join(
        s.text for slide in presentation.slides for s in slide.shapes
        if s.has_text_frame
    )


def validate(presentation):
    if len(presentation.slides) != 12:
        raise AssertionError("IR must have 12 editable slides")
    text = all_text(presentation)
    if BAD.search(text):
        raise AssertionError("Unexpanded investor shorthand")
    for figure in ("199", "433", "541", "1,082", "3,700", "400"):
        if figure not in text:
            raise AssertionError(f"Missing original business assumption: {figure}")
    if text.count("손익분기점") < 6 or text.count("단계") < 7:
        raise AssertionError("IR descriptive labels not retained")
    for idx in (9, 16, 23, 30):
        sh = presentation.slides[8].shapes[idx]
        if sh.width < Inches(.78):
            raise AssertionError("Expanded stage badge may be clipped")
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", type=Path,
                        default=Path("downloads/MOSIGO_IR_Investment_Review_12slides.pptx"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    p = Presentation(args.path)
    if not args.check:
        original = all_text(p)
        expected = {v for v in ("BEP","P0","P1","P2","P3") if v in original}
        if not expected:
            raise AssertionError("Expected legacy shorthand before normalization")
        for slide in p.slides:
            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        text = run.text
                        for short, expanded in MAPPING.items():
                            text = re.sub(r"\b" + re.escape(short) + r"\b", expanded, text)
                        run.text = text
        for index in (9,16,23,30):
            badge = p.slides[8].shapes[index]
            badge.width = Inches(.80)
            for para in badge.text_frame.paragraphs:
                for run in para.runs:
                    run.font.size = Pt(15)
        validate(p)
        p.save(args.path)
    verify = Presentation(args.path)
    validate(verify)
    print("PASS IR 12 slides: descriptive stage and break-even labels, all financial values retained")


if __name__ == "__main__":
    main()
