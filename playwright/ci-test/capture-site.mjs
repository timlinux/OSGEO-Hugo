#!/usr/bin/env node
// Capture a scroll-through screenshot sequence of every page in the
// site's sitemap, with the URL path burned into each frame so issues
// can be pointed at by path. Driven by site-video.sh (osgeo video),
// which stitches the frames into a validation video with ffmpeg.
//
// Environment:
//   BASE_URL         server to crawl        (default http://127.0.0.1:1316)
//   FRAMES_DIR       output directory       (default artifacts/frames)
//   VIDEO_MAX_STEPS  max scroll frames/page, 0 = full page (default 1:
//                    top of page only; use --full in site-video.sh for
//                    the whole page)
//   VIDEO_LIMIT      only first N pages, 0 = all (default 0)
//   VIDEO_THEME      brand theme to capture (default "current"; the
//                    site's theme switcher persists via localStorage)

import { chromium } from 'playwright';
import { mkdirSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const BASE_URL = process.env.BASE_URL ?? 'http://127.0.0.1:1316';
const FRAMES_DIR = process.env.FRAMES_DIR ?? 'artifacts/frames';
const MAX_STEPS = Math.max(0, Number(process.env.VIDEO_MAX_STEPS ?? 1));
const LIMIT = Number(process.env.VIDEO_LIMIT ?? 0);
const THEME = process.env.VIDEO_THEME ?? 'current';
const WIDTH = 1440;
const HEIGHT = 900;

async function pagePaths() {
  const res = await fetch(`${BASE_URL}/sitemap.xml`);
  if (!res.ok) {
    throw new Error(`Could not fetch ${BASE_URL}/sitemap.xml (HTTP ${res.status})`);
  }
  const xml = await res.text();
  const locs = [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((m) => m[1]);
  const paths = [...new Set(locs.map((u) => new URL(u).pathname))].sort();
  return LIMIT > 0 ? paths.slice(0, LIMIT) : paths;
}

async function addBanner(page, text) {
  await page.evaluate((label) => {
    const el = document.createElement('div');
    el.id = '__osgeo-video-banner';
    el.textContent = label;
    Object.assign(el.style, {
      position: 'fixed',
      top: '0',
      left: '0',
      right: '0',
      zIndex: '2147483647',
      background: 'rgba(0, 0, 0, 0.85)',
      color: '#ffffff',
      font: 'bold 22px/1.6 monospace',
      padding: '8px 16px',
      pointerEvents: 'none',
    });
    document.body.appendChild(el);
    // Freeze animations so every frame is stable.
    const style = document.createElement('style');
    style.textContent = '*, *::before, *::after { animation: none !important; transition: none !important; }';
    document.head.appendChild(style);
  }, text);
}

mkdirSync(FRAMES_DIR, { recursive: true });

// CHROMIUM_PATH overrides the browser binary — useful when the pinned
// playwright browser bundle is unavailable (a system chromium works).
// The extra flags keep chromium alive in containers/sandboxes.
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
  viewport: { width: WIDTH, height: HEIGHT },
  deviceScaleFactor: 1,
});

// Pin the brand theme before any page script runs; the site's theme
// switcher reads localStorage and applies data-theme on load.
await page.addInitScript((theme) => {
  try {
    localStorage.setItem('osgeo-theme', theme);
  } catch {
    /* storage unavailable — page falls back to the default theme */
  }
}, THEME);

const paths = await pagePaths();
console.log(
  `Capturing ${paths.length} pages from ${BASE_URL} in "${THEME}" theme ` +
  (MAX_STEPS > 0 ? `(max ${MAX_STEPS} frames/page)` : '(full pages)'),
);

let frame = 0;
const manifest = [];

for (const [index, pagePath] of paths.entries()) {
  const label = `[${index + 1}/${paths.length}] ${pagePath}`;
  try {
    await page.goto(`${BASE_URL}${pagePath}`, { waitUntil: 'load', timeout: 20000 });
  } catch {
    console.warn(`  ⚠ slow load, capturing anyway: ${pagePath}`);
  }
  // Alias pages navigate again via meta-refresh; let that settle, and
  // retry once if the first injection races a navigation.
  await page.waitForTimeout(300);
  try {
    await addBanner(page, label);
  } catch {
    try {
      await page.waitForLoadState('load', { timeout: 10000 });
      await page.waitForTimeout(300);
      await addBanner(page, label);
    } catch (err) {
      console.warn(`  ⚠ skipping ${pagePath}: ${String(err).split('\n')[0]}`);
      continue;
    }
  }

  const scrollHeight = await page.evaluate(() => document.documentElement.scrollHeight);
  const needed = Math.max(1, Math.ceil(scrollHeight / HEIGHT));
  const steps = MAX_STEPS > 0 ? Math.min(MAX_STEPS, needed) : needed;

  for (let step = 0; step < steps; step += 1) {
    // Single-frame pages capture the top; multi-frame pages end on the
    // page bottom so the full height is covered.
    const y = step === 0 ? 0 : step === steps - 1 ? scrollHeight : step * HEIGHT;
    await page.evaluate((top) => window.scrollTo(0, top), y);
    await page.waitForTimeout(150);
    const file = join(FRAMES_DIR, `frame_${String(frame).padStart(6, '0')}.png`);
    await page.screenshot({ path: file });
    manifest.push(`${file}\t${pagePath}`);
    frame += 1;
  }
  console.log(`  ✓ ${label} (${steps} frame${steps === 1 ? '' : 's'})`);
}

writeFileSync(join(FRAMES_DIR, 'manifest.tsv'), manifest.join('\n') + '\n');
await browser.close();
console.log(`Captured ${frame} frames into ${FRAMES_DIR}`);
