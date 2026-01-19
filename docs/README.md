# Documentation Hub

Welcome to the jkcoukblog documentation! This site automatically converts a WordPress CMS into a static site with automated deployment, optimization, and monitoring.

## 📚 Documentation Categories

### Getting Started
- [Main README](../README.md) - Project overview, quick start, and architecture
- [DEVELOPMENT.md](DEVELOPMENT.md) - Development environment, commands, and workflow

### Core Features
- [FEATURES.md](FEATURES.md) - Analytics, search, RSS, comments, and theme
- [OPTIMIZATION.md](OPTIMIZATION.md) - Image optimization, lazy loading, DNS prefetch, and performance
- [SEO.md](SEO.md) - IndexNow, rich results, security headers, and SEO improvements

### Deployment & Testing
- [DEPLOYMENT.md](DEPLOYMENT.md) - GitHub Actions, deployment guide, and environment setup
- [TESTING.md](TESTING.md) - Live site tests, spell checking, and test procedures

### Reference Documentation
- [CHANGELOG.md](CHANGELOG.md) - Version history and improvements
- [BUILD_AND_DEPLOY_DOCUMENTATION.md](BUILD_AND_DEPLOY_DOCUMENTATION.md) - Comprehensive build and deployment guide
- [IMAGE_OPTIMIZATION.md](IMAGE_OPTIMIZATION.md) - Image optimization strategy and implementation
- [archive/](archive/) - Historical implementation docs and archived guides

## 🚀 Quick Links

### Common Tasks

**Generate Static Site:**
```bash
export WP_AUTH_TOKEN="your_token"
python3 scripts/wp_to_static_generator.py ./public
```

**Test Locally:**
```bash
python3 scripts/deploy_static_site.py server ./public 8080
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
| `deploy_static_site.py` | Multi-platform deployment tool |
| `generate_search_index.py` | Search index generator |
| `test_live_site_formatting.py` | Live site validation tests |
| `ollama_spell_checker.py` | AI-powered spell checker |
| `submit_indexnow.py` | IndexNow search engine submission |

## 📖 Documentation Structure

```
docs/
├── README.md                                  # Documentation hub
├── DEVELOPMENT.md                             # Development guide
├── FEATURES.md                                # Feature documentation
├── OPTIMIZATION.md                            # Performance optimization
├── IMAGE_OPTIMIZATION.md                      # Image optimization
├── SEO.md                                     # SEO and search engines
├── DEPLOYMENT.md                              # Deployment and CI/CD
├── BUILD_AND_DEPLOY_DOCUMENTATION.md          # Build system guide
├── TESTING.md                                 # Testing procedures
├── CHANGELOG.md                               # Version history
└── archive/                                   # Historical implementation docs
    ├── Implementation-specific docs (CLS, CSS, fonts, etc.)
    ├── Build & validation docs (HTML cache, incremental build)
    ├── Mobile optimization docs
    ├── Spell checker implementation history
    └── Feature implementation records
```

## 🔗 External Resources

- **Production Site:** [jameskilby.co.uk](https://jameskilby.co.uk)
- **Staging Site:** [jkcoukblog.pages.dev](https://jkcoukblog.pages.dev)
- **WordPress CMS:** wordpress.jameskilby.cloud (private)
- **Analytics:** plausible.jameskilby.cloud
- **GitHub:** [jameskilbynet/jkcoukblog](https://github.com/jameskilbynet/jkcoukblog)

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
