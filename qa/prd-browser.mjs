import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';

const base = process.env.SITE_QA_URL || 'http://127.0.0.1:8765/';
const prefix = process.env.SITE_QA_MODE === 'live' ? 'live-' : '';
const prdUrl = new URL('downloads/mosigo_prd_delivery.html', base).href;
const appendixUrl = new URL('downloads/mosigo_qa_appendix.html', base).href;
const widths = [320,390,768,1440];
await mkdir('qa-artifacts', { recursive:true });
const browser=await chromium.launch({ headless:true });
try {
  for(const width of widths){
    const page=await browser.newPage({ viewport:{width,height:900} });
    const errors=[];
    page.on('pageerror', e=>errors.push(e.message));
    const response=await page.goto(prdUrl,{waitUntil:'domcontentloaded',timeout:45000});
    assert.equal(response?.status(),200,'PRD HTTP 200 '+width);
    assert.match(await page.title(),/요구사항.*PRD|PRD.*요구사항/,'PRD title');
    assert.match(await page.locator('main h1').innerText(),/제품 요구사항 정의서/);
    assert.equal(await page.locator('main > section').count(),13,'Kuse-style 13 PRD sections');
    assert.equal(await page.locator('.toc a').count(),13,'13 TOC links');
    assert.equal(await page.locator('#prd-requirements tbody tr').count(),6,'6 product requirements');
    assert.equal(await page.locator('#user-stories tbody tr').count(),4,'4 user stories');
    assert.equal(await page.locator('#success-metrics tbody tr').count(),4,'4 KPI definitions');
    assert.equal(await page.locator('#ux-design .flow article').count(),5,'5 journey steps');
    const copy=await page.locator('main').innerText();
    for(const phrase of ['사용자 페르소나','성공 지표','UX·화면 설계','R-01','R-02','R-03',
      'R-04','R-05','R-06','실제 운영','검증','기능 검증 기록(별도 부록)']){
      assert.ok(copy.includes(phrase),'PRD copy missing '+phrase);
    }
    assert.ok(!copy.includes('제품 QA 176/176'),'QA count should not dominate product PRD');
    assert.equal(await page.locator('#supporting a[href="mosigo_qa_appendix.html"]').count(),1);
    const state=await page.evaluate(()=>({
      overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth,
      tables:[...document.querySelectorAll('.tablewrap')].map(el=>getComputedStyle(el).overflowX)
    }));
    assert.equal(state.overflow,false,'PRD horizontal overflow '+width);
    assert.ok(state.tables.length>=5,'tables in PRD');
    assert.ok(state.tables.every(x=>x==='auto'),'tables horizontally scrollable');
    assert.deepEqual(errors,[],'no PRD JS errors');
    if(width===390||width===1440){
      await page.screenshot({path:'qa-artifacts/'+prefix+'prd-'+width+'.png',fullPage:true});
    }
    await page.close();
    console.log('PASS product PRD browser QA',width+'px','13 sections, 6 requirements, user stories and metrics');
  }
  const page=await browser.newPage({viewport:{width:390,height:900}});
  const appendix=await page.goto(appendixUrl,{waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(appendix?.status(),200,'optional QA appendix accessible');
  assert.equal(await page.locator('#prd-qa tbody tr').count(),11,'11 QA appendix cases');
  assert.equal(await page.locator('#prd-uat tbody tr').count(),5,'5 unperformed UAT appendix scenarios');
  assert.match(await page.locator('h1').innerText(),/기능 검증/);
  await page.close();
  console.log('PASS optional QA appendix separated from product PRD');
}finally{
  await browser.close();
}