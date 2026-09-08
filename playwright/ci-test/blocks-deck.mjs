#!/usr/bin/env node
// Capture each .block-demo-card on the /dev/blocks/ gallery as its own
// PNG, for assembly into the gallery slide deck (osgeo blocks --pdf).
//
// Environment: BASE_URL, CARDS_DIR, CHROMIUM_PATH (see capture-site.mjs).

import { chromium } from 'playwright';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const BASE_URL = process.env.BASE_URL ?? 'http://127.0.0.1:1316';
const CARDS_DIR = process.env.CARDS_DIR ?? 'artifacts/block-cards';

const browser = await chromium.launch(
  process.env.CHROMIUM_PATH
    ? {
        executablePath: process.env.CHROMIUM_PATH,
        chromiumSandbox: false,
        args: ['--disable-gpu', '--disable-dev-shm-usage', '--disable-crashpad'],
      }
    : {},
);

const page = await browser.newPage({
  viewport: { width: 1440, height: 900 },
  deviceScaleFactor: 1,
});

mkdirSync(CARDS_DIR, { recursive: true });
await page.goto(`${BASE_URL}/dev/blocks/`, { waitUntil: 'load', timeout: 30000 });
await page.evaluate(() => {
  const style = document.createElement('style');
  style.textContent =
    '*, *::before, *::after { animation: none !important; transition: none !important; }' +
    // Breathing room inside each captured card.
    '.block-demo-card { padding: 24px; background: #ffffff; }' +
    // The floating edit-on-github widget photobombs card screenshots.
    '.block-rich-edit-on-gh, #rich-edit-on-gh { display: none !important; }';
  document.head.appendChild(style);
});

const cards = page.locator('.block-demo-card');
const total = await cards.count();
console.log(`Capturing ${total} block cards from ${BASE_URL}/dev/blocks/`);

const manifest = [];
for (let i = 0; i < total; i += 1) {
  const card = cards.nth(i);
  const name = await card.getAttribute('id');
  await card.scrollIntoViewIfNeeded();
  await page.waitForTimeout(100);
  const file = join(CARDS_DIR, `card_${String(i).padStart(3, '0')}.png`);
  await card.screenshot({ path: file });
  manifest.push(`${file}\t${name ?? ''}`);
}

writeFileSync(join(CARDS_DIR, 'manifest.tsv'), manifest.join('\n') + '\n');
await browser.close();
console.log(`Captured ${total} cards into ${CARDS_DIR}`);
