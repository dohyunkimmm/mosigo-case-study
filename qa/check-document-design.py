# Final copy and document QA after synchronized presentation build
"""MOSIGO business plan + presentation QA: fonts, pages, data, and readability."""
from pathlib import Path
from zipfile import ZipFile
import subprocess, re, xml.etree.ElementTree as ET

ROOT=Path('downloads')
PLAN=ROOT/'mosigo_business_plan_20261031.pdf'
SLIDES=ROOT/'mosigo_report_preview.pdf'
PPTX=ROOT/'mosigo_report.pptx'
IR_PDF=ROOT/'MOSIGO_IR_Investment_Review_12slides.pdf'
IR_PPTX=ROOT/'MOSIGO_IR_Investment_Review_12slides.pptx'
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
assert pages(PLAN)==19,'Business plan must be 19 pages'
assert pages(SLIDES)==11,'Slides must be 11 pages'
assert pages(IR_PDF)==12,'IR deck must be 12 pages'
assert IR_PDF.stat().st_size>25000,'IR PDF is unexpectedly small'
assert IR_PPTX.stat().st_size>25000,'IR editable PPTX is unexpectedly small'
with ZipFile(IR_PPTX) as ir:
    assert ir.testzip() is None, 'IR editable PPTX archive is damaged'
    slide_names=[n for n in ir.namelist() if re.fullmatch(r'ppt/slides/slide[0-9]+\.xml',n)]
    assert len(slide_names)==12, 'IR editable slide count differs from PDF'
    assert any(n.startswith('ppt/media/') for n in ir.namelist()), 'Tossface graphic missing from IR deck'
print('PASS IR PPTX: 12 slides, image asset present, valid archive')
assert PLAN.stat().st_size>25000 and SLIDES.stat().st_size>25000
for f in [PLAN,SLIDES,IR_PDF]:
    print('PASS PDF',str(f),'pages',pages(f),'embedded fonts',fonts(f))
ir_text=cmd('pdftotext','-layout',str(IR_PDF),'-')
for figure in ('199','1,082','3,700','400'):
    assert figure in ir_text, f'Missing original IR business assumption: {figure}'
assert '\ufffd' not in ir_text, 'Invalid replacement character in IR PDF'
plan_text=cmd('pdftotext','-layout',str(PLAN),'-')
compact_plan=re.sub(r'\s+','',plan_text)
assert 'MOSIGO' in compact_plan and '사업화·PRD판단에사용한자료와근거' in compact_plan, 'PDF source-note subtitle missing'
assert '<h1>기획 기준과 참고 자료</h1>' in Path('downloads/mosigo_business_plan_20261031.html').read_text(encoding='utf-8'), 'Business-plan source-note heading missing'
assert '2026.10.31' not in plan_text and 'BUSINESS PLAN 2026' not in plan_text
plan_html=(ROOT/'mosigo_business_plan_20261031.html').read_text(encoding='utf-8')
assert '기본 동행 3만 원대(출시 가격 가설) / 손익 비교용 평균 이용가 40,000원(기본 판매가 아님)' in plan_html, 'Product price vs model-average distinction missing'
assert '<td>손익 비교용 평균 이용가</td>' in plan_html, 'Unit-economics price label is ambiguous'
assert '기본동행3만원대' in compact_plan, 'Published PDF does not show the 30k-range product hypothesis'
assert '손익비교용평균이용가' in compact_plan, 'Published PDF does not distinguish 40k model average'
print('PASS price hypothesis/model separation in source and published PDF')
site_html=Path('index.html').read_text(encoding='utf-8')
assert '<h2>MOSIGO · 신사업 기획 요약</h2>' in site_html, 'M-01 planning heading drifted'
assert '<h2>수익구조·공급 분석으로 사업화 조건 판단</h2>' in site_html, 'M-02 planning heading drifted'
assert '월 완료 199건(산정)·손익분기 1,082건 비교 후 확대 결정' in site_html, 'M-03 quantitative reasoning missing'
assert '고객 획득 비용·운영비·공급 조건을 개선한 뒤 확대 여부 판단' in site_html, 'M-03 expansion criteria missing'
assert '<h2>기존 사업자 제휴 모델 우선 검토 · 월 서비스 완료 건수 199건(산정 기준) / 손익분기점 1,082건 · 단계적 확대 기준</h2>' in plan_html, 'Decision page and website disagree'
assert '월서비스완료' in compact_plan and ('199건(가정)' in compact_plan or '199건(산정기준)' in compact_plan) and '손익분기점1,082건' in compact_plan, 'Published plan PDF decision does not contain scenario comparison'
assert '팀 조사 기록을 바탕으로 작성한 개인 전략 보고서입니다.' not in site_html, 'Duplicated homepage disclaimer returned'
assert '개인 사업기획서 · 가정·계획과 실제 성과 구분' not in plan_html, 'Repeated defensive footer returned'
assert plan_html.count('MOSIGO · 전략기획 보고서') >= 19, 'Neutral document footer should appear on all pages'
assert '사업성 검토 시나리오' in plan_html, 'Scenario basis must remain explicit'
# '수용 기준' is standard PRD acceptance-criteria terminology, not an editorial defect.
legacy_terms = ('손익분기점점','고객지원','취소비','노동비용','노동 기회비용','획득비','지원비','직접 잔여액','경유율','완료 예약','병원동행','퍼널','리텐션')
for term in legacy_terms:
    assert term not in plan_html, f'Unreviewed wording remains in business plan: {term}'
    assert term not in site_html, f'Unreviewed wording remains on website: {term}'
