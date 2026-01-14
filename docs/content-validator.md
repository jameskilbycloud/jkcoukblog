# Content Validator

Automated content quality and SEO validation for jameskilby.co.uk.

## Overview

The content validator runs automatically during the build process and checks for:

- **SEO Issues**: Title length, meta descriptions, H1 tags, canonical URLs, Open Graph tags
- **Accessibility**: Missing alt text, form labels, empty links, heading hierarchy
- **Performance**: Lazy loading, render-blocking resources, inline styles, script optimization
- **Security**: Mixed content (HTTP resources on HTTPS), inline scripts without CSP
- **Broken Links**: Internal links that don't resolve to existing pages

## Usage

### Automated (CI/CD)

The validator runs automatically in the GitHub Actions workflow after HTML validation. It's configured as **non-blocking**, meaning warnings won't fail the build but will be reported in:

1. GitHub Actions console output
2. GitHub Actions job summary
3. `validation-report.json` (committed to repo)

### Manual Testing

Run locally before pushing changes:

```bash
# Validate the public directory
python3 content_validator.py

# View the full report
cat validation-report.json | jq
```

## Report Format

The validator generates a JSON report with:

```json
{
  "summary": {
    "checks_run": 163,
    "errors": 82,
    "warnings": 1165,
    "status": "FAIL"
  },
  "errors": [...],
  "warnings": [...]
}
```

### Error Types

**Critical Errors** (will show as FAIL):
- `broken_link`: Internal link doesn't resolve
- `seo_no_title`: Missing title tag
- `seo_no_h1`: Missing H1 heading
- `accessibility_empty_link`: Link without text content
- `security_mixed_content`: HTTP resources on HTTPS page

**Warnings** (informational only):
- `seo_title_long/short`: Title length not optimal
- `seo_description_long/short`: Meta description not optimal
- `seo_multiple_h1`: Multiple H1 tags (should be 1)
- `missing_alt`: Image without alt text
- `performance_no_lazy_loading`: Image without lazy loading
- `performance_render_blocking`: CSS/JS blocking render
- `accessibility_no_label`: Form input without label
- `accessibility_heading_skip`: Skipped heading level (e.g., H1 -> H3)

## Configuration

Edit `content_validator.py` to adjust:

- **SEO thresholds**: Title length (30-60 chars), description length (120-160 chars)
- **Performance limits**: Inline styles threshold (currently 10)
- **Check toggles**: Enable/disable specific validation checks

## Integration Status

✅ Integrated into `.github/workflows/deploy-static-site.yml`
- Step: "Content quality validation"
- Non-blocking: `continue-on-error: true`
- Timeout: 5 minutes
- Report committed to repo: `validation-report.json`

## Future Enhancements

Potential improvements:

- [ ] Validate JSON-LD structured data
- [ ] Check for mobile viewport meta tag
- [ ] Validate robots.txt and sitemap references
- [ ] Check for duplicate content (title/description)
- [ ] Validate RSS/Atom feed format
- [ ] Performance budget checks (page size, resource count)
- [ ] Link checking against external URLs (with rate limiting)
- [ ] Image size recommendations
- [ ] Contrast ratio checking for accessibility
