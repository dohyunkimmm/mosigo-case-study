"""Apply the reviewed sensitivity-scenario labels and preserve the workbook package.

The Excel source values and formula were first edited/recalculated with artifact_tool.
This script transports those four corrected XML cells into the deployed Office package,
preserving every other workbook member byte-for-byte after extraction.
"""
from pathlib import Path
from zipfile import ZipFile
from tempfile import NamedTemporaryFile
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

# Additional wording clarifications found during page-by-page review.
label_patches["xl/worksheets/sheet1.xml"]["C8"] = (
    "결제 수수료·고객 지원·시스템 이용·고객 획득 비용 차감",
    "결제 수수료·고객 지원 비용·시스템 이용 비용·고객 획득 비용 차감",
)
label_patches["xl/worksheets/sheet2.xml"]["A19"] = ("초기 투자비", "초기 투자비(별도 가정)")
label_patches["xl/worksheets/sheet2.xml"]["C26"] = (
    "본문의 직접형 예시 연 고정비 1억 원과 별도 시나리오",
    "초기 투자비 500만 원은 월 손익·손익분기 계산에서 제외하며, 직접 운영형 연 고정비 1억 원은 별도 비교 시나리오입니다.",
)
label_patches["xl/worksheets/sheet3.xml"]["A12"] = ("취소 제외 비율", "취소를 제외한 비율")
label_patches["xl/worksheets/sheet3.xml"]["C23"] = (
    "배정·교육·고객지원 비용 증가를 반영해 필요 인원 재산정",
    "배정·교육·고객 지원 비용 증가를 반영해 필요 인원을 다시 산정",
)
label_patches["xl/worksheets/sheet4.xml"]["A11"] = (
    "직접 운영형 금액은 고객 지원·고객 획득 비용 차감 전 / 구독은 월 3회 모두 이용하는 것으로 가정 / 차량 원가는 추정치",
    "직접 운영형 잔여 금액은 고객 지원 비용과 고객 획득 비용을 차감하기 전 금액입니다. 구독은 월 3회 이용, 차량 원가는 추정치로 가정했습니다.",
)
label_patches["xl/worksheets/sheet5.xml"]["C9"] = (
    "원문·수집 기준 추가 확인",
    "원문과 수집 기준을 추가로 확인해야 함",
)
label_patches["xl/worksheets/sheet5.xml"]["A20"] = (
    "민감도 분석은 계획 가정의 변화에 따른 비교이며, 실제 실험 결과는 근거 확보 후 별도 기록",
    "민감도 분석은 계획 가정의 변화에 따른 비교이며, 실제 실험 결과는 근거를 확보한 뒤 별도로 기록합니다.",
)

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

print("PASS Excel sensitivity scenario labels and recalculated values")

# Rebuild marker: regenerate the current reviewed MOSIGO document deliverables.


# Harmonize workbook terminology across all five sheets while preserving formulas,
# cached formula results, chart relationships, and the original Office package.
from xml.sax.saxutils import escape as xml_escape