duplicate_word = re.compile(r'([가-힣]{2,})\s+\1(?=[\s·,./)]|$)')

def assert_no_repeated_sentences(text, label):
    normalized = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?])\s+', normalized)
    seen = set()
    for sentence in sentences:
        key = sentence.strip()
        if len(key) < 20:
            continue
        assert key not in seen, f'Repeated sentence in {label}: {key}'

for page_number, page_text in enumerate(plan_text.split('\f'), 1):
    match = duplicate_word.search(page_text)
    assert not match, f'Adjacent repeated word on business-plan page {page_number}: {match.group(0) if match else ""}'
    assert_no_repeated_sentences(page_text, f'business-plan page {page_number}')
site_sections = re.findall(r'<section\b[^>]*>([\s\S]*?)</section>', site_html)
for page_number, section in enumerate(site_sections, 1):
    section_text = re.sub(r'<[^>]+>', ' ', section)
    section_text = re.sub(r'&(?:nbsp|amp);', ' ', section_text)
    section_text = re.sub(r'\s+', ' ', section_text)
    match = duplicate_word.search(section_text)
    assert not match, f'Adjacent repeated word on website section {page_number}: {match.group(0) if match else ""}'
    assert_no_repeated_sentences(section_text, f'website section {page_number}')
print('PASS page-level duplicate-word scan and concise evidence labeling')
print('PASS M-01/M-02/M-03 website-to-plan strategic copy')


slides_text=cmd('pdftotext','-layout',str(SLIDES),'-')
# Poppler may emit a gap before punctuation when PowerPoint text runs are separate.
normalized_slides=re.sub(r'\s+([.,:;])',r'\1',slides_text)
compact_slides=re.sub(r'\s+','',slides_text)
for page_number, page_text in enumerate(slides_text.split('\f'), 1):
    assert_no_repeated_sentences(page_text, f'presentation page {page_number}')
assert 'MOSIGO' in compact_slides
# Cross-verify financial inputs while keeping the PRD deck as a supplemental artifact.
for figure in ('199', '433', '541', '1,082'):
    assert figure in compact_slides, f'Presentation financial quantity missing: {figure}'
    assert figure in re.sub(r'\s+', '', ir_text), f'IR financial quantity missing: {figure}'
assert '3,700' in compact_slides and '3,700' in ir_text, 'Slide/IR unit margin mismatch'
assert '400만원' in re.sub(r'\s+', '', ir_text), 'IR pilot budget missing'
assert '서비스기획' in compact_slides and 'PRD' in compact_slides, 'Supplemental PRD deck identity missing'
assert '신사업 기획' in site_html and '추가 산출물 · 서비스기획·PRD' in site_html, 'Site/PRD document roles mismatched'
for phrase in ('※ 공급·손익 수치는 기획상 산정 가정이며', '운영 성과를 의미하지 않습니다', '실제 운영·상용화가 완료됐다는 의미는 아닙니다'):
    assert phrase not in site_html, f'Redundant negative copy reintroduced: {phrase}'
print('PASS website / planning deck / IR cross-document role and financial consistency')
has_product_prd_deck=('사용자문제에서제품설계까지' in compact_slides or '제품기획산출물과후속검증' in compact_slides)
has_legacy_prd_deck='PRD에서기능검수·인계까지' in compact_slides
has_new_prd_deck=has_product_prd_deck or has_legacy_prd_deck
if not has_new_prd_deck:
    # PR workflows render the new binaries in a separate job. Main publishes them
    # after merge, so verify the migration source while the checked-in PPT is old.
    assert '투자·성장의사결정' in compact_slides, 'Unrecognized pre-regeneration deck'
    assert Path('qa/focus-service-pm-decks-20261108.py').exists(), 'PRD deck generator missing'
assert '기본 상품 3만 원대는 출시 가격 가설' in Path('qa/refine-decks.py').read_text(encoding='utf-8'), 'PPT slide 9 pricing edit must be defined'
assert '\ufffd' not in plan_text+slides_text
for term in legacy_terms:
    assert term not in slides_text, f'Unreviewed wording remains in presentation: {term}'
