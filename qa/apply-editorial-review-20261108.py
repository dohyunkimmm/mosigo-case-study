"""One-time reviewed editorial pass for MOSIGO report and companion documents.

Preserve existing financial assumptions, deck/page counts, source attribution,
editable PPT shapes, and product functionality. Changes are wording-only.
"""
from pathlib import Path
import re
from pptx import Presentation

ROOT=Path(".")
summary=[]

def edit_html(name, exact, patterns=()):
    path=Path(name)
    src=path.read_text(encoding="utf-8")
    text=src
    for old,new in exact:
        if old in text:
            count=text.count(old)
            if count!=1:
                raise AssertionError((name,old,count))
            text=text.replace(old,new)
            summary.append((name,"text",old[:35]))
        elif new not in text:
            raise AssertionError(f"Missing both old and new in {name}: {old!r}")
    for old,new in patterns:
        text,n=re.subn(old,new,text,count=1,flags=re.DOTALL)
        if n!=1 and new not in text:
            raise AssertionError(f"Missing HTML block in {name}: {old[:80]!r}")
        if n:
            summary.append((name,"block",old[:30]))
    if text!=src:
        path.write_text(text,encoding="utf-8")

edit_html("index.html",[
 ("<strong>핵심 판단 · 기존 사업자와 제한적 제휴 운영부터 검증</strong><p>대리 예약·진행 확인에 집중합니다. 초기 공급 기준 월 완료 예상 199건, 손익분기점 1,082건입니다.</p>",
  "<strong>핵심 산출물 · 고객 과업에서 화면 정책까지</strong><p>가족 대리 예약과 진행 공유의 사용자 여정을 요구사항·동의·권한 정책으로 연결했습니다. 공급·손익은 사업성 섹션에서 별도로 판단합니다.</p>"),
 ("<h2>수요·공급·손익 격차로 사업화 가능성을 판단한다</h2>",
  "<h2>공급 규모와 단위손익으로 사업화 조건 판단</h2>"),
 ("<h3 class=\"subhead\">시나리오 비교 <span class=\"label orange\">시나리오 모델</span></h3>",
  "<h3 class=\"subhead\">시나리오별 손익 비교 <span class=\"label orange\">가정 모델</span></h3>"),
 ("<strong>그래서 실행 순서를 바꿨습니다</strong>",
  "<strong>사업성 분석에 따른 실행 우선순위</strong>"),
 ("<strong>시장 규모 기준과 시점</strong> · 경기도 65세 이상 주민등록 인구는",
  "<strong>시장 규모의 참고 기준</strong> · 경기도 65세 이상 주민등록 인구는"),
 ("이전 기획의 약 238만 명·후보 지역 약 154만 명은 기준연월·대상 시군 확인 후 재산정합니다.",
  "이전 기획의 약 238만 명과 후보 지역 약 154만 명은 현재 시장 규모가 아닌 기존 추정치이며, 기준연월·대상 시군 확인 후 재산정합니다."),
 ("MOSIGO는 대리 예약·매니저 선택·진행 공유의 유료 이용 의향과 운영 조건을 검증합니다.",
  "MOSIGO는 대리 예약·매니저 선택·진행 공유의 편의를 제품 가치로 제안하고, 추가 지불 의향은 고객 조사에서 검증합니다."),
 ("<h3 class=\"subhead\">시장 진입 검토</h3><div class=\"callout\"><p>경쟁 서비스 7종·리뷰 118건은 기존 팀 조사입니다. 원본의 수집 기간·분류 기준을 확인하고, 공급량·가격 수용도·고객 획득 비용은 인터뷰·파일럿에서 측정합니다.</p></div>",
  "<h3 class=\"subhead\">시장 진입 검증 과제</h3><div class=\"callout\"><p>기존 팀 조사(서비스 7종·리뷰 118건)를 제품 요구사항의 출발점으로 활용했습니다. 공급 가능성·가격 수용도·획득 비용은 인터뷰와 제한 운영에서 확인하고, 조사 원본·분류 기준은 별도 근거로 관리합니다.</p></div>"),
 ("기존 팀 조사: 경쟁 앱 7종·리뷰 118건. 원본·분류 기준 추가 확인 필요.",
  "기존 팀 조사 7종·118건을 활용했습니다. 상세 출처·검증 범위는 02에서 확인합니다."),
 ("<span class=\"investment-gap-intro\">서비스 완료 전망, 현재 공급 상한, 두 손익분기 조건을 동일한 월 기준으로 비교했습니다.</span>",
  "<span class=\"investment-gap-intro\">동일한 월 기준으로 공급 제약과 투자 전 개선 조건을 비교했습니다.</span>"),
 ("<h2>MOSIGO 신사업 투자전략·성장 판단</h2>",
  "<h2>검증 결과에 따른 투자·확대 의사결정</h2>"),
 ("<strong id=\"investment-gap-title\">초기 공급과 손익분기 간 격차</strong>",
  "<strong id=\"investment-gap-title\">확대 전 확인할 공급·손익 조건</strong>"),
 ("<h3 class=\"subhead\">정보구조·핵심 여정</h3>",
  "<h3 class=\"subhead\">정보구조·7단계 사용자 여정</h3>"),
 ("<p>자녀 예약·부모 이용 흐름을 담은 <strong>개념 시안 3종</strong>입니다.</p>",
  "<p>역할 구분·매니저 선택·진행 공유를 보여주는 <strong>개념 시안 3종</strong>입니다.</p>"),
],patterns=[
 (r'<ol class="skim-journey"><li>가족 등록</li><li>병원 탐색</li><li>매니저 선택</li><li>신청·동의</li><li>진행 공유</li><li>결과 요약</li><li>재예약</li></ol>',
  '<p>7단계 사용자 여정은 아래 정보구조에서 확인할 수 있습니다.</p>'),
 (r'<h3 class="subhead">주요 변수별 사업성 민감도</h3>.*?</table></div>',
  '''<h3 class="subhead">사업성 변수의 측정 계획</h3><p>손익 영향은 06에서 계산하고, 여기서는 파일럿에서 필요한 기록과 해석을 구분합니다.</p><div class="tablewrap"><table class="tbl"><thead><tr><th scope="col">측정 변수</th><th scope="col">기록 기준</th><th scope="col">의사결정에 활용할 질문</th></tr></thead><tbody><tr><th scope="row">플랫폼 이용 비율</th><td>실제 매니저 가용 시간과 플랫폼 신청·완료 건수</td><td>지역·시간대별 공급 활용을 개선할 수 있는가</td></tr><tr><th scope="row">고객 획득 비용</th><td>유입 채널별 집행액·신규 완료 고객 수</td><td>고객 지원 비용을 포함한 공헌이익이 유지되는가</td></tr><tr><th scope="row">취소·완료율</th><td>신청·확정·취소·완료와 추가 지원 소요</td><td>취소·환불·지원 원가를 반영한 계약 조건은 무엇인가</td></tr></tbody></table></div>''')
])

