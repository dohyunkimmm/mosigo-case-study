"""Apply MOSIGO IR visual identity without altering any slide copy or numbers.

Fonts: Pretendard across editable runs and the inherited PowerPoint theme.
Pictogram: the existing unmodified Tossface phone PNG used on the MOSIGO website.
"""
from pathlib import Path
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.util import Inches
from pptx.oxml.xmlchemy import OxmlElement
from pptx.oxml.ns import qn
from zipfile import ZipFile
from collections import Counter
import os
import re
import sys

filename = Path(sys.argv[1] if len(sys.argv) > 1 else "downloads/MOSIGO_IR_Investment_Review_12slides.pptx")
icon_file = Path(sys.argv[2] if len(sys.argv) > 2 else "assets/tossface-phone.png")
assert filename.is_file() and icon_file.is_file(), "MOSIGO IR deck or original Tossface icon missing"
assert icon_file.read_bytes()[:8] == bytes.fromhex("89504e470d0a1a0a"), "Expected original PNG source"

prs = Presentation(filename)
assert len(prs.slides) == 12, "Expected the existing MOSIGO 12-slide IR deck"

def frames(shapes):
    for shape in shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from frames(shape.shapes)
        if shape.has_text_frame:
            yield shape.text_frame
        if shape.has_table:
            for row in shape.table.rows:
                for cell in row.cells:
                    yield cell.text_frame

def slide_copy(slide):
    return tuple(
        "".join(run.text for run in paragraph.runs)
        for frame in frames(slide.shapes)
        for paragraph in frame.paragraphs
    )

original_text = tuple(slide_copy(slide) for slide in prs.slides)
is_styled = "mosigo-ir-pretendard-tossface-v1" in (prs.core_properties.keywords or "")

for slide in prs.slides:
    for frame in frames(slide.shapes):
        for paragraph in frame.paragraphs:
            for run in paragraph.runs:
                if not run.text:
                    continue
                run.font.name = "Pretendard"
                props = run._r.get_or_add_rPr()
                for key in ("ea", "cs"):
                    node = props.find(qn("a:" + key))
                    if node is None:
                        node = OxmlElement("a:" + key)
                        props.append(node)
                    node.set("typeface", "Pretendard")

# The deck originally has no pictogram images. Keep its data tables, copy,
# visual diagrams and all other shapes untouched; add only the source-brand icon.
if not is_styled:
    for number, slide in enumerate(prs.slides, 1):
        if number == 1:
            left, top, size = 10.65, 2.05, 1.13
        elif number == 12:
            left, top, size = 11.64, 1.21, 0.72
        else:
            left, top, size = 12.23, 0.36, 0.34
        pictogram = slide.shapes.add_picture(
            str(icon_file), Inches(left), Inches(top),
            width=Inches(size), height=Inches(size)
        )
        pictogram.name = "Tossface phone pictogram — MOSIGO original asset"

assert original_text == tuple(slide_copy(slide) for slide in prs.slides), "An IR slide text item changed"
prs.core_properties.keywords = (
    (prs.core_properties.keywords or "") + " mosigo-ir-pretendard-tossface-v1"
).strip() if not is_styled else prs.core_properties.keywords
prs.core_properties.comments = "Tossface pictogram: Toss / Viva Republica (existing original MOSIGO asset)."
prs.save(filename)

# Normalize inherited theme/master font defaults, including East Asian fonts.
temp_name = str(filename) + ".font-tmp"
replacements = 0
with ZipFile(filename, "r") as source, ZipFile(temp_name, "w") as target:
    for info in source.infolist():
        data = source.read(info.filename)
        if re.fullmatch(
            r"ppt/(?:theme|slideMasters|slideLayouts|notesMasters|notesSlides|handoutMasters)/.+\\.xml",
            info.filename
        ):
            data, n = re.subn(
                rb'(<a:(?:latin|ea|cs)\\b[^>]*?\\btypeface=")[^"]*(")',
                rb'\\1Pretendard\\2', data
            )
            replacements += n
        target.writestr(info, data)
os.replace(temp_name, filename)

verify = Presentation(filename)
assert len(verify.slides) == 12
assert original_text == tuple(slide_copy(slide) for slide in verify.slides)
run_fonts = Counter()
for slide in verify.slides:
    assert len([sh for sh in slide.shapes if sh.shape_type == MSO_SHAPE_TYPE.PICTURE]) >= 1, "Tossface icon missing"
    for frame in frames(slide.shapes):
        for para in frame.paragraphs:
            for run in para.runs:
                if run.text.strip():
                    run_fonts[run.font.name] += 1
                    p = run._r.get_or_add_rPr()
                    assert all(
                        p.find(qn("a:" + key)) is not None
                        and p.find(qn("a:" + key)).get("typeface") == "Pretendard"
                        for key in ("latin", "ea", "cs")
                    ), "Missing editable Pretendard font"
assert set(run_fonts) == {"Pretendard"}, run_fonts
print(
    "PASS MOSIGO IR deck visual identity:",
    len(verify.slides), "slides;",
    sum(run_fonts.values()), "Pretendard text runs;",
    replacements, "theme/master font references;",
    "12 slides with original Tossface pictogram; original copy preserved"
)
