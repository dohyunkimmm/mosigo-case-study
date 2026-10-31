"""MOSIGO business plan + presentation QA: fonts, pages, data, and readability."""
from pathlib import Path
from zipfile import ZipFile
import subprocess, re, xml.etree.ElementTree as ET

ROOT=Path('downloads')
PLAN=ROOT/'mosigo_business_plan_20261031.pdf'
SLIDES=ROOT/'mosigo_report_preview.pdf'
PPTX=ROOT/'mosigo_report.pptx'
def cmd(*args):
    return subprocess.check_output(args,text=True,stderr=subprocess.STDOUT)
def pages(p):
    m=re.search(r'^Pages:\s*(\d+)\s*$',cmd('pdfinfo',str(p)),re.M)
    assert m, f'Invalid pdfinfo output: {p}'
    return int(m.group(1))
def fonts(p):
    info=cmd('pdffonts',str(p))
    assert 'Pretendard' in info, f'Pretendard not embedded in {p}'
    return sorted(set(re.findall(r'Pretendard-[A-Za-z]+',info)))
assert pages(PLAN)==17,'Business plan must be 17 pages'
assert pages(SLIDES)==11,'Slides must be 11 pages'
assert PLAN.stat().st_size>25000 and SLIDES.stat().st_size>25000
for f in [PLAN,SLIDES]:
    print('PASS PDF',str(f),'pages',pages(f),'embedded fonts',fonts(f))
plan_text=cmd('pdftotext','-layout',str(PLAN),'-')
compact_plan=re.sub(r'\s+','',plan_text)
assert 'MOSIGO' in compact_plan and '기획기준과참고자료' in compact_plan
assert '2026.10.31' not in plan_text and 'BUSINESS PLAN 2026' not in plan_text
plan_html=(ROOT/'mosigo_business_plan_20261031.html').read_text(encoding='utf-8')
assert '기본 동행 3만 원대(상품 가정) / 평균 40,000원(손익 비교용)' in plan_html, 'Product price vs model-average distinction missing'
assert '<td>손익 비교용 평균 이용가</td>' in plan_html, 'Unit-economics price label is ambiguous'
assert '기본동행3만원대' in compact_plan, 'Published PDF does not show the 30k-range product hypothesis'
assert '손익비교용평균이용가' in compact_plan, 'Published PDF does not distinguish 40k model average'
print('PASS price hypothesis/model separation in source and published PDF')
site_html=Path('index.html').read_text(encoding='utf-8')
assert '<h2>MOSIGO · 고객·시장 분석에서 사업화 전략 결정까지</h2>' in site_html, 'M-01 heading drifted'
assert '<h2>수요·공급·손익 격차로 사업화 가능성을 판단한다</h2>' in site_html, 'M-02 heading drifted'
assert '월 완료 199건과 손익분기 1,082건의 격차를 고려해' in site_html, 'M-03 quantitative reasoning missing'
assert '고객 획득비·운영비·공급 조건 검증 전 확대를 보류' in site_html, 'M-03 expansion gate missing'
assert '<h2>제휴형 우선 검토 · 월 완료 199건 대비 손익분기 1,082건 · 확대 보류</h2>' in plan_html, 'Decision page and website disagree'
assert '월완료199건대비손익분기1,082건' in compact_plan, 'Published plan PDF decision does not contain comparison'
print('PASS M-01/M-02/M-03 website-to-plan strategic copy')


slides_text=cmd('pdftotext','-layout',str(SLIDES),'-')
compact_slides=re.sub(r'\s+','',slides_text)
assert 'MOSIGO' in compact_slides and '사업화의사결정' in compact_slides
assert '\ufffd' not in plan_text+slides_text
assert '사업기획서3쪽' in compact_slides, 'Slide 2 source citation must point to current plan p3'
assert '11~12쪽' not in slides_text, 'Obsolete source page reference remains'
with ZipFile(ROOT/'mosigo_model.xlsx') as model:
    assert model.testzip() is None, 'Excel archive damaged'
    sheet = ET.fromstring(model.read('xl/worksheets/sheet5.xml'))
    xn = {'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    def cell(address, tag='v'):
        node=sheet.find(".//x:c[@r='"+address+"']/x:"+tag,xn)
        assert node is not None, (address, tag)
        return node.text
    assert cell('A14') == '경유율 20%p 하락', 'Excel scenario label'
    assert cell('B14') == '기준 80% → 60% (−20%p)', 'Excel scenario definition'
    assert "('가정'!B22-20%)" in cell('D14','f'), 'Excel scenario formula'
    assert cell('D14') == '149', 'Excel completed count'
    assert cell('E14') == '-3448700', 'Excel monthly economic profit'
print('PASS cross-document scenarios: 80% to 60%, 149, -3,448,700, PPT p3 reference')

ns={'a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
with ZipFile(PPTX) as z:
    assert z.testzip() is None,'PPTX archive corrupt'
    slides=sorted(n for n in z.namelist() if re.fullmatch(r'ppt/slides/slide\d+\.xml',n))
    assert len(slides)==11,'PPTX slide count mismatch'
    east_asian=0
    for name in slides:
        root=ET.fromstring(z.read(name))
        for run in root.findall('.//a:r',ns):
            txt=run.find('a:t',ns)
            if txt is None or not (txt.text or '').strip(): continue
            props=run.find('a:rPr',ns)
            assert props is not None,name+' has unstyled text'
            for k in ('latin','ea','cs'):
                node=props.find('a:'+k,ns)
                assert node is not None and node.get('typeface')=='Pretendard',name+' has non-Pretendard '+k+' font'
            east_asian+=1
assert east_asian>100,'Expected text runs were not checked'
with ZipFile(PPTX) as z:
    title=ET.fromstring(z.read('ppt/slides/slide1.xml'))
    decision=ET.fromstring(z.read('ppt/slides/slide11.xml'))
    first=''.join((t.text or '') for t in title.findall('.//a:t',ns))
    last=''.join((t.text or '') for t in decision.findall('.//a:t',ns))
    assert '제휴형 우선 검토, 획득비·운영비·공급 조건 검증 전 확대 보류' in first, 'Slide 1 decision not synchronized'
    assert '제휴형 우선 검토 · 월 199건 대비 손익분기 1,082건' in last, 'Slide 11 quantified recommendation missing'
    assert '획득비·운영비·공급 조건 검증 전 확대 보류' in last, 'Slide 11 expansion gate missing'
print('PASS PPT cover and decision wording synchronized with case study')

print('PASS PPTX',len(slides),'editable slides',east_asian,'consistent text runs')
def rgb(hexcode):
    return [int(hexcode[i:i+2],16)/255 for i in (0,2,4)]
def lum(h):
    vals=[c/12.92 if c<=.04045 else ((c+.055)/1.055)**2.4 for c in rgb(h)]
    return sum(x*y for x,y in zip(vals,(.2126,.7152,.0722)))
def ratio(a,b):
    x,y=lum(a),lum(b)
    return (max(x,y)+.05)/(min(x,y)+.05)
for a,b in [('FFFFFF','123E33'),('192C25','FBFCF8'),('4F6958','FBFCF8'),('D6EF8A','0D3028')]:
    score=ratio(a,b)
    assert score>=4.5, f'Brand contrast below AA: {a}/{b}={score:.2f}'
    print('PASS color contrast',a,b,round(score,2))
print('PASS full document QA')
