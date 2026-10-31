import { chromium, webkit, devices } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';

const base = process.env.SITE_QA_URL || 'https://mosigo-case-study.vercel.app/';
const cases = [
  { name: 'webkit-iphone-se', engine: webkit, device: 'iPhone SE' },
  { name: 'webkit-iphone-13', engine: webkit, device: 'iPhone 13' },
  { name: 'chromium-iphone-13', engine: chromium, device: 'iPhone 13' },
  { name: 'chromium-pixel-7', engine: chromium, device: 'Pixel 7' }
];
const assetTests = [
  { path: '/downloads/mosigo_business_plan_20261031.pdf', label: 'business plan' },
  { path: '/downloads/mosigo_report_preview.pdf', label: 'presentation preview' }
];
const screenshots = 'qa-artifacts/mobile-browser';
await mkdir(screenshots, { recursive: true });
let runs = 0;
for (const { name, engine, device } of cases) {
  const browser = await engine.launch({ headless: true });
  try {
    const context = await browser.newContext({
      ...devices[device],
      locale: 'ko-KR',
      reducedMotion: 'reduce'
    });
    const page = await context.newPage();
    const pageErrors = [];
    page.on('pageerror', err => pageErrors.push(err.message));
    const response = await page.goto(base + '#attachments', { waitUntil: 'load', timeout: 45000 });
    assert.equal(response.status(), 200, name + ' site HTTP status');
    await page.locator('#doc-frame').scrollIntoViewIfNeeded();
    assert.equal(await page.locator('.doc-tab').count(), 2);
    assert.equal(await page.locator('#doc-frame').isVisible(), true);
    assert.equal(await page.locator('#doc-open').isVisible(), true);

    for (const { path, label } of assetTests) {
      const response = await context.request.get(new URL(path, base).href, { timeout: 25000 });
      assert.equal(response.status(), 200, name + ' ' + label + ' PDF status');
      const bytes = await response.body();
      assert.equal(bytes.subarray(0,5).toString('ascii'), '%PDF-');
      assert.ok(bytes.subarray(-4096).includes(Buffer.from('%%EOF')));
      assert.ok(bytes.length > 25000);
    }
    for (const [tab, path] of [
      ['presentation', '/downloads/mosigo_report_preview.pdf'],
      ['plan', '/downloads/mosigo_business_plan_20261031.pdf']
    ]) {
      await page.locator('[data-doc-preview="' + tab + '"]').click();
      assert.ok((await page.locator('#doc-frame').getAttribute('src')).startsWith(path + '#'), name + ' frame switches');
      assert.ok(new URL(await page.locator('#doc-open').getAttribute('href'), base).pathname === path, name + ' open link updates');
      assert.equal(await page.locator('[data-doc-preview="' + tab + '"]').getAttribute('aria-pressed'), 'true', name + ' accessible selected state');
    }
    await page.locator('#doc-frame').scrollIntoViewIfNeeded();
    const layout = await page.evaluate(() => {
      const tabs = [...document.querySelectorAll('.doc-tab')];
      const fallback = document.querySelector('#doc-open');
      const frame = document.querySelector('#doc-frame');
      const doc = document.querySelector('#attachments');
      const nav = document.querySelector('.mobile-toc');
      const r = element => {
        const b = element.getBoundingClientRect();
        return { w: b.width, h: b.height, top: b.top, bottom: b.bottom };
      };
      return {
        overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
        fontFamily: getComputedStyle(document.querySelector('.emoji-icon')).fontFamily,
        tabs: tabs.map(r), fallback: r(fallback), iframe: r(frame), viewer: r(doc),
        navPointerEvents: getComputedStyle(nav).pointerEvents,
        viewerVisible: r(doc).bottom > 0 && r(doc).top < innerHeight
      };
    });
    assert.equal(layout.overflow, false, name + ' horizontal scroll');
    assert.ok(layout.tabs.every(t => t.h >= 44), name + ' tab touch targets');
    assert.ok(layout.fallback.h >= 44, name + ' open-PDF touch target');
    assert.ok(layout.iframe.h >= 300 && layout.iframe.w > 240, name + ' document area');
    assert.ok(layout.fontFamily.includes('Tossface'), name + ' emoji family CSS');
    await page.screenshot({ path: screenshots + '/' + name + '.png', fullPage: false });
    const cssLink = page.locator('link[href*="tossface"]').first();
    assert.ok(await cssLink.count(), name + ' Tossface CSS link');
    const css = await context.request.get(await cssLink.getAttribute('href'), {timeout:25000});
    assert.equal(css.status(), 200, name + ' Tossface CSS available');
    assert.ok((await css.text()).includes('font-family: "Tossface"'), name + ' CSS declares Tossface');
    const fontResult = await page.evaluate(async () => {
      await document.fonts.ready;
      try {
        const faces = await document.fonts.load('24px "Tossface"', '📱');
        return { count: faces.length, loaded: faces.filter(f=>f.status==='loaded').length,
                 errors: [], check: document.fonts.check('24px "Tossface"', '📱') };
      } catch (e) { return { count: 0, loaded: 0, errors: [String(e)], check: false }; }
    });
    assert.ok(fontResult.loaded > 0 && fontResult.check, name + ' Tossface glyph loaded '+JSON.stringify(fontResult));
    assert.deepEqual(pageErrors, [], name + ' uncaught JS errors');
    console.log('PASS',name,JSON.stringify({layout,fontResult,documents:'PDF header and EOF verified, both tabs and fallback links verified'}));
    runs++;
    await context.close();
  } finally { await browser.close(); }
}
assert.equal(runs, cases.length);
console.log('PASS mobile WebKit/Chromium PDF-link and Tossface QA',runs,'device/browser combinations');
