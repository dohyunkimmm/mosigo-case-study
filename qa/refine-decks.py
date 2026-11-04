"""Targeted editorial and layout polish for both MOSIGO editable PPTX decks.

Run after existing source normalization. Preserve the established design, slide count,
case-study provenance and all financial formulas. This script is repeatable.
"""
from pathlib import Path
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE_TYPE

MODE = sys.argv[1] if len(sys.argv) > 1 else "strategy"
FILES = {
    "strategy": ("downloads/mosigo_report.pptx", 11),
    "ir": ("downloads/MOSIGO_IR_Investment_Review_12slides.pptx", 12),
}
assert MODE in FILES, MODE
path, expected = FILES[MODE]
prs = Presentation(path)
assert len(prs.slides) == expected
changes = []

def frames(slide):
    for sh in slide.shapes:
        if sh.has_text_frame:
            yield (sh, sh.text_frame)
        if sh.has_table:
            for row in sh.table.rows:
                for cell in row.cells:
                    yield (sh, cell.text_frame)

def replace(slide_no, old, new, required=True):
    slide = prs.slides[slide_no - 1]
    hits = 0
    already = 0
    for sh, frame in frames(slide):
        for para in frame.paragraphs:
            text = "".join(r.text for r in para.runs)
            if old in text:
                hits += text.count(old)
                if para.runs:
                    if any(old in r.text for r in para.runs):
                        for r in para.runs:
                            if old in r.text:
                                r.text = r.text.replace(old, new)
                    else:
                        para.runs[0].text = text.replace(old, new)
                        for r in para.runs[1:]: r.text = ""
            elif new in text:
                already += 1
    if required:
        assert hits == 1 or (hits == 0 and already >= 1), (MODE, slide_no, old, hits, already)
    if hits: changes.append((slide_no, old, new))

if MODE == "strategy":
    replace(7, "공급 가용 시간과 실제 완료량을 함께 관리",
            "최대 공급 433건·예상 완료 199건·현금 BEP 541건을 함께 비교")
    replace(8, "월 완료 199건은 손익분기점 1,082건의 18.4%입니다. 수요·공급·비용을 실측해 확대 시점을 판단합니다.",
            "예상 완료 199건은 경제적 BEP 1,082건의 18.4%입니다. 실측 결과로 확대 시점을 판단합니다.")
    replace(8, "현재 생산성이 유지된다고 산정 기준하면 매니저 약 109명이 필요합니다. 따라서 공급을 확대하기 전에 고객 획득 비용과 고객 지원 비용을 개선해야 합니다.",
            "동일 생산성·고정비 기준 약 109명에 해당합니다. 확대 시에는 고객 획득·지원 비용 변화도 반영합니다.")
    replace(8, "초기 공급 199건  /  손익분기점 1,082건  ·  18.4%",
            "예상 199건  /  현금 BEP 541건  /  경제적 BEP 1,082건", required=False)
    replace(9, "상품별 원가 구조와 계약 책임을 분리",
            "상품별 원가·청구시간·제휴 계약 조건을 확인")
    replace(10, "유료 수요·완료율·지원비·공헌이익 기록 후 단계별 심의",
            "수요·완료율·고객 지원 비용·공헌이익 측정 후 단계별 심의", required=False)
    replace(10, "실제 수요·운영비 확인 후 단계별 투자 승인",
            "수요·완료율·고객 지원 비용·공헌이익 측정 후 단계별 심의")
    slide = prs.slides[7]
    # Keep the native table and the original two-bar graphic. Allocate clean
    # vertical lanes below the table for the progress label and the decision.
    for sh in slide.shapes:
        if not sh.has_text_frame or not sh.text.strip():
            continue
        val = sh.text
        if "초기 공급" in val and "손익분기점" in val and sh.top > Inches(4.9):
            sh.top = Inches(5.35)
            sh.height = Inches(.20)
        if "예상 완료 199건은 경제적 BEP" in val:
            sh.top = Inches(6.12)
            sh.height = Inches(.76)
            sh.text_frame.word_wrap = True
            for p in sh.text_frame.paragraphs:
                p.space_before = Pt(0);p.space_after = Pt(0)
                for run in p.runs:
                    if run.font.size and run.font.size.pt > 13:
                        run.font.size = Pt(12.5)
    # Review should remain visually compact; no extra shapes or duplicated footnotes.
else:
    replace(4, "경기도 65세 이상 인구를 활용한 산정 기준",
            "고령 인구 참고치 · 유료 이용 수요는 별도 확인")
    replace(4, "20개 시·군 대상 지역 인구를 기준으로 산출한 규모",
            "대상 지역 인구 기준 · 서비스 가능 수요와 구분")
    replace(4, "SAM 약 1% 확보를 전제한 목표 산정 기준",
            "장기 목표 가설 · 초기 공급 계획과 별도")
    replace(7, "초기 완료량은 BEP의 18.4% · 목표까지 약 5.4배",
            "초기 199건 · 최대 공급 433건 · 현금 BEP 541건 · 경제적 BEP 1,082건")
    replace(8, "완료율 관리", "플랫폼 이용 비율 관리")
    replace(10, "월 현금 고정비 200만 원 × 2개월 · 단계별 배분 산정 기준",
            "현금 고정비 2개월 400만 원의 단계별 배분안")
    replace(10, "8주 현금 고정비 상한",
            "8주 고정비 내 배분 상한")
    replace(10, "별도 견적: 구축·보험·법무·환불·채용·판촉 / 필요 시 재심의",
            "별도 확인: 구축·보험·법무·환불·채용·판촉비는 400만 원 외 추가 검토")
    # Keep metric details legible in the existing editable text boxes.
    for sh in prs.slides[6].shapes:
        if not sh.has_text_frame: continue
        if "초기 199건 · 최대 공급 433건" in sh.text:
            sh.text_frame.word_wrap = True
            for para in sh.text_frame.paragraphs:
                for run in para.runs:
                    if run.font.size and run.font.size.pt > 16:
                        run.font.size = Pt(14)

prs.save(path)
check = Presentation(path)
assert len(check.slides) == expected
corpus = " ".join(
    "".join(p.text for p in frame.paragraphs)
    for slide in check.slides for _, frame in frames(slide)
)
for required in ("199건", "1,082건", "3,700원"):
    assert required in corpus, (MODE, required)
assert "541건" in corpus, (MODE, "cash BEP")
assert all(x not in corpus for x in ("검토 방향로", "고객 설정로", "산정 기준한"))
print("PASS", MODE, "slides", expected, "editorial updates", len(changes),
      "cash and economic break-even labeled", path)
