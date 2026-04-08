/* ============================================================
   飞书 vs 钉钉 深度对比报告 — 长页面交互逻辑
   主要功能：
   1. Scroll Spy — 滚动时高亮左侧目录对应条目
   2. 平滑锚点滚动（含 header offset 补偿）
   3. 侧边栏折叠/展开
   4. 滚动到顶部按钮
   5. 阅读进度条
   6. 入场动画（IntersectionObserver）
   ============================================================ */

(function () {
    "use strict";

    /* ---- 常量 ---- */
    const HEADER_OFFSET = 80;   // 顶部保留高度（px）
    const SPY_OFFSET = 100;     // Scroll Spy 触发偏移
    const SCROLL_TOP_THRESHOLD = 300;

    /* ---- DOM 引用 ---- */
    const sidebar     = document.getElementById("sidebar");
    const collapseBtn = document.getElementById("collapseBtn");
    const scrollTopBtn = document.getElementById("scrollToTop");
    const progressBar = document.getElementById("readingProgress");

    // 所有 toc-link
    const tocLinks = Array.from(document.querySelectorAll(".toc-link"));

    // 所有带 id 的 section / 锚点目标
    const anchorIds = tocLinks
        .map(a => a.getAttribute("href"))
        .filter(h => h && h.startsWith("#"))
        .map(h => h.slice(1));

    const anchorEls = anchorIds
        .map(id => document.getElementById(id))
        .filter(Boolean);

    /* ===========================================================
       1. 平滑锚点滚动
    =========================================================== */
    document.querySelectorAll('a[href^="#"]').forEach(link => {
        link.addEventListener("click", e => {
            const targetId = link.getAttribute("href").slice(1);
            const target = document.getElementById(targetId);
            if (!target) return;
            e.preventDefault();
            const top = target.getBoundingClientRect().top + window.scrollY - HEADER_OFFSET;
            window.scrollTo({ top, behavior: "smooth" });
        });
    });

    /* ===========================================================
       2. Scroll Spy — 滚动时更新目录高亮
    =========================================================== */
    function getActiveId() {
        const scrollY = window.scrollY + SPY_OFFSET;
        let activeId = anchorIds[0];
        for (const el of anchorEls) {
            if (el.offsetTop <= scrollY) {
                activeId = el.id;
            } else {
                break;
            }
        }
        return activeId;
    }

    function updateTocHighlight() {
        const activeId = getActiveId();
        tocLinks.forEach(link => {
            const href = link.getAttribute("href");
            if (href === "#" + activeId) {
                link.classList.add("toc-active");
                // 侧边栏自动滚动到可见区域
                ensureVisible(link);
            } else {
                link.classList.remove("toc-active");
            }
        });
    }

    function ensureVisible(el) {
        if (!sidebar) return;
        const elTop = el.offsetTop;
        const elBottom = elTop + el.offsetHeight;
        const sTop = sidebar.scrollTop;
        const sBottom = sTop + sidebar.clientHeight;
        if (elTop < sTop + 60) {
            sidebar.scrollTo({ top: elTop - 60, behavior: "smooth" });
        } else if (elBottom > sBottom - 60) {
            sidebar.scrollTo({ top: elBottom - sidebar.clientHeight + 60, behavior: "smooth" });
        }
    }

    /* ===========================================================
       3. 阅读进度条
    =========================================================== */
    function updateProgress() {
        if (!progressBar) return;
        const doc = document.documentElement;
        const scrolled = window.scrollY;
        const total = doc.scrollHeight - doc.clientHeight;
        const pct = total > 0 ? Math.min(100, (scrolled / total) * 100) : 0;
        progressBar.style.width = pct.toFixed(1) + "%";
    }

    /* ===========================================================
       4. 回到顶部按钮
    =========================================================== */
    function updateScrollTopBtn() {
        if (!scrollTopBtn) return;
        if (window.scrollY > SCROLL_TOP_THRESHOLD) {
            scrollTopBtn.classList.add("visible");
        } else {
            scrollTopBtn.classList.remove("visible");
        }
    }

    scrollTopBtn && scrollTopBtn.addEventListener("click", () => {
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    /* ===========================================================
       5. 侧边栏折叠/展开
    =========================================================== */
    collapseBtn && collapseBtn.addEventListener("click", () => {
        const isCollapsed = sidebar.classList.toggle("sidebar-collapsed");
        collapseBtn.textContent = isCollapsed ? "»" : "«";
        collapseBtn.title = isCollapsed ? "展开导航" : "折叠导航";
        collapseBtn.setAttribute("aria-label", isCollapsed ? "展开导航" : "折叠导航");
        // 切换按钮位置：展开时在侧边栏右边沿，折叠时贴左侧
        if (isCollapsed) {
            collapseBtn.classList.add("collapsed-pos");
        } else {
            collapseBtn.classList.remove("collapsed-pos");
        }
    });

    /* ===========================================================
       6. 入场动画（IntersectionObserver）
    =========================================================== */
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("visible");
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.08, rootMargin: "0px 0px -40px 0px" });

    document.querySelectorAll(".animate-on-scroll").forEach(el => observer.observe(el));

    /* ===========================================================
       7. 统一 scroll 监听（节流）
    =========================================================== */
    let ticking = false;
    window.addEventListener("scroll", () => {
        if (!ticking) {
            requestAnimationFrame(() => {
                updateTocHighlight();
                updateProgress();
                updateScrollTopBtn();
                ticking = false;
            });
            ticking = true;
        }
    }, { passive: true });

    /* ---- 初始化 ---- */
    updateTocHighlight();
    updateProgress();
    updateScrollTopBtn();

})();
