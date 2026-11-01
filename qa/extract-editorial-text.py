from pathlib import Path
from zipfile import ZipFile
import subprocess
from pptx import Presentation
from openpyxl import load_workbook

ROOT = Path("downloads")
OUT = Path("qa-artifacts")
OUT.mkdir(exist_ok=True)

# Final PDFs: preserve page boundaries for page-by-page editorial review.
for source, target in [
    (ROOT / "mosigo_business_plan_20261031.pdf", OUT / "business-plan-pages.txt"),
    (ROOT / "mosigo_report_preview.pdf", OUT / "presentation-pages.txt"),
]:
    text = subprocess.check_output(
        ["pdftotext", "-layout", str(source), "-"], text=True
    )
    pages = text.split("\\f")
    target.write_text(
        "\\n\\n".join(
            f"===== PAGE {i + 1} =====\\n{page.strip()}"
            for i, page in enumerate(pages) if page.strip()
        ),
        encoding="utf-8",
    )

# Editable PPTX: extract each shape and table cell in slide order.
prs = Presentation(ROOT / "mosigo_report.pptx")
lines = []
for slide_no, slide in enumerate(prs.slides, 1):
    lines.append(f"===== SLIDE {slide_no} =====")
    for shape_no, shape in enumerate(slide.shapes, 1):
        if shape.has_text_frame and shape.text.strip():
            lines.append(f"[shape {shape_no}] {shape.text.strip()}")
        if shape.has_table:
            for row_no, row in enumerate(shape.table.rows, 1):
                lines.append(
                    f"[table row {row_no}] " +
                    " | ".join(cell.text.strip() for cell in row.cells)
                )
(OUT / "presentation-editable.txt").write_text("\\n".join(lines), encoding="utf-8")

# Excel: expose every populated cell with formula and cached-value views.
model = ROOT / "mosigo_model.xlsx"
wb_formula = load_workbook(model, data_only=False)
wb_values = load_workbook(model, data_only=True)
lines = []
for ws in wb_formula.worksheets:
    wv = wb_values[ws.title]
    lines.append(f"===== SHEET {ws.title} ({ws.max_row}x{ws.max_column}) =====")
    for row in ws.iter_rows():
        cells = []
        for cell in row:
            if cell.value is None:
                continue
            cached = wv[cell.coordinate].value
            if isinstance(cell.value, str) and cell.value.startswith("="):
                cells.append(f"{cell.coordinate}: {cell.value} [cached={cached!r}]")
            else:
                cells.append(f"{cell.coordinate}: {cell.value}")
        if cells:
            lines.append(" | ".join(cells))
(OUT / "excel-all-sheets.txt").write_text("\\n".join(lines), encoding="utf-8")

print(f"PASS editorial extraction: {len(prs.slides)} slides, {len(wb_formula.worksheets)} sheets")
for p in sorted(OUT.glob("*.txt")):
    print(f"EXTRACTED {p.name}: {p.stat().st_size} bytes")
