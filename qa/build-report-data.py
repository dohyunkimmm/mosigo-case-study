"""Build the document search index and web calculator defaults from release assets."""
import argparse
import json
import math
import re
import subprocess
from pathlib import Path
from openpyxl import load_workbook
from pptx import Presentation

root = Path("downloads")
model = load_workbook(root / "mosigo_model.xlsx", data_only=True)
assumptions = {label: value for label, value, *_ in model["가정"].values if label}
keys = [
    "매니저 수", "매니저 1명당 주간 가용 시간", "완료 1건당 소요 시간",
    "가동률", "플랫폼 이용 비율", "취소율", "완료율", "평균 이용가",
    "중개 수수료율", "결제 수수료율", "완료 건당 고객 지원 비용", "건당 시스템 이용 비용",
    "신규 고객 비중", "신규 고객 획득 비용", "월 고정비", "인력 투입 기회비용",
]
percents = {3,4,5,6,8,9,12}
values = [round(assumptions[key] * (100 if i in percents else 1), 8) for i,key in enumerate(keys)]
staff,hours,time,utilization,platform,cancel,completion,price,rate,fee,support,system,new_share,cac,fixed,labor = values
capacity = staff * hours * 4.33 / time
orders = math.floor(capacity * utilization * platform * (100-cancel) * completion / 100**4 + .5)
margin = math.floor(price * (rate-fee)/100 - support - system - new_share*cac/100 + .5)
metrics = {
    "capacity": math.floor(capacity), "orders": orders, "margin": margin,
    "cashBep": math.ceil(fixed/margin), "economicBep": math.ceil((fixed+labor)/margin),
}
summary = model["사업성판단"]
for cell, key in {"B6":"orders","B8":"margin","B10":"economicBep"}.items():
    if not math.isclose(summary[cell].value, metrics[key]):
        raise ValueError(f"Excel cache does not match assumptions: {cell}")

def compact(value):
    return re.sub(r"[\s,]", "", value)

def check_metrics(text, label):
    text = compact(text)
    for value, unit in ((orders,"건"),(margin,"원"),(metrics["economicBep"],"건")):
        if str(value)+unit not in text:
            raise ValueError(f"{label}: expected {value:,}{unit}")

documents = {}
for key,name,count in [
    ("plan","mosigo_business_plan_20261031.pdf",17),
    ("presentation","mosigo_report_preview.pdf",11),
    ("ir","MOSIGO_IR_Investment_Review_12slides.pdf",12),
]:
    raw = subprocess.check_output(["pdftotext","-layout",str(root/name),"-"], text=True)
    pages = raw.rstrip("\f\n").split("\f")
    if len(pages) != count or any(not page.strip() for page in pages):
        raise ValueError(f"{name}: expected {count} searchable pages")
    check_metrics(raw,name)
    documents[key] = ["\n".join(" ".join(line.split()) for line in page.splitlines() if line.strip()) for page in pages]

for name in ("mosigo_report.pptx","MOSIGO_IR_Investment_Review_12slides.pptx"):
    deck = Presentation(root/name)
    parts = []
    for slide in deck.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                parts.append(shape.text)
            if shape.has_table:
                parts.extend(cell.text for row in shape.table.rows for cell in row.cells)
    check_metrics(" ".join(parts),name)
check_metrics(Path("index.html").read_text(),"web report")

parser=argparse.ArgumentParser()
parser.add_argument("--check", action="store_true")
args=parser.parse_args()
assets = {
    "assets/partner-baseline.js": "window.MOSIGO_PARTNER_BASELINE = Object.freeze(" + json.dumps(values) + ");\n",
    "assets/document-search.json": json.dumps(documents, ensure_ascii=False, separators=(",",":"))+"\n",
}
for file, data in assets.items():
    path=Path(file)
    if args.check:
        if path.read_text() != data:
            raise ValueError(f"{file} is stale. Run python qa/build-report-data.py")
    else:
        path.write_text(data)
print(f"PASS: {sum(map(len,documents.values()))} searchable pages, Excel and document baseline agreement")
