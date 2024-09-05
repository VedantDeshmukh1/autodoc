document.addEventListener('DOMContentLoaded', (event) => {
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const themeToggle = document.getElementById('theme-toggle');

    searchInput.addEventListener('input', debounce(performSearch, 300));

    themeToggle.addEventListener('click', toggleTheme);

    function performSearch() {
        const query = searchInput.value;
        if (query.length < 2) {
            searchResults.innerHTML = '';
            return;
        }

        fetch(`/search?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(results => {
                searchResults.innerHTML = results.map(result => `
                    <div class="search-result">
                        <a href="/file/${result.file}#${result.type}-${result.name || ''}">
                            ${result.file} - ${result.type} ${result.name || ''}
                        </a>
                    </div>
                `).join('');
            });
    }

    function toggleTheme() {
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('theme', document.body.classList.contains('dark-mode') ? 'dark' : 'light');
    }

    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Apply saved theme
    if (localStorage.getItem('theme') === 'dark') {
        document.body.classList.add('dark-mode');
    }
});