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
        // The box is pre-rendered into <main> at build time
        // (wp_to_static_generator._inject_search_box) so it occupies its 82px
        // from first paint. Injecting it here instead pushed every page's
        // content down ~2s after load, which is what took the origin's p75
        // CLS from 0.05 to 0.22. When the markup is already there, skip
        // building it but still wire up the behaviour.
        if (document.getElementById('blog-search-container')) {
            attachSearchListener();
            attachKeyboardShortcut();
            return;
        }

        const searchHTML = `
            <div id="blog-search-container" style="padding: 16px; margin-bottom: 20px;">
                <div style="max-width: 600px; margin: 0 auto;">
                    <div style="position: relative;">
                        <input type="text"
                               id="blog-search-input"
                               placeholder="Search posts…"
                               style="width: 100%; padding: 12px 48px 12px 16px; font-size: 15px; border: 1px solid #262625; border-radius: 0; outline: none; box-sizing: border-box; background: #111110; color: #f5f3ee; transition: border-color 0.2s ease, box-shadow 0.2s ease; font-family: inherit;">
                        <span style="position: absolute; right: 12px; top: 50%; transform: translateY(-50%); color: #7a766c; pointer-events: none; font-size: 12px; font-family: 'JetBrains Mono', monospace;">⌘K</span>
                    </div>
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
                this.style.borderColor = '#f6821f';
                this.style.background = '#161513';
                this.style.boxShadow = '0 0 0 3px rgba(246, 130, 31, 0.15)';
            });
            input.addEventListener('blur', function() {
                this.style.borderColor = '#262625';
                this.style.background = '#111110';
                this.style.boxShadow = 'none';
            });
        }
    }
    
    function attachKeyboardShortcut() {
        document.addEventListener('keydown', function(e) {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                focusSearch();
            }
            if (e.key === 'Escape') {
                hideResults();
            }
        });
    }

    function focusSearch() {
        const input = document.getElementById('blog-search-input');
        if (input) {
            // CSS prefers-reduced-motion can't override an explicit JS
            // behavior option — gate it here.
            const reduceMotion = window.matchMedia
                && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
            input.scrollIntoView({ behavior: reduceMotion ? 'auto' : 'smooth', block: 'center' });
            input.focus();
        }
    }

    // The header search button (.jk-search) is static HTML; the search box is
    // injected into <main> on load. Delegate so the click works regardless of
    // order, and so it survives the button being re-rendered.
    function attachHeaderSearchButton() {
        document.addEventListener('click', function(e) {
            const btn = e.target.closest && e.target.closest('.jk-search');
            if (!btn) return;
            e.preventDefault();
            focusSearch();
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
        script.src = '/js/fuse.min.js';
        script.onload = () => {
            fuse = new window.Fuse(searchIndex, {
                keys: ['title', 'description', 'content'],
                threshold: 0.4,
                includeMatches: true,
                ignoreLocation: true,
                minMatchCharLength: 2
            });
            if (callback) callback();
        };
        script.onerror = () => console.error('[Search] Failed to load /js/fuse.min.js');
        document.head.appendChild(script);
    }
    
    function search(query) {
        if (!fuse) return;
        
        const results = fuse.search(query);
        displayResults(results, query);
        
        // Track search analytics (privacy-friendly)
        trackSearch(query, results.length);
    }
    
    function displayResults(results, query) {
        hideResults();
        
        // NOTE: backgrounds use inline !important on purpose. The theme ships a
        // blanket reset — `div, section, aside, nav { background-color:
        // transparent !important }` (brutalist-theme.css) — to neutralise
        // WordPress block backgrounds. Because this overlay is built from divs,
        // a plain inline background loses to that !important and the whole modal
        // renders see-through over the page. An inline !important is the one
        // author declaration that beats a stylesheet !important, so every div
        // surface below (overlay, panel, header, result number badge) needs it.
        let html = `<div class="search-overlay" style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85) !important; z-index: 99999; display: flex; flex-direction: column; align-items: center; justify-content: flex-start; padding: 20px; overflow-y: auto; animation: fadeIn 0.2s ease;" onclick="if(event.target===this) this.remove()">
            <div style="background: #171613 !important; border: 1px solid #33322e; border-radius: 0; max-width: 650px; width: 100%; max-height: 90vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.7); animation: slideUp 0.3s ease; margin-top: 20px;">
                <div style="padding: 20px; border-bottom: 1px solid #33322e; background: #1c1b17 !important; position: sticky; top: 0; z-index: 10;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 12px;">
                        <div style="flex: 1;">
                            <div style="font-size: 13px; color: #f6821f; font-weight: 600; text-transform: uppercase; letter-spacing: 0.12em; margin-bottom: 4px; font-family: 'JetBrains Mono', monospace;">Search Results</div>
                            <div style="font-size: 16px; font-weight: 700; color: #f5f3ee; word-break: break-word;">` + results.length + ` result` + (results.length !== 1 ? 's' : '') + `</div>
                        </div>
                        <button onclick="this.closest('.search-overlay').remove()" style="background: transparent; border: 1px solid #262625; font-size: 20px; cursor: pointer; color: #c8c5bd; padding: 0; width: 36px; height: 36px; display: flex; align-items: center; justify-content: center; border-radius: 0; transition: all 0.2s; flex-shrink: 0;" onmouseover="this.style.borderColor='#f6821f';this.style.color='#f6821f'" onmouseout="this.style.borderColor='#262625';this.style.color='#c8c5bd'">×</button>
                    </div>
                </div>
                <div style="overflow-y: auto; max-height: calc(75vh - 120px);">`;

        if (results.length === 0) {
            html += `<div style="padding: 60px 40px; text-align: center;">
                <div style="font-size: 18px; font-weight: 600; color: #f5f3ee; margin-bottom: 8px;">No results found</div>
                <div style="color: #7a766c; font-size: 14px;">Try searching for different keywords</div>
            </div>`;
        } else {
            results.slice(0, 10).forEach((r, idx) => {
                const item = r.item;
                const highlightedTitle = highlightSearchTerms(item.title, query);
                const highlightedDesc = highlightSearchTerms((item.description || '').substring(0, 150), query);
                const safeUrl = /^https?:\/\//.test(item.url) ? item.url : '#';

                html += `<a href="` + safeUrl + `" style="display: block; padding: 16px; border-bottom: 1px solid #2a2925; text-decoration: none; color: inherit; transition: background-color 0.15s;" onmouseover="this.style.background='#232019'" onmouseout="this.style.background='transparent'">
                    <div style="display: flex; align-items: flex-start; gap: 10px;">
                        <div style="flex-shrink: 0; width: 28px; height: 28px; background: #f6821f !important; border-radius: 0; display: flex; align-items: center; justify-content: center; color: #0a0a0a; font-size: 12px; font-weight: 700; font-family: 'JetBrains Mono', monospace;">` + (idx + 1) + `</div>
                        <div style="flex: 1; min-width: 0;">
                            <div style="font-size: 14px; font-weight: 600; color: #f5f3ee; margin-bottom: 4px; line-height: 1.3;">` + highlightedTitle + `</div>
                            <div style="font-size: 12px; color: #a8a59c; margin-bottom: 6px; line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;">` + highlightedDesc + `</div>
                            <div style="font-size: 11px; color: #7a766c; word-break: break-all; font-family: 'JetBrains Mono', monospace;">` + item.url.replace('https://jameskilby.co.uk', '') + `</div>
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
        const overlay = document.querySelector('.search-overlay');
        if (overlay) overlay.remove();
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Highlight search terms in text
    function highlightSearchTerms(text, query) {
        if (!query || !text) return escapeHtml(text);
        
        const escapedText = escapeHtml(text);
        const terms = query.toLowerCase().split(/\s+/).filter(t => t.length > 1);
        
        let highlighted = escapedText;
        terms.forEach(term => {
            const regex = new RegExp(`(${term})`, 'gi');
            highlighted = highlighted.replace(regex, '<mark style="background-color: #f6821f; color: #0a0a0a; padding: 1px 3px; border-radius: 0; font-weight: 600;">$1</mark>');
        });
        
        return highlighted;
    }
    
    // Privacy-friendly search analytics
    function trackSearch(query, resultCount) {
        // Send to Plausible as custom event (respects DNT and privacy)
        if (window.plausible) {
            window.plausible('Search', {
                props: {
                    query_length: query.length,
                    result_count: resultCount,
                    has_results: resultCount > 0 ? 'yes' : 'no'
                }
            });
        }
    }
    
    // Header search button works independently of the (main-injected) box.
    attachHeaderSearchButton();

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', createSearchBox);
    } else {
        createSearchBox();
    }
})();
