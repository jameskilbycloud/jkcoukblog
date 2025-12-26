# Performance Monitoring with Lighthouse CI

Automated performance monitoring is configured to track site speed, accessibility, SEO, and best practices metrics over time.

## 🚦 What's Monitored

### Core Web Vitals
- **Largest Contentful Paint (LCP)** - Loading performance (target: <2.5s)
- **First Input Delay (FID)** - Interactivity (target: <100ms)
- **Cumulative Layout Shift (CLS)** - Visual stability (target: <0.1)

### Performance Metrics
- **First Contentful Paint (FCP)** - When first content appears
- **Speed Index** - How quickly content is visually displayed
- **Time to Interactive (TTI)** - When page becomes fully interactive
- **Total Blocking Time (TBT)** - Time blocked by long tasks

### Category Scores (0-100)
- **Performance** - Overall page speed
- **Accessibility** - WCAG compliance and usability
- **Best Practices** - Modern web standards
- **SEO** - Search engine optimization

### Resource Budgets
- Document size: 50 KB
- Stylesheets: 100 KB total
- Scripts: 200 KB total
- Images: 500 KB total
- Fonts: 100 KB total
- Total page weight: 1 MB

---

## 📊 Monitoring Schedule

### Automatic Scans
- **On every push** to main/master branch (after 2-minute deployment delay)
- **On every pull request** to catch regressions before merge
- **Daily at 3 AM UTC** for trend tracking

### Manual Scans
Trigger manually via GitHub Actions:
```bash
gh workflow run lighthouse-ci.yml
```

---

## 📁 What Gets Tested

Three key pages are monitored:

1. **Homepage** - `https://jameskilby.co.uk`
   - First impression for visitors
   - Critical for SEO rankings

2. **Category Page** - `https://jameskilby.co.uk/category/`
   - Archive/listing performance
   - Typical user journey

3. **Recent Posts** - `https://jameskilby.co.uk/2025/`
   - Content page performance
   - Representative of blog post pages

Each URL is tested **3 times** and the **median scores** are reported to reduce variance.

---

## 🎯 Performance Budgets

Performance budgets are defined in `.github/lighthouse/budget.json`:

### Timing Budgets

| Metric | Budget | Tolerance |
|--------|--------|-----------|
| First Contentful Paint (FCP) | 2000ms | ±200ms |
| Largest Contentful Paint (LCP) | 2500ms | ±500ms |
| Time to Interactive (TTI) | 3500ms | ±500ms |
| Speed Index | 3000ms | ±300ms |
| Total Blocking Time (TBT) | 300ms | ±100ms |
| Cumulative Layout Shift (CLS) | 0.1 | ±0.05 |

### Resource Size Budgets (KB)

| Resource Type | Budget |
|---------------|--------|
| Document (HTML) | 50 KB |
| Stylesheets (CSS) | 100 KB |
| Scripts (JS) | 200 KB |
| Images | 500 KB |
| Fonts | 100 KB |
| **Total** | **1000 KB (1 MB)** |

### Resource Count Budgets

| Resource Type | Max Count |
|---------------|-----------|
| Stylesheets | 10 |
| Scripts | 15 |
| Images | 30 |
| Fonts | 5 |
| Third-party resources | 10 |

**If any budget is exceeded**, the workflow will fail and alert via Slack.

---

## 🔔 Notifications

### Performance Regressions
When budgets are exceeded on push events:
- Slack alert sent to `#web` channel
- Alert includes:
  - Branch and commit information
  - Link to detailed Lighthouse report
  - Triggered by user

### Daily Status
After successful daily scan:
- Confirmation posted to Slack
- Shows all budgets are within acceptable ranges
- Link to detailed metrics

---

## 📈 Viewing Reports

### GitHub Actions Artifacts

After each run, reports are uploaded as artifacts:

```bash
# List recent Lighthouse runs
gh run list --workflow=lighthouse-ci.yml

# View specific run
gh run view <run-id>

# Download reports
gh run download <run-id>
```

Reports are kept for **30 days**.

### Temporary Public Storage

Reports are also uploaded to temporary public storage (lasts 7 days):
- Check workflow logs for public URL
- Share link with team for review
- No authentication required

### GitHub Actions Summary

Each run includes a summary in the GitHub Actions UI:
- List of URLs tested
- Metrics tracked
- Link to download full reports

---

## ⚙️ Configuration

### Lighthouse Config (`.github/lighthouse/lighthouse-config.json`)

```json
{
  "extends": "lighthouse:default",
  "settings": {
    "onlyCategories": ["performance", "accessibility", "best-practices", "seo"],
    "formFactor": "desktop",
    "throttling": {
      "rttMs": 40,
      "throughputKbps": 10240,
      "cpuSlowdownMultiplier": 1
    }
  }
}
```

**Settings:**
- Desktop simulation (1350x940 viewport)
- Fast 3G throttling
- Audits: Performance, Accessibility, Best Practices, SEO

### Budget Config (`.github/lighthouse/budget.json`)

