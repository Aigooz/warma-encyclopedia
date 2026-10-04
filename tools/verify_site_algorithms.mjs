import { chromium } from "file:///C:/Users/Aigooz/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const messages = [];
page.on("console", msg => { if (msg.type() === "error") messages.push(msg.text()); });
page.on("pageerror", err => messages.push(err.message));
await page.goto("http://127.0.0.1:8765/index.html?v=33", { waitUntil: "networkidle" });
await page.waitForTimeout(3000);
const counts = {};
for (const id of ["chartGraph", "chartAlgorithmClusters", "chartTagAffinity", "chartKeywordEvolution", "similarList"]) {
  counts[id] = await page.locator(`#${id}`).count();
}
const similarCount = await page.locator("#similarList .similarity-item").count();
const sourceCount = await page.locator("#similarSource option").count();
await page.locator("#explore").scrollIntoViewIfNeeded();
await page.waitForTimeout(1800);
await page.screenshot({ path: "F:/warma百科/warma-encyclopedia/tools/artifact_tmp/algorithms_top.png", fullPage: false });
await page.locator("#chartTagAffinity").scrollIntoViewIfNeeded();
await page.waitForTimeout(1800);
await page.screenshot({ path: "F:/warma百科/warma-encyclopedia/tools/artifact_tmp/algorithms_bottom.png", fullPage: false });
console.log(JSON.stringify({ counts, similarCount, sourceCount, messages }, null, 2));
await browser.close();

