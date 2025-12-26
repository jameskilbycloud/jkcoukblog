# Development Documentation

This document provides guidance for developers working on the jkcoukblog static site generator.

## Table of Contents
- [Project Overview](#project-overview)
- [Common Commands](#common-commands)
- [Architecture](#architecture)
- [Configuration](#configuration)
- [Common Issues](#common-issues)
- [Testing](#testing)

---

## Project Overview

Automated WordPress-to-static-site generator and deployment system. Converts private WordPress CMS (`wordpress.jameskilby.cloud`) into a static site deployed at `jameskilby.co.uk` via Cloudflare Pages. Includes spell checking, image optimization, search functionality, and automated deployment through GitHub Actions.

---

## Common Commands

### Site Generation
```bash
# Generate static site (requires WP_AUTH_TOKEN environment variable)
python3 wp_to_static_generator.py ./static-output

# Submit URLs to search engines via IndexNow
python3 submit_indexnow.py ./public
```

### Testing
```bash
# Start local test server
python3 deploy_static_site.py server ./static-output 8080

# Test search functionality
python3 test_search.py

# Test environment configuration (runner validation)
python3 test_runner_env.py

# Test live site formatting and structure
python3 test_live_site_formatting.py

# Test staging site
python3 test_live_site_formatting.py --url https://jkcoukblog.pages.dev
```

### Search Index
```bash
# Generate search index from static site
python3 generate_search_index.py ./public
```

### URL Conversion
```bash
# Convert absolute URLs to relative (for staging)
python3 convert_to_staging.py
```

### Spell Checking
```bash
# Check last 3 posts (requires WP_AUTH_TOKEN and OLLAMA_API_CREDENTIALS)
./ollama_spell_checker.py 3

# Check posts modified since timestamp (uses SINCE_TIMESTAMP env var)
./ollama_spell_checker.py
```

### GitHub Actions
```bash
# Manually trigger deployment workflow
gh workflow run deploy-static-site.yml

# View workflow runs
gh run list --workflow=deploy-static-site.yml

# Manually trigger live site testing
gh workflow run test-live-site.yml

# Test staging site
gh workflow run test-live-site.yml -f test_url='https://jkcoukblog.pages.dev'
```

---

## Architecture

### Core Components

#### wp_to_static_generator.py
**Main static site generator**

- Connects to WordPress REST API with authentication
- Discovers all content (posts, pages, categories, tags) via pagination
- Downloads and processes HTML, CSS, JS, images, and fonts
- Performs URL replacement (WordPress → target domain)
- Processes WordPress embeds (Acast, YouTube, Vimeo, Twitter)
- Injects Plausible Analytics tracking code
- Generates sitemap and redirects file
- Uses concurrent processing (ThreadPoolExecutor) for performance
- **Key class:** `WordPressStaticGenerator`

#### deploy_static_site.py
**Multi-platform deployment tool**

- Supports Cloudflare Pages, Netlify, AWS S3, rsync, and Git deployment
- Provides local HTTP server for testing
- Can generate GitHub Actions workflows and cron scripts
- **Key class:** `StaticSiteDeployer`

#### generate_search_index.py
**Search index generator**

- Extracts clean text from HTML files
- Creates structured JSON with title, description, content, categories, tags
- Outputs both full (`search-index.json`) and minified (`search-index.min.json`) versions
- **Key class:** `SearchIndexGenerator`

#### ollama_spell_checker.py
**AI-powered spell checker**

- Uses local Ollama instance (llama3.1:8b model) for spell/grammar checking
- Checks WordPress posts via REST API before publishing
- Whitelists technical terms (vmware, kubernetes, etc.)
- Non-blocking in CI/CD pipeline (continues on error)
- **Key class:** `OllamaSpellChecker`

#### convert_to_staging.py
**URL converter**

- Converts absolute URLs to relative paths for staging deployment
- Processes both HTML and CSS files
- Enables staging site (`jkcoukblog.pages.dev`) to work correctly

#### submit_indexnow.py
**IndexNow submission tool**

- Submits all pages to search engines (Bing, Yandex, etc.) via IndexNow protocol
- Generates and manages API key for domain verification
- Creates key verification file in site root
- Logs submission history to `indexnow-submission.json`
- **Key class:** `IndexNowSubmitter`

### Deployment Flow

```
WordPress CMS (Private)     →     Static Generator     →     GitHub Repo     →     Cloudflare Pages (Public)
wordpress.jameskilby.cloud         (Self-Hosted Runner)       (public/ dir)           jameskilby.co.uk
(Behind Cloudflare Access)                                                            
```

### Data Flow

1. **Content Discovery**: WordPress REST API → Fetch all posts, pages, categories, tags, media
2. **HTML Processing**: Download pages → BeautifulSoup parsing → URL replacement → Asset extraction
3. **Asset Management**: Concurrent downloads of CSS, JS, images, fonts
4. **Transformations**: Embed processing, WordPress cleanup, analytics injection
5. **Optimization**: Image optimization (optipng/jpegoptim), URL conversion
6. **Deployment**: Git commit → Cloudflare Pages auto-deploy

---

## Configuration

### Environment Variables

**Required:**
- `WP_AUTH_TOKEN` - WordPress Basic Auth token for API access

**Optional:**
- `OLLAMA_API_CREDENTIALS` - Format: `username:password` for Ollama authentication
- `OLLAMA_URL` - Ollama instance URL (default: `https://ollama.jameskilby.cloud`)
- `OLLAMA_MODEL` - Model name (default: `llama3.1:8b`)
- `SINCE_TIMESTAMP` - ISO timestamp for incremental spell checking
- `SLACK_WEBHOOK_URL` - For Slack notifications in GitHub Actions

### Hardcoded Configuration

In `wp_to_static_generator.py` and `deploy_static_site.py`:
- **WordPress URL**: `https://wordpress.jameskilby.cloud`
- **Target Domain**: `https://jameskilby.co.uk`
- **Staging Domain**: `jkcoukblog.pages.dev`
- **Analytics Domain**: `plausible.jameskilby.cloud`

### GitHub Runner Requirements

- Must be **self-hosted** (not GitHub-hosted) to access WordPress behind Cloudflare Access
- Requires Python 3.11+
- Optional but recommended: `optipng` and `jpegoptim` for image optimization

### Python Dependencies

```bash
pip install requests beautifulsoup4
```

---

## Key Design Decisions

### Authentication
- WordPress site is protected by Cloudflare Access
- Uses Basic Auth via `WP_AUTH_TOKEN` environment variable
- Self-hosted runner required to access private WordPress instance

### Asset Management
- All assets downloaded from WordPress domain, not target domain
- CSS files parsed to extract font URLs and other embedded assets
- WordPress cache files (WP-Optimize minified files) detected with regex
- Responsive images (srcset) and background images handled

### URL Replacement
- Replaces WordPress URLs with target domain URLs during generation
- Separate conversion to relative URLs for staging compatibility
- Handles absolute, relative, and WordPress-specific paths

### Spell Checking
- Runs before site generation in CI/CD pipeline
- Non-blocking: continues on error to avoid failed deployments
- Tracks last check timestamp to only check modified posts
- Uses incremental checking (modified since last run) by default

### Image Optimization
- Reuses already-optimized images from previous builds
- Tracks optimized images with MD5 hash cache
- Skips re-optimization of unchanged images
- Non-blocking: continues on error

### Deployment Strategy
- Commits to `public/` directory in repository
- Cloudflare Pages auto-deploys when `public/` changes
- No Cloudflare API token needed (Pages monitors repo)
- Git conflict resolution with automatic retry logic

### Search Implementation
- Client-side search using Fuse.js (no server required)
- Search index generated during static site creation
- Includes title, content, categories, tags, dates
- Fuzzy search for typo tolerance

### Analytics
- Plausible Analytics automatically injected on every page
- Ensures `data-domain` attribute is always correct (`jameskilby.co.uk`)
- Prevents duplicate analytics scripts

---

## Common Issues

### "wp_to_static_generator.py not found" in GitHub Actions
- Workflow may be running in wrong directory
- Check with `pwd` and `ls -la` in workflow steps

### Authentication errors (401)
- Verify `WP_AUTH_TOKEN` is set correctly in GitHub Secrets
- Ensure self-hosted runner can access `wordpress.jameskilby.cloud`
- Check Cloudflare Access policies

### Git push conflicts
- Workflow includes automatic conflict resolution
- First attempts rebase, then falls back to force-with-lease
- Regenerates site if needed to ensure consistency

### Image optimization not working
- Check if `optipng` and `jpegoptim` are installed on runner
- These are optional; workflow continues if not available
- Install on Ubuntu: `sudo apt-get install optipng jpegoptim`

### Staging site shows production URLs
- Run `convert_to_staging.py` after generation to fix
- This is done automatically in GitHub Actions workflow

### Spell checker failures
- Check Ollama instance is accessible at configured URL
- Verify `OLLAMA_API_CREDENTIALS` if authentication required
- Spell check is non-blocking; doesn't prevent deployment

---

## File Structure

### `/public/`
- Generated static site output
- Deployed by Cloudflare Pages
- Not tracked in git until generated

### `/.image_optimization_cache/`
- MD5 hashes of optimized images
- Prevents re-optimization of unchanged images
- Tracked in git to persist across workflow runs

### `/.last_spell_check_timestamp`
- ISO timestamp of last spell check
- Used for incremental spell checking
- Tracked in git to persist state

### `/.indexnow_key`
- UUID-based API key for IndexNow protocol
- Auto-generated on first run
- Tracked in git for persistence across builds

### `/indexnow-submission.json`
- Submission history log (last 30 submissions)
- Contains timestamps, URLs submitted, and response codes
- Used for monitoring and troubleshooting

### `/workers/`
- Cloudflare Workers scripts (if any)
- See `wrangler.toml` for configuration

---

## WordPress-Specific Notes

### Supported Embeds
The generator automatically converts these WordPress embeds to static equivalents:
- Acast podcasts → iframe embeds
- YouTube videos → iframe embeds
- Vimeo videos → iframe embeds
- Twitter embeds → converted to links (X/Twitter)
- Generic iframe embeds → preserved

### WordPress Cleanup
Automatically removes:
- Admin bar elements
- WordPress generator meta tags
- REST API discovery links
- wp-embed scripts
- WordPress-specific navigation elements

### Content Discovery
Uses WordPress REST API endpoints:
- `/wp-json/wp/v2/posts` - Published posts (paginated)
- `/wp-json/wp/v2/pages` - Published pages (paginated)
- `/wp-json/wp/v2/categories` - Category archives
- `/wp-json/wp/v2/tags` - Tag archives
- `/wp-json/wp/v2/media` - Media library assets

---

## Performance Characteristics

- **Processing Speed**: ~156 URLs in 12 seconds
- **Success Rate**: 96% (150/156 URLs typical)
- **Output Size**: ~9.3 MB optimized static site
- **Concurrent Downloads**: Uses ThreadPoolExecutor for parallel processing
- **Image Optimization**: PNG (optipng -o2), JPEG (jpegoptim --max=85)

---

## Testing

### Manual Testing
```bash
# Generate and test locally
export WP_AUTH_TOKEN="your_token"
python3 wp_to_static_generator.py ./test-output
python3 deploy_static_site.py server ./test-output 8080
# Visit http://localhost:8080
```

### CI/CD Testing
- GitHub Actions workflow includes environment validation
- Tests Python dependencies and file structure
- Non-blocking tests (spell check, image optimization) continue on error

---

## Related Documentation
- [Main README](../README.md)
- [FEATURES.md](FEATURES.md)
- [OPTIMIZATION.md](OPTIMIZATION.md)
- [SEO.md](SEO.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [TESTING.md](TESTING.md)
