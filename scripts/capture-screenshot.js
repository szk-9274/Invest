const { chromium } = require('playwright');
const fs = require('fs');

async function capture(url, outDir) {
  await fs.promises.mkdir(outDir, { recursive: true });
  let browser;
  try {
    browser = await chromium.launch();
  } catch (e) {
    console.error('Failed to launch Playwright browser. This is often caused by missing system libraries (e.g., libnspr4, libnss3).');
    console.error('Error:', e.message || e);
    throw e;
  }

  const contextDesktop = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const page = await contextDesktop.newPage();
  await page.goto(url, { waitUntil: 'networkidle' });
  await page.screenshot({ path: `${outDir}/desktop.png`, fullPage: true });

  const contextMobile = await browser.newContext({ viewport: { width: 375, height: 812 }, isMobile: true });
  const page2 = await contextMobile.newPage();
  await page2.goto(url, { waitUntil: 'networkidle' });
  await page2.screenshot({ path: `${outDir}/mobile.png`, fullPage: true });

  await browser.close();
}

const argv = require('minimist')(process.argv.slice(2));
const url = argv.url || argv.u || 'http://localhost:5173/dashboard';
const out = argv.out || argv.o || 'tests/screenshots';

// Ensure output directory exists and is writable before starting browsers
(async () => {
  try {
    await fs.promises.mkdir(out, { recursive: true });
  } catch (e) {
    console.error('Failed to create screenshot output directory', e);
    process.exit(1);
  }

  // Basic readiness check for backend
  try {
    const res = await fetch(url.replace('/dashboard','/api/backtest/latest'));
    if (!res.ok) {
      console.warn('Backend readiness check failed, continuing anyway');
    }
  } catch (e) {
    console.warn('Backend readiness check error, continuing anyway:', e.message || e);
  }

  capture(url, out).then(() => console.log('Screenshots saved to', out)).catch((e) => { console.error(e); process.exit(1); });
})();