Edit budgets to match your performance goals:
```json
{
  "timings": [
    {
      "metric": "first-contentful-paint",
      "budget": 2000,
      "tolerance": 200
    }
  ]
}
```

---

## 🔧 Customization

### Add More URLs

Edit `.github/workflows/lighthouse-ci.yml`:
```yaml
urls: |
  https://jameskilby.co.uk
  https://jameskilby.co.uk/about/
  https://jameskilby.co.uk/2025/01/specific-post/
```

### Adjust Timing

Change deployment wait time:
```yaml
- name: Wait for deployment
  run: |
    echo "⏳ Waiting 3 minutes..."
    sleep 180  # Increase from 120 to 180 seconds
```

### Modify Budgets

Tighten or relax performance budgets:
```json
{
  "metric": "largest-contentful-paint",
  "budget": 2000,  // Stricter: 2.5s -> 2.0s
  "tolerance": 300  // Tighter tolerance
}
```

### Change Schedule

Adjust cron schedule in workflow:
```yaml
schedule:
  - cron: '0 */6 * * *'  # Every 6 hours instead of daily
```

---

## 📊 Interpreting Results

### Score Ranges

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | ✅ Good | Maintain current performance |
| 50-89 | 🟡 Needs Improvement | Investigate opportunities |
| 0-49 | 🔴 Poor | Immediate action required |

### Common Issues & Fixes

#### Slow LCP (Largest Contentful Paint)
- **Problem:** Images loading too slowly
- **Fix:** Optimize images, use WebP format, add lazy loading

#### High CLS (Cumulative Layout Shift)
- **Problem:** Content shifting as page loads
- **Fix:** Set explicit dimensions for images, avoid dynamic content insertion

#### Poor TTI (Time to Interactive)
- **Problem:** Too much JavaScript blocking main thread
- **Fix:** Code splitting, defer non-critical JS, reduce bundle size

#### Large Total Page Size
- **Problem:** Exceeding 1 MB budget
- **Fix:** Compress assets, remove unused CSS/JS, optimize images

---

## 🚀 Optimization Tips

### Images
```bash
# Already implemented in your workflow
- PNG: optipng -o2
- JPEG: jpegoptim --max=85
```

### CSS
- Inline critical CSS
- Defer non-critical stylesheets
- Remove unused CSS (use PurgeCSS)

### JavaScript
- Minimize third-party scripts
- Use async/defer for non-critical scripts
- Tree-shake unused code

### Fonts
- Use `font-display: swap`
- Subset fonts to include only used characters
- Serve fonts from same origin

### Caching
- Already configured in Cloudflare Pages
- Long cache times for static assets
- Versioned filenames for cache busting

---

## 🔍 Troubleshooting

### Workflow Fails Immediately

**Issue:** Lighthouse can't reach site
**Solution:** 
```bash
# Test manually
curl -I https://jameskilby.co.uk
# Check Cloudflare Pages deployment status
```

### Inconsistent Scores

**Issue:** Scores vary between runs
**Solution:** This is normal - Lighthouse runs 3 times and takes median

### Budgets Always Exceeded

**Issue:** Budgets too strict
**Solution:** Adjust budgets in `.github/lighthouse/budget.json` to match current performance

### Public Storage Upload Fails

**Issue:** Third-party service issues
**Solution:** Reports still available as GitHub artifacts

---

## 📚 Additional Resources

- **Lighthouse Documentation:** https://developer.chrome.com/docs/lighthouse/
- **Web Vitals:** https://web.dev/vitals/
- **Performance Budgets:** https://web.dev/performance-budgets-101/
- **Lighthouse CI:** https://github.com/GoogleChrome/lighthouse-ci
- **Core Web Vitals Guide:** https://web.dev/learn-core-web-vitals/

---

## 🎯 Performance Goals

Based on your static WordPress site, aim for:

| Metric | Target | Current Baseline | Status |
|--------|--------|------------------|--------|
| Performance Score | >95 | TBD after first run | ⏳ |
| LCP | <2.5s | TBD | ⏳ |
| FCP | <1.8s | TBD | ⏳ |
| CLS | <0.1 | TBD | ⏳ |
| TTI | <3.5s | TBD | ⏳ |
| Total Page Size | <1 MB | TBD | ⏳ |

**First run will establish your baseline metrics.**

---

## 🔄 Continuous Improvement

### Weekly Review
1. Check daily Lighthouse reports
2. Identify trending issues
3. Prioritize optimizations

### Monthly Optimization Sprint
1. Review month's performance data
2. Implement top 3 opportunities
3. Measure improvement

### Before Major Changes
1. Run manual Lighthouse scan
2. Make changes
3. Run scan again
4. Compare before/after

---

## ❓ Questions?

If you have questions about performance monitoring:
1. Check this documentation first
2. Review Lighthouse reports in GitHub artifacts
3. Check Slack notifications for alerts
4. Test manually: `npx lighthouse https://jameskilby.co.uk`

Performance monitoring is now tracking your site 24/7!
