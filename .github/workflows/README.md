# GitHub Actions Workflows

## Available Workflows

### 1. WordPress to Static Site Deploy
**File:** `deploy-static-site.yml`

**Purpose:** Generates static site from WordPress and deploys to Cloudflare Pages

**Trigger:** 
- Manual (`workflow_dispatch`)
- Webhook (`repository_dispatch`)

**Key Steps:**
- Spell check (optional)
- Generate static site
- Optimize images
- Submit to IndexNow
- Deploy to Cloudflare Pages

**Secrets Required:**
- `WP_AUTH_TOKEN` (required)
- `SLACK_WEBHOOK_URL` (optional)
- `OLLAMA_API_CREDENTIALS` (optional, for spell check)

**Documentation:** See main `README.md` and `docs/WARP.md`

---

### 2. Test Live Site Formatting
**File:** `test-live-site.yml`

**Purpose:** Tests live site (production or staging) for formatting, SEO, and technical standards

**Trigger:** Manual only (`workflow_dispatch`)

**Key Features:**
- 14 comprehensive tests
- Test production or staging
- Optional post page testing
- Slack notifications
- GitHub Actions summary

**Secrets Required:**
- None (tests public site)
- `SLACK_WEBHOOK_URL` (optional, for notifications)

**How to Run:**

#### Via GitHub UI
1. Go to **Actions** tab
2. Select **Test Live Site Formatting**
3. Click **Run workflow**
4. Choose URL to test
5. Optionally add post page URL

#### Via CLI
```bash
# Test production
gh workflow run test-live-site.yml

# Test staging
gh workflow run test-live-site.yml \
  -f test_url='https://jkcoukblog.pages.dev'

# Test with specific post
gh workflow run test-live-site.yml \
  -f test_post='https://jameskilby.co.uk/2025/12/ubuntu-disk-expansion-steps/'
```

**Documentation:** See `docs/GITHUB_ACTIONS_LIVE_SITE_TESTING.md`

---

## Quick Commands

### List Recent Workflow Runs
```bash
gh run list --limit 10
```

### View Specific Workflow Runs
```bash
# Deployment workflow
gh run list --workflow=deploy-static-site.yml

# Testing workflow
gh run list --workflow=test-live-site.yml
```

### Watch Live Workflow Run
```bash
gh run watch
```

### View Workflow Logs
```bash
# Get run ID from list, then:
gh run view <run-id> --log
```

### Cancel Running Workflow
```bash
gh run cancel <run-id>
```

---

## Workflow Status Badges

Add to README.md if desired:

```markdown
[![Deploy Static Site](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/deploy-static-site.yml/badge.svg)](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/deploy-static-site.yml)

[![Test Live Site](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/test-live-site.yml/badge.svg)](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/test-live-site.yml)
```

---

## Typical Workflow Usage

### After Publishing New Content

1. WordPress plugin generates static site
2. Webhook triggers `deploy-static-site.yml`
3. Site is deployed to Cloudflare Pages
4. Manually run `test-live-site.yml` to verify

### Before Major Changes

1. Test current production: `gh workflow run test-live-site.yml`
2. Make changes in WordPress
3. Deploy to staging first
4. Test staging: `gh workflow run test-live-site.yml -f test_url='https://jkcoukblog.pages.dev'`
5. If tests pass, deploy to production

### Regular Maintenance

- Run `test-live-site.yml` weekly to catch issues
- Review warnings even when tests pass
- Check Slack notifications for results

---

## Debugging Workflows

### View Detailed Logs
```bash
gh run view --log
```

### Re-run Failed Jobs
```bash
gh run rerun <run-id>
```

### Re-run Only Failed Jobs
```bash
gh run rerun <run-id> --failed
```

---

## Related Documentation

- `docs/WARP.md` - General project guidance
- `docs/GITHUB_ACTIONS_LIVE_SITE_TESTING.md` - Detailed testing workflow docs
- `docs/LIVE_SITE_FORMATTING_TESTS.md` - What gets tested
- `README.md` - Project overview
