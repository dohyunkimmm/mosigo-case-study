"""Concise editorial pass for MOSIGO's 12-slide IR review deck.

Only replaces specifically reviewed copy, preserving paragraph style and all slide layout.
"""
import json
from pathlib import Path
from pptx import Presentation
import sys

path = Path(sys.argv[1] if len(sys.argv) > 1 else "downloads/MOSIGO_IR_Investment_Review_12slides.pptx")
mapping = json.loads(Path("qa/concise-ir-copy.json").read_text(encoding="utf-8"))
prs = Presentation(path)
assert len(prs.slides) == 12
edited = 0
already = 0

for n, pairs in mapping.items():
    slide = prs.slides[int(n)-1]
    for old, new in pairs:
        original = [s for s in slide.shapes if s.has_text_frame and s.text == old]
        if not original and any(s.has_text_frame and s.text == new for s in slide.shapes):
            already += 1
            continue
        assert len(original) == 1, f"Slide {n} missing expected IR copy: {old!r}"
        paragraphs = original[0].text_frame.paragraphs
        newparts = new.split("\n")
        assert len(paragraphs) == len(newparts), f"Slide {n} paragraph structure changed"
        for p, value in zip(paragraphs, newparts):
            assert p.runs or not value
            if p.runs:
                p.runs[0].text = value
                for r in p.runs[1:]:
                    r.text = ""
        edited += 1

assert edited + already == 53, f"Missing IR editorial revision: {edited} changed, {already} already done"
assert edited > 0 or already == 53
prs.save(path)
check = Presentation(path)
assert len(check.slides) == 12
for num, pairs in mapping.items():
    current = {s.text for s in check.slides[int(num)-1].shapes if s.has_text_frame}
    for old,new in pairs:
        assert new in current, f"Slide {num} editorial review failed: {new!r}"
for slide_number, essential in {
    2:["199건","3,700원","1,082건","18.4%"],
    4:["238만 명","154만 명","1.5만 명","9억 원"],
    6:["40,000원","8,000원","1,200원","1,800원","3,700원"],
    7:["199건","1,082건","3,700원","3,263,700원"],
    9:["80만 원","120만 원","200만 원","400만 원"],
    10:["400만 원","800만 원","126.4만 원"],
    12:["199건","1,082건","400만 원"]
}.items():
    text = "\n".join(s.text for s in check.slides[slide_number-1].shapes if s.has_text_frame)
    for value in essential:
        assert value in text, f"Slide {slide_number} key IR value changed: {value}"
print(f"PASS concise MOSIGO IR copy: {edited} updated, {already} already reviewed; 12 slides and key figures retained")
