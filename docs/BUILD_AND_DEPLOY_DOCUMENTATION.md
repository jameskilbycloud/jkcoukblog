# Build and Deploy Action Documentation

## Overview

The **`deploy-static-site.yml`** GitHub Actions workflow automates the conversion of a private WordPress CMS into a static website and deploys it to Cloudflare Pages. It runs on a self-hosted Ubuntu runner to access the WordPress instance behind Cloudflare Access.

## Trigger Events

The workflow can be triggered in two ways:

1. **Manual Trigger** (`workflow_dispatch`): Allows manual execution from the GitHub UI
2. **Webhook Trigger** (`repository_dispatch` with type `wordpress-update`): Triggered by external systems (e.g., WordPress plugin) when content changes

## Concurrency Control

- **Group**: `wordpress-static-site-deploy`
- **Cancel In Progress**: False (waits for running jobs to complete before starting new ones)

This prevents concurrent deployments that could cause git conflicts.

## Jobs

### Job 1: Spell Check (Optional, Non-Blocking)

**Runner**: Self-hosted  
**Timeout**: 15 minutes

This job runs spell and grammar checks on modified posts using an AI-powered Ollama instance.

#### Steps:

1. **Validate Required Environment Variables**
   - Checks for `WP_AUTH_TOKEN` (required)
   - Checks for `OLLAMA_API_CREDENTIALS` (required for spell check)
   - Fails if required variables are missing

2. **Checkout Repository**
   - Fetches the full git history (`fetch-depth: 0`)

3. **Restore Spell Check Cache**
   - Restores timestamp from previous runs to enable incremental checking
   - Cache key: `spell-check-{commit-sha}`

4. **Setup Python 3.11**
   - Installs Python 3.11 with pip dependency caching

5. **Install Dependencies**
   - Installs packages from `requirements.txt`

6. **Run Spell Check**
   - **Environment Variables**:
     - `WP_AUTH_TOKEN`: WordPress authentication
     - `OLLAMA_API_CREDENTIALS`: Ollama API authentication
     - `OLLAMA_URL`: `https://ollama.jameskilby.cloud`
     - `OLLAMA_MODEL`: `llama3.1:8b`
   
   - **Process**:
     - Reads timestamp from `.last_spell_check_timestamp` file
     - If timestamp exists: checks only posts modified since that time
     - If no timestamp: checks the last 3 posts
     - Runs `ollama_spell_checker.py` script
     - Saves current timestamp for next run
     - Outputs summary to GitHub Actions UI
   
   - **Non-Blocking**: Continues even if spell check fails (does not fail the workflow)

---

### Job 2: Build and Deploy (Main Job)

**Runner**: Self-hosted  
**Timeout**: 60 minutes

This is the core job that generates the static site and pushes it to the repository.

#### Steps:

##### 1. Validate Required Environment Variables

- **Required**:
  - `WP_AUTH_TOKEN`: WordPress REST API authentication
  
