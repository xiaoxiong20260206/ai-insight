/**
 * HTML智能截图脚本 — html-screenshot 原子技能
 * 
 * 功能：将 HTML 文件渲染为高清 PNG 截图
 * 
 * 两种模式自动适配：
 *   - 动态高度：HTML不设固定高度，脚本自动获取 scrollHeight
 *   - 固定高度：HTML设了固定高度，脚本按 HTML 声明的尺寸截图
 * 
 * 使用方式：
 *   node screenshot-html.js <html目录或单个文件>
 * 
 * 示例：
 *   node screenshot-html.js 02-deep-research/topics/kim-docs/images/
 *   node screenshot-html.js some-chart.html
 */

let puppeteer;
try {
    puppeteer = require('puppeteer');
} catch (e) {
    console.error('❌ 未安装 puppeteer。请先执行:');
    console.error('   npm install puppeteer');
    process.exit(1);
}
const path = require('path');
const fs = require('fs');

const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

// 默认配置
const CONFIG = {
    width: 1060,           // 固定宽度
    deviceScaleFactor: 2,  // 2x高清
    padding: 0,            // 额外padding（防边缘裁切）
};

/**
 * 获取页面内容的实际高度
 * 兼容多种容器 class 命名：.container / .outer-container / .white-border / body
 */
async function getContentHeight(page) {
    return await page.evaluate(() => {
        // 按优先级依次尝试多种容器选择器
        const selectors = ['.container', '.outer-container', '.white-border'];
        for (const sel of selectors) {
            const el = document.querySelector(sel);
            if (el) return el.scrollHeight;
        }
        return document.body.scrollHeight;
    });
}

/**
 * 检测 HTML 是否声明了固定高度（即固定高度模式）
 * 如果 body 有 overflow:hidden 且有明确的 height，认为是固定高度模式
 */
async function detectFixedHeight(page) {
    return await page.evaluate(() => {
        const body = document.body;
        const style = window.getComputedStyle(body);
        const hasOverflowHidden = style.overflow === 'hidden' || style.overflowY === 'hidden';
        const height = parseInt(style.height, 10);
        // 有 overflow:hidden 且高度 < 3000（排除默认值），认为是固定高度
        if (hasOverflowHidden && height > 0 && height < 3000) {
            return { fixed: true, width: parseInt(style.width, 10), height };
        }
        return { fixed: false };
    });
}

/**
 * 截图单个 HTML 文件（需要传入已启动的 browser）
 */
async function screenshotFile(browser, htmlPath) {
    const page = await browser.newPage();
    
    try {
        // 先用大高度打开，让内容完全渲染
        await page.setViewport({ 
            width: CONFIG.width, 
            height: 2000,
            deviceScaleFactor: CONFIG.deviceScaleFactor 
        });
        
        const absolutePath = path.resolve(htmlPath);
        
        if (!fs.existsSync(absolutePath)) {
            console.error(`  ❌ 文件不存在: ${htmlPath}`);
            return null;
        }
        
        await page.goto('file://' + absolutePath, { 
            waitUntil: 'networkidle0',
            timeout: 15000
        });
        
        // 等待字体加载
        await page.evaluate(() => document.fonts.ready);
        await delay(200);
        
        // 检测是固定高度还是动态高度
        const detection = await detectFixedHeight(page);
        let finalWidth, finalHeight;
        
        if (detection.fixed) {
            // 固定高度模式：按 HTML 声明的尺寸截图
            finalWidth = detection.width || CONFIG.width;
            finalHeight = detection.height;
        } else {
            // 动态高度模式：获取内容实际高度
            finalWidth = CONFIG.width;
            const contentHeight = await getContentHeight(page);
            finalHeight = contentHeight + CONFIG.padding;
        }
        
        // 重新设置 viewport 为实际尺寸
        await page.setViewport({ 
            width: finalWidth, 
            height: finalHeight, 
            deviceScaleFactor: CONFIG.deviceScaleFactor 
        });
        await delay(100);
        
        // 生成 PNG 路径
        const pngPath = htmlPath.replace(/\.html$/, '.png');
        
        // 截图
        await page.screenshot({ 
            path: pngPath, 
            clip: { x: 0, y: 0, width: finalWidth, height: finalHeight } 
        });
        
        const mode = detection.fixed ? '固定' : '动态';
        console.log(`  ✅ ${path.basename(pngPath)} (${finalWidth}x${finalHeight}, ${mode}高度)`);
        
        return { path: pngPath, width: finalWidth, height: finalHeight, mode };
        
    } catch (err) {
        console.error(`  ❌ ${path.basename(htmlPath)} 截图失败: ${err.message}`);
        return null;
    } finally {
        await page.close();
    }
}

/**
 * 主函数
 */
async function main() {
    const target = process.argv[2];
    
    if (!target) {
        console.log('Usage: node screenshot-html.js <html-file-or-directory>');
        console.log('');
        console.log('Examples:');
        console.log('  node screenshot-html.js ./images/           # 截图目录下所有HTML');
        console.log('  node screenshot-html.js chart.html          # 截图单个文件');
        process.exit(1);
    }
    
    const targetPath = path.resolve(target);
    
    if (!fs.existsSync(targetPath)) {
        console.error(`Error: 路径不存在: ${target}`);
        process.exit(1);
    }
    
    const stat = fs.statSync(targetPath);
    let htmlFiles = [];
    
    if (stat.isDirectory()) {
        htmlFiles = fs.readdirSync(targetPath)
            .filter(f => f.endsWith('.html'))
            .map(f => path.join(targetPath, f));
    } else if (stat.isFile() && target.endsWith('.html')) {
        htmlFiles = [targetPath];
    } else {
        console.error('Error: 目标必须是 HTML 文件或包含 HTML 文件的目录');
        process.exit(1);
    }
    
    if (htmlFiles.length === 0) {
        console.log('⚠️  目录中没有找到 HTML 文件');
        process.exit(0);
    }
    
    console.log(`\n📷 准备截图 ${htmlFiles.length} 个 HTML 文件\n`);
    
    // 只启动一次浏览器，所有文件共享
    let browser;
    try {
        browser = await puppeteer.launch({ headless: 'new' });
    } catch (err) {
        console.error('❌ 浏览器启动失败。请确认已安装 puppeteer:');
        console.error('   npm install puppeteer');
        console.error(`   错误: ${err.message}`);
        process.exit(1);
    }
    
    const results = [];
    let successCount = 0;
    let failCount = 0;
    
    for (const htmlPath of htmlFiles) {
        const result = await screenshotFile(browser, htmlPath);
        if (result) {
            results.push(result);
            successCount++;
        } else {
            failCount++;
        }
    }
    
    await browser.close();
    
    // 输出汇总
    console.log(`\n${'─'.repeat(40)}`);
    if (failCount === 0) {
        console.log(`🎉 全部完成! ${successCount} 张截图生成成功\n`);
    } else {
        console.log(`⚠️  完成: ${successCount} 成功, ${failCount} 失败\n`);
    }
}

main().catch(err => {
    console.error(`❌ 未预期的错误: ${err.message}`);
    process.exit(1);
});
