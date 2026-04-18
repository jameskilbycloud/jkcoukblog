# SEO Documentation

This document covers all SEO-related features and optimizations.

## Table of Contents
- [Soft-404 guard](#soft-404-guard)
- [IndexNow](#indexnow)
- [Rich Results](#rich-results)
- [Security Headers](#security-headers)
- [SEO Quick Wins](#seo-quick-wins)
- [WWW Redirect](#www-redirect)

---

## Soft-404 guard

### Why it exists
The Cloudflare Pages project was historically configured with SPA-style
`not_found_handling`, which made `env.ASSETS.fetch()` return
`/index.html` with HTTP 200 for every missing path. The Advanced Mode
Worker in front then cached those homepage responses under the bogus
URL's KV key. Bing's Site Explorer ended up showing ~40 legacy flat
permalinks (`/nutanix-ce`, `/cloudflare`, `/lab-storage-2`, …) all
returning 200, which is why recent `/YYYY/MM/slug/` posts never ranked
— Bing's crawl budget was spent re-validating ghosts, and IndexNow
submissions to Bing were 403'd because the site failed its
soft-404 sanity check.

### Components
1. **Path manifest** (`public/path-manifest.json`) — JSON array of
   every legitimate content URL. Generated from `public/*.html` by
   `scripts/generate_soft404_artefacts.py`.
2. **Stamped worker** — `scripts/stamp_worker_manifest.py` inlines the
   manifest into `_worker.template.js` (replacing the
   `/*__PATH_MANIFEST_START__*/…/*__PATH_MANIFEST_END__*/` placeholder)
   and writes the result to `public/_worker.js`. The Worker refuses to
   serve or cache any path not in the manifest — unknown paths get a
   real 404 body and `X-Robots-Tag: noindex`.
3. **404 page** — `public/404.html`, also written by
   `generate_soft404_artefacts.py`. Theme-consistent, small, noindex.
4. **Legacy redirects** — the same script appends `/slug/ →
   /YYYY/MM/slug/` 301s to `public/_redirects` inside a marked block
   (idempotent across reruns). This rescues every external backlink
   that still points at the pre-date-prefix permalink structure.
5. **Targeted KV purge** — `scripts/purge_soft404_kv_cache.py` lists
   every `html:*` key in `HTML_CACHE`, cross-references the manifest,
   and deletes only the poisoned entries (preserving the warm cache
   for real pages). Needed once after deploying this change, then only
   if soft-404s reappear.

### Manual steps that must accompany a code deploy
These cannot be automated from the repo:

- **No dashboard setting to change.** Classic Cloudflare Pages has no
  "Not Found Behavior" toggle — 404 handling is driven entirely by
  whether `404.html` is present in the project output. The build now
  emits `public/404.html`, so once the deploy lands, `env.ASSETS.fetch()`
  will return that page with a real 404 status for missing paths. The
  Worker's `isKnownContentPath` guard is defence in depth on top of
  that.
- **Bing Webmaster Tools** (bing.com/webmasters):
  1. Open the `jameskilby.co.uk` property.
  2. Site Explorer → find any `/nutanix-ce`-style URL → **Submit URL
     for re-inspection** to trigger a re-crawl. Once Bing sees the
     301 (or the new 404 when the redirect is missing), it drops the
     ghost.
  3. Re-verify the IndexNow key (Settings → IndexNow) — Bing starts
     rejecting keys with `UserForbiddedToAccessSite` after repeated
     soft-404 responses. Re-verification should succeed once the site
     is serving proper 404s.
  4. Resubmit `https://jameskilby.co.uk/sitemap.xml` under Sitemaps.

### Operational runbook

```bash
# After the next deploy lands, purge the historically poisoned KV entries
export CLOUDFLARE_API_TOKEN=…
export CLOUDFLARE_ACCOUNT_ID=…
python3 scripts/purge_soft404_kv_cache.py --dry-run   # review
python3 scripts/purge_soft404_kv_cache.py             # execute

# Sanity check — both should return 404 with X-Cache-Status: SOFT404-FIXED
curl -I https://jameskilby.co.uk/nutanix-ce              # expect: 301 → /2018/01/nutanix-ce/
curl -I https://jameskilby.co.uk/this-does-not-exist-xyz # expect: 404
curl -I https://jameskilby.co.uk/                        # expect: 200
```

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
- ✅ Reading time and word count visible on posts

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
