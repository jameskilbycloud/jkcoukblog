# Additional Performance Improvement Recommendations

## Overview
This document outlines recommended performance enhancements beyond the current SEO and performance fixes already implemented.

---

## High Priority Recommendations

### 1. Critical CSS Extraction and Inlining

**Current State**: All CSS is loaded as external files, some with media attributes.

**Problem**: First Contentful Paint (FCP) is delayed while browser downloads CSS files.

**Recommendation**: Extract and inline critical "above-the-fold" CSS directly in `<head>`.

**Implementation**:
```python
# scripts/extract_critical_css.py
#!/usr/bin/env python3
"""
Extract critical CSS and inline it in the <head>
Uses Penthouse or similar tool to identify above-the-fold styles
"""

import subprocess
from pathlib import Path
from bs4 import BeautifulSoup

class CriticalCSSExtractor:
    def __init__(self, public_dir='public'):
        self.public_dir = Path(public_dir)

    def extract_critical_css(self, html_file):
        """Extract critical CSS for a page"""
        # Use Penthouse.js or critical package
        # Identify CSS needed for above-the-fold content
        # Return minified critical CSS
        pass

    def inline_critical_css(self, html_file, critical_css):
        """Inline critical CSS in <head>"""
        with open(html_file, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # Create inline style tag
        style_tag = soup.new_tag('style')
        style_tag.string = critical_css

        # Insert at top of head
        soup.head.insert(0, style_tag)

        # Convert external CSS to preload
        for link in soup.find_all('link', rel='stylesheet'):
            if 'critical' not in link.get('href', ''):
                # Preload non-critical CSS
                link['rel'] = 'preload'
                link['as'] = 'style'
                link['onload'] = "this.onload=null;this.rel='stylesheet'"

        with open(html_file, 'w') as f:
            f.write(str(soup))
```

**Workflow Integration**:
```yaml
- name: Extract and inline critical CSS
  run: |
    npm install -g critical
    python3 scripts/extract_critical_css.py ./public
```

**Expected Impact**:
- FCP improvement: 30-50%
- Lighthouse Performance: +5-10 points
- Perceived load time: Much faster

---

### 2. Resource Hints (Preconnect, Prefetch, Preload)

**Current State**: DNS prefetch implemented, but no preconnect/preload.

**Recommendation**: Add strategic resource hints for fonts, analytics, and critical resources.

**Implementation**:
```python
# Add to scripts/enhance_html_performance.py

def add_resource_hints(self, soup):
    """Add preconnect, prefetch, and preload hints"""
    if not soup.head:
        return False

    modified = False

    # Preconnect to external domains (stronger than dns-prefetch)
    critical_domains = {
        'https://plausible.jameskilby.cloud',  # Analytics
        'https://fonts.googleapis.com',         # Google Fonts
        'https://fonts.gstatic.com',            # Font files
    }

    for domain in critical_domains:
        # Check if preconnect already exists
        existing = soup.find('link', rel='preconnect', href=domain)
        if not existing:
            preconnect = soup.new_tag('link')
            preconnect['rel'] = 'preconnect'
            preconnect['href'] = domain
            preconnect['crossorigin'] = ''  # Required for fonts
            soup.head.insert(0, preconnect)
            modified = True

    # Preload critical resources
    critical_resources = []

    # Find hero images (first image in main content)
    main_content = soup.find(['main', 'article'])
    if main_content:
        first_img = main_content.find('img')
        if first_img and first_img.get('src'):
            critical_resources.append({
                'href': first_img['src'],
                'as': 'image',
                'type': self._get_image_type(first_img['src'])
            })

    # Find critical fonts
    for link in soup.find_all('link', rel='stylesheet'):
        href = link.get('href', '')
        if 'fonts.googleapis.com' in href:
            # Extract font URLs and preload
            # This requires parsing the CSS file
            pass

    # Add preload tags
    for resource in critical_resources:
        preload = soup.new_tag('link')
        preload['rel'] = 'preload'
        preload['href'] = resource['href']
        preload['as'] = resource['as']
        if 'type' in resource:
            preload['type'] = resource['type']
        soup.head.insert(0, preload)
        modified = True

    return modified

def _get_image_type(self, src):
    """Get MIME type from image extension"""
    if src.endswith('.avif'):
        return 'image/avif'
    elif src.endswith('.webp'):
        return 'image/webp'
    elif src.endswith('.jpg') or src.endswith('.jpeg'):
        return 'image/jpeg'
    elif src.endswith('.png'):
        return 'image/png'
    return None
```

