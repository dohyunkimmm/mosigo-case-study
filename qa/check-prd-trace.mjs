import assert from 'node:assert/strict';
import { existsSync, readFileSync, readdirSync } from 'node:fs';
import path from 'node:path';

const read = path => readFileSync(path, 'utf8');
const prd = read('downloads/mosigo_prd_delivery.html');
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

// Internal QA evidence must not be tracked in the public new-business-planning repository.
for (const path of [
  'qa/internal/verification-appendix.html',
  'qa/evidence/2026-11-08-live-browser.json',
  'qa/evidence/2026-11-08-document-crosscheck.json',
]) assert.ok(!existsSync(path), 'private QA evidence must not be committed to public case study: ' + path);
assert.ok(site.includes('핵심 기능 6개와 사용자 흐름·화면·예외 정책을 정의했습니다.'));
assert.ok(!site.includes('mosigo_qa_appendix.html') && !site.includes('QA·인수인계'), 'Public portfolio must not expose QA appendix or QA handoff claims');
assert.ok(site.includes('추가 산출물 · 서비스기획·PRD') && site.includes('개념 시안 3종'), 'PRD must remain a clearly labeled supplementary deliverable');
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
assert.ok(site.includes('MOSIGO · 신사업 기획 요약') && site.includes('병원 동행 서비스 신사업 기획'),
  'portfolio intro must lead with new-business planning');
assert.ok(!prd.includes('완료된 결과물은 아닙니다.'),
  'remove repeated defensive phrasing from user-facing PRD');
assert.ok(!site.includes('QA 테스트 케이스 11개'),
  'QA proof should not dominate the core deliverable');
console.log('PASS cross-document KPI, user journey and editorial QA');

console.log('PASS supplemental PRD: 13 sections, 6 requirements; private QA remains unpublished');


// Keep the public repository index and archived audit references in sync.
const documentation = ['README.md',
  ...readdirSync('docs/history').filter(name => name.endsWith('.md'))
    .map(name => path.join('docs/history', name))];
const missingLinks = [];
for (const file of documentation) {
  const markdown = read(file);
  for (const match of markdown.matchAll(/!?\[[^\]\r\n]*\]\((<[^>]+>|[^)\r\n]+)\)/g)) {
    let href = match[1].trim();
    if (href.startsWith('<')) href = href.slice(1, href.indexOf('>'));
    else href = href.replace(/\s+(?:"[^"]*"|'[^']*')\s*$/, '').trim();
    if (!href || /^(?:[a-z][a-z0-9+.-]*:|\/\/|#)/i.test(href)) continue;
    href = href.split(/[?#]/)[0];
    if (!href) continue;
    let decoded;
    try { decoded = decodeURIComponent(href); }
    catch { missingLinks.push(file + ': invalid URI ' + href); continue; }
    const absolute = decoded.startsWith('/')
      ? path.resolve('.', '.' + decoded)
      : path.resolve(path.dirname(file), decoded);
    if (!existsSync(absolute)) missingLinks.push(file + ': ' + href);
  }
}
assert.deepEqual(missingLinks, [], 'broken repository-local Markdown links');
console.log('PASS README and archived-document relative links');

// Generated assets must use PRs; both mandatory QA jobs must run on every PR.
const generatorWorkflows = [
  'business-plan-pdf.yml', 'ppt-preview.yml', 'preview-pages.yml',
  'ir-deck.yml', 'build-social-preview.yml', 'tossface-icon.yml',
];
for (const workflow of generatorWorkflows) {
  const content = read('.github/workflows/' + workflow);
  assert.ok(content.includes('publish-generated-pr.sh'), workflow + ' must open an asset PR');
  assert.ok(content.includes('pull-requests: write'), workflow + ' requires PR write permission');
  assert.ok(!/git\s+push\s+origin\s+HEAD:main/.test(content),
    workflow + ' must not push generated files directly to main');
}
const prdWorkflow = read('.github/workflows/prd-evidence-qa.yml');
const prTriggers = prdWorkflow.split('  pull_request:')[1]?.split('  push:')[0] || '';
assert.ok(prTriggers.includes('branches: [main]') && !prTriggers.includes('paths:'),
  'required PRD QA must run on all PR changes');
const siteWorkflow = read('.github/workflows/site-qa.yml');
const siteTriggers = siteWorkflow.split('  pull_request:')[1]?.split('  push:')[0] || '';
assert.ok(siteTriggers.includes('branches: [main]') && !siteTriggers.includes('paths:'),
  'required Site QA must run on all PR changes');
console.log('PASS generator PR-only publishing and unfiltered required checks');
