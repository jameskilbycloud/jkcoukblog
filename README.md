# WordPress to Static Site Automation

🚀 **Automated WordPress to Static Site Generator** with spelling corrections, SEO optimizations, and multi-platform deployment.

📚 **[Complete Documentation Hub →](docs/README.md)**

## 🎯 Overview

This repository contains a complete automation solution that:

- ✅ **Connects to WordPress CMS** via REST API (works with Cloudflare Access protected sites)
- ✅ **Generates static site** with all content, assets, and optimizations
- ✅ **Applies spelling corrections** to URLs and content automatically
- ✅ **Creates redirects** for old misspelled URLs
- ✅ **Deploys to multiple platforms** (Cloudflare Pages, Netlify, S3, GitHub Pages)
- ✅ **Runs automatically** via GitHub Actions or cron

## 🏗️ Architecture

```
WordPress CMS (Private) → Static Site Generator → GitHub Repository → Cloudflare Pages (Public)
wordpress.jameskilby.cloud   |                    |                   jameskilby.co.uk
(Behind Cloudflare Access)   |                    |                   (Public Static Site)
                              |                    |
                         Self-Hosted Runner   Auto-Deploy
```

## 📁 Repository Structure

```
├── .github/workflows/
│   ├── deploy-static-site.yml           # Main deployment workflow
│   └── quality-checks.yml               # Live site testing workflow
├── public/                              # Generated static site (deployed by Cloudflare)
├── wp_to_static_generator.py            # Core WordPress to static converter
├── deploy_static_site.py                # Multi-platform deployment tool
├── generate_search_index.py             # Search index generator
├── convert_to_staging.py                # URL converter for staging compatibility
├── test_runner_env.py                   # Environment validation script
├── test_search.py                       # Search functionality tests
├── workers/                             # Cloudflare Workers scripts
├── wrangler.toml                        # Cloudflare Wrangler configuration
├── automated_static_deployment_guide.md # Detailed deployment documentation
├── SEARCH_IMPLEMENTATION.md             # Search functionality documentation
├── PLAUSIBLE_ANALYTICS.md               # Analytics automation documentation
└── README.md                            # This file
```

## 🐍 Python Scripts - Detailed Documentation

### 1. `wp_to_static_generator.py` - Core Static Site Generator

**Purpose:** The main engine that converts a live WordPress site into a static HTML site.

**What it does:**

#### Content Discovery
- Connects to WordPress REST API with authentication
- Discovers all posts, pages, categories, and tags using pagination
- Fetches media library assets (images, videos, documents)
- Supports sites behind Cloudflare Access or other authentication

#### HTML Processing
- Downloads each page and post as HTML
- Parses HTML using BeautifulSoup4
- Replaces all WordPress URLs with target domain URLs
- Processes special URL patterns:
  - Regular links (`<a href>`)
  - Images and srcset for responsive images
  - CSS and JavaScript references
  - Background images in inline styles
  - Font files referenced in CSS

#### Asset Management
- Downloads all CSS stylesheets
- Downloads all JavaScript files
- Downloads all images (including responsive variants)
- Downloads fonts referenced in CSS files
- Handles WordPress cache files (WP-Optimize minified files)
- Processes CSS files to convert absolute URLs to relative paths
- Validates downloaded files to ensure correct content-type

#### Content Transformations
- **Embed Processing:** Converts WordPress embed blocks to proper iframes
  - Acast podcast embeds
  - YouTube video embeds
  - Vimeo video embeds
  - Twitter embeds (converts to links)
  - Generic iframe embeds
- **WordPress Cleanup:** Removes WordPress-specific elements
  - Admin bar
  - WordPress generator meta tags
  - REST API discovery links
  - wp-embed scripts
- **URL Replacements:** Converts all WordPress URLs to static site URLs
  - Main content links
  - Asset URLs (CSS, JS, images)
  - Inline styles and CSS
  - Font URLs in @font-face declarations

