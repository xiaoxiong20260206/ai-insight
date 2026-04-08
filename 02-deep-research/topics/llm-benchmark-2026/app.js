/* app.js — 清爽调研报告 v5.0 交互逻辑
   功能：Scroll Spy + 阅读进度 + 进度条视口动画 + 滚动入场 + 侧边栏折叠
*/
(function () {
    "use strict";

    const HEADER_OFFSET = 72;
    const SPY_OFFSET    = 110;

    const sidebar     = document.getElementById("sidebar");
    const collapseBtn = document.getElementById("collapseBtn");
    const progressBar = document.getElementById("readingProgress");
    const scrollTopBtn = document.getElementById("scrollToTop");

    /* ---- 平滑锚点滚动 ---- */
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener("click", e => {
            const id = link.getAttribute("href").slice(1);
            const target = document.getElementById(id);
            if (!target) return;
            e.preventDefault();
            window.scrollTo({
                top: target.getBoundingClientRect().top + window.scrollY - HEADER_OFFSET,
                behavior: "smooth"
            });
        });
    });

    /* ---- Scroll Spy ---- */
    const tocLinks = Array.from(document.querySelectorAll(".toc-link"));
    const anchorEls = tocLinks.map(a => {
        const href = a.getAttribute("href") || "";
        return document.getElementById(href.slice(1));
    }).filter(Boolean);

    function updateTocHighlight() {
        const scrollY = window.scrollY + SPY_OFFSET;
        let activeEl = anchorEls[0];
        for (const el of anchorEls) {
            if (el && el.offsetTop <= scrollY) activeEl = el;
            else break;
        }
        const activeId = activeEl ? "#" + activeEl.id : "";
        tocLinks.forEach(link => {
            link.classList.toggle("toc-active", link.getAttribute("href") === activeId);
        });
    }

    /* ---- 阅读进度 ---- */
    function updateProgress() {
        if (!progressBar) return;
        const total = document.documentElement.scrollHeight - window.innerHeight;
        const pct = total > 0 ? Math.min(100, (window.scrollY / total) * 100) : 0;
        progressBar.style.width = pct.toFixed(1) + "%";
    }

    /* ---- 侧边栏折叠 ---- */
    if (collapseBtn && sidebar) {
        collapseBtn.addEventListener("click", () => {
            const isCollapsed = sidebar.classList.toggle("sidebar-collapsed");
            collapseBtn.textContent = isCollapsed ? "»" : "«";
            collapseBtn.classList.toggle("collapsed-pos", isCollapsed);
            collapseBtn.setAttribute("aria-label", isCollapsed ? "展开导航" : "折叠导航");
        });
    }

    /* ---- 回到顶部 ---- */
    if (scrollTopBtn) {
        scrollTopBtn.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
    }

    /* ---- 滚动入场动画 — v5.0 降级增强 ---- */
    const animEls = document.querySelectorAll(".animate-on-scroll");
    if (!("IntersectionObserver" in window)) {
        // 降级：直接显示所有元素
        animEls.forEach(el => el.classList.add("visible"));
    } else {
        const scrollObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("visible");
                    scrollObserver.unobserve(entry.target);
                }
            });
        }, { threshold: 0.06, rootMargin: "0px 0px -30px 0px" });
        animEls.forEach(el => scrollObserver.observe(el));
    }

    /* ---- 进度条视口动画 — v5.0 新增 ---- */
    const barFills = document.querySelectorAll(".bar-fill");
    if ("IntersectionObserver" in window && barFills.length) {
        const barObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const el = entry.target;
                    const targetW = el.dataset.targetWidth || el.style.width || "0%";
                    el.style.width = "0%";
                    requestAnimationFrame(() => {
                        requestAnimationFrame(() => { el.style.width = targetW; });
                    });
                    barObserver.unobserve(el);
                }
            });
        }, { threshold: 0.3 });
        barFills.forEach(el => {
            el.dataset.targetWidth = el.style.width || "0%";
            el.style.width = "0%";
            barObserver.observe(el);
        });
    }

    /* ---- rAF 节流滚动事件 ---- */
    let ticking = false;
    window.addEventListener("scroll", () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                updateTocHighlight();
                updateProgress();
                if (scrollTopBtn) {
                    scrollTopBtn.classList.toggle("visible", window.scrollY > 280);
                }
                ticking = false;
            });
            ticking = true;
        }
    }, { passive: true });

    // 初始化
    updateTocHighlight();
    updateProgress();
})();