label_patches = {
    "xl/worksheets/sheet1.xml": {
        "A6": ("월 완료 예약", "월 서비스 완료 건수"),
        "A7": ("제휴 수수료 매출", "월 제휴 수수료 매출"),
        "A8": ("공헌이익/건", "건당 공헌이익"),
        "C8": ("결제·지원·IT·획득비 차감", "결제 수수료·고객 지원·시스템 이용·고객 획득 비용 차감"),
        "A9": ("경제적 손익", "월 손익(인력 투입 기회비용 반영)"),
        "C9": ("고정비·노동비용 포함", "고정비·인력 투입 기회비용 포함"),
        "A10": ("손익분기 예약", "월 손익분기 완료 건수"),
        "A13": ("권고 · 기존 사업자 제휴 방식으로 범위를 제한하고, 고객 획득 비용·운영 비용 확인 후 확대 여부 판단", "권고 · 기존 사업자 제휴로 운영 범위를 제한하고, 고객 획득 비용과 운영비를 확인한 뒤 확대 여부를 판단"),
        "A15": ("수요 가정 월 1,875건 / 초기 공급 월 199건 / 손익분기 월 1,082건", "수요 가정 1,875건/월 · 초기 공급 199건/월 · 손익분기점 1,082건/월"),
    },
    "xl/worksheets/sheet2.xml": {
        "A6": ("객단가", "평균 이용가"),
        "A7": ("수수료율", "중개 수수료율"),
        "A8": ("결제비율", "결제 수수료율"),
        "A9": ("완료 건 고객지원비", "완료 건당 고객 지원 비용"),
        "A10": ("시스템 비용", "건당 시스템 이용 비용"),
        "A11": ("신규고객 비중", "신규 고객 비중"),
        "A12": ("신규 고객 획득비", "신규 고객 획득 비용"),
        "A14": ("노동 기회비용", "인력 투입 기회비용"),
        "A15": ("매니저 주간 가능 시간", "매니저 1명당 주간 가용 시간"),
        "A16": ("건당 소요 시간", "완료 1건당 소요 시간"),
        "A19": ("초기 투자", "초기 투자비"),
        "A20": ("공급 단위 수", "매니저 수"),
        "A21": ("가동·충원율", "가동률"),
        "A22": ("플랫폼 경유율", "플랫폼 이용 비율"),
        "C24": ("기본 동행 상품은 3만 원대 가정 / 손익 계산용 평균 이용가 40,000원", "기본 동행 상품은 3만 원대 상품 가정 / 손익 계산에는 평균 이용가 40,000원 적용"),
        "C25": ("제휴형 월 고정비 200만 원 + 노동 기회비용 200만 원", "제휴형 월 고정비 200만 원 + 인력 투입 기회비용 200만 원"),
    },
    "xl/worksheets/sheet3.xml": {
        "A2": ("매니저 공급능력과 제휴형 사업성", "매니저 공급 역량과 제휴형 사업성"),
        "A7": ("주간 가능 시간", "매니저 1명당 주간 가용 시간"),
        "A8": ("건당 소요 시간", "완료 1건당 소요 시간"),
        "A9": ("월 공급 가능 건수", "월 최대 공급 가능 건수"),
        "A11": ("경유율", "플랫폼 이용 비율"),
        "A12": ("취소 후 비율", "취소 제외 비율"),
        "A14": ("월 완료 예약", "월 서비스 완료 건수"),
        "A15": ("수수료 매출", "월 제휴 수수료 매출"),
        "A16": ("공헌이익/건", "건당 공헌이익"),
        "A17": ("월 운영 손익(기회비용 제외)", "월 운영 손익(인력 투입 기회비용 제외)"),
        "A18": ("인력 투입 기회비용 반영 월 손익", "월 손익(인력 투입 기회비용 반영)"),
        "A19": ("손익분기 예약", "월 손익분기 완료 건수"),
        "A20": ("필요 매니저", "손익분기 달성에 필요한 매니저 수"),
    },
    "xl/worksheets/sheet4.xml": {
        "C5": ("직접 변동비", "직접 운영형 변동비"),
        "D5": ("직접 잔여액", "변동비 차감 후 금액"),
        "E5": ("제휴 공헌이익", "제휴형 건당 공헌이익"),
        "A8": ("월3회 구독", "월 3회 구독"),
        "A11": ("직접 운영형 금액은 고객 지원 비용·고객 획득 비용 차감 전 / 구독은 월 3회 모두 이용 가정 / 차량 원가는 추정치", "직접 운영형 금액은 고객 지원·고객 획득 비용 차감 전 / 구독은 월 3회 모두 이용하는 것으로 가정 / 차량 원가는 추정치"),
        "C13": ("기본 동행 상품은 3만 원대 가정이며, 손익 계산에는 평균 이용가 40,000원을 적용", "기본 동행 상품은 3만 원대 상품 가정이며, 손익 계산에는 평균 이용가 40,000원을 적용합니다."),
    },
    "xl/worksheets/sheet5.xml": {
        "A6": ("수수료 0% 공헌이익", "중개 수수료 0%일 때 공헌이익"),
        "A7": ("공급 가능 범위 내 여부", "월 공급 가능 범위 충족 여부"),
        "C7": ("완료 예약 ≤ 공급 건수", "완료 건수 ≤ 월 최대 공급 가능 건수"),
        "A8": ("기본 가격 연결", "기본 동행 가격 일치 여부"),
        "C8": ("기본 상품 가격과 가정 객단가 비교", "기본 동행 가격과 평균 이용가 비교"),
        "C12": ("공헌이익/건", "건당 공헌이익"),
        "D12": ("완료 예약/월", "완료 건수/월"),
        "E12": ("인력 기회비용 반영 손익", "월 손익(인력 투입 기회비용 반영)"),
        "F12": ("손익분기/월", "손익분기 완료 건수/월"),
        "A15": ("고객 획득비 2배", "고객 획득 비용 2배"),
        "B15": ("신규 고객 획득비 × 2", "신규 고객 획득 비용 × 2"),
        "B18": ("완료 예약 0건 가정", "서비스 완료 건수 0건 가정"),
        "A20": ("민감도 결과는 계획 가정의 변화 비교 / 실험 결과는 근거 확보 후 별도 기록", "민감도 분석은 계획 가정의 변화에 따른 비교이며, 실제 실험 결과는 근거 확보 후 별도 기록"),
    },
}

