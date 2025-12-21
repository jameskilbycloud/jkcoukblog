// Blog Search with Fuse.js
(function() {
    'use strict';
    
    console.log('[Search] Loading...');
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    function init() {
        console.log('[Search] Initializing...');
        
        // Add search box immediately
        createSearchBox();
        
        // Load Fuse.js
        loadFuse();
    }
    
    function createSearchBox() {
        console.log('[Search] Creating search box...');
        
        // Create search container
        const container = document.createElement('div');
        container.id = 'blog-search-container';
        container.style.cssText = 'background: #f8f9fa; padding: 16px; border-bottom: 2px solid #e9ecef; margin-bottom: 20px;';
        
        container.innerHTML = `
            <div style="max-width: 600px; margin: 0 auto;">
                <input type="text" 
                       id="blog-search-input" 
                       placeholder="🔍 Search posts..." 
                       style="width: 100%; padding: 12px 16px; font-size: 16px; border: 2px solid #dee2e6; border-radius: 8px; outline: none; transition: border-color 0.3s;"
                       onfocus="this.style.borderColor='#0d6efd'"
                       onblur="this.style.borderColor='#dee2e6'">
            </div>
        `;
        
        // Insert at top of main content
        const main = document.querySelector('main') || document.querySelector('#primary') || document.body;
        main.insertBefore(container, main.firstChild);
        
        console.log('[Search] Search box created');
    }
    
    function loadFuse() {
        console.log('[Search] Loading Fuse.js...');
        
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/fuse.js@7.0.0'\;
        script.onload = function() {
            console.log('[Search] Fuse.js loaded');
            loadSearchIndex();
        };
        script.onerror = function() {
            console.error('[Search] Failed to load Fuse.js');
        };
        document.head.appendChild(script);
    }
    
    function loadSearchIndex() {
        console.log('[Search] Loading search index...');
        
        fetch('/search-index.min.json')
            .then(res => res.json())
            .then(data => {
                console.log(`[Search] Loaded ${data.length} posts`);
                initSearch(data);
            })
            .catch(err => {
                console.error('[Search] Failed to load index:', err);
            });
    }
    
    function initSearch(searchData) {
        const fuse = new Fuse(searchData, {
            keys: ['title', 'description', 'content', 'categories', 'tags'],
            threshold: 0.4,
            minMatchCharLength: 2
        });
        
        const input = document.getElementById('blog-search-input');
        const resultsContainer = createResultsContainer();
        
        input.addEventListener('input', function(e) {
            const query = e.target.value.trim();
            
            if (query.length < 2) {
                resultsContainer.style.display = 'none';
                return;
            }
            
            const results = fuse.search(query);
            displayResults(results, resultsContainer, query);
        });
        
        console.log('[Search] Fully initialized');
    }
    
    function createResultsContainer() {
        const overlay = document.createElement('div');
        overlay.id = 'search-results-overlay';
        overlay.style.cssText = 'position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0,0,0,0.5); z-index: 9999; display: none; padding: 80px 20px; overflow-y: auto;';
        
        const container = document.createElement('div');
        container.style.cssText = 'max-width: 700px; margin: 0 auto; background: white; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.2); max-height: 80vh; overflow-y: auto;';
        
        overlay.appendChild(container);
        document.body.appendChild(overlay);
        
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                overlay.style.display = 'none';
            }
        });
        
        return overlay;
    }
    
    function displayResults(results, container, query) {
        const resultsBox = container.querySelector('div');
        
        if (results.length === 0) {
            resultsBox.innerHTML = `<div style="padding: 40px; text-align: center; color: #6c757d;">No results found for "${escapeHtml(query)}"</div>`;
        } else {
            let html = `<div style="padding: 20px; border-bottom: 1px solid #e9ecef; background: #f8f9fa;">
                <strong>${results.length} result${results.length > 1 ? 's' : ''} for "${escapeHtml(query)}"</strong>
            </div>`;
            
            results.slice(0, 10).forEach(result => {
                const item = result.item;
                html += `
                    <a href="${item.url}" style="display: block; padding: 20px; border-bottom: 1px solid #e9ecef; text-decoration: none; color: inherit; transition: background 0.2s;"
                       onmouseover="this.style.background='#f8f9fa'" 
                       onmouseout="this.style.background='white'">
                        <h3 style="margin: 0 0 8px 0; color: #0d6efd; font-size: 18px;">${escapeHtml(item.title)}</h3>
                        <p style="margin: 0; color: #6c757d; font-size: 14px; line-height: 1.5;">${escapeHtml(item.description || 'No description')}</p>
                    </a>
                `;
            });
            
            resultsBox.innerHTML = html;
        }
        
        container.style.display = 'block';
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
})();
