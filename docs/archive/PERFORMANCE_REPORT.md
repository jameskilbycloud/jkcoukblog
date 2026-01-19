# Performance Analysis & Optimization Report
**Date**: December 26, 2025  
**Site**: jameskilby.co.uk

## Current Performance Metrics

### Load Times
- **DNS Lookup**: 2.8ms ✅ Excellent
- **Connection**: 48.8ms ✅ Good
- **TLS Handshake**: 114.9ms ⚠️ Could be better
- **TTFB**: 202.9ms ⚠️ Needs improvement
- **Total Load**: 263.6ms ✅ Good
- **HTML Size**: 223KB (down from 244KB) ✅ Improved

### File Sizes
- **Homepage HTML**: 223KB (8.6% reduction after CSS extraction)
- **Extracted CSS Files**:
  - `brutalist-theme`: 11KB
  - `global-styles`: 10KB
  - `classic-theme-styles`: 293 bytes
  - `core-block-supports`: 308 bytes
- **Total Site Size**: 61MB (was 64MB)
- **CSS Load Time**: 213ms per file

### Caching Status
- **HTTP Headers**:
  - `cache-control: public, max-age=300, must-revalidate` (5 minutes)
  - `cf-cache-status: DYNAMIC` ❌ **Not using CDN cache**
  - `vary: accept-encoding` ✅

## 🔴 Critical Issues

### 1. Cloudflare Not Caching HTML ⚠️ HIGH PRIORITY
**Problem**: `cf-cache-status: DYNAMIC` means every request hits origin
**Impact**: Slower TTFB, higher server load, wasted CDN potential
**Solution**: Create Cloudflare Page Rule

### 2. Google Fonts External Dependency 🔴 BLOCKING
**Problem**: Line 48 loads fonts from `fonts.googleapis.com` via `@import`
**Impact**: 
- Blocks rendering until fonts load
- External DNS lookup + connection
- Adds 200-400ms to first paint
**Solution**: Self-host fonts or use font-display: swap

### 3. Large CSS Bundle (214KB) ⚠️
**Problem**: `wpo-minify-header-9efd2777.min.css` is 214KB
**Impact**: Takes 213ms to load, blocks rendering
**Solution**: 
- Split into critical and non-critical CSS
- Inline critical CSS
- Defer non-critical CSS

### 4. No Brotli Compression Yet ⚠️
**Problem**: Brotli not deployed (still in local testing)
**Impact**: Larger file transfers (70-80% more data than needed)
**Solution**: Deploy changes to trigger GitHub Actions build

## 🟡 Medium Priority Issues

### 5. No HTTP/2 Server Push Headers
**Problem**: Not leveraging HTTP/2 push for critical resources
**Solution**: Add Link headers for critical CSS/JS

### 6. Preload Links in Wrong Order
**Problem**: Preload links present but may not be prioritized correctly
**Solution**: Reorder preload hints by importance

### 7. TLS Handshake Time
**Problem**: 115ms TLS handshake is higher than optimal
**Note**: This is Cloudflare's TLS, can't control directly

### 8. Images Not Using Modern Formats
**Problem**: Using PNG/JPG instead of WebP/AVIF
**Impact**: 30-50% larger image sizes
**Solution**: Add WebP conversion to build process

## 🟢 Working Well

✅ DNS resolution is fast (2.8ms)  
✅ HTML size reduced by 8.6%  
✅ Inline CSS successfully extracted  
✅ Security headers properly configured  
✅ HTTP/2 enabled  
✅ Image optimization pipeline in place

## Recommended Optimizations (Priority Order)

### 🔴 CRITICAL: Deploy Now

#### 1. Enable Cloudflare HTML Caching
**Create Page Rule** in Cloudflare Dashboard:

```
Pattern: jameskilby.co.uk/*
Settings:
- Cache Level: Cache Everything
- Edge Cache TTL: 5 minutes
- Browser Cache TTL: 5 minutes
```

**Expected Improvement**: TTFB drops from 203ms → ~50ms (75% faster)

#### 2. Self-Host Google Fonts
**Action**: Download and include fonts locally

```bash
# Download fonts
wget https://fonts.googleapis.com/css2?family=Anton&display=swap -O fonts.css
# Extract woff2 URLs and download them
# Place in /assets/fonts/
```

**Update** `brutalist-theme-855147c0.min.css`:
```css
/* Instead of @import url('https://fonts.googleapis.com/...'); */
@font-face {
  font-family: 'Anton';
  font-style: normal;
  font-weight: 400;
  font-display: swap;
  src: url('/assets/fonts/anton.woff2') format('woff2');
}
```

**Expected Improvement**: First Contentful Paint improves by 200-400ms

#### 3. Deploy Brotli Compression
**Action**: Commit current changes to trigger GitHub Actions

```bash
git add .
git commit -m "feat: Add Brotli compression and CSS extraction"
git push
```

**Expected Improvement**: 70-80% reduction in transfer sizes

### 🟡 HIGH PRIORITY: Next Sprint

#### 4. Inline Critical CSS
**Create** `inline-critical.css` with above-the-fold styles:

