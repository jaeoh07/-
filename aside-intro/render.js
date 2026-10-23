// 사용법: node render.js  →  frames를 ffmpeg로 넘겨 intro_video.mp4 생성 (무음)
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');

const FPS = 30;
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
  await page.goto('file://' + path.join(__dirname, 'intro.html') + '?render');
  await page.evaluate(() => Promise.all([...document.fonts].map((f) => f.load().catch(() => {}))));
  await page.evaluate(() => document.fonts.ready);
  await page.waitForTimeout(300);
  const dur = await page.evaluate(() => window.DURATION);
  const frames = Math.round(dur * FPS);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'medium', path.join(__dirname, 'intro_video.mp4')],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let f = 0; f < frames; f++) {
    await page.evaluate((t) => window.render(t), f / FPS);
    const buf = await page.screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
  }
  ff.stdin.end();
  await new Promise((r) => ff.on('close', r));
  await browser.close();
  console.log(`rendered ${frames} frames`);
})();
