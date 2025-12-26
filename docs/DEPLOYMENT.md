# Deployment Documentation

This document covers deployment options, GitHub Actions workflows, and environment configuration.

## Table of Contents
- [GitHub Actions Workflows](#github-actions-workflows)
- [Deployment Options](#deployment-options)
- [Environment Validation](#environment-validation)
- [Troubleshooting](#troubleshooting)

---

## GitHub Actions Workflows

### Main Deployment Workflow

**File:** `.github/workflows/deploy-static-site.yml`

**Triggers:**
- Manual (`workflow_dispatch`)
- Webhook (`repository_dispatch`)

**Steps:**
1. Setup Python 3.11 and install dependencies
2. Run optional spell check (non-blocking)
3. Generate static site
4. Reuse optimized images from previous builds
5. Optimize images (optipng, jpegoptim) with caching
6. Convert URLs for staging compatibility
7. Submit URLs to IndexNow
8. Commit to `public/` directory
9. Push to repository (triggers Cloudflare Pages auto-deploy)
10. Send Slack notifications

**Required Secrets:**
- `WP_AUTH_TOKEN` - WordPress Basic Auth token
- `SLACK_WEBHOOK_URL` - Optional for notifications
- `OLLAMA_API_CREDENTIALS` - Optional for spell check

**Manual Trigger:**
```bash
gh workflow run deploy-static-site.yml
```

### Live Site Testing Workflow

**File:** `.github/workflows/test-live-site.yml`

**Purpose:** Tests live site (production or staging) for formatting, SEO, and technical standards

**Trigger:** Manual only

**Features:**
- 14 comprehensive tests
- Test production or staging
- Optional post page testing
- Slack notifications
- GitHub Actions summary

**Run via CLI:**
```bash
# Test production
gh workflow run test-live-site.yml

# Test staging
gh workflow run test-live-site.yml -f test_url='https://jkcoukblog.pages.dev'

# Test with specific post
gh workflow run test-live-site.yml -f test_post='https://jameskilby.co.uk/2025/12/post-slug/'
```

---

## Deployment Options

### 1. Cloudflare Pages (Primary)

**Automatic deployment** from Git repository.

**Setup:**
1. Connect Cloudflare Pages to GitHub repository
2. Set build directory: `public/`
3. No build command needed (pre-built)
4. Custom domain: `jameskilby.co.uk`

**Manual deployment:**
```bash
npx wrangler pages publish ./public --project-name=jameskilby-co-uk
```

### 2. Netlify

```bash
# Via netlify.toml configuration
netlify deploy --prod

# Or via CLI
netlify deploy --dir=./public --prod
```

### 3. AWS S3

```bash
aws s3 sync ./public s3://bucket-name/ --delete --cache-control "max-age=86400"
```

### 4. SSH/rsync

```bash
rsync -avz --delete ./public/ user@server:/var/www/html/
```

### 5. Git Repository (Recommended)

```bash
# Handled automatically by GitHub Actions workflow
git add public/
git commit -m "Deploy static site"
git push origin main
```

---

## Environment Validation

### Runner Requirements

**Self-hosted runner needed** for Cloudflare Access authentication.

**Requirements:**
- Python 3.11+
- Git
- Optional: `optipng`, `jpegoptim` for image optimization

### Validation Script

**Test environment:**
```bash
python3 test_runner_env.py
```

**Checks:**
- Python version and path
- Current working directory
- Required Python scripts exist
- Python dependencies (requests, beautifulsoup4)
- Environment variables (WP_AUTH_TOKEN)

**Exit Codes:**
- `0` = All checks passed
- `1` = Some checks failed

### Environment Variables

**Required:**
- `WP_AUTH_TOKEN` - WordPress API authentication token

**Optional:**
- `OLLAMA_API_CREDENTIALS` - Format: `username:password`
- `OLLAMA_URL` - Default: `https://ollama.jameskilby.cloud`
- `OLLAMA_MODEL` - Default: `llama3.1:8b`
- `SINCE_TIMESTAMP` - ISO timestamp for incremental spell checking
- `SLACK_WEBHOOK_URL` - For Slack notifications

**Set environment variable:**
```bash
# For current session
export WP_AUTH_TOKEN="your_token_here"

# Persist in shell profile
echo 'export WP_AUTH_TOKEN="your_token_here"' >> ~/.zshrc
```

---

## Troubleshooting

### Common Issues

**Missing Python Dependencies:**
```bash
pip install requests beautifulsoup4
# or
pip3 install requests beautifulsoup4
```

**Python Command Not Found:**
- Use `python3` instead of `python`
- Verify Python 3.11+ installed: `python3 --version`

**WordPress API Access Issues:**
- Ensure self-hosted runner can access wordpress.jameskilby.cloud
- Verify authentication token: `echo $WP_AUTH_TOKEN`
- Check Cloudflare Access policies

**Environment Variable Issues:**
```bash
# Check if set
echo $WP_AUTH_TOKEN

# Set temporarily
export WP_AUTH_TOKEN="your_token_here"

# Add to shell profile
echo 'export WP_AUTH_TOKEN="your_token_here"' >> ~/.zshrc
source ~/.zshrc
```

**Generation Failures:**
- Review Python dependencies (requests, beautifulsoup4)
- Check disk space for output directory
- Verify network connectivity to WordPress site
- Ensure WP_AUTH_TOKEN is set correctly

**Deployment Issues:**
- Ensure git repository is properly initialized
- Check file permissions: `chmod +x automated_deploy.sh`
- Verify Cloudflare Pages is connected to repository
- Check GitHub Actions secrets are properly configured

### GitHub Actions Debugging

**View workflow logs:**
```bash
gh run list --workflow=deploy-static-site.yml
gh run view <run-id> --log
```

**Re-run failed jobs:**
```bash
gh run rerun <run-id>
gh run rerun <run-id> --failed
```

**Cancel running workflow:**
```bash
gh run cancel <run-id>
```

---

## Related Documentation
- [Main README](../README.md)
- [TESTING.md](TESTING.md)
- [FEATURES.md](FEATURES.md)
- [OPTIMIZATION.md](OPTIMIZATION.md)
