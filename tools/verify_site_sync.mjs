import { chromium } from "file:///C:/Users/Aigooz/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright/index.mjs";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const messages = [];
page.on("console", msg => { if (msg.type() === "error") messages.push(msg.text()); });
page.on("pageerror", err => messages.push(err.message));
await page.goto("http://127.0.0.1:8765/index.html?v=29", { waitUntil: "networkidle" });
await page.waitForTimeout(2500);
await page.screenshot({ path: "F:/warma百科/warma-encyclopedia/tools/artifact_tmp/site_sync_top.png", fullPage: false });
await page.locator("#sync").scrollIntoViewIfNeeded();
await page.waitForTimeout(1500);
await page.screenshot({ path: "F:/warma百科/warma-encyclopedia/tools/artifact_tmp/site_sync_section.png", fullPage: false });
const text = await page.locator("#sync").innerText();
console.log("SYNC_TEXT\n" + text.slice(0, 1000));
console.log("ERRORS", JSON.stringify(messages));
await browser.close();
