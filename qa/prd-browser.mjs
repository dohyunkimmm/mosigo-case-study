import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';

const base = process.env.SITE_QA_URL || 'http://127.0.0.1:8765/';
const prefix = process.env.SITE_QA_MODE === 'live' ? 'live-' : '';
const url = new URL('downloads/mosigo_prd_delivery.html', base).href;
const widths = [320, 390, 768, 1440];
const browser = await chromium.launch({ headless: true });
await mkdir('qa-artifacts', { recursive: true });
try {
  for (const width of widths) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const response = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    assert.equal(response?.status(), 200, 'PRD HTTP 200 at ' + width);
    assert.match(await page.title(), /요구사항|PRD/, 'PRD page title');
    assert.match(await page.locator('main h1').innerText(), /제품 요구사항 정의서/, 'PRD main heading');
    assert.equal(await page.locator('#prd-requirements tbody tr').count(), 6, 'six numbered requirements');
    assert.equal(await page.locator('#prd-qa tbody tr').count(), 11, '11 QA trace cases');
    assert.equal(await page.locator('#prd-uat tbody tr').count(), 5, 'five pending user UAT cases');
    assert.equal(await page.locator('main > section').count(), 6, 'six PRD sections');
    const content = await page.locator('main').innerText();
    for (const required of ['R-01', 'R-02', 'R-03', 'R-04', 'R-05', 'R-06',
       'TC-03-04', 'TC-04-02', 'UAT-05', '176건 통과', '실제 고객 UAT: 미실시']) {
      assert.ok(content.includes(required), 'PRD claim missing: ' + required);
    }
    const state = await page.evaluate(() => ({
      overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
      tables: [...document.querySelectorAll('.tablewrap')].map(el => ({
        viewport: el.clientWidth,
        content: el.scrollWidth,
        overflowX: getComputedStyle(el).overflowX
      }))
    }));
    assert.equal(state.overflow, false, 'PRD must not overflow page at ' + width + 'px');
    assert.ok(state.tables.length >= 5, 'PRD tables available at ' + width);
    assert.ok(state.tables.every(t => t.overflowX === 'auto'), 'wide tables remain horizontally scrollable');
    assert.deepEqual(errors, [], 'PRD has no page JS errors');
    if (width === 390 || width === 1440) {
      await page.screenshot({ path: 'qa-artifacts/' + prefix + 'prd-' + width + '.png', fullPage: true });
    }
    await page.close();
    console.log('PASS PRD responsive/trace QA', width + 'px', '6 requirements, 11 test cases, 5 pending UAT');
  }
} finally {
  await browser.close();
}
