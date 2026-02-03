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
from incremental_builder import IncrementalBuilder

class WordPressStaticGenerator:
    def __init__(self, wp_url, auth_token, output_dir, target_domain, use_incremental=True):
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
        self.extracted_css_files = {}  # Map CSS hash to filename
        self.css_output_dir = self.output_dir / 'assets' / 'css'
        self.use_incremental = use_incremental
        self.incremental_builder = IncrementalBuilder() if use_incremental else None
        
    def get_all_content_urls(self):
        """Get all content URLs from WordPress REST API"""
        urls = set()
        
        # Check if we should do incremental build
        if self.incremental_builder:
            print("📋 Discovering content (incremental mode)...")
            changed_posts = self.incremental_builder.get_changed_posts(self.session, self.wp_url)
            changed_pages = self.incremental_builder.get_changed_pages(self.session, self.wp_url)
            
            # Add changed post/page URLs
            for post in changed_posts:
                relative_url = post['link'].replace(self.wp_url, '')
                urls.add(relative_url)
                print(f"   📄 Changed post: {post['title']['rendered']}")
            
            for page in changed_pages:
                relative_url = page['link'].replace(self.wp_url, '')
                urls.add(relative_url)
                print(f"   📑 Changed page: {page['title']['rendered']}")
            
            # Check if we need to rebuild archives
            if changed_posts or changed_pages or self.incremental_builder.should_rebuild_archives():
                print("   🔄 Rebuilding archive pages...")
                # Add essential pages and archives
                urls.update(['/', '/category/', '/tag/'])
                
                # Get all categories and tags (archives need full list)
                categories_response = self.session.get(f'{self.wp_url}/wp-json/wp/v2/categories?per_page=100')
                if categories_response.status_code == 200:
                    for category in categories_response.json():
                        if category['count'] > 0:
                            relative_url = category['link'].replace(self.wp_url, '')
                            urls.add(relative_url)
                            print(f"   📁 Category: {category['name']}")
                
                tags_response = self.session.get(f'{self.wp_url}/wp-json/wp/v2/tags?per_page=100')
                if tags_response.status_code == 200:
                    for tag in tags_response.json():
                        if tag['count'] > 0:
                            relative_url = tag['link'].replace(self.wp_url, '')
                            urls.add(relative_url)
                            print(f"   🏷️  Tag: {tag['name']}")
            
            print(f"\n✅ Incremental build: {len(urls)} URLs to process")
            return sorted(list(urls))
        
        # Full build mode
        print("📋 Discovering content from WordPress REST API...")
        
        # Get posts with pagination
        page = 1
        post_count = 0
        while True:
            print(f"   🔍 Fetching posts page {page}...")
            posts_response = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/posts',
                params={'per_page': 100, 'page': page, 'status': 'publish'}
            )
            
            if posts_response.status_code != 200:
                print(f"   ⚠️  Posts API returned status {posts_response.status_code} on page {page}")
                if posts_response.status_code == 400:
                    # Reached end of pagination
                    print(f"   ℹ️  Reached end of posts (page {page})")
                elif posts_response.status_code == 401:
                    print(f"   ❌ Authentication failed - check WP_AUTH_TOKEN")
                else:
                    print(f"   ❌ Error: {posts_response.text[:200]}")
                break
                
            posts = posts_response.json()
            if not posts:
                print(f"   ℹ️  No more posts on page {page}")
                break
                
            for post in posts:
                # Convert WordPress URL to relative path
                relative_url = post['link'].replace(self.wp_url, '')
                urls.add(relative_url)
                post_count += 1
                print(f"   📄 Post: {post['title']['rendered']}")
            
            page += 1
        
        print(f"   ✅ Discovered {post_count} posts from REST API")
        
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
        
        print(f"\n✅ Total URLs to process: {len(urls)}")
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
        
        # Extract and queue assets for download BEFORE URL replacement
        # This ensures we download from WordPress, not from the target domain
        self.extract_assets(soup, current_url)
        
        # Replace all WordPress URLs with target domain URLs
        self.replace_urls_in_soup(soup)
        
        # Remove WordPress-specific elements
        self.remove_wordpress_elements(soup)
        
        # Add static site optimizations
        self.add_static_optimizations(soup)
        
        # Add lazy loading to images
        self.add_lazy_loading(soup)
        
        # Optimize responsive image sizes
        self.optimize_responsive_images(soup)
        
        # Add copy code button to code blocks
        self.add_copy_code_button(soup)
        
        # Add content freshness indicator (published/updated dates)
        self.add_content_freshness_indicator(soup)
        
        # Add reading time and word count to entry-meta
        self.add_reading_time_indicator(soup)
        
        # Fix inline CSS font URLs
        self.fix_inline_css_urls(soup)
        
        # Extract inline CSS to external files
        self.extract_inline_css(soup, current_url)
        
        # Consolidate small inline CSS files to reduce critical request chain
        self.consolidate_inline_css_files(soup)
        
        # Process WordPress embeds (convert to proper iframes)
        self.process_wordpress_embeds(soup)
        
        # Clean up WordPress admin AJAX URLs
        self.clean_wordpress_ajax_urls(soup)
        
        # Add Utterances comments to every page
        self.add_utterances_comments(soup)
        
        # Add meta descriptions for taxonomy pages (tags/categories)
        self.add_taxonomy_meta_description(soup, current_url)
        
        # Fix missing H1 on homepage
        self.fix_homepage_h1(soup, current_url)
        
        # Fix table structure (add proper header rows)
        self.fix_table_headers(soup)
        
        # Add markdown and API links to footer
        self.add_markdown_api_links(soup)
        
        # Add breadcrumb navigation with schema markup
        self.add_breadcrumb_navigation(soup, current_url)
        
        # Add related posts section (only for single posts)
        self.add_related_posts(soup, current_url)
        
        # Convert to string
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
                                # Relative URLs - keep them relative (don't make absolute)
                                pass  # Leave relative URLs as-is
        
        # Fix meta tags (Open Graph, Twitter Cards, canonical, etc.)
        self.fix_meta_tag_urls(soup)
        
        # Fix JSON-LD structured data
        self.fix_jsonld_urls(soup)
    
    def fix_meta_tag_urls(self, soup):
        """Fix URLs in meta tags (Open Graph, Twitter Cards, canonical)"""
        # Fix meta tags with property attribute (Open Graph)
        for meta in soup.find_all('meta', property=True):
            prop = meta.get('property', '')
            content = meta.get('content', '')
            
            if content:
                # Convert relative URLs to absolute (for og:image, og:url, etc.)
                if content.startswith('/'):
                    meta['content'] = f"{self.target_domain}{content}"
                    print(f"   🔧 Made {prop} absolute: {content} -> {self.target_domain}{content}")
                # Replace WordPress URLs in og:url, og:image, etc.
                elif self.wp_url in content:
                    meta['content'] = content.replace(self.wp_url, self.target_domain)
                    print(f"   🔧 Fixed meta property: {prop}")
        
        # Check if og:image exists, add default if missing
        og_image = soup.find('meta', property='og:image')
        if not og_image and soup.head:
            # Use the site logo as default Open Graph image
            default_image_url = f"{self.target_domain}/wp-content/uploads/2025/12/ChatGPT-Image-Dec-17-2025-at-09_03_10-PM.png"
            
            og_image = soup.new_tag('meta')
            og_image['property'] = 'og:image'
            og_image['content'] = default_image_url
            soup.head.append(og_image)
            
            # Also add og:image:width and og:image:height
            og_image_width = soup.new_tag('meta')
            og_image_width['property'] = 'og:image:width'
            og_image_width['content'] = '1024'
            soup.head.append(og_image_width)
            
            og_image_height = soup.new_tag('meta')
            og_image_height['property'] = 'og:image:height'
            og_image_height['content'] = '1024'
            soup.head.append(og_image_height)
            
            print(f"   🇾added default og:image: {default_image_url}")
        
        # Add twitter:image if missing (use same as og:image)
        twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
        if not twitter_image and og_image and soup.head:
            twitter_image = soup.new_tag('meta')
            twitter_image['name'] = 'twitter:image'
            twitter_image['content'] = og_image.get('content', '')
            soup.head.append(twitter_image)
            print(f"   🐦 Added twitter:image from og:image")
        
        # Fix meta tags with name attribute (Twitter Cards)
        for meta in soup.find_all('meta', attrs={'name': True}):
            name = meta.get('name', '')
            content = meta.get('content', '')
            
            if content:
                # Convert relative URLs to absolute (for twitter:image, etc.)
                if content.startswith('/'):
                    meta['content'] = f"{self.target_domain}{content}"
                    print(f"   🔧 Made {name} absolute: {content} -> {self.target_domain}{content}")
                # Fix twitter:image, twitter:url, etc.
                elif self.wp_url in content:
                    meta['content'] = content.replace(self.wp_url, self.target_domain)
                    print(f"   🔧 Fixed meta name: {name}")
        
        # Fix canonical links - make them absolute
        for link in soup.find_all('link', rel='canonical'):
            href = link.get('href', '')
            if href:
                # Convert relative URLs to absolute
                if href.startswith('/'):
                    link['href'] = f"{self.target_domain}{href}"
                    print(f"   🔧 Made canonical URL absolute: {href} -> {self.target_domain}{href}")
                # Replace WordPress URLs
                elif self.wp_url in href:
                    link['href'] = href.replace(self.wp_url, self.target_domain)
                    print(f"   🔧 Fixed canonical URL")
        
        # Fix RSS feed links
        for link in soup.find_all('link', type=['application/rss+xml', 'application/atom+xml']):
            href = link.get('href', '')
            if href and self.wp_url in href:
                link['href'] = href.replace(self.wp_url, self.target_domain)
                print(f"   🔧 Fixed feed URL")
    
    def fix_jsonld_urls(self, soup):
        """Fix URLs in JSON-LD structured data for rich results"""
        # Find all script tags with JSON-LD
        for script in soup.find_all('script', type='application/ld+json'):
            if script.string:
                try:
                    # Parse JSON properly
                    data = json.loads(script.string)
                    
                    # Fix URLs recursively
                    modified = self._fix_jsonld_object(data)
                    
                    # Enhance BlogPosting with reading time and word count
                    if self._enhance_blogposting_schema(data, soup):
                        modified = True
                    
                    if modified:
                        # Convert back to JSON and update
                        script.string = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
                        print(f"   🔧 Enhanced JSON-LD with reading time and word count")
                        
                except json.JSONDecodeError as e:
                    print(f"   ⚠️  Invalid JSON-LD: {str(e)}")
                except Exception as e:
                    print(f"   ⚠️  Error fixing JSON-LD: {str(e)}")
    
    def _fix_jsonld_object(self, obj):
        """Recursively fix URLs in JSON-LD object"""
        modified = False
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Fix URL strings
                if isinstance(value, str):
                    # Convert relative URLs to absolute
                    if value.startswith('/'):
                        # Relative URL - make absolute
                        obj[key] = f"{self.target_domain}{value}"
                        modified = True
                    elif self.wp_url in value:
                        # WordPress URL - replace with target
                        obj[key] = value.replace(self.wp_url, self.target_domain)
                        modified = True
                
                # Recursively process nested objects/arrays
                elif isinstance(value, (dict, list)):
                    if self._fix_jsonld_object(value):
                        modified = True
        
        elif isinstance(obj, list):
            for item in obj:
                if isinstance(item, (dict, list)):
                    if self._fix_jsonld_object(item):
                        modified = True
        
        return modified
    
    def _enhance_blogposting_schema(self, data, soup):
        """Add reading time, word count, and publisher URL to BlogPosting schema"""
        modified = False
        
        # Handle @graph structure (Rank Math uses this)
        items = data.get('@graph', [data]) if '@graph' in data else [data]
        
        # First pass: Ensure Organization/Person publishers have URL
        for item in items:
            if isinstance(item, dict):
                item_types = item.get('@type', [])
                # Handle both single type and array of types
                if not isinstance(item_types, list):
                    item_types = [item_types]
                
                # If this is an Organization or Person that acts as publisher
                if any(t in ['Organization', 'Person'] for t in item_types):
                    if '@id' in item and '/#person' in item['@id']:
                        if 'url' not in item:
                            item['url'] = self.target_domain
                            modified = True
                            print(f"      ➕ Added URL to publisher entity: {self.target_domain}")
        
        # Second pass: Process BlogPosting items
        for item in items:
            if isinstance(item, dict) and item.get('@type') == 'BlogPosting':
                # Ensure publisher reference has URL (for inline publisher objects)
                if 'publisher' in item and isinstance(item['publisher'], dict):
                    if '@id' not in item['publisher'] and 'url' not in item['publisher']:
                        # Inline publisher without @id reference
                        item['publisher']['url'] = self.target_domain
                        modified = True
                        print(f"      ➕ Added publisher URL to inline publisher: {self.target_domain}")
                
                # Extract article content for word count
                article_content = self._extract_article_text(soup)
                
                if article_content:
                    # Calculate word count
                    word_count = len(article_content.split())
                    
                    # Calculate reading time (200 words per minute average)
                    reading_minutes = max(1, round(word_count / 200))
                    
                    # Add properties if not already present
                    if 'wordCount' not in item:
                        item['wordCount'] = word_count
                        modified = True
                        print(f"      ➕ Added wordCount: {word_count}")
                    
                    if 'timeRequired' not in item:
                        # Format as ISO 8601 duration (PT5M = 5 minutes)
                        item['timeRequired'] = f"PT{reading_minutes}M"
                        modified = True
                        print(f"      ➕ Added timeRequired: {reading_minutes} min")
                    
                    # Optionally add article body (truncated to 5000 chars)
                    if 'articleBody' not in item and len(article_content) > 100:
                        item['articleBody'] = article_content[:5000]
                        modified = True
                        print(f"      ➕ Added articleBody: {len(article_content[:5000])} chars")
        
        return modified
    
    def _extract_article_text(self, soup):
        """Extract main article text for word count calculation"""
        # Try to find the main article content
        # Common WordPress content containers
        content_selectors = [
            'article .entry-content',
            '.entry-content',
            'article',
            '.post-content',
            '.content',
            'main'
        ]
        
        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                # Clone to avoid modifying original
                content_copy = content_div.__copy__()
                
                # Remove unwanted elements
                for tag in content_copy(['script', 'style', 'nav', 'aside', 'footer', 'header']):
                    tag.decompose()
                
                # Get text content
                text = content_copy.get_text(separator=' ', strip=True)
                
                # Clean up whitespace
                text = ' '.join(text.split())
                
                # Only return if we found substantial content
                if len(text) > 100:
                    return text
        
        return None
    
    def remove_wordpress_elements(self, soup):
        """Remove WordPress-specific dynamic elements and artifacts"""
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
        
        # Remove xmlrpc.php RSD (Really Simple Discovery) links
        for link in soup.find_all('link', rel='EditURI'):
            if link.get('href') and 'xmlrpc.php' in link.get('href'):
                link.decompose()
                print(f"   🗑️  Removed xmlrpc.php RSD link")
        
        # Remove Windows Live Writer manifest links
        for link in soup.find_all('link', rel='wlwmanifest'):
            link.decompose()
            print(f"   🗑️  Removed wlwmanifest link")
        
        # Remove Rank Math HTML comments
        import re
        comments = soup.find_all(string=lambda text: isinstance(text, str) and '<!-- Search Engine Optimization by Rank Math' in text)
        for comment in comments:
            comment.extract()
        
        # Also remove the closing Rank Math comment
        comments = soup.find_all(string=lambda text: isinstance(text, str) and '/Rank Math WordPress SEO plugin' in text)
        for comment in comments:
            comment.extract()
            print(f"   🗑️  Removed Rank Math HTML comments")
        
        # Remove Kadence WP footer credit/links
        for link in soup.find_all('a', href=lambda x: x and 'kadencewp.com' in x):
            # Remove the parent paragraph or just the link
            parent = link.parent
            if parent and parent.name == 'p' and 'WordPress Theme by' in parent.get_text():
                parent.decompose()
                print(f"   🗑️  Removed Kadence WP footer credit")
            else:
                link.decompose()
    
    def process_wordpress_embeds(self, soup):
        """Convert WordPress embed blocks to proper iframe embeds"""
        # Handle wp-block-embed elements
        embed_blocks = soup.find_all('figure', class_=lambda x: x and 'wp-block-embed' in x)
        
        for embed_block in embed_blocks:
            embed_wrapper = embed_block.find('div', class_='wp-block-embed__wrapper')
            if not embed_wrapper:
                continue
                
            # Get the URL from the wrapper
            url_text = embed_wrapper.get_text(strip=True)
            if not url_text.startswith('http'):
                continue
            
            embed_url = url_text.strip()
            print(f"   🎬 Processing embed URL: {embed_url}")
            
            # Handle different embed providers
            if 'acast.com' in embed_url:
                iframe = self.create_acast_embed(embed_url, soup)
            elif 'youtube.com' in embed_url or 'youtu.be' in embed_url:
                iframe = self.create_youtube_embed(embed_url, soup)
            elif 'vimeo.com' in embed_url:
                iframe = self.create_vimeo_embed(embed_url, soup)
            elif 'twitter.com' in embed_url:
                iframe = self.create_twitter_embed(embed_url, soup)
            else:
                # Generic iframe embed
                iframe = self.create_generic_embed(embed_url, soup)
            
            if iframe:
                # Replace the embed wrapper with the iframe
                embed_wrapper.clear()
                embed_wrapper.append(iframe)
                print(f"   ✅ Converted embed to iframe: {embed_url}")
            else:
                print(f"   ⚠️  Could not convert embed: {embed_url}")
    
    def create_acast_embed(self, url, soup):
        """Create an iframe for Acast podcast embeds"""
        # Extract episode ID from Acast URL
        import re
        
        # Pattern: https://shows.acast.com/show-name/episodes/episode-name
        if '/episodes/' in url:
            try:
                # Convert to embeddable URL
                embed_url = url.replace('shows.acast.com', 'embed.acast.com')
                
                iframe = soup.new_tag('iframe')
                iframe['src'] = embed_url
                iframe['width'] = '100%'
                iframe['height'] = '190'
                iframe['frameborder'] = '0'
                iframe['scrolling'] = 'no'
                iframe['style'] = 'border: none;'
                iframe['loading'] = 'lazy'
                
                return iframe
            except Exception as e:
                print(f"   ⚠️  Error creating Acast embed: {e}")
                return None
        return None
    
    def create_youtube_embed(self, url, soup):
        """Create an iframe for YouTube embeds"""
        import re
        
        # Extract video ID from various YouTube URL formats
        video_id = None
        if 'youtu.be/' in url:
            video_id = url.split('youtu.be/')[1].split('?')[0]
        elif 'youtube.com/watch?v=' in url:
            video_id = url.split('v=')[1].split('&')[0]
        elif 'youtube.com/embed/' in url:
            video_id = url.split('/embed/')[1].split('?')[0]
        
        if video_id:
            iframe = soup.new_tag('iframe')
            iframe['src'] = f'https://www.youtube.com/embed/{video_id}'
            iframe['width'] = '560'
            iframe['height'] = '315'
            iframe['frameborder'] = '0'
            iframe['allowfullscreen'] = ''
            iframe['loading'] = 'lazy'
            
            return iframe
        return None
    
    def create_vimeo_embed(self, url, soup):
        """Create an iframe for Vimeo embeds"""
        import re
        
        # Extract video ID from Vimeo URL
        video_match = re.search(r'vimeo\.com/(\d+)', url)
        if video_match:
            video_id = video_match.group(1)
            
            iframe = soup.new_tag('iframe')
            iframe['src'] = f'https://player.vimeo.com/video/{video_id}'
            iframe['width'] = '640'
            iframe['height'] = '360'
            iframe['frameborder'] = '0'
            iframe['allowfullscreen'] = ''
            iframe['loading'] = 'lazy'
            
            return iframe
        return None
    
    def create_twitter_embed(self, url, soup):
        """Create a Twitter embed (simplified)"""
        # For Twitter, we'll create a simple link since Twitter embeds require JS
        link = soup.new_tag('a')
        link['href'] = url
        link['target'] = '_blank'
        link['rel'] = 'noopener noreferrer'
        link.string = f'View Tweet: {url}'
        
        return link
    
    def create_generic_embed(self, url, soup):
        """Create a generic iframe embed"""
        iframe = soup.new_tag('iframe')
        iframe['src'] = url
        iframe['width'] = '100%'
        iframe['height'] = '400'
        iframe['frameborder'] = '0'
        iframe['loading'] = 'lazy'
        
        return iframe
    
    def clean_wordpress_ajax_urls(self, soup):
        """Clean up WordPress admin AJAX URLs that won't work in static site"""
        # Find all script tags with WordPress admin AJAX URLs
        for script in soup.find_all('script'):
            if script.string:
                script_content = script.string
                # Replace WordPress admin AJAX URLs
                if 'wp-admin/admin-ajax.php' in script_content:
                    # Comment out or remove the AJAX URL since it won't work in static site
                    wp_domain = self.wp_url.replace('https://', '').replace('http://', '')
                    updated_content = script_content.replace(
                        f'"ajaxurl":"https:\\/\\/{wp_domain}\\/wp-admin\\/admin-ajax.php"',
                        '"ajaxurl":"#" /* Static site - AJAX disabled */'
                    )
                    if updated_content != script_content:
                        script.string = updated_content
                        print(f"   🧹 Cleaned WordPress AJAX URL in script")
    
    def fix_inline_css_urls(self, soup):
        """Fix inline CSS to convert font URLs from absolute to relative"""
        import re
        
        # Find all style tags with inline CSS
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                css_content = style_tag.string
                
                # Pattern to match font URLs
                font_url_pattern = r"url\(([^)]+)\)"
                
                def replace_font_url(match):
                    url = match.group(1).strip('"\'')
                    if url.startswith(self.wp_url):
                        # Convert absolute WordPress URL to relative
                        relative_url = url.replace(self.wp_url, '')
                        return f"url({relative_url})"
                    else:
                        # Leave other URLs as-is
                        return match.group(0)
                
                # Replace font URLs in the inline CSS
                updated_css = re.sub(font_url_pattern, replace_font_url, css_content)
                
                if updated_css != css_content:
                    style_tag.string = updated_css
                    print(f"   🎨 Fixed inline CSS font URLs")
    
    def extract_inline_css(self, soup, current_url):
        """Extract inline CSS to external files to reduce HTML payload"""
        import hashlib
        
        # Find all inline style tags
        style_tags = soup.find_all('style')
        
        if not style_tags:
            return
        
        # Ensure CSS output directory exists
        self.css_output_dir.mkdir(parents=True, exist_ok=True)
        
        for style_tag in style_tags:
            # Skip empty style tags
            if not style_tag.string or not style_tag.string.strip():
                continue
            
            # Get style ID if present
            style_id = style_tag.get('id', 'inline-styles')
            css_content = style_tag.string
            
            # Skip very small CSS blocks (< 100 bytes) - not worth extracting
            if len(css_content) < 100:
                continue
            
            # Create a hash of the CSS content for deduplication
            css_hash = hashlib.md5(css_content.encode()).hexdigest()[:8]
            
            # Check if we've already created a file for this CSS content
            if css_hash in self.extracted_css_files:
                css_filename = self.extracted_css_files[css_hash]
            else:
                # Create external CSS file
                css_filename = f"{style_id}-{css_hash}.min.css"
                css_file_path = self.css_output_dir / css_filename
                
                # Write CSS to external file
                css_file_path.write_text(css_content, encoding='utf-8')
                self.extracted_css_files[css_hash] = css_filename
                print(f"   📄 Created CSS: /assets/css/{css_filename}")
            
            # Use absolute path from root for CSS files
            # This works correctly at any depth in the site hierarchy
            css_path = f"/assets/css/{css_filename}"
            
            # Create link tag to replace inline style
            link_tag = soup.new_tag('link')
            link_tag['rel'] = 'stylesheet'
            link_tag['href'] = css_path
            link_tag['media'] = 'all'
            
            # Replace inline style with link tag
            style_tag.replace_with(link_tag)
    
    def add_utterances_comments(self, soup):
        """Add Utterances comments section to the page"""
        # Only add comments to single post/page views, not archive/list pages
        body = soup.find('body')
        if not body:
            return
        
        # Check body classes to determine if this is a single post
        body_classes = body.get('class', [])
        body_class_str = ' '.join(body_classes).lower()
        
        # Only add comments if this is explicitly a single post or page
        is_single_post = 'single-post' in body_class_str or 'single' in body_classes
        is_page = 'page-template' in body_class_str or ('page' in body_classes and 'single' not in body_class_str)
        
        if not (is_single_post or is_page):
            return  # Not a single post/page, skip comments
        
        # Find the best insertion point - right after entry-content, before entry-footer
        insertion_point = None
        insert_before = None
        
        # Try to find existing comments area first
        comments_area = soup.find('div', id='comments')
        if comments_area:
            # Replace existing comments with Utterances
            insertion_point = comments_area
        else:
            # Find the main article element
            articles = soup.find_all('article')
            if articles and len(articles) >= 1:
                article = articles[0]
                
                # Look for entry-content div inside the article - this is the main post content
                entry_content = article.find('div', class_=lambda x: x and 'entry-content' in x)
                
                if entry_content:
                    # Find the entry-footer in the parent article
                    entry_footer = article.find('footer', class_=lambda x: x and 'entry-footer' in x)
                    
                    if entry_footer:
                        # Insert before the footer (between content and footer)
                        insert_before = entry_footer
                    else:
                        # Fallback: insert after entry-content
                        insertion_point = entry_content
                else:
                    # Fallback: insert after the article itself
                    insertion_point = article
        
        if insertion_point or insert_before:
            # Create the Utterances comments section
            comments_div = soup.new_tag('div')
            comments_div['id'] = 'comments'
            comments_div['class'] = 'comments-area'
            
            inner_div = soup.new_tag('div')
            inner_div['class'] = 'pb-30'
            
            section = soup.new_tag('section')
            section['id'] = 'utterances-comments'
            
            script = soup.new_tag('script')
            script['src'] = 'https://utteranc.es/client.js'
            script['data-repo'] = 'jameskilbynet/jkcoukblog'
            script['data-issue-term'] = 'pathname'
            script['data-theme'] = 'github-dark'
            script['crossorigin'] = 'anonymous'
            script['async'] = ''
            script['data-cfasync'] = 'false'  # Bypass Cloudflare Rocket Loader
            
            section.append(script)
            inner_div.append(section)
            comments_div.append(inner_div)
            
            # Insert the comments section
            if comments_area:
                # Replace existing comments
                comments_area.replace_with(comments_div)
                print(f"   💬 Replaced existing comments with Utterances")
            elif insert_before:
                # Insert before the entry-footer
                insert_before.insert_before(comments_div)
                print(f"   💬 Added Utterances comments section before footer")
            elif insertion_point:
                # Insert immediately after the insertion point
                insertion_point.insert_after(comments_div)
                print(f"   💬 Added Utterances comments section after main content")
    
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
        
        # Add theme-color meta tag for mobile browsers
        # This colors the browser UI to match the site (improves mobile UX)
        existing_theme_color = soup.find('meta', attrs={'name': 'theme-color'})
        if not existing_theme_color:
            theme_color_meta = soup.new_tag('meta')
            theme_color_meta['name'] = 'theme-color'
            theme_color_meta['content'] = '#0a0a0a'  # Dark background - matches brutalist theme
            soup.head.append(theme_color_meta)
            print(f"   🎨 Added theme-color meta tag")
        else:
            # Update existing theme-color to match brutalist theme
            existing_theme_color['content'] = '#0a0a0a'
            print(f"   🎨 Updated theme-color meta tag to dark theme")
        
        # Add favicon links
        self.add_favicon_links(soup)
        
        # Inject brutalist theme CSS
        self.add_brutalist_theme_css(soup)
        
        # Add Plausible analytics if not already present
        self.add_plausible_analytics(soup)
        
        # Add font preloading for critical fonts
        self.add_font_preloads(soup)
        
        # Add preload hints for critical resources (with duplicate detection)
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                href = link['href']
                # Check if preload already exists for this href
                existing_preload = soup.find('link', rel='preload', href=href)
                if not existing_preload:
                    preload = soup.new_tag('link')
                    preload['rel'] = 'preload'
                    preload['as'] = 'style'
                    preload['href'] = href
                    soup.head.insert(0, preload)
    
    def add_favicon_links(self, soup):
        """Add favicon links for better browser support and performance"""
        if not soup.head:
            return
        
        # Check if favicon links already exist
        existing_favicon = soup.find('link', rel=lambda x: x and 'icon' in x)
        if existing_favicon:
            return  # Already has favicon links
        
        # Add favicon.ico (legacy browser support)
        favicon_ico = soup.new_tag('link')
        favicon_ico['rel'] = 'icon'
        favicon_ico['type'] = 'image/x-icon'
        favicon_ico['href'] = '/favicon.ico'
        soup.head.append(favicon_ico)
        
        # Add PNG favicon for modern browsers
        favicon_32 = soup.new_tag('link')
        favicon_32['rel'] = 'icon'
        favicon_32['type'] = 'image/png'
        favicon_32['sizes'] = '32x32'
        favicon_32['href'] = '/favicon-32x32.png'
        soup.head.append(favicon_32)
        
        favicon_16 = soup.new_tag('link')
        favicon_16['rel'] = 'icon'
        favicon_16['type'] = 'image/png'
        favicon_16['sizes'] = '16x16'
        favicon_16['href'] = '/favicon-16x16.png'
        soup.head.append(favicon_16)
        
        # Add Apple touch icon
        apple_touch = soup.new_tag('link')
        apple_touch['rel'] = 'apple-touch-icon'
        apple_touch['sizes'] = '180x180'
        apple_touch['href'] = '/apple-touch-icon.png'
        soup.head.append(apple_touch)
        
        # Add web app manifest
        manifest = soup.new_tag('link')
        manifest['rel'] = 'manifest'
        manifest['href'] = '/site.webmanifest'
        soup.head.append(manifest)
        
        print(f"   🐞 Added favicon links for browser support")
    
    def add_font_preloads(self, soup):
        """Preload critical fonts for faster text rendering (reduces FCP/LCP)"""
        if not soup.head:
            return
        
        # Critical fonts used above-the-fold
        # Anton for headings, Space Grotesk for body text
        critical_fonts = [
            '/assets/fonts/anton-v27-latin-400.woff2',
            '/assets/fonts/spacegrotesk-v22-latin-400.woff2',
            '/assets/fonts/spacegrotesk-v22-latin-500.woff2'
        ]
        
        for font_url in critical_fonts:
            # Check if font preload already exists
            existing_preload = soup.find('link', rel='preload', href=font_url)
            if not existing_preload:
                preload = soup.new_tag('link')
                preload['rel'] = 'preload'
                preload['as'] = 'font'
                preload['type'] = 'font/woff2'
                preload['href'] = font_url
                preload['crossorigin'] = 'anonymous'
                # Insert at beginning of head for highest priority
                soup.head.insert(0, preload)
        
        print(f"   🔤 Preloaded {len(critical_fonts)} critical fonts")
    
    def consolidate_inline_css_files(self, soup):
        """Consolidate multiple small inline CSS files into one to reduce critical request chain"""
        if not soup.head:
            return
        
        # Find all inline CSS files (wp-block-*, global-styles, etc.)
        inline_css_patterns = [
            'wp-block-library-inline-css',
            'wp-block-heading-inline-css',
            'wp-block-paragraph-inline-css',
            'wp-block-table-inline-css',
            'wp-img-auto-sizes-contain-inline-css',
            'global-styles-inline-css',
            'classic-theme-styles-inline-css',
            'inline-styles-'
        ]
        
        css_links_to_consolidate = []
        
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if any(pattern in href for pattern in inline_css_patterns):
                css_links_to_consolidate.append(link)
        
        if len(css_links_to_consolidate) < 2:
            return  # Not enough files to consolidate
        
        print(f"   📦 Consolidating {len(css_links_to_consolidate)} inline CSS files")
        
        # Read and merge CSS content
        consolidated_css = []
        
        for link in css_links_to_consolidate:
            href = link.get('href', '')
            if href.startswith('/'):
                css_file_path = self.output_dir / href.lstrip('/')
                if css_file_path.exists():
                    try:
                        css_content = css_file_path.read_text(encoding='utf-8')
                        consolidated_css.append(f"/* {href} */\n{css_content}\n")
                    except Exception as e:
                        print(f"   ⚠️  Could not read {href}: {e}")
        
        if not consolidated_css:
            return
        
        # Create consolidated file
        consolidated_content = '\n'.join(consolidated_css)
        consolidated_filename = 'consolidated-inline-styles.min.css'
        consolidated_path = self.output_dir / 'assets' / 'css' / consolidated_filename
        
        consolidated_path.parent.mkdir(parents=True, exist_ok=True)
        consolidated_path.write_text(consolidated_content, encoding='utf-8')
        
        # Replace all inline CSS links with single consolidated link
        # Remove old links
        for link in css_links_to_consolidate:
            link.decompose()
        
        # Add new consolidated link
        consolidated_link = soup.new_tag('link')
        consolidated_link['rel'] = 'stylesheet'
        consolidated_link['href'] = f'/assets/css/{consolidated_filename}'
        consolidated_link['media'] = 'all'
        
        # Insert after first stylesheet or at beginning of head
        first_stylesheet = soup.find('link', rel='stylesheet')
        if first_stylesheet:
            first_stylesheet.insert_after(consolidated_link)
        else:
            soup.head.insert(0, consolidated_link)
        
        print(f"   ✅ Consolidated {len(css_links_to_consolidate)} CSS files → {consolidated_filename} ({len(consolidated_content)} bytes)")
    
    def add_brutalist_theme_css(self, soup):
        """Add brutalist theme CSS with critical mobile CSS inlined"""
        if not soup.head:
            return
        
        # Check if brutalist theme link is already injected
        existing_brutalist = soup.find('link', href='/assets/css/brutalist-theme.css')
        if existing_brutalist:
            return
        
        # Copy CSS to output directory once
        source_css_path = Path(__file__).parent / 'brutalist-theme.css'
        theme_css_path = self.output_dir / 'assets' / 'css' / 'brutalist-theme.css'
        
        if not source_css_path.exists():
            print(f"   ⚠️  Brutalist theme CSS not found at {source_css_path}")
            return
        
        try:
            # Ensure the assets/css directory exists
            theme_css_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy CSS file if it doesn't exist or is outdated
            if not theme_css_path.exists() or source_css_path.stat().st_mtime > theme_css_path.stat().st_mtime:
                shutil.copy(source_css_path, theme_css_path)
                print(f"   📋 Copied brutalist theme CSS to {theme_css_path}")
            
            # Inline critical mobile CSS for faster FCP
            critical_css_path = Path(__file__).parent / 'critical-mobile.css'
            if critical_css_path.exists():
                try:
                    critical_css = critical_css_path.read_text(encoding='utf-8')
                    # Minify: remove comments and extra whitespace
                    import re
                    critical_css = re.sub(r'/\*[^*]*\*+(?:[^/*][^*]*\*+)*/', '', critical_css)  # Remove comments
                    critical_css = re.sub(r'\s+', ' ', critical_css)  # Collapse whitespace
                    critical_css = critical_css.strip()
                    
                    # Create inline style tag with media query for mobile
                    style_tag = soup.new_tag('style')
                    style_tag['media'] = 'screen and (max-width: 768px)'
                    style_tag.string = critical_css
                    # Insert at beginning of head for highest priority
                    soup.head.insert(0, style_tag)
                    print(f"   📱 Inlined critical mobile CSS ({len(critical_css)} bytes)")
                except Exception as e:
                    print(f"   ⚠️  Failed to inline critical CSS: {str(e)}")
            
            # Link to external file with media query and preload
            # Add preload for faster loading
            preload = soup.new_tag('link')
            preload['rel'] = 'preload'
            preload['as'] = 'style'
            preload['href'] = '/assets/css/brutalist-theme.css'
            soup.head.append(preload)
            
            # Add main stylesheet link
            # IMPORTANT: Load synchronously (not media="print" trick) because this CSS
            # contains @import for custom fonts which must load before first paint
            # to avoid Flash of Unstyled Text (FOUT)
            link = soup.new_tag('link', rel='stylesheet', href='/assets/css/brutalist-theme.css')
            link['media'] = 'all'
            soup.head.append(link)
            
            print(f"   🎨 Added brutalist theme CSS with non-blocking load")
        except Exception as e:
            print(f"   ❌ Failed to add brutalist theme CSS: {str(e)}")
    
    def add_plausible_analytics(self, soup):
        """Add Plausible Analytics script to the page if not already present"""
        if not soup.head:
            return
        
        # Import config for Plausible settings
        from config import Config
        
        # Check if Plausible script is already present
        plausible_domain = Config.PLAUSIBLE_URL
        plausible_script_url = Config.get_plausible_script_url()
        target_analytics_domain = Config.get_plausible_domain()
        
        # Add DNS prefetch and preconnect for faster analytics loading
        # This helps browser establish connection early, improving performance
        
        # Check if dns-prefetch already exists
        existing_dns_prefetch = soup.find('link', rel='dns-prefetch', href=f'//{plausible_domain}')
        if not existing_dns_prefetch:
            dns_prefetch = soup.new_tag('link')
            dns_prefetch['rel'] = 'dns-prefetch'
            dns_prefetch['href'] = f'//{plausible_domain}'
            soup.head.insert(0, dns_prefetch)  # Insert early in head
            print(f"   🔗 Added DNS prefetch for {plausible_domain}")
        
        # Check if preconnect already exists
        existing_preconnect = soup.find('link', rel='preconnect', href=f'https://{plausible_domain}')
        if not existing_preconnect:
            preconnect = soup.new_tag('link')
            preconnect['rel'] = 'preconnect'
            preconnect['href'] = f'https://{plausible_domain}'
            preconnect['crossorigin'] = ''
            soup.head.insert(1, preconnect)  # Insert after dns-prefetch
            print(f"   🔗 Added preconnect for {plausible_domain}")
        
        # Look for existing Plausible script
        existing_plausible = soup.find('script', src=lambda x: x and 'plausible' in x and 'script.js' in x)
        
        if existing_plausible:
            # Update the data-domain attribute to ensure it's correct
            existing_plausible['data-domain'] = target_analytics_domain
            existing_plausible['defer'] = ''  # Use defer for better preconnect timing
            existing_plausible['data-cfasync'] = 'false'  # Bypass Cloudflare Rocket Loader
            # Remove async if it exists
            if existing_plausible.get('async'):
                del existing_plausible['async']
            print(f"   📊 Updated existing Plausible analytics configuration")
        else:
            # Add new Plausible script
            plausible_script = soup.new_tag('script')
            plausible_script['data-domain'] = target_analytics_domain
            plausible_script['defer'] = ''  # Use defer for better preconnect timing
            plausible_script['data-cfasync'] = 'false'  # Bypass Cloudflare Rocket Loader
            plausible_script['src'] = plausible_script_url
            soup.head.append(plausible_script)
            print(f"   📊 Added Plausible analytics script to page")
    
    def add_lazy_loading(self, soup):
        """Add intelligent lazy loading based on image position and priority"""
        
        # Find all images
        images = soup.find_all('img')
        
        if not images:
            return
        
        eager_count = 0
        lazy_count = 0
        high_priority_count = 0
        
        for idx, img in enumerate(images):
            # Skip if image already has loading attribute
            if img.get('loading'):
                continue
            
            # Determine if this is a high-priority image
            is_hero_image = self._is_hero_image(img)
            is_featured_post = self._is_featured_post_image(img, idx)
            is_above_fold = idx < 3  # First 3 images likely above fold
            
            # High priority images: load eagerly with high fetchpriority
            if is_hero_image or (is_featured_post and idx == 0):
                img['loading'] = 'eager'
                img['fetchpriority'] = 'high'
                high_priority_count += 1
                eager_count += 1
                print(f"   🚀 Image {idx + 1}: HIGH PRIORITY (hero/featured)")
            
            # Above-fold images: eager loading but normal priority
            elif is_above_fold and (is_featured_post or idx < 2):
                img['loading'] = 'eager'
                img['decoding'] = 'async'
                eager_count += 1
                print(f"   ⚡ Image {idx + 1}: eager loading (above fold)")
            
            # Below-fold images: lazy loading
            else:
                img['loading'] = 'lazy'
                img['decoding'] = 'async'
                lazy_count += 1
                # Reduce priority for way-below-fold images
                if idx > 10:
                    # These are far down the page, lowest priority
                    pass
        
        print(f"   ✅ Image loading strategy:")
        print(f"      🚀 High priority: {high_priority_count}")
        print(f"      ⚡ Eager: {eager_count - high_priority_count}")
        print(f"      📦 Lazy: {lazy_count}")
    
    def _is_hero_image(self, img):
        """Determine if an image is a hero/banner image"""
        # Check for hero image classes or attributes
        img_class = ' '.join(img.get('class', []))
        
        # Common hero image patterns
        hero_patterns = ['hero', 'banner', 'featured-image', 'masthead']
        
        for pattern in hero_patterns:
            if pattern in img_class.lower():
                return True
        
        # Check parent elements for hero sections
        parent = img.parent
        for _ in range(3):  # Check up to 3 levels up
            if parent and parent.name:
                parent_class = ' '.join(parent.get('class', []))
                for pattern in hero_patterns:
                    if pattern in parent_class.lower():
                        return True
                parent = parent.parent
            else:
                break
        
        return False
    
    def _is_featured_post_image(self, img, idx):
        """Determine if an image is a featured post thumbnail"""
        img_class = ' '.join(img.get('class', []))
        
        # WordPress post thumbnail classes
        if 'wp-post-image' in img_class or 'post-thumbnail' in img_class:
            return True
        
        # Check if inside a post entry/article
        parent = img.parent
        for _ in range(5):  # Check up to 5 levels up
            if parent and parent.name:
                parent_class = ' '.join(parent.get('class', []))
                # Archive/list page entry classes
                if any(cls in parent_class for cls in ['entry', 'post', 'article']):
                    return True
                parent = parent.parent
            else:
                break
        
        return False
    
    def optimize_responsive_images(self, soup):
        """Optimize responsive image sizes attribute for better mobile performance"""
        # Find featured images (post thumbnails) that have srcset
        featured_images = soup.find_all('img', class_=lambda x: x and 'wp-post-image' in x and 'attachment-medium_large' in x)
        
        if not featured_images:
            return
        
        optimized_count = 0
        
        for img in featured_images:
            srcset = img.get('srcset', '')
            sizes = img.get('sizes', '')
            
            if not srcset or not sizes:
                continue
            
            # Mobile-optimized sizes attribute with granular breakpoints
            # Tells browser to load appropriately sized images for each device
            # Original: sizes="(max-width: 768px) 100vw, 768px" or similar
            # Optimized with mobile breakpoints:
            #   - 320px screens (iPhone SE): ~95vw = 304px -> use 300w image
            #   - 375px screens (iPhone): ~95vw = 356px -> use 300w image
            #   - 480px screens: ~90vw = 432px -> use 768w image
            #   - 768px tablets: ~90vw = 691px -> use 768w image
            #   - Desktop: fixed 400px
            
            # Check if this needs optimization (has old pattern)
            if sizes and ('768px' in sizes or '100vw' in sizes):
                # New mobile-optimized sizes with multiple breakpoints
                new_sizes = '(max-width: 480px) 95vw, (max-width: 768px) 90vw, 400px'
                img['sizes'] = new_sizes
                optimized_count += 1
                print(f"   📱 Optimized image sizes for mobile: added 480px breakpoint")
        
        if optimized_count > 0:
            print(f"   ✅ Optimized {optimized_count} featured image(s) with mobile-specific breakpoints")
    
    def add_copy_code_button(self, soup):
        """Add copy code button to all code blocks"""
        
        # Find all pre > code blocks (standard code block pattern)
        code_blocks = soup.find_all('pre')
        
        if not code_blocks:
            return
        
        button_count = 0
        
        for pre in code_blocks:
            # Skip if already has copy button wrapper
            if pre.parent and 'code-block-wrapper' in pre.parent.get('class', []):
                continue
            
            # Wrap pre in a div with relative positioning
            wrapper = soup.new_tag('div')
            wrapper['class'] = 'code-block-wrapper'
            wrapper['style'] = 'position: relative; margin: 1em 0;'
            
            # Create copy button
            button = soup.new_tag('button')
            button['class'] = 'copy-code-button'
            button['aria-label'] = 'Copy code to clipboard'
            button['style'] = '''position: absolute; top: 8px; right: 8px; 
                padding: 6px 12px; background: #2d3748; color: #fff; 
                border: 1px solid #4a5568; border-radius: 4px; 
                cursor: pointer; font-size: 12px; font-family: sans-serif;
                opacity: 0.8; transition: opacity 0.2s, background 0.2s;
                z-index: 10;'''
            button.string = '📋 Copy'
            
            # Insert wrapper before pre
            pre.insert_before(wrapper)
            # Move pre into wrapper
            wrapper.append(pre.extract())
            # Add button to wrapper
            wrapper.append(button)
            
            button_count += 1
        
        if button_count > 0:
            # Add JavaScript for copy functionality
            script = soup.new_tag('script')
            script.string = '''
(function() {
    document.querySelectorAll('.copy-code-button').forEach(function(button) {
        button.addEventListener('click', function() {
            var pre = this.previousElementSibling;
            var code = pre.querySelector('code') || pre;
            var text = code.textContent || code.innerText;
            
            // Copy to clipboard
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(function() {
                    // Success feedback
                    button.textContent = '✅ Copied!';
                    button.style.background = '#48bb78';
                    setTimeout(function() {
                        button.textContent = '📋 Copy';
                        button.style.background = '#2d3748';
                    }, 2000);
                }).catch(function() {
                    button.textContent = '❌ Failed';
                    setTimeout(function() {
                        button.textContent = '📋 Copy';
                    }, 2000);
                });
            } else {
                // Fallback for older browsers
                var textarea = document.createElement('textarea');
                textarea.value = text;
                textarea.style.position = 'fixed';
                textarea.style.opacity = '0';
                document.body.appendChild(textarea);
                textarea.select();
                try {
                    document.execCommand('copy');
                    button.textContent = '✅ Copied!';
                    button.style.background = '#48bb78';
                    setTimeout(function() {
                        button.textContent = '📋 Copy';
                        button.style.background = '#2d3748';
                    }, 2000);
                } catch (err) {
                    button.textContent = '❌ Failed';
                    setTimeout(function() {
                        button.textContent = '📋 Copy';
                    }, 2000);
                }
                document.body.removeChild(textarea);
            }
        });
        
        // Hover effects
        button.addEventListener('mouseenter', function() {
            this.style.opacity = '1';
            this.style.background = '#4a5568';
        });
        button.addEventListener('mouseleave', function() {
            this.style.opacity = '0.8';
            this.style.background = '#2d3748';
        });
    });
})();
'''
            
            # Add script to end of body
            if soup.body:
                soup.body.append(script)
                print(f"   📋 Added copy buttons to {button_count} code blocks")
        else:
            print(f"   ℹ️  No code blocks found to add copy buttons")
    
    def add_content_freshness_indicator(self, soup):
        """Add visible content freshness indicator showing published and updated dates"""
        
        # Extract dates from JSON-LD structured data
        date_published = None
        date_modified = None
        
        for script in soup.find_all('script', type='application/ld+json'):
            if script.string:
                try:
                    data = json.loads(script.string)
                    
                    # Handle @graph structure (Rank Math uses this)
                    items = data.get('@graph', [data]) if '@graph' in data else [data]
                    
                    for item in items:
                        if isinstance(item, dict) and item.get('@type') in ['BlogPosting', 'WebPage']:
                            date_published = item.get('datePublished')
                            date_modified = item.get('dateModified')
                            if date_published and date_modified:
                                break
                    
                    if date_published and date_modified:
                        break
                        
                except (json.JSONDecodeError, Exception) as e:
                    print(f"   ⚠️  Error parsing JSON-LD: {e}")
                    continue
        
        # Only add indicator if we have dates and the content was modified after publication
        if not date_published or not date_modified:
            print(f"   ℹ️  Skipping freshness indicator - dates not found (pub: {date_published}, mod: {date_modified})")
            return
        
        # Parse dates to compare them
        try:
            from datetime import datetime
            pub_dt = datetime.fromisoformat(date_published.replace('Z', '+00:00'))
            mod_dt = datetime.fromisoformat(date_modified.replace('Z', '+00:00'))
            
            # Format dates for display (human-readable)
            pub_formatted = pub_dt.strftime('%B %d, %Y')
            mod_formatted = mod_dt.strftime('%B %d, %Y')
            
            # Only show freshness indicator if modified date is different from published date
            # (allowing for same-day edits to not trigger indicator)
            if pub_dt.date() == mod_dt.date():
                print(f"   ℹ️  Skipping freshness indicator - same-day edit ({pub_dt.date()})")
                return
            
        except (ValueError, AttributeError) as e:
            print(f"   ⚠️  Error parsing dates: {e}")
            return
        
        # Find the entry-header or entry-meta to insert the freshness indicator after
        # Try multiple selectors to match different theme structures
        insertion_targets = [
            soup.find('header', class_=lambda x: x and 'entry-header' in x),
            soup.find('div', class_=lambda x: x and 'entry-meta' in x),
            soup.find('h1', class_=lambda x: x and 'entry-title' in x),
            soup.find('article')
        ]
        
        insertion_point = None
        for target in insertion_targets:
            if target:
                insertion_point = target
                break
        
        if not insertion_point:
            print(f"   ⚠️  Could not find insertion point for freshness indicator")
            return
        
        # Create the freshness indicator
        freshness_div = soup.new_tag('div')
        freshness_div['class'] = 'content-freshness-indicator'
        
        # Icon and text
        icon_span = soup.new_tag('span')
        icon_span['class'] = 'freshness-icon'
        icon_span.string = '📅'
        
        text_span = soup.new_tag('span')
        
        # Published date
        pub_strong = soup.new_tag('strong')
        pub_strong.string = 'Published: '
        text_span.append(pub_strong)
        
        pub_time = soup.new_tag('time')
        pub_time['datetime'] = date_published
        pub_time.string = pub_formatted
        text_span.append(pub_time)
        
        # Separator
        separator = soup.new_tag('span')
        separator['class'] = 'freshness-separator'
        separator.string = '•'
        text_span.append(separator)
        
        # Updated date
        mod_strong = soup.new_tag('strong')
        mod_strong.string = 'Updated: '
        text_span.append(mod_strong)
        
        mod_time = soup.new_tag('time')
        mod_time['datetime'] = date_modified
        mod_time.string = mod_formatted
        text_span.append(mod_time)
        
        freshness_div.append(icon_span)
        freshness_div.append(text_span)
        
        # Insert after the entry-header or chosen insertion point
        insertion_point.insert_after(freshness_div)
        
        print(f"   📅 Added content freshness indicator (Published: {pub_formatted}, Updated: {mod_formatted})")
    
    def add_reading_time_indicator(self, soup):
        """Add visible reading time and word count to the entry-meta section"""
        
        # Extract article content for word count
        article_content = self._extract_article_text(soup)
        
        if not article_content:
            print(f"   ℹ️  Skipping reading time indicator - no article content found")
            return
        
        # Calculate word count and reading time
        word_count = len(article_content.split())
        reading_minutes = max(1, round(word_count / 200))  # 200 words per minute average
        
        # Find the entry-meta div to add reading time
        entry_meta = soup.find('div', class_=lambda x: x and 'entry-meta' in x)
        
        if not entry_meta:
            print(f"   ℹ️  Skipping reading time indicator - entry-meta not found")
            return
        
        # Create reading time span
        reading_time_span = soup.new_tag('span')
        reading_time_span['class'] = 'reading-time'
        reading_time_span['style'] = 'color: #718096;'
        
        # Add separator
        separator = soup.new_tag('span')
        separator.string = ' • '
        reading_time_span.append(separator)
        
        # Add reading time icon and text
        time_icon = soup.new_tag('span')
        time_icon['style'] = 'margin-right: 4px;'
        time_icon.string = '📖'
        reading_time_span.append(time_icon)
        
        # Reading time text
        time_text = soup.new_tag('span')
        time_text.string = f'{reading_minutes} min read'
        reading_time_span.append(time_text)
        
        # Add word count
        word_count_text = soup.new_tag('span')
        word_count_text['style'] = 'margin-left: 4px; color: #a0aec0;'
        word_count_text.string = f'({word_count:,} words)'
        reading_time_span.append(word_count_text)
        
        # Append to entry-meta
        entry_meta.append(reading_time_span)
        
        print(f"   📖 Added reading time: {reading_minutes} min ({word_count:,} words)")
    
    def add_taxonomy_meta_description(self, soup, current_url):
        """Add meta descriptions to tag and category archive pages"""
        # Check if this is a taxonomy page (tag or category)
        if '/tag/' not in current_url and '/category/' not in current_url:
            return
        
        # Check if description already exists
        existing_desc = soup.find('meta', attrs={'name': 'description'})
        if existing_desc and existing_desc.get('content'):
            # Check if it's the default site description
            content = existing_desc.get('content', '')
            if 'James Kilby' in content and 'technical blog' in content:
                # This is the generic site description, replace it
                pass
            else:
                # Already has a specific description
                return
        
        # Extract taxonomy name from URL and title
        taxonomy_type = 'tag' if '/tag/' in current_url else 'category'
        
        # Try to get taxonomy name from the page title
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.get_text().strip()
            # Extract taxonomy name from title (e.g., "VMware Archives - jameskilbycouk" -> "VMware")
            import re
            match = re.match(r'^([^-|]+)(?:\s+Archives)?\s+[-|]', title)
            if match:
                taxonomy_name = match.group(1).strip()
            else:
                # Fallback to URL
                taxonomy_name = current_url.strip('/').split('/')[-1].replace('-', ' ').title()
        else:
            # Fallback to URL
            taxonomy_name = current_url.strip('/').split('/')[-1].replace('-', ' ').title()
        
        # Generate appropriate description
        if taxonomy_type == 'tag':
            description = f"Articles tagged with {taxonomy_name}. Explore technical guides, tutorials, and insights about {taxonomy_name} from James Kilby's blog."
        else:
            description = f"Browse all {taxonomy_name} articles. In-depth technical content covering {taxonomy_name} topics, best practices, and real-world solutions."
        
        # Update or create meta description
        if existing_desc:
            existing_desc['content'] = description
            print(f"   🏷️  Updated meta description for {taxonomy_type}: {taxonomy_name}")
        else:
            # Create new meta description
            if soup.head:
                meta_desc = soup.new_tag('meta')
                meta_desc['name'] = 'description'
                meta_desc['content'] = description
                soup.head.append(meta_desc)
                print(f"   🏷️  Added meta description for {taxonomy_type}: {taxonomy_name}")
        
        # Also update og:description and twitter:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            og_desc['content'] = description
        elif soup.head:
            og_desc = soup.new_tag('meta')
            og_desc['property'] = 'og:description'
            og_desc['content'] = description
            soup.head.append(og_desc)
        
        twitter_desc = soup.find('meta', attrs={'name': 'twitter:description'})
        if twitter_desc:
            twitter_desc['content'] = description
        elif soup.head:
            twitter_desc = soup.new_tag('meta')
            twitter_desc['name'] = 'twitter:description'
            twitter_desc['content'] = description
            soup.head.append(twitter_desc)
    
    def fix_homepage_h1(self, soup, current_url):
        """Fix missing H1 tag on homepage by converting site title to H1"""
        # Only apply to homepage
        if current_url not in ['/', '']:
            return
        
        # Check if H1 already exists
        if soup.find('h1'):
            print(f"   ℹ️  H1 already exists on homepage")
            return
        
        # Find site-title elements (both desktop and mobile versions)
        site_titles = soup.find_all(class_='site-title')
        
        if not site_titles:
            print(f"   ⚠️  Could not find site-title element on homepage")
            return
        
        # Convert each site-title to H1
        for title_elem in site_titles:
            # Get the current tag name (p, div, etc.)
            old_tag_name = title_elem.name
            
            # Create new H1 tag with same attributes and content
            h1_tag = soup.new_tag('h1')
            
            # Copy all attributes except class (we'll reconstruct it)
            for attr, value in title_elem.attrs.items():
                if attr == 'class':
                    # Keep site-title class but ensure h1 semantics
                    h1_tag['class'] = value
                else:
                    h1_tag[attr] = value
            
            # Copy all children (preserves inner structure)
            for child in title_elem.children:
                h1_tag.append(child)
            
            # Replace old tag with H1
            title_elem.replace_with(h1_tag)
            
            print(f"   ✅ Converted {old_tag_name}.site-title to H1 on homepage")
    
    def add_markdown_api_links(self, soup):
        """Add links to markdown and API versions in footer"""
        import re
        
        footer = soup.find('footer', class_=re.compile(r'site-footer', re.I))
        
        if footer:
            # Create a new div for content formats
            formats_div = soup.new_tag('div')
            formats_div['class'] = 'content-formats'
            formats_div['style'] = 'margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--gray-mid);'
            
            p = soup.new_tag('p')
            p.string = 'Content also available in: '
            
            # Markdown link
            md_link = soup.new_tag('a', href='/markdown/')
            md_link.string = 'Markdown'
            p.append(md_link)
            
            p.append(' | ')
            
            # API link
            api_link = soup.new_tag('a', href='/api/')
            api_link.string = 'JSON API'
            p.append(api_link)
            
            formats_div.append(p)
            footer.append(formats_div)
            print(f"   🔗 Added markdown and API links to footer")
    
    def fix_table_headers(self, soup):
        """Fix table structure by converting first row to proper thead with th elements"""
        # Find all tables
        tables = soup.find_all('table')
        
        if not tables:
            return
        
        fixed_count = 0
        
        for table in tables:
            # Check if table already has a thead
            if table.find('thead'):
                continue
            
            # Find tbody
            tbody = table.find('tbody')
            if not tbody:
                continue
            
            # Get the first row
            first_row = tbody.find('tr')
            if not first_row:
                continue
            
            # Check if first row contains only td elements (potential header)
            cells = first_row.find_all(['td', 'th'])
            if not cells:
                continue
            
            # Only convert if all cells are td (not already th)
            all_td = all(cell.name == 'td' for cell in cells)
            if not all_td:
                continue
            
            # Create new thead element
            thead = soup.new_tag('thead')
            
            # Create new tr for the header
            header_row = soup.new_tag('tr')
            
            # Convert each td to th
            for cell in cells:
                th = soup.new_tag('th')
                # Copy all attributes
                for attr, value in cell.attrs.items():
                    th[attr] = value
                # Copy all children (preserves inner structure)
                for child in list(cell.children):
                    th.append(child.extract())
                header_row.append(th)
            
            # Add the header row to thead
            thead.append(header_row)
            
            # Remove the first row from tbody
            first_row.decompose()
            
            # Insert thead before tbody in the table
            tbody.insert_before(thead)
            
            fixed_count += 1
            print(f"   📊 Converted table first row to proper header (thead with th elements)")
        
        if fixed_count > 0:
            print(f"   ✅ Fixed {fixed_count} table(s) with proper semantic structure")
    
    def extract_assets(self, soup, current_url):
        """Extract asset URLs for later download"""
        # Enhanced asset selectors including WordPress-specific patterns
        asset_selectors = [
            ('img', 'src'),
            ('img', 'data-src'),  # Lazy loading images
            ('link[rel="stylesheet"]', 'href'),
            ('link[rel="preload"]', 'href'),  # Preload stylesheets
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
                        print(f"   🔍 Found absolute asset: {asset_url}")
                    elif asset_url.startswith('/wp-content/') or asset_url.startswith('/wp-includes/'):
                        # WordPress files - including cache, media, and core files
                        full_url = self.wp_url + asset_url
                        self.downloaded_assets.add(full_url)
                        print(f"   🔍 Found relative asset: {asset_url} -> {full_url}")
                    elif asset_url.startswith('/') and not asset_url.startswith('//'):
                        # Any other relative URLs (could be theme files, etc.)
                        full_url = self.wp_url + asset_url
                        self.downloaded_assets.add(full_url)
                        print(f"   🔍 Found other relative asset: {asset_url} -> {full_url}")
        
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
        css_links = soup.find_all('link', rel=['stylesheet', 'preload'])
        for link in css_links:
            href = link.get('href', '')
            if href:
                # Build full CSS URL
                if href.startswith('http'):
                    css_url = href
                elif href.startswith('/'):
                    css_url = self.wp_url + href
                else:
                    css_url = self.wp_url + '/' + href
                
                print(f"   🎨 Parsing CSS for embedded assets: {href}")
                try:
                    css_resp = self.session.get(css_url, timeout=30)
                    if css_resp.status_code == 200:
                        css_text = css_resp.text
                        # Find all URL references in CSS (fonts, images, etc.)
                        import re
                        url_patterns = [
                            r'url\(["\']?([^"\')]+)["\']?\)',  # Standard URL pattern
                            r'@font-face[^}]*src:[^}]*url\(["\']?([^"\')]+)["\']?\)',  # Font face URLs
                        ]
                        
                        for pattern in url_patterns:
                            urls_found = re.findall(pattern, css_text)
                            for found_url in urls_found:
                                clean_url = found_url.strip('"\' ')
                                if clean_url.startswith('data:') or not clean_url:
                                    continue
                                
                                if clean_url.startswith('http'):
                                    if clean_url.startswith(self.wp_url):
                                        self.downloaded_assets.add(clean_url)
                                        print(f"   📦 Found CSS asset (absolute): {clean_url}")
                                elif clean_url.startswith('/'):
                                    full_asset_url = self.wp_url + clean_url
                                    self.downloaded_assets.add(full_asset_url)
                                    print(f"   📦 Found CSS asset (relative): {clean_url} -> {full_asset_url}")
                                else:
                                    # Relative to CSS file location
                                    base_path = '/'.join(href.split('/')[:-1]) if '/' in href else ''
                                    if base_path:
                                        full_asset_url = self.wp_url + '/' + base_path + '/' + clean_url
                                    else:
                                        full_asset_url = self.wp_url + '/' + clean_url
                                    self.downloaded_assets.add(full_asset_url)
                                    print(f"   📦 Found CSS asset (relative to CSS): {clean_url} -> {full_asset_url}")
                    else:
                        print(f"   ⚠️  Failed to fetch CSS: {css_url} (status: {css_resp.status_code})")
                except Exception as e:
                    print(f"   ⚠️  Error parsing CSS {css_url}: {str(e)}")
        
        # Manually detect and queue WordPress minified cache files
        print(f"   🔍 Manually detecting WordPress minified cache files...")
        import re
        
        # Look for WPO minify CSS files
        wpo_css_matches = re.findall(r'href="([^"]*wpo-minify[^"]*\.min\.css[^"]*)"', str(soup))
        for css_match in wpo_css_matches:
            # Always convert to WordPress domain for downloading, regardless of current URL
            if css_match.startswith('/'):
                full_css_url = self.wp_url + css_match
            elif css_match.startswith(self.target_domain):
                # Convert target domain back to WordPress domain for downloading
                full_css_url = css_match.replace(self.target_domain, self.wp_url)
            else:
                full_css_url = css_match
            self.downloaded_assets.add(full_css_url)
            print(f"   🎨 Found WPO minified CSS: {css_match} -> {full_css_url}")
        
        # Look for WPO minify JS files
        wpo_js_matches = re.findall(r'src="([^"]*wpo-minify[^"]*\.min\.js[^"]*)"', str(soup))
        for js_match in wpo_js_matches:
            # Always convert to WordPress domain for downloading, regardless of current URL
            if js_match.startswith('/'):
                full_js_url = self.wp_url + js_match
            elif js_match.startswith(self.target_domain):
                # Convert target domain back to WordPress domain for downloading
                full_js_url = js_match.replace(self.target_domain, self.wp_url)
            else:
                full_js_url = js_match
            self.downloaded_assets.add(full_js_url)
            print(f"   📜 Found WPO minified JS: {js_match} -> {full_js_url}")
        
        # Look for any other cache files (general pattern)
        cache_matches = re.findall(r'(?:href|src)="([^"]*wp-content/cache[^"]+)"', str(soup))
        for cache_match in cache_matches:
            # Always convert to WordPress domain for downloading, regardless of current URL
            if cache_match.startswith('/'):
                full_cache_url = self.wp_url + cache_match
            elif cache_match.startswith(self.target_domain):
                # Convert target domain back to WordPress domain for downloading
                full_cache_url = cache_match.replace(self.target_domain, self.wp_url)
            else:
                full_cache_url = cache_match
            self.downloaded_assets.add(full_cache_url)
            print(f"   📦 Found cache file: {cache_match} -> {full_cache_url}")
    
    def download_assets(self):
        """Download all discovered assets"""
        if not self.downloaded_assets:
            print("   ⚠️  No assets discovered to download")
            return
            
        print(f"📁 Downloading {len(self.downloaded_assets)} assets...")
        
        def download_single_asset(asset_url):
            try:
                # Convert to relative path - handle both wp_url and target_domain
                if asset_url.startswith(self.wp_url):
                    relative_path = asset_url.replace(self.wp_url, '').lstrip('/')
                elif asset_url.startswith(self.target_domain):
                    relative_path = asset_url.replace(self.target_domain, '').lstrip('/')
                else:
                    # Fallback - extract path after domain
                    from urllib.parse import urlparse
                    parsed = urlparse(asset_url)
                    relative_path = parsed.path.lstrip('/')
                    
                output_path = self.output_dir / relative_path
                
                # Skip if already downloaded
                if output_path.exists():
                    return f"⏭️  {relative_path} (exists)"
                
                # Create directory
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Download with proper headers
                response = self.session.get(asset_url, timeout=30, stream=True)
                if response.status_code == 200:
                    # Validate content type matches expected file type
                    content_type = response.headers.get('content-type', '').lower()
                    
                    # Check for mismatched content type (e.g., HTML returned for CSS request)
                    if asset_url.endswith('.css') and 'text/css' not in content_type:
                        if 'text/html' in content_type:
                            return f"❌ {relative_path} (HTML returned instead of CSS - authentication/access issue)"
                        else:
                            return f"❌ {relative_path} (Wrong content-type: {content_type})"
                    elif asset_url.endswith('.js') and 'javascript' not in content_type and 'text/plain' not in content_type:
                        if 'text/html' in content_type:
                            return f"❌ {relative_path} (HTML returned instead of JS - authentication/access issue)"
                        else:
                            return f"❌ {relative_path} (Wrong content-type: {content_type})"
                    
                    # Special handling for CSS files - need to process URLs
                    if asset_url.endswith('.css'):
                        css_content = response.text
                        
                        # Validate CSS content by checking for HTML doctype or tags
                        if css_content.strip().startswith('<!DOCTYPE') or '<html' in css_content[:200].lower():
                            return f"❌ {relative_path} (HTML content returned instead of CSS)"
                        
                        # Convert absolute WordPress URLs to relative URLs
                        css_content = css_content.replace(self.wp_url + '/wp-content/', '/wp-content/')
                        css_content = css_content.replace(self.wp_url + '/wp-includes/', '/wp-includes/')
                        # Also convert the target domain URLs to relative
                        if self.target_domain:
                            css_content = css_content.replace(self.target_domain + '/wp-content/', '/wp-content/')
                            css_content = css_content.replace(self.target_domain + '/wp-includes/', '/wp-includes/')
                        
                        # Convert font URLs in CSS files to relative paths
                        import re
                        
                        # Pattern to match font URLs in CSS @font-face declarations
                        font_url_pattern = r"url\(([^)]+)\)"
                        
                        def replace_font_url(match):
                            url = match.group(1).strip('"\'')
                            if url.startswith(self.wp_url):
                                # Convert absolute WordPress URL to relative
                                relative_url = url.replace(self.wp_url, '')
                                return f"url({relative_url})"
                            elif url.startswith('http'):
                                # Leave external URLs as-is
                                return match.group(0)
                            else:
                                # Already relative or data URL
                                return match.group(0)
                        
                        css_content = re.sub(font_url_pattern, replace_font_url, css_content)
                        
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
    
    def add_breadcrumb_navigation(self, soup, current_url):
        """Add breadcrumb navigation with schema markup for better site hierarchy and SEO"""
        
        # Only add breadcrumbs to non-homepage pages
        if current_url == '/' or current_url == '':
            return
        
        # Check if this is a single post or page
        body = soup.find('body')
        if not body:
            return
        
        body_classes = body.get('class', [])
        body_class_str = ' '.join(body_classes).lower()
        
        # Parse URL to build breadcrumb path
        url_parts = [p for p in current_url.strip('/').split('/') if p]
        
        if not url_parts:
            return
        
        # Build breadcrumb items
        breadcrumb_items = [{
            'name': 'Home',
            'url': self.target_domain,
            'position': 1
        }]
        
        cumulative_path = ''
        position = 2
        
        # Determine breadcrumb structure based on URL pattern
        if 'category' in url_parts:
            # Category archive: Home > Category Name
            category_index = url_parts.index('category')
            if category_index + 1 < len(url_parts):
                category_slug = url_parts[category_index + 1]
                category_name = category_slug.replace('-', ' ').title()
                breadcrumb_items.append({
                    'name': category_name,
                    'url': f"{self.target_domain}/category/{category_slug}/",
                    'position': position
                })
        
        elif 'tag' in url_parts:
            # Tag archive: Home > Tags > Tag Name
            breadcrumb_items.append({
                'name': 'Tags',
                'url': f"{self.target_domain}/tag/",
                'position': position
            })
            position += 1
            tag_index = url_parts.index('tag')
            if tag_index + 1 < len(url_parts):
                tag_slug = url_parts[tag_index + 1]
                tag_name = tag_slug.replace('-', ' ').title()
                breadcrumb_items.append({
                    'name': tag_name,
                    'url': f"{self.target_domain}/tag/{tag_slug}/",
                    'position': position
                })
        
        elif len(url_parts) >= 3 and url_parts[0].isdigit():
            # Single post: Home > Category > Post Title
            # Extract category from page if available
            categories = soup.find_all('a', rel='tag', href=lambda x: x and '/category/' in x)
            if categories:
                # Use first category
                first_category = categories[0]
                category_url = first_category.get('href', '')
                category_name = first_category.get_text(strip=True)
                
                breadcrumb_items.append({
                    'name': category_name,
                    'url': category_url if category_url.startswith('http') else f"{self.target_domain}{category_url}",
                    'position': position
                })
                position += 1
            
            # Add current page (extract title from h1)
            h1 = soup.find('h1', class_=lambda x: x and 'entry-title' in x)
            if h1:
                page_title = h1.get_text(strip=True)
                breadcrumb_items.append({
                    'name': page_title,
                    'url': f"{self.target_domain}{current_url}",
                    'position': position
                })
        
        else:
            # Generic page: Home > Page Title
            h1 = soup.find('h1')
            if h1:
                page_title = h1.get_text(strip=True)
                breadcrumb_items.append({
                    'name': page_title,
                    'url': f"{self.target_domain}{current_url}",
                    'position': position
                })
        
        # Only proceed if we have more than just Home
        if len(breadcrumb_items) <= 1:
            return
        
        # Create breadcrumb HTML
        breadcrumb_nav = soup.new_tag('nav')
        breadcrumb_nav['class'] = 'breadcrumb-navigation site-container'
        breadcrumb_nav['aria-label'] = 'Breadcrumb'
        
        breadcrumb_ol = soup.new_tag('ol')
        breadcrumb_ol['class'] = 'breadcrumb-list'
        
        for i, item in enumerate(breadcrumb_items):
            li = soup.new_tag('li')
            li['style'] = 'display: inline-flex; align-items: center;'
            
            # Add separator for non-first items
            if i > 0:
                separator = soup.new_tag('span')
                separator['class'] = 'breadcrumb-separator'
                separator.string = '/'
                li.append(separator)
            
            # Last item is current page (no link)
            if i == len(breadcrumb_items) - 1:
                current_span = soup.new_tag('span')
                current_span['class'] = 'breadcrumb-current'
                current_span['aria-current'] = 'page'
                current_span.string = item['name']
                li.append(current_span)
            else:
                link = soup.new_tag('a')
                link['href'] = item['url']
                link['class'] = 'breadcrumb-link'
                link.string = item['name']
                li.append(link)
            
            breadcrumb_ol.append(li)
        
        breadcrumb_nav.append(breadcrumb_ol)
        
        # Find insertion point (after header, before main content)
        main_wrap = soup.find('main', id='inner-wrap')
        if main_wrap:
            # Insert at the beginning of main
            first_child = main_wrap.find()
            if first_child:
                first_child.insert_before(breadcrumb_nav)
            else:
                main_wrap.insert(0, breadcrumb_nav)
            
            # Add BreadcrumbList JSON-LD schema
            if soup.head:
                schema_script = soup.new_tag('script')
                schema_script['type'] = 'application/ld+json'
                
                breadcrumb_list = {
                    "@context": "https://schema.org",
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": item['position'],
                            "name": item['name'],
                            "item": item['url']
                        }
                        for item in breadcrumb_items
                    ]
                }
                
                schema_script.string = json.dumps(breadcrumb_list, ensure_ascii=False, separators=(',', ':'))
                soup.head.append(schema_script)
                
                print(f"   🍞 Added breadcrumb navigation: {' > '.join([item['name'] for item in breadcrumb_items])}")
    
    def add_related_posts(self, soup, current_url):
        """Add related posts section based on categories and tags"""
        
        # Only add to single post pages
        body = soup.find('body')
        if not body:
            return
        
        body_classes = body.get('class', [])
        body_class_str = ' '.join(body_classes).lower()
        
        # Check if this is a single post (not a page or archive)
        if 'single-post' not in body_class_str and 'single' not in body_classes:
            return
        
        # Extract categories and tags from the current post
        categories = []
        tags = []
        
        # Find category links
        category_links = soup.find_all('a', rel='tag', href=lambda x: x and '/category/' in x)
        for link in category_links:
            category_slug = link.get('href', '').split('/category/')[1].strip('/')
            if category_slug and category_slug not in categories:
                categories.append(category_slug)
        
        # Find tag links
        tag_links = soup.find_all('a', rel='tag', href=lambda x: x and '/tag/' in x)
        for link in tag_links:
            tag_slug = link.get('href', '').split('/tag/')[1].strip('/')
            if tag_slug and tag_slug not in tags:
                tags.append(tag_slug)
        
        if not categories and not tags:
            print(f"   ℹ️  No categories or tags found for related posts")
            return
        
        # Query WordPress API for related posts
        try:
            related_posts = []
            
            # First try to get posts from the same categories
            if categories:
                # Get category ID from the first category
                cat_response = self.session.get(
                    f'{self.wp_url}/wp-json/wp/v2/categories',
                    params={'slug': categories[0]}
                )
                if cat_response.status_code == 200:
                    cat_data = cat_response.json()
                    if cat_data:
                        category_id = cat_data[0]['id']
                        
                        # Get posts from this category
                        posts_response = self.session.get(
                            f'{self.wp_url}/wp-json/wp/v2/posts',
                            params={'categories': category_id, 'per_page': 4, '_fields': 'id,title,link,featured_media'}
                        )
                        if posts_response.status_code == 200:
                            related_posts = posts_response.json()
            
            # Filter out current post
            current_post_url = f"{self.wp_url}{current_url}"
            related_posts = [p for p in related_posts if p['link'] != current_post_url][:3]
            
            if not related_posts:
                print(f"   ℹ️  No related posts found")
                return
            
            # Create related posts section
            related_section = soup.new_tag('section')
            related_section['class'] = 'related-posts'
            related_section['style'] = '''margin: 40px 0; padding: 30px; background: #f7fafc; border-radius: 8px; border-left: 4px solid #4299e1;'''
            
            # Section heading
            heading = soup.new_tag('h2')
            heading['style'] = 'margin: 0 0 20px 0; font-size: 24px; color: #2d3748;'
            heading.string = '📚 Related Posts'
            related_section.append(heading)
            
            # Posts list
            posts_list = soup.new_tag('ul')
            posts_list['style'] = 'list-style: none; padding: 0; margin: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;'
            
            for post in related_posts:
                li = soup.new_tag('li')
                li['style'] = 'background: white; padding: 16px; border-radius: 6px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); transition: box-shadow 0.2s;'
                
                link = soup.new_tag('a')
                link['href'] = post['link'].replace(self.wp_url, self.target_domain)
                link['style'] = 'color: #2d3748; text-decoration: none; display: block; font-weight: 500; hover: color: #4299e1;'
                link.string = post['title']['rendered']
                
                li.append(link)
                posts_list.append(li)
            
            related_section.append(posts_list)
            
            # Find insertion point (after entry-content, before comments)
            entry_content = soup.find('div', class_=lambda x: x and 'entry-content' in x)
            if entry_content:
                # Find the parent article
                article = entry_content.find_parent('article')
                if article:
                    # Insert before comments or at the end of article
                    comments = article.find('div', id='comments')
                    if comments:
                        comments.insert_before(related_section)
                    else:
                        article.append(related_section)
                    
                    print(f"   📚 Added {len(related_posts)} related posts")
        
        except Exception as e:
            print(f"   ⚠️  Error fetching related posts: {str(e)}")
    
    def create_security_headers(self):
        """Create _headers file with security headers for Cloudflare Pages"""
        print("🔒 Creating security headers file...")
        
        headers_content = [
            "# Security Headers for jameskilby.co.uk",
            "# Generated by WordPress Static Generator",
            "",
            "# HTML pages - minimal caching for fresh content",
            "/*.html",
            "  Cache-Control: public, max-age=300, must-revalidate",
            "  ",
            "# Root paths - minimal caching",
            "/",
            "  Cache-Control: public, max-age=300, must-revalidate",
            "",
            "# Static assets - longer cache with immutable for versioned files",
            "/wp-content/*",
            "  Cache-Control: public, max-age=31536000, immutable",
            "",
            "/wp-includes/*",
            "  Cache-Control: public, max-age=31536000, immutable",
            "",
            "# Search index - moderate caching",
            "/search-index*.json",
            "  Cache-Control: public, max-age=3600",
            "",
            "# Markdown files - allow CORS for API access",
            "/markdown/*",
            "  Content-Type: text/markdown; charset=utf-8",
            "  Cache-Control: public, max-age=3600",
            "  Access-Control-Allow-Origin: *",
            "  Access-Control-Allow-Methods: GET, HEAD, OPTIONS",
            "",
            "# API endpoints - JSON with CORS",
            "/api/*",
            "  Content-Type: application/json; charset=utf-8",
            "  Cache-Control: public, max-age=600",
            "  Access-Control-Allow-Origin: *",
            "  Access-Control-Allow-Methods: GET, HEAD, OPTIONS",
            "  Access-Control-Allow-Headers: Content-Type",
            "",
            "# Global security headers",
            "/*",
            "  # Clickjacking Protection - prevents site from being embedded in iframes",
            "  X-Frame-Options: SAMEORIGIN",
            "  ",
            "  # XSS Protection for older browsers",
            "  X-XSS-Protection: 1; mode=block",
            "  ",
            "  # Force HTTPS for 1 year (31536000 seconds)",
            "  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
            "  ",
            "  # Control browser features - deny access to device APIs",
            "  Permissions-Policy: geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=()",
            "  ",
            "  # Content Security Policy - controls what resources can load",
            "  Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https: cdn.jsdelivr.net plausible.jameskilby.cloud utteranc.es github.com static.cloudflareinsights.com cdn.credly.com cdn.youracclaim.com; style-src 'self' 'unsafe-inline' https: github.com; img-src 'self' data: https:; font-src 'self' data: https:; connect-src 'self' https: plausible.jameskilby.cloud; frame-src https://www.youtube.com https://player.vimeo.com https://embed.acast.com https://utteranc.es https://plausible.jameskilby.cloud https://www.credly.com https://www.youracclaim.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'",
        ]
        
        headers_file = self.output_dir / '_headers'
        headers_file.write_text('\n'.join(headers_content))
        print("   ✅ Created _headers file with security headers")
        print("   🔒 Security headers: X-Frame-Options, CSP, HSTS, Permissions-Policy")
    
    def create_redirects_file(self):
        """Create redirects for old URLs (Netlify/Cloudflare format)"""
        redirects_content = [
            "# Redirect www to non-www (canonical URL)",
            "# Note: Cloudflare's 'Always Use HTTPS' runs first, so HTTP www gets 2 hops",
            "# This is normal and acceptable for the rare HTTP www case",
            "www.jameskilby.co.uk/* jameskilby.co.uk/:splat 301",
            "",
            "# Automatic redirects for spelling corrections",
            "/2025/04/warp-the-inteligent-terminal/ /2025/04/warp-the-intelligent-terminal/ 301",
            "/category/artificial-inteligence/ /category/artificial-intelligence/ 301"
        ]
        
        redirects_file = self.output_dir / '_redirects'
        redirects_file.write_text('\n'.join(redirects_content))
        print("✅ Created _redirects file for URL corrections and www redirect")
    
    def create_robots_txt(self):
        """
        Download robots.txt from WordPress and update URLs for static site
        """
        print("🤖 Creating robots.txt...")
        
        try:
            # Download robots.txt from WordPress
            robots_url = f"{self.wp_url}/robots.txt"
            response = self.session.get(robots_url, timeout=10)
            
            if response.status_code == 200 and 'text/plain' in response.headers.get('content-type', ''):
                # Get robots.txt content
                robots_content = response.text
                
                # Replace WordPress URLs with target domain URLs
                robots_content = robots_content.replace(self.wp_url, self.target_domain)
                
                # Update sitemap reference to point to our generated sitemap
                import re
                robots_content = re.sub(
                    r'Sitemap:\s*https?://[^\n]+',
                    f'Sitemap: {self.target_domain}/sitemap.xml',
                    robots_content,
                    flags=re.IGNORECASE
                )
                
                # Write to static output
                robots_file = self.output_dir / 'robots.txt'
                robots_file.write_text(robots_content)
                print(f"   ✅ Downloaded and updated robots.txt from WordPress")
                
            else:
                # WordPress doesn't have robots.txt, create a basic one
                print(f"   ⚠️  WordPress robots.txt not found, creating default")
                self._create_default_robots_txt()
                
        except Exception as e:
            print(f"   ⚠️  Error downloading robots.txt: {str(e)}")
            print(f"   🔧 Creating default robots.txt")
            self._create_default_robots_txt()
    
    def _create_default_robots_txt(self):
        """Create a default robots.txt file"""
        robots_content = [
            "User-agent: *",
            "Allow: /",
            "",
            f"Sitemap: {self.target_domain}/sitemap.xml",
            ""
        ]
        
        robots_file = self.output_dir / 'robots.txt'
        robots_file.write_text('\n'.join(robots_content))
        print(f"   ✅ Created default robots.txt")
    
    def create_sitemap(self):
        """Generate a basic XML sitemap"""
        urls_for_sitemap = []

        # Collect all HTML files with their modification dates
        for html_file in self.output_dir.rglob('*.html'):
            relative_path = html_file.relative_to(self.output_dir)
            if relative_path.name == 'index.html':
                if relative_path.parent == Path('.'):
                    url_path = '/'
                else:
                    url_path = f'/{relative_path.parent}/'
            else:
                url_path = f'/{relative_path.with_suffix("")}/'

            # Extract modification date from HTML
            lastmod_date = self._extract_modified_date(html_file)

            urls_for_sitemap.append({
                'url': f'{self.target_domain}{url_path}',
                'lastmod': lastmod_date
            })

        # Generate XML
        sitemap_content = ['<?xml version="1.0" encoding="UTF-8"?>']
        sitemap_content.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

        # Sort by URL and remove duplicates
        seen_urls = set()
        for item in sorted(urls_for_sitemap, key=lambda x: x['url']):
            if item['url'] not in seen_urls:
                seen_urls.add(item['url'])
                sitemap_content.append('  <url>')
                sitemap_content.append(f'    <loc>{item["url"]}</loc>')
                sitemap_content.append(f'    <lastmod>{item["lastmod"]}</lastmod>')
                sitemap_content.append('  </url>')

        sitemap_content.append('</urlset>')

        sitemap_file = self.output_dir / 'sitemap.xml'
        sitemap_file.write_text('\n'.join(sitemap_content))
        print(f"✅ Created sitemap.xml with {len(seen_urls)} URLs")

    def _extract_modified_date(self, html_file):
        """Extract modification date from HTML file's Schema.org JSON-LD"""
        try:
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()

            soup = BeautifulSoup(html_content, 'html.parser')

            # Look for Schema.org JSON-LD script
            json_ld_scripts = soup.find_all('script', type='application/ld+json')

            for script in json_ld_scripts:
                try:
                    data = json.loads(script.string)

                    # Handle both single objects and @graph arrays
                    items = data.get('@graph', [data]) if isinstance(data, dict) else [data]

                    for item in items:
                        if isinstance(item, dict):
                            # Look for dateModified in Article, BlogPosting, or WebPage
                            if item.get('@type') in ['Article', 'BlogPosting', 'WebPage']:
                                date_modified = item.get('dateModified')
                                if date_modified:
                                    # Parse and format date (handle ISO8601 format)
                                    parsed_date = datetime.fromisoformat(date_modified.replace('Z', '+00:00'))
                                    return parsed_date.strftime('%Y-%m-%d')
                except (json.JSONDecodeError, ValueError, AttributeError):
                    continue

            # Fallback: try to get file modification time
            file_mtime = html_file.stat().st_mtime
            return datetime.fromtimestamp(file_mtime).strftime('%Y-%m-%d')

        except Exception as e:
            # Ultimate fallback: use current date
            return datetime.now().strftime('%Y-%m-%d')

    def generate_rss_feed(self):
        """Generate RSS feed from posts"""
        print("📡 Generating RSS feed...")
        
        # Collect all post information
        posts = []
        
        # Look for post directories (year/month pattern)
        for year_dir in sorted(self.output_dir.glob('[0-9][0-9][0-9][0-9]'), reverse=True):
            for month_dir in sorted(year_dir.glob('[0-9][0-9]'), reverse=True):
                for post_dir in month_dir.iterdir():
                    if post_dir.is_dir():
                        index_file = post_dir / 'index.html'
                        if index_file.exists():
                            try:
                                with open(index_file, 'r', encoding='utf-8', errors='ignore') as f:
                                    html_content = f.read()
                                
                                soup = BeautifulSoup(html_content, 'html.parser')
                                
                                # Extract title
                                title_tag = soup.find('h1', class_=re.compile(r'entry-title', re.I))
                                if not title_tag:
                                    title_tag = soup.find('title')
                                title = title_tag.get_text().strip() if title_tag else 'Untitled'
                                title = re.sub(r'\s*[-–|]\s*jameskilby.*$', '', title, flags=re.IGNORECASE)
                                
                                # Extract description
                                meta_desc = soup.find('meta', attrs={'name': 'description'})
                                description = meta_desc.get('content', '').strip() if meta_desc else ''
                                
                                if not description:
                                    # Try to get excerpt from content
                                    content_div = soup.find('div', class_=re.compile(r'entry-content|entry-summary', re.I))
                                    if content_div:
                                        for script in content_div(["script", "style"]):
                                            script.decompose()
                                        text = content_div.get_text()
                                        words = text.split()[:50]
                                        description = ' '.join(words) + ('...' if len(words) >= 50 else '')
                                
                                # Extract date
                                date_elem = soup.find('time', class_=re.compile(r'published', re.I))
                                pub_date = ''
                                if date_elem:
                                    datetime_str = date_elem.get('datetime', '')
                                    if datetime_str:
                                        try:
                                            from email.utils import format_datetime
                                            from datetime import datetime as dt
                                            dt_obj = dt.fromisoformat(datetime_str.replace('Z', '+00:00'))
                                            pub_date = format_datetime(dt_obj)
                                        except:
                                            pub_date = datetime_str
                                
                                # Extract author
                                author_elem = soup.find('a', class_=re.compile(r'author|fn', re.I))
                                author = author_elem.get_text().strip() if author_elem else 'James Kilby'
                                
                                # Construct URL
                                relative_path = post_dir.relative_to(self.output_dir)
                                url = f"{self.target_domain}/{relative_path}/"
                                
                                posts.append({
                                    'title': title,
                                    'description': description,
                                    'link': url,
                                    'pub_date': pub_date,
                                    'author': author
                                })
                            except Exception as e:
                                print(f"   ⚠️  Error processing {post_dir}: {str(e)}")
                                continue
        
        # Sort posts by date (newest first) - take top 20
        posts = posts[:20]
        
        if not posts:
            print("   ⚠️  No posts found for RSS feed")
            return
        
        # Generate RSS XML
        from xml.sax.saxutils import escape
        
        rss_lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
            '  <channel>',
            '    <title>Jameskilbycouk</title>',
            f'    <link>{self.target_domain}/</link>',
            '    <description>VMware and cloud infrastructure tutorials, homelab guides, and DevOps insights</description>',
            '    <language>en-gb</language>',
            f'    <lastBuildDate>{datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>',
            f'    <atom:link href="{self.target_domain}/feed/index.xml" rel="self" type="application/rss+xml" />',
        ]
        
        for post in posts:
            rss_lines.extend([
                '    <item>',
                f'      <title>{escape(post["title"])}</title>',
                f'      <link>{escape(post["link"])}</link>',
                f'      <description>{escape(post["description"])}</description>',
                f'      <author>{escape(post["author"])}</author>',
                f'      <guid isPermaLink="true">{escape(post["link"])}</guid>',
            ])
            if post['pub_date']:
                rss_lines.append(f'      <pubDate>{escape(post["pub_date"])}</pubDate>')
            rss_lines.append('    </item>')
        
        rss_lines.extend([
            '  </channel>',
            '</rss>'
        ])
        
        # Save RSS feed
        feed_dir = self.output_dir / 'feed'
        feed_dir.mkdir(exist_ok=True)
        
        feed_file = feed_dir / 'index.xml'
        feed_file.write_text('\n'.join(rss_lines), encoding='utf-8')
        
        # Also create a simple HTML redirect for /feed/
        feed_html = feed_dir / 'index.html'
        feed_html.write_text(
            '<!DOCTYPE html>\n'
            '<html><head>\n'
            '<meta http-equiv="refresh" content="0; url=index.xml" />\n'
            '<link rel="alternate" type="application/rss+xml" href="index.xml" />\n'
            '</head><body>\n'
            '<p>Redirecting to <a href="index.xml">RSS feed</a>...</p>\n'
            '</body></html>',
            encoding='utf-8'
        )
        
        print(f"   ✅ Created RSS feed with {len(posts)} posts")
        print(f"   📡 Feed URL: {self.target_domain}/feed/index.xml")
    
    def copy_assets(self):
        """Copy assets directory (fonts, CSS, etc.) to output"""
        print("📦 Copying static assets...")
        
        # Copy assets directory from project root
        assets_src = Path(__file__).parent / 'assets'
        assets_dest = self.output_dir / 'assets'
        
        if assets_src.exists():
            shutil.copytree(assets_src, assets_dest, dirs_exist_ok=True)
            
            # Count files copied
            file_count = sum(1 for _ in assets_dest.rglob('*') if _.is_file())
            total_size = sum(f.stat().st_size for f in assets_dest.rglob('*') if f.is_file())
            
            print(f"   ✅ Copied {file_count} asset files ({total_size / 1024:.1f}KB)")
            print(f"   📁 Assets directory: {assets_dest}")
        else:
            print(f"   ℹ️  No assets directory found at {assets_src}")
    
    def copy_search_script(self):
        """Copy search script to public/js directory"""
        print("📋 Copying search script...")

        # Create js directory
        js_dir = self.output_dir / 'js'
        js_dir.mkdir(exist_ok=True)

        # Copy search.js from project root
        search_script_src = Path(__file__).parent / 'search.js'
        search_script_dest = js_dir / 'search.js'

        if search_script_src.exists():
            shutil.copy(search_script_src, search_script_dest)
            print(f"   ✅ Copied search.js to public/js/search.js")
        else:
            print(f"   ⚠️  search.js not found at {search_script_src}")

    def copy_static_root_files(self):
        """Copy static files (favicons, manifest) to public root"""
        print("🎨 Copying favicon and manifest files...")

        # Source directory for static root files
        static_src = Path(__file__).parent / 'static-files'

        if not static_src.exists():
            print(f"   ℹ️  No static-files directory found at {static_src}")
            return

        # Copy all files from static-files to public root
        file_count = 0
        for file_path in static_src.iterdir():
            if file_path.is_file():
                dest_path = self.output_dir / file_path.name
                shutil.copy(file_path, dest_path)
                file_count += 1
                print(f"   ✅ Copied {file_path.name} to public root")

        if file_count > 0:
            print(f"   📁 Total files copied: {file_count}")
        else:
            print(f"   ℹ️  No files to copy from {static_src}")

    def inject_search_script(self):
        """Inject search script into all HTML files"""
        print("📝 Injecting search script into HTML files...")
        
        injected_count = 0
        
        # Find all HTML files
        for html_file in self.output_dir.rglob('*.html'):
            try:
                # Read HTML
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    html_content = f.read()
                
                # Check if search script is already injected
                if '<script src="/js/search.js"' in html_content:
                    continue
                
                # Find closing body tag and inject script before it
                if '</body>' in html_content:
                    search_script_tag = '<script src="/js/search.js" data-cfasync="false"></script>\n</body>'
                    html_content = html_content.replace('</body>', search_script_tag)
                    
                    # Write back to file
                    with open(html_file, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    
                    injected_count += 1
            except Exception as e:
                print(f"   ⚠️  Error injecting script into {html_file}: {str(e)}")
                continue
        
        if injected_count > 0:
            print(f"   ✅ Injected search script into {injected_count} HTML files")
        else:
            print(f"   ℹ️  No HTML files needed script injection")
    
    def generate_search_index(self):
        """Generate search index for client-side search functionality"""
        print("🔍 Generating search index...")
        
        search_index = []
        
        # Process all HTML files
        for html_file in self.output_dir.rglob('*.html'):
            try:
                relative_path = html_file.relative_to(self.output_dir)
                
                # Convert file path to URL path
                if relative_path.name == 'index.html':
                    if relative_path.parent == Path('.'):
                        url_path = '/'
                    else:
                        url_path = f'/{relative_path.parent}/'
                else:
                    url_path = f'/{relative_path}'
                
                # Read and parse HTML
                with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                    html_content = f.read()
                
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Skip redirects and error pages
                if soup.find('meta', attrs={'http-equiv': 'refresh'}):
                    continue
                
                # Extract metadata
                title_tag = soup.find('title')
                title = title_tag.get_text().strip() if title_tag else "Untitled"
                
                # Clean up title (remove site name)
                title = re.sub(r'\s*[-–|]\s*jameskilby.*$', '', title, flags=re.IGNORECASE)
                
                # Skip if no meaningful title
                if not title or title.lower() in ['untitled', 'page not found', '404']:
                    continue
                
                # Meta description
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc.get('content', '').strip() if meta_desc else ''
                
                # Extract excerpt from content if no description
                if not description:
                    content_areas = soup.find_all(['div'], class_=re.compile(r'(content|entry|post|article)', re.I))
                    if content_areas:
                        # Remove script and style elements
                        for script in content_areas[0](["script", "style", "nav", "footer"]):
                            script.decompose()
                        
                        content_text = content_areas[0].get_text()
                        # Clean up whitespace
                        lines = (line.strip() for line in content_text.splitlines())
                        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                        content_text = ' '.join(chunk for chunk in chunks if chunk)
                        
                        # Take first 150 words as excerpt
                        words = content_text.split()
                        description = ' '.join(words[:150]) + ('...' if len(words) > 150 else '')
                
                # Extract full content for searching (limit to 1000 chars)
                # Remove script and style elements
                content_soup = BeautifulSoup(html_content, 'html.parser')
                for script in content_soup(["script", "style", "nav", "footer"]):
                    script.decompose()
                
                full_content = content_soup.get_text()
                # Clean up whitespace
                lines = (line.strip() for line in full_content.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                full_content = ' '.join(chunk for chunk in chunks if chunk)
                
                # Skip if content is too short (likely navigation pages)
                if len(full_content.split()) < 50:
                    continue
                
                # Extract categories and tags
                categories = []
                tags = []
                
                # Look for category and tag links
                cat_links = soup.find_all('a', href=re.compile(r'/category/'))
                for link in cat_links:
                    cat_text = link.get_text().strip()
                    if cat_text and cat_text not in categories:
                        categories.append(cat_text)
                
                tag_links = soup.find_all('a', href=re.compile(r'/tag/'))
                for link in tag_links:
                    tag_text = link.get_text().strip()
                    if tag_text and tag_text not in tags:
                        tags.append(tag_text)
                
                # Extract date
                date = ""
                date_elem = soup.find('time', class_=re.compile(r'(entry-date|published)', re.I))
                if date_elem:
                    date = date_elem.get('datetime', '') or date_elem.get_text().strip()
                
                # Create search entry
                entry = {
                    'title': title,
                    'url': f"{self.target_domain}{url_path}",
                    'description': description[:200] if description else '',  # Limit description length
                    'content': full_content[:1000],  # Limit content for searching
                    'categories': categories,
                    'tags': tags,
                    'date': date
                }
                
                search_index.append(entry)
                
            except Exception as e:
                print(f"❌ Error indexing {html_file}: {str(e)}")
                continue
        
        # Save search index
        if search_index:
            # Save full version
            search_index_file = self.output_dir / 'search-index.json'
            with open(search_index_file, 'w', encoding='utf-8') as f:
                json.dump(search_index, f, ensure_ascii=False, indent=2)
            
            # Save minified version
            search_index_min_file = self.output_dir / 'search-index.min.json'
            with open(search_index_min_file, 'w', encoding='utf-8') as f:
                json.dump(search_index, f, ensure_ascii=False, separators=(',', ':'))
            
            print(f"✅ Generated search index with {len(search_index)} entries")
            print(f"   📄 Full: search-index.json ({search_index_file.stat().st_size / 1024:.1f}KB)")
            print(f"   📄 Min: search-index.min.json ({search_index_min_file.stat().st_size / 1024:.1f}KB)")
        else:
            print("⚠️  No content found for search index")
    
    def generate_static_site(self):
        """Main generation process"""
        print(f"🚀 WordPress to Static Site Generator")
        print(f"Source: {self.wp_url}")
        print(f"Target: {self.target_domain}")
        print(f"Output: {self.output_dir}")
        
        # Show build mode
        if self.incremental_builder:
            cache_stats = self.incremental_builder.get_stats()
            if cache_stats['last_build']:
                print(f"Mode: Incremental (cache has {cache_stats['posts_cached'] + cache_stats['pages_cached']} entries)")
            else:
                print(f"Mode: Full build (creating cache)")
        else:
            print(f"Mode: Full build (incremental disabled)")
        
        print("=" * 60)
        
        start_time = time.time()
        
        # For incremental builds, don't clean output directory
        # For full builds, clean it
        if self.incremental_builder and self.incremental_builder.cache.get('last_build_time'):
            print("♻️  Incremental build - preserving existing output...")
            if not self.output_dir.exists():
                self.output_dir.mkdir(parents=True)
        else:
            # Clean output directory for full builds
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
        error_count = len(results) - success_count
        print(f"\\n📊 Processing Results:")
        print(f"   ✅ Success: {success_count}")
        print(f"   ❌ Failed: {error_count}")
        
        # Download assets
        print(f"\\n📁 Asset Processing:")
        self.download_assets()
        
        # Copy static assets (fonts, CSS, etc.)
        print(f"\n📦 Static Assets:")
        self.copy_assets()
        
        # Create additional files
        print(f"\n📄 Creating additional files:")
        self.create_security_headers()
        self.create_robots_txt()
        self.create_redirects_file()
        self.create_sitemap()
        self.generate_rss_feed()
        self.generate_search_index()
        self.copy_search_script()
        self.copy_static_root_files()
        self.inject_search_script()
        
        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print(f"\\n🎉 GENERATION COMPLETE!")
        print(f"Duration: {duration:.1f} seconds")
        print(f"Output directory: {self.output_dir}")
        
        # Show directory size
        total_size = sum(f.stat().st_size for f in self.output_dir.rglob('*') if f.is_file())
        print(f"Total size: {total_size / 1024 / 1024:.1f} MB")
        
        # Generate build metrics report
        print(f"\n📊 Generating build report:")
        try:
            from generate_build_report import generate_build_metrics
            generate_build_metrics(
                output_dir=self.output_dir,
                duration=duration,
                urls_processed=len(urls),
                assets_downloaded=len(self.downloaded_assets),
                error_count=error_count
            )
        except Exception as e:
            print(f"   ⚠️  Failed to generate build report: {str(e)}")
        
        # Finalize incremental build cache
        if self.incremental_builder:
            is_full_build = not self.incremental_builder.cache.get('last_build_time')
            self.incremental_builder.finalize_build(is_full_build=is_full_build)
            
            # Show cache statistics
            stats = self.incremental_builder.get_stats()
            print(f"\n📦 Build Cache:")
            print(f"   Cached posts: {stats['posts_cached']}")
            print(f"   Cached pages: {stats['pages_cached']}")
            if not is_full_build:
                print(f"   ⚡ Time saved vs full build: ~{100 - int((duration / 12) * 100)}%")
        
        return True

def main():
    if len(sys.argv) < 2:
        print("Usage: python wp_to_static_generator.py <output_directory> [--deploy] [--no-incremental]")
        print("Example: python wp_to_static_generator.py ./static-site-output")
        print("Options:")
        print("  --no-incremental    Force full build (ignore cache)")
        sys.exit(1)
    
    output_dir = sys.argv[1]
    deploy_flag = '--deploy' in sys.argv
    use_incremental = '--no-incremental' not in sys.argv
    
    # Import configuration
    from config import Config
    
    # Get authentication token from environment
    AUTH_TOKEN = os.getenv('WP_AUTH_TOKEN')
    
    if not AUTH_TOKEN:
        print('❌ Error: WP_AUTH_TOKEN environment variable is required')
        print('   Set it with: export WP_AUTH_TOKEN="your_token_here"')
        sys.exit(1)
    
    # Create generator instance
    generator = WordPressStaticGenerator(
        wp_url=Config.WP_URL,
        auth_token=AUTH_TOKEN,
        output_dir=output_dir,
        target_domain=Config.TARGET_DOMAIN,
        use_incremental=use_incremental
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
