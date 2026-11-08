import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const read = path => readFileSync(path, 'utf8');
const prd = read('downloads/mosigo_prd_delivery.html');
const appendix = read('downloads/mosigo_qa_appendix.html');
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

for (const term of ['사용자 페르소나','사용자 스토리','성공 지표','UX·화면 설계',
  '추진 일정','미해결 질문·위험 요소','측정 설계 단계','페르소나 가설']) {
  assert.ok(prd.includes(term), 'PRD missing product planning element: ' + term);
}
assert.ok(prd.includes('mosigo_qa_appendix.html'), 'PRD must link optional technical appendix');
for (const technicalTerm of ['github.com','PATCH 403','176건 통과','TC-03-04']) {
  assert.ok(!prd.includes(technicalTerm), 'Technical evidence leaked into product PRD: ' + technicalTerm);
}

const tc = ['TC-02-01','TC-03-01','TC-03-02','TC-03-03','TC-03-04',
  'TC-03-05','TC-04-01','TC-04-02','TC-01-01','TC-05-01','TC-06-01'];
for (const id of tc) assert.ok(appendix.includes(id), 'optional QA appendix missing ' + id);
for (let i=1;i<=5;i++) assert.ok(appendix.includes('UAT-0' + i), 'optional UAT appendix missing ' + i);
assert.ok(appendix.includes('176건 통과'), 'appendix preserves verified QA evidence');
assert.ok(site.includes('고객 문제와 목표, 사용자 페르소나, 서비스 흐름, 핵심 기능 6개'));
assert.ok(site.includes('mosigo_qa_appendix.html'), 'tech evidence remains separately accessible');
assert.ok(plan.includes('사용자 경험 중심 제품 요구사항'));
assert.ok(plan.includes('탐색부터 대리 신청·진행 공유까지'));
assert.equal((plan.match(/<section\b/g) || []).length, 19, 'business plan page count');
assert.ok(deck.includes('대리 예약의 핵심 경험과 요구사항'));
assert.ok(source.includes('사용자 문제에서 제품 설계까지'));
assert.ok(source.includes('P1 제품 설계'));

console.log('PASS product-centered PRD: 13 sections, 6 requirements, separate 11 TC + 5 UAT, synchronized site/plan/slides');
