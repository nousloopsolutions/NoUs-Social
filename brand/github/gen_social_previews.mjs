// Renders 1280x640 GitHub social preview PNGs from the brand exports.
// @NCL{v=1.0;agent=claude;mod=github-presentation;tier=L2}
// #S{purpose="Render branded GitHub social previews from brand/nous-loop exports"}
// #I{1="Product-level text only, no memory or learning internals";2="Output PNGs stay under 1 MB (GitHub limit)"}
// #F{1="Palette-quantized PNGs lost the neon-red slash and label tints; keep full colour"}
// Setup: Node 18+, then `npm install --no-save playwright && npx playwright install chromium`
//   (or point PLAYWRIGHT_PATH at an existing playwright install).
// Usage (from repo root): node brand/github/gen_social_previews.mjs
import { createRequire } from 'node:module';
const { chromium } = createRequire(import.meta.url)(process.env.PLAYWRIGHT_PATH || 'playwright');
import { readFileSync, writeFileSync } from 'node:fs';

const wall = readFileSync('brand/nous-loop/exports/nous-loop-wordmark-wall-still.svg');
const wallUri = 'data:image/svg+xml;base64,' + wall.toString('base64');

// name, one line (product level only), label
const repos = [
  ['NoUs Loop Solutions', 'Calm, private tools for a neurodivergent mind.', 'ON-DEVICE · PRIVATE BY DESIGN', 'profile'],
  ['NoUsClaWW', 'A local-first agent stack. Runs on your machine, works with any model.', 'OPEN SOURCE · MIT'],
  ['NoNu-Note', 'Private notes that help you remember what matters.', 'ANDROID · LOCAL FIRST'],
  ['Nousmoji', 'A calm face that shows how your day is going.', 'TYPESCRIPT · ON DEVICE'],
  ['NomojiClaWW', 'Your local helpers on one calm desktop screen.', 'DESKTOP · TAURI'],
  ['Nous-hub', 'Plans, status and shared tooling for NoUs Loop.', 'HOME BASE'],
  ['LASSY', 'A local AI stack that sets itself up and stays out of the way.', 'EARLY WORK'],
  ['NoUs-Social', 'Brand art and campaign content for NoUs Loop.', 'BRAND'],
];

const page = (name, line, label) => `<!doctype html><html><head><style>
  html,body{margin:0;width:1280px;height:640px;background:#0d0d0e;overflow:hidden}
  .bg{position:absolute;inset:0;background:#0d0d0e url('${wallUri}') center 30%/1340px auto no-repeat;filter:brightness(.92)}
  .shade{position:absolute;inset:0;background:linear-gradient(180deg,rgba(13,13,14,0) 45%,rgba(13,13,14,.92) 72%,#0d0d0e 100%)}
  .text{position:absolute;left:72px;right:72px;bottom:58px;font-family:Inter,sans-serif}
  .label{font-family:'JetBrains Mono','DejaVu Sans Mono',monospace;font-size:20px;letter-spacing:.22em;color:#94a3b8;margin-bottom:14px}
  .name{font-size:64px;font-weight:700;color:#f8fafc;letter-spacing:-.01em;line-height:1.05}
  .line{font-size:30px;color:#60f0f0;margin-top:14px}
  .tag{position:absolute;right:72px;top:40px;font-family:Inter,sans-serif;font-size:22px;color:#94a3b8}
  .tag b{color:#e45c5c;font-weight:700}
</style></head><body><div class="bg"></div><div class="shade"></div>
<div class="tag">safety through severance<b>/</b></div>
<div class="text"><div class="label">${label}</div><div class="name">${name}</div><div class="line">${line}</div></div></body></html>`;

const browser = await chromium.launch();
const p = await browser.newPage({ viewport: { width: 1280, height: 640 }, deviceScaleFactor: 1 });
for (const [name, line, label, file] of repos) {
  await p.setContent(page(name, line, label), { waitUntil: 'load' });
  await p.waitForTimeout(300);
  writeFileSync(`brand/github/social/${file || name.toLowerCase()}.png`, await p.screenshot({ type: 'png' }));
  console.log('wrote', name);
}
await browser.close();
