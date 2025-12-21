// DIRECT TEST - Create search box with absolutely minimal code
console.log('[Search] START');

// Create search box immediately
const searchHTML = '<div id="blog-search-container" style="background: #f8f9fa; padding: 16px; border-bottom: 2px solid #e9ecef;"><div style="max-width: 600px; margin: 0 auto;"><input type="text" id="blog-search-input" placeholder="🔍 Search..." style="width: 100%; padding: 12px 16px; border: 2px solid #dee2e6; border-radius: 8px; box-sizing: border-box;"></div></div>';

// Try multiple ways to insert
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('[Search] DOMContentLoaded');
        const main = document.querySelector('main');
        if (main) {
            main.insertAdjacentHTML('afterbegin', searchHTML);
            console.log('[Search] Inserted into main');
        }
    });
} else {
    console.log('[Search] DOM already loaded');
    const main = document.querySelector('main');
    if (main) {
        main.insertAdjacentHTML('afterbegin', searchHTML);
        console.log('[Search] Inserted into main');
    } else {
        document.body.insertAdjacentHTML('afterbegin', searchHTML);
        console.log('[Search] Inserted into body');
    }
}

console.log('[Search] END');
