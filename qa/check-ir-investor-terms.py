#!/usr/bin/env python3
"""Validate published IR readability and synchronized editable source without modifying files."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as ET

ROOT = Path("downloads")
PDF = ROOT / "MOSIGO_IR_Investment_Review_12slides.pdf"
PPT = ROOT / "MOSIGO_IR_Investment_Review_12slides.pptx"
STEMS = ROOT / "previews"
BAD = re.compile(r"R\s*-\s*0[1-6]|\b[GP][0-3]\b|\b(?:BEP|CAC)\b")
NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}

def output(*args):
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT)

assert PDF.is_file() and PPT.is_file()
count = re.search(r"(?m)^Pages:\s*(\d+)$", output("pdfinfo", str(PDF)))
assert count and int(count.group(1)) == 12, "Public IR PDF must have 12 pages"
pdf_text = output("pdftotext", "-layout", str(PDF), "-")
assert not BAD.search(pdf_text), "IR PDF has unexplained investor abbreviations"
for figure in ("199","433","541","1,082","3,700","400"):
    assert figure in pdf_text, "Public financial assumption missing: " + figure
assert "손익분기점" in pdf_text and "단계" in pdf_text

with ZipFile(PPT) as f:
    assert f.testzip() is None, "Invalid editable IR package"
    names = sorted(
        (name for name in f.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)),
        key=lambda x: int(re.search(r"slide(\d+)", x).group(1))
    )
    assert len(names) == 12, "IR PPTX should have exactly 12 editable slides"
    text = "\n".join(
        (node.text or "")
        for name in names
        for node in ET.fromstring(f.read(name)).findall(".//a:t", NS)
    )
    assert not BAD.search(text), "Editable IR PPTX still has unexplained shorthand"
    for figure in ("199","433","541","1,082","3,700","400"):
        assert figure in text, "Editable IR assumption missing: " + figure
    for stage in ("0단계","1단계","2단계","3단계"):
        assert stage in text, "Editable IR stage missing: " + stage

for page in range(1,13):
    for kind in ("", "-sm"):
        asset = STEMS / f"ir-{page:02}{kind}.webp"
        assert asset.is_file() and asset.stat().st_size > 1000, f"Missing IR preview {asset}"
assert len(list(STEMS.glob("ir-*.webp"))) == 24, "IR previews must be exactly 24"
print("PASS IR: 12 editable/PDF slides, 24 previews, expanded labels and six unchanged financial values")
