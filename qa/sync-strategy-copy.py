"""Keep PPT conclusions aligned with the quantified MOSIGO strategy decision.

Edits only existing editable text runs on slides 1 and 11; preserves design.
Run from repository root after python-pptx is installed.
"""
from pathlib import Path
from pptx import Presentation

file = Path("downloads/mosigo_report.pptx")
prs = Presentation(file)
assert len(prs.slides) == 11
updates = {
    1: {
        "기존 사업자 제휴로 범위 한정, 획득비·운영비 확인 후 확대 판단":
        "제휴형 우선 검토, 획득비·운영비·공급 조건 검증 전 확대 보류",
    },
    11: {
        "제휴형으로 범위를 좁히고 획득비·운영비부터 확인":
        "제휴형 우선 검토 · 월 199건 대비 손익분기 1,082건",
        "현재 결정 · 제휴 조건·고객 과업·운영 원가 확인 우선":
        "현재 결정 · 획득비·운영비·공급 조건 검증 전 확대 보류",
    },
}
changes = 0
for slide_num, edits in updates.items():
    slide = prs.slides[slide_num-1]
    for old, new in edits.items():
        count = 0
        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue
            for paragraph in shape.text_frame.paragraphs:
                for run in paragraph.runs:
                    if run.text == old:
                        run.text = new
                        changes += 1
                        count += 1
                    elif run.text == new:
                        count += 1
        assert count == 1, f"Slide {slide_num}: expected one matching text run: {old}"
if changes:
    prs.save(file)
check = Presentation(file)
for slide_num, edits in updates.items():
    text = "\n".join(sh.text for sh in check.slides[slide_num-1].shapes if sh.has_text_frame)
    for new in edits.values():
        assert new in text, f"Slide {slide_num}: failed to preserve update {new}"
print(f"PASS strategic decision slide sync: {changes} edited runs, 11 editable slides retained")
