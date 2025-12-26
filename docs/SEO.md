# SEO Documentation

This document covers all SEO-related features and optimizations.

## Table of Contents
- [IndexNow](#indexnow)
- [Rich Results](#rich-results)
- [Security Headers](#security-headers)
- [SEO Quick Wins](#seo-quick-wins)
- [WWW Redirect](#www-redirect)

---

## IndexNow

### Overview
IndexNow is a protocol that allows websites to instantly notify search engines (Bing, Yandex, etc.) when content is published or updated.

### Implementation
Script: `submit_indexnow.py`

### Usage

**Submit all pages:**
```bash
python submit_indexnow.py ./public
```

**The script automatically:**
- Generates and manages API key for domain verification
- Creates key verification file in site root
- Scans all HTML files in the public directory
- Submits URLs to IndexNow endpoint
- Logs submission history to `indexnow-submission.json`

### Benefits
- **Instant indexing**: Search engines notified immediately
- **Faster discovery**: New content appears in search results sooner
- **Reduced crawl budget**: Search engines focus on updated content
- **Multiple search engines**: One submission reaches Bing, Yandex, and partners

### Supported Search Engines
- Microsoft Bing
- Yandex
- Seznam.cz
- Naver (via partnerships)

### Verification
Check submission logs:
```bash
cat indexnow-submission.json | jq '.recent_submissions'
```

### GitHub Actions Integration
Automatically runs after each deployment:
```yaml
- name: Submit to IndexNow
  run: python3 submit_indexnow.py ./public
```

---

## Rich Results

### Overview
Structured data (JSON-LD) implementation for better search engine visibility and rich snippets.

### Implemented Types

#### Article Schema
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "Post Title",
  "datePublished": "2025-01-01T12:00:00Z",
  "dateModified": "2025-01-02T14:30:00Z",
  "author": {
    "@type": "Person",
    "name": "James Kilby"
  },
  "publisher": {
    "@type": "Organization",
    "name": "Jameskilbycouk"
  }
}
```

#### Breadcrumb Schema
Helps search engines understand site hierarchy.

#### Organization Schema
Defines site identity and branding.

### Benefits
- Enhanced search results with rich snippets
- Better click-through rates
- Improved SEO rankings
- Google Search Console insights

### Validation
Use Google's Rich Results Test:
```
https://search.google.com/test/rich-results
```

---

## Security Headers

### Overview
HTTP security headers protect against common web vulnerabilities and improve SEO ranking.

### Implemented Headers

#### Content Security Policy (CSP)
```
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' plausible.jameskilby.cloud
```

#### X-Content-Type-Options
```
X-Content-Type-Options: nosniff
```
Prevents MIME type sniffing.

#### X-Frame-Options
```
X-Frame-Options: SAMEORIGIN
```
Protects against clickjacking.

#### Referrer-Policy
```
Referrer-Policy: strict-origin-when-cross-origin
```
Controls referrer information.

#### Permissions-Policy
```
Permissions-Policy: geolocation=(), microphone=(), camera=()
```
Disables unnecessary browser features.

### Configuration

**Cloudflare Pages:**
Add to `_headers` file in public directory:
```
/*
  X-Content-Type-Options: nosniff
  X-Frame-Options: SAMEORIGIN
  Referrer-Policy: strict-origin-when-cross-origin
```

**Netlify:**
Add to `netlify.toml`:
```toml
[[headers]]
  for = "/*"
  [headers.values]
    X-Content-Type-Options = "nosniff"
    X-Frame-Options = "SAMEORIGIN"
```

### Verification
Check headers:
```bash
curl -I https://jameskilby.co.uk
```

Test with securityheaders.com:
```
https://securityheaders.com/?q=jameskilby.co.uk
```

---

## SEO Quick Wins

### Completed Optimizations

#### Meta Tags
- ✅ Title tags (optimal length 50-60 chars)
- ✅ Meta descriptions (150-160 chars)
- ✅ Canonical URLs (prevent duplicate content)
- ✅ Open Graph tags (social sharing)
- ✅ Twitter Card tags

#### Content Optimization
- ✅ Heading hierarchy (H1 → H2 → H3)
- ✅ Alt text on all images
- ✅ Internal linking structure
- ✅ Clean URL structure

#### Technical SEO
- ✅ XML sitemap generated automatically
- ✅ Robots.txt properly configured
- ✅ 404 pages handled gracefully
- ✅ Fast page load times (<2s)
- ✅ Mobile-responsive design

#### Performance
- ✅ Image optimization (PNG/JPEG compression)
- ✅ Lazy loading for below-fold images
- ✅ CSS/JS minification
- ✅ Browser caching headers
- ✅ DNS prefetch for external resources

### Remaining Tasks

#### Content
- [ ] Add FAQ schema markup
- [ ] Implement article series/collection pages
- [ ] Add estimated reading time
- [ ] Create cornerstone content

#### Technical
- [ ] Implement WebP with fallback
- [ ] Add service worker for offline support
- [ ] Create AMP versions of key pages
- [ ] Implement lazy loading for fonts

#### Link Building
- [ ] Submit to relevant directories
- [ ] Guest posting opportunities
- [ ] Internal link audit and optimization
- [ ] Broken link monitoring

---

## WWW Redirect

### Overview
Redirect www subdomain to apex domain for consistency and SEO.

### Implementation

**DNS Configuration:**
- A record: jameskilby.co.uk → Cloudflare Pages
- CNAME record: www.jameskilby.co.uk → jameskilby.co.uk

**Cloudflare Pages:**
Custom domain configured with automatic HTTPS redirect.

### Benefits
- **SEO**: Prevents duplicate content penalties
- **Consistency**: Single canonical domain
- **SSL**: Automatic HTTPS for both domains
- **User experience**: Works with or without www

### Verification
```bash
# Test www redirect
curl -I https://www.jameskilby.co.uk

# Should return 301/302 redirect to:
# https://jameskilby.co.uk
```

### Best Practice
Always use apex domain (jameskilby.co.uk) in:
- Canonical tags
- Sitemaps
- Internal links
- Social media links

---

## Related Documentation
- [Main README](../README.md)
- [FEATURES.md](FEATURES.md)
- [OPTIMIZATION.md](OPTIMIZATION.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