**Expected Impact**:
- Connection time: -100-300ms per external domain
- LCP improvement: 10-20% (for hero images)
- Lighthouse Performance: +3-5 points

---

### 3. Font Loading Optimization

**Current State**: Fonts likely loading as render-blocking resources.

**Recommendation**: Implement font-display: swap and preload critical fonts.

**Implementation**:
```python
# scripts/optimize_font_loading.py
#!/usr/bin/env python3
"""
Optimize web font loading to prevent FOIT/FOUT
"""

from pathlib import Path
from bs4 import BeautifulSoup
import re

class FontOptimizer:
    def optimize_fonts(self, html_file):
        with open(html_file, 'r') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        modified = False

        # Find Google Fonts links
        for link in soup.find_all('link', href=re.compile(r'fonts\.googleapis\.com')):
            # Add display=swap parameter
            href = link['href']
            if 'display=' not in href:
                separator = '&' if '?' in href else '?'
                link['href'] = f"{href}{separator}display=swap"
                modified = True

        # Add preload for critical fonts
        # Extract font URLs from @font-face declarations
        for style in soup.find_all('style'):
            content = style.string
            if content and '@font-face' in content:
                # Parse font URLs and add preload
                font_urls = re.findall(r'url\((.*?\.woff2)\)', content)
                for font_url in font_urls:
                    font_url = font_url.strip('\'"')
                    # Add preload
                    preload = soup.new_tag('link')
                    preload['rel'] = 'preload'
                    preload['href'] = font_url
                    preload['as'] = 'font'
                    preload['type'] = 'font/woff2'
                    preload['crossorigin'] = ''
                    soup.head.insert(0, preload)
                    modified = True

        if modified:
            with open(html_file, 'w') as f:
                f.write(str(soup))

        return modified
```

**CSS Enhancement**:
```css
/* Add to all @font-face declarations */
@font-face {
  font-family: 'MyFont';
  src: url('/fonts/myfont.woff2') format('woff2');
  font-display: swap; /* Show fallback font immediately */
}
```

**Expected Impact**:
- Eliminates Flash of Invisible Text (FOIT)
- Faster perceived load time
- CLS improvement (if fallback font is similar)

---

### 4. Image Optimization Enhancements

**Current State**: Images converted to AVIF/WebP, but could be further optimized.

**Recommendations**:

#### A. Responsive Image Sizes
```python
# scripts/generate_responsive_images.py
"""
Generate multiple image sizes for srcset
"""

from PIL import Image
from pathlib import Path

def generate_responsive_sizes(image_path, sizes=[320, 640, 1024, 1920]):
    """Generate multiple image sizes"""
    img = Image.open(image_path)
    base_path = image_path.stem

    for size in sizes:
        if img.width > size:
            # Calculate proportional height
            ratio = size / img.width
            new_height = int(img.height * ratio)

            # Resize image
            resized = img.resize((size, new_height), Image.LANCZOS)

            # Save with size suffix
            output_path = image_path.parent / f"{base_path}-{size}w{image_path.suffix}"
            resized.save(output_path, optimize=True, quality=85)
```

#### B. Modern Image Formats with Better Fallbacks
```html
<picture>
  <source
    type="image/avif"
    srcset="
      /images/hero-320w.avif 320w,
      /images/hero-640w.avif 640w,
      /images/hero-1024w.avif 1024w,
      /images/hero-1920w.avif 1920w
    "
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 80vw, 1200px"
  />
  <source
    type="image/webp"
    srcset="
      /images/hero-320w.webp 320w,
      /images/hero-640w.webp 640w,
      /images/hero-1024w.webp 1024w,
      /images/hero-1920w.webp 1920w
    "
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 80vw, 1200px"
  />
  <img
    src="/images/hero-1024w.jpg"
    srcset="
      /images/hero-320w.jpg 320w,
      /images/hero-640w.jpg 640w,
      /images/hero-1024w.jpg 1024w,
      /images/hero-1920w.jpg 1920w
    "
    sizes="(max-width: 640px) 100vw, (max-width: 1024px) 80vw, 1200px"
    alt="Hero image"
    loading="lazy"
    width="1200"
    height="800"
  />
</picture>
```

