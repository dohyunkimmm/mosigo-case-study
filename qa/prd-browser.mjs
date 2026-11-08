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
    assert.equal(await page.locator('main h1').innerText(),'MOSIGO PRD','concise PRD title');
    assert.equal(await page.locator('main > section').count(),13,'Kuse-style 13 PRD sections');
    assert.equal(await page.locator('.toc a').count(),13,'13 TOC links');
    assert.deepEqual(await page.locator('.toc a').allTextContents(),await page.locator('main > section h2').allTextContents(),
      'English TOC and section titles match');
    assert.equal(await page.locator('#prd-requirements tbody tr').count(),6,'6 product requirements');
    assert.equal(await page.locator('#user-stories tbody tr').count(),4,'4 user stories');
    assert.equal(await page.locator('#success-metrics tbody tr').count(),4,'4 KPI definitions');
    assert.equal(await page.locator('#ux-design .flow article').count(),5,'5 journey steps');
    const copy=await page.locator('main').innerText();
    for(const phrase of ['Personas','Metrics','Requirements','UX Design','R-01','R-02','R-03',
      'R-04','R-05','R-06','실제 운영','검증']){
      assert.ok(copy.includes(phrase),'PRD copy missing '+phrase);
    }
    assert.ok(!copy.includes('제품 QA 176/176'),'QA count should not dominate product PRD');
    assert.equal(await page.locator('#supporting a[href="mosigo_qa_appendix.html"]').count(),0,'public PRD must not link technical QA');
    const state=await page.evaluate(()=>({
      overflow:document.documentElement.scrollWidth>document.documentElement.clientWidth,
      tables:[...document.querySelectorAll('.tablewrap')].map(el=>({overflow:getComputedStyle(el).overflowX,requirements:!!el.closest('#prd-requirements'),focusable:el.tabIndex===0,label:el.getAttribute('aria-label'),role:el.getAttribute('role')})),
      requirements:[...document.querySelectorAll('#prd-requirements tbody tr')].map((row,index)=>{
        const id=row.querySelector('td:first-child strong');
        const r=id.getBoundingClientRect();
        const content=[...row.querySelectorAll('td')];
        return {id:id.innerText,visible:r.left>=0&&r.right<=innerWidth&&id.scrollWidth<=id.clientWidth+1,
          rowDisplay:getComputedStyle(row).display,clippedCells:content.filter(td=>td.scrollWidth>td.clientWidth+2).length,
          labels:content.filter(td=>td.hasAttribute('data-label')).length};
      })
    }));
    assert.equal(state.overflow,false,'PRD horizontal overflow '+width);
    assert.ok(state.tables.length>=5,'tables in PRD');
    assert.ok(state.tables.every(x=>x.requirements ? x.overflow===(width<=760?'visible':'auto') : x.overflow==='auto'),
      'requirements are mobile cards, other tables stay horizontally scrollable');
    assert.ok(state.requirements.length===6 && state.requirements.every((r,i)=>r.id==='R-0'+(i+1)&&r.visible&&r.clippedCells===0&&r.labels===5),
      'all six requirement IDs and cells stay visible without clipping');
    assert.ok(state.requirements.every(r=>r.rowDisplay===(width<=760?'block':'table-row')),
      'requirements must switch between cards and rows based on screen width');
    assert.ok(state.tables.every(x=>x.focusable && x.role==='region' && x.label),'tables are keyboard-accessible labelled scroll regions');
    assert.deepEqual(errors,[],'no PRD JS errors');
    if(width===390||width===1440){
      await page.screenshot({path:'qa-artifacts/'+prefix+'prd-'+width+'.png',fullPage:true});
    }
    await page.close();
    console.log('PASS product PRD browser QA',width+'px','13 sections, 6 requirements, user stories and metrics');
  }
  const page=await browser.newPage({viewport:{width:390,height:900}});
  const appendix=await page.goto(appendixUrl,{waitUntil:'domcontentloaded',timeout:45000});
  assert.equal(appendix?.status(),404,'technical QA appendix excluded from public site');

  await page.close();
  console.log('PASS technical QA appendix excluded from public portfolio');
}finally{
  await browser.close();
}