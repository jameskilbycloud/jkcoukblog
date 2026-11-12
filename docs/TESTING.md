# Testing Documentation

This document covers all testing procedures and tools.

## Table of Contents
- [Live Site Testing](#live-site-testing)
- [Spell Checking](#spell-checking)
- [UI smoke tests (Playwright)](#ui-smoke-tests-playwright)
- [Unit tests](#unit-tests)

---

## Live Site Testing

### Overview
Automated tests for site formatting, SEO, and technical standards.

### Test Script
`test_live_site_formatting.py`

### Usage

**Test production:**
```bash
python3 scripts/test_live_site_formatting.py
```

**Test staging:**
```bash
python3 scripts/test_live_site_formatting.py --url https://jkcoukblog.pages.dev
```

**Test specific post:**
```bash
python3 scripts/test_live_site_formatting.py --post https://jameskilby.co.uk/2025/12/post-slug/
```

### What Gets Tested (14 Tests)

#### HTML & Structure
- ✅ Valid DOCTYPE and HTML structure
- ✅ All required meta tags (charset, viewport, description)
- ✅ Page title and canonical URLs
- ✅ Structured data (JSON-LD)

#### Analytics & Tracking
- ✅ Plausible Analytics properly configured
- ✅ Correct data-domain attribute
- ✅ No duplicate tracking scripts

#### Comments System
- ✅ Utterances comments widget properly configured
- ✅ Correct GitHub repository linked
- ✅ Theme and issue-term settings present

#### Assets & Resources
- ✅ CSS stylesheets load correctly
- ✅ JavaScript files load correctly
- ✅ Images have alt attributes
- ✅ Responsive images have srcset

#### SEO & Social
- ✅ Open Graph tags (Facebook/LinkedIn)
- ✅ Twitter Card tags
- ✅ Canonical URLs point to correct domain

#### Content Quality
- ✅ Internal links are not broken
- ✅ WordPress-specific elements removed
- ✅ Cache control headers present

### Exit Codes
- **0** = All tests passed ✅
- **1** = Tests failed ❌

### GitHub Actions Integration

**Via CLI:**
```bash
# Test production
gh workflow run quality-checks.yml

# Test staging
gh workflow run quality-checks.yml -f test_url='https://jkcoukblog.pages.dev'
```

---

## Spell Checking

### Overview
AI-powered spell and grammar checking using local Ollama instance before publishing.

### Implementation
Script: `ollama_spell_checker.py`

### Features
- Uses local Ollama instance (llama3.1:8b model)
- Checks WordPress posts via REST API before publishing
- Whitelists technical terms (vmware, kubernetes, etc.)
- Non-blocking in CI/CD pipeline (continues on error)

### Usage

**Check last 3 posts:**
```bash
python3 scripts/ollama_spell_checker.py 3
```

**Check posts modified since timestamp:**
```bash
export SINCE_TIMESTAMP="2025-01-01T00:00:00Z"
python3 scripts/ollama_spell_checker.py
```

**Check all recent posts:**
```bash
python3 scripts/ollama_spell_checker.py
```

### Configuration

**Environment Variables:**
- `WP_AUTH_TOKEN` - WordPress API authentication (required)
- `OLLAMA_API_CREDENTIALS` - Format: `username:password`
- `OLLAMA_URL` - Default: `https://ollama.jameskilby.cloud`
- `OLLAMA_MODEL` - Default: `llama3.1:8b`
- `SINCE_TIMESTAMP` - ISO timestamp for incremental checking

**Technical Term Whitelist:**
The spell checker knows common technical terms:
- vmware, vcenter, esxi
- kubernetes, k8s, docker
- terraform, ansible, packer
- And many more...

### GitHub Actions Integration

Spell checking runs as the `spell-check` job of `deploy-static-site.yml`, after the build (`needs: build-and-deploy`) and `continue-on-error`, so it never affects a deploy. It sets `SINCE_TIMESTAMP` from `.last_spell_check_timestamp` (restored from the `spell-check-` Actions cache), checks posts modified since then (or the last 3 if there's no timestamp), and writes the new timestamp back for the next run.

---

## UI smoke tests (Playwright)

`scripts/test_interactive_ui.py` serves the build locally and drives headless Chromium through the JS-driven UI (mobile drawer, Splide carousel, sticky header, sub-menus). The deploy runs it after compression with `--require-browser`, so a run that can't launch Chromium fails the step instead of skipping silently. The step is `continue-on-error`: a failure is reported in "Report non-blocking step failures" and the Slack warning, and the deploy still goes out.

Playwright is pinned in `requirements-ui.txt` (Dependabot bumps it); the step installs the pin whenever the runner's copy differs, then `playwright install --only-shell chromium`.

**Runner setup (one-off, per runner).** The browser needs shared libraries from apt, which the step can't install (no passwordless sudo). The step names any that are missing. On Ubuntu 26.04:

```bash
sudo apt-get install -y libasound2t64 libatk1.0-0t64 libatk-bridge2.0-0t64 \
  libatspi2.0-0t64 libxcomposite1 libxdamage1 libxfixes3 libxrandr2
```

Do this on both runners (`uk-bhr-ghr-1`, `uk-bhr-p-ghr-2`) — either can pick up a deploy. `sudo python3 -m playwright install-deps` doesn't work here: Playwright is a per-user install under `~/.local`, which root's Python can't import.

Locally:

```bash
pip install -r requirements-ui.txt
python3 -m playwright install --only-shell chromium
python3 scripts/test_interactive_ui.py ./static-output
```

---

## Unit tests

`tests/` holds the pytest suite for the build scripts (`conftest.py` puts `scripts/` on the path):

```bash
make test    # pytest tests/ -v
make lint    # ruff check scripts/ tests/
```

Both run in CI via `python-checks.yml` on changes to `scripts/`, `tests/` or the requirements files. Tests that need the image toolchain (Pillow AVIF) skip when it isn't installed.

The deploy workflow also has a manual-only "Test runner environment" step (runs on `workflow_dispatch`) that prints the runner's Python, tools and paths — there's no separate script for it.

---

## Related Documentation
- [Main README](../README.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [FEATURES.md](FEATURES.md)
- [OPTIMIZATION.md](OPTIMIZATION.md)
