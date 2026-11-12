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
python3 scripts/wp_to_static_generator.py ./static-output

# Submit URLs to search engines via IndexNow
python3 scripts/submit_indexnow.py ./public
```

### Testing
```bash
# Start local test server (serves ./static-output on :8080; OUTPUT_DIR=./public after `make fetch-site`)
make deploy-local

# Unit tests and lint
make test
make lint

# Test live site formatting and structure
python3 scripts/test_live_site_formatting.py

# Test staging site
python3 scripts/test_live_site_formatting.py --url https://jkcoukblog.pages.dev
```

### Search Index
The search index is built during generation by `scripts/site_artifacts_builder.py` (called from `wp_to_static_generator.py`); there is no separate command.

### URL Conversion
```bash
# Convert absolute URLs to relative (for staging)
python3 scripts/convert_to_staging.py
```

### Spell Checking
```bash
# Check last 3 posts (requires WP_AUTH_TOKEN and OLLAMA_API_CREDENTIALS)
python3 scripts/ollama_spell_checker.py 3

# Check posts modified since timestamp (uses SINCE_TIMESTAMP env var)
python3 scripts/ollama_spell_checker.py
```

### GitHub Actions
```bash
# Manually trigger deployment workflow
gh workflow run deploy-static-site.yml

# View workflow runs
gh run list --workflow=deploy-static-site.yml

# Manually trigger live site testing
gh workflow run quality-checks.yml

# Test staging site
gh workflow run quality-checks.yml -f test_url='https://jkcoukblog.pages.dev'
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

#### site_artifacts_builder.py
**Sitemap, robots.txt and search index**

- Writes `sitemap.xml` (with lastmod and image entries) and `robots.txt`
- Builds the client-side search index from the generated pages
- Called by `wp_to_static_generator.py`; not run on its own

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
WordPress CMS (Private)     →     Static Generator     →     `site` branch   →     Cloudflare Pages (Public)
wordpress.jameskilby.cloud         (Self-Hosted Runner)       (public/ only)          jameskilby.co.uk
(Behind Cloudflare Access)                                                            
```

### Data Flow

1. **Content Discovery**: WordPress REST API → Fetch all posts, pages, categories, tags, media
2. **HTML Processing**: Download pages → BeautifulSoup parsing → URL replacement → Asset extraction
3. **Asset Management**: Concurrent downloads of CSS, JS, images, fonts
4. **Transformations**: Embed processing, WordPress cleanup, analytics injection
5. **Optimization**: AVIF/WebP, CSS, single-pass HTML transform, Brotli/Gzip, URL conversion
6. **Deployment**: force-push `public/` to the `site` branch → Cloudflare Pages auto-deploy (see [DEPLOYMENT.md](DEPLOYMENT.md))

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

### Configuration

All hostnames live in `scripts/config.py` (`Config`). Do not hardcode them elsewhere:
- **WordPress URL**: `https://wordpress.jameskilby.cloud`
- **Target Domain**: `https://jameskilby.co.uk`
- **Staging Domain**: `jkcoukblog.pages.dev`
- **Analytics Domain**: `plausible.jameskilby.cloud`

### GitHub Runner Requirements

- Must be **self-hosted** (not GitHub-hosted) to access WordPress behind Cloudflare Access
- Requires Python 3.11+
- System tools: `jq`, `bc` (the deploy workflow installs either if missing). Image encoding is Pillow, so no image CLIs

### Python Dependencies

```bash
make install-dev   # requirements.txt + requirements-dev.txt
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
- Runs as a separate job after the deploy (so it doesn't compete with the build for the runner)
- Non-blocking: continues on error to avoid failed deployments
- Tracks last check timestamp to only check modified posts
- Uses incremental checking (modified since last run) by default

### Image Optimization
- Reuses already-optimized images from previous builds
- Tracks optimized images with a BLAKE2b hash cache
- Skips re-optimization of unchanged images
- Non-blocking: continues on error

### Deployment Strategy
- The built site is force-pushed as one parentless commit to the `site` branch; `main` never contains `public/`
- Cloudflare Pages' production branch is `site`, so the push is the deploy
- The push is leased to the `site` commit the build started from — a concurrent publish fails the build instead of being overwritten
- `CLOUDFLARE_API_TOKEN` is only needed for the post-deploy steps (KV, cache purge, rollback)

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

### "site branch moved since this build started"
- Something else published to `site` during the build
- Re-run the workflow; it seeds from the newer `site` commit
- Build-cache commits to `main` rebase and retry automatically, and are non-fatal if they still fail

### Image optimization not working
- Check the "Optimize images" step log for the failing file
- Check the "Install dependencies" step: it fails if Pillow can't encode AVIF
- See [IMAGE_OPTIMIZATION.md](IMAGE_OPTIMIZATION.md#troubleshooting)

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
- Build output, gitignored on `main`
- CI publishes it to the `site` branch, which Cloudflare Pages deploys
- `make fetch-site` recreates it locally from `site`

### `/.image_optimization_cache/`
- `optimization_cache.json`: BLAKE2b hashes of optimized images (plus `words_total.json`, the homepage word-count cache)
- Prevents re-optimization of unchanged images
- Tracked in git to persist across workflow runs

### `/.last_spell_check_timestamp`
- ISO timestamp of last spell check
- Used for incremental spell checking
- Gitignored; persisted between runs by the spell-check job's Actions cache

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

- **Size** (2026-11-12 build): 265 HTML pages, ~1,900 source images, 226 MB built output
- **Incremental deploy**: ~10 minutes end to end; a full rebuild is mostly WordPress fetches + image work
- **Concurrent Downloads**: Uses ThreadPoolExecutor for parallel processing
- **Image Optimization**: Pillow → AVIF + WebP (originals served as-is)

---

## Testing

### Manual Testing
```bash
# Generate and test locally
export WP_AUTH_TOKEN="your_token"
python3 scripts/wp_to_static_generator.py ./test-output
python3 -m http.server 8080 --directory ./test-output
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