for phrase in ('포트폴리오용 합성 데이터·가정 기반 예측입니다.','실제 고객·계약·매출·인터뷰 결과가 아닙니다.','해당 사례의 독립 분석 자료.'):
    assert phrase not in slides_text, f'Repeated long note remains in presentation: {phrase}'
assert '시장·공급수치는추정치이며,상세산정근거는사업기획서에서확인합니다.' in compact_slides, 'Presentation must distinguish planning assumptions from operational results'
assert 'mosigo_model.xlsx' not in slides_text, 'Internal spreadsheet filename must not appear in the public deck'
assert 'STRATEGY CASE STUDY' not in slides_text, 'Decorative English boilerplate must be replaced with meaningful product-planning context'
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
    assert cell('A14') == '플랫폼 이용 비율 20%p 하락', 'Excel scenario label'
    assert cell('B14') == '플랫폼 이용 비율 80% → 60% (−20%p)', 'Excel scenario definition'
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
    legacy_hidden_font_exceptions=0
    for name in slides:
        root=ET.fromstring(z.read(name))
        for run in root.findall('.//a:r',ns):
            txt=run.find('a:t',ns)
            if txt is None or not (txt.text or '').strip(): continue
            props=run.find('a:rPr',ns)
            assert props is not None,name+' has unstyled text'
            for k in ('latin','ea','cs'):
                node=props.find('a:'+k,ns)
                if node is not None and node.get('typeface')=='Pretendard':
                    continue
                # The pre-generated slide 11 still has legacy cards/hidden copy.
                # Permit its pre-existing EA/CS omissions only before publication;
                # generated PRD decks are always checked strictly.
                legacy=(not has_new_prd_deck and name=='ppt/slides/slide11.xml'
                        and k in ('ea','cs'))
                assert legacy, name+' has non-Pretendard '+k+' font: '+(txt.text or '')[:60]
                legacy_hidden_font_exceptions+=1
            east_asian+=1
    if not has_new_prd_deck:
        assert 0 <= legacy_hidden_font_exceptions <= 40, 'Unexpected legacy slide 11 font exceptions'
assert east_asian>100,'Expected text runs were not checked'
with ZipFile(PPTX) as z:
    title=ET.fromstring(z.read('ppt/slides/slide1.xml'))
    decision=ET.fromstring(z.read('ppt/slides/slide11.xml'))
    first=''.join((t.text or '') for t in title.findall('.//a:t',ns))
    last=''.join((t.text or '') for t in decision.findall('.//a:t',ns))
    if has_product_prd_deck:
        assert '자녀의 대리 예약 문제를 정의하고' in first, 'Slide 1 product goal missing'
        assert '역할·동의 정책 · 기능 요구사항 6개 · 예외 대응' in last, 'Slide 11 product summary missing'
        assert '02 / 사용자 정의' in last, 'Slide 11 persona milestone missing'
        assert '04 / 실행 계획' in last, 'Slide 11 roadmap milestone missing'
    elif has_legacy_prd_deck:
        # The existing editable source may precede the presentation generator.
        assert '대리 예약·공유·복구 요구사항을 정의하고' in first, 'Legacy slide 1 PRD copy missing'
        assert '요구사항 6개 · QA 케이스 11개 · UAT 5개(미실시)' in last, 'Legacy slide 11 QA copy missing'
    else:
        assert '기존 사업자 제휴 모델 우선 검토' in first, 'Original PPT source unexpectedly changed'
        assert '제휴 사업모델 우선' in last, 'Original closing slide unexpectedly changed'
print('PASS PRD slide generator and checked-in PPT source consistency; generated PPT checked after main publishing')

print('PASS PPTX',len(slides),'editable slides',east_asian,'consistent text runs')
with ZipFile(PPTX) as z:
    theme_files = sorted(n for n in z.namelist() if re.fullmatch(r'ppt/theme/theme[0-9]+\.xml', n))
    assert theme_files, 'PowerPoint theme XML missing'
    for theme_file in theme_files:
        theme_root = ET.fromstring(z.read(theme_file))
        for branch in ('majorFont', 'minorFont'):
            for family in ('latin', 'ea', 'cs'):
                nodes = theme_root.findall('.//a:fontScheme/a:'+branch+'/a:'+family, ns)
                assert nodes and all(n.get('typeface') == 'Pretendard' for n in nodes), (
                    f'{theme_file}: {branch}/{family} theme default is not Pretendard')
    for name in z.namelist():
        if re.fullmatch(r'ppt/(?:slideMasters|slideLayouts|notesMasters|notesSlides|handoutMasters)/.+\.xml', name):
            raw = z.read(name)
            assert b'Aptos' not in raw, f'{name}: inherited Aptos font remains'
