"""P0/P1/P2 presentation QA: editable source with no new charts or invented figures.
Run AFTER focus-service-pm-decks in each corresponding deck workflow.
"""
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt

ROOT=Path("downloads")

def shape_text(shape, text):
    assert shape.has_text_frame
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
       ["요구사항·기능","검수 기준 · 구현/운영 구분"],
       ["R-02 예약 소유권","비소유자 조회·변경 거부 / 구현·자동 검증"],
       ["R-03 공유·권한","링크 만료·폐기, 읽기 전용 처리 / 구현·자동 검증"],
       ["R-04 예약 상태·복구","중복·오래된 변경 요청 차단 / 구현·자동 검증"],
       ["R-01·05 역할·비교","예약자·이용자 분리, 매니저 비교 / 정책·시연; 운영 검증 전"],
    ]
    updates=shape_text(slide.shapes[2],"PRD 요구사항과 검수 근거 추적")
    for i,row in enumerate(rows):
        for j,value in enumerate(row):
            cell=table.cell(i,j)
            updates+=shape_text(cell,value)
    for idx,value in [
       (9,"핵심 요구사항 R-01~06"),
       (11,"서버 검증 R-02~04"),
       (13,"운영 전 확인 R-01·05"),
       (15,"요구사항 → 구현·테스트 → 인수 판단 연결"),
    ]:
        updates+=shape_text(slide.shapes[idx],value)
    # No new numeric facts: existing economics source remains in original model,
    # main pages 8/9, the full business plan, and companion IR deck.
    assert "예약 소유권" in table.cell(1,0).text
    assert "검수" in slide.shapes[2].text
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
        assert "PRD 요구사항과 검수 근거 추적" in check.slides[6].shapes[2].text
    else:
        assert check.slides[11].shapes[5].text=="요구사항·안전 책임·제휴 확인 후 투자"
        assert check.slides[11].shapes[5].top+check.slides[11].shapes[5].height < check.slides[11].shapes[6].top
    print("PASS MOSIGO final presentation QA",mode,"changes",updates,
          "slides",len(check.slides),"charts and pictograms preserved")

if __name__=="__main__":
    import sys
    main(sys.argv[1])