#### C. Native Lazy Loading with Intersection Observer Fallback
```javascript
// For browsers that don't support native lazy loading
if ('loading' in HTMLImageElement.prototype) {
  // Native lazy loading supported
  const images = document.querySelectorAll('img[loading="lazy"]');
  images.forEach(img => {
    img.src = img.dataset.src;
  });
} else {
  // Fallback to Intersection Observer
  const imageObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target;
        img.src = img.dataset.src;
        img.classList.remove('lazy');
        observer.unobserve(img);
      }
    });
  });

  const images = document.querySelectorAll('img[loading="lazy"]');
  images.forEach(img => imageObserver.observe(img));
}
```

**Expected Impact**:
- Bandwidth savings: 40-60% (right-sized images)
- Mobile LCP: -30-50%
- Data usage: Significantly reduced

---

### 5. JavaScript Optimization

**Current State**: Scripts have async/defer, but could be further optimized.

**Recommendations**:

#### A. Code Splitting
```javascript
// Instead of one large bundle, split by route/feature
// main.js (critical)
import { initNavigation } from './navigation.js';
initNavigation();

// Non-critical features loaded dynamically
if (document.querySelector('.search-form')) {
  import('./search.js').then(module => module.initSearch());
}

if (document.querySelector('.comments')) {
  import('./comments.js').then(module => module.initComments());
}
```

#### B. Remove Unused JavaScript
```bash
# Use terser to remove dead code
npm install -g terser
terser input.js -o output.js --compress --mangle
```

#### C. Defer Third-Party Scripts
```html
<!-- Load analytics after page is interactive -->
<script>
  window.addEventListener('load', function() {
    setTimeout(function() {
      // Load analytics script
      var script = document.createElement('script');
      script.src = 'https://plausible.jameskilby.cloud/js/script.js';
      script.async = true;
      document.head.appendChild(script);
    }, 2000); // Delay 2 seconds after load
  });
</script>
```

**Expected Impact**:
- TBT (Total Blocking Time): -40-60%
- TTI (Time to Interactive): -20-30%
- Lighthouse Performance: +5-10 points

---

### 6. Service Worker for Offline Support & Caching

**Current State**: No service worker implementation.

**Recommendation**: Implement service worker for aggressive caching and offline support.

**Implementation**:
```javascript
// public/sw.js
const CACHE_VERSION = 'v1';
const CACHE_NAME = `jameskilby-${CACHE_VERSION}`;

const STATIC_CACHE = [
  '/',
  '/offline.html',
  '/assets/css/main.css',
  '/assets/js/main.js',
  // Add critical resources
];

// Install event - cache static resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      return cache.addAll(STATIC_CACHE);
    })
  );
  self.skipWaiting();
});

// Activate event - clean old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames
          .filter(name => name !== CACHE_NAME)
          .map(name => caches.delete(name))
      );
    })
  );
  self.clients.claim();
});

// Fetch event - stale-while-revalidate strategy
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(cachedResponse => {
      const fetchPromise = fetch(event.request).then(networkResponse => {
        // Update cache with fresh response
        if (networkResponse.ok) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then(cache => {
            cache.put(event.request, responseClone);
          });
        }
        return networkResponse;
      });

      // Return cached response immediately, fetch in background
      return cachedResponse || fetchPromise;
    }).catch(() => {
      // Offline fallback
      if (event.request.mode === 'navigate') {
        return caches.match('/offline.html');
      }
    })
  );
});
```

```html
<!-- Register service worker in main layout -->
<script>
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/sw.js')
        .then(reg => console.log('SW registered'))
        .catch(err => console.log('SW registration failed'));
    });
  }
</script>
```

**Expected Impact**:
- Repeat visits: 80-90% faster (served from cache)
- Offline functionality: Full site browsing
- Network resilience: Graceful fallbacks

---

### 7. HTTP/3 and Early Hints

**Current State**: Cloudflare Pages supports HTTP/3 but Early Hints may not be configured.

**Recommendation**: Enable HTTP/3 and configure Early Hints for critical resources.

**Cloudflare Configuration**:
```javascript
// In _worker.js, add Early Hints header
export default {
  async fetch(request, env, ctx) {
    // Send Early Hints for critical resources
    const earlyHints = new Response(null, {
      status: 103,
      headers: {
        'Link': [
          '</assets/css/critical.css>; rel=preload; as=style',
          '</assets/fonts/main.woff2>; rel=preload; as=font; crossorigin',
          '//plausible.jameskilby.cloud; rel=preconnect',
        ].join(', ')
      }
    });

    // Note: Cloudflare Workers don't directly support 103 yet,
    // but this shows the concept

    // Continue with normal response
    return env.ASSETS.fetch(request);
  }
}
```

