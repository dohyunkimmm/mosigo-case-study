#!/usr/bin/env python3
"""Regression: source text must survive the visual card-bounds repair."""
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import subprocess
import sys

from pptx import Presentation

SOURCE = Path("downloads/mosigo_report.pptx")
FIX = Path("qa/fix-presentation-card-overlaps.py")


def text(pptx):
    p = Presentation(pptx)
    return [[x.text for x in slide.shapes if x.has_text_frame] for slide in p.slides]


with TemporaryDirectory() as tmp:
    output = Path(tmp) / "report.pptx"
    shutil.copy2(SOURCE, output)
    before = text(output)
    assert len(before) == 11
    assert "4주차" in "\n".join(before[9])
    assert "동행" in "\n".join(before[4])
    subprocess.run([sys.executable, str(FIX), str(output)], check=True)
    subprocess.run([sys.executable, str(FIX), str(output), "--check"], check=True)
    after = text(output)
    assert before == after, "Actual presentation text changed"
    assert output.stat().st_size > 30_000
print("PASS preserved all 11 editable slides and source text while limiting masked textboxes")
