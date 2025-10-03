# Automated WordPress to Static Site Deployment Guide

## Current Setup Analysis
- **Source**: wordpress.jameskilby.cloud (private WordPress CMS)
- **Target**: jameskilby.co.uk (public static site)
- **Challenge**: Simply Static API requires manual triggers

## Recommended Automated Solutions

### 🚀 OPTION 1: GitHub Actions + WP2Static CLI (Recommended)

**Advantages**: Most reliable, version controlled, fully automated
**Best for**: Your technical background and existing GitHub workflow

#### Implementation:

```yaml
# .github/workflows/static-site-deploy.yml
name: WordPress Static Site Deploy

on:
  schedule:
    - cron: '0 */6 * * *'  # Every 6 hours
  workflow_dispatch:      # Manual trigger
  repository_dispatch:    # Webhook trigger

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout repository
      uses: actions/checkout@v4
      
    - name: Setup Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        
    - name: Install WP2Static CLI
      run: |
        npm install -g @wp2static/wp2static-cli
        # or use wget-based static site generator
        
    - name: Generate static site
      env:
        WP_URL: https://wordpress.jameskilby.cloud
        WP_AUTH: ${{ secrets.WP_AUTH_TOKEN }}
      run: |
        wp2static crawl $WP_URL \
          --auth-token=$WP_AUTH \
          --output-dir=./static \
          --clean-urls \
          --replace-urls
          
    - name: Deploy to production
      env:
        CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      run: |
        # Deploy to Cloudflare Pages
        npx wrangler pages publish ./static \
          --project-name=jameskilby-co-uk \
          --compatibility-date=2023-09-01
```

### 🐳 OPTION 2: Docker + Cron-based Solution

**Advantages**: Self-hosted, full control, resource efficient
**Best for**: Running on your homelab infrastructure

```dockerfile
# Dockerfile
FROM node:18-alpine

RUN apk add --no-cache curl wget

# Install static site generators
RUN npm install -g @wp2static/wp2static-cli httrack

COPY scripts/ /app/scripts/
COPY config/ /app/config/

WORKDIR /app

CMD ["./scripts/generate-and-deploy.sh"]
```

```bash
#!/bin/bash
# scripts/generate-and-deploy.sh

set -e

echo "🚀 Starting automated WordPress to static conversion..."

# Configuration
WP_URL="https://wordpress.jameskilby.cloud"
OUTPUT_DIR="/app/output"
DEPLOY_TARGET="cloudflare"  # or "s3", "netlify", etc.

# Clean previous build
rm -rf $OUTPUT_DIR
mkdir -p $OUTPUT_DIR

# Method 1: WP2Static CLI approach
wp2static crawl $WP_URL \
  --auth-token="$WP_AUTH_TOKEN" \
  --output-dir=$OUTPUT_DIR \
  --clean-urls \
  --replace-urls \
  --exclude="/wp-admin,/wp-content/uploads/private" \
  --include-discovery

# Method 2: Alternative HTTrack approach (more reliable for some setups)
# httrack "$WP_URL" \
#   -O "$OUTPUT_DIR" \
#   -s0 -a \
#   --clean \
#   --replace-external \
#   -F "Mozilla/5.0 (compatible; StaticSiteBot/1.0)" \
#   --connection-per-second=4

# Post-processing
echo "📝 Post-processing static files..."

# Fix any remaining dynamic URLs
find $OUTPUT_DIR -name "*.html" -exec sed -i \
  's|https://wordpress.jameskilby.cloud|https://jameskilby.co.uk|g' {} \;

# Optimize assets
find $OUTPUT_DIR -name "*.css" -exec gzip -k {} \;
find $OUTPUT_DIR -name "*.js" -exec gzip -k {} \;

# Deploy based on target
case $DEPLOY_TARGET in
  "cloudflare")
    echo "☁️ Deploying to Cloudflare Pages..."
    wrangler pages publish $OUTPUT_DIR \
      --project-name=jameskilby-co-uk
    ;;
  "s3")
    echo "📦 Deploying to AWS S3..."
    aws s3 sync $OUTPUT_DIR s3://jameskilby-co-uk/ \
      --delete \
      --cache-control "max-age=86400"
    ;;
  *)
    echo "❌ Unknown deploy target: $DEPLOY_TARGET"
    exit 1
    ;;
esac

echo "✅ Deployment complete!"
```

