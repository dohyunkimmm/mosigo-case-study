"""Make the existing editable MOSIGO presentation visually consistent."""
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.dml.color import RGBColor
import sys
src=sys.argv[1] if len(sys.argv)>1 else "downloads/mosigo_report.pptx"
p=Presentation(src)
if "mosigo-design-v1" in (p.core_properties.keywords or ""):
    print("Presentation already normalized");sys.exit(0)
C=lambda x:RGBColor.from_string(x)
forest=C("123E33");dark=C("0D3028");ivory=C("FBFCF8");lime=C("D6EF8A")
pale=C("E9F4EB");white=C("FFFFFF");ink=C("192C25");muted=C("4F6958")
def text_style(sh,size,color,bold=False,align=PP_ALIGN.LEFT):
    tf=sh.text_frame;tf.word_wrap=True;tf.vertical_anchor=MSO_ANCHOR.MIDDLE
    tf.margin_left=Inches(.06);tf.margin_right=Inches(.06)
    tf.margin_top=Inches(.04);tf.margin_bottom=Inches(.04)
    for par in tf.paragraphs:
        par.alignment=align;par.space_before=Pt(0);par.space_after=Pt(0)
        for run in par.runs:
            run.font.name="Pretendard";run.font.size=Pt(size)
            run.font.bold=bold;run.font.color.rgb=color
def label(slide,x,y,w,h,s,size,color,bold=False,align=PP_ALIGN.LEFT):
    sh=slide.shapes.add_textbox(Inches(x),Inches(y),Inches(w),Inches(h))
    sh.text=s;text_style(sh,size,color,bold,align)
def bar(slide,x,y,w,h,color):
    sh=slide.shapes.add_shape(MSO_SHAPE.RECTANGLE,Inches(x),Inches(y),Inches(w),Inches(h))
    sh.fill.solid();sh.fill.fore_color.rgb=color;sh.line.fill.background()
    tree=slide.shapes._spTree;tree.remove(sh._element);tree.insert(2,sh._element)
for idx,slide in enumerate(p.slides,1):
    darkpage=idx in (1,11)
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb=dark if darkpage else ivory
    texts=[sh for sh in slide.shapes if sh.has_text_frame and sh.text.strip()]
    if not texts:continue
    title=texts[0];title.left=Inches(.77);title.top=Inches(1.04 if darkpage else .67)
    title.width=Inches(11.8);title.height=Inches(1.14 if darkpage else .76)
    text_style(title,38 if darkpage else 29.5,white if darkpage else forest,True)
    bar(slide,0,0,13.333,.11,lime if darkpage else forest)
    bar(slide,.77,2.26 if darkpage else 1.57,.82 if darkpage else 1.1,.065,lime if darkpage else C("429969"))
    for sh in texts[1:]:
        y=sh.top/Inches(1)
        if y>6.78:
            sh.text="MOSIGO";sh.left=Inches(.78);sh.top=Inches(7.08)
            sh.width=Inches(5);sh.height=Inches(.23)
            text_style(sh,10,C("C6E0CD") if darkpage else muted,True)
        elif idx==1:
            if y<2.3:
                sh.left=Inches(.78);sh.top=Inches(2.54);sh.width=Inches(11.7);sh.height=Inches(.58)
                text_style(sh,20,lime)
            elif y>5.9:
                sh.left=Inches(.78);sh.top=Inches(6.52);sh.width=Inches(11.5);sh.height=Inches(.36)
                text_style(sh,12.5,C("C0DDC9"))
            else:
                sh.left=Inches(.78);sh.top=Inches(3.51);sh.width=Inches(11.6);sh.height=Inches(1.7)
                text_style(sh,24,white,True)
        elif idx==11:
            if y<3.6:
                sh.left=Inches(.78);sh.top=Inches(2.64);sh.width=Inches(11.7);sh.height=Inches(.87)
                text_style(sh,26,lime,True)
            else:
                sh.left=Inches(.8);sh.top=Inches(3.95);sh.width=Inches(11.5);sh.height=Inches(2.05)
                text_style(sh,19,white)
        elif y<2.3:
            sh.left=Inches(.78);sh.top=Inches(1.70);sh.width=Inches(11.8);sh.height=Inches(.5)
            text_style(sh,16,muted)
        else:
            sh.left=Inches(.78);sh.top=Inches(6.21);sh.width=Inches(11.8);sh.height=Inches(.62)
            text_style(sh,14.2,forest,True)
    if not darkpage:
        for sh in slide.shapes:
            if not sh.has_table:continue
            tbl=sh.table;sh.left=Inches(.78)
            sh.top=Inches(2.23 if any(x.top/Inches(1)<2.3 and x!=title for x in texts[1:]) else 1.96)
            sh.width=Inches(11.77);sh.height=Inches(3.72 if len(tbl.rows)<=4 else 4.07)
            for ri,row in enumerate(tbl.rows):
                row.height=Inches(sh.height/Inches(1)/len(tbl.rows))
                for ci,cell in enumerate(row.cells):
                    cell.fill.solid();cell.fill.fore_color.rgb=forest if ri==0 else (white if ri%2 else pale)
                    cell.margin_left=Inches(.17);cell.margin_right=Inches(.13)
                    cell.margin_top=Inches(.07);cell.margin_bottom=Inches(.07)
                    cell.vertical_anchor=MSO_ANCHOR.MIDDLE;cell.text_frame.word_wrap=True
                    for pg in cell.text_frame.paragraphs:
                        pg.space_before=Pt(0);pg.space_after=Pt(0)
                        for run in pg.runs:
                            run.font.name="Pretendard";run.font.size=Pt(14 if len(tbl.columns)>=4 else 16)
                            run.font.bold=ri==0 or ci==0
                            run.font.color.rgb=white if ri==0 else (forest if ci==0 else ink)
    label(slide,11.82,7.04,.65,.29,f"{idx:02d} / {len(p.slides):02d}",10.5,C("C2DFCC") if darkpage else muted,True,PP_ALIGN.RIGHT)
    if not darkpage:label(slide,10.35,.27,2.12,.25,"STRATEGY CASE STUDY",9.5,muted,True,PP_ALIGN.RIGHT)
p.core_properties.keywords=((p.core_properties.keywords or "")+" mosigo-design-v1").strip()
p.save(src)
print("Normalized Pretendard presentation",len(p.slides),"slides")
