"""Align public MOSIGO editable PPTX with the investment-strategy case study.
Keep slide counts, diagrams, original Tossface images and source financial values.
Run after existing style/financial refinements and before rendering PDFs.
"""
from pathlib import Path
from pptx import Presentation

IR = {
  1:{6:'병원 동행 대리 예약 플랫폼\n신사업 투자전략 · 중장기 성장계획',7:'시장 기회 → 사업모델 비교 → 단위 경제성 → 단계별 투자·성장',9:'신사업 투자 검토안'},
  2:{3:'신사업 투자 판단 요약',4:'시장 기회·수익성·투자 단계를 연결한 경영 의사결정',21:'기존 사업자 제휴 우선  |  8주 검증 후 연차별 성장 투자',34:'수치: 투자 검토용 기준 시나리오 · 단계별 자원 배분과 성장전략 제시'},
  3:{3:'예약자와 이용자가 다른 신사업 기회',4:'지불 주체·서비스 이용자·제휴 공급자의 가치와 운영 조건'},
  4:{3:'시장 기회에서 투자 가능한 수요까지',4:'시장 인구 → 후보 생활권 → 공급·전환 가능한 시장 정의',14:'후보 지역 인구 · 선정 시군·기준월 확정 후 재산정',18:'3개년 성장 목표 후보 · 초기 공급과 별도 관리',24:'투자 판단 기준',25:'생활권별 수요·대체재·고객 유입·매니저 공급·전환 성과'},
  5:{3:'제휴 중심 신사업 운영모델',4:'제품 경쟁력과 제휴 운영 책임을 분리해 투자 부담 관리'},
  6:{3:'제휴 모델의 단위 경제성',4:'계약·수수료 조건과 획득·지원 비용을 반영한 건당 공헌이익'},
  7:{3:'공급 확대와 손익분기 전략',4:'공급 상한 433건 대비 경제적 BEP 1,082건 · 공급 확대와 단위손익 개선 병행',17:'초기 199건 · 공급 상한 433건 · 현금 BEP 541건 · 경제적 BEP 1,082건'},
  8:{3:'투자조건별 손익 민감도',4:'플랫폼 이용 비율·획득 비용·취소율 변화에 따른 투자 우선순위',58:'개선 우선순위: 제휴 공급 확보 → 획득·지원 비용 최적화 → 재이용 확대'},
  9:{3:'단계별 투자 승인 및 성과관리',4:'8주 검증 결과를 1년 차 사업모델 확정과 연계',32:'후속 투자 심의',34:'8주 성과·예산 검토 / 90일 재예약은 이후 성과평가'},
  10:{3:'신사업 초기 투자 예산 · 400만 원',4:'8주 검증 운영비의 단계별 배분 · 추가 투자 항목은 별도 심의',28:'기본 운영비 외 구축·보험·법무·판촉 등은 별도 견적 및 투자 승인 대상'},
  11:{2:'10 / 3-YEAR INVESTMENT ROADMAP',3:'3개년 신사업 성장·투자 로드맵',4:'제휴 검증 → 지역 확대 → 기업·공공 채널 다각화',
      8:'1년 차',9:'제휴 사업모델 정교화',10:'공급·원가·고객 반응 기반 투자 기준 확정',
      12:'2년 차',13:'인접 생활권·제휴 네트워크 확대',14:'지역별 공헌이익·운영비로 자원 배분',
      16:'3년 차',17:'기업·공공 협력 모델 검토',18:'반복 이용·채널별 획득비·수익성 비교',
      20:'자원 배분',21:'제휴·서비스·IT 투자 우선순위 조정',22:'수요·공급·현금 소요에 따른 단계별 승인',
      24:'투자 심의',25:'확대·개선·보류 판단 기준 운영',26:'계약·안전 책임과 90일 재예약 후속 평가',
      28:'3개년 방향은 전략 제안 · 성과에 따라 투자규모·시점 조정',29:'자료 성격: 개인 전략기획 · 신사업 투자 및 사업화'},
  12:{4:'신사업 투자 및 성장 판단',5:'제휴형 신사업 투자 · 단계별 확장 전략',6:'8주 검증 → 1년 차 모델 확립 → 2년 차 지역 확장 → 3년 차 채널 다각화',
      8:'단계별 투자 승인 기준 3가지',
      9:'① 초기 투자 · 제휴 공급·고객 수요·비용 조건 확인\n② 확대 투자 · 지역별 공헌이익·현금 소요 평가\n③ 성장 투자 · 반복 수요·채널별 경제성 분석',
      10:'의사결정 원칙 · 투자 성과와 공급 역량을 함께 판단',
      11:'월 완료 199건 · BEP 1,082건 기준. 성장계획은 성과에 따라 조정.'},
}
STRATEGY={
  1:{2:'MOSIGO 신사업 사업화·투자전략',3:'고객·시장 분석부터 제휴 투자 판단까지',9:'시장 기회 분석  →  사업모델 평가  →  투자·성장 전략'},
  4:{2:'신사업 진입 전략과 우선 고객',5:'자녀 중심 고객 여정을 바탕으로 제휴형 초기 진입 전략 선택'},
  5:{2:'신사업 투자 대안과 운영모델 비교',4:'직접 운영·제휴·기업·공공 확장을 공급·현금비용·책임·확장성 기준으로 비교',16:'기존 사업자 제휴 우선 · 성과에 따라 사업모델 전환 검토'},
  7:{2:'제휴 투자안의 공급·단위 손익 평가',15:'공급 상한 433건·예상 완료 199건 대비 경제적 BEP 1,082건'},
  8:{2:'공급 확대와 손익분기 차이 분석',4:'초기 완료 199건은 BEP 1,082건의 18.4%. 공급 상한 433건을 넘어서기 위해 제휴 확대와 단위손익 개선을 병행.\n동일 생산성 기준 약 109명은 단순 환산이며, 확대 시 원가 구조 재계산이 필요.',16:'제휴 확대 · 비용 효율 · 수익구조 개선의 투자 우선순위'},
  9:{2:'상품·수익모델별 투자 매력도 비교',16:'동일 비용 범위로 비교하고 제휴 계약 조건에 따라 최종 수익성 판단'},
  10:{2:'단계별 투자 승인과 3개년 실행전략',5:'1년 차 모델 정교화 → 2년 차 생활권 확대 → 3년 차 기업·공공 제휴 검토',16:'단계별 비용·완료·재이용 성과를 투자 승인과 연계'},
  11:{2:'신사업 투자·성장 의사결정',4:'제휴 사업모델 우선 · 초기 완료 199건 / 손익분기점 1,082건(계획 기준)',
      5:'초기 투자 · 공급 계약, 고객 수요, 단위 손익 확인\n1년 차 · 제휴 사업모델과 운영 책임 정교화\n2년 차 · 지역별 사업성에 따른 생활권 확대\n3년 차 · 반복수요 기반 기업·공공 협력 모델 검토',
      9:'사업모델 정교화  ·  공급 확대  ·  자원 배분  ·  투자 심의'},
}