**Expected Impact**:
- TTFB (Time to First Byte): -50-100ms
- Connection establishment: Parallel with HTML download
- Overall load time: -5-10%

---

### 8. CSS Optimization

**Current State**: CSS loaded as external files with some media attributes.

**Recommendations**:

#### A. Minify and Purge Unused CSS
```bash
# Use PurgeCSS to remove unused styles
npm install -g purgecss
purgecss --css public/assets/css/*.css \
         --content public/**/*.html \
         --output public/assets/css/
```

#### B. Modern CSS Features (CSS Containment)
```css
/* Add containment hints to improve rendering performance */
.blog-post {
  contain: layout style;
}

.sidebar {
  contain: layout style paint;
}

.article-list {
  contain: layout;
}

/* Use will-change for animated elements */
.menu-toggle {
  will-change: transform;
}

/* But remove will-change after animation */
.menu-toggle.animating {
  will-change: transform;
}
```

#### C. CSS Grid over Floats/Flexbox (where appropriate)
```css
/* More performant layout with CSS Grid */
.blog-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 2rem;
}

@media (max-width: 768px) {
  .blog-layout {
    grid-template-columns: 1fr;
  }
}
```

**Expected Impact**:
- CSS file size: -30-50%
- Render time: -10-20%
- Lighthouse Performance: +2-5 points

---

### 9. Reduce Third-Party Impact

**Current State**: Plausible analytics loaded on every page.

**Recommendations**:

#### A. Self-Host Analytics
```bash
# Instead of loading from plausible.jameskilby.cloud
# Host the script file directly on your domain
curl -o public/assets/js/plausible.js \
  https://plausible.jameskilby.cloud/js/script.js

# Update HTML to use local version
<script src="/assets/js/plausible.js" defer></script>
<script>window.plausible = window.plausible || function() { (window.plausible.q = window.plausible.q || []).push(arguments) }</script>
```

#### B. Conditionally Load Analytics
```javascript
// Only load analytics for real users, not bots
if (!navigator.userAgent.match(/bot|crawler|spider/i)) {
  // Load analytics
}

// Don't track same user multiple times in session
if (!sessionStorage.getItem('tracked')) {
  // Load analytics
  sessionStorage.setItem('tracked', '1');
}
```

**Expected Impact**:
- Third-party impact: -100%
- DNS lookups: -1
- HTTP requests: -1
- Load time: -50-100ms

---

### 10. Advanced Image Techniques

#### A. Blur-Up Placeholder (LQIP - Low Quality Image Placeholder)
```python
# Generate tiny placeholder images
from PIL import Image, ImageFilter

def generate_placeholder(image_path, size=20):
    """Generate tiny blurred placeholder"""
    img = Image.open(image_path)

    # Resize to tiny size
    img.thumbnail((size, size), Image.LANCZOS)

    # Apply blur
    img = img.filter(ImageFilter.GaussianBlur(2))

    # Convert to base64 for inline embedding
    import base64
    import io
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG", quality=50)
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return f"data:image/jpeg;base64,{img_str}"
```

```html
<!-- Use placeholder while loading -->
<img
  src="data:image/jpeg;base64,/9j/4AAQ..."
  data-src="/images/hero.jpg"
  alt="Hero"
  loading="lazy"
  style="background-size: cover; background-image: url('data:image/jpeg;base64,/9j/4AAQ...')"
  onload="this.style.backgroundImage='none'"
/>
```

#### B. Progressive JPEG
```bash
# Convert images to progressive JPEG
convert input.jpg -interlace Plane output.jpg
```

**Expected Impact**:
- Perceived load time: Much faster
- CLS: Reduced (placeholder prevents layout shift)
- User experience: Smoother

---

## Medium Priority Recommendations

### 11. Database Query Optimization (WordPress Side)

**Recommendation**: Optimize WordPress queries before static generation.

```php
// In WordPress theme functions.php

// Reduce number of queries
add_filter('wp_get_nav_menu_items', 'cache_nav_menu', 10, 3);
function cache_nav_menu($items, $menu, $args) {
    $cache_key = 'nav_menu_' . $menu->term_id;
    $cached = wp_cache_get($cache_key);

    if ($cached === false) {
        wp_cache_set($cache_key, $items, '', 3600);
    }

    return $items;
}

// Disable unnecessary features during export
add_filter('wp_revisions_to_keep', '__return_false');
remove_action('wp_head', 'wp_generator');
remove_action('wp_head', 'wlwmanifest_link');
remove_action('wp_head', 'rsd_link');
```