edit_html("downloads/mosigo_business_plan_20261031.html",[
 ("<span>SAM 기존 가정</span><strong>약 154만 명</strong><small>이전 지역 추정치 · 대상 시군·기준월 재산정</small>",
  "<span>SAM·기존 추정</span><strong>약 154만 명</strong><small>확정 시장 규모 아님 · 대상 시군·기준월 재산정</small>"),
 ("건당 공헌이익이 양수여도 사업 전체의 흑자를 보장하지는 않습니다.",
  "건당 공헌이익과 고정비를 함께 검토해 투자 조건을 판단합니다."),
 ("<h1>민감도 분석과 손익 악화 요인</h1><h2>수요 감소, 고객 획득 비용 증가, 취소율 상승에 따른 수익성 변화를 검토</h2>",
  "<h1>민감도 분석과 개선 우선순위</h1><h2>수요·획득 비용·취소율 변화에 대응할 운영 조건 비교</h2>"),
 ("기존 SAM 약 154만 명과 장기 거래액 9억 원은 지역·수요·공급을 재확인할 기획 가정입니다.",
  "SAM 약 154만 명은 이전 지역 추정치이며, 연 거래액 9억 원은 장기 거래 시나리오입니다. 모두 유료 수요 실측값과 구분합니다."),
 ("성장 목표보다 공급 확보와 단위 경제성 개선을 우선하고, 연차별 사업성과에 따라 자원을 재배분합니다.",
  "첫해에는 공급·단위 경제성 개선에 집중하고, 후속 연차의 투자 시점과 규모는 실측 성과로 조정합니다."),
 ("8주 심의는 유료 전환·완료·운영비 중심으로 진행하고, 90일 재예약 성과는 후속 평가합니다.",
  "8주에는 유료 전환·완료·운영비를 평가하며, 재예약은 첫 완료 후 90일 관찰이 끝난 고객만 후속 평가합니다."),
 ("금액·공급·시장 수치는 사업계획 가정이며, 구축·보험·법무·환불·판촉 비용은 심의에 반영합니다.",
  "8주 현금 운영비 상한 400만 원에는 구축·보험·법무·환불·추가 판촉 비용이 포함되지 않습니다. 금액·공급·시장 수치는 사업계획 시나리오입니다."),
])

