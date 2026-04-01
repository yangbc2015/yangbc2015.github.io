// AI WANDER - Main JavaScript
(function() {
    'use strict';

    // ===== Page Loader =====
    window.addEventListener('load', () => {
        setTimeout(() => {
            const loader = document.getElementById('loader');
            if (loader) loader.classList.add('hidden');
        }, 700);
    });

    // ===== Mobile Menu Toggle =====
    const menuToggle = document.getElementById('menu-toggle');
    const siteMenu = document.getElementById('site-menu');
    if (menuToggle && siteMenu) {
        menuToggle.addEventListener('click', () => {
            siteMenu.classList.toggle('active');
        });
    }

    // ===== Reading Progress =====
    const readingProgress = document.getElementById('reading-progress');
    if (readingProgress) {
        window.addEventListener('scroll', () => {
            const winScroll = document.body.scrollTop || document.documentElement.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const scrolled = (winScroll / height) * 100;
            readingProgress.style.width = scrolled + '%';
        }, { passive: true });
    }

    // ===== Back to Top =====
    const backToTop = document.getElementById('back-to-top');
    if (backToTop) {
        window.addEventListener('scroll', () => {
            if (window.pageYOffset > 250) {
                backToTop.classList.add('visible');
            } else {
                backToTop.classList.remove('visible');
            }
        }, { passive: true });

        backToTop.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // ===== Spotlight Effect =====
    const spotlight = document.querySelector('.spotlight');
    if (spotlight) {
        let rafId = null;
        let mouseX = 50;
        let mouseY = 50;
        
        document.addEventListener('mousemove', (e) => {
            mouseX = (e.clientX / window.innerWidth) * 100;
            mouseY = (e.clientY / window.innerHeight) * 100;
            
            if (!rafId) {
                rafId = requestAnimationFrame(() => {
                    spotlight.style.setProperty('--mouse-x', mouseX + '%');
                    spotlight.style.setProperty('--mouse-y', mouseY + '%');
                    rafId = null;
                });
            }
        }, { passive: true });
    }

    // ===== Search Modal =====
    const searchModal = document.getElementById('search-modal');
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const searchClose = document.getElementById('search-close');
    const searchToggle = document.getElementById('search-toggle');
    
    if (searchModal && searchInput && searchResults) {
        let searchData = [];
        let selectedIndex = -1;

        // Load search data
        const searchJsonPath = searchModal.dataset.searchUrl || '/index.json';
        fetch(searchJsonPath)
            .then(response => response.json())
            .then(data => { searchData = data; })
            .catch(err => console.error('Search data load failed:', err));

        function openSearch() {
            searchModal.classList.add('active');
            searchInput.focus();
            searchInput.value = '';
            searchResults.innerHTML = '';
            selectedIndex = -1;
        }

        function closeSearch() {
            searchModal.classList.remove('active');
        }

        function performSearch(query) {
            if (!query.trim()) {
                searchResults.innerHTML = '';
                return;
            }

            const results = searchData.filter(item => {
                const searchText = (item.title + ' ' + item.content + ' ' + (item.tags || []).join(' ')).toLowerCase();
                return searchText.includes(query.toLowerCase());
            }).slice(0, 10);

            if (results.length === 0) {
                searchResults.innerHTML = '<div style="text-align: center; color: var(--text-secondary); padding: 2rem;">没有找到相关结果</div>';
                return;
            }

            searchResults.innerHTML = results.map((item, index) => `
                <div class="search-result-item" data-index="${index}" data-url="${item.permalink}">
                    <div class="search-result-title">${item.title}</div>
                    <div class="search-result-desc">${item.description || item.content.substring(0, 100)}...</div>
                </div>
            `).join('');

            document.querySelectorAll('.search-result-item').forEach(item => {
                item.addEventListener('click', () => {
                    window.location.href = item.dataset.url;
                });
            });

            selectedIndex = 0;
            updateSelection();
        }

        function updateSelection() {
            const items = document.querySelectorAll('.search-result-item');
            items.forEach((item, index) => {
                if (index === selectedIndex) {
                    item.classList.add('selected');
                    item.scrollIntoView({ block: 'nearest' });
                } else {
                    item.classList.remove('selected');
                }
            });
        }

        if (searchToggle) searchToggle.addEventListener('click', openSearch);
        if (searchClose) searchClose.addEventListener('click', closeSearch);

        searchInput.addEventListener('input', (e) => {
            performSearch(e.target.value);
        });

        searchInput.addEventListener('keydown', (e) => {
            const items = document.querySelectorAll('.search-result-item');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
                updateSelection();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                selectedIndex = Math.max(selectedIndex - 1, 0);
                updateSelection();
            } else if (e.key === 'Enter' && selectedIndex >= 0) {
                e.preventDefault();
                const selected = items[selectedIndex];
                if (selected) window.location.href = selected.dataset.url;
            } else if (e.key === 'Escape') {
                closeSearch();
            }
        });

        searchModal.addEventListener('click', (e) => {
            if (e.target === searchModal) closeSearch();
        });

        document.addEventListener('keydown', (e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
                e.preventDefault();
                openSearch();
            }
        });
    }
})();
