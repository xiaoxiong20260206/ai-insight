<script>
    (function() {
        // ===== TOC SCROLL SPY =====
        const tocLinks = document.querySelectorAll('.toc-link[href^="#"]');
        const sections = Array.from(tocLinks)
            .map(l => document.querySelector(l.getAttribute('href')))
            .filter(Boolean);

        function updateToc() {
            let active = null;
            const scrollY = window.scrollY + 120;
            for (const sec of sections) {
                if (sec.getBoundingClientRect().top + window.scrollY <= scrollY) {
                    active = sec;
                }
            }
            tocLinks.forEach(l => {
                const target = document.querySelector(l.getAttribute('href'));
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

        // ===== ANIMATE ON SCROLL =====
        const animEls = document.querySelectorAll('.animate-on-scroll');
        if (animEls.length) {
            const observer = new IntersectionObserver(entries => {
                entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target); } });
            }, { rootMargin: '0px 0px -40px 0px', threshold: 0.08 });
            animEls.forEach(el => observer.observe(el));
        }
    })();
</script>