#### Static Site Optimizations
- Adds cache control meta tags
- Adds static site generator identification
- Adds preload hints for critical CSS
- Optimizes loading with lazy loading attributes
- **Automatically injects Plausible Analytics** tracking code on every page
  - Ensures analytics is always present even if missing from WordPress
  - Verifies and corrects the `data-domain` attribute
  - Prevents duplicate analytics scripts

#### Additional Features
- **Redirects File:** Creates `_redirects` file for spelling corrections
- **Sitemap Generation:** Creates XML sitemap of all pages
- **Search Index:** Generates JSON search index for client-side search
- **Concurrent Processing:** Uses ThreadPoolExecutor for parallel downloads
- **Error Handling:** Robust error handling with detailed logging

**Usage:**
```bash
export WP_AUTH_TOKEN="your_token_here"
python3 scripts/wp_to_static_generator.py ./output-directory
```

**Key Classes:**
- `WordPressStaticGenerator`: Main class that orchestrates the entire generation process

**Main Methods:**
- `get_all_content_urls()`: Discovers all WordPress content via REST API
- `get_all_media_assets()`: Fetches all media from WordPress Media Library
- `download_and_process_url()`: Downloads and processes a single URL
- `process_html()`: Transforms HTML for static hosting
- `download_assets()`: Downloads all discovered assets
- `generate_static_site()`: Main orchestration method

---

### 2. `deploy_static_site.py` - Multi-Platform Deployment Tool

**Purpose:** Provides deployment capabilities to multiple hosting platforms and local testing.

**What it does:**

#### Deployment Targets
- **Cloudflare Pages:** Deploys using Wrangler CLI
  - Automatic project creation
  - Compatibility date configuration
  - Production deployments
  
- **Netlify:** Deploys using Netlify CLI
  - Site ID support
  - Production deployments
  - Automatic site linking
  
- **AWS S3:** Deploys using AWS CLI
  - Bucket sync with delete flag
  - Cache control headers
  - AWS profile support
  
- **rsync/SSH:** Traditional server deployment
  - SSH key support
  - Incremental transfers
  - Delete mode for old files
  
- **Git Repository:** Commits to repository for auto-deploy
  - Automatic git add, commit, push
  - Timestamped commit messages
  - Cloudflare Pages auto-deployment trigger

#### Additional Features
- **Local Testing Server:** Starts HTTP server for local preview
- **Workflow Generation:** Creates GitHub Actions workflows
- **Cron Script Generation:** Creates automated deployment scripts

**Usage Examples:**
```bash
# Generate static site only
python3 scripts/deploy_static_site.py generate ./static

# Deploy to Cloudflare Pages
python3 scripts/deploy_static_site.py deploy ./static --cloudflare jameskilby-co-uk

# Full generation and deployment
python3 scripts/deploy_static_site.py full ./static --cloudflare jameskilby-co-uk

# Start local test server
python3 scripts/deploy_static_site.py server ./static 8080

# Create GitHub Actions workflow
python3 scripts/deploy_static_site.py setup-github

# Create cron automation script
python3 scripts/deploy_static_site.py setup-cron
```

**Key Classes:**
- `StaticSiteDeployer`: Handles all deployment operations

**Main Methods:**
- `deploy_to_cloudflare_pages()`: Cloudflare deployment
- `deploy_to_netlify()`: Netlify deployment
- `deploy_to_aws_s3()`: S3 deployment
- `deploy_via_rsync()`: SSH/rsync deployment
- `deploy_to_git_repo()`: Git commit and push
- `start_local_server()`: Local HTTP server

---

### 3. `generate_search_index.py` - Search Index Generator

**Purpose:** Creates a searchable JSON index from static HTML files for client-side search functionality.

**What it does:**

#### Content Extraction
- Scans all HTML files in the static site
- Extracts clean text content (removes scripts, styles, nav, footer)
- Parses HTML to extract structured metadata:
  - Page title (cleaned of site name)
  - Meta description
  - Content excerpt (first 150 words if no description)
  - Categories (from category links)
  - Tags (from tag links)
  - Publication date (from time elements)