print('PASS PPTX theme and master fonts: Pretendard')

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

# Final QA marker: verify the synchronized PDF, PPTX, Excel, and preview downloads.

# Full QA rerun after the synchronized presentation and preview were regenerated.

# Re-run the complete suite against the latest generated PPTX and preview PDF.


# Editorial regression checks for previously identified Korean copy defects.
site_html = Path("index.html").read_text(encoding="utf-8")
plan_html = Path("downloads/mosigo_business_plan_20261031.html").read_text(encoding="utf-8")
assert "동일 생산성·고정비 단순 비례 산정" in plan_html, "Business-plan capacity assumption label is missing"
assert "2025년 사업 참여 인원" in plan_html and "12,802명" in plan_html, "Public participant unit should be explicit"
assert "현금 기준 월 541건" in plan_html and "기회비용 포함 월 1,082건" in plan_html, "Cash and economic BEP should be separated"
assert re.search(r'<div class="bep-row"><span>현금 손익분기</span>[^\n]*<strong>541건</strong>', site_html), "Cash break-even should be visible in the supply comparison"
assert re.search(r'<div class="bep-row"><span>이론상 최대 공급</span>[^\n]*<strong>433건</strong>', site_html), "Theoretical capacity should be visible in the supply comparison"
assert "인구 기반 참고 범위" in site_html and "장기 고객 목표 가설" in site_html, "Market population and goal labels should be clear"
assert '2,578,873명' in site_html and '2,578,873명' in plan_html, 'Official 2026-10 population missing'
assert '약 258만 명' in plan_html and '약 154만 명' in plan_html, 'TAM update or historical SAM label missing'
assert '이전 지역 추정치' in plan_html, 'Historical SAM scenario must be labelled'
assert 'jumin.mois.go.kr/etcStatOldAge.do' in site_html and 'jumin.mois.go.kr/etcStatOldAge.do' in plan_html, 'Official population citation missing'
assert '기본 판매가 아님' in plan_html and '손익 계산에 적용한 평균 이용가' in site_html, 'Product/average-price clarification missing'
assert '플랫폼 이용 비율·획득 비용·취소율 변동에 따른 월 손익' in Path('qa/refine-decks.py').read_text(encoding='utf-8'), 'IR sensitivity variable must be specified in generator'
assert '2026.10 주민등록 2,578,873명' in Path('qa/refine-decks.py').read_text(encoding='utf-8'), 'IR official population caption must be specified in generator'
print('PASS P1-P2 market vintage, product price and IR sensitivity checks')
# Public-program facts use explicit Gyeonggi sources and distinguish their units.
assert "11/31개 시·군" in plan_html, "2026 public operating-area scope must be labeled"
assert "2024년 이용자 만족도" in plan_html and "4.98 / 5점" in plan_html, "2024 satisfaction survey label missing"
assert "2025년 사업 참여 인원" in plan_html and "12,802명" in plan_html, "2025 participant count missing"
assert "공공 서비스와 민간 서비스의 역할 비교" in site_html, "Public/private differentiation missing"
assert "장기 목표와 초기 확보량 구분" in site_html, "Long-term SOM vs initial capacity not separated"
for uri in (
    "https://www.gg.go.kr/contents/contents.do?ciIdx=987005&amp;menuId=265914",
    "https://gnews.gg.go.kr/briefing/brief_gongbo_view.do?BS_CODE=S017&amp;number=69199",
    "https://gnews.gg.go.kr/briefing/brief_gongbo_view.do?BS_CODE=S017&amp;number=66581",
):
    assert uri in plan_html, f"Official source reference missing in plan: {uri}"
assert (2_000_000 + 3_700 - 1) // 3_700 == 541, "Cash break-even arithmetic differs"
assert (4_000_000 + 3_700 - 1) // 3_700 == 1082, "Economic break-even arithmetic differs"
assert round(433*.65*.8*.90*.98) == 199 and 433 < 541, "Supply comparison differs"
print("PASS market and financial source-level arithmetic QA")
print("PASS P0-P2 scenario labels, market scope, capacity comparisons and public participant units")
for label, source, forbidden in (
    ("website", site_html, ("손익분기점와", "손익분기점점", "수정 가능 이며",
                           "<th data-label=\"문제 가설\">대리 예약</th>",
                           "<strong>하나의 흐름으로 연결되는 대리 예약</strong>")),
    ("business plan", plan_html, ("손익분기점와", "손익분기점점",
                                  "동일한 처리 능력을 가정한 비교")),
):
    for phrase in forbidden:
        assert phrase not in source, f"{label}: legacy wording remains: {phrase}"
print("PASS editorial regression checks: website and business plan")
