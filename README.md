# WordPress to Static Site Automation

🚀 **Automated WordPress to Static Site Generator** with spelling corrections, SEO optimizations, and multi-platform deployment.

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
│   └── deploy-static-site.yml    # GitHub Actions automation
├── public/                       # Generated static site (deployed by Cloudflare)
├── wp_to_static_generator.py     # Core WordPress to static converter
├── deploy_static_site.py         # Multi-platform deployment tool
├── automated_deploy.sh           # Cron-based automation script
└── README.md                     # This file
```

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
# Generate static site
python deploy_static_site.py generate ./static-output

# Test locally
python deploy_static_site.py server ./static-output 8080

# Deploy to repository (triggers Cloudflare auto-deploy)
python deploy_static_site.py deploy ./static-output --git public
```

### Option 3: Cron Automation

```bash
# Make script executable
chmod +x automated_deploy.sh

# Add to cron (runs twice daily)
crontab -e
# Add: 0 6,18 * * * /path/to/automated_deploy.sh
```

## ✨ Features

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

The system is pre-configured for:
- **Source**: `wordpress.jameskilby.cloud` (Cloudflare Access protected)
- **Target**: `jameskilby.co.uk` (public static site)
- **Auth**: Basic authentication with hardcoded token

To customize for your setup, edit the configuration section in the Python scripts.

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

**WordPress API Access Issues:**
- Ensure self-hosted runner can access `wordpress.jameskilby.cloud`
- Verify authentication token is valid
- Check Cloudflare Access policies

**Generation Failures:**
- Review Python dependencies (requests, beautifulsoup4)
- Check disk space for output directory
- Verify network connectivity

**Deployment Issues:**  
- Ensure git repository is properly initialized
- Check file permissions for automated_deploy.sh
- Verify Cloudflare Pages is connected to repository

## 📈 Future Enhancements

- [ ] **Webhook integration** for real-time updates
- [ ] **Image optimization** and WebP conversion  
- [ ] **Advanced SEO features** and schema markup
- [ ] **Multi-language support**
- [ ] **Content validation** and broken link checking

---

**Generated by WordPress Static Site Automation** - Eliminating manual deployment since 2025! 🎉