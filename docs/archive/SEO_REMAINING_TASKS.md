# SEO Remaining Tasks

## ✅ Recently Completed (December 18, 2025)
1. **Canonical URLs now absolute** - Fixed: `/` → `https://jameskilby.co.uk/`
2. **OG:image URLs absolute** - Fixed relative image paths in social sharing
3. **Twitter card URLs absolute** - All meta tags now use full URLs
4. **Tag/Category meta descriptions** - Auto-generated context-specific descriptions
5. **Changelog with categorization** - Tracks features, fixes, improvements
6. **Lighthouse score history** - 90-day performance tracking

## 🔴 Critical Issues (Fix Next)

### 1. Missing H1 on Homepage ❌
**Issue**: Homepage has no H1 tag (critical for SEO)  
**Impact**: Major ranking factor - search engines need H1 for page topic  
**Fix**: Add H1 to homepage in WordPress theme  
**Priority**: HIGHEST

**Action**:
```
In WordPress:
1. Edit homepage
2. Add H1 heading at top: "VMware & Cloud Infrastructure Expert"
3. Or configure theme to auto-generate H1 from site title
```

### 2. Title Tag Too Long (143 chars) ⚠️
**Current**: "Jameskilbycouk - James Kilby's Technical Blog Covering VMware, Homelab Projects, Cloud Computing, And Infrastructure Automation. Real-world IT Solutions."  
**Google displays**: ~60-70 characters  
**Suggested**: "James Kilby | VMware & Cloud Infrastructure Expert"  
**Priority**: HIGH

**Action**:
```
In WordPress:
1. Go to Rank Math > Titles & Meta
2. Update homepage title template
3. Keep it under 60 characters
```

### 3. Meta Description Could Be Better ⚠️
**Current**: "James Kilby's technical blog covering VMware, homelab projects, cloud computing, and infrastructure automation. Real-world IT solutions."  
**Good**: Length is fine (150 chars), but could be more compelling  
**Suggested**: "Expert VMware tutorials, homelab guides, and cloud infrastructure insights. Practical tech content for vSphere, Kubernetes, and datacenter automation."  
**Priority**: MEDIUM

## 🟡 Medium Priority

### 4. Add Sitemap Priority & Changefreq
**Issue**: XML sitemap lacks priority and changefreq tags  
**Impact**: Helps search engines understand update patterns  
**Fix**: Update `create_sitemap()` in generator

**Implementation**:
```python
def create_sitemap(self):
    # Add to each <url> block:
    # <priority>0.8</priority>  # 1.0 for homepage, 0.8 for posts, 0.5 for archives
    # <changefreq>weekly</changefreq>  # daily/weekly/monthly
```

### 5. Add Schema.org Breadcrumbs
**Issue**: Missing BreadcrumbList schema  
**Impact**: Better navigation understanding, potential rich results  
**Fix**: Add to JSON-LD generation

**Example**:
```json
{
  "@type": "BreadcrumbList",
  "itemListElement": [
    {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://jameskilby.co.uk/"},
    {"@type": "ListItem", "position": 2, "name": "VMware", "item": "https://jameskilby.co.uk/category/vmware/"}
  ]
}
```

### 6. Image Alt Text Audit
**Action**:
```bash
# Check for missing alt text
grep -r 'alt=""' public/2025/*/index.html | wc -l

# Update images in WordPress before next generation
```

### 7. Add WebSite SearchAction Schema
**Benefit**: Enables Google sitelinks searchbox  
**Implementation**: Add to homepage JSON-LD

```json
{
  "@type": "WebSite",
  "@id": "https://jameskilby.co.uk/#website",
  "url": "https://jameskilby.co.uk/",
  "potentialAction": {
    "@type": "SearchAction",
    "target": "https://jameskilby.co.uk/?s={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
```

## 🟢 Low Priority (Nice to Have)

### 8. Add Article Publisher Information
**Current**: BlogPosting has publisher reference  
**Improve**: Add full Organization schema with logo

### 9. Add Author/Person Schema
**Benefit**: Rich results for author  
**Implementation**: Add Person schema linked to posts

### 10. Create Custom 404 Page
**Current**: Default 404  
**Improve**: 
- Friendly message
- Search functionality
- Links to popular posts
- Site navigation

### 11. Internal Linking
**Action**: Add 2-3 related post links at bottom of articles  
**Benefit**: SEO + user engagement + reduced bounce rate

### 12. Update About Page
**Current**: Minimal  
**Suggested**:
- Professional background
- Areas of expertise
- Certifications
- Social links
- Contact information

## 📊 Validation & Monitoring

### After Next Deploy
- [ ] Test with Google Rich Results: https://search.google.com/test/rich-results
- [ ] Validate structured data: https://validator.schema.org/
- [ ] Check social sharing: https://developers.facebook.com/tools/debug/
- [ ] Verify canonical URLs are absolute: `curl -s https://jameskilby.co.uk/ | grep canonical`
- [ ] Check OG images are absolute: `curl -s https://jameskilby.co.uk/ | grep og:image`

### Regular Monitoring
- [ ] Google Search Console - Check for errors weekly
- [ ] Core Web Vitals - Monitor Lighthouse scores (automated)
- [ ] Plausible Analytics - Track traffic trends
- [ ] Manual SEO audit - Monthly

## 🎯 Long-term Strategy

### Content
1. Identify high-value keywords (VMware, homelab, vSphere, etc.)
2. Create comprehensive guides for popular topics
3. Update old posts with fresh information
4. Build content clusters around core topics

### Technical
1. Monitor Core Web Vitals (already tracking in changelog)
2. Implement WebP images with fallbacks
3. Consider critical CSS inline for faster render
4. Test AMP versions for mobile

### Link Building
1. Guest posts on VMware/homelab communities
2. Participate in r/homelab, r/vmware
3. Share on relevant Twitter/LinkedIn
4. Comment on related blogs (natural linking)

## Quick Commands

```bash
# Verify absolute canonical URLs (should show full URL)
curl -s https://jameskilby.co.uk/ | grep -o '<link[^>]*canonical[^>]*>'

# Check OG image (should be absolute)
curl -s https://jameskilby.co.uk/ | grep -o '<meta[^>]*og:image[^>]*>'

# Count H1 tags (should be 1 per page)
curl -s https://jameskilby.co.uk/ | grep -o '<h1[^>]*>' | wc -l

# Validate sitemap
curl https://jameskilby.co.uk/sitemap.xml | head -50

# Check meta description length
curl -s https://jameskilby.co.uk/ | grep -o 'meta name="description" content="[^"]*"' | wc -c
```

## Resources
- [Google Search Central](https://developers.google.com/search)
- [Schema.org Documentation](https://schema.org)
- [Lighthouse CI](https://github.com/GoogleChrome/lighthouse-ci)
- [Web.dev](https://web.dev/measure/)
