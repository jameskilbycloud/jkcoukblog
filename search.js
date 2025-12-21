// Blog Search with Fuse.js - SIMPLE DEBUG VERSION
console.log('[Search] Script loaded');

(function() {
    'use strict';
    
    // Create search box IMMEDIATELY on load
    function createSearchBoxNow() {
        console.log('[Search] Creating search box immediately');
        
        // Find main element
        const main = document.querySelector('main');
        if (!main) {
            console.log('[Search] No main element found, trying body');
            document.body.insertAdjacentHTML('afterbegin', getSearchHTML());
            return;
        }
        
        // Insert at very top of main
        main.insertAdjacentHTML('afterbegin', getSearchHTML());
        console.log('[Search] Search box inserted into main');
        
        // Attach event listener
        const input = document.getElementById('blog-search-input');
        if (input) {
            console.log('[Search] Found search input, loading Fuse.js');
            input.addEventListener('input', debounce(handleSearch, 300));
        }
    }
    
    function getSearchHTML() {
        return `<div id="blog-search-container" style="background: #f8f9fa; padding: 16px; border-bottom: 2px solid #e9ecef; margin-bottom: 20px;">
    <div style="max-width: 600px; margin: 0 auto;">
        <input type="text" 
               id="blog-search-input" 
               placeholder="🔍 Search posts..." 
               style="width: 100%; padding: 12px 16px; font-size: 16px; border: 2px solid #dee2e6; border-radius: 8px; outline: none; box-sizing: border-box;"
               onfocus="this.style.borderColor='#0d6efd'"
               onblur="this.style.borderColor='#dee2e6'">
    </div>
</div>`;
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
    
    function handleSearch(e) {
        const query = e.target.value.trim();
        if (query.length < 2) return;
        
        console.log('[Search] Searching for:', query);
        
        // Dynamically load Fuse.js and search index
        if (!window.Fuse || !window.searchData) {
            loadDependencies(() => performSearch(query));
        } else {
            performSearch(query);
        }
    }
    
    function loadDependencies(callback) {
        console.log('[Search] Loading dependencies');
        
        // Load Fuse.js
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/fuse.js@7.0.0'\;
        script.onload = () => {
            console.log('[Search] Fuse.js loaded');
            
            // Load search index
            fetch('/search-index.min.json')
                .then(r => r.json())
                .then(data => {
                    window.searchData = data;
                    console.log('[Search] Index loaded:', data.length, 'items');
                    callback();
                })
                .catch(e => console.error('[Search] Failed to load index:', e));
        };
        document.head.appendChild(script);
    }
    
    function performSearch(query) {
        if (!window.Fuse || !window.searchData) {
            console.log('[Search] Dependencies not ready');
            return;
        }
        
        const fuse = new window.Fuse(window.searchData, {
            keys: ['title', 'description', 'content'],
            threshold: 0.4,
            minMatchCharLength: 2
        });
        
        const results = fuse.search(query);
        console.log('[Search] Found', results.length, 'results');
        showResults(results, query);
    }
    
    function showResults(results, query) {
        let html = `<div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 99999; display: flex; align-items: center; justify-content: center; padding: 20px;" onclick="if(event.target===this) this.remove()">
    <div style="background: white; border-radius: 12px; max-width: 600px; width: 100%; max-height: 70vh; overflow-y: auto; box-shadow: 0 10px 40px rgba(0,0,0,0.3);">
        <div style="padding: 20px; border-bottom: 1px solid #e0e0e0; font-weight: bold;">
            ${results.length} result${results.length !== 1 ? 's' : ''} for "${escapeHtml(query)}"
        </div>`;
        
        if (results.length === 0) {
            html += `<div style="padding: 40px; text-align: center; color: #999;">No results found</div>`;
        } else {
            results.slice(0, 10).forEach(r => {
                const item = r.item;
                html += `<a href="${item.url}" style="display: block; padding: 16px 20px; border-bottom: 1px solid #f0f0f0; text-decoration: none; color: inherit;" onmouseover="this.style.background='#f8f9fa'" onmouseout="this.style.background='white'">
                    <div style="color: #0d6efd; font-weight: 600; margin-bottom: 4px;">${escapeHtml(item.title)}</div>
                    <div style="color: #666; font-size: 14px;">${escapeHtml((item.description || '').substring(0, 100))}</div>
                </a>`;
            });
        }
        
        html += `</div></div>`;
        
        const div = document.createElement('div');
        div.innerHTML = html;
        document.body.appendChild(div.firstChild);
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Create search box when page loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createSearchBoxNow);
    } else {
        createSearchBoxNow();
    }
    
    console.log('[Search] Initialization complete');
})();
