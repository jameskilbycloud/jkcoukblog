// Blog Search - Beautiful UI Version
console.log('[Search] Script loaded');

(function() {
    'use strict';
    
    if (window.searchInitialized) {
        console.log('[Search] Already initialized');
        return;
    }
    window.searchInitialized = true;
    
    let searchIndex = null;
    let fuse = null;
    
    function createSearchBox() {
        if (document.getElementById('blog-search-container')) {
            return;
        }
        
        const searchHTML = `
            <div id="blog-search-container" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 24px 16px; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(102, 126, 234, 0.15);">
                <div style="max-width: 600px; margin: 0 auto;">
                    <div style="position: relative;">
                        <input type="text" 
                               id="blog-search-input" 
                               placeholder="🔍 Search 160+ posts..." 
                               style="width: 100%; padding: 14px 40px 14px 16px; font-size: 16px; border: none; border-radius: 8px; outline: none; box-sizing: border-box; box-shadow: 0 4px 12px rgba(0,0,0,0.1); transition: all 0.3s ease; font-family: inherit;">
                        <span style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: #999; pointer-events: none;">⌘K</span>
                    </div>
                    <div style="color: rgba(255,255,255,0.8); font-size: 13px; margin-top: 8px; text-align: center;">Press <kbd style="background: rgba(255,255,255,0.2); padding: 2px 6px; border-radius: 3px; font-size: 12px;">Ctrl+K</kbd> to search</div>
                </div>
            </div>
        `;
        
        const main = document.querySelector('main');
        if (main) {
            main.insertAdjacentHTML('afterbegin', searchHTML);
            attachSearchListener();
            attachKeyboardShortcut();
        }
    }
    
    function attachSearchListener() {
        const input = document.getElementById('blog-search-input');
        if (input) {
            input.addEventListener('input', debounce(handleSearch, 300));
            input.addEventListener('focus', function() {
                this.style.boxShadow = '0 4px 20px rgba(102, 126, 234, 0.3), 0 0 0 3px rgba(102, 126, 234, 0.1)';
            });
            input.addEventListener('blur', function() {
                this.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
            });
        }
    }
    
    function attachKeyboardShortcut() {
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                document.getElementById('blog-search-input')?.focus();
            }
        });
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
        
        if (query.length < 2) {
            hideResults();
            return;
        }
        
        if (!searchIndex) {
            loadIndex(() => search(query));
        } else if (fuse) {
            search(query);
        }
    }
    
    function loadIndex(callback) {
        fetch('/search-index.min.json')
            .then(r => r.json())
            .then(data => {
                searchIndex = data;
                loadFuse(callback);
            })
            .catch(e => console.error('[Search] Failed to load index:', e));
    }
    
    function loadFuse(callback) {
        const script = document.createElement('script');
        script.src = 'https://cdn.jsdelivr.net/npm/fuse.js@7.0.0';
        script.onload = () => {
            fuse = new window.Fuse(searchIndex, {
                keys: ['title', 'description', 'content'],
                threshold: 0.4
            });
            if (callback) callback();
        };
        document.head.appendChild(script);
    }
    
    function search(query) {
        if (!fuse) return;
        
        const results = fuse.search(query);
        displayResults(results, query);
    }
    
    function displayResults(results, query) {
        hideResults();
        
        let html = `<div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.6); z-index: 99999; display: flex; align-items: flex-start; justify-content: center; padding: 40px 20px; overflow-y: auto; animation: fadeIn 0.2s ease;" onclick="if(event.target===this) this.remove()">
            <div style="background: white; border-radius: 12px; max-width: 650px; width: 100%; max-height: 75vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3); animation: slideUp 0.3s ease;">
                <div style="padding: 24px; border-bottom: 1px solid #e5e7eb; background: linear-gradient(135deg, #f5f7fa 0%, #f9fafb 100%); position: sticky; top: 0; z-index: 10;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-size: 14px; color: #667eea; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px;">Search Results</div>
                            <div style="font-size: 18px; font-weight: 700; color: #111;">` + results.length + ` result` + (results.length !== 1 ? 's' : '') + ` for "<span style="color: #667eea;">` + escapeHtml(query) + `</span>"</div>
                        </div>
                        <button onclick="this.closest('[style*=\"position: fixed\"]').remove()" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #999; padding: 0; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; border-radius: 6px; transition: all 0.2s;" onmouseover="this.style.background='#f0f0f0'; this.style.color='#111'" onmouseout="this.style.background='none'; this.style.color='#999'">×</button>
                    </div>
                </div>
                <div style="overflow-y: auto; max-height: calc(75vh - 120px);">`;
        
        if (results.length === 0) {
            html += `<div style="padding: 60px 40px; text-align: center;">
                <div style="font-size: 48px; margin-bottom: 16px;">🔍</div>
                <div style="font-size: 18px; font-weight: 600; color: #111; margin-bottom: 8px;">No results found</div>
                <div style="color: #666; font-size: 14px;">Try searching for different keywords</div>
            </div>`;
        } else {
            results.slice(0, 10).forEach((r, idx) => {
                const item = r.item;
                html += `<a href="` + item.url + `" style="display: block; padding: 20px 24px; border-bottom: 1px solid #f0f0f0; text-decoration: none; color: inherit; transition: all 0.15s;" onmouseover="this.style.background='#f9fafb'; this.style.paddingLeft='28px'" onmouseout="this.style.background='white'; this.style.paddingLeft='24px'">
                    <div style="display: flex; align-items: flex-start; gap: 12px;">
                        <div style="flex-shrink: 0; width: 24px; height: 24px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 6px; display: flex; align-items: center; justify-content: center; color: white; font-size: 12px; font-weight: 600; margin-top: 2px;">` + (idx + 1) + `</div>
                        <div style="flex: 1; min-width: 0;">
                            <div style="font-size: 15px; font-weight: 600; color: #111; margin-bottom: 6px; line-height: 1.4;">` + escapeHtml(item.title) + `</div>
                            <div style="font-size: 13px; color: #666; margin-bottom: 8px; line-height: 1.5; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">` + escapeHtml((item.description || '').substring(0, 120)) + `</div>
                            <div style="font-size: 12px; color: #999;">` + item.url.replace('https://jameskilby.co.uk', '') + `</div>
                        </div>
                    </div>
                </a>`;
            });
        }
        
        html += `</div>
            </div>
            <style>
                @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
                @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
            </style>
        </div>`;
        
        const div = document.createElement('div');
        div.innerHTML = html;
        document.body.appendChild(div.firstChild);
    }
    
    function hideResults() {
        const overlay = document.querySelector('div[style*="position: fixed"][style*="rgba(0,0,0,0.6)"]');
        if (overlay) overlay.remove();
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createSearchBox);
    } else {
        createSearchBox();
    }
})();
