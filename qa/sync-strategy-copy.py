"""Synchronize reviewed Korean copy across the editable MOSIGO presentation.

Text edits preserve the existing slide count and formatting where a phrase stays
inside one PowerPoint run. If a phrase crosses runs, the paragraph is consolidated
into its first run so the replacement remains complete and readable.
"""
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

file = Path("downloads/mosigo_report.pptx")
prs = Presentation(file)
assert len(prs.slides) == 11, "Expected the existing 11-slide presentation"


def iter_frames(shapes):
    for shape in shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from iter_frames(shape.shapes)
        if shape.has_text_frame:
            yield shape.text_frame
        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    yield cell.text_frame


def paragraph_text(paragraph):
    return "".join(run.text for run in paragraph.runs)


def replace_paragraph(paragraph, old, new):
    runs = paragraph.runs
    current = paragraph_text(paragraph)
    count = current.count(old)
    if not count:
        return 0
    if count != 1:
        raise AssertionError(f"Phrase appears {count} times in one paragraph: {old!r}")
    start = current.index(old)
    offset = 0
    for run in runs:
        end = offset + len(run.text)
        if offset <= start and start + len(old) <= end:
            local = start - offset
            run.text = run.text[:local] + new + run.text[local + len(old):]
            return 1
        offset = end
    if not runs:
        raise AssertionError(f"Paragraph has no runs for {old!r}")
    runs[0].text = current.replace(old, new)
    for run in runs[1:]:
        run.text = ""
    return 1


def slide_paragraphs(slide):
    for frame in iter_frames(slide.shapes):
        for paragraph in frame.paragraphs:
            yield paragraph


def replace_on_slide(slide_number, old, new):
    slide = prs.slides[slide_number - 1]
    paragraphs = list(slide_paragraphs(slide))
    old_hits = sum(paragraph_text(p).count(old) for p in paragraphs)
    new_hits = sum(paragraph_text(p).count(new) for p in paragraphs)
    if old_hits:
        if old_hits != 1:
            raise AssertionError(f"Slide {slide_number}: expected one {old!r}; got {old_hits}")
        for paragraph in paragraphs:
            if old in paragraph_text(paragraph):
                replace_paragraph(paragraph, old, new)
                break
    elif new_hits != 1:
        raise AssertionError(f"Slide {slide_number}: expected one old/new phrase for {old!r}; got old={old_hits}, new={new_hits}")


def replace_everywhere(old, new):
    changed = 0
    existing = 0
    for slide in prs.slides:
        for paragraph in slide_paragraphs(slide):
            current = paragraph_text(paragraph)
            if old in current:
                changed += replace_paragraph(paragraph, old, new)
            elif new in current:
                existing += current.count(new)
    if changed + existing == 0:
        raise AssertionError(f"Expected repeated source phrase not found: {old!r}")
    return changed


