"""Subtle, editable presentation hierarchy refinements; leave source numerical facts untouched.
IR 12: strengthen three-year stages; strategy 11: convert final multi-line narrative
into four explicit investment milestones. No icons or download buttons added.
"""
import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR

FOREST=RGBColor(19,76,53)
GREEN=RGBColor(42,116,78)
PALE=RGBColor(231,244,234)
INK=RGBColor(25,61,44)
MUTED=RGBColor(82,113,95)
WHITE=RGBColor(255,255,255)

def rect(sl,x,y,w,h,fill,name):
    sh=sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if h>.18 else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h))
    sh.name=name
    sh.fill.solid()
    sh.fill.fore_color.rgb=fill
    sh.line.fill.background()
    return sh

def label(sl,value,x,y,w,h,size=15,bold=False,color=INK,name="MOSIGO_VISUAL_20261108_LABEL"):
    sh=sl.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    sh.name=name
    tf=sh.text_frame
    tf.clear()
    tf.word_wrap=True
    tf.margin_left=Inches(.02)
    tf.margin_right=Inches(.02)
    tf.margin_top=Inches(.03)
    tf.margin_bottom=Inches(.02)
    tf.vertical_anchor=MSO_ANCHOR.MIDDLE
    for i,line in enumerate(value.split("\n")):
        p=tf.paragraphs[0] if i==0 else tf.add_paragraph()
        r=p.add_run()
        r.text=line
        r.font.name="Pretendard"
        r.font.size=Pt(size)
        r.font.color.rgb=color
        r.font.bold=bold
    return sh

def update(mode):
    assert mode in ("ir","strategy")
    path=Path("downloads/MOSIGO_IR_Investment_Review_12slides.pptx" if mode=="ir" else "downloads/mosigo_report.pptx")
    prs=Presentation(path)
    assert len(prs.slides)==(12 if mode=="ir" else 11)
    page=prs.slides[10]
    original_images=sum(sh.shape_type==13 for slide in prs.slides for sh in slide.shapes)
    if any(sh.name.startswith("MOSIGO_VISUAL_20261108") for sh in page.shapes):
        print("PASS visual hierarchy already applied",mode)
        return
    if mode=="ir":
        assert "3개년 신사업" in page.shapes[3].text
        for index,top in enumerate((1.99,2.80,3.61),1):
            # A clear left-edge stage accent makes the three investment years distinguishable.
            accent=GREEN if index==1 else RGBColor(68,142,98) if index==2 else RGBColor(111,171,128)
            rect(page,.70,top,.085,.75,accent,f"MOSIGO_VISUAL_20261108_IR_{index}")
            year_shape=page.shapes[[8,12,16][index-1]]
            for para in year_shape.text_frame.paragraphs:
                for run in para.runs:
                    run.font.name="Pretendard"
                    run.font.bold=True
                    run.font.color.rgb=FOREST
        # Resource allocation and approval remain separate from the three chronological stages.
        for idx in (19,23):
            sh=page.shapes[idx]
            sh.fill.solid()
            sh.fill.fore_color.rgb=PALE
    else:
        original=page.shapes[5]
        text=original.text.replace("\n"," ")
        assert "초기 투자" in text and "3년 차" in text, text[:240]
        original.text=""
        steps=[
          ("01 / 초기 투자","공급 계약·고객 수요\n단위 손익 확인"),
          ("02 / 1년 차","제휴 사업모델과\n운영 책임 정교화"),
          ("03 / 2년 차","지역별 사업성에 따른\n생활권 확대"),
          ("04 / 3년 차","반복수요 기반 기업·\n공공 협력 모델 검토")]
        fills=[RGBColor(234,245,235),WHITE,RGBColor(234,245,235),WHITE]
        for i,(heading,detail) in enumerate(steps):
            x=.79+i*2.96
            card=rect(page,x,3.83,2.78,2.08,fills[i],f"MOSIGO_VISUAL_20261108_CARD_{i+1}")
            card.line.color.rgb=RGBColor(209,229,213)
            card.line.width=Pt(.6)
            rect(page,x,3.83,2.78,.075,GREEN if i==0 else RGBColor(92,152,112),
                 f"MOSIGO_VISUAL_20261108_TOP_{i+1}")
            label(page,heading,x+.17,4.05,2.46,.38,15,True,FOREST)
            label(page,detail,x+.17,4.57,2.46,.89,15,False,INK)
    prs.save(path)
    fresh=Presentation(path)
    assert len(fresh.slides)==len(prs.slides)
    assert sum(sh.shape_type==13 for slide in fresh.slides for sh in slide.shapes)==original_images
    assert any(sh.name.startswith("MOSIGO_VISUAL_20261108") for sh in fresh.slides[10].shapes)
    print(f"PASS {mode} editable presentation visual polish, numeric source and Tossface pictograms preserved")

if __name__=="__main__":
    update(sys.argv[1])
