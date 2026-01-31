# Staging Workflow Guide

## Overview

The staging workflow allows you to preview drafts, test theme changes, and validate content before deploying to the live site at jameskilby.co.uk.

## Architecture

```
WordPress CMS
wordpress.jameskilby.cloud
       │
       ├─────────────────┬─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
   Draft Posts      Scheduled Posts   Published Posts
       │                 │                 │
       └─────────────────┴─────────────────┘
                         │
                         ▼
           ┌─────────────────────────────┐
           │  Staging Deployment         │
           │  (--include-drafts)         │
           │  Branch: staging            │
           └─────────────┬───────────────┘
                         │
                         ▼
           ┌─────────────────────────────┐
           │  Cloudflare Pages           │
           │  jkcoukblog.pages.dev       │
           │  🎭 Preview & Test          │
           └─────────────────────────────┘
                         
                         
           After Approval ✅
                         │
                         ▼
           ┌─────────────────────────────┐
           │  Production Deployment      │
           │  (published only)           │
           │  Branch: main               │
           └─────────────┬───────────────┘
                         │
                         ▼
           ┌─────────────────────────────┐
           │  Cloudflare Pages           │
           │  jameskilby.co.uk          │
           │  🚀 Live Site               │
           └─────────────────────────────┘
```

## How It Works

### Staging Branch
- **Purpose**: Deploy drafts and scheduled content for review
- **Branch**: `staging`
- **Output**: `public-staging/` directory
- **URL**: https://jkcoukblog.pages.dev
- **Content**: Drafts + Scheduled + Published posts
- **Trigger**: Manual only (via GitHub Actions)

### Production Branch
- **Purpose**: Deploy live site
- **Branch**: `main`
- **Output**: `public/` directory
- **URL**: https://jameskilby.co.uk
- **Content**: Published posts only
- **Trigger**: Manual or webhook

## Workflow Usage

### 1. Write and Preview Draft Content

```bash
# Write post in WordPress (save as Draft)
# No need to publish yet

# Deploy to staging
gh workflow run deploy-staging-site.yml

# Wait for deployment (2-3 minutes)
# View at https://jkcoukblog.pages.dev
```

### 2. Test Theme Changes

```bash
# Make theme changes in WordPress
# Update CSS, layout, etc.

# Deploy to staging (includes all content)
gh workflow run deploy-staging-site.yml

# Review changes on staging site
# Verify no layout issues, broken images, etc.
```

### 3. Schedule Posts

```bash
# Create post in WordPress
# Set publish date to future
# Status will be "Scheduled"

# Deploy to staging to preview
gh workflow run deploy-staging-site.yml

# Content appears on staging
# Will NOT appear on production until publish date
```

### 4. Deploy to Production

```bash
# After reviewing on staging:
# 1. Publish post in WordPress (Draft → Published)
# 2. Deploy to production

gh workflow run deploy-static-site.yml

# Site goes live at jameskilby.co.uk
```

## Cloudflare Pages Configuration

### Required Setup

1. **Go to Cloudflare Pages Dashboard**
   - Select your `jkcoukblog` project

2. **Configure Branch Deployments**
   - **Production Branch**: `main`
     - Build output: `public/`
     - Production URL: jameskilby.co.uk
   
   - **Preview Branch**: `staging`
     - Build output: `public-staging/`
     - Preview URL: jkcoukblog.pages.dev

3. **Build Settings**
   - Build command: (none - pre-built by GitHub Actions)
   - Build output directory: `public/` for main, `public-staging/` for staging
   - Root directory: `/`

### Branch Configuration in Cloudflare

```
Settings → Builds & deployments → Production branch
  → Set to: main

Settings → Builds & deployments → Preview branches
  → Enable previews for: staging
  → Branch configuration: Automatic
```

## Local Testing

### Test Staging Build Locally

```bash
# Set environment
export WP_AUTH_TOKEN="your_token"

# Generate staging site (includes drafts)
python scripts/wp_to_static_generator.py ./test-staging --include-drafts

# Serve locally
python -m http.server 8000 --directory ./test-staging

# Visit http://localhost:8000
```

### Test Production Build Locally

```bash
# Set environment
export WP_AUTH_TOKEN="your_token"

# Generate production site (published only)
python scripts/wp_to_static_generator.py ./test-production

# Serve locally
python -m http.server 8001 --directory ./test-production

# Visit http://localhost:8001
```

## Post Status Indicators

When running staging builds, you'll see status indicators:

- ✅ **Published** - Live content
- ⏰ **Scheduled** - Future publish date
- 📝 **Draft** - Work in progress

Example output:
```
📝 Status filter: all statuses (drafts + scheduled + published)
   ✅ Post: My Live Article [publish]
   ⏰ Post: Upcoming Post [future]
   📝 Post: Work in Progress [draft]
```

