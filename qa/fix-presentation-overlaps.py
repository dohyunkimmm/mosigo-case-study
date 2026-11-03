"""Repair recurring text/table overlaps in the reviewed MOSIGO 11-slide PPTX.

Applied after the existing style and copy scripts, before PDF/WebP rendering.
Leaves all numeric scenario values, native editable tables, and slide count intact.
"""
from pathlib import Path
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.shapes import MSO_SHAPE_TYPE

source=Path(sys.argv[1] if len(sys.argv)>1 else "downloads/mosigo_report.pptx")
prs=Presentation(source)
assert len(prs.slides)==11
mark="mosigo-editorial-layout-v4"
if mark in (prs.core_properties.keywords or ""):
    print("PASS MOSIGO: reviewed slide geometry already applied")
    sys.exit(0)

def paragraph_replace(slide,old,new):
    changes=0
    for sh in slide.shapes:
        frames=[sh.text_frame] if sh.has_text_frame else []
        if sh.has_table:
            frames += [c.text_frame for row in sh.table.rows for c in row.cells]
        for frame in frames:
            for para in frame.paragraphs:
                runs=para.runs
                txt="".join(run.text for run in runs)
                if old not in txt:continue
                if not runs:continue
                if any(old in run.text for run in runs):
                    for run in runs:
                        if old in run.text:run.text=run.text.replace(old,new)
                else:
                    runs[0].text=txt.replace(old,new)
                    for run in runs[1:]:run.text=""
                changes+=1
    return changes

def near(actual,target,tolerance=.07):
    return abs(actual/Inches(1)-target)<tolerance

def move_band(slide, page_number):
    bg=0;text=0
    for sh in slide.shapes:
        y=sh.top/Inches(1)
        width=sh.width/Inches(1)
        if 5.75 < y < 5.91 and width>10 and (not sh.has_text_frame or not sh.text.strip()) and not sh.has_table:
            sh.top=Inches(5.79 if page_number==8 else 5.68)
            bg+=1
        elif 5.75 < y < 5.91 and width>10 and sh.has_text_frame:
            sh.top=Inches(5.80 if page_number==8 else 5.69)
            text+=1
    assert bg>=1 and text>=1, f"Page {page_number}: decision band not found ({bg},{text})"

for page_number in range(2,11):
    slide=prs.slides[page_number-1]
    # Legacy one-line subtitles now sit under three small comparison chips.
    # Remove only the wide duplicate labels in the same row as those chips.
    for sh in list(slide.shapes):
        if sh.has_text_frame and 1.55 <= sh.top/Inches(1) <= 2.20 and sh.width/Inches(1)>6:
            slide.shapes._spTree.remove(sh._element)

    if page_number not in (5,6,7,8,10):
        continue
    tables=[sh for sh in slide.shapes if sh.has_table]
    assert len(tables)==1, f"Page {page_number}: expected one native editable table"
    table=tables[0]
    new_top=2.29 if page_number==8 else 2.29
    new_height=3.02 if page_number==8 else 3.15
    table.top=Inches(new_top)
    table.height=Inches(new_height)
    for row in table.table.rows:
        row.height=Inches(new_height/len(table.table.rows))
    move_band(slide,page_number)

# Slide 8: the original progress bar crossed the lower table row.
# Relocate both bar rectangles and the text label to their own space.
slide=prs.slides[7]
bar_count=0
label_count=0
for sh in slide.shapes:
    if 5.19 < sh.top/Inches(1) < 5.60:
        if sh.has_text_frame and "초기 공급" in sh.text and "손익분기점" in sh.text:
            sh.top=Inches(5.35);sh.height=Inches(.22)
            label_count+=1
        elif (not sh.has_text_frame or not sh.text.strip()) and not sh.has_table and sh.height/Inches(1)<.24 and sh.width/Inches(1)>1:
            sh.top=Inches(5.62)
            bar_count+=1
assert bar_count>=2 and label_count>=1, f"Slide 8 progress data missing ({bar_count} bars, {label_count} labels)"

# Explicit Korean sentence repair; never change numerals or scenario provenance.
assert paragraph_replace(prs.slides[3],"우선 검토 방향로 검증","우선안으로 검토")>=1, "Slide 4 awkward phrase not found"
for slide in prs.slides:
    paragraph_replace(slide,"고객 설정로","고객 상황으로")
    paragraph_replace(slide,"검토 방향로","검토 방향으로")

prs.core_properties.keywords=((prs.core_properties.keywords or "")+" "+mark).strip()
prs.save(source)
check=Presentation(source)
assert len(check.slides)==11
for n in (5,6,7,8,10):
    slide=check.slides[n-1]
    table=next(sh for sh in slide.shapes if sh.has_table)
    assert table.top+table.height <= Inches(5.48 if n!=8 else 5.35), f"Slide {n}: table overlaps decision band"
assert "우선 검토 방향로" not in " ".join(sh.text for sh in check.slides[3].shapes if sh.has_text_frame)
assert "199" in " ".join(c.text for sh in check.slides[7].shapes if sh.has_table for row in sh.table.rows for c in row.cells)
print("PASS MOSIGO editorial slide QA: 11 slides, 5 table/band layouts, slide 8 progress, Korean copy")
