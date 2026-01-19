# Intelligent Image Loading Strategy

## Overview

This optimization implements a smart image loading strategy that prioritizes critical above-the-fold images while lazy-loading below-the-fold content, resulting in faster perceived page load times and better Core Web Vitals.

## Problem

The previous approach used a simple counter-based system:
- First 2 images: `loading="eager"`
- All other images: `loading="lazy"`

**Issues:**
- Didn't account for actual image importance
- Hero images might load late if not in first 2 positions
- Featured post thumbnails on archive pages not optimized
- No use of `fetchpriority` for LCP images
- Same strategy for all page types

## Solution

Implemented intelligent image prioritization based on:
1. **Image type** (hero, featured thumbnail, content image)
2. **Position** in DOM (above-fold vs below-fold)
3. **Context** (archive page vs single post)

### Three-Tier Loading Strategy

#### 🚀 Tier 1: High Priority (fetchpriority="high")
```html
<img loading="eager" fetchpriority="high" ... >
```
**Applied to:**
- Hero/banner images
- First featured post image on archive pages
- Masthead images

**Purpose:** Signals browser to prioritize these images for LCP optimization

---

#### ⚡ Tier 2: Eager Loading (normal priority)
```html
<img loading="eager" decoding="async" ... >
```
**Applied to:**
- First 2-3 images on the page (if above-fold)
- Featured post thumbnails in first 3 positions
- Critical content images

**Purpose:** Load immediately but don't compete with highest priority images

---

#### 📦 Tier 3: Lazy Loading (deferred)
```html
<img loading="lazy" decoding="async" ... >
```
**Applied to:**
- All images below position 3
- Non-critical content images
- Footer images
- Social media icons

**Purpose:** Only load when user scrolls near them, saving bandwidth

## Implementation Details

### Detection Algorithms

#### Hero Image Detection
```python
def _is_hero_image(self, img):
    # Checks for:
    # - Class names: 'hero', 'banner', 'featured-image', 'masthead'
    # - Parent elements up to 3 levels with hero patterns
    # Returns: bool
```

#### Featured Post Detection
```python
def _is_featured_post_image(self, img, idx):
    # Checks for:
    # - WordPress classes: 'wp-post-image', 'post-thumbnail'
    # - Parent elements up to 5 levels: 'entry', 'post', 'article'
    # Returns: bool
```

### Loading Logic

```python
for idx, img in enumerate(images):
    is_hero = _is_hero_image(img)
    is_featured = _is_featured_post_image(img, idx)
    is_above_fold = idx < 3
    
    if is_hero or (is_featured and idx == 0):
        # Tier 1: High Priority
        img['loading'] = 'eager'
        img['fetchpriority'] = 'high'
    
    elif is_above_fold and (is_featured or idx < 2):
        # Tier 2: Eager
        img['loading'] = 'eager'
        img['decoding'] = 'async'
    
    else:
        # Tier 3: Lazy
        img['loading'] = 'lazy'
        img['decoding'] = 'async'
```

## Performance Impact

### Before (Simple Strategy)
```
Page Load Timeline:
0ms: Start
100ms: First 2 images start loading (eager)
150ms: Browser discovers image #3
150ms: Image #3 starts loading (lazy - waits for scroll)
// LCP image might be #3, causing delay
```

### After (Intelligent Strategy)
```
Page Load Timeline:
0ms: Start
50ms: Hero image starts loading (HIGH PRIORITY)
100ms: Featured thumbnails #1-2 start loading (eager)
150ms: Browser discovers image #4
150ms: Image #4 waits (lazy)
// LCP image (#1) prioritized, loads faster
```

### Expected Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| LCP | ~2.5s | ~1.8s | **-700ms** |
| FCP | ~1.2s | ~1.0s | **-200ms** |
| TBT | 250ms | 180ms | **-70ms** |
| Images loaded initially | 2 | 2-3 (smart) | Context-aware |
| Bandwidth (initial) | ~150KB | ~100KB | **-33%** |

## Browser Support

### fetchpriority Attribute
- ✅ Chrome/Edge 101+
- ✅ Safari 17.2+ (iOS 17.2+)
- ⚠️ Firefox: Not yet supported (ignored gracefully)

**Fallback:** Browsers without `fetchpriority` support simply ignore it and use `loading="eager"` normally.

### loading Attribute
- ✅ Chrome/Edge 76+
- ✅ Firefox 75+
- ✅ Safari 15.4+ (iOS 15.4+)
- ✅ Samsung Internet 12+

**Fallback:** Older browsers load all images eagerly (no lazy loading).

## Testing

### Verify in Generated HTML

```bash
# Check high priority images
grep -B 2 'fetchpriority="high"' public/index.html

# Count eager vs lazy images
grep -o 'loading="eager"' public/index.html | wc -l
grep -o 'loading="lazy"' public/index.html | wc -l

# View image loading strategy summary
python3 wp_to_static_generator.py ./public 2>&1 | grep "Image loading strategy" -A 4
```

### Chrome DevTools Testing

1. **Network Panel:**
   ```
   - Open DevTools → Network tab → Filter: Img
   - Disable cache, reload page
   - Sort by "Priority" column
   - Verify: First image shows "High" priority
   ```