---

### 12. Implement Compression for JSON/XML Files

**Current State**: Brotli compression for HTML, but JSON/XML might not be compressed.

```yaml
# Add to workflow
- name: Compress JSON and XML files
  run: |
    find ./public -name "*.json" -exec brotli -f -k -q 11 {} \;
    find ./public -name "*.xml" -exec brotli -f -k -q 11 {} \;
```

---

### 13. Optimize Cloudflare Page Rules

**Recommendation**: Configure optimal cache settings in Cloudflare.

```
Cloudflare Page Rules:
1. *jameskilby.co.uk/*.jpg
   - Cache Level: Cache Everything
   - Edge Cache TTL: 1 month

2. *jameskilby.co.uk/*.css
   - Cache Level: Cache Everything
   - Edge Cache TTL: 1 week

3. *jameskilby.co.uk/*.js
   - Cache Level: Cache Everything
   - Edge Cache TTL: 1 week

4. *jameskilby.co.uk/
   - Cache Level: Cache Everything
   - Edge Cache TTL: 4 hours
   - Browser Cache TTL: 2 hours
```

---

## Implementation Priority

### Phase 1 (Immediate - High ROI)
1. ✅ Script async/defer (DONE)
2. ✅ DNS prefetch (DONE)
3. Resource hints (preconnect/preload) - **NEW**
4. Font optimization - **NEW**
5. Remove unused CSS - **NEW**

### Phase 2 (Short-term - 1-2 weeks)
6. Critical CSS extraction - **NEW**
7. Responsive images with srcset - **NEW**
8. Service worker implementation - **NEW**
9. JavaScript code splitting - **NEW**

### Phase 3 (Medium-term - 1 month)
10. Self-host third-party scripts - **NEW**
11. Blur-up image placeholders - **NEW**
12. Advanced caching strategies - **NEW**

---

## Expected Cumulative Impact

### Current State (After Initial Fixes)
```
Lighthouse Scores:
├─ Performance: 85-90
├─ SEO: 95-100
├─ Accessibility: 95-100
└─ Best Practices: 95-100

Core Web Vitals:
├─ FCP: 1.2s
├─ LCP: 2.1s
├─ TBT: 120ms
└─ CLS: 0.05
```

### After Phase 1 Improvements
```
Lighthouse Scores:
├─ Performance: 90-95 (+5 points)
├─ SEO: 95-100
├─ Accessibility: 95-100
└─ Best Practices: 95-100

Core Web Vitals:
├─ FCP: 0.9s (-25%)
├─ LCP: 1.7s (-19%)
├─ TBT: 80ms (-33%)
└─ CLS: 0.03 (-40%)
```

### After All Phases Complete
```
Lighthouse Scores:
├─ Performance: 95-100 (+10-15 points from baseline)
├─ SEO: 95-100
├─ Accessibility: 95-100
└─ Best Practices: 100

Core Web Vitals:
├─ FCP: 0.6s (-50%)
├─ LCP: 1.2s (-43%)
├─ TBT: 40ms (-67%)
└─ CLS: 0.02 (-60%)

Page Load Time:
├─ Fast 3G: 3.0s (-63% from original)
├─ Regular 4G: 1.2s (-61%)
└─ Cable/Fiber: 0.4s (-67%)
```

---

## Monitoring and Measurement

### Tools to Use
1. **Lighthouse CI** - Automated performance testing in GitHub Actions
2. **WebPageTest** - Detailed waterfall analysis
3. **Chrome DevTools** - Performance profiling
4. **Google Search Console** - Real-world Core Web Vitals
5. **Cloudflare Analytics** - CDN performance metrics

### Metrics to Track
- Lighthouse scores (all categories)
- Core Web Vitals (FCP, LCP, TBT, CLS)
- Page load time (3G, 4G, Cable)
- Total page size
- Number of requests
- Time to Interactive (TTI)
- First Input Delay (FID)

---

## Conclusion

These recommendations build on the already-implemented SEO and performance fixes to achieve **world-class performance scores**. Prioritize Phase 1 improvements for quick wins, then gradually implement Phase 2 and 3 for maximum optimization.

The key principle: **Measure, optimize, measure again.** Every change should be validated with real metrics.
