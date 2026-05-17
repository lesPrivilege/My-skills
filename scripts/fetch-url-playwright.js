#!/usr/bin/env node
const { chromium } = require('playwright');
const fs = require('fs');

const url = process.argv[2];
const outfile = process.argv[3];

if (!url || !outfile) {
  console.error('Usage: node fetch-url-playwright.js <url> <outfile>');
  process.exit(1);
}

(async () => {
  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'],
    });
    const context = await browser.newContext({
      userAgent:
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
      locale: 'en-US',
    });
    const page = await context.newPage();

    await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    // let JS settle
    await page.waitForTimeout(3000);

    const html = await page.content();
    fs.writeFileSync(outfile, html, 'utf-8');
  } catch (e) {
    fs.writeFileSync(outfile, `FETCH_ERROR: ${e.message}`, 'utf-8');
    process.exit(1);
  } finally {
    if (browser) await browser.close();
  }
})();
