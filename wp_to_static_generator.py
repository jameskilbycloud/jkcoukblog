#!/usr/bin/env python3
"""
WordPress to Static Site Generator
A complete solution for converting your WordPress CMS to a static site
"""

import os
import sys
import time
import requests
import shutil
import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse, urlunparse
from bs4 import BeautifulSoup
import concurrent.futures
from datetime import datetime

class WordPressStaticGenerator:
    def __init__(self, wp_url, auth_token, output_dir, target_domain):
        self.wp_url = wp_url.rstrip('/')
        self.auth_token = auth_token
        self.output_dir = Path(output_dir)
        self.target_domain = target_domain.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Basic {auth_token}',
            'User-Agent': 'StaticSiteGenerator/1.0'
        })
        self.downloaded_assets = set()
        self.processed_urls = set()
        
    def get_all_content_urls(self):
        """Get all content URLs from WordPress REST API"""
        urls = set()
        
        print("📋 Discovering content from WordPress REST API...")
        
        # Get posts with pagination
        page = 1
        while True:
            posts_response = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/posts',
                params={'per_page': 100, 'page': page, 'status': 'publish'}
            )
            if posts_response.status_code != 200:
                break
                
            posts = posts_response.json()
            if not posts:
                break
                
            for post in posts:
                # Convert WordPress URL to relative path
                relative_url = post['link'].replace(self.wp_url, '')
                urls.add(relative_url)
                print(f"   📄 Post: {post['title']['rendered']}")
            
            page += 1
        
        # Get pages
        page = 1
        while True:
            pages_response = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/pages',
                params={'per_page': 100, 'page': page, 'status': 'publish'}
            )
            if pages_response.status_code != 200:
                break
                
            pages = pages_response.json()
            if not pages:
                break
                
            for page_item in pages:
                relative_url = page_item['link'].replace(self.wp_url, '')
                urls.add(relative_url)
                print(f"   📑 Page: {page_item['title']['rendered']}")
            
            page += 1
        
        # Get categories
        categories_response = self.session.get(f'{self.wp_url}/wp-json/wp/v2/categories?per_page=100')
        if categories_response.status_code == 200:
            categories = categories_response.json()
            for category in categories:
                if category['count'] > 0:  # Only categories with posts
                    relative_url = category['link'].replace(self.wp_url, '')
                    urls.add(relative_url)
                    print(f"   📁 Category: {category['name']}")
        
        # Get tags with posts
        tags_response = self.session.get(f'{self.wp_url}/wp-json/wp/v2/tags?per_page=100')
        if tags_response.status_code == 200:
            tags = tags_response.json()
            for tag in tags:
                if tag['count'] > 0:  # Only tags with posts
                    relative_url = tag['link'].replace(self.wp_url, '')
                    urls.add(relative_url)
                    print(f"   🏷️  Tag: {tag['name']}")
        
        # Add essential pages
        essential_urls = ['/', '/category/', '/tag/']
        urls.update(essential_urls)
        
        print(f"✅ Found {len(urls)} URLs to process")
        return sorted(list(urls))
    
    def get_all_media_assets(self):
        """Get all media assets from WordPress Media API"""
        print("🖼️  Discovering media assets from WordPress Media API...")
        media_assets = set()
        
        page = 1
        while True:
            media_response = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/media',
                params={'per_page': 100, 'page': page}
            )
            if media_response.status_code != 200:
                break
                
            media_items = media_response.json()
            if not media_items:
                break
                
            for media_item in media_items:
                # Get the main media URL
                if 'source_url' in media_item:
                    media_assets.add(media_item['source_url'])
                
                # Get different size variants if available
                if 'media_details' in media_item and 'sizes' in media_item['media_details']:
                    sizes = media_item['media_details']['sizes']
                    for size_name, size_data in sizes.items():
                        if 'source_url' in size_data:
                            media_assets.add(size_data['source_url'])
                
                print(f"   🖼️  Media: {media_item.get('title', {}).get('rendered', 'Untitled')}")
            
            page += 1
        
        # Add media assets to downloaded_assets set
        self.downloaded_assets.update(media_assets)
        print(f"✅ Found {len(media_assets)} media assets")
        return media_assets
    
    def download_and_process_url(self, url_path):
        """Download a single URL and process it for static hosting"""
        if url_path in self.processed_urls:
            return f"⏭️  {url_path} (already processed)"
            
        full_url = f'{self.wp_url}{url_path}'
        
        try:
            response = self.session.get(full_url, timeout=30)
            
            if response.status_code == 200:
                # Determine output file path
                if url_path == '' or url_path == '/':
                    file_path = self.output_dir / 'index.html'
                elif url_path.endswith('/'):
                    file_path = self.output_dir / url_path.strip('/') / 'index.html'
                else:
                    # Handle clean URLs
                    file_path = self.output_dir / url_path.lstrip('/') / 'index.html'
                
                # Create directories
                file_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Process content based on type
                content_type = response.headers.get('content-type', '').lower()
                
                if 'text/html' in content_type:
                    processed_content = self.process_html(response.text, url_path)
                    file_path.write_text(processed_content, encoding='utf-8')
                else:
                    # Binary content (images, etc.)
                    file_path.write_bytes(response.content)
                
                self.processed_urls.add(url_path)
                return f"✅ {url_path}"
                
            elif response.status_code == 404:
                return f"⚠️  {url_path} (404 - skipped)"
            else:
                return f"❌ {url_path} ({response.status_code})"
                
        except requests.exceptions.Timeout:
            return f"⏱️  {url_path} (timeout)"
        except Exception as e:
            return f"❌ {url_path} (Error: {str(e)[:50]})"
    
    def process_html(self, html_content, current_url):
        """Process HTML content for static site compatibility"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Replace all WordPress URLs with target domain URLs
        self.replace_urls_in_soup(soup)
        
        # Remove WordPress-specific elements
        self.remove_wordpress_elements(soup)
        
        # Add static site optimizations
        self.add_static_optimizations(soup)
        
        # Extract and queue assets for download
        self.extract_assets(soup, current_url)
        
        return str(soup)
    
    def replace_urls_in_soup(self, soup):
        """Replace WordPress URLs with target domain URLs"""
        url_attributes = {
            'a': ['href'],
            'link': ['href'],
            'img': ['src', 'srcset'],
            'script': ['src'],
            'source': ['src', 'srcset'],
            'iframe': ['src'],
            'form': ['action']
        }
        
        for tag_name, attributes in url_attributes.items():
            for tag in soup.find_all(tag_name):
                for attr in attributes:
                    if tag.get(attr):
                        original_url = tag[attr]
                        
                        # Handle srcset specially (multiple URLs)
                        if attr == 'srcset':
                            new_srcset = []
                            for srcset_item in original_url.split(','):
                                item = srcset_item.strip()
                                if item:
                                    parts = item.split(' ')
                                    if parts[0].startswith(self.wp_url):
                                        parts[0] = parts[0].replace(self.wp_url, self.target_domain)
                                    new_srcset.append(' '.join(parts))
                            tag[attr] = ', '.join(new_srcset)
                        else:
                            # Regular URL replacement
                            if original_url.startswith(self.wp_url):
                                tag[attr] = original_url.replace(self.wp_url, self.target_domain)
                            elif original_url.startswith('/') and not original_url.startswith('//'):
                                # Relative URLs - make them absolute with target domain
                                tag[attr] = self.target_domain + original_url
    
    def remove_wordpress_elements(self, soup):
        """Remove WordPress-specific dynamic elements"""
        # Remove admin bar
        for element in soup.find_all(id='wpadminbar'):
            element.decompose()
        
        # Remove wp-embed scripts
        for script in soup.find_all('script'):
            if script.get('src') and 'wp-embed' in script.get('src'):
                script.decompose()
        
        # Remove WordPress generator meta tag
        for meta in soup.find_all('meta', attrs={'name': 'generator'}):
            if 'wordpress' in meta.get('content', '').lower():
                meta.decompose()
        
        # Remove WordPress REST API links
        for link in soup.find_all('link', rel='https://api.w.org/'):
            link.decompose()
    
    def add_static_optimizations(self, soup):
        """Add optimizations for static site performance"""
        if not soup.head:
            return
            
        # Add cache control meta tag
        cache_meta = soup.new_tag('meta')
        cache_meta['http-equiv'] = 'Cache-Control'
        cache_meta['content'] = 'max-age=86400'
        soup.head.append(cache_meta)
        
        # Add static site generator meta tag
        generator_meta = soup.new_tag('meta')
        generator_meta['name'] = 'generator'
        generator_meta['content'] = 'WordPress Static Generator 1.0'
        soup.head.append(generator_meta)
        
        # Add preload hints for critical resources
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                preload = soup.new_tag('link')
                preload['rel'] = 'preload'
                preload['as'] = 'style'
                preload['href'] = link['href']
                soup.head.insert(0, preload)
    
    def extract_assets(self, soup, current_url):
        """Extract asset URLs for later download"""
        # Enhanced asset selectors including WordPress-specific patterns
        asset_selectors = [
            ('img', 'src'),
            ('img', 'data-src'),  # Lazy loading images
            ('link[rel="stylesheet"]', 'href'),
            ('script[src]', 'src'),
            ('source', 'src'),
            ('source', 'srcset'),
            ('video', 'src'),
            ('video', 'poster'),
            ('audio', 'src')
        ]
        
        for selector, attr in asset_selectors:
            for element in soup.select(selector):
                asset_url = element.get(attr)
                if asset_url:
                    # Handle both WordPress URL and relative URLs
                    if asset_url.startswith(self.wp_url):
                        self.downloaded_assets.add(asset_url)
                    elif asset_url.startswith('/wp-content/'):
                        # WordPress media URLs that might be relative
                        full_url = self.wp_url + asset_url
                        self.downloaded_assets.add(full_url)
                        print(f"   🔍 Found asset: {asset_url} -> {full_url}")
                    elif asset_url.startswith('/wp-includes/'):
                        # WordPress core files
                        full_url = self.wp_url + asset_url
                        self.downloaded_assets.add(full_url)
                        print(f"   🔍 Found core asset: {asset_url} -> {full_url}")
        
        # Extract srcset URLs (multiple images for responsive design)
        for img in soup.find_all('img', srcset=True):
            srcset = img.get('srcset', '')
            for srcset_item in srcset.split(','):
                item = srcset_item.strip()
                if item:
                    url = item.split(' ')[0]  # Get URL part (before size descriptor)
                    if url.startswith(self.wp_url):
                        self.downloaded_assets.add(url)
                    elif url.startswith('/wp-content/'):
                        full_url = self.wp_url + url
                        self.downloaded_assets.add(full_url)
        
        # Extract background images from inline styles
        for element in soup.find_all(style=True):
            style = element.get('style', '')
            # Look for background-image URLs
            import re
            bg_urls = re.findall(r'background-image:\s*url\(["\']?([^"\')]+)["\']?\)', style)
            for bg_url in bg_urls:
                if bg_url.startswith(self.wp_url):
                    self.downloaded_assets.add(bg_url)
                elif bg_url.startswith('/wp-content/') or bg_url.startswith('/wp-includes/'):
                    full_url = self.wp_url + bg_url
                    self.downloaded_assets.add(full_url)
        
        # Parse CSS files referenced and queue their font files if they contain font URLs
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if href:
                css_url = href if href.startswith('http') else self.wp_url + href
                try:
                    css_resp = self.session.get(css_url, timeout=15)
                    if css_resp.status_code == 200:
                        css_text = css_resp.text
                        # Find font URLs and other assets inside CSS
                        font_urls = re.findall(r'url\(([^)]+)\)', css_text)
                        for url in font_urls:
                            clean_url = url.strip('"\'')
                            if clean_url.startswith('data:'):
                                continue
                            if clean_url.startswith('http'):
                                if clean_url.startswith(self.wp_url):
                                    self.downloaded_assets.add(clean_url)
                            elif clean_url.startswith('/'):
                                self.downloaded_assets.add(self.wp_url + clean_url)
                except Exception:
                    pass
    
    def download_assets(self):
        """Download all discovered assets"""
        if not self.downloaded_assets:
            print("   ⚠️  No assets discovered to download")
            return
            
        print(f"📁 Downloading {len(self.downloaded_assets)} assets...")
        
        def download_single_asset(asset_url):
            try:
                # Convert to relative path
                relative_path = asset_url.replace(self.wp_url, '').lstrip('/')
                output_path = self.output_dir / relative_path
                
                # Skip if already downloaded
                if output_path.exists():
                    return f"⏭️  {relative_path} (exists)"
                
                # Create directory
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Download with proper headers
                response = self.session.get(asset_url, timeout=30, stream=True)
                if response.status_code == 200:
                    # Special handling for CSS files - need to process URLs
                    if asset_url.endswith('.css'):
                        css_content = response.text
                        # Convert absolute WordPress URLs to relative URLs
                        css_content = css_content.replace(self.wp_url + '/wp-content/', '/wp-content/')
                        css_content = css_content.replace(self.wp_url + '/wp-includes/', '/wp-includes/')
                        # Also convert the target domain URLs to relative
                        if self.target_domain:
                            css_content = css_content.replace(self.target_domain + '/wp-content/', '/wp-content/')
                            css_content = css_content.replace(self.target_domain + '/wp-includes/', '/wp-includes/')
                        output_path.write_text(css_content, encoding='utf-8')
                    else:
                        # Write in chunks for large files
                        with open(output_path, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                    
                    # Get file size for reporting
                    file_size = output_path.stat().st_size
                    size_mb = file_size / 1024 / 1024
                    if size_mb > 1:
                        return f"✅ {relative_path} ({size_mb:.1f}MB)"
                    else:
                        return f"✅ {relative_path} ({file_size/1024:.1f}KB)"
                else:
                    return f"❌ {relative_path} ({response.status_code})"
                    
            except Exception as e:
                return f"❌ {relative_path} (Error: {str(e)[:50]})"
        
        # Download assets concurrently
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(download_single_asset, self.downloaded_assets))
        
        # Count and categorize results
        success_results = [r for r in results if r.startswith('✅')]
        error_results = [r for r in results if r.startswith('❌')]
        skipped_results = [r for r in results if r.startswith('⏭️')]
        
        print(f"   ✅ Downloaded: {len(success_results)}")
        print(f"   ⏭️  Skipped: {len(skipped_results)}")
        print(f"   ❌ Failed: {len(error_results)}")
        
        # Show some example results
        if success_results:
            print(f"   Recent downloads:")
            for result in success_results[:5]:
                print(f"     {result}")
        
        if error_results:
            print(f"   ⚠️  Some download errors:")
            for result in error_results[:3]:
                print(f"     {result}")
    
    def create_redirects_file(self):
        """Create redirects for old URLs (Netlify/Cloudflare format)"""
        redirects_content = [
            "# Automatic redirects for spelling corrections",
            "/2025/04/warp-the-inteligent-terminal/ /2025/04/warp-the-intelligent-terminal/ 301",
            "/category/artificial-inteligence/ /category/artificial-intelligence/ 301"
        ]
        
        redirects_file = self.output_dir / '_redirects'
        redirects_file.write_text('\n'.join(redirects_content))
        print("✅ Created _redirects file for URL corrections")
    
    def create_sitemap(self):
        """Generate a basic XML sitemap"""
        urls_for_sitemap = []
        
        # Collect all HTML files
        for html_file in self.output_dir.rglob('*.html'):
            relative_path = html_file.relative_to(self.output_dir)
            if relative_path.name == 'index.html':
                if relative_path.parent == Path('.'):
                    url_path = '/'
                else:
                    url_path = f'/{relative_path.parent}/'
            else:
                url_path = f'/{relative_path.with_suffix("")}/'
            
            urls_for_sitemap.append(f'{self.target_domain}{url_path}')
        
        # Generate XML
        sitemap_content = ['<?xml version="1.0" encoding="UTF-8"?>']
        sitemap_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
        
        for url in sorted(set(urls_for_sitemap)):
            sitemap_content.append('  <url>')
            sitemap_content.append(f'    <loc>{url}</loc>')
            sitemap_content.append(f'    <lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod>')
            sitemap_content.append('  </url>')
        
        sitemap_content.append('</urlset>')
        
        sitemap_file = self.output_dir / 'sitemap.xml'
        sitemap_file.write_text('\n'.join(sitemap_content))
        print(f"✅ Created sitemap.xml with {len(urls_for_sitemap)} URLs")
    
    def generate_static_site(self):
        """Main generation process"""
        print(f"🚀 WordPress to Static Site Generator")
        print(f"Source: {self.wp_url}")
        print(f"Target: {self.target_domain}")
        print(f"Output: {self.output_dir}")
        print("=" * 60)
        
        start_time = time.time()
        
        # Clean output directory
        if self.output_dir.exists():
            print("🗑️  Cleaning output directory...")
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True)
        
        # Get all URLs from WordPress
        urls = self.get_all_content_urls()
        
        # Discover all media assets via WordPress API
        print(f"\\n🖼️  Media Asset Discovery:")
        media_assets = self.get_all_media_assets()
        
        # Download and process all content
        print(f"\\n⬇️  Processing {len(urls)} URLs...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(self.download_and_process_url, urls))
        
        # Print results summary
        success_count = len([r for r in results if r.startswith('✅')])
        print(f"\\n📊 Processing Results:")
        print(f"   ✅ Success: {success_count}")
        print(f"   ❌ Failed: {len(results) - success_count}")
        
        # Download assets
        print(f"\\n📁 Asset Processing:")
        self.download_assets()
        
        # Create additional files
        print(f"\\n📄 Creating additional files:")
        self.create_redirects_file()
        self.create_sitemap()
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\\n🎉 GENERATION COMPLETE!")
        print(f"Duration: {duration:.1f} seconds")
        print(f"Output directory: {self.output_dir}")
        
        # Show directory size
        total_size = sum(f.stat().st_size for f in self.output_dir.rglob('*') if f.is_file())
        print(f"Total size: {total_size / 1024 / 1024:.1f} MB")
        
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python wp_to_static_generator.py <output_directory> [--deploy]")
        print("Example: python wp_to_static_generator.py ./static-site-output")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    deploy_flag = '--deploy' in sys.argv
    
    # Configuration
    WP_URL = 'https://wordpress.jameskilby.cloud'
    AUTH_TOKEN = os.getenv('WP_AUTH_TOKEN')  # Use environment variable
    
    if not AUTH_TOKEN:
        print('❌ Error: WP_AUTH_TOKEN environment variable is required')
        print('   Set it with: export WP_AUTH_TOKEN="your_token_here"')
        sys.exit(1)
    TARGET_DOMAIN = 'https://jameskilby.co.uk'
    
    # Create generator instance
    generator = WordPressStaticGenerator(
        wp_url=WP_URL,
        auth_token=AUTH_TOKEN,
        output_dir=output_dir,
        target_domain=TARGET_DOMAIN
    )
    
    # Generate static site
    success = generator.generate_static_site()
    
    if success:
        print(f"\\n💡 Next steps:")
        print(f"1. Review the generated files in: {output_dir}")
        print(f"2. Test locally: python -m http.server 8000 --directory {output_dir}")
        print(f"3. Deploy to your hosting platform")
        print(f"4. Verify old URLs redirect correctly")
        
        if deploy_flag:
            print(f"\\n🚀 Deploy flag detected - implement your deployment logic here")
            # You could add deployment logic here for Cloudflare, Netlify, etc.
    else:
        print("❌ Generation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()