<script>
    (function() {
        // ===== TAB NAVIGATION (v4.0) =====
        const tabNav = document.querySelector('.tab-nav');
        const tabBtns = document.querySelectorAll('.tab-btn');
        const tabPanels = document.querySelectorAll('.tab-panel');

        function switchTab(tabId) {
            // Update buttons
            tabBtns.forEach(btn => {
                btn.classList.toggle('active', btn.dataset.tab === tabId);
            });
            // Update panels
            tabPanels.forEach(panel => {
                panel.classList.toggle('active', panel.dataset.tab === tabId);
            });
            // Update sidebar TOC active state
            const tocLinks = document.querySelectorAll('.toc-link');
            tocLinks.forEach(link => {
                const href = link.getAttribute('href');
                if (href === '#' + tabId) {
                    link.classList.add('toc-active');
                } else if (tabId && !href.startsWith('#' + tabId)) {
                    // Only remove active from board-section TOC links, not overview/heat/data/watch
                    const boardIds = ['llm', 'coding', 'app', 'industry', 'enterprise'];
                    if (boardIds.some(id => href === '#' + id)) {
                        link.classList.remove('toc-active');
                    }
                }
            });
            // Scroll to tab navigation area so user sees the new tab content
            // (scrolling to contentInner.offsetTop jumps to page top, making it look like nothing changed — #132 fix 2026-07-01)
            const tabNavEl = document.querySelector('.tab-nav');
            if (tabNavEl) {
                window.scrollTo({ top: tabNavEl.offsetTop - 20, behavior: 'smooth' });
            }
        }

        if (tabBtns.length && tabPanels.length) {
            tabBtns.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    switchTab(btn.dataset.tab);
                });
                // Keyboard support
                btn.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        switchTab(btn.dataset.tab);
                    }
                    // Arrow key navigation
                    const btns = Array.from(tabBtns);
                    const idx = btns.indexOf(btn);
                    if (e.key === 'ArrowRight' && idx < btns.length - 1) {
                        e.preventDefault();
                        btns[idx + 1].focus();
                        switchTab(btns[idx + 1].dataset.tab);
                    }
                    if (e.key === 'ArrowLeft' && idx > 0) {
                        e.preventDefault();
                        btns[idx - 1].focus();
                        switchTab(btns[idx - 1].dataset.tab);
                    }
                });
            });

            // Show first tab by default if none active
            const hasActive = document.querySelector('.tab-panel.active');
            if (!hasActive && tabPanels.length > 0) {
                tabPanels[0].classList.add('active');
                if (tabBtns[0]) tabBtns[0].classList.add('active');
            }
        }

        // ===== TOC SCROLL SPY =====
        const tocLinks = document.querySelectorAll('.toc-link[href^="#"]');
        const sections = Array.from(tocLinks)
            .map(l => document.querySelector(l.getAttribute('href')))
            .filter(Boolean);

        function updateToc() {
            // Skip scroll spy for tab-managed sections (they're hidden/shown by tab)
            const boardIds = ['llm', 'coding', 'app', 'industry', 'enterprise'];
            const activeTabId = document.querySelector('.tab-btn.active')?.dataset.tab || '';
            
            let active = null;
            const scrollY = window.scrollY + 120;
            for (const sec of sections) {
                if (!sec) continue;
                const secId = sec.id;
                // For board sections, only mark active if it's the current tab
                if (boardIds.includes(secId)) {
                    if (secId === activeTabId) {
                        active = sec;
                    }
                    continue;
                }
                if (sec.getBoundingClientRect().top + window.scrollY <= scrollY) {
                    active = sec;
                }
            }
            tocLinks.forEach(l => {
                const target = document.querySelector(l.getAttribute('href'));
                const targetId = target?.id;
                // Don't change active for tab-managed sections (that's Tab's job)
                if (boardIds.includes(targetId)) return;
                l.classList.toggle('toc-active', target === active);
            });
        }

        // ===== READING PROGRESS =====
        const progressFill = document.getElementById('readingProgress');
        function updateProgress() {
            if (!progressFill) return;
            const doc = document.documentElement;
            const scrollTop = window.scrollY;
            const total = doc.scrollHeight - doc.clientHeight;
            const pct = total > 0 ? Math.round((scrollTop / total) * 100) : 0;
            progressFill.style.width = pct + '%';
        }

        window.addEventListener('scroll', () => {
            updateToc();
            updateProgress();
            // scroll-to-top visibility
            const btn = document.getElementById('scrollToTop');
            if (btn) btn.classList.toggle('visible', window.scrollY > 400);
        }, { passive: true });

        updateToc();
        updateProgress();

        // ===== SCROLL TO TOP =====
        const scrollBtn = document.getElementById('scrollToTop');
        if (scrollBtn) {
            scrollBtn.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
        }

        // ===== SIDEBAR COLLAPSE =====
        const collapseBtn = document.getElementById('collapseBtn');
        const sidebar = document.getElementById('sidebar');
        if (collapseBtn && sidebar) {
            collapseBtn.addEventListener('click', () => {
                const isCollapsed = sidebar.classList.toggle('sidebar-collapsed');
                collapseBtn.textContent = isCollapsed ? '»' : '«';
                collapseBtn.classList.toggle('collapsed-pos', isCollapsed);
            });
        }

        // ===== SIDEBAR TOC LINKS → TAB SWITCH =====
        // When clicking a board TOC link, switch to that tab
        const boardTocLinks = document.querySelectorAll('.toc-link[href^="#"]');
        boardTocLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                const href = link.getAttribute('href');
                const targetId = href.replace('#', '');
                const boardIds = ['llm', 'coding', 'app', 'industry', 'enterprise'];
                if (boardIds.includes(targetId)) {
                    e.preventDefault();
                    switchTab(targetId);
                    // Scroll to tab nav area
                    const tabNavEl = document.querySelector('.tab-nav');
                    if (tabNavEl) {
                        window.scrollTo({ top: tabNavEl.offsetTop - 20, behavior: 'smooth' });
                    }
                }
            });
        });

        // ===== ANIMATE ON SCROLL =====
        const animEls = document.querySelectorAll('.animate-on-scroll');
        if (animEls.length) {
            const observer = new IntersectionObserver(entries => {
                entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target); } });
            }, { rootMargin: '0px 0px -40px 0px', threshold: 0.08 });
            animEls.forEach(el => observer.observe(el));
        }

        // ===== PREFERS-REDUCED-MOTION =====
        if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
            document.querySelectorAll('.animate-on-scroll').forEach(el => {
                el.classList.add('visible');
            });
        }
    })();
</script>