#### Content Processing
- Cleans up whitespace and formatting
- Limits content length for search performance
- Skips non-content pages (redirects, error pages, short pages)
- Filters out navigation and administrative pages

#### Index Generation
- Creates structured JSON with searchable fields:
  - `title`: Page title
  - `url`: Full URL to the page
  - `description`: Brief description or excerpt
  - `content`: First 1000 characters for full-text search
  - `categories`: Array of categories
  - `tags`: Array of tags
  - `date`: Publication date

#### Output Formats
- **Full version** (`search-index.json`): Pretty-printed for debugging
- **Minified version** (`search-index.min.json`): Compact for production use

**Usage:**
```bash
# Generate search index from static site
python3 scripts/generate_search_index.py ./public

# Specify custom output file and base URL
python3 scripts/generate_search_index.py ./public --output search.json --base-url https://yoursite.com
```

**Key Classes:**
- `SearchIndexGenerator`: Main class for index generation

**Main Methods:**
- `extract_text_content()`: Extracts clean text from HTML
- `extract_metadata()`: Extracts structured metadata
- `process_html_file()`: Processes individual HTML file
- `generate_index()`: Main generation method
- `save_index()`: Saves JSON output

---

### 4. `convert_to_staging.py` - Staging URL Converter

**Purpose:** Converts absolute URLs in a static site to relative URLs for staging deployment.

**What it does:**

#### URL Conversion
- **HTML Files:** Converts absolute URLs to relative paths
  - Converts `https://jameskilby.co.uk/wp-content/` → `/wp-content/`
  - Converts `https://jameskilby.co.uk/` → `/`
  - Works on links, images, scripts, and all HTML elements

- **CSS Files:** Converts URLs in stylesheets
  - Converts WordPress URLs: `https://wordpress.jameskilby.cloud/wp-content/` → `/wp-content/`
  - Converts public URLs: `https://jameskilby.co.uk/wp-content/` → `/wp-content/`
  - Preserves relative URLs and data URIs

#### Processing
- Recursively processes all files in the public directory
- Uses regex patterns for reliable URL replacement
- Reports progress and changes made
- Handles encoding issues gracefully

**Usage:**
```bash
# Convert URLs in public directory
python3 scripts/convert_to_staging.py
```

**Use Case:**
Perfect for staging environments like `jkcoukblog.pages.dev` where absolute URLs would point to production.

---

### 5. `test_runner_env.py` - Environment Validation

**Purpose:** Validates that the self-hosted GitHub runner environment is properly configured.

**What it does:**

#### Environment Checks
- **Python Environment:**
  - Python version
  - Python executable path
  - Current working directory

- **File System:**
  - Lists files in current directory
  - Checks for required Python scripts
  - Verifies GitHub Actions workflow files exist

- **Python Dependencies:**
  - Tests `requests` library import and version
  - Tests `beautifulsoup4` library import and version
  - Reports missing dependencies

- **Environment Variables:**
  - Checks for `WP_AUTH_TOKEN` presence
  - Masks token value for security
  - Warns if not set

#### Output
- Provides clear success/failure indication
- Lists all checks with ✅ or ❌ indicators
- Suggests fixes for missing components

**Usage:**
```bash
# Run environment validation
python3 scripts/test_runner_env.py
```

**Exit Codes:**
- `0`: All checks passed
- `1`: Some checks failed

---

### 6. `test_search.py` - Search Functionality Tests

**Purpose:** Tests the search index generation and validates search functionality.

**What it does:**

#### Search Index Tests
- Validates search index file exists
- Checks JSON structure is valid
- Verifies required fields are present
- Tests search index size and performance
- Validates URLs in search results

#### Search Query Tests
- Tests various search queries
- Validates search results relevance
- Checks fuzzy search functionality
- Tests category and tag filtering