# Keep future document regenerators aligned with the reviewed source.
workflow=Path(".github/workflows/ppt-preview.yml")
wf=workflow.read_text(encoding="utf-8")
old_detector='"사용자 문제에서 제품 설계까지" in text'
new_detector='"제품기획 산출물과 후속 검증" in text'
if old_detector in wf:
    workflow.write_text(wf.replace(old_detector,new_detector),encoding="utf-8")

irworkflow=Path(".github/workflows/ir-deck.yml")
ir=irworkflow.read_text(encoding="utf-8")
step="      - name: Apply final concise editorial review to regenerated IR slides\\n        run: /tmp/mosigo-ir-venv/bin/python qa/apply-editorial-review-20261108.py\\n"
needle="      - name: Export PDF, verify 12 slides and stage-gated funding assumptions"
if "Apply final concise editorial review" not in ir:
    assert needle in ir
    irworkflow.write_text(ir.replace(needle,step.replace("\\\\n","\\n")+needle),encoding="utf-8")

def iter_frames(slide):
    def rec(shapes):
        for s in shapes:
            if s.shape_type==6:  # group
                yield from rec(s.shapes)
            if s.has_text_frame:
                yield s.text_frame
            if s.has_table:
                for row in s.table.rows:
                    for c in row.cells:
                        yield c.text_frame
    yield from rec(slide.shapes)

def replace_on_slide(prs, page, old, new, mandatory=False):
    n=0
    for tf in iter_frames(prs.slides[page-1]):
        for p in tf.paragraphs:
            txt="".join(run.text for run in p.runs)
            if old not in txt:
                continue
            if old in [run.text for run in p.runs]:
                for run in p.runs:
                    if old in run.text:
                        run.text=run.text.replace(old,new)
                        n+=1
            else:
                if not p.runs:
                    continue
                p.runs[0].text=txt.replace(old,new)
                for run in p.runs[1:]:
                    run.text=""
                n+=1
    if mandatory and n!=1:
        raise AssertionError(f"slide {page}: expected exactly one {old!r}, got {n}")
    if n:
        summary.append(("slide",page,old[:40]))
    return n