with ZipFile(model) as archive:
    members = [(info, archive.read(info.filename)) for info in archive.infolist()]
    replacements = {}
    changed_any = False
    for filename, edits in label_patches.items():
        source = next(data.decode("utf-8") for info, data in members if info.filename == filename)
        for coordinate, (before, after) in edits.items():
            pattern = r'<x:c r="' + re.escape(coordinate) + r'"[^>]*>.*?</x:c>'
            matches = re.findall(pattern, source, re.S)
            assert len(matches) == 1, (filename, coordinate, "missing or duplicate cell")
            old_cell = matches[0]
            before_xml, after_xml = xml_escape(before), xml_escape(after)
            if after_xml in old_cell:
                continue
            assert before_xml in old_cell, (filename, coordinate, "unexpected current value")
            new_cell = old_cell.replace(before_xml, after_xml)
            assert new_cell != old_cell
            source = source.replace(old_cell, new_cell, 1)
            changed_any = True
        replacements[filename] = source.encode("utf-8")

if changed_any:
    with NamedTemporaryFile(dir=model.parent, suffix=".xlsx", delete=False) as tmp:
        temp_name = tmp.name
    try:
        with ZipFile(temp_name, "w") as patched:
            for info, data in members:
                patched.writestr(info, replacements.get(info.filename, data))
        with ZipFile(temp_name) as verify:
            assert verify.testzip() is None, "Workbook archive damaged after terminology patch"
            for filename, edits in label_patches.items():
                source = verify.read(filename).decode("utf-8")
                for coordinate, (_, after) in edits.items():
                    pattern = r'<x:c r="' + re.escape(coordinate) + r'"[^>]*>.*?</x:c>'
                    cell = re.findall(pattern, source, re.S)
                    assert len(cell) == 1 and xml_escape(after) in cell[0], (filename, coordinate, after)
            # Formula and cached result in the operating model must remain intact.
            sheet1 = verify.read("xl/worksheets/sheet1.xml").decode("utf-8")
            assert '<x:c r="B9"' in sheet1 and "<x:v>-3263700</x:v>" in sheet1
        os.replace(temp_name, model)
    finally:
        if os.path.exists(temp_name):
            os.remove(temp_name)

print("PASS workbook terminology harmonization: 57 labels across 5 sheets; formulas, cached results, and chart package preserved")