**Usage:**
```bash
# Run search tests
python3 scripts/test_search.py
```

---

## 📋 Prerequisites

Before getting started, ensure you have:

- **Python 3.11+** installed on your system
- **Required Python packages**:
  ```bash
  pip install requests beautifulsoup4
  ```
- **Git** configured with access to your repository
- **Self-hosted GitHub runner** (for Cloudflare Access protected WordPress sites)
- **Environment variable** `WP_AUTH_TOKEN` with your WordPress authentication token

## 🚀 Quick Start

### Option 1: GitHub Actions (Recommended)

1. **Fork this repository** to your GitHub account

2. **Set up a self-hosted GitHub runner** (required for Cloudflare Access):
   ```bash
   # In your repository: Settings → Actions → Runners → New self-hosted runner
   # Follow GitHub's setup instructions for macOS/Linux
   ```

3. **Add repository secrets**:
   - `WP_AUTH_TOKEN`: Your WordPress Basic Auth token
   - (No Cloudflare token needed - Cloudflare auto-deploys from the repo)

4. **Push changes** - The workflow runs automatically twice daily (6 AM & 6 PM UTC)

### Option 2: Manual Generation

```bash
# Set authentication token
export WP_AUTH_TOKEN="your_wordpress_auth_token_here"

# Generate static site
python3 scripts/deploy_static_site.py generate ./static-output

# Test locally
python3 scripts/deploy_static_site.py server ./static-output 8080

# Deploy to repository (triggers Cloudflare auto-deploy)
python3 scripts/deploy_static_site.py deploy ./static-output --git
```

### Option 3: Cron Automation

```bash
# Set authentication token (add to your shell profile for persistence)
export WP_AUTH_TOKEN="your_wordpress_auth_token_here"

# Make script executable
chmod +x automated_deploy.sh

# Add to cron (runs twice daily)
crontab -e
# Add: 0 6,18 * * * /absolute/path/to/automated_deploy.sh
```

## ✨ Features

### 📊 Analytics Automation
- ✅ **Plausible Analytics** automatically injected on every page during publishing
- ✅ **Domain verification** ensures `data-domain` is correctly set to `jameskilby.co.uk`
- ✅ **Duplicate prevention** checks for existing analytics and updates configuration
- ✅ **Privacy-focused** tracking using self-hosted Plausible instance

### 🔤 Spelling Corrections Applied
- ✅ **URLs**: `/warp-the-inteligent-terminal/` → `/warp-the-intelligent-terminal/`
- ✅ **Categories**: "Artificial Inteligence" → "Artificial Intelligence"  
- ✅ **Content**: All spelling errors corrected in posts and pages
- ✅ **Redirects**: `_redirects` file for old URLs (301 redirects)

### 🎛️ Technical Features
- **WordPress REST API integration** - Discovers all content automatically
- **Concurrent processing** - Fast generation with threading
- **Asset management** - Downloads CSS, JS, images with optimization
- **URL replacement** - WordPress URLs → Static site URLs
- **SEO optimization** - Sitemap generation, cache headers, meta tags
- **Clean URLs** - Proper directory structure for static hosting

### 🌐 Deployment Targets
- **Cloudflare Pages** (primary)
- **Netlify**
- **AWS S3**  
- **GitHub Pages**
- **rsync/SSH**
- **Git repository** (auto-deploy via Cloudflare)

## ⚙️ Configuration

### Centralized Configuration File

All URLs and domains are centralized in `config.py`:
- **WordPress URL**: `https://wordpress.jameskilby.cloud`
- **Target Domain**: `https://jameskilby.co.uk`
- **Staging Domain**: `jkcoukblog.pages.dev`
- **Ollama URL**: `https://ollama.jameskilby.cloud`
- **Plausible Analytics**: `plausible.jameskilby.cloud`

To customize for your setup, edit `config.py`. Secrets (tokens, credentials) remain in environment variables and GitHub Secrets.

