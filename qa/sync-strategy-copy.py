"""Synchronize the positive, evidence-led MOSIGO presentation copy.

Change only matching text runs, preserving slide layout and original formatting.
Idempotent when the presentation has already been synchronized.
"""
from pathlib import Path
from pptx import Presentation

file = Path("downloads/mosigo_report.pptx")
prs = Presentation(file)
assert len(prs.slides) == 11

updates = {
    1: {
        "제휴형 우선 검토, 획득비·운영비·공급 조건 검증 전 확대 보류":
        "제휴형 우선 · 획득비·운영비·공급 조건을 확대 기준으로 설정",
    },
    2: {
        "기존 7종·118건 팀 조사":
        "경쟁 앱 7종·리뷰 118건",
        "출처 · MOSIGO 사업기획서 3쪽의 팀 조사 기록 / 원문·수집 기준 추가 확인":
        "분석 자료 · 경쟁 앱 7종·리뷰 118건(기존 팀 조사) / 사업기획서 3쪽",
    },
    5: {
        "정성 비교 / 비용 우위는 계약 견적·운영 자료 확보 후 판단":
        "정성 비교 기준 · 계약 견적·운영 자료",
    },
    10: {
        "실행 전 제안 기준 / 모집 수·관찰 기간·비용 한도는 착수 전 확정":
        "추진 기준 · 대상·기간·비용 한도 설정",
    },
    11: {
        "제휴형 우선 검토 · 월 199건 대비 손익분기 1,082건":
        "제휴형 우선 · 월 199건(가정) / 손익분기 1,082건",
        "현재 결정 · 획득비·운영비·공급 조건 검증 전 확대 보류":
        "현재 방향 · 제휴형 집중, 획득비·운영비·공급 조건을 확대 기준으로 설정",
        "재검토 조건 · 공급·책임 합의 미충족 시 범위·계약 조정":
        "추진 기준 · 공급 가용성과 책임 분담에 맞춰 범위·계약 조정",
    },
}
changes = 0
for slide_num, edits in updates.items():
    slide = prs.slides[slide_num-1]
    for old, new in edits.items():
        hits = 0
        for shape in slide.shapes:
            frames = [shape.text_frame] if shape.has_text_frame else []
            if shape.has_table:
                frames.extend(cell.text_frame for row in shape.table.rows for cell in row.cells)
            for frame in frames:
                for paragraph in frame.paragraphs:
                    for run in paragraph.runs:
                        if old in run.text:
                            run.text = run.text.replace(old, new)
                            changes += 1
                            hits += 1
                        elif new in run.text:
                            hits += 1
        assert hits == 1, f"Slide {slide_num}: expected one text occurrence of {old!r}; got {hits}"
if changes:
    prs.save(file)

check = Presentation(file)
for slide_num, edits in updates.items():
    slide = check.slides[slide_num-1]
    text = "\n".join(
        [shape.text for shape in slide.shapes if shape.has_text_frame] +
        [cell.text for shape in slide.shapes if shape.has_table for row in shape.table.rows for cell in row.cells]
    )
    for new in edits.values():
        assert new in text, f"Slide {slide_num}: missing updated text {new!r}"

print(f"PASS MOSIGO neutral slide copy: {changes} updated runs; 11 editable slides retained")
