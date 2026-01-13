#!/usr/bin/env python3
"""
WordPress Media Asset Checker
Reviews all posts and pages to identify missing media assets
"""

import os
import sys
import requests
import re
from collections import defaultdict
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from config import Config

class MediaAssetChecker:
    def __init__(self, wp_url, auth_token):
        self.wp_url = wp_url.rstrip('/')
        self.auth_token = auth_token
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Basic {auth_token}',
            'User-Agent': 'MediaAssetChecker/1.0'
        })
        self.all_media_urls = set()
        self.referenced_media = set()
        self.missing_media = defaultdict(list)
        
    def get_all_media_from_api(self):
        """Get all media assets from WordPress Media API"""
        print("🖼️  Fetching all media from WordPress Media API...")
        
        page = 1
        total_media = 0
        
        while True:
            try:
                response = self.session.get(
                    f'{self.wp_url}/wp-json/wp/v2/media',
                    params={'per_page': 100, 'page': page, 'status': 'any'},
                    timeout=30
                )
                
                if response.status_code != 200:
                    if page == 1:
                        print(f"   ❌ Error fetching media: {response.status_code}")
                        print(f"   Response: {response.text[:200]}")
                    break
                    
                media_items = response.json()
                if not media_items:
                    break
                    
                for media_item in media_items:
                    # Get the main media URL
                    if 'source_url' in media_item:
                        self.all_media_urls.add(media_item['source_url'])
                    
                    # Get different size variants if available
                    if 'media_details' in media_item and 'sizes' in media_item['media_details']:
                        sizes = media_item['media_details']['sizes']
                        for size_name, size_data in sizes.items():
                            if 'source_url' in size_data:
                                self.all_media_urls.add(size_data['source_url'])
                    
                    total_media += 1
                
                print(f"   📄 Page {page}: {len(media_items)} items")
                page += 1
                
            except Exception as e:
                print(f"   ❌ Error on page {page}: {str(e)}")
                break
        
        print(f"✅ Found {total_media} media items with {len(self.all_media_urls)} total URLs (including sizes)")
        return self.all_media_urls
    
    def extract_media_from_content(self, content, content_type, content_id, content_title):
        """Extract media references from HTML content"""
        if not content:
            return
            
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract images from <img> tags
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                self.referenced_media.add(src)
                # Check if this media exists in our media library
                if not self.is_media_available(src):
                    self.missing_media[content_id].append({
                        'type': content_type,
                        'title': content_title,
                        'media_type': 'image',
                        'url': src,
                        'alt': img.get('alt', ''),
                        'context': str(img)[:200]
                    })
        
        # Extract from <picture> tags
        for picture in soup.find_all('picture'):
            for source in picture.find_all('source'):
                srcset = source.get('srcset')
                if srcset:
                    # Parse srcset which can contain multiple URLs
                    for src_item in srcset.split(','):
                        src = src_item.strip().split()[0]
                        self.referenced_media.add(src)
                        if not self.is_media_available(src):
                            self.missing_media[content_id].append({
                                'type': content_type,
                                'title': content_title,
                                'media_type': 'picture_source',
                                'url': src,
                                'context': str(source)[:200]
                            })
        
        # Extract from background images in style attributes
        for element in soup.find_all(style=True):
            style = element.get('style', '')
            bg_images = re.findall(r'url\([\'"]?([^\'"]+)[\'"]?\)', style)
            for bg_img in bg_images:
                self.referenced_media.add(bg_img)
                if not self.is_media_available(bg_img):
                    self.missing_media[content_id].append({
                        'type': content_type,
                        'title': content_title,
                        'media_type': 'background_image',
                        'url': bg_img,
                        'context': style[:200]
                    })
        
        # Extract from video sources
        for video in soup.find_all('video'):
            src = video.get('src')
            if src:
                self.referenced_media.add(src)
                if not self.is_media_available(src):
                    self.missing_media[content_id].append({
                        'type': content_type,
                        'title': content_title,
                        'media_type': 'video',
                        'url': src,
                        'context': str(video)[:200]
                    })
            
            for source in video.find_all('source'):
                src = source.get('src')
                if src:
                    self.referenced_media.add(src)
                    if not self.is_media_available(src):
                        self.missing_media[content_id].append({
                            'type': content_type,
                            'title': content_title,
                            'media_type': 'video_source',
                            'url': src,
                            'context': str(source)[:200]
                        })
        
        # Extract from audio sources
        for audio in soup.find_all('audio'):
            src = audio.get('src')
            if src:
                self.referenced_media.add(src)
                if not self.is_media_available(src):
                    self.missing_media[content_id].append({
                        'type': content_type,
                        'title': content_title,
                        'media_type': 'audio',
                        'url': src,
                        'context': str(audio)[:200]
                    })
    
    def is_media_available(self, url):
        """Check if a media URL is in the WordPress media library"""
        # Normalize URL for comparison
        parsed = urlparse(url)
        
        # Check direct match
        if url in self.all_media_urls:
            return True
        
        # Check if path matches any media URL
        for media_url in self.all_media_urls:
            media_parsed = urlparse(media_url)
            if parsed.path == media_parsed.path:
                return True
        
        # Check if it's an external URL (not from WordPress)
        if not parsed.netloc or parsed.netloc not in url:
            # Relative URL or same domain
            return False
        
        # External URLs are considered "available" (not missing from WP)
        if 'jameskilby' not in parsed.netloc:
            return True
        
        return False
    
    def check_posts(self):
        """Check all posts for media references"""
        print("\n📝 Checking posts for media references...")
        
        page = 1
        total_posts = 0
        
        while True:
            try:
                response = self.session.get(
                    f'{self.wp_url}/wp-json/wp/v2/posts',
                    params={'per_page': 100, 'page': page, 'status': 'publish'},
                    timeout=30
                )
                
                if response.status_code != 200:
                    if page == 1:
                        print(f"   ❌ Error fetching posts: {response.status_code}")
                    break
                    
                posts = response.json()
                if not posts:
                    break
                    
                for post in posts:
                    post_id = post['id']
                    post_title = post['title']['rendered']
                    
                    # Check content
                    if 'content' in post and 'rendered' in post['content']:
                        self.extract_media_from_content(
                            post['content']['rendered'],
                            'post',
                            post_id,
                            post_title
                        )
                    
                    # Check excerpt
                    if 'excerpt' in post and 'rendered' in post['excerpt']:
                        self.extract_media_from_content(
                            post['excerpt']['rendered'],
                            'post',
                            post_id,
                            post_title
                        )
                    
                    # Check featured media
                    if post.get('featured_media', 0) > 0:
                        # This will be checked separately via media API
                        pass
                    
                    total_posts += 1
                
                print(f"   📄 Page {page}: {len(posts)} posts checked")
                page += 1
                
            except Exception as e:
                print(f"   ❌ Error on page {page}: {str(e)}")
                break
        
        print(f"✅ Checked {total_posts} posts")
    
    def check_pages(self):
        """Check all pages for media references"""
        print("\n📑 Checking pages for media references...")
        
        page = 1
        total_pages = 0
        
        while True:
            try:
                response = self.session.get(
                    f'{self.wp_url}/wp-json/wp/v2/pages',
                    params={'per_page': 100, 'page': page, 'status': 'publish'},
                    timeout=30
                )
                
                if response.status_code != 200:
                    if page == 1:
                        print(f"   ❌ Error fetching pages: {response.status_code}")
                    break
                    
                pages = response.json()
                if not pages:
                    break
                    
                for page_item in pages:
                    page_id = page_item['id']
                    page_title = page_item['title']['rendered']
                    
                    # Check content
                    if 'content' in page_item and 'rendered' in page_item['content']:
                        self.extract_media_from_content(
                            page_item['content']['rendered'],
                            'page',
                            page_id,
                            page_title
                        )
                    
                    total_pages += 1
                
                print(f"   📄 Page {page}: {len(pages)} pages checked")
                page += 1
                
            except Exception as e:
                print(f"   ❌ Error on page {page}: {str(e)}")
                break
        
        print(f"✅ Checked {total_pages} pages")
    
    def verify_media_accessibility(self):
        """Verify that missing media URLs are truly inaccessible"""
        print("\n🔍 Verifying accessibility of potentially missing media...")
        
        verified_missing = defaultdict(list)
        
        for content_id, media_list in self.missing_media.items():
            for media in media_list:
                url = media['url']
                
                # Try to access the URL
                try:
                    response = requests.head(url, timeout=5, allow_redirects=True)
                    if response.status_code == 404:
                        verified_missing[content_id].append(media)
                        print(f"   ❌ 404: {url}")
                    elif response.status_code >= 400:
                        verified_missing[content_id].append(media)
                        print(f"   ⚠️  {response.status_code}: {url}")
                except Exception as e:
                    # If we can't access it, consider it missing
                    verified_missing[content_id].append(media)
                    print(f"   ⚠️  Error accessing: {url} - {str(e)[:50]}")
        
        self.missing_media = verified_missing
    
    def generate_report(self):
        """Generate a report of missing media"""
        print("\n" + "="*80)
        print("📊 MISSING MEDIA REPORT")
        print("="*80)
        
        if not self.missing_media:
            print("\n✅ No missing media found! All referenced media assets are available.")
            return
        
        print(f"\n⚠️  Found missing media in {len(self.missing_media)} content items")
        print(f"📊 Total referenced media URLs: {len(self.referenced_media)}")
        print(f"🖼️  Total available media URLs: {len(self.all_media_urls)}")
        
        # Group by content
        for content_id, media_list in sorted(self.missing_media.items()):
            if media_list:
                first_item = media_list[0]
                print(f"\n{'─'*80}")
                print(f"📄 {first_item['type'].upper()}: {first_item['title']}")
                print(f"   ID: {content_id}")
                print(f"   Missing items: {len(media_list)}")
                
                for media in media_list:
                    print(f"\n   ❌ {media['media_type'].upper()}")
                    print(f"      URL: {media['url']}")
                    if 'alt' in media and media['alt']:
                        print(f"      Alt: {media['alt']}")
                    print(f"      Context: {media['context'][:150]}...")
        
        print("\n" + "="*80)
        print(f"📊 SUMMARY: {sum(len(m) for m in self.missing_media.values())} total missing media items")
        print("="*80)
    
    def run(self, verify_accessibility=True):
        """Run the complete media check"""
        print("="*80)
        print("WordPress Media Asset Checker")
        print("="*80)
        
        # Step 1: Get all media from WordPress
        self.get_all_media_from_api()
        
        # Step 2: Check posts
        self.check_posts()
        
        # Step 3: Check pages
        self.check_pages()
        
        # Step 4: Optionally verify accessibility
        if verify_accessibility and self.missing_media:
            self.verify_media_accessibility()
        
        # Step 5: Generate report
        self.generate_report()


def main():
    """Main entry point"""
    # Get configuration
    config = Config()
    
    # Get auth token from environment
    auth_token = os.environ.get('WP_AUTH_TOKEN')
    if not auth_token:
        print("❌ Error: WP_AUTH_TOKEN environment variable not set")
        print("Please set it with: export WP_AUTH_TOKEN='your_token_here'")
        sys.exit(1)
    
    # Create checker
    checker = MediaAssetChecker(config.WP_URL, auth_token)
    
    # Run the check
    verify = '--no-verify' not in sys.argv
    checker.run(verify_accessibility=verify)


if __name__ == '__main__':
    main()
