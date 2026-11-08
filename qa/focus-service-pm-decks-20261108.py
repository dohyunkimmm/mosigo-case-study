"""Align MOSIGO's editable decks with the service-PRD case-study direction.
Keep the 11-slide main deck and the 12-slide IR companion, charts and numeric facts.
Run AFTER legacy style/strategy/visual scripts, before preview rendering.
"""
import sys
from pathlib import Path
from pptx import Presentation

ROOT = Path("downloads")
CHANGES = {
 "strategy": {
  1: {2: "MOSIGO 서비스기획 · PRD", 3: "고객 문제 → 사용자 여정 → 핵심 기능 → UX 설계",
      5: "자녀의 대리 예약 문제를 정의하고, 사용자 흐름·핵심 기능·화면 정책으로 제품 경험을 구체화",
      9: "사용자 문제 · 페르소나 · 서비스 흐름 · 기능 요구사항"},
  4: {2: "예약자와 이용자 요구사항 정의",
      5: "자녀 대리 예약의 사용자 역할·동의·공유 범위를 기능 요구사항으로 정리"},
  10: {2: "제품 요구사항과 실행 우선순위",
       5: "문제 확인 → 제품 설계 → 사용성 확인 → 운영 타당성 판단",
       10: "문제 정의", 12: "제품 설계", 14: "운영 검토",
       16: "사용자 과업과 기능 우선순위를 단계별로 구체화"},
  11: {2: "사용자 문제에서 제품 설계까지",
       4: "사용자 문제 · 핵심 여정 · 기능 6개 · UX 설계",
       5: "", 9: "사용자 요구 · 서비스 흐름 · UX 설계 · 실행 계획"},
 },
 "ir": {
  1: {6: "MOSIGO 서비스기획 연계\n사업성·투자 조건 검토",
      7: "PRD 범위 → 운영 전제 → 사업모델 → 조건부 예산 심의"},
  12: {4: "서비스 운영 전 투자·인수 조건",
       5: "요구사항·안전 책임·제휴 공급을 확인한 뒤 조건부 투자",
       6: "기획·검수 범위 확정 → 제한 운영 검증 → 수익성 심사"},
 }
}
CARD_PAIRS = [
 ("01 / 초기 투자", "01 / 문제 정의", "01 / 문제 정의"),
 ("공급 계약·고객 수요\n단위 손익 확인", "예약자·이용자 분리\n고객 과업 확인", "자녀의 대리 예약\n정보 확인 부담 파악"),
 ("02 / 1년 차", "02 / PRD 설계", "02 / 사용자 정의"),
 ("제휴 사업모델과\n운영 책임 정교화", "역할·권한·동의\n예외 정책 정리", "자녀·부모 페르소나\n과업·동의 조건"),
 ("03 / 2년 차", "03 / 핵심 기능 검토", "03 / 핵심 기능"),
 ("지역별 사업성에 따른\n생활권 확대", "공유·변경·복구\n화면 정책 정리", "비교·신청·공유\n상태 확인 흐름"),
 ("04 / 3년 차", "04 / 실행 계획", "04 / 실행 계획"),
 ("반복수요 기반 기업·\n공공 협력 모델 검토", "운영 정책·지원 범위\n정리와 보완", "사용성 확인·공급 조건\n시범 운영 검토")
]
def set_preserving_style(shape, value):
 assert shape.has_text_frame
 tf=shape.text_frame
 paragraphs=value.split("\n")
 # Keep the existing first run formatting and editable shape position.
 for i, part in enumerate(paragraphs):
  p=tf.paragraphs[i] if i<len(tf.paragraphs) else tf.add_paragraph()
  if p.runs:
   p.runs[0].text=part
   for run in p.runs[1:]: run.text=""
  else: p.text=part
 for p in tf.paragraphs[len(paragraphs):]:
  for run in p.runs:run.text=""
 tf.word_wrap=True
 for p in tf.paragraphs:
  for run in p.runs:run.font.name="Pretendard"
def snapshot_numbers(prs):
 import re
 output=[]
 for slide in prs.slides:
  for shape in slide.shapes:
   if shape.has_chart:
    output.append(("chart",tuple(tuple(series.values) for series in shape.chart.series)))
 return output
