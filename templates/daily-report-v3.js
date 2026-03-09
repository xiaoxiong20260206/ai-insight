<script>
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.tab-btn').forEach(b => b.setAttribute('aria-selected', 'false'));
                document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
                btn.setAttribute('aria-selected', 'true');
                document.getElementById(btn.dataset.tab).classList.add('active');
            });
        });
    </script>