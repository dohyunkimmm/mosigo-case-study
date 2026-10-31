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
compact_plan=re.sub(r'\\s+','',plan_text)
assert 'MOSIGO' in compact_plan and '기획기준과참고자료' in compact_plan
assert '2026.10.31' not in plan_text and 'BUSINESS PLAN 2026' not in plan_text
slides_text=cmd('pdftotext','-layout',str(SLIDES),'-')
compact_slides=re.sub(r'\\s+','',slides_text)
assert 'MOSIGO' in compact_slides and '사업화의사결정' in compact_slides
assert '\ufffd' not in plan_text+slides_text
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
