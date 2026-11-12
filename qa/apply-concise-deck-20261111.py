#!/usr/bin/env python3
"""Small, idempotent copy edits in the existing editable MOSIGO slide decks.

Run after the established formatting and content pipeline; preserve slide
counts, geometry, financial tables, pictures, and charts.
"""
from pathlib import Path
import sys
from pptx import Presentation

PATHS = {
    "strategy": Path("downloads/mosigo_report.pptx"),
    "ir": Path("downloads/MOSIGO_IR_Investment_Review_12slides.pptx"),
}
COPY = {
    "strategy": {
        6: [("예약 → 진행 공유 → 재이용까지 연결",
             "공유·변경 권한은 운영 검증 후 확정")],
        7: [("사용자 문제 → 기능 정의 → 화면 정책 → 후속 검증",
             "동의·상태 복구는 과업 테스트로 확인")],
        10: [("사용자 과업과 기능 우선순위를 단계별로 구체화",
              "단계별 검증 결과에 따라 기능 범위를 조정")],
    },
    "ir": {
        4: [("약 154만 명", "재산정 필요"),
            ("기존 지역 추정치", "종전 약 154만 명")],
        12: [("검증 단계별 통과 조건에 따라 승인·보류 결정",
              "8주 제한 검증 승인 여부 결정"),
             ("수요·공급 검증 → 책임 조건 합의 → 투자 재심의",
              "확대 투자는 수요·공급·손익 실측 후 별도 심의")],
    },
}

def frames(slide):
    for shape in slide.shapes:
        if shape.has_text_frame:
            yield shape.text_frame
        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    yield cell.text_frame

def replace_paragraph(tf, old, new):
    hits = 0
    for p in tf.paragraphs:
        chunks = [r.text for r in p.runs]
        original = "".join(chunks)
        if old not in original:
            continue
        if any(old in t for t in chunks):
            for r in p.runs:
                if old in r.text:
                    r.text = r.text.replace(old, new)
        else:
            assert p.runs, old
            p.runs[0].text = original.replace(old, new)
            for r in p.runs[1:]:
                r.text = ""
        hits += 1
    return hits

def chart_snapshot(prs):
    return [tuple(tuple(series.values) for series in sh.chart.series)
            for slide in prs.slides for sh in slide.shapes if sh.has_chart]

def image_count(prs):
    return sum(sh.shape_type == 13 for slide in prs.slides for sh in slide.shapes)

def main(mode):
    path = PATHS[mode]
    prs = Presentation(path)
    nslides = 11 if mode == "strategy" else 12
    assert len(prs.slides) == nslides
    charts = chart_snapshot(prs)
    images = image_count(prs)
    updated = 0
    skipped = 0
    for page, changes in COPY[mode].items():
        for old, new in changes:
            if any(new in tf.text for tf in frames(prs.slides[page - 1])):
                skipped += 1
                continue
            count = sum(replace_paragraph(tf, old, new)
                        for tf in frames(prs.slides[page - 1]))
            assert count == 1, f"{mode} page {page}: expected one {old!r}, found {count}"
            updated += count
    assert updated + skipped == sum(map(len, COPY[mode].values()))
    assert chart_snapshot(prs) == charts and image_count(prs) == images
    if updated:
        prs.save(path)
    check = Presentation(path)
    assert len(check.slides) == nslides
    assert chart_snapshot(check) == charts and image_count(check) == images
    for page, changes in COPY[mode].items():
        texts = "\n".join(tf.text for tf in frames(check.slides[page-1]))
        for _, new in changes:
            assert new in texts, f"{mode} page {page}: revised copy missing"
    essentials = ["199건", "3,700원", "1,082건"]
    joined = "\n".join(tf.text for sl in check.slides for tf in frames(sl))
    for value in essentials:
        assert value in joined, f"Essential planning assumption missing: {value}"
    print(f"PASS {mode}: {updated} revised, {skipped} already present; {nslides} slides")

if __name__ == "__main__":
    assert len(sys.argv) == 2 and sys.argv[1] in PATHS
    main(sys.argv[1])