**Test your configuration:**
```bash
python3 config.py
```

### Environment Variables

The system requires:
- **`WP_AUTH_TOKEN`**: WordPress Basic Auth token (required)

Optional:
- **`OLLAMA_API_CREDENTIALS`**: Ollama authentication (format: `username:password`)
- **`SLACK_WEBHOOK_URL`**: Slack notifications
- **`PLAUSIBLE_SHARE_LINK`**: Plausible Analytics share link

## 📊 Performance

- **Processing**: ~156 URLs in 12 seconds
- **Success rate**: 96% (150/156 URLs)
- **Output size**: ~9.3 MB optimized static site
- **Automation**: Runs completely unattended

## 🔐 Security

- **Private WordPress CMS** behind Cloudflare Access
- **Public static site** with no dynamic vulnerabilities  
- **Self-hosted runner** for secure access to protected WordPress
- **No API keys exposed** in static site

## 📝 Logs & Monitoring

- **GitHub Actions**: Full logs in Actions tab
- **Cron jobs**: Logs to `deploy.log` 
- **Success/failure notifications** in workflow
- **Git commit messages** track each deployment

## 🛠️ Troubleshooting

**Missing Python Dependencies:**
```bash
# Install required packages
pip install requests beautifulsoup4

# Or using pip3 on some systems
pip3 install requests beautifulsoup4
```

**Python Command Not Found:**
- Use `python3` instead of `python` on most modern systems
- Ensure Python 3.11+ is installed: `python3 --version`

**WordPress API Access Issues:**
- Ensure self-hosted runner can access `wordpress.jameskilby.cloud`
- Verify authentication token is valid: `echo $WP_AUTH_TOKEN`
- Check Cloudflare Access policies

**Environment Variable Issues:**
```bash
# Set the token in your current session
export WP_AUTH_TOKEN="your_token_here"

# Or add to your shell profile (~/.zshrc, ~/.bashrc)
echo 'export WP_AUTH_TOKEN="your_token_here"' >> ~/.zshrc
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

## 🤖 GitHub Actions Workflows

### Available Workflows

#### 1. WordPress to Static Site Deploy
**File:** `.github/workflows/deploy-static-site.yml`

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

---

#### 2. Quality Checks (Lighthouse + Formatting Tests)
**File:** `.github/workflows/quality-checks.yml`

**Purpose:** Comprehensive quality monitoring combining Lighthouse performance tests and site formatting validation

**Triggers:**
- Push to main/master (Lighthouse only)
- Pull requests (Lighthouse only)
- Manual trigger (`workflow_dispatch`) - can run both or individually
- Daily schedule at 3 AM UTC (Lighthouse only)

**Jobs:**

##### Lighthouse Performance
- Runs automatically on push/PR and daily
- Tests homepage, category page, recent posts
- Tracks Performance, Accessibility, Best Practices, SEO scores
- Monitors Core Web Vitals (LCP, FCP, CLS, TTI)
- Slack notifications with detailed metrics
- Artifacts available for detailed analysis

##### Site Formatting Tests
- Manual trigger only
- 14 comprehensive formatting tests
- Test production or staging URL
- Optional specific post testing
- Slack notifications
- GitHub Actions summary

**Secrets Required:**
- None (tests public site)
- `SLACK_WEBHOOK_URL` (optional, for notifications)

**How to Run:**

##### Via GitHub UI
1. Go to **Actions** tab
2. Select **Quality Checks**
3. Click **Run workflow**
4. Choose which tests to run:
   - Lighthouse performance: ✅/❌
   - Site formatting: ✅/❌
5. Choose URL to test (formatting)
6. Optionally add post page URL (formatting)

##### Via CLI
```bash
# Run both Lighthouse and formatting tests
gh workflow run quality-checks.yml \
  -f run_lighthouse=true \
  -f run_formatting=true

# Run only Lighthouse
gh workflow run quality-checks.yml \
  -f run_lighthouse=true \
  -f run_formatting=false