def run(mode):
 assert mode in CHANGES
 path=ROOT/("mosigo_report.pptx" if mode=="strategy" else "MOSIGO_IR_Investment_Review_12slides.pptx")
 prs=Presentation(path);assert len(prs.slides)==(11 if mode=="strategy" else 12)
 before_charts=snapshot_numbers(prs)
 before_images=sum(sh.shape_type==13 for slide in prs.slides for sh in slide.shapes)
 updates=0
 for slide_no, shapes in CHANGES[mode].items():
  slide=prs.slides[slide_no-1]
  for idx, value in shapes.items():
   sh=slide.shapes[idx]
   assert sh.has_text_frame, (slide_no,idx)
   if sh.text!=value:
    set_preserving_style(sh,value)
    if sh.text != value:
     # Old decks contain manual a:br elements outside text runs. Clear only
     # this edited text frame and rebuild one run to avoid hidden legacy copy.
     source=sh.text_frame.paragraphs[0].runs
     oldfont=source[0].font if source else None
     size=oldfont.size if oldfont is not None else None
     bold=oldfont.bold if oldfont is not None else None
     color=None
     if oldfont is not None:
      try: color=oldfont.color.rgb
      except (AttributeError,ValueError,TypeError):pass
     sh.text_frame.clear()
     run=sh.text_frame.paragraphs[0].add_run()
     run.text=value
     run.font.name="Pretendard"
     if size is not None:run.font.size=size
     if bold is not None:run.font.bold=bold
     if color is not None:run.font.color.rgb=color
     sh.text_frame.word_wrap=True
    updates+=1
 if mode=="strategy":
  table=prs.slides[9].shapes[4].table
  assert len(table.rows)==5 and len(table.columns)==3
  revised=[
   ["단계","핵심 작업","판단 기준"],
   ["P0 문제 정의","자녀·부모 과업·동의 조건 확인","우선 고객 문제와 사용자의 필요 가설"],
   ["P1 제품 설계","비교·신청·공유 흐름과 R-01~06 정의","화면·권한·예외 정책 정리"],
   ["P2 사용성 확인","프로토타입 과업·이탈 원인 확인","사용성 문제·개선점 기록"],
   ["P3 운영 검토","공급·비용·안전·지원 책임 확인","제휴·시범 운영 가능성 검토"]
  ]
  for i,row in enumerate(table.rows):
   for j,cell in enumerate(row.cells):
    if cell.text==revised[i][j]:continue
    tf=cell.text_frame
    p=tf.paragraphs[0]
    if p.runs:
     p.runs[0].text=revised[i][j]
     for run in p.runs[1:]:run.text=""
    else:p.text=revised[i][j]
    for rest in tf.paragraphs[1:]:
     for run in rest.runs:run.text=""
    tf.word_wrap=True
    updates+=1
 if mode=="strategy":
  slide=prs.slides[10]
  for original,previous,new in CARD_PAIRS:
   candidates=[sh for sh in slide.shapes if sh.has_text_frame and sh.text.strip() in (original,previous) and sh.text.strip()!=new]
   already=[sh for sh in slide.shapes if sh.has_text_frame and sh.text.strip()==new]
   if len(candidates)==1:
    set_preserving_style(candidates[0],new);updates+=1
   elif len(already)!=1:
    raise AssertionError("Missing editable product-planning stage card: "+original)
 # In editable PPTX text, python-pptx's font.name writes the Latin face only.
 # Add explicit East Asian and complex-script faces for newly rebuilt runs.
 from pptx.oxml.xmlchemy import OxmlElement
 from pptx.oxml.ns import qn
 for slide in prs.slides:
  for sh in slide.shapes:
   frames=[sh.text_frame] if sh.has_text_frame else []
   if sh.has_table: frames.extend(cell.text_frame for row in sh.table.rows for cell in row.cells)
   for tf in frames:
    for para in tf.paragraphs:
     for run in para.runs:
      if not run.text.strip():continue
      run.font.name="Pretendard"
      props=run._r.get_or_add_rPr()
      for family in ("latin","ea","cs"):
       node=props.find(qn("a:"+family))
       if node is None:
        node=OxmlElement("a:"+family);props.append(node)
       node.set("typeface","Pretendard")
 assert snapshot_numbers(prs)==before_charts,"Existing chart numeric values changed"
 assert sum(sh.shape_type==13 for slide in prs.slides for sh in slide.shapes)==before_images
 if updates:
  prs.save(path)
 check=Presentation(path)
 assert len(check.slides)==len(prs.slides)
 assert snapshot_numbers(check)==before_charts
 assert sum(sh.shape_type==13 for slide in check.slides for sh in slide.shapes)==before_images
 for no,edits in CHANGES[mode].items():
  for idx,text in edits.items():
   assert check.slides[no-1].shapes[idx].text==text, (mode,no,idx)
 print("PASS MOSIGO",mode,"editable slides, PRD focus, charts and images intact; edits",updates)

if __name__=="__main__":run(sys.argv[1])