updates = {
    1: {
        "자녀 대리 예약형 병원동행 서비스 기획": "자녀 대리 예약 기반 병원 동행 서비스 기획",
        "제휴형 우선 · 획득비·운영비·공급 조건을 확대 기준으로 설정": "기존 사업자 제휴 모델 우선 검토 · 고객 획득 비용·운영비·공급 조건을 확대 판단 기준으로 설정",
    },
    4: {
        "자녀 중심 여정을 선택하되 부모의 수용과 동의를 선행 조건으로 설정": "자녀 중심 예약 과정을 우선 검토하되 부모의 동의와 이용 수용성을 먼저 확인",
    },
    5: {
        "정성 비교 기준 · 계약 견적·운영 자료": "정성적 비교 결과 · 실제 계약 견적과 운영 자료 확보 후 판단",
    },
    7: {
        "제휴형 사업성은 공급 시간으로 검토": "제휴 모델의 사업성은 매니저 가용 시간으로 검토",
        "월 공급 가능 예약": "월 최대 처리 가능 건수",
        "가동·경유·취소·완료 반영": "가동률·플랫폼 이용 비율·취소율·완료율 반영",
        "수수료 매출 / 공헌이익": "수수료 매출 / 건당 공헌이익",
        "노동비용 포함 손익": "인력 투입 비용 반영 월 손익",
    },
    8: {
        "수요·초기 공급·손익분기를 같은 기간으로 비교": "수요·초기 공급·손익분기점을 월 기준으로 비교",
        "노동비용 포함 손익분기": "인력 투입 비용 반영 손익분기점",
        "초기 공급은 수요 가정의 약 10.6% / 손익분기에 완료 건수 약 5.4배 필요": "초기 공급은 예상 수요의 약 10.6% / 손익분기점 달성에는 현재 완료 건수의 약 5.4배 필요",
        "동일 생산성 기준 총 매니저 약 109명 필요, 공급 확대 전 획득비·지원비 개선": "현재 생산성이 유지된다고 가정하면 매니저 약 109명이 필요하므로, 공급 확대 전에 고객 획득 비용과 고객 지원 비용을 개선해야 함",
    },
    9: {
        "직접 잔여액은 지원·획득비 차감 전 / 구독 전 회차 사용 / 차량 원가 가정": "직접 운영 모델의 잔여 금액은 고객 지원 비용·고객 획득 비용 차감 전 / 구독은 월 3회 모두 이용하는 경우 / 차량 원가는 가정치",
        "직접 잔여액": "직접 운영 모델의 건당 잔여 금액",
    },
    10: {
        "G3 사업": "G3 시범 운영",
        "건당 이익·손익분기와 공급 계획 재심사": "건당 공헌이익·손익분기점·공급 계획 재검토",
    },
    11: {
        "제휴형 우선 · 월 199건(가정) / 손익분기 1,082건": "기존 사업자 제휴 모델 우선 검토 · 월 서비스 완료 199건(가정) / 손익분기점 1,082건",
        "현재 방향 · 제휴형 집중, 획득비·운영비·공급 조건을 확대 기준으로 설정": "현재 방향 · 기존 사업자 제휴 모델 검토, 고객 획득 비용·운영비·공급 조건을 확대 판단 기준으로 설정",
        "확대 조건 · 안전·권한 검수 통과와 노동비용 포함 손익 개선": "확대 조건 · 안전·권한 검수 통과와 인력 투입 비용 반영 손익 개선",
        "추진 기준 · 공급 가용성과 책임 분담에 맞춰 범위·계약 조정": "추진 기준 · 공급 가능 지역·시간과 책임 분담에 맞춰 운영 범위·계약 조정",
        "구독 판단 · 재예약 효과와 고객 획득비 절감 함께 비교": "구독 판단 · 재예약 효과와 고객 획득 비용 절감 효과를 함께 비교",
    },
}
changes = 0
for slide_number, edits in updates.items():
    for old, new in edits.items():
        replace_on_slide(slide_number, old, new)
        changes += 1

disclaimer_changes = replace_everywhere(
    "포트폴리오용 합성 데이터·가정 기반 예측입니다. 실제 고객·계약·매출·인터뷰 결과가 아닙니다.",
    "가정 기반 시나리오 분석이며 실제 운영 실적이 아닙니다.",
)
source_note_changes = replace_everywhere(
    "해당 사례의 독립 분석 자료. 계산 파일: mosigo_model.xlsx. 시장·고객 근거의 출처와 한계는 원본 케이스 스터디에 표시.",
    "자료·계산 근거: 원본 케이스 스터디 및 mosigo_model.xlsx.",
)

prs.save(file)
check = Presentation(file)
assert len(check.slides) == 11
for slide_number, edits in updates.items():
    text = "\n".join(paragraph_text(p) for p in slide_paragraphs(check.slides[slide_number - 1]))
    for new in edits.values():
        assert new in text, f"Slide {slide_number}: missing updated phrase {new!r}"
for slide in check.slides:
    text = "\n".join(paragraph_text(p) for p in slide_paragraphs(slide))
    assert "포트폴리오용 합성 데이터·가정 기반 예측" not in text
    assert "해당 사례의 독립 분석 자료" not in text
print(f"PASS Korean copy revision: {changes} slide edits, {disclaimer_changes} concise disclaimers, {source_note_changes} concise source notes; 11 editable slides retained")
