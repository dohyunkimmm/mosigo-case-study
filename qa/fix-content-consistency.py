"""Apply the verified sensitivity-scenario labels and preserve the workbook package.

The Excel source values and formula were first edited/recalculated with artifact_tool.
This script transports those four corrected XML cells into the deployed Office package,
preserving every other workbook member byte-for-byte after extraction.
"""
from pathlib import Path
from zipfile import ZipFile
from tempfile import NamedTemporaryFile
from pptx import Presentation
from xml.etree import ElementTree as ET
import os
import re

model = Path("downloads/mosigo_model.xlsx")
cells = {
    "A14": (
        "경유율 20%p 하락",
        "플랫폼 이용 비율 20%p 하락",
    ),
    "B14": (
        "기준 80% → 60% (−20%p)",
        "플랫폼 이용 비율 80% → 60% (−20%p)",
    ),
    "D14": (
        "ROUND('공급사업성'!B9*'가정'!B21*'가정'!B22*0.8*(1-'가정'!B17)*'가정'!B18,0)",
        "ROUND('공급사업성'!B9*'가정'!B21*('가정'!B22-20%)*(1-'가정'!B17)*'가정'!B18,0)",
    ),
    "E14": ("-3411700", "-3448700"),
}
with ZipFile(model) as archive:
    original_members = [(item, archive.read(item.filename)) for item in archive.infolist()]
    assert all(info.filename != "xl/externalLinks/externalLink1.xml" for info, _ in original_members)
    worksheet = next(data for info, data in original_members if info.filename == "xl/worksheets/sheet5.xml").decode()
    replaced = worksheet
    for coordinate, (before, after) in cells.items():
        pattern = r'<x:c r="' + coordinate + r'"[^>]*>.*?</x:c>'
        matching = re.findall(pattern, replaced)
        assert len(matching) == 1, (coordinate, "missing or duplicate")
        old_cell = matching[0]
        if after in old_cell:
            continue
        assert before in old_cell, (coordinate, old_cell)
        new_cell = old_cell.replace(before, after)
        if coordinate == "D14":
            new_cell = new_cell.replace("<x:v>159</x:v>", "<x:v>149</x:v>")
        assert new_cell != old_cell
        replaced = replaced.replace(old_cell, new_cell, 1)
    ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    tree = ET.fromstring(replaced)
    find = lambda address: tree.find(".//x:c[@r='" + address + "']", ns)
    assert find("A14").find("x:v",ns).text == "플랫폼 이용 비율 20%p 하락"
    assert find("B14").find("x:v",ns).text == "플랫폼 이용 비율 80% → 60% (−20%p)"
    assert "B22-20%" in find("D14").find("x:f",ns).text
    assert find("D14").find("x:v",ns).text == "149"
    assert find("E14").find("x:v",ns).text == "-3448700"
    if replaced != worksheet:
        with NamedTemporaryFile(dir=model.parent, suffix=".xlsx", delete=False) as tmp:
            temp_name = tmp.name
        try:
            with ZipFile(temp_name, "w") as patched:
                for info,data in original_members:
                    patched.writestr(info, replaced.encode() if info.filename == "xl/worksheets/sheet5.xml" else data)
            with ZipFile(temp_name) as verify:
                assert verify.testzip() is None
                for info, data in original_members:
                    if info.filename != "xl/worksheets/sheet5.xml":
                        assert verify.read(info.filename) == data, info.filename
            os.replace(temp_name,model)
        finally:
            if os.path.exists(temp_name): os.remove(temp_name)
print("PASS Excel 5-sheet sensitivity scenario: platform use ratio 80% to 60%, 149 completions, -3,448,700 KRW")

slides = Path("downloads/mosigo_report.pptx")
prs = Presentation(slides)
assert len(prs.slides)==11
count=0
slides_changed=False
for shape in prs.slides[1].shapes:
    if not shape.has_text_frame: continue
    for paragraph in shape.text_frame.paragraphs:
        for run in paragraph.runs:
            if "MOSIGO 사업기획서 11~12쪽" in run.text:
                run.text=run.text.replace("MOSIGO 사업기획서 11~12쪽","MOSIGO 사업기획서 3쪽")
                slides_changed=True
                count += 1
            elif "MOSIGO 사업기획서 3쪽" in run.text:
                count += 1
assert count==1, "Expected precisely one source reference on slide 2"
if slides_changed:
    prs.save(slides)
assert "MOSIGO 사업기획서 3쪽" in "\n".join(sh.text for sh in Presentation(slides).slides[1].shapes if sh.has_text_frame)
print("PASS PowerPoint slide 2 now references current business plan p3; 11 slides retained")
