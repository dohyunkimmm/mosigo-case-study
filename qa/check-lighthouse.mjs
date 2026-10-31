import fs from 'node:fs';
import assert from 'node:assert/strict';

const isLive = process.env.SITE_QA_MODE === 'live';
const prefix = isLive ? 'live-' : '';
// Live Lighthouse measures a synthetic CI browser, not actual user field performance.
const limits = { performance: isLive ? 75 : 90, accessibility: 95, 'best-practices': 95, seo: 95 };
for (const device of ['mobile', 'desktop']) {
  const report = JSON.parse(fs.readFileSync('qa-artifacts/' + prefix + 'lighthouse-' + device + '.json', 'utf8'));
  assert.ok(!report.runtimeError, device + ' Lighthouse runtime error');
  for (const [category, limit] of Object.entries(limits)) {
    const score = Math.round(report.categories[category].score * 100);
    console.log((isLive ? 'live ' : 'local ') + device + ' ' + category + ': ' + score + ' (min ' + limit + ')');
    assert.ok(score >= limit, device + ' ' + category + ' failed');
  }
}
console.log('PASS ' + (isLive ? 'live synthetic' : 'local') + ' Lighthouse QA');
