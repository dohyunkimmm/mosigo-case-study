import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';

const base = process.env.SITE_QA_URL || 'http://127.0.0.1:8765/';
const widths = [320, 390, 600, 601, 768, 1024, 1440];
await mkdir('qa-artifacts', { recursive: true });
const browser = await chromium.launch({ headless: true });
const errors = [];
try {
  for (const width of widths) {
    const page = await browser.newPage({ viewport: { width, height: 844 } });
    page.on('pageerror', e => errors.push(width + 'px: ' + e.message));
    page.on('console', m => { if (m.type() === 'error') errors.push(width + 'px: ' + m.text()); });
    const response = await page.goto(base, { waitUntil: 'load', timeout: 30000 });
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
    assert.equal(check.tables, 19, 'table count');
    assert.ok(check.labels > 0 && check.unlabeled === 0, 'static table labels');
    assert.equal(check.open, width <= 600 ? 0 : 9, width + 'px details mode');
    assert.equal(check.mobileSummary, width <= 600, 'mobile summary mode');
    assert.equal(check.missingAnchors, 0, 'internal anchors');
    if (width === 390 || width === 1440) {
      await page.screenshot({ path: 'qa-artifacts/site-' + width + '.png', fullPage: false });
    }
    if (width === 390) {
      const details = page.locator('details.chapter-detail').first();
      await details.locator('summary').click();
      assert.equal(await details.evaluate(el => el.open), true, 'mobile detail opens');
      await details.locator('summary').click();
      assert.equal(await details.evaluate(el => el.open), false, 'mobile detail closes');
    }
    if (width === 1440) {
      await page.locator('#price').evaluate(el => { el.value = '41000'; el.dispatchEvent(new Event('input', { bubbles: true })); });
      assert.equal((await page.locator('#gmv').innerText()).trim(), '9.23억 원', 'rounding');
      await page.locator('#reset').click();
      assert.equal((await page.locator('#gmv').innerText()).trim(), '9.00억 원', 'reset');
      for (const path of ['/favicon.svg', '/downloads/mosigo_model.xlsx', '/downloads/mosigo_report.pptx']) {
        const file = await page.request.get(new URL(path, base).href);
        assert.equal(file.status(), 200, path + ' HTTP status');
        assert.ok((await file.body()).length > 200, path + ' file length');
      }
      await page.locator('a[href="#decision"]').first().click();
      assert.equal(new URL(page.url()).hash, '#decision', 'decision anchor');
    }
    console.log('PASS ' + width + 'px', JSON.stringify(check));
    await page.close();
  }
  const noJs = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  const page = await noJs.newPage();
  await page.goto(base, { waitUntil: 'load', timeout: 30000 });
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