2. **Performance Panel:**
   ```
   - Record page load
   - Look for LCP marker
   - Verify LCP image loaded with high priority
   ```

3. **Lighthouse Audit:**
   ```
   - Run Lighthouse (mobile)
   - Check "Largest Contentful Paint element"
   - Verify it has fetchpriority="high"
   ```

### Expected Results

**Archive Page (e.g., homepage):**
```
✅ Image loading strategy:
   🚀 High priority: 1 (first featured post)
   ⚡ Eager: 2 (next 2 featured posts)
   📦 Lazy: 12+ (remaining posts)
```

**Single Post Page:**
```
✅ Image loading strategy:
   🚀 High priority: 1 (hero/featured image)
   ⚡ Eager: 1-2 (top content images)
   📦 Lazy: 5+ (body images)
```

## Integration with Existing Optimizations

### Works with Mobile Image Breakpoints
```html
<img loading="eager"
     fetchpriority="high"
     sizes="(max-width: 480px) 95vw, (max-width: 768px) 90vw, 400px"
     srcset="image-300w.avif 300w, image-768w.avif 768w"
     src="image-768w.png">
```

### Works with AVIF/WebP Conversion
```html
<picture>
  <source type="image/avif" srcset="..." sizes="...">
  <source type="image/webp" srcset="..." sizes="...">
  <img loading="eager" fetchpriority="high" ...>
</picture>
```

### Works with Critical CSS
- Critical CSS renders layout immediately
- High priority images fill the rendered layout quickly
- Below-fold lazy images don't block initial render

## Real-World Examples

### Homepage/Archive
```html
<!-- First post (LCP candidate) -->
<article class="entry-list-item">
  <a class="post-thumbnail">
    <img class="wp-post-image" 
         loading="eager" 
         fetchpriority="high"    <!-- HIGH PRIORITY -->
         src="post1.png">
  </a>
</article>

<!-- Second post -->
<article class="entry-list-item">
  <img class="wp-post-image" 
       loading="eager"           <!-- EAGER (above fold) -->
       decoding="async"
       src="post2.png">
</article>

<!-- Third post -->
<article class="entry-list-item">
  <img class="wp-post-image" 
       loading="eager"           <!-- EAGER (above fold) -->
       decoding="async"
       src="post3.png">
</article>

<!-- Fourth+ posts -->
<article class="entry-list-item">
  <img class="wp-post-image" 
       loading="lazy"            <!-- LAZY (below fold) -->
       decoding="async"
       src="post4.png">
</article>
```

### Single Post
```html
<!-- Featured/hero image -->
<div class="featured-image">
  <img loading="eager" 
       fetchpriority="high"      <!-- HIGH PRIORITY -->
       src="hero.png">
</div>

<!-- First content image -->
<article class="entry-content">
  <p><img loading="eager"        <!-- EAGER -->
          decoding="async"
          src="content1.png"></p>
  
  <!-- Later images -->
  <p><img loading="lazy"         <!-- LAZY -->
          decoding="async"
          src="content2.png"></p>
</article>
```

## Monitoring & Optimization

### Key Metrics

1. **LCP (Largest Contentful Paint)**
   - Target: <2.5s on mobile
   - Monitor via PageSpeed Insights
   - Check that LCP element has `fetchpriority="high"`

2. **Initial Bandwidth**
   - Target: <200KB images on initial load
   - Check Network tab: filter by Img, look at transfer size
   - Compare eager vs lazy image counts

3. **Time to Interactive (TTI)**
   - Should improve with fewer initial images loading
   - Monitor via Lighthouse

### Optimization Tips

1. **If LCP is slow:**
   - Verify LCP image has `fetchpriority="high"`
   - Check image file size (should use AVIF)
   - Verify mobile breakpoints are working

2. **If too many eager images:**
   - Review detection logic
   - Adjust `is_above_fold` threshold (currently 3)

3. **If hero image not prioritized:**
   - Add appropriate class names
   - Update `hero_patterns` list in code

## Future Enhancements

1. **Priority Hints API:**
   - Add `importance="high"` for older browsers
   - Broader browser support

2. **Adaptive Loading:**
   - Detect connection speed (NetworkInformation API)
   - Adjust eager count based on bandwidth

3. **Intersection Observer:**
   - Dynamic lazy loading with custom thresholds
   - Progressive loading for image galleries

4. **Machine Learning:**
   - Learn which images are typically LCP
   - Auto-adjust priorities based on analytics

## Related Documentation

- `docs/MOBILE_IMAGE_BREAKPOINTS.md` - Responsive image sizing
- `docs/MOBILE_OPTIMIZATIONS_SUMMARY.md` - Overall mobile performance
- `docs/CRITICAL_MOBILE_CSS.md` - Critical CSS implementation

## References

- [MDN: fetchpriority](https://developer.mozilla.org/en-US/docs/Web/API/HTMLImageElement/fetchPriority)
- [Web.dev: Optimize LCP](https://web.dev/optimize-lcp/)
- [Chrome: Priority Hints](https://web.dev/priority-hints/)
- [Web.dev: Browser-level image lazy loading](https://web.dev/browser-level-image-lazy-loading/)
