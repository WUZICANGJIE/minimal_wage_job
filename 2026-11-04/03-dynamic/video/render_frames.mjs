// Screenshot every frame listed in build/frames.json from template.html.
// Usage: node render_frames.mjs   (run from this directory)
import { createRequire } from 'node:module';
import { readFileSync } from 'node:fs';
import { join, resolve } from 'node:path';
import { execSync } from 'node:child_process';

// Use a local playwright if installed, otherwise the global one
// (ESM imports and plain require ignore npm's global node_modules).
function loadPlaywright() {
  const req = createRequire(import.meta.url);
  try { return req('playwright'); } catch {}
  const globalRoot = execSync('npm root -g', { encoding: 'utf8' }).trim();
  return createRequire(join(globalRoot, 'noop.js'))('playwright');
}
const { chromium } = loadPlaywright();

const frames = JSON.parse(readFileSync('build/frames.json', 'utf8'));
const browser = await chromium.launch(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : {});
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
const errors = [];
page.on('pageerror', e => errors.push(String(e)));
await page.goto('file://' + resolve('template.html'));
await page.evaluate(() => document.fonts.ready);

const overflow = [];
for (const f of frames) {
  const r = await page.evaluate(a => show(...a), [f.scene, f.step, f.sub, f.progress]);
  if (r.overflow) overflow.push(f.out);
  await page.screenshot({ path: f.out });
}
await browser.close();
if (errors.length) { console.error(errors.join('\n')); process.exit(1); }
if (overflow.length) console.warn('content overflow:', [...new Set(overflow)].join(', '));
console.log(`rendered ${frames.length} frames`);