def set_text(shape, value):
    assert shape.has_text_frame, "expected editable text shape"
    tf=shape.text_frame
    parts=value.split('\n')
    if len(parts)==len(tf.paragraphs):
        for p,t in zip(tf.paragraphs,parts):
            if p.runs:
                p.runs[0].text=t
                for r in p.runs[1:]:r.text=''
            else:p.text=t
    else:
        p=tf.paragraphs[0]
        if p.runs:
            p.runs[0].text=value
            for r in p.runs[1:]:r.text=''
        else:p.text=value
        for p in tf.paragraphs[1:]:
            for r in p.runs:r.text=''
def main(kind):
    assert kind in {"ir","strategy"}
    pth=Path("downloads/MOSIGO_IR_Investment_Review_12slides.pptx" if kind=="ir" else "downloads/mosigo_report.pptx")
    p=Presentation(pth)
    changes=IR if kind=="ir" else STRATEGY
    assert len(p.slides)==(12 if kind=="ir" else 11)
    images_before=sum(int(sh.shape_type==13) for sl in p.slides for sh in sl.shapes)
    for no,update in changes.items():
        shapes=p.slides[no-1].shapes
        for idx,value in update.items():
            assert idx<len(shapes),(no,idx,len(shapes))
            set_text(shapes[idx],value)
    for sl in p.slides:
        for sh in sl.shapes:
            fs=[]
            if sh.has_text_frame:fs.append(sh.text_frame)
            if sh.has_table:fs.extend(c.text_frame for row in sh.table.rows for c in row.cells)
            for tf in fs:
                for pa in tf.paragraphs:
                    pa.font.name="Pretendard"
                    for run in pa.runs:run.font.name="Pretendard"
    images_after=sum(int(sh.shape_type==13) for sl in p.slides for sh in sl.shapes)
    assert images_before==images_after, "do not replace original Tossface pictograms"
    p.save(pth)
    check=Presentation(pth)
    assert len(check.slides)==len(p.slides)
    assert sum(int(sh.shape_type==13) for sl in check.slides for sh in sl.shapes)==images_before
    print(f"PASS {kind}: {len(check.slides)} editable pages, {images_before} original images, Pretendard text, strategic copy")
if __name__=="__main__":
    import sys
    main(sys.argv[1])
