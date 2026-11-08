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

# Public source decks already carry the post-review investment/growth titles.
# Re-running the earlier copy-refinement pass must not demand obsolete wording.
already_aligned = (
    (MODE == "strategy" and any(
        sh.has_text_frame and ("단계별 투자 승인과 3개년 실행전략" in sh.text or "요구사항 우선순위와 검수·인계" in sh.text)
        for sh in prs.slides[9].shapes
    )) or
    (MODE == "ir" and any(
        sh.has_text_frame and "3개년 신사업 성장·투자 로드맵" in sh.text
        for sh in prs.slides[10].shapes
    ))
)
if already_aligned:
    print("PASS MOSIGO original deck already has aligned investment-and-growth strategic copy:", MODE)
    raise SystemExit(0)

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
    replace(9, "직접 운영 잔여 금액은 고객 지원·획득 비용 차감 전, 제휴형 건당 공헌이익은 차감 후입니다. 구독은 월 3회(회당 33,000원, 월 99,000원), 차량 원가는 추정치입니다.",
            "기본 상품 3만 원대는 출시 가격 가설, 표의 40,000원은 평균가 산정 기준입니다. 직접형은 고객 지원·획득 비용 차감 전, 제휴형은 차감 후입니다. 차량 원가는 추정치, 구독은 월 3회·9.9만 원입니다.", required=False)
    replace(10, "유료 수요·완료율·지원비·공헌이익 기록 후 단계별 심의",
            "수요·완료율·고객 지원 비용·공헌이익 측정 후 단계별 심의", required=False)
    replace(10, "실제 수요·운영비 확인 후 단계별 투자 승인",
            "수요·완료율·고객 지원 비용·공헌이익 측정 후 단계별 심의")
    replace(7, "기준 산정 기준 결과", "기준 시나리오 결과", required=False)
    for _, frame in frames(prs.slides[8]):
        if frame.text.strip() == "기본":
            frame.paragraphs[0].runs[0].text = "평균 이용가 기준"
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
    # P1: Official resident population is a dated benchmark, not measured
    # paid demand. Historical SAM is kept as a scenario until area-level
    # eligibility and supply filters have been recalculated.
    replace(4, "약 238만 명", "약 258만 명")
    replace(4, "고령 인구는 시장 참고 지표 · 실제 이용 수요는 별도 확인",
            "출처: 행안부 2026.10 주민등록 인구 · 인구는 유료 수요와 구분", required=False)
    replace(4, "경기도 65세 이상 인구를 활용한 산정 기준",
            "고령 인구 참고치 · 유료 이용 수요는 별도 확인")
    replace(4, "20개 시·군 대상 지역 인구를 기준으로 산출한 규모",
            "대상 지역 인구 기준 · 서비스 가능 수요와 구분")
    replace(4, "고령 인구 참고치 · 유료 이용 수요는 별도 확인",
            "2026.10 주민등록 2,578,873명 · 유료 수요 별도 확인", required=False)
    replace(4, "대상 지역 인구 기준 · 서비스 가능 수요와 구분",
            "기존 후보 지역 가정 · 기준월·대상 시군 재산정", required=False)
    replace(4, "SAM 약 1% 확보를 전제한 목표 산정 기준",
            "장기 목표 가설 · 초기 공급 계획과 별도")
    replace(7, "초기 완료량은 BEP의 18.4% · 목표까지 약 5.4배",
            "초기 199건 · 최대 공급 433건 · 현금 BEP 541건 · 경제적 BEP 1,082건")
    replace(8, "완료율 관리", "플랫폼 이용 비율 관리")
    replace(8, "완료율·획득 비용·취소율 변동에 따른 월 손익",
            "플랫폼 이용 비율·획득 비용·취소율 변동에 따른 월 손익", required=False)
    replace(8, "우선 측정: 고객 획득 비용·완료율·계약 단가",
            "우선 측정: 플랫폼 이용 비율·고객 획득 비용·계약 단가", required=False)
    replace(10, "월 현금 고정비 200만 원 × 2개월 · 단계별 배분 산정 기준",
            "현금 고정비 2개월 400만 원의 단계별 배분안")
    replace(10, "8주 현금 고정비 상한",
            "8주 고정비 내 배분 상한")
    replace(10, "별도 견적: 구축·보험·법무·환불·채용·판촉 / 필요 시 재심의",
            "별도 확인: 구축·보험·법무·환불·채용·판촉비는 400만 원 외 추가 검토")
    replace(9, "예약·완료·취소·재예약, 실제 획득·지원 비용 측정",
            "유료 전환·완료·취소와 실제 획득·지원 비용 측정")
    replace(9, "심의 기준  ·  실측 성과에 따라 확대 여부 결정",
            "8주 심의 · 실측 손익 검토 / 90일 재예약은 후속 평가", required=False)
    replace(10, "8주 단순 환산 약 252.7만 원",
            "예산상 2개월 환산 약 252.7만 원")
    replace(12, "고객 유료 의향·재예약 근거",
            "유료 전환·완료 근거 / 90일 재예약은 후속 평가")
    # P2: Align the two values to the right of the native bars without
    # changing the plotted bar lengths or numeric assumptions.
    from pptx.enum.text import PP_ALIGN
    for sh in prs.slides[6].shapes:
        if sh.has_text_frame and sh.text.strip() in ("199건", "1,082건"):
            sh.left = Inches(7.06)
            sh.width = Inches(1.22)
            sh.height = Inches(.32)
            sh.text_frame.word_wrap = False
            for paragraph in sh.text_frame.paragraphs:
                paragraph.alignment = PP_ALIGN.RIGHT
                for run in paragraph.runs:
                    if run.font.size and run.font.size.pt > 12: run.font.size = Pt(12)
        if sh.has_text_frame and sh.text.strip().startswith("초기 199건 · 최대 공급 433건"):
            sh.width = Inches(7.12)
            sh.text_frame.word_wrap = False
            for paragraph in sh.text_frame.paragraphs:
                for run in paragraph.runs:
                    if run.font.size and run.font.size.pt > 11.5: run.font.size = Pt(11.5)
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
if MODE == "ir":
    assert "약 258만 명" in corpus and "2,578,873명" in corpus
    assert "플랫폼 이용 비율·획득 비용·취소율" in corpus
    assert not any(x in corpus for x in ("완료율·획득 비용·취소율", "우선 측정: 고객 획득 비용·완료율"))
else:
    assert "기본 상품 3만 원대는 출시 가격 가설" in corpus
assert all(x not in corpus for x in ("검토 방향로", "고객 설정로", "산정 기준한"))
print("PASS", MODE, "slides", expected, "editorial updates", len(changes),
      "cash and economic break-even labeled", path)

