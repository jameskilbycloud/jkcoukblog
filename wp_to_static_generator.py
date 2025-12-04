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
        
        # Add Utterances comments to every page
        self.add_utterances_comments(soup)
        
        # Fix inline CSS font URLs
        self.fix_inline_css_urls(soup)
        
        # Process WordPress embeds (convert to proper iframes)
        self.process_wordpress_embeds(soup)
        
        # Extract and queue assets for download
        self.extract_assets(soup, current_url)
        
        # Clean up WordPress admin AJAX URLs
        self.clean_wordpress_ajax_urls(soup)
        
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
                    updated_content = script_content.replace(
                        f'"ajaxurl":"https:\\/\\/wordpress.jameskilby.cloud\\/wp-admin\\/admin-ajax.php"',
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
        
        # Find the best insertion point - right after the main article, before author/related sections
        insertion_point = None
        
        # Try to find existing comments area first
        comments_area = soup.find('div', id='comments')
        if comments_area:
            # Replace existing comments with Utterances
            insertion_point = comments_area
        else:
            # Find the main article element (only if single article)
            if articles and len(articles) == 1:
                article = articles[0]
                
                # Look for entry-content div inside the article - this is the main post content
                entry_content = article.find('div', class_=lambda x: x and 'entry-content' in x)
                
                if entry_content:
                    # Insert immediately after entry-content, before any other sections
                    insertion_point = entry_content
                else:
                    # Fallback: insert after the article itself
                    insertion_point = article
        
        if insertion_point:
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
            script['repo'] = 'jameskilbynet/jkcoukblog'
            script['issue-term'] = 'pathname'
            script['theme'] = 'github-light'
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
            else:
                # Insert immediately after the entry-content or article
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
        
        # Add Plausible analytics if not already present
        self.add_plausible_analytics(soup)
        
        # Add preload hints for critical resources
        for link in soup.find_all('link', rel='stylesheet'):
            if link.get('href'):
                preload = soup.new_tag('link')
                preload['rel'] = 'preload'
                preload['as'] = 'style'
                preload['href'] = link['href']
                soup.head.insert(0, preload)
    
    def add_plausible_analytics(self, soup):
        """Add Plausible Analytics script to the page if not already present"""
        if not soup.head:
            return
        
        # Check if Plausible script is already present
        plausible_domain = 'plausible.jameskilby.cloud'
        plausible_script_url = f'https://{plausible_domain}/js/script.js'
        target_analytics_domain = 'jameskilby.co.uk'
        
        # Look for existing Plausible script
        existing_plausible = soup.find('script', src=lambda x: x and 'plausible' in x and 'script.js' in x)
        
        if existing_plausible:
            # Update the data-domain attribute to ensure it's correct
            existing_plausible['data-domain'] = target_analytics_domain
            existing_plausible['defer'] = ''
            print(f"   📊 Updated existing Plausible analytics configuration")
        else:
            # Add new Plausible script
            plausible_script = soup.new_tag('script')
            plausible_script['data-domain'] = target_analytics_domain
            plausible_script['defer'] = ''
            plausible_script['src'] = plausible_script_url
            soup.head.append(plausible_script)
            print(f"   📊 Added Plausible analytics script to page")
    
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
        self.generate_search_index()
        
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