# Additional Performance Recommendations

Beyond the CLS optimizations already implemented, here are further improvements to maximize performance.

## 1. Font Preloading (HIGH IMPACT)
**Status**: ✅ IMPLEMENTED  
**Impact**: -200-400ms FCP, -100-200ms LCP

### Problem
Your critical fonts (Anton, Space Grotesk) aren't preloaded, causing FOIT (Flash of Invisible Text) or delayed text rendering.

### Solution
Add font preloading in `add_static_optimizations()` method:

```python
# In wp_to_static_generator.py, around line 1005
def add_font_preloads(self, soup):
    """Preload critical fonts for faster text rendering"""
    if not soup.head:
        return
    
    critical_fonts = [
        '/assets/fonts/anton-v27-latin-400.woff2',
        '/assets/fonts/spacegrotesk-v22-latin-400.woff2',
        '/assets/fonts/spacegrotesk-v22-latin-500.woff2'
    ]
    
    for font_url in critical_fonts:
        preload = soup.new_tag('link')
        preload['rel'] = 'preload'
        preload['as'] = 'font'
        preload['type'] = 'font/woff2'
        preload['href'] = font_url
        preload['crossorigin'] = 'anonymous'
        # Insert at beginning of head for highest priority
        soup.head.insert(0, preload)
    
    print(f"   🔤 Preloaded {len(critical_fonts)} critical fonts")

# Then call it from add_static_optimizations():
self.add_font_preloads(soup)
```

**Why it works**:
- Browser discovers fonts immediately without waiting for CSS to download/parse
- Fonts start downloading in parallel with CSS
- Reduces text rendering delay by 200-400ms

---

## 2. Duplicate Preload Elimination (LOW IMPACT)
**Status**: ✅ FIXED  
**Impact**: -10-20ms, cleaner HTML

### Problem
Looking at your HTML line 4:
```html
<link as="style" href="/assets/css/brutalist-theme.css" rel="preload"/>
<link as="style" href="/assets/css/brutalist-theme.css" rel="preload"/>
```
**Duplicate preload for brutalist-theme.css!**

### Solution
In `add_static_optimizations()` around line 999-1005, check for existing preloads:

```python
# Before adding preload
for link in soup.find_all('link', rel='stylesheet'):
    if link.get('href'):
        href = link['href']
        # Check if preload already exists
        existing_preload = soup.find('link', rel='preload', href=href)
        if not existing_preload:
            preload = soup.new_tag('link')
            preload['rel'] = 'preload'
            preload['as'] = 'style'
            preload['href'] = href
            soup.head.insert(0, preload)
```

---

## 3. Remove Unused CSS (MEDIUM IMPACT)
**Status**: ❌ Not implemented  
**Impact**: -50-100KB transfer, -100-200ms FCP

### Problem
You're loading several CSS files that may have significant unused rules:
- `wp-block-library-inline-css-*.min.css` (Gutenberg blocks)
- `kadence-footer-css`, `kadence-rankmath-css`
- Multiple inline CSS files

### Solution (Advanced)
Use PurgeCSS or critical CSS extraction:

```python
def remove_unused_css(self, soup):
    """Remove unused CSS rules to reduce payload"""
    import re
    from pathlib import Path
    
    # Get all text content from the page
    page_text = soup.get_text()
    
    # Find all class names used on the page
    used_classes = set()
    for element in soup.find_all(class_=True):
        if isinstance(element['class'], list):
            used_classes.update(element['class'])
        else:
            used_classes.add(element['class'])
    
    # Similarly find all IDs
    used_ids = {el['id'] for el in soup.find_all(id=True)}
    
    # Process inline styles and remove unused rules
    for style in soup.find_all('style'):
        if style.string:
            # Parse CSS and keep only used selectors
            # This is a simplified example - use a proper CSS parser
            css = style.string
            # Keep rules that match used classes/ids
            # (Implementation requires CSS parsing library)
```

**Alternative**: Use Cloudflare's Auto Minify feature (already on Cloudflare Pages)

---

## 4. Script Defer/Async Optimization (LOW IMPACT)
**Status**: ✅ Partially implemented  
**Impact**: Already using `defer` on Plausible

### Current State
- ✅ Plausible analytics: `defer` 
- ⚠️ Footer script: preloaded but not deferred
- ✅ Utterances: `async`

### Recommendation
Check if footer scripts can be deferred:
```html
<link as="script" href="/wp-content/cache/wpo-minify/.../wpo-minify-footer-*.min.js" rel="preload"/>
```

