// jobs.json の各場面を開き、段階と字幕を切り替えて 1920x1080 の PNG を撮る。
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");
const jobs = JSON.parse(readFileSync(process.argv[2], "utf8"));
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
for (const job of jobs) {
  await page.goto(pathToFileURL(job.html).href);
  await page.waitForFunction(() => window.__ready === true);
  await page.waitForLoadState("networkidle");
  for (const shot of job.shots) {
    await page.evaluate(({ step, sub }) => {
      document.body.dataset.step = String(step);
      document.getElementById("sub").textContent = sub;
    }, shot);
    await page.screenshot({ path: shot.out });
  }
}
await browser.close();
