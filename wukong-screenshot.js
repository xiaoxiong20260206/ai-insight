const puppeteer = require('puppeteer');
const path = require('path');

const OUTPUT_DIR = '/Users/shenlang/Documents/Codeflicker/AI-Insight/02-deep-research/topics/images/wukong';

(async () => {
    const browser = await puppeteer.launch({
        headless: 'new',
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--window-size=1440,3000']
    });
    
    const page = await browser.newPage();
    await page.setViewport({ width: 1440, height: 900, deviceScaleFactor: 2 });
    
    console.log('🔗 Loading wukong page...');
    await page.goto('https://www.dingtalk.com/wukong', { 
        waitUntil: 'networkidle2',
        timeout: 60000 
    });
    
    // Wait for page to settle
    await new Promise(r => setTimeout(r, 5000));
    
    // Step 0: Take a full-page screenshot first to understand layout
    console.log('📸 0. Full page screenshot for analysis...');
    await page.screenshot({
        path: path.join(OUTPUT_DIR, 'wukong-fullpage.png'),
        fullPage: true
    });
    console.log('✅ Full page done');
    
    // Step 1: Analyze the page structure
    const analysis = await page.evaluate(() => {
        const results = {};
        
        // Find all video elements
        const videos = document.querySelectorAll('video');
        results.videoCount = videos.length;
        results.videos = Array.from(videos).map(v => ({
            src: v.src?.substring(0, 80),
            width: v.offsetWidth,
            height: v.offsetHeight,
            position: getComputedStyle(v.parentElement).position,
            zIndex: getComputedStyle(v.parentElement).zIndex
        }));
        
        // Find fixed/sticky elements
        const allEls = document.querySelectorAll('*');
        results.fixedElements = [];
        for (const el of allEls) {
            const cs = getComputedStyle(el);
            if ((cs.position === 'fixed' || cs.position === 'sticky') && el.offsetHeight > 100) {
                results.fixedElements.push({
                    tag: el.tagName,
                    class: el.className?.substring(0, 60),
                    height: el.offsetHeight,
                    zIndex: cs.zIndex
                });
            }
        }
        
        // Find the value section
        const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
        while (walker.nextNode()) {
            if (walker.currentNode.textContent.includes('悟空的独特价值')) {
                const el = walker.currentNode.parentElement;
                const rect = el.getBoundingClientRect();
                results.valueSectionY = window.scrollY + rect.top;
                results.valueSectionTag = el.tagName;
                results.valueSectionClass = el.className?.substring(0, 60);
                
                // Find the parent section
                let parent = el.parentElement;
                for (let i = 0; i < 5 && parent; i++) {
                    const pRect = parent.getBoundingClientRect();
                    if (pRect.height > 500) {
                        results.sectionParent = {
                            tag: parent.tagName,
                            class: parent.className?.substring(0, 60),
                            top: window.scrollY + pRect.top,
                            height: pRect.height,
                            position: getComputedStyle(parent).position
                        };
                        break;
                    }
                    parent = parent.parentElement;
                }
                break;
            }
        }
        
        results.bodyHeight = document.body.scrollHeight;
        return results;
    });
    
    console.log('Page analysis:', JSON.stringify(analysis, null, 2));
    
    // Step 2: Remove/hide video overlay and fixed elements that block content
    console.log('\n🔧 Removing video overlays...');
    await page.evaluate(() => {
        // Pause and hide all videos
        document.querySelectorAll('video').forEach(v => {
            v.pause();
            v.style.display = 'none';
        });
        
        // Remove fixed/sticky elements that cover the page (except navigation)
        document.querySelectorAll('*').forEach(el => {
            const cs = getComputedStyle(el);
            if (cs.position === 'fixed' && el.offsetHeight > 200) {
                el.style.position = 'absolute';
            }
        });
        
        // Disable all CSS animations and transitions
        const style = document.createElement('style');
        style.textContent = '*, *::before, *::after { animation: none !important; transition: none !important; }';
        document.head.appendChild(style);
    });
    
    await new Promise(r => setTimeout(r, 1000));
    
    // Step 3: Take full page again after removing overlays
    console.log('📸 Full page after cleanup...');
    await page.screenshot({
        path: path.join(OUTPUT_DIR, 'wukong-fullpage-clean.png'),
        fullPage: true
    });
    console.log('✅ Clean full page done');
    
    // Step 4: Now try to capture specific sections
    if (analysis.valueSectionY) {
        const baseY = analysis.valueSectionY;
        
        // Value header (title + tabs)
        console.log(`📸 Scrolling to value section at Y=${baseY}...`);
        await page.evaluate((y) => window.scrollTo(0, y - 80), baseY);
        await new Promise(r => setTimeout(r, 1500));
        await page.screenshot({
            path: path.join(OUTPUT_DIR, 'wukong-value-header.png'),
            clip: { x: 0, y: 0, width: 1440, height: 900 }
        });
        console.log('✅ Value header captured');
        
        // Now click each tab
        const tabTexts = ['身外化身', '如意万法', '千里传音', '灵根共长'];
        const fileNames = ['shenwaifuashen', 'ruyiwanfa', 'qianlichuanyin', 'linggengongzhang'];
        
        for (let i = 0; i < tabTexts.length; i++) {
            console.log(`📸 Tab: ${tabTexts[i]}...`);
            
            await page.evaluate((name) => {
                const spans = document.querySelectorAll('span');
                for (const s of spans) {
                    if (s.textContent.trim() === name && s.offsetWidth > 0) {
                        s.click();
                        // Also try clicking parent
                        if (s.parentElement) s.parentElement.click();
                        return true;
                    }
                }
                return false;
            }, tabTexts[i]);
            
            await new Promise(r => setTimeout(r, 2000));
            
            // Scroll to show content below tabs
            await page.evaluate((y) => window.scrollTo(0, y + 60), baseY);
            await new Promise(r => setTimeout(r, 1000));
            
            await page.screenshot({
                path: path.join(OUTPUT_DIR, `wukong-capability-${fileNames[i]}.png`),
                clip: { x: 0, y: 0, width: 1440, height: 900 }
            });
            console.log(`✅ ${tabTexts[i]} done`);
        }
    }
    
    // Vision section
    console.log('📸 Vision...');
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight - 1000));
    await new Promise(r => setTimeout(r, 2000));
    await page.screenshot({
        path: path.join(OUTPUT_DIR, 'wukong-vision.png'),
        clip: { x: 0, y: 0, width: 1440, height: 900 }
    });
    console.log('✅ Vision done');
    
    await browser.close();
    console.log('\n🎉 All done! Check', OUTPUT_DIR);
})().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});
