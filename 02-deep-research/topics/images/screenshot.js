const puppeteer = require('puppeteer');
const path = require('path');

const files = [
  { html: 'openclaw-evolution-stages.html', png: 'openclaw-evolution-stages.png', width: 1060, height: 520 },
];

(async () => {
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  for (const file of files) {
    const page = await browser.newPage();
    await page.setViewport({ 
      width: file.width, 
      height: file.height, 
      deviceScaleFactor: 2
    });
    
    const htmlPath = path.resolve(__dirname, file.html);
    await page.goto(`file://${htmlPath}`, { waitUntil: 'networkidle0' });
    await page.evaluate(() => document.fonts.ready);
    await new Promise(r => setTimeout(r, 1000));
    
    await page.screenshot({ 
      path: path.resolve(__dirname, file.png),
      clip: { x: 0, y: 0, width: file.width, height: file.height }
    });
    console.log(`✅ ${file.png} generated`);
    await page.close();
  }
  
  await browser.close();
  console.log('Done!');
})();