## Common Workflows

### Scenario 1: Preview Single Draft Post

```bash
# 1. Write draft in WordPress
# 2. Deploy to staging
gh workflow run deploy-staging-site.yml

# 3. Review at https://jkcoukblog.pages.dev
# 4. Make edits in WordPress
# 5. Re-deploy to staging (as many times as needed)
# 6. When satisfied, publish in WordPress
# 7. Deploy to production
gh workflow run deploy-static-site.yml
```

### Scenario 2: Test Major Theme Changes

```bash
# 1. Update theme/CSS in WordPress
# 2. Create test draft posts with various content types
# 3. Deploy to staging
gh workflow run deploy-staging-site.yml

# 4. Test on staging:
#    - Check all post types
#    - Test responsive design
#    - Verify images load
#    - Test navigation
# 5. If issues found, fix in WordPress and re-deploy staging
# 6. When approved, deploy to production
gh workflow run deploy-static-site.yml
```

### Scenario 3: Content Calendar with Scheduled Posts

```bash
# 1. Write multiple posts in WordPress
# 2. Set future publish dates (Status: Scheduled)
# 3. Deploy to staging to preview all upcoming content
gh workflow run deploy-staging-site.yml

# 4. Review scheduled posts on staging
# 5. Make any final edits
# 6. When publish date arrives, WordPress status auto-changes
# 7. Deploy to production to publish
gh workflow run deploy-static-site.yml
```

## Differences Between Staging and Production

| Feature | Staging | Production |
|---------|---------|------------|
| **Branch** | `staging` | `main` |
| **Output Dir** | `public-staging/` | `public/` |
| **URL** | jkcoukblog.pages.dev | jameskilby.co.uk |
| **Content** | Drafts + Scheduled + Published | Published only |
| **Purpose** | Preview & testing | Live site |
| **Workflow** | `deploy-staging-site.yml` | `deploy-static-site.yml` |
| **Generator Flag** | `--include-drafts` | (none) |
| **Optimizations** | Minimal (faster builds) | Full (images, CSS, Brotli) |
| **Search Engines** | Not indexed | Indexed |

## Troubleshooting

### Staging site shows 404

**Cause**: Cloudflare Pages not configured for staging branch

**Solution**:
1. Go to Cloudflare Pages dashboard
2. Settings → Builds & deployments
3. Enable preview deployments for `staging` branch

### Draft posts not appearing on staging

**Cause**: `--include-drafts` flag not used

**Solution**: Check `deploy-staging-site.yml` line 69 includes `--include-drafts`

### Staging and production have same content

**Cause**: Both using same branch or flag

**Solution**: 
- Staging should use `staging` branch + `--include-drafts`
- Production should use `main` branch without flag

### Staging site using wrong URL

**Cause**: URL conversion not working

**Solution**: Check `convert_to_staging.py` is running in workflow

## Best Practices

### ✅ Do

- Deploy to staging before production
- Test all drafts on staging first
- Use staging to validate theme changes
- Review scheduled posts before their publish date
- Test images, links, and formatting on staging

### ❌ Don't

- Skip staging for major changes
- Deploy drafts directly to production
- Assume staging matches production exactly
- Forget to publish drafts before deploying to production
- Use production for testing

## Security Notes

- Staging site (jkcoukblog.pages.dev) is **publicly accessible**
- Do NOT put sensitive information in drafts
- Drafts are visible to anyone who knows the staging URL
- Consider adding Cloudflare Access to staging if needed

## Automation Ideas

### Webhook Trigger for Staging

Currently staging is manual-only. You could add automation:

```yaml
on:
  workflow_dispatch:
  repository_dispatch:
    types: [wordpress-draft-update]  # Trigger from WordPress
```

### Scheduled Staging Deploys

Deploy staging daily to preview scheduled content:

```yaml
on:
  schedule:
    - cron: '0 9 * * *'  # Daily at 9am UTC
```

## Monitoring

### Check Deployment Status

```bash
# View staging deployments
gh run list --workflow=deploy-staging-site.yml

# View production deployments  
gh run list --workflow=deploy-static-site.yml

# Watch specific run
gh run watch <run_id>
```

### Cloudflare Pages Dashboard

Monitor at: https://dash.cloudflare.com/
- View deployment history
- Check build logs
- Monitor traffic/bandwidth

## Related Documentation

- `WARP.md` - Project overview and commands
- `README.md` - Full project documentation
- `.github/workflows/deploy-staging-site.yml` - Staging workflow config
- `.github/workflows/deploy-static-site.yml` - Production workflow config
- `scripts/wp_to_static_generator.py` - Static site generator

## Support

Issues? Check:
1. GitHub Actions logs for errors
2. Cloudflare Pages deployment logs
3. WordPress post status (draft vs published)
4. Branch configuration in Cloudflare