### ⚡ OPTION 3: Serverless Function Approach

**Advantages**: Event-driven, cost-effective, auto-scaling
**Best for**: Modern cloud-native deployment

```javascript
// netlify/functions/rebuild-site.js or vercel api endpoint
export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  try {
    // Verify webhook signature
    const signature = req.headers['x-wp-signature'];
    // ... verify signature logic

    console.log('🚀 WordPress webhook received, triggering rebuild...');

    // Option A: Trigger GitHub Action
    await fetch('https://api.github.com/repos/your-username/static-site/dispatches', {
      method: 'POST',
      headers: {
        'Authorization': `token ${process.env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json',
      },
      body: JSON.stringify({
        event_type: 'wordpress-update'
      })
    });

    // Option B: Direct static generation
    const staticSite = await generateStaticSite({
      wpUrl: 'https://wordpress.jameskilby.cloud',
      authToken: process.env.WP_AUTH_TOKEN
    });

    // Deploy to CDN
    await deployToCloudflare(staticSite);

    res.status(200).json({ 
      status: 'success', 
      message: 'Static site rebuild triggered' 
    });
    
  } catch (error) {
    console.error('❌ Rebuild failed:', error);
    res.status(500).json({ error: 'Rebuild failed' });
  }
}
```

### 🔧 OPTION 4: Custom Python Solution (Your Tech Stack)

**Advantages**: Full control, Python-based, extensible
**Best for**: Integration with your existing Python tools

```python
#!/usr/bin/env python3
"""
Automated WordPress to Static Site Generator
Custom solution using your existing Python tooling
"""

import os
import sys
import time
import requests
import shutil
from pathlib import Path
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import concurrent.futures
import subprocess

