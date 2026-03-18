/**
 * HTML智能截图脚本 - 动态匹配内容高度
 * 
 * 核心原理：
 * 1. HTML文件中不设置固定高度，让内容自然撑开
 * 2. Puppeteer渲染后动态获取container的实际高度
 * 3. 根据实际高度进行截图，确保内容完整
 * 
 * 使用方式：
 * node scripts/screenshot-html.js <html目录或单个文件>
 * 
 * 示例：
 * node scripts/screenshot-html.js 02-deep-research/topics/kim-docs/images/
 * node scripts/screenshot-html.js 02-deep-research/topics/kim-docs/images/wukong-03-security.html
 */

const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// 辅助函数：延时
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

// 默认配置
const CONFIG = {
    width: 1060,           // 固定宽度
    deviceScaleFactor: 2,  // 2x清晰度
    padding: 0,            // 额外padding（防止边缘裁切）
};

async function getContentHeight(page) {
    // 获取.container元素的实际高度，如果没有则获取body高度
    return await page.evaluate(() => {
        const container = document.querySelector('.container');
        if (container) {
            return container.scrollHeight;
        }
        return document.body.scrollHeight;
    });
}

async function screenshotHTML(htmlPath) {
    const browser = await puppeteer.launch({ headless: 'new' });
    const page = await browser.newPage();
    
    // 先用一个大高度打开页面
    await page.setViewport({ 
        width: CONFIG.width, 
        height: 2000, // 临时大高度
        deviceScaleFactor: CONFIG.deviceScaleFactor 
    });
    
    const absolutePath = path.resolve(htmlPath);
    await page.goto('file://' + absolutePath, { waitUntil: 'networkidle0' });
    await page.evaluate(() => document.fonts.ready);
    
    // 动态获取内容实际高度
    const contentHeight = await getContentHeight(page);
    const finalHeight = contentHeight + CONFIG.padding;
    
    // 重新设置viewport为实际高度
    await page.setViewport({ 
        width: CONFIG.width, 
        height: finalHeight, 
        deviceScaleFactor: CONFIG.deviceScaleFactor 
    });
    
    // 等待重新渲染
    await delay(100);
    
    // 生成PNG文件路径
    const pngPath = htmlPath.replace(/\.html$/, '.png');
    
    // 截图
    await page.screenshot({ 
        path: pngPath, 
        clip: { 
            x: 0, 
            y: 0, 
            width: CONFIG.width, 
            height: finalHeight 
        } 
    });
    
    console.log(`✅ ${path.basename(pngPath)} (${CONFIG.width}x${finalHeight})`);
    
    await browser.close();
    return { path: pngPath, width: CONFIG.width, height: finalHeight };
}

async function screenshotDirectory(dirPath) {
    const files = fs.readdirSync(dirPath)
        .filter(f => f.endsWith('.html'))
        .map(f => path.join(dirPath, f));
    
    console.log(`\n📷 Found ${files.length} HTML files to screenshot\n`);
    
    const browser = await puppeteer.launch({ headless: 'new' });
    const results = [];
    
    for (const htmlPath of files) {
        const page = await browser.newPage();
        
        // 先用一个大高度打开页面
        await page.setViewport({ 
            width: CONFIG.width, 
            height: 2000,
            deviceScaleFactor: CONFIG.deviceScaleFactor 
        });
        
        const absolutePath = path.resolve(htmlPath);
        await page.goto('file://' + absolutePath, { waitUntil: 'networkidle0' });
        await page.evaluate(() => document.fonts.ready);
        
        // 动态获取内容实际高度
        const contentHeight = await getContentHeight(page);
        const finalHeight = contentHeight + CONFIG.padding;
        
        // 重新设置viewport为实际高度
        await page.setViewport({ 
            width: CONFIG.width, 
            height: finalHeight, 
            deviceScaleFactor: CONFIG.deviceScaleFactor 
        });
        
        await delay(100);
        
        const pngPath = htmlPath.replace(/\.html$/, '.png');
        
        await page.screenshot({ 
            path: pngPath, 
            clip: { 
                x: 0, 
                y: 0, 
                width: CONFIG.width, 
                height: finalHeight 
            } 
        });
        
        console.log(`✅ ${path.basename(pngPath)} (${CONFIG.width}x${finalHeight})`);
        results.push({ path: pngPath, width: CONFIG.width, height: finalHeight });
        
        await page.close();
    }
    
    await browser.close();
    console.log(`\n🎉 All ${results.length} screenshots generated!\n`);
    return results;
}

async function main() {
    const target = process.argv[2];
    
    if (!target) {
        console.log('Usage: node screenshot-html.js <html-file-or-directory>');
        process.exit(1);
    }
    
    const targetPath = path.resolve(target);
    const stat = fs.statSync(targetPath);
    
    if (stat.isDirectory()) {
        await screenshotDirectory(targetPath);
    } else if (stat.isFile() && target.endsWith('.html')) {
        await screenshotHTML(targetPath);
    } else {
        console.error('Error: Target must be an HTML file or directory containing HTML files');
        process.exit(1);
    }
}

main().catch(console.error);
