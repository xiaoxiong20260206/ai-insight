const puppeteer = require('puppeteer');
const path = require('path');

// 每个文件的精确尺寸配置
const files = [
  { html: 'architecture.html', png: 'architecture.png', width: 1060, height: 720 },
  { html: 'tracking-matrix.html', png: 'tracking-matrix.png', width: 1060, height: 660 },
  { html: 'daily-workflow.html', png: 'daily-workflow.png', width: 1060, height: 560 },
  { html: 'knowledge-system.html', png: 'knowledge-system.png', width: 1060, height: 660 }
];

(async () => {
  console.log('🚀 启动浏览器...');
  const browser = await puppeteer.launch({
    headless: 'new',
    executablePath: '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  for (const file of files) {
    console.log(`📸 处理 ${file.html}...`);
    const page = await browser.newPage();
    
    // 设置viewport为页面精确尺寸，使用2x像素密度
    await page.setViewport({ 
      width: file.width, 
      height: file.height, 
      deviceScaleFactor: 2 
    });
    
    const htmlPath = path.resolve(__dirname, file.html);
    await page.goto(`file://${htmlPath}`, { 
      waitUntil: 'networkidle0',
      timeout: 30000
    });
    
    // 等待字体加载完成
    await page.evaluate(() => document.fonts.ready);
    
    // 额外等待确保渲染完成
    await new Promise(r => setTimeout(r, 1000));
    
    // 使用clip参数精确截取页面区域
    await page.screenshot({ 
      path: path.resolve(__dirname, file.png),
      clip: { 
        x: 0, 
        y: 0, 
        width: file.width, 
        height: file.height 
      }
    });
    
    console.log(`  ✅ ${file.png} 生成成功 (${file.width}x${file.height})`);
    await page.close();
  }
  
  await browser.close();
  console.log('🎉 所有图片生成完成');
})();
