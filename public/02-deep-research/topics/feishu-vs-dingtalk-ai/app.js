/* ===== app.js · 飞书 vs 钉钉 AI对比报告 ===== */
(function() {
    'use strict';

    /* ---- Tab 切换 ---- */
    const navBtns = document.querySelectorAll('.nav-btn[data-tab]');
    const tabPanels = document.querySelectorAll('.tab-content');

    function switchTab(targetTabId) {
        tabPanels.forEach(p => { p.style.display = 'none'; });
        navBtns.forEach(b => { b.classList.remove('active'); b.setAttribute('aria-selected', 'false'); });

        const panel = document.getElementById(targetTabId);
        if (panel) {
            panel.style.display = 'block';
            // 触发进入视口的动画
            setTimeout(() => {
                panel.querySelectorAll('.animate-on-scroll').forEach(el => {
                    observer.observe(el);
                });
            }, 10);
        }

        navBtns.forEach(b => {
            if (b.getAttribute('data-tab') === targetTabId) {
                b.classList.add('active');
                b.setAttribute('aria-selected', 'true');
            }
        });
    }

    navBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');
            const scrollTarget = btn.getAttribute('data-scroll');
            switchTab(targetTab);
            if (scrollTarget) {
                setTimeout(() => {
                    const el = document.getElementById(scrollTarget);
                    if (el) { el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
                }, 80);
            }
        });
    });

    /* ---- 键盘导航（左右键切换Tab）---- */
    const tabIds = ['tab-overview', 'tab-feishu', 'tab-dingtalk', 'tab-compare', 'tab-insight', 'tab-more'];
    document.querySelector('.sidebar-nav').addEventListener('keydown', e => {
        const current = [...navBtns].find(b => b.classList.contains('active'));
        if (!current) return;
        const idx = tabIds.indexOf(current.getAttribute('data-tab'));
        if (e.key === 'ArrowDown' && idx < tabIds.length - 1) {
            e.preventDefault();
            switchTab(tabIds[idx + 1]);
        } else if (e.key === 'ArrowUp' && idx > 0) {
            e.preventDefault();
            switchTab(tabIds[idx - 1]);
        }
    });

    /* ---- IntersectionObserver 滚动进入动画 ---- */
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry, i) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('is-visible');
                }, i * 60);
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });

    function observeVisible() {
        document.querySelectorAll('.animate-on-scroll').forEach(el => {
            // 只观察当前可见Tab中的元素
            const panel = el.closest('.tab-content');
            if (!panel || panel.style.display !== 'none') {
                observer.observe(el);
            }
        });
    }

    // 首次加载
    observeVisible();

    /* ---- 进度条动画（在对比Tab首次显示时触发）---- */
    let progressAnimated = false;
    function animateProgressBars() {
        if (progressAnimated) return;
        progressAnimated = true;
        document.querySelectorAll('.bar-fill').forEach(bar => {
            const targetWidth = bar.style.width;
            bar.style.width = '0';
            requestAnimationFrame(() => {
                requestAnimationFrame(() => {
                    bar.style.width = targetWidth;
                });
            });
        });
    }

    // 监听Tab切换到对比页时动画
    const compareBtn = document.querySelector('[data-tab="tab-compare"]');
    if (compareBtn) {
        const originalClick = compareBtn.onclick;
        compareBtn.addEventListener('click', () => {
            setTimeout(animateProgressBars, 300);
        });
    }

    /* ---- 默认显示第一个Tab ---- */
    // 已在HTML中默认显示 tab-overview，通过CSS style=display:none 隐藏其余
    document.getElementById('tab-overview').style.display = 'block';

})();
