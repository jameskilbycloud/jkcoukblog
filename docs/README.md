# Documentation Hub

Welcome to the jkcoukblog documentation! This site automatically converts a WordPress CMS into a static site with automated deployment, optimization, and monitoring.

## 📚 Documentation Categories

### Start here
- [TODO.md](TODO.md) - **The open-work list** (SEO phases, typo patches, docs)
- [Main README](../README.md) - Project overview, quick start, and architecture
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development environment, commands, and workflow

### Core Features
- [FEATURES.md](FEATURES.md) - Analytics, search, RSS, comments, and theme
- [OPTIMIZATION.md](OPTIMIZATION.md) - Image optimization, lazy loading, DNS prefetch, and performance
- [SEO.md](SEO.md) - IndexNow, rich results, security headers, and SEO improvements

### Deployment & Testing
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deploy workflow, the `site` branch, the Worker, rollback and secrets
- [TESTING.md](TESTING.md) - Live site tests, spell checking, and test procedures

### Reference Documentation
- [CHANGELOG.md](CHANGELOG.md) - How the public /changelog/ page is generated
- [IMAGE_OPTIMIZATION.md](IMAGE_OPTIMIZATION.md) - Image optimization strategy and implementation
- [PAGES_KV_SETUP.md](PAGES_KV_SETUP.md) - Cloudflare KV namespace setup
- [homelab-power-widget.md](homelab-power-widget.md) - Live homelab power-draw widget on /lab/

### Stream Deck Integration
- [STREAMDECK_DEPLOY_SETUP.md](STREAMDECK_DEPLOY_SETUP.md) - Stream Deck deployment setup
- [STREAMDECK_QUICK_REFERENCE.md](STREAMDECK_QUICK_REFERENCE.md) - Quick reference card
- [STREAMDECK_README.md](STREAMDECK_README.md) - Stream Deck overview

### SEO evidence
- [seo/](seo/) - October 2026 SEO recommendations, code review, Search Console insights and link audit (the basis for TODO.md)
- [Style/style-guide.md](Style/style-guide.md) - Blog voice, formatting and visual style

### Archive
- [archive/](archive/) - Superseded audits and recommendations; do not work from them

## 🚀 Quick Links

### Common Tasks

**Build locally** (needs `WP_AUTH_TOKEN` and the Cloudflare Access token, so in practice the self-hosted runner):
```bash
make build          # generate → optimise → validate, all in ./static-output
make deploy-local   # serve ./static-output on :8080
```

**Inspect the live build:**
```bash
make fetch-site                          # site branch → ./public
make deploy-local OUTPUT_DIR=./public
```

**Deploy via GitHub Actions:**
```bash
gh workflow run deploy-static-site.yml
```

**Test Live Site:**
```bash
python3 scripts/test_live_site_formatting.py
```

### Key Scripts

| Script | Purpose |
|--------|---------|
| `wp_to_static_generator.py` | Core static site generator |
| `incremental_builder.py` | BLAKE2b incremental build cache |
| `optimize_images.py` | AVIF/WebP generation (parallel, cached) |
| `test_live_site_formatting.py` | Live site validation tests |
| `ollama_spell_checker.py` | AI-powered spell checker |
| `submit_indexnow.py` | IndexNow search engine submission |

## 📖 Documentation Structure

```
docs/
├── README.md                                  # Documentation hub
├── TODO.md                                    # Open-work list
├── DEVELOPMENT.md                             # Development guide
├── FEATURES.md                                # Feature documentation
├── OPTIMIZATION.md                            # Performance optimization
├── IMAGE_OPTIMIZATION.md                      # Image optimization
├── SEO.md                                     # SEO and search engines
├── DEPLOYMENT.md                              # Deployment and CI/CD
├── TESTING.md                                 # Testing procedures
├── CHANGELOG.md                               # /changelog/ page generator
├── PAGES_KV_SETUP.md                          # Cloudflare KV setup
├── STREAMDECK_DEPLOY_SETUP.md                 # Stream Deck deployment setup
├── STREAMDECK_QUICK_REFERENCE.md              # Stream Deck quick reference
├── STREAMDECK_README.md                       # Stream Deck overview
├── homelab-power-widget.md                    # /lab/ power widget
├── Style/style-guide.md                       # Blog style guide
├── seo/                                       # Current SEO evidence (Oct 2026)
├── seo-audit-2026-06/seo-baseline.json        # Drift baseline (scripts/drift_baseline.py)
└── archive/                                   # Superseded audits and recommendations
```

## 🔗 External Resources

- **Production Site:** [jameskilby.co.uk](https://jameskilby.co.uk)
- **Staging Site:** [jkcoukblog.pages.dev](https://jkcoukblog.pages.dev)
- **WordPress CMS:** wordpress.jameskilby.cloud (private)
- **Analytics:** plausible.jameskilby.cloud
- **GitHub:** [jameskilbycloud/jkcoukblog](https://github.com/jameskilbycloud/jkcoukblog)

## 💡 Contributing

When updating documentation:
1. Update the appropriate consolidated file (FEATURES.md, OPTIMIZATION.md, etc.)
2. Keep cross-references updated
3. Test all commands and examples
4. Update this hub if adding new documentation categories
5. Move implementation-specific or historical docs to archive/ to keep the root clean

## 📝 Documentation Guidelines

- Use clear, concise language
- Include code examples where helpful
- Keep commands up to date
- Link to related documentation
- Update the table of contents when adding sections
