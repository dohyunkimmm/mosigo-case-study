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
  1: {2: "MOSIGO 서비스기획 · PRD", 3: "고객 문제 → 요구사항 → 권한·예외 정책 → 검수·인계",
      9: "서비스 여정 · 요구사항 · 검수 · 인수 기준"},
  4: {2: "예약자와 이용자 요구사항 정의",
      5: "자녀 대리 예약의 사용자 역할·동의·공유 범위를 기능 요구사항으로 정리"},
  10: {2: "요구사항 우선순위와 검수·인계",
       5: "P0 필수 정책 → P1 구현·검수 → P2 운영 안내·인수 준비"},
  11: {2: "PRD에서 기능 검수·인계까지",
       4: "고객 요구를 정책·기능·테스트·운영 기준으로 연결"},
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
 ("01 / 초기 투자", "01 / 문제 정의"),
 ("공급 계약·고객 수요\n단위 손익 확인", "예약자·이용자 분리\n고객 과업 확인"),
 ("02 / 1년 차", "02 / PRD 설계"),
 ("제휴 사업모델과\n운영 책임 정교화", "역할·권한·동의\n예외 정책 정리"),
 ("03 / 2년 차", "03 / 기능 검수"),
 ("지역별 사업성에 따른\n생활권 확대", "공유·복구·충돌\n테스트와 조치"),
 ("04 / 3년 차", "04 / 운영 인계"),
 ("반복수요 기반 기업·\n공공 협력 모델 검토", "인수 기준·잔여 과제\n운영 안내 정리")
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
    set_preserving_style(sh,value);updates+=1
 if mode=="strategy":
  slide=prs.slides[10]
  for old,new in CARD_PAIRS:
   candidates=[sh for sh in slide.shapes if sh.has_text_frame and sh.text.strip()==old]
   already=[sh for sh in slide.shapes if sh.has_text_frame and sh.text.strip()==new]
   if len(candidates)==1:
    set_preserving_style(candidates[0],new);updates+=1
   elif len(already)!=1:
    raise AssertionError("Missing editable PRD stage card: "+old)
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