```css
/* Critical styles only - layout, colors, fonts for above-fold content */
body { background: #0a0a0a; color: #fafafa; }
.site-header { /* header styles */ }
/* ~2-3KB max */
```

Inline in `<head>`, defer rest:
```html
<style>/* critical CSS here */</style>
<link rel="preload" href="/assets/css/full.css" as="style" onload="this.onload=null;this.rel='stylesheet'">
```

**Expected Improvement**: First Paint improves by 100-200ms

#### 5. Add WebP Images
**Modify** `optimize_images.py` to also create WebP versions:

```python
# After PNG/JPG optimization
if img.format in ['PNG', 'JPEG']:
    webp_path = path.with_suffix('.webp')
    img.save(webp_path, 'WebP', quality=85)
```

Update HTML to use `<picture>`:
```html
<picture>
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="...">
</picture>
```

**Expected Improvement**: 30-50% smaller images

#### 6. Reduce JavaScript Bundle Size
**Current**: `wpo-minify-footer-95ac0934.min.js` is 53KB  
**Action**: 
- Defer non-critical JS
- Remove unused libraries
- Code split by route

### 🟢 LOW PRIORITY: Future Enhancements

#### 7. Service Worker for Offline Support
Add service worker for:
- Offline page views
- Faster repeat visits
- Background sync

#### 8. Resource Hints for External Domains
```html
<link rel="dns-prefetch" href="//plausible.jameskilby.cloud">
<link rel="preconnect" href="https://plausible.jameskilby.cloud" crossorigin>
```

Already present ✅ but could add more for other domains

#### 9. Lazy Load Below-Fold Images
Currently using `loading="lazy"` on some images ✅  
Ensure ALL below-fold images use it

#### 10. Reduce JSON-LD Size
**Current**: 2.3KB JSON-LD in `<head>`  
**Action**: Minify and remove unnecessary fields

## Implementation Plan

### Week 1 (Immediate)
- [ ] Create Cloudflare Page Rule for caching
- [ ] Download and self-host Google Fonts
- [ ] Deploy Brotli compression (commit changes)
- [ ] Test and verify improvements

### Week 2 (High Priority)
- [ ] Extract and inline critical CSS
- [ ] Add WebP image generation
- [ ] Optimize CSS bundle (split/defer)

### Week 3 (Polish)
- [ ] Further JS optimization
- [ ] Add more lazy loading
- [ ] Performance monitoring setup

## Expected Results After All Optimizations

| Metric | Current | Target | Improvement |
|--------|---------|--------|-------------|
| TTFB | 203ms | ~50ms | 75% faster |
| Total Load | 264ms | ~150ms | 43% faster |
| HTML Size | 223KB | ~180KB | 19% smaller |
| CSS Size | 214KB | ~30KB (critical) | 86% smaller |
| First Paint | ~300ms | ~150ms | 50% faster |
| Total Transfer | ~500KB | ~100KB | 80% smaller |

## Monitoring & Testing

### Tools to Use
1. **Chrome DevTools** - Network/Performance tabs
2. **WebPageTest** - https://www.webpagetest.org/
3. **Lighthouse** - Built into Chrome DevTools
4. **Cloudflare Analytics** - Check cache hit rate

### Key Metrics to Track
- **Core Web Vitals**:
  - LCP (Largest Contentful Paint): Target < 2.5s
  - FID (First Input Delay): Target < 100ms
  - CLS (Cumulative Layout Shift): Target < 0.1
- **Cache Hit Rate**: Target > 95%
- **Bandwidth Savings**: Track with Brotli compression

### Testing Commands

```bash
# Test TTFB
curl -o /dev/null -s -w "TTFB: %{time_starttransfer}s\n" https://jameskilby.co.uk/

# Check cache status
curl -I https://jameskilby.co.uk/ | grep cf-cache-status

# Check Brotli encoding
curl -H "Accept-Encoding: br" -I https://jameskilby.co.uk/ | grep content-encoding

# Test with multiple requests (check caching)
for i in {1..5}; do
  curl -o /dev/null -s -w "$i: %{time_total}s\n" https://jameskilby.co.uk/
done
```

## Cost-Benefit Analysis

### High ROI (Do First)
1. **Cloudflare Caching**: 5 min setup → 75% TTFB improvement
2. **Brotli Compression**: Already done → 70-80% bandwidth savings
3. **Self-host Fonts**: 30 min → 200-400ms FCP improvement

### Medium ROI
4. **Critical CSS**: 2-3 hours → 100-200ms improvement
5. **WebP Images**: 1-2 hours → 30-50% image size reduction

### Lower ROI (Nice to Have)
6. **JS Optimization**: 4-6 hours → 10-15% improvement
7. **Service Worker**: 6-8 hours → Better UX for repeat visitors

## Conclusion

The site is performing reasonably well (264ms total load), but has significant room for improvement. The three critical fixes (Cloudflare caching, self-hosted fonts, Brotli compression) could reduce load times by 50-60% and bandwidth by 70-80%.

**Immediate Action Items**:
1. Create Cloudflare Page Rule (5 minutes)
2. Self-host Google Fonts (30 minutes)
3. Deploy Brotli changes (1 minute - git push)

**Expected Result**: Load time drops from 264ms → ~150ms, bandwidth drops by 70-80%.