- **Optional** (warns but doesn't fail):
  - `SLACK_WEBHOOK_URL`: Slack notifications
  - `PLAUSIBLE_SHARE_LINK`: Analytics dashboard link

---

##### 2. Checkout Repository

- Fetches the repository with full history (`fetch-depth: 0`)
- Full history needed for accurate git statistics in changelog generation

---

##### 3. Restore Build Cache

- **Cached Paths**:
  - `.image_optimization_cache/`: Prevents re-optimization of unchanged images
  - `.last_spell_check_timestamp`: Persists spell check state

---

##### 4. Setup Python 3.11

- Installs Python 3.11 with pip dependency caching
- Dependencies defined in `requirements.txt`

---

##### 5. Install Dependencies

- Installs Python packages: `requests`, `beautifulsoup4`
- Displays installed package versions

---

##### 6. Test Runner Environment

**Condition**: Only runs on manual triggers (`workflow_dispatch`)

- Validates working directory and file presence
- Checks Python version and executable location
- Verifies required dependencies are importable
- Outputs diagnostic information for troubleshooting

---

##### 7. Generate Static Site

**Timeout**: 30 minutes

- **Command**: `python wp_to_static_generator.py ./static-output`
- **Process**:
  - Connects to WordPress REST API using `WP_AUTH_TOKEN`
  - Discovers all posts, pages, categories, and tags
  - Downloads HTML, CSS, JS, images, and fonts
  - Replaces WordPress URLs with target domain URLs
  - Processes WordPress embeds (Acast, YouTube, Vimeo, Twitter)
  - Injects Plausible Analytics tracking code
  - Generates sitemap and redirects file
  - Uses ThreadPoolExecutor for concurrent processing

- **Output Metrics**:
  - Counts generated HTML files
  - Calculates total site size
  - Reuses already-optimized images from `public/` directory if available
  - Stores metrics in environment variables for later steps

---

##### 8. Optimize Images

**Timeout**: 20 minutes

- **Command**: `python3 optimize_images.py ./static-output --workers 4 --json-output optimization-results.json`
- **Process**:
  - Uses 4 parallel workers for concurrent optimization
  - Detects format type (PNG vs JPEG)
  - Checks cache (`/.image_optimization_cache/`) to skip already-optimized images
  - Applies compression: PNG (optipng -o2), JPEG (jpegoptim --max=85)
  - Calculates space savings in MB
  - Measures optimization time per image

- **Output Metrics** (from `optimization-results.json`):
  - PNG count
  - JPEG count
  - Newly optimized images
  - Cached/skipped images
  - Total space saved in MB
  - Average optimization time in ms

- **Non-Blocking**: Continues if optimization fails, sets default metrics

---

##### 9. Brotli Compress Static Files

**Timeout**: 10 minutes

- **Command**: `python3 brotli_compress.py ./public`
- **Process**:
  - Compresses HTML, CSS, JS, JSON, XML, and SVG files
  - Creates `.br` versions alongside original files
  - Calculates compression ratio and space savings

- **Output Metrics**:
  - Number of compressed files
  - Original size (MB)
  - Compressed size (MB)
  - Space saved (MB)
  - Compression ratio (percentage)

- **Non-Blocking**: Continues if compression fails

---

##### 10. Commit and Push Static Site

**Timeout**: 10 minutes

This is the critical deployment step that updates the git repository and triggers Cloudflare Pages.

**Process**:

1. **Configure Git**
   ```bash
   git config --local user.email "action@github.com"
   git config --local user.name "GitHub Action"
   ```

2. **Sync with Remote**
   - Fetches latest remote state
   - Resets local HEAD to `origin/main` to ensure clean state

3. **Replace Static Content**
   ```bash
   rm -rf public/
   mv ./static-output public/
   ```

4. **Convert URLs for Staging**
   - Runs `convert_to_staging.py` to convert absolute URLs to relative paths
   - Enables staging site (`jkcoukblog.pages.dev`) to work correctly

5. **Generate Changelog Page**
   - Runs `generate_changelog.py` to create changelog documenting all changes
   - Non-blocking if generation fails

6. **Generate Stats Page**
   - Runs `generate_stats_page.py` with Plausible analytics link
   - Pulls analytics data from `PLAUSIBLE_SHARE_LINK` secret
   - Non-blocking if generation fails

7. **Submit to IndexNow**
   - Runs `submit_indexnow.py ./public`
   - Notifies search engines (Bing, Yandex, etc.) about all published pages
   - Uses IndexNow protocol for instant indexing
   - Maintains submission history in `indexnow-submission.json`
   - Non-blocking if submission fails

8. **Commit Changes**
   - Stages all changes: `public/`, `.last_spell_check_timestamp`, `.image_optimization_cache/`, `.indexnow_key`, `indexnow-submission.json`
   - Only commits if changes exist
   - Commit message: `🚀 Auto-update static site - {timestamp}`

9. **Push to Repository**
   - **Primary Push**: `git push origin main`
   - **Fallback Strategies** (if primary fails):
     1. Attempts rebase: `git rebase origin/main`
     2. If rebase succeeds: pushes again
     3. If rebase fails: performs force push with lease
        - Resets to `origin/main`
        - Regenerates static site
        - Force pushes with `--force-with-lease` to resolve all conflicts

10. **Output Summary**
    - Displays commit SHA
    - Shows deployment status
    - Indicates that Cloudflare Pages will auto-deploy

---

##### 11. Notify on Success

**Condition**: Only runs if all previous steps succeed

- Displays console message confirming successful generation and deployment
- Indicates that Cloudflare Pages will auto-deploy from `public/` directory

---

##### 12. Notify Slack on Success

**Condition**: Only runs if all previous steps succeed  
**Action**: Posts rich message to Slack `#web` channel

**Message Contents**:
- Build status: ✅ Success
- HTML pages generated
- Total site size
- Images optimized with count of newly optimized vs cached
- Space saved in MB
- Trigger type (manual or commit)
- Commit message
- Button linking to workflow run

---

##### 13. Notify on Failure

**Condition**: Only runs if any previous step fails

- Displays console error message

---

##### 14. Notify Slack on Failure

**Condition**: Only runs if any previous step fails  
**Action**: Posts error message to Slack `#web` channel

**Message Contents**:
- Build status: ❌ Failed
- Trigger type and user/author
- Branch name
- Commit message
- Button linking to workflow logs for troubleshooting

---

## Deployment Flow

```
WordPress CMS (Private)     Static Generator          GitHub Repository       Cloudflare Pages (Public)
wordpress.jameskilby.cloud  (Self-Hosted Runner)      (main branch)           jameskilby.co.uk
   ↓                              ↓                            ↓                      ↓
[REST API]                  [wp_to_static_generator]  [public/ directory]    [Auto-Deploy on Change]
   ↓                              ↓                            ↓                      ↓
[Content + Assets]          [HTML + CSS + JS]         [Committed Changes]     [Live Site Updated]
```

## Data Flow

1. **Content Discovery**: WordPress REST API → fetch all posts, pages, categories, tags, media
2. **HTML Processing**: Download pages → BeautifulSoup parsing → URL replacement → asset extraction
3. **Asset Management**: Concurrent downloads of CSS, JS, images, fonts
4. **Transformations**: WordPress embed processing, cleanup, analytics injection
5. **Optimization**: Image optimization (optipng/jpegoptim), Brotli compression, URL conversion
6. **Deployment**: Git commit to `public/` → Cloudflare Pages auto-deploy

## Key Configuration

### Environment Variables

**Required**:
- `WP_AUTH_TOKEN`: WordPress Basic Auth token (base64 encoded `username:password`)

**Optional**:
- `OLLAMA_API_CREDENTIALS`: Format `username:password` for Ollama API
- `SLACK_WEBHOOK_URL`: Slack webhook for notifications
- `PLAUSIBLE_SHARE_LINK`: Plausible Analytics share link for stats page

### Static Site URLs (from config.py)

- **WordPress Source**: `https://wordpress.jameskilby.cloud`
- **Target Domain**: `https://jameskilby.co.uk`
- **Staging Domain**: `jkcoukblog.pages.dev`
- **Ollama Instance**: `https://ollama.jameskilby.cloud`
- **Analytics**: `plausible.jameskilby.cloud`

## Error Handling & Robustness

### Non-Blocking Steps

The following steps are non-blocking (failures don't stop deployment):
- Spell check
- Image optimization
- Brotli compression
- Changelog generation
- Stats page generation
- IndexNow submission

This ensures that even if optional features fail, the core static site is still generated and deployed.

### Git Conflict Resolution

The workflow includes sophisticated git conflict handling:
1. **First Attempt**: Simple push
2. **Second Attempt**: Rebase and retry
3. **Final Resolution**: Force push with lease after site regeneration

This prevents failed deployments due to concurrent updates while maintaining data safety.

### Cache Strategy

- **Image Optimization Cache**: Prevents re-optimizing unchanged images
- **Spell Check Cache**: Tracks last check timestamp for incremental checking
- **Build Cache**: Preserves state across workflow runs

## Performance Characteristics

- **Processing Speed**: ~156 URLs in 12 seconds
- **Success Rate**: 96% (150/156 URLs typical)
- **Output Size**: ~9.3 MB optimized static site
- **Concurrent Downloads**: ThreadPoolExecutor for parallel asset downloads
- **Compression**: 4 parallel image optimization workers
- **Timeout Protection**: 60-minute overall timeout, granular timeouts for each step

## Cloudflare Pages Integration

This workflow **does not** directly deploy to Cloudflare Pages. Instead:

1. Changes are committed to the `public/` directory in the repository
2. Cloudflare Pages monitors the GitHub repository
3. When `public/` changes, Cloudflare Pages automatically rebuilds and deploys
4. No Cloudflare API token required (Pages is configured to watch the repo)

This provides:
- **Automatic Deployment**: No manual trigger needed
- **Version Control**: Every deployment tracked in git
- **Rollback Capability**: Previous versions available in git history
- **Preview URLs**: Automatic preview builds for each commit

## Related Files

- `wp_to_static_generator.py`: Core site generation script
- `optimize_images.py`: Image optimization with caching
- `brotli_compress.py`: Brotli compression utility
- `convert_to_staging.py`: URL conversion for staging
- `generate_changelog.py`: Changelog generation
- `generate_stats_page.py`: Analytics stats page generation
- `submit_indexnow.py`: Search engine notification
- `ollama_spell_checker.py`: AI-powered spell checking
- `requirements.txt`: Python dependencies
- `.github/workflows/deploy-static-site.yml`: This workflow definition

## Usage

### Manual Trigger

```bash
gh workflow run deploy-static-site.yml
```

### View Workflow Runs

```bash
gh run list --workflow=deploy-static-site.yml
```

### Check Logs

Visit: `https://github.com/jameskilbynet/jkcoukblog/actions/workflows/deploy-static-site.yml`

## Troubleshooting

### Workflow Hangs

- Check timeout settings (default: 60 minutes overall, 30 minutes for site generation)
- Verify self-hosted runner is healthy and responding

### Authentication Errors (401)

- Verify `WP_AUTH_TOKEN` is set correctly in GitHub Secrets
- Confirm self-hosted runner can access `wordpress.jameskilby.cloud`
- Check Cloudflare Access policies

### Git Push Fails

- Workflow automatically attempts rebase and force push
- Check GitHub Actions logs for conflict details
- Verify runner has push permissions

### Image Optimization Skipped

- Verify `optipng` and `jpegoptim` are installed on runner
- These are optional; optimization continues without them
- Install on Ubuntu: `sudo apt-get install optipng jpegoptim`

### Staging Site Shows Production URLs

- `convert_to_staging.py` converts URLs automatically
- If issues persist, check for hardcoded URLs in content

### Spell Check Failing

- Verify Ollama instance is accessible at `https://ollama.jameskilby.cloud`
- Confirm `OLLAMA_API_CREDENTIALS` is set if Ollama requires authentication
- Spell check is non-blocking; doesn't prevent deployment

## Success Indicators

A successful workflow run shows:

1. ✅ All environment variables validated
2. ✅ Static site generated with HTML page count and total size
3. ✅ Images optimized with space saved reported
4. ✅ Files Brotli compressed with compression ratio reported
5. ✅ Changes committed and pushed to `public/` directory
6. ✅ Slack notification sent with success details
7. ✅ Cloudflare Pages begins auto-deployment

You can verify the live deployment at `https://jameskilby.co.uk`