# Run only formatting tests on staging
gh workflow run quality-checks.yml \
  -f run_lighthouse=false \
  -f run_formatting=true \
  -f test_url='https://jkcoukblog.pages.dev'

# Test with specific post
gh workflow run quality-checks.yml \
  -f run_formatting=true \
  -f test_post='https://jameskilby.co.uk/2025/12/ubuntu-disk-expansion-steps/'
```

**Documentation:** See `docs/GITHUB_ACTIONS_LIVE_SITE_TESTING.md`

---

### Quick Workflow Commands

#### List Recent Workflow Runs
```bash
gh run list --limit 10
```

#### View Specific Workflow Runs
```bash
# Deployment workflow
gh run list --workflow=deploy-static-site.yml

# Quality checks (Lighthouse + formatting)
gh run list --workflow=quality-checks.yml

# Image optimization
gh run list --workflow=optimize-images.yml
```

#### Watch Live Workflow Run
```bash
gh run watch
```

#### View Workflow Logs
```bash
# Get run ID from list, then:
gh run view <run-id> --log
```

#### Cancel Running Workflow
```bash
gh run cancel <run-id>
```

---

### Typical Workflow Usage

#### After Publishing New Content

1. WordPress plugin generates static site
2. Webhook triggers `deploy-static-site.yml`
3. Site is deployed to Cloudflare Pages
4. Manually run `quality-checks.yml` to verify

#### Before Major Changes

1. Test current production: `gh workflow run quality-checks.yml`
2. Make changes in WordPress
3. Deploy to staging first
4. Test staging: `gh workflow run quality-checks.yml -f test_url='https://jkcoukblog.pages.dev'`
5. If tests pass, deploy to production

#### Regular Maintenance

- Run `quality-checks.yml` weekly to catch issues
- Review warnings even when tests pass
- Check Slack notifications for results

---

### Debugging Workflows

#### View Detailed Logs
```bash
gh run view --log
```

#### Re-run Failed Jobs
```bash
gh run rerun <run-id>
```

#### Re-run Only Failed Jobs
```bash
gh run rerun <run-id> --failed
```

---

### Workflow Status Badges

[![Deploy Static Site](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/deploy-static-site.yml/badge.svg)](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/deploy-static-site.yml)

[![Quality Checks](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/quality-checks.yml/badge.svg)](https://github.com/jameskilbynet/jkcoukblog/actions/workflows/quality-checks.yml)

---

## 🖼️ Image Optimization

**NEW:** Automated image optimization with WebP and AVIF conversion!

- ✅ **Converts images** to modern WebP and AVIF formats
- ✅ **Reduces bandwidth** by 40-50% without quality loss
- ✅ **Updates HTML** with responsive `<picture>` elements
- ✅ **GitHub Actions** workflow for automated optimization
- ✅ **Intelligent caching** to avoid reprocessing

**Quick Start:**
```bash
# Install dependencies
pip install -r requirements-images.txt

# Optimize all images
python3 optimize_images.py ./public

# Or run via GitHub Actions (weekly automatic + manual trigger)
```

**See:** `docs/IMAGE_OPTIMIZATION.md` for complete guide

---

## 📈 Future Enhancements

- [ ] **Webhook integration** for real-time updates
- [x] **Image optimization** and WebP/AVIF conversion ✅ COMPLETED
- [ ] **Advanced SEO features** and schema markup
- [ ] **Multi-language support**
- [ ] **Content validation** and broken link checking

---

## 📚 Related Documentation

- `docs/IMAGE_OPTIMIZATION.md` - **NEW:** Image optimization complete guide
- `docs/WARP.md` - General project guidance
- `docs/GITHUB_ACTIONS_LIVE_SITE_TESTING.md` - Detailed testing workflow docs
- `docs/LIVE_SITE_FORMATTING_TESTS.md` - What gets tested

---

**Generated by WordPress Static Site Automation** - Eliminating manual deployment since 2025! 🎉