class WordPressStaticGenerator:
    def __init__(self, wp_url, auth_token, output_dir):
        self.wp_url = wp_url.rstrip('/')
        self.auth_token = auth_token
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Basic {auth_token}',
            'User-Agent': 'StaticSiteGenerator/1.0'
        })
        
    def get_all_urls(self):
        """Get all URLs from WordPress REST API"""
        urls = set()
        
        # Get posts
        posts_response = self.session.get(f'{self.wp_url}/wp-json/wp/v2/posts?per_page=100')
        if posts_response.status_code == 200:
            posts = posts_response.json()
            for post in posts:
                urls.add(post['link'].replace(self.wp_url, ''))
        
        # Get pages
        pages_response = self.session.get(f'{self.wp_url}/wp-json/wp/v2/pages?per_page=100')
        if pages_response.status_code == 200:
            pages = pages_response.json()
            for page in pages:
                urls.add(page['link'].replace(self.wp_url, ''))
                
        # Add essential pages
        essential_urls = ['/', '/category/', '/tag/', '/archives/']
        urls.update(essential_urls)
        
        return list(urls)
    
    def download_url(self, url_path):
        """Download a single URL and save as static file"""
        full_url = f'{self.wp_url}{url_path}'
        
        try:
            response = self.session.get(full_url, timeout=30)
            if response.status_code == 200:
                # Determine file path
                if url_path.endswith('/') or url_path == '':
                    file_path = self.output_dir / url_path.strip('/') / 'index.html'
                else:
                    file_path = self.output_dir / url_path.lstrip('/')
                
                # Create directories
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Process HTML content
                if 'text/html' in response.headers.get('content-type', ''):
                    content = self.process_html(response.text)
                else:
                    content = response.content
                
                # Write file
                if isinstance(content, str):
                    file_path.write_text(content, encoding='utf-8')
                else:
                    file_path.write_bytes(content)
                    
                return f"✅ {url_path}"
            else:
                return f"❌ {url_path} ({response.status_code})"
                
        except Exception as e:
            return f"❌ {url_path} (Error: {e})"
    
    def process_html(self, html_content):
        """Process HTML to make it static-friendly"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Replace WordPress URLs with static site URLs
        for tag in soup.find_all(['a', 'link']):
            if tag.get('href'):
                tag['href'] = tag['href'].replace(self.wp_url, 'https://jameskilby.co.uk')
        
        for tag in soup.find_all(['img', 'script']):
            if tag.get('src'):
                tag['src'] = tag['src'].replace(self.wp_url, 'https://jameskilby.co.uk')
        
        # Remove WordPress admin bar and dynamic elements
        for tag in soup.find_all(id='wpadminbar'):
            tag.decompose()
            
        # Add static site optimizations
        self.add_static_optimizations(soup)
        
        return str(soup)
    
    def add_static_optimizations(self, soup):
        """Add static site optimizations"""
        # Add cache headers meta tag
        meta_cache = soup.new_tag('meta')
        meta_cache['http-equiv'] = 'Cache-Control'
        meta_cache['content'] = 'max-age=86400'
        
        if soup.head:
            soup.head.append(meta_cache)
    
    def download_assets(self):
        """Download CSS, JS, images, etc."""
        asset_patterns = [
            '/wp-content/themes/',
            '/wp-content/plugins/', 
            '/wp-content/uploads/'
        ]
        
        print("📁 Downloading assets...")
        
        for pattern in asset_patterns:
            # This would need more sophisticated crawling
            # For now, rely on the HTML processing to catch most assets
            pass
    
    def generate(self):
        """Main generation process"""
        print(f"🚀 Starting static site generation from {self.wp_url}")
        
        # Clean output directory
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)
        
        # Get all URLs
        print("📋 Discovering URLs...")
        urls = self.get_all_urls()
        print(f"Found {len(urls)} URLs to process")
        
        # Download all URLs concurrently
        print("⬇️  Downloading pages...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(self.download_url, urls))
        
        # Print results
        for result in results:
            print(result)
        
        # Download assets
        self.download_assets()
        
        print(f"✅ Static site generated in {self.output_dir}")
        
    def deploy_to_cloudflare(self):
        """Deploy to Cloudflare Pages"""
        print("☁️ Deploying to Cloudflare Pages...")
        
        result = subprocess.run([
            'wrangler', 'pages', 'publish', str(self.output_dir),
            '--project-name=jameskilby-co-uk',
            '--compatibility-date=2023-09-01'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Cloudflare deployment successful!")
        else:
            print(f"❌ Cloudflare deployment failed: {result.stderr}")

def main():
    generator = WordPressStaticGenerator(
        wp_url='https://wordpress.jameskilby.cloud',
        auth_token=os.getenv('WP_AUTH_TOKEN'),  # Use environment variable
        output_dir='./static-output'
    )
    
    generator.generate()
    generator.deploy_to_cloudflare()

if __name__ == "__main__":
    main()
```

## 🎯 Deployment Automation Setup

### Webhook Integration
```python
# Add to WordPress functions.php or use a plugin
function trigger_static_rebuild($post_id) {
    if (wp_is_post_revision($post_id)) return;
    
    $webhook_url = 'https://your-function-endpoint.com/rebuild';
    
    wp_remote_post($webhook_url, array(
        'body' => json_encode(array(
            'action' => 'rebuild',
            'post_id' => $post_id,
            'timestamp' => time()
        )),
        'headers' => array(
            'Content-Type' => 'application/json',
            'X-WP-Signature' => hash_hmac('sha256', $body, WP_WEBHOOK_SECRET)
        )
    ));
}

add_action('save_post', 'trigger_static_rebuild');
add_action('delete_post', 'trigger_static_rebuild');
```

## 📊 Comparison Matrix

| Solution | Setup Complexity | Maintenance | Cost | Reliability | Speed |
|----------|------------------|-------------|------|-------------|-------|
| GitHub Actions | Medium | Low | Free | High | Fast |
| Docker + Cron | High | Medium | Low | High | Medium |
| Serverless | Low | Low | Low | High | Very Fast |
| Custom Python | Medium | Medium | Free | Medium | Fast |

## 🎯 My Recommendation for You

**Primary: GitHub Actions + Custom Python Script**
- Leverages your GitHub workflow
- Uses your Python expertise
- Version controlled and auditable
- Easy to monitor and debug
- Free for public repositories

**Secondary: Docker solution for your homelab**
- Runs on your infrastructure
- Full control over the process
- Can be integrated with your existing homelab monitoring

Would you like me to implement any of these solutions specifically for your setup?