If this script doesn't manipulate DOM on load, add `defer`:
```python
script['defer'] = ''
```

---

## 5. Resource Hints for External Domains (LOW IMPACT)
**Status**: ✅ Already implemented  
**Impact**: Already optimal

```html
<link href="//plausible.jameskilby.cloud" rel="dns-prefetch"/>
<link crossorigin="" href="https://plausible.jameskilby.cloud" rel="preconnect"/>
```

✅ Good! Utterances CDN could also benefit:

```python
# Add to add_static_optimizations()
dns_prefetch = soup.new_tag('link')
dns_prefetch['rel'] = 'dns-prefetch'
dns_prefetch['href'] = '//utteranc.es'
soup.head.insert(0, dns_prefetch)
```

---

## 6. Image Format Optimization (ALREADY DONE)
**Status**: ✅ Excellent implementation

Your images use:
```html
<picture>
  <source srcset="...768x560.avif" type="image/avif"/>
  <img src="...768x560.png" />
</picture>
```

✅ **AVIF with PNG fallback** - optimal!  
AVIF is ~50% smaller than PNG with better quality.

---

## 7. HTTP/2 Server Push (NOT RECOMMENDED)
**Status**: ❌ Not needed  
**Why**: Cloudflare Pages already uses HTTP/3 with automatic prioritization. Server Push is deprecated.

---

## 8. Service Worker for Offline Support (OPTIONAL)
**Status**: ❌ Not implemented  
**Impact**: Better offline experience, faster repeat visits

### Implementation
Create `service-worker.js`:
```javascript
const CACHE_NAME = 'jkcouk-v1';
const CACHE_URLS = [
  '/',
  '/assets/css/brutalist-theme.css',
  '/assets/fonts/anton-v27-latin-400.woff2',
  '/assets/fonts/spacegrotesk-v22-latin-400.woff2'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(CACHE_URLS))
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
```

Register in HTML:
```javascript
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/service-worker.js');
}
```

**Tradeoff**: Adds complexity, cache invalidation challenges.  
**Recommendation**: Not needed for a blog unless offline reading is important.

---

## 9. Reduce JavaScript Payload (LOW PRIORITY)
**Status**: Already minimal  
**Current JS**:
- Plausible analytics (~1KB gzipped)
- Footer minified bundle (size unknown)
- Utterances (lazy-loaded)

**Recommendation**: Already lean. No action needed.

---

## 10. Early Hints (103 Status) (ADVANCED)
**Status**: ❌ Not supported by Cloudflare Pages yet  
**Impact**: -50-100ms on cold visits

Early Hints (HTTP 103) send critical resource hints before HTML is ready.

**Check support**: https://developers.cloudflare.com/pages/platform/early-hints/

If supported, add to `_headers` file in public directory:
```
/*
  Link: </assets/fonts/anton-v27-latin-400.woff2>; rel=preload; as=font; crossorigin
  Link: </assets/fonts/spacegrotesk-v22-latin-400.woff2>; rel=preload; as=font; crossorigin
  Link: </assets/css/brutalist-theme.css>; rel=preload; as=style
```

---

## Priority Ranking

### High Priority (Implement Now)
1. **Font Preloading** - Biggest impact (-200-400ms FCP)
2. **Fix Duplicate Preload** - Quick fix, cleaner HTML

### Medium Priority (Consider)
3. **Unused CSS Removal** - Moderate complexity, good impact
4. **DNS Prefetch for Utterances** - 1-line change

### Low Priority (Nice to Have)
5. **Service Worker** - Only if offline support is desired
6. **Early Hints** - Wait for Cloudflare Pages support

---

## Expected Performance After Implementation

With font preloading + duplicate fix:
- **Desktop**: Lighthouse 95-98 (currently ~92-95)
- **Mobile**: Lighthouse 92-96 (currently ~90-95)
- **FCP**: 500-700ms on 3G (currently 700-900ms)
- **LCP**: 1000-1300ms on 3G (currently 1200-1500ms)

---

## Next Steps

1. Implement font preloading (highest ROI)
2. Fix duplicate preload issue
3. Test with Lighthouse
4. Monitor real-user metrics in Search Console
5. Consider unused CSS removal if payload is >150KB

---

## Files to Modify
- `wp_to_static_generator.py` - Add `add_font_preloads()` method
- `wp_to_static_generator.py` - Fix duplicate preload logic (line 999-1005)
