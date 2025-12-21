// Blog Search - WORKING VERSION
console.log('[Search] Script loaded and executing');

(function() {
    'use strict';
    
    let searchIndex = null;
    let fuse = null;
    
    // Create search box immediately
    function createSearchBox() {
        console.log('[Search] Creating search box');
        const searchHTML = '<div id="blog-search-container" style="background: #f8f9fa; padding: 16px; border-bottom: 2px solid #e9ecef; margin-bottom: 20px;"><div style="max-width: 600px; margin: 0 auto;"><input type="text" id="blog-search-input" placeholder="🔍 Search posts..." style="width: 100%; padding: 12px 16px; font-size: 16px; border: 2px solid #dee2e6; border-radius: 8px; box-sizing: border-box;" onfocus="this.style.borderColor=\'#0d6efd\'" onblur="this.style.borderColor=\'#dee2e6\'"></div></div>';
        
        const main = document.querySelector('main');
        if (main) {
            main.insertAdjacentHTML('afterbegin', searchHTML);
            console.log('[Search] Search box created in main');
            attachSearchListener();
        }
    }
    
    function attachSearchListener() {
        const input = document.getElementById('blog-search-input');
        if (input) {
            input.addEventListener('input', debounce(handleSearch, 300));
            console.log('[Search] Event listener attached');
        }
    }
    
    function debounce(func, ms) {
        let timeout;
        return function(...args) {
            clearTimeout(timeout);
            timeout = setTimeout(() => func.apply(this, args), ms);
        };
    }
    
    function handleSearch(e) {
        const query = e.target.value.trim();
        console.log('[Search] Query:', query);
        
        if (query.length < 2) {
            hideResults();
            return;
        }
        
        // Load dependencies if needed
        if (!searchIndex) {
            console.log('[Search] Loading index and Fuse');
            loadIndex();
        } else if (fuse) {
            console.log('[Search] Index ready, searching');
            search(query);
        }
    }
    
    function loadIndex() {
        console.log('[Search] Fetching search-index.min.json');
        fetch('/search-index.min.json')
            .then(r => {
                console.log('[Search] Response status:', r.status);
                return r.json();
            })
            .then(data => {
                console.log('[Search] Index loaded:', data.length, 'items');
                searchIndex = data;
                loadFuse();
            })
            .catch(e => console.error('[Search] Failed to load index:', e));
    }
    
    function loadFuse() {
        console.log('[Search] Loading Fuse.js');
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/fuse.js@7.0.0';
        script.onload = () => {
            console.log('[Search] Fuse.js loaded');
            fuse = new window.Fuse(searchIndex, {
                keys: ['title', 'description', 'content'],
                threshold: 0.4
            });
            console.log('[Search] Fuse initialized');
            
            // Do search if there's a query
            const input = document.getElementById('blog-search-input');
            if (input && input.value.length >= 2) {
                search(input.value.trim());
            }
        };
        script.onerror = () => console.error('[Search] Failed to load Fuse.js');
        document.head.appendChild(script);
    }
    
    function search(query) {
        if (!fuse) {
            console.log('[Search] Fuse not ready');
            return;
        }
        
        const results = fuse.search(query);
        console.log('[Search] Found', results.length, 'results');
        displayResults(results, query);
    }
    
    function displayResults(results, query) {
        let html = '<div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.5); z-index: 99999; padding: 40px 20px; overflow-y: auto;" onclick="if(event.target===this) this.remove()"><div style="background: white; border-radius: 12px; max-width: 600px; margin: 0 auto; max-height: 70vh; overflow-y: auto; box-shadow: 0 10px 40px rgba(0,0,0,0.3);">';
        
        html += '<div style="padding: 20px; border-bottom: 1px solid #e0e0e0; font-weight: bold; position: sticky; top: 0; background: white;">' + results.length + ' result' + (results.length !== 1 ? 's' : '') + ' for "' + escapeHtml(query) + '"</div>';
        
        if (results.length === 0) {
            html += '<div style="padding: 40px; text-align: center; color: #999;">No results found</div>';
        } else {
            results.slice(0, 10).forEach(r => {
                const item = r.item;
                html += '<a href="' + item.url + '" style="display: block; padding: 16px 20px; border-bottom: 1px solid #f0f0f0; text-decoration: none; color: inherit;" onmouseover="this.style.background=\'#f8f9fa\'" onmouseout="this.style.background=\'white\'">';
                html += '<div style="color: #0d6efd; font-weight: 600; margin-bottom: 4px;">' + escapeHtml(item.title) + '</div>';
                html += '<div style="color: #666; font-size: 14px;">' + escapeHtml((item.description || '').substring(0, 100)) + '</div>';
                html += '</a>';
            });
        }
        
        html += '</div></div>';
        
        const div = document.createElement('div');
        div.innerHTML = html;
        document.body.appendChild(div.firstChild);
    }
    
    function hideResults() {
        const overlay = document.querySelector('div[style*="position: fixed"][style*="rgba(0,0,0,0.5)"]');
        if (overlay) overlay.remove();
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Initialize
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createSearchBox);
    } else {
        createSearchBox();
    }
    
    console.log('[Search] Setup complete');
})();
