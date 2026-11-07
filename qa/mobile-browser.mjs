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
  { path: '/downloads/mosigo_report_preview.pdf', label: 'presentation preview' },
  { path: '/downloads/MOSIGO_IR_Investment_Review_12slides.pdf', label: 'IR 12 slide deck' }
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
    await page.locator('#mobile-doc-viewer').scrollIntoViewIfNeeded();
    assert.equal(await page.locator('.doc-tab').count(), 3);
    assert.equal(await page.locator('#doc-frame').isVisible(), false, name + ' blank PDF iframe hidden');
    assert.equal(await page.locator('#mobile-doc-viewer').isVisible(), true, name + ' preview image viewer visible');
    const bodyFont = await page.locator('body').evaluate(el => getComputedStyle(el).fontFamily);
    assert.match(bodyFont, /Pretendard/, name + ' site typography must declare Pretendard');

    await page.waitForFunction(() => {const im=document.querySelector('#doc-page-img');return im.complete&&im.naturalWidth>0;});
    assert.equal(await page.locator('#doc-pdf-save').isVisible(), true);

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
      ['ir', '/downloads/MOSIGO_IR_Investment_Review_12slides.pdf'],
      ['plan', '/downloads/mosigo_business_plan_20261031.pdf']
    ]) {
      await page.locator('[data-doc-preview="' + tab + '"]').click();
      assert.ok((await page.locator('#doc-frame').getAttribute('src')).startsWith(path + '#'), name + ' frame switches');
      assert.ok(new URL(await page.locator('#doc-pdf-save').getAttribute('href'), base).pathname === path, name + ' open link updates');
      assert.equal(await page.locator('[data-doc-preview="' + tab + '"]').getAttribute('aria-pressed'), 'true', name + ' accessible selected state');
      const prefix=tab==='plan'?'plan':tab==='ir'?'ir':'slides';
      assert.ok((await page.locator('#doc-page-img').getAttribute('src')).endsWith('/'+prefix+'-01-sm.webp'), name + ' initial preview image');
      await page.waitForFunction(() => {const im=document.querySelector('#doc-page-img');return im.complete&&im.naturalWidth>0;});
      await page.locator('#doc-next').click();
      assert.ok((await page.locator('#doc-page-img').getAttribute('src')).endsWith('/'+prefix+'-02-sm.webp'), name + ' next page');
      await page.locator('#doc-prev').click();
      assert.ok((await page.locator('#doc-page-img').getAttribute('src')).endsWith('/'+prefix+'-01-sm.webp'), name + ' previous page');
      await page.waitForFunction(() => {const im=document.querySelector('#doc-page-img');return im.complete&&im.naturalWidth>0;});
      // Walk every published mobile page rather than checking only the first two.
      const total = tab === 'plan' ? 19 : tab === 'ir' ? 12 : 11;
      for (let number = 2; number <= total; number++) {
        await page.locator('#doc-next').click();
        const padded = String(number).padStart(2, '0');
        const preview = '/downloads/previews/' + prefix + '-' + padded + '-sm.webp';
        assert.ok((await page.locator('#doc-page-img').getAttribute('src')).endsWith(preview), name + ' page ' + number + ' preview URL');
        assert.ok((await page.locator('#doc-page-open').getAttribute('href')).endsWith('/' + prefix + '-' + padded + '.webp'), name + ' page ' + number + ' full-resolution link');
        assert.equal(await page.locator('#doc-page-count').getAttribute('aria-label'),
          '현재 ' + number + (tab === 'plan' ? '쪽' : '장') + ', 전체 ' + total + (tab === 'plan' ? '쪽' : '장'),
          name + ' page ' + number + ' accessible page counter');
        await page.waitForFunction(() => {
          const image = document.querySelector('#doc-page-img');
          return image.complete && image.naturalWidth >= 200 && image.naturalHeight >= 110;
        }, { timeout: 20000 });
      }
      assert.equal(await page.locator('#doc-next').isDisabled(), true, name + ' last-page boundary');
      assert.equal(await page.locator('#doc-prev').isEnabled(), true, name + ' previous-page control');
      await page.screenshot({ path: screenshots + '/' + name + '-' + tab + '-last.png', fullPage: false });
      await page.locator('[data-doc-preview="' + tab + '"]').click();
      assert.equal(await page.locator('#doc-next').isDisabled(), true, name + ' remembers the last page when reselected');
      await page.locator('#doc-prev').click();
      assert.ok((await page.locator('#doc-page-img').getAttribute('src')).endsWith('/' + prefix + '-' + String(total-1).padStart(2, '0') + '-sm.webp'), name + ' previous-page navigation');
      assert.equal(await page.locator('#doc-next').isEnabled(), true, name + ' can return to last page');
      await page.locator('#doc-next').click();
      assert.equal(await page.locator('#doc-next').isDisabled(), true, name + ' last-page boundary after returning');
      await page.screenshot({ path: screenshots + '/' + name + '-' + tab + '.png', fullPage: false });
    }
    await page.locator('#mobile-doc-viewer').scrollIntoViewIfNeeded();
    const layout = await page.evaluate(() => {
      const tabs = [...document.querySelectorAll('.doc-tab')];
      const fallback = document.querySelector('#doc-pdf-save');
      const image = document.querySelector('#doc-page-img');
      const doc = document.querySelector('#attachments');
      const r = element => {
        const b = element.getBoundingClientRect();
        return { w: b.width, h: b.height, top: b.top, bottom: b.bottom };
      };
      return {
        overflow: document.documentElement.scrollWidth > document.documentElement.clientWidth,
        iconWidth: document.querySelector('.emoji-icon').naturalWidth,
        tabs: tabs.map(r), fallback: r(fallback), image: r(image), viewer: r(doc),
        viewerVisible: r(doc).bottom > 0 && r(doc).top < innerHeight
      };
    });
    assert.equal(layout.overflow, false, name + ' horizontal scroll');
    assert.ok(layout.tabs.every(t => t.h >= 44), name + ' tab touch targets');
    assert.ok(layout.fallback.h >= 44, name + ' open-PDF touch target');
    assert.ok(layout.image.h >= 140 && layout.image.w > 240, name + ' visible mobile document image');
    assert.ok(layout.iconWidth>=100,name+' Tossface visual asset');
    assert.equal(await page.locator('.mobile-toc').count(),0,name + ' duplicate floating toc removed');
    assert.equal(await page.locator('.nav-link').count(),9,name + ' original chapter navigation retained');
    const imageInfo=await page.locator('#doc-page-img').evaluate(el=>({ready:el.complete,w:el.naturalWidth,h:el.naturalHeight}));
    assert.ok(imageInfo.ready&&imageInfo.w>=200&&imageInfo.h>=110,name+' decoded responsive WebP preview '+JSON.stringify(imageInfo));
    console.log('PASS visible mobile PDF preview',name,imageInfo);
    const icon=page.locator('img.emoji-icon');
    assert.equal(await icon.count(),1,name+' renders original Tossface icon');
    const iconData=await icon.evaluate(el=>({loaded:el.complete,w:el.naturalWidth,h:el.naturalHeight}));
    assert.ok(iconData.loaded&&iconData.w>=100&&iconData.h>=100,name+' Tossface icon decoded '+JSON.stringify(iconData));
    const png=await context.request.get(new URL('/assets/tossface-phone.png',base).href);
    assert.equal(png.status(),200,name+' Tossface PNG status');
    const bytes=await png.body();
    assert.equal(bytes.subarray(0,8).toString('hex'),'89504e470d0a1a0a',name+' PNG signature');
    assert.ok(bytes.length<20000,name+' optimized icon size');
    const fontResult={type:'official Tossface glyph, static PNG',bytes:bytes.length};
    // Test the full mobile preview manifest (both the 800px and 1400px variants).
    // Execute once for the last device, because assets are common to every engine.
    if (name === cases[cases.length - 1].name) {
      for (const [prefix, count] of [['plan', 19], ['slides', 11], ['ir', 12]]) {
        for (let number = 1; number <= count; number++) {
          const numberText = String(number).padStart(2, '0');
          for (const suffix of ['-sm.webp', '.webp']) {
            const path = '/downloads/previews/' + prefix + '-' + numberText + suffix;
            const response = await context.request.get(new URL(path, base).href, { timeout: 20000 });
            assert.equal(response.status(), 200, path + ' HTTP status');
            const buffer = await response.body();
            assert.ok(buffer.length > 1000, path + ' nonempty');
            assert.equal(buffer.subarray(0, 4).toString('ascii'), 'RIFF', path + ' RIFF header');
            assert.equal(buffer.subarray(8, 12).toString('ascii'), 'WEBP', path + ' WebP format');
          }
        }
      }
      console.log('PASS 84 mobile preview WebP files: 19 plan pages, 11 presentation slides and 12 IR slides at both sizes');
    }
    assert.deepEqual(pageErrors, [], name + ' uncaught JS errors');
    console.log('PASS',name,JSON.stringify({layout,fontResult,documents:'PDF header and EOF verified, all three tabs and fallback links verified'}));
    runs++;
    await context.close();
  } finally { await browser.close(); }
}
assert.equal(runs, cases.length);
console.log('PASS mobile WebKit/Chromium PDF-link and Tossface QA',runs,'device/browser combinations');
