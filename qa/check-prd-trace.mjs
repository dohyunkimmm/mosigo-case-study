import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = path => readFileSync(path, 'utf8');
const prd = read('downloads/mosigo_prd_delivery.html');
const appendix = read('qa/internal/verification-appendix.html');
const site = read('index.html');
const plan = read('downloads/mosigo_business_plan_20261031.html');
const deck = read('qa/final-presentation-readability-20261108.py');
const source = read('qa/focus-service-pm-decks-20261108.py');

const sections = ['project-overview','objective','personas','success-metrics',
  'prd-requirements','user-stories','ux-design','prd-scope','technical',
  'dependencies','timeline','risks','supporting'];
for (const id of sections) assert.ok(prd.includes('id="' + id + '"'), 'missing PRD section ' + id);
assert.equal((prd.match(/<section\b/g) || []).length, 13, 'PRD follows 13-section product template');
for (let i=1;i<=6;i++) assert.ok(prd.includes('<strong>R-0' + i + '</strong>'), 'missing product requirement R-0' + i);

for (const term of ['Overview','Objectives','Personas','Metrics','Requirements','User Stories','UX Design',
  'Scope','Technical Requirements','Dependencies','Timeline','Open Questions','References','측정 설계 단계','페르소나 가설']) {
  assert.ok(prd.includes(term), 'PRD missing product planning element: ' + term);
}
assert.ok(prd.includes('<h1>MOSIGO PRD</h1>') && !prd.includes('문서 기준'), 'PRD title should stay concise');
assert.ok(prd.includes('min-width:990px;table-layout:fixed') && (prd.match(/data-label="ID"/g) || []).length===6, 'requirements ID column stays readable');
assert.ok(!prd.includes('mosigo_qa_appendix.html'), 'Public PRD must not link technical QA records');
for (const technicalTerm of ['github.com','PATCH 403','176건 통과','TC-03-04']) {
  assert.ok(!prd.includes(technicalTerm), 'Technical evidence leaked into product PRD: ' + technicalTerm);
}

const tc = ['TC-02-01','TC-03-01','TC-03-02','TC-03-03','TC-03-04',
  'TC-03-05','TC-04-01','TC-04-02','TC-01-01','TC-05-01','TC-06-01'];
for (const id of tc) assert.ok(appendix.includes(id), 'optional QA appendix missing ' + id);
for (let i=1;i<=5;i++) assert.ok(appendix.includes('UAT-0' + i), 'optional UAT appendix missing ' + i);
assert.ok(appendix.includes('176건 통과'), 'appendix preserves verified QA evidence');
assert.ok(site.includes('고객 문제와 목표, 사용자 페르소나, 서비스 흐름, 핵심 기능 6개'));
assert.ok(!site.includes('mosigo_qa_appendix.html') && !site.includes('QA·인수인계'), 'Public portfolio must not expose QA appendix or QA handoff claims');
assert.ok(site.includes('핵심 사용자 페르소나') && site.includes('2유형'), 'portfolio hero must present personas, not QA counts');
assert.ok(!site.includes('기능 검수') && !site.includes('인수인계'), 'public portfolio uses product planning vocabulary');
assert.ok(plan.includes('사용자 경험 중심 제품 요구사항'));
assert.ok(plan.includes('탐색부터 대리 신청·진행 공유까지'));
assert.equal((plan.match(/<section\b/g) || []).length, 19, 'business plan page count');
assert.ok(deck.includes('대리 예약의 핵심 경험과 요구사항'));
assert.ok(source.includes('사용자 문제에서 제품 설계까지'));
assert.ok(source.includes('P1 제품 설계'));

// Cross-document editorial QA: identical KPI labels and product-planning framing.
for (const metric of ['예약 확정률','매니저 선택 성공률','90일 내 재예약률']) {
  for (const [name,doc] of [['PRD',prd],['site',site],['business plan',plan]]) {
    assert.ok(doc.includes(metric), name+' uses a mismatched KPI label: '+metric);
  }
}
assert.ok(prd.includes('상태 이해도') && site.includes('상태 이해도'),
  'PRD and website state-understanding metric differ');
const siteJourney = site.match(/<ol class="skim-journey">([\s\S]*?)<\/ol>/);
assert.ok(siteJourney && (siteJourney[1].match(/<li>/g) || []).length === 7,
  'Website journey must retain 7 steps');
assert.ok(prd.includes('상세 7단계 보기') && (prd.match(/<article><strong>0[1-5] /g) || []).length === 5,
  '5-step PRD summary must link to detailed 7-step site flow');
assert.ok(source.includes('사용자 문제에서 제품 설계까지') && deck.includes('핵심 과업 · 4가지'),
  'slide 7/10/11 product journey and task summary drifted');
assert.ok(plan.includes('대리 신청·진행 공유·변경 흐름과 사용자 과업 검증'),
  'business-plan G2 must emphasize user tasks over test code');
assert.ok(site.includes('MOSIGO · 고객 문제에서 제품 설계까지'),
  'portfolio intro must lead with product planning');
assert.ok(!prd.includes('완료된 결과물은 아닙니다.'),
  'remove repeated defensive phrasing from user-facing PRD');
assert.ok(!site.includes('QA 테스트 케이스 11개'),
  'QA proof should not dominate the core deliverable');
console.log('PASS cross-document KPI, user journey and editorial QA');

console.log('PASS product-centered PRD: 13 sections, 6 requirements; technical QA confined to private repository');