deck_edits={
 "downloads/mosigo_report.pptx":{
  2:[
   ("시장·공급 수치는 사업기획을 위한 추정치이며, 운영 실적과 구분했습니다.","시장·공급 수치는 추정치이며, 상세 산정 근거는 사업기획서에서 확인합니다."),
   ("고객 문제와 조사 근거","사용자 문제와 요구사항의 근거"),
  ],
  5:[
   ("신사업 투자 대안과 운영모델 비교","서비스 제공 방식과 운영 전제"),
   ("기존 사업자 제휴 우선 · 성과에 따라 사업모델 전환 검토","제휴 공급을 먼저 확인하고 운영 책임을 구분"),
  ],
  7:[
   ("핵심 과업 · 4가지","사용자 과업 · 4개"),
   ("요구사항 · R-01~R-06","기능 요구사항 · 6개(R-01~06)"),
  ],
  8:[
   ("공급 확대와 손익분기 차이 분석","서비스 운영을 위한 공급 조건"),
   ("제휴 확대 · 비용 효율 · 수익구조 개선의 투자 우선순위","공급 가능 시간·지원 비용을 제품 출시 조건과 연결"),
  ],
  9:[
   ("상품 · 수익모델별 투자 매력도 비교","상품별 이용 조건과 수익성 비교"),
   ("상품·수익모델별 투자 매력도 비교","상품별 이용 조건과 수익성 비교"),
  ],
  11:[
   ("사용자 문제에서 제품 설계까지","제품기획 산출물과 후속 검증"),
   ("사용자 문제 · 핵심 여정 · 기능 6개 · UX 설계","역할·동의 정책 · 기능 요구사항 6개 · 예외 대응"),
   ("사용자 요구 · 서비스 흐름 · UX 설계 · 실행 계획","요구사항·화면 정책·사용성 검증 계획"),
  ]
 },
 "downloads/MOSIGO_IR_Investment_Review_12slides.pptx":{
  3:[
   ("투자 검증 검토 방향","핵심 검증 질문"),
  ],
  4:[
   ("후보 지역 인구 · 선정 시군 · 기준월 확정 후 재산정","기존 지역 추정치 · 시군·기준월 재산정 전"),
   ("후보 지역 인구 · 선정 시군·기준월 확정 후 재산정","기존 지역 추정치 · 시군·기준월 재산정 전"),
  ],
  7:[
   ("공급 확대와 손익분기 전략","공급·단위손익 개선 조건"),
  ],
  8:[
   ("투자조건별 손익 민감도","조건 변화에 따른 손익 대응"),
   ("기준 산정 기준","기준 시나리오"),
   ("지표 개선","공급·비용 기준 점검"),
  ],
  9:[
   ("승인 한도 · 80만 원 · 검증 준비 증빙","통과 조건 · 고객 수요·동의 기준 기록"),
   ("승인 한도  ·  80만 원 · 검증 준비 증빙","통과 조건 · 고객 수요·동의 기준 기록"),
   ("승인 한도 · 120만 원 · 계약 조건 검토","통과 조건 · 공급 가능·책임 범위 합의"),
   ("승인 한도  ·  120만 원 · 계약 조건 검토","통과 조건 · 공급 가능·책임 범위 합의"),
   ("승인 한도 · 200만 원 · 실측 손익 기록","통과 조건 · 완료·비용 실측값 확보"),
   ("승인 한도  ·  200만 원 · 실측 손익 기록","통과 조건 · 완료·비용 실측값 확보"),
   ("P0~P2 현금 집행 상한 400만 원 · 단계별 배분 산정 기준","단계별 예산 배분은 다음 장에서 확인"),
  ],
  10:[
   ("손익 기준 참고 · 월 199건 × 3,700원 − 200만 원","예산 편성 기준 · 현금 고정비 200만 원 × 2개월"),
   ("현금 손실 약 126.4만 원/월 · 예산상 2개월 환산 약 252.7만 원","실제 집행액은 단계별 확인 · 경제적 비용은 별도"),
   ("기본 운영비 외 구축·보험·법무·판촉 등은 별도 견적 및 투자 승인 대상","400만 원에 구축·보험·법무·환불·추가 판촉비 미포함"),
  ],
  12:[
   ("서비스 운영 전 투자·인수 조건","서비스 운영 전 투자 승인 조건"),
   ("요구사항·안전 책임·제휴 확인 후 투자","검증 단계별 통과 조건에 따라 승인·보류 결정"),
   ("기획·검수 범위 확정 → 제한 운영 검증 → 수익성 심사","수요·공급 검증 → 책임 조건 합의 → 투자 재심의"),
   ("월 완료 199건 · BEP 1,082건 기준. 성장계획은 성과에 따라 조정.","8주 성과로 초기 투자 판단, 90일 재예약은 후속 평가."),
  ]
 }
}

for filename,changes in deck_edits.items():
    prs=Presentation(filename)
    expected=11 if "mosigo_report" in filename else 12
    assert len(prs.slides)==expected,(filename,len(prs.slides))
    for page,mapping in changes.items():
        for old,new in mapping:
            replace_on_slide(prs,page,old,new)
    prs.save(filename)
    assert len(Presentation(filename).slides)==expected
    print("DECK",filename,"pages",expected)

print("EDITORIAL PASS",len(summary))
for x in summary: print(*x,sep=" | ")

