import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';

const base = process.env.SITE_QA_URL || 'http://127.0.0.1:8765/';
const reportPrefix = process.env.SITE_QA_MODE === 'live' ? 'live-' : '';
const widths = [320, 390, 600, 601, 768, 1024, 1440];
await mkdir('qa-artifacts', { recursive: true });
const browser = await chromium.launch({ headless: true });
const errors = [];
try {
  for (const width of widths) {
    const page = await browser.newPage({ viewport: { width, height: 844 } });
    page.on('pageerror', e => errors.push(width + 'px: ' + e.message));
    page.on('console', m => { if (m.type() === 'error') errors.push(width + 'px: ' + m.text()); });
    const response = await page.goto(base, { waitUntil: 'domcontentloaded', timeout: 45000 });
    assert.equal(response.status(), 200, width + 'px HTTP status');
    const check = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
      sections: document.querySelectorAll('main section[id]').length,
      details: document.querySelectorAll('details.chapter-detail').length,
      open: [...document.querySelectorAll('details.chapter-detail')].filter(el => el.open).length,
      mobileSummary: getComputedStyle(document.querySelector('.mobile-skim')).display !== 'none',
      tables: document.querySelectorAll('table').length,
      labels: document.querySelectorAll('tbody [data-label]').length,
      unlabeled: [...document.querySelectorAll('tbody tr')].flatMap(row => [...row.children]).filter(cell => !cell.hasAttribute('data-label')).length,
      missingAnchors: [...document.querySelectorAll('a[href^="#"]')].filter(a => !document.getElementById(a.getAttribute('href').slice(1))).length,
    }));
    assert.equal(check.overflow, false, width + 'px horizontal overflow');
    assert.equal(check.sections, 9, 'section count');
    assert.equal(check.details, 9, 'details count');
    assert.equal(check.tables, 14, 'table count');
    assert.ok(check.labels > 0 && check.unlabeled === 0, 'static table labels');
    assert.equal(check.open, 0, width + 'px concise chapter mode');
    assert.equal(check.mobileSummary, true, 'summary shown at every width');
    assert.equal(check.missingAnchors, 0, 'internal anchors');
    // Prevent repeated English report labels in the sidebar, sticky header and hero.
    assert.equal(await page.locator('aside .brand-sub, .top .top-l, .hero .tag.dark').count(), 0, width + 'px no duplicate report badges');
    assert.equal(await page.locator('.hero h1').count(), 1, width + 'px one main report heading');
    const heading = (await page.locator('.hero h1').textContent()).replace(/\s+/g, '');
    assert.equal(heading, 'MOSIGO전략기획보고서', width + 'px single Korean report title');
    const visibleLabels = await page.locator('aside, .top, .hero').allTextContents();
    assert.ok(!visibleLabels.join(' ').includes('STRATEGY CASE STUDY'), width + 'px no repeated case-study slogan');
    assert.ok(!visibleLabels.join(' ').includes('STRATEGY REPORT'), width + 'px no competing report slogan');

    assert.equal(await page.locator('.docs-note').count(), 0, width + 'px no redundant disclaimer beneath documents');
    assert.equal(await page.locator('.hero-actions a, .v3-phase-link, .top-r, .mobile-toc, #v3-page-share').count(), 0, width + 'px no duplicate section-jump shortcuts');
    assert.equal(await page.locator('.nav-link').count(), 9, width + 'px original primary contents navigation');
    // Regression: switching between plan, presentation and IR must never resize the preview box.
    if (width === 390 || width === 1024 || width === 1440) {
      const previewSelector = '#doc-page-open';
      const boxes = [];
      for (const tab of ['plan', 'presentation', 'ir']) {
        await page.locator('[data-doc-preview="' + tab + '"]').click();
        const img = page.locator('#doc-page-img');
        const prefix = tab === 'plan' ? 'plan' : tab === 'presentation' ? 'slides' : 'ir';
        await img.evaluate(element => element.decode());
        assert.ok((await img.getAttribute('src')).endsWith(prefix + '-01-sm.webp'), width + 'px ' + tab + ' preview source');
        const rendered = await img.evaluate(element => ({ready:element.complete,w:element.naturalWidth,h:element.naturalHeight}));
        assert.ok(rendered.ready && rendered.w >= 200 && rendered.h >= 110, width + 'px ' + tab + ' actual preview image loaded: ' + JSON.stringify(rendered));
        await page.waitForFunction(({ prefix }) => {
          const fullscreen = document.querySelector('#v3-fullscreen-img');
          const firstThumb = document.querySelector('#v3-doc-thumbs img');
          return fullscreen?.getAttribute('src')?.endsWith(prefix + '-01.webp') &&
                 firstThumb?.getAttribute('src')?.endsWith(prefix + '-01-sm.webp');
        }, { prefix });
        const rect = await page.locator(previewSelector).boundingBox();
        assert.ok(rect && rect.width > 200 && rect.height > 120, width + 'px ' + tab + ' preview renders');
        if (width === 1440) {
          const screenshot = await page.locator(previewSelector).screenshot({path:'qa-artifacts/'+reportPrefix+'preview-'+tab+'-1440.png'});
          assert.ok(screenshot.length > 10000, width + 'px ' + tab + ' preview has visible page content');
        }
        boxes.push({ tab, width: rect.width, height: rect.height });
      }
      for (const rect of boxes.slice(1)) {
        assert.ok(Math.abs(rect.width - boxes[0].width) <= 1, width + 'px preview width matches plan for ' + rect.tab);
        assert.ok(Math.abs(rect.height - boxes[0].height) <= 1, width + 'px preview height matches plan for ' + rect.tab);
      }
      if (width > 800) assert.ok(boxes[0].height >= 565, width + 'px consistent readable desktop preview height');
      await page.locator('[data-doc-preview="plan"]').click();
      console.log('PASS equal plan/presentation/IR viewer geometry', width, JSON.stringify(boxes));
    }

    const pageCopy = await page.locator('body').innerText();
    for (const removed of [
      '8주 파일럿 예산 400만 원(가정)',
      '동일한 공급·비용 가정을 비교한 추정치이며, 실제 운영 실적이 아닙니다.',
      '핵심 결정: 기존 사업자 제휴 조건을 먼저 검증한 뒤 확대 여부를 판단합니다.',
      '제품 설계 살펴보기', '사업기획서·IR Deck 보기', '최종 전략 판단 보기',
      '핵심 고객 이용 과업 고객 가설',
      'IR Deck PDF 저장'
    ]) {
      assert.ok(!pageCopy.includes(removed), width + 'px removed duplicate/caveat: ' + removed);
    }
    assert.equal(await page.locator('#doc-pdf-save').count(), 1, width + 'px one current-document PDF download');
    assert.equal(await page.locator('.doc-links a[download$=".pdf"]').count(), 1, width + 'px no duplicate IR PDF download');
    assert.equal(await page.locator('.doc-links a[download$=".pptx"]').count(), 2, width + 'px both editable slide decks retained');
    assert.equal(await page.locator('.doc-links a[download$=".xlsx"]').count(), 1, width + 'px calculation file retained');
    assert.match(await page.locator('#market .chapter-content').textContent(), /15,000명.*1\.5회.*40,000원.*9억 원/, width + 'px market scenario arithmetic retained');
    assert.match(await page.locator('#customer .chapter-content h3.subhead').textContent(), /고객 이용 과업/, width + 'px duplicate customer hypothesis wording removed');
    const decisionSummary = await page.locator('#decision .skim-verdict').textContent();
    assert.ok(decisionSummary.includes('월 서비스 완료 199건(산정 기준)'), width + 'px scenario label retained');
    assert.ok(decisionSummary.includes('손익분기점 1,082건'), width + 'px break-even count retained');
    assert.ok(decisionSummary.includes('확대 여부 판단'), width + 'px decision described by action criteria');

    const demoLink = page.locator('a[href="https://mosigo-nine.vercel.app/"]');
    assert.equal(await demoLink.count(), 1, width + 'px exactly one demo link');
    assert.equal(await page.locator('.hero a[href="https://mosigo-nine.vercel.app/"]').count(), 0, width + 'px hero stays focused on case study');
    assert.equal(await page.locator('#product a[href="https://mosigo-nine.vercel.app/"]').count(), 0, width + 'px product chapter focuses on strategy');
    assert.equal(await page.locator('footer.footer a[href="https://mosigo-nine.vercel.app/"]').count(), 1, width + 'px optional demo link belongs in footer');
    assert.equal(await page.locator('.prototype-reference').count(), 0, width + 'px redundant demo strip removed');
    assert.equal(await demoLink.getAttribute('target'), '_blank', 'demo opens separate tab');
    assert.ok((await demoLink.getAttribute('rel')).includes('noopener'), 'demo target is protected');
    assert.ok(await page.locator('link[href*="pretendardvariable"]').count() > 0, 'Pretendard stylesheet');
    assert.equal(await page.locator('img.emoji-icon[src="/assets/tossface-phone.png"]').count(), 1, 'official Tossface static icon');
    await page.locator('.emoji-icon').first().evaluate(el=>el.decode());
    assert.ok(await page.locator('.emoji-icon').first().evaluate(el=>el.complete && el.naturalWidth>60), 'Tossface icon loads on screen');
    if (width === 390 || width === 1440) {
      await page.screenshot({ path: 'qa-artifacts/' + reportPrefix + 'site-' + width + '.png', fullPage: false });
    }
    if (width === 390) {
      assert.equal(await page.locator('#mobile-doc-viewer').isVisible(), true, 'mobile static preview visible');
      assert.equal(await page.locator('#doc-frame').isVisible(), false, 'mobile blank PDF iframe hidden');
      await page.locator('#doc-next').click();
      assert.ok((await page.locator('#doc-page-img').getAttribute('src')).endsWith('/plan-02-sm.webp'), 'mobile next page');
      await page.locator('#doc-prev').click();
      assert.ok((await page.locator('#doc-page-img').getAttribute('src')).endsWith('/plan-01-sm.webp'), 'mobile previous page');
      await page.locator('[data-doc-preview="ir"]').click();
      assert.equal(await page.locator('#doc-pdf-save').getAttribute('href'), '/downloads/MOSIGO_IR_Investment_Review_12slides.pdf', 'selected IR PDF download points to IR deck');
      assert.equal(await page.locator('.doc-links a[download$=".pdf"]').count(), 1, 'IR view has one PDF save action');
      assert.ok((await page.locator('#doc-page-img').getAttribute('src')).endsWith('/ir-01-sm.webp'), 'mobile IR preview');
      await page.locator('#doc-next').click();
      assert.ok((await page.locator('#doc-page-img').getAttribute('src')).endsWith('/ir-02-sm.webp'), 'mobile IR next slide');
      assert.ok((await page.locator('#doc-page-count').innerText()).includes('12장'), 'IR slide count');
      await page.locator('[data-doc-preview="plan"]').click();
      await page.waitForFunction(() => {const img=document.getElementById('doc-page-img');return img.complete&&img.naturalWidth>0;});
      const details = page.locator('details.chapter-detail').first();
      await details.locator('summary').click();
      assert.equal(await details.evaluate(el => el.open), true, 'mobile detail opens');
      await details.locator('summary').click();
      assert.equal(await details.evaluate(el => el.open), false, 'mobile detail closes');
    }
    if (width === 1440) {
      await page.locator('#business .chapter-detail summary').click();
      await page.locator('#price').evaluate(el => { el.value = '41000'; el.dispatchEvent(new Event('input', { bubbles: true })); });
      assert.equal((await page.locator('#gmv').innerText()).trim(), '9.23억 원', 'rounding');
      await page.locator('#reset').click();
      assert.equal((await page.locator('#gmv').innerText()).trim(), '9.00억 원', 'reset');
      assert.equal(await page.locator('#doc-frame').isVisible(), false, 'browser-native PDF iframe hidden on desktop');
      assert.equal(await page.locator('#mobile-doc-viewer').isVisible(), true, 'same decoded page preview used on desktop');
      assert.ok((await page.locator('#doc-frame').getAttribute('src')).startsWith('/downloads/mosigo_business_plan_20261031.pdf#'), 'PDF initial tab');
      await page.locator('[data-doc-preview="presentation"]').click();
      assert.ok((await page.locator('#doc-frame').getAttribute('src')).startsWith('/downloads/mosigo_report_preview.pdf#'), 'PPT tab changes viewer');
      assert.equal(await page.locator('[data-doc-preview="presentation"]').getAttribute('aria-pressed'), 'true', 'PPT selected');
      await page.locator('[data-doc-preview="ir"]').click();
      assert.ok((await page.locator('#doc-frame').getAttribute('src')).startsWith('/downloads/MOSIGO_IR_Investment_Review_12slides.pdf#'), 'IR tab changes viewer');
      assert.equal(await page.locator('[data-doc-preview="ir"]').getAttribute('aria-pressed'), 'true', 'IR selected');
      assert.equal(await page.locator('#doc-pdf-save').getAttribute('href'), '/downloads/MOSIGO_IR_Investment_Review_12slides.pdf', 'selected IR document download');
      await page.locator('[data-doc-preview="plan"]').click();
      assert.ok((await page.locator('#doc-frame').getAttribute('src')).startsWith('/downloads/mosigo_business_plan_20261031.pdf#'), 'PDF tab restored');
      const assets = [
        { path: '/favicon.svg', kind: 'svg', minBytes: 200 },
        { path: '/downloads/mosigo_business_plan_20261031.pdf', kind: 'pdf', minBytes: 1000 },
        { path: '/downloads/mosigo_report_preview.pdf', kind: 'pdf', minBytes: 1000 },
        { path: '/downloads/MOSIGO_IR_Investment_Review_12slides.pdf', kind: 'pdf', minBytes: 1000 },
        { path: '/downloads/mosigo_model.xlsx', kind: 'zip', minBytes: 200 },
        { path: '/downloads/mosigo_report.pptx', kind: 'zip', minBytes: 200 },
        { path: '/downloads/MOSIGO_IR_Investment_Review_12slides.pptx', kind: 'zip', minBytes: 200 },
      ];
      for (const { path, kind, minBytes } of assets) {
        if (path.startsWith('/downloads/') && !path.endsWith('/mosigo_report_preview.pdf') && !path.endsWith('/MOSIGO_IR_Investment_Review_12slides.pdf')) {
          assert.ok(await page.locator('a[href$="' + path + '"]').count() >= 1, path + ' document link');
        }
        const response = await page.request.get(new URL(path, base).href);
        assert.equal(response.status(), 200, path + ' HTTP status');
        assert.ok(!/text\/html/i.test(response.headers()['content-type'] || ''), path + ' is not an HTML error page');
        const bytes = await response.body();
        assert.ok(bytes.length > minBytes, path + ' minimum file length');
        if (kind === 'pdf') {
          assert.equal(bytes.subarray(0, 5).toString('ascii'), '%PDF-', path + ' PDF header');
          assert.ok(bytes.subarray(-4096).includes(Buffer.from('%%EOF')), path + ' PDF trailer');
        } else if (kind === 'zip') {
          assert.equal(bytes.subarray(0, 4).toString('hex'), '504b0304', path + ' Office ZIP signature');
        } else if (kind === 'svg') {
          assert.ok(bytes.toString('utf8').includes('<svg'), path + ' SVG content');
        }
        console.log('PASS asset', path, bytes.length + ' bytes');
      }
      // Preserve the old public URLs that forward to sections of the consolidated report.
      for (const [legacyPath, anchor] of [
        ['/decision-memos.html', '#decision'],
        ['/forecast.html', '#business'],
        ['/materials.html', '#attachments'],
      ]) {
        const redirectResponse = await page.request.get(new URL(legacyPath, base).href);
        assert.equal(redirectResponse.status(), 200, legacyPath + ' HTTP status');
        const redirectHtml = await redirectResponse.text();
        assert.match(redirectHtml, /<meta\s+http-equiv="refresh"/i, legacyPath + ' meta refresh');
        assert.ok(redirectHtml.includes('content="0;url=/' + anchor + '"'), legacyPath + ' target');
        assert.ok(redirectHtml.includes('href="/' + anchor + '"'), legacyPath + ' fallback link');
      }
      for(const [kind,count] of [['plan',17],['slides',11]]){
        for(let i=1;i<=count;i++){
          const imagePath='/downloads/previews/'+kind+'-'+String(i).padStart(2,'0')+'.webp';
          const response=await page.request.get(new URL(imagePath,base).href);
          assert.equal(response.status(),200,imagePath+' HTTP');
          const bytes=await response.body();
          assert.ok(bytes.length>1000,imagePath+' size');
          assert.equal(bytes.subarray(0,4).toString('ascii'),'RIFF',imagePath+' header');
          assert.equal(bytes.subarray(8,12).toString('ascii'),'WEBP',imagePath+' format');
          const smallPath=imagePath.replace('.webp','-sm.webp');
          const small=await page.request.get(new URL(smallPath,base).href);
          assert.equal(small.status(),200,smallPath+' HTTP');
          const smallBytes=await small.body();
          assert.equal(smallBytes.subarray(8,12).toString('ascii'),'WEBP',smallPath+' format');
          assert.ok(smallBytes.length<bytes.length,smallPath+' optimized size');
        }
        console.log('PASS static document preview pages',kind,count);
      }
      await page.locator('a[href="#decision"]').first().click();
      assert.equal(new URL(page.url()).hash, '#decision', 'decision anchor');
    }
    console.log('PASS ' + width + 'px', JSON.stringify(check));
    await page.close();
  }
  const noJs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const page = await noJs.newPage();
  await page.goto(base, { waitUntil: 'domcontentloaded', timeout: 45000 });
  assert.equal(await page.locator('details.chapter-detail[open]').count(), 9, 'no-JS contents available');
  const label = await page.locator('tbody td[data-label]').first().evaluate(el => getComputedStyle(el, '::before').content);
  assert.ok(label && label !== 'none' && label !== '""', 'no-JS mobile table label visible');
  console.log('PASS disabled-JS mobile table label', label);
  await noJs.close();
  assert.deepEqual(errors, [], 'browser console and JS errors');
  console.log('PASS browser QA');
} finally {
  await browser.close();
}
