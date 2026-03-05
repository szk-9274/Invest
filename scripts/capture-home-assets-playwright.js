const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

(async () => {
  const outDir = path.resolve(__dirname, '..', 'docs', 'PLAN', 'assets');
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext();
  const page = await context.newPage();

  const resourceMap = new Map();

  page.on('request', request => {
    resourceMap.set(request.url(), {
      url: request.url(),
      method: request.method(),
      type: request.resourceType(),
      from: 'request'
    });
  });

  page.on('response', async response => {
    try {
      const url = response.url();
      const entry = resourceMap.get(url) || { url };
      entry.status = response.status();
      entry.ok = response.ok();
      entry.headers = response.headers();
      entry.from = 'response';
      resourceMap.set(url, entry);
    } catch (e) {
      // ignore
    }
  });

  try {
    await page.goto('https://metaplanet.jp/en', { timeout: 60000 });
    await page.waitForLoadState('networkidle', { timeout: 60000 });
    await page.waitForTimeout(2000);

    const screenshotPath = path.join(outDir, 'home_en_full.png');
    await page.screenshot({ path: screenshotPath, fullPage: true });

    const perf = await page.evaluate(() => performance.getEntriesByType('resource').map(r => ({ name: r.name, initiatorType: r.initiatorType, transferSize: r.transferSize || 0 })));
    fs.writeFileSync(path.join(outDir, 'home_en_resources_perf.json'), JSON.stringify(perf, null, 2));

    const resources = Array.from(resourceMap.values());
    fs.writeFileSync(path.join(outDir, 'home_en_resources.json'), JSON.stringify(resources, null, 2));

    console.log('Captured assets to', screenshotPath);
  } catch (err) {
    console.error('Capture failed:', err);
    process.exitCode = 2;
  } finally {
    await browser.close();
  }
})();
