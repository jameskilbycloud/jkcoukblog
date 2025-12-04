# SEO Quick Wins - Priority Actions

## ✅ Completed (December 4, 2025)
1. **Fixed all WordPress URL references** - Now all meta tags and JSON-LD point to jameskilby.co.uk
2. **Created robots.txt** - Guides search engine crawlers
3. **Added security headers** - via _headers file for Cloudflare Pages

## 🔴 High Priority (Do Next)

### 1. Disable Duplicate SEO Plugin (5 minutes)
**Issue**: Both All in One SEO and Rank Math are active, causing duplicate meta tags
**Action**: In WordPress, deactivate "All in One SEO" plugin
**Why**: Reduces page weight by ~5KB, removes conflicting SEO directives

### 2. Fix Future Dates (15 minutes)
**Issue**: Posts dated October 2025, September 2025 (future dates)
**Action**: In WordPress, correct post dates to 2024
**Why**: Future dates harm credibility and may confuse search engines

### 3. Update Homepage Meta (10 minutes)
**Current Title**: "Jameskilbycouk - Some ramblings usually about computers"
**Suggested**: "James Kilby | VMware Expert, Cloud Infrastructure & Homelab Enthusiast"

**Current Description**: "Some ramblings usually about computers"
**Suggested**: "VMware and cloud infrastructure tutorials, homelab guides, and DevOps insights from a field expert. Practical tech content about vSphere, Kubernetes, and home datacenter builds."

**Why**: Better CTR in search results, more professional appearance

## 🟡 Medium Priority (This Week)

### 4. Image Alt Text Audit (30 minutes)
**Issue**: Several images have empty alt="" attributes
**Action**: 
```bash
# Find images without alt text
grep -r 'alt=""' public/2025/*/index.html
```
Update in WordPress before next generation

### 5. Add Internal Linking (30 minutes)
**Action**: Add 2-3 related post links at the bottom of each major article
**Why**: Improves SEO, increases time on site, better UX

### 6. Update Author Bio (10 minutes)
**Action**: Create proper /about-me/ page with:
- Professional background
- Areas of expertise
- Social links (if desired)
- Contact information

## 🟢 Low Priority (Nice to Have)

### 7. Create Custom 404 Page
```html
<!-- public/404.html -->
- Friendly message
- Link to homepage
- Search functionality
- Popular posts
```

### 8. Add Structured Data Enhancements
- Review article structured data
- Add FAQ schema where applicable
- Consider HowTo schema for tutorial posts

### 9. Performance Optimizations
- Implement lazy loading for below-fold images
- Consider WebP with fallbacks
- Optimize CSS delivery (critical CSS inline)

## 📊 Monitoring & Validation

### After Next Deploy
1. Check Google Search Console for errors
2. Validate structured data: https://search.google.com/test/rich-results
3. Test social sharing: https://developers.facebook.com/tools/debug/
4. Verify robots.txt: https://jameskilby.co.uk/robots.txt

### Weekly
- Monitor Google Search Console for crawl errors
- Check Plausible Analytics for traffic trends
- Review new posts for SEO optimization

## 🎯 Long-term Goals

1. **Content Strategy**
   - Identify high-value keywords in your niche
   - Create comprehensive guides for popular topics
   - Update old posts with new information

2. **Technical SEO**
   - Submit sitemap to Google Search Console
   - Submit sitemap to Bing Webmaster Tools
   - Monitor Core Web Vitals

3. **Link Building**
   - Guest posts on VMware/homelab blogs
   - Participate in tech communities
   - Share on relevant social platforms

## Quick Commands

```bash
# Check for WordPress URLs (should be 0 after fix)
grep -r "wordpress.jameskilby.cloud" public/*.html | wc -l

# Check for missing alt text
grep -r 'alt=""' public/ | wc -l

# Count pages generated
find public -name "index.html" | wc -l

# Check sitemap
curl https://jameskilby.co.uk/sitemap.xml

# Verify robots.txt
curl https://jameskilby.co.uk/robots.txt
```

## Resources
- [Google Search Central](https://developers.google.com/search)
- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages)
- [Schema.org Documentation](https://schema.org)
