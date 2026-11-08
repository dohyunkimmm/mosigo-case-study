"""P0/P1/P2 presentation QA: editable source with no new charts or invented figures.
Run AFTER focus-service-pm-decks in each corresponding deck workflow.
"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt

ROOT=Path("downloads")

def shape_text(shape, text):
    assert hasattr(shape, 'text_frame')
    if shape.text == text:
        return 0
    frame=shape.text_frame
    para=frame.paragraphs[0]
    if para.runs:
        para.runs[0].text=text
        for run in para.runs[1:]:run.text=""
    else:
        para.text=text
    for other in frame.paragraphs[1:]:
        for run in other.runs:run.text=""
    frame.word_wrap=True
    return 1

def chart_values(prs):
    return [tuple(tuple(s.values) for s in sh.chart.series)
        for slide in prs.slides for sh in slide.shapes if sh.has_chart]

def apply_strategy(prs):
    slide=prs.slides[6]  # Page 7: redundant economics is already retained on pages 8 and 9.
    table_shapes=[sh for sh in slide.shapes if sh.has_table]
    assert len(table_shapes)==1
    table=table_shapes[0].table
    assert len(table.rows)==5 and len(table.columns)==2
    rows=[
       ["사용자 과업","핵심 기능·화면 정책"],
       ["탐색·비교","지역·일정·매니저 정보 기준 비교"],
       ["대리 신청","예약자·이용자 분리 / 동의 확인"],
       ["진행 공유","상태 확인·공유 대상·유효기간 안내"],
       ["변경·복구","취소·변경·오류 시 다시 확인 경로"],
    ]
    updates=shape_text(slide.shapes[2],"대리 예약의 핵심 경험과 요구사항")
    for i,row in enumerate(rows):
        for j,value in enumerate(row):
            cell=table.cell(i,j)
            updates+=shape_text(cell,value)
    for idx,value in [
       (9,"주요 사용자 · 자녀/부모"),
       (11,"핵심 과업 · 4가지"),
       (13,"요구사항 · R-01~R-06"),
       (15,"사용자 문제 → 기능 정의 → 화면 정책 → 후속 검증"),
    ]:
        updates+=shape_text(slide.shapes[idx],value)
    # Public-facing slide copy follows the user-centered PRD; QA evidence stays private.
    wording = {
       "STRATEGY CASE STUDY": "MOSIGO · 제품기획",
       "정책·검수 기준": "주요 정책·설계 원칙",
       "읽기·변경 권한, 만료·중복 요청 검수": "읽기·변경 권한과 링크 만료·중복 요청 안내",
       "P2 UX 검증": "P2 사용성 확인",
       "문제 확인 → 제품 설계 → UX 검증 → 운영 타당성 판단": "문제 확인 → 제품 설계 → 사용성 확인 → 운영 타당성 판단",
       "UX 검증·공급 조건": "사용성 확인·공급 조건",
       "사용자 니즈 · 서비스 흐름 · UX 설계 · 실행 계획": "사용자 요구 · 서비스 흐름 · UX 설계 · 실행 계획",
       "우선 고객 문제와 니즈 가설": "우선 고객 문제와 사용자의 필요 가설",
       "예상 시나리오 분석과 실제 운영 실적을 구분합니다. 산출 근거: mosigo_model.xlsx.": "시장·공급 수치는 사업기획을 위한 추정치이며, 운영 실적과 구분했습니다.",
       "예상 199건  /  현금 BEP 541건  /  경제적 BEP 1,082건": "예상 199건 / 현금 손익분기 541건 / 경제적 손익분기 1,082건",
    }
    for sl in prs.slides:
        for sh in sl.shapes:
            frames = [sh.text_frame] if sh.has_text_frame else []
            if sh.has_table:
                frames += [c.text_frame for row in sh.table.rows for c in row.cells]
            for tf in frames:
                for paragraph in tf.paragraphs:
                    for run in paragraph.runs:
                        for before, after in wording.items():
                            if before in run.text:
                                run.text = run.text.replace(before, after)
                                updates += 1
    # The document generator must never reintroduce the old QA-focused copy.
    assert all(
       "STRATEGY CASE STUDY" not in sh.text and "검수" not in sh.text
       for sl in prs.slides for sh in sl.shapes if sh.has_text_frame
    )
    # No new numeric facts: existing economics source remains in original model,
    # main pages 8/9, the full business plan, and companion IR deck.
    assert "탐색·비교" in table.cell(1,0).text
    assert "핵심 경험" in slide.shapes[2].text
    return updates

def apply_ir(prs):
    slide=prs.slides[11]
    assert "조건" in slide.shapes[4].text
    updates=shape_text(slide.shapes[5],"요구사항·안전 책임·제휴 확인 후 투자")
    title=slide.shapes[5]
    title.text_frame.word_wrap=False
    for para in title.text_frame.paragraphs:
        for run in para.runs:
            if run.font.size != Pt(33):
                run.font.size=Pt(33)
                updates+=1
    # One line remains wholly above the lower subtitle at y=2.70in.
    title.top=Inches(1.76)
    title.height=Inches(.70)
    assert title.top+title.height < slide.shapes[6].top
    # Presentation footer/supporting notes were 9–9.5 pt. Increase carefully
    # while reserving safe vertical room before the page footer.
    for page in prs.slides:
        for shape in page.shapes:
            if not shape.has_text_frame or not shape.text.strip():continue
            y=shape.top / Inches(1)
            if y < 6.70:continue
            caption=shape.text
            target=Pt(10 if len(caption)>70 else 10.5)
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    if run.text.strip() and (run.font.size is None or run.font.size < target):
                        run.font.size=target
                        updates+=1
            if 6.7 <= y < 7.05:
                if shape.top != Inches(6.74):
                    shape.top=Inches(6.74)
                    updates+=1
                if shape.height < Inches(.32):
                    shape.height=Inches(.32)
                    updates+=1
            else:
                # Footer at y=7.11, no overlap with upper notes.
                if shape.height < Inches(.26):
                    shape.top=Inches(7.06)
                    shape.height=Inches(.26)
                    updates+=1
    return updates

def main(mode):
    assert mode in ("strategy","ir")
    path=ROOT/("mosigo_report.pptx" if mode=="strategy" else "MOSIGO_IR_Investment_Review_12slides.pptx")
    prs=Presentation(path)
    assert len(prs.slides)==(11 if mode=="strategy" else 12)
    before=chart_values(prs)
    nimages=sum(sh.shape_type==13 for slide in prs.slides for sh in slide.shapes)
    updates=apply_strategy(prs) if mode=="strategy" else apply_ir(prs)
    assert before==chart_values(prs)
    assert sum(sh.shape_type==13 for slide in prs.slides for sh in slide.shapes)==nimages
    if updates:prs.save(path)
    check=Presentation(path)
    assert len(check.slides)==len(prs.slides)
    assert before==chart_values(check)
    if mode=="strategy":
        assert "대리 예약의 핵심 경험과 요구사항" in check.slides[6].shapes[2].text
    else:
        assert check.slides[11].shapes[5].text=="요구사항·안전 책임·제휴 확인 후 투자"
        assert check.slides[11].shapes[5].top+check.slides[11].shapes[5].height < check.slides[11].shapes[6].top
    print("PASS MOSIGO final presentation QA",mode,"changes",updates,
          "slides",len(check.slides),"charts and pictograms preserved")

if __name__=="__main__":
    import sys
    main(sys.argv[1])
