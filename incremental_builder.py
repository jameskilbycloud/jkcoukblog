#!/usr/bin/env python3
"""
Incremental Builder - Only regenerate changed content
Massive time savings by tracking what's already been built
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

class IncrementalBuilder:
    def __init__(self, cache_file='.build-cache.json'):
        self.cache_file = Path(cache_file)
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Load build cache from disk"""
        if self.cache_file.exists():
            try:
                return json.loads(self.cache_file.read_text())
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Failed to load cache, starting fresh: {e}")
                return self._empty_cache()
        return self._empty_cache()
    
    def _empty_cache(self):
        """Create empty cache structure"""
        return {
            'posts': {},
            'pages': {},
            'assets': {},
            'last_build_time': None,
            'last_full_build': None
        }
    
    def _save_cache(self):
        """Save build cache to disk"""
        try:
            self.cache_file.write_text(json.dumps(self.cache, indent=2))
        except IOError as e:
            print(f"⚠️  Failed to save cache: {e}")
    
    def _hash_content(self, content):
        """Create hash of content for change detection"""
        if isinstance(content, str):
            content = content.encode('utf-8')
        return hashlib.md5(content).hexdigest()
    
    def has_changed(self, url, content_hash, modified_date):
        """Check if content needs regeneration"""
        cache_type = self._get_cache_type(url)
        
        if url not in self.cache[cache_type]:
            return True
        
        cached = self.cache[cache_type][url]
        return (
            cached.get('hash') != content_hash or
            cached.get('modified') != modified_date
        )
    
    def _get_cache_type(self, url):
        """Determine cache type based on URL"""
        if '/category/' in url or '/tag/' in url:
            return 'pages'  # Archive pages
        elif url.count('/') >= 3 and not url.endswith('/'):
            return 'posts'  # Individual posts
        else:
            return 'pages'  # Home, pages, etc.
    
    def get_changed_posts(self, session, wp_url):
        """Get only posts modified since last build"""
        last_build = self.cache.get('last_build_time')
        
        if not last_build:
            print("📦 First build - processing all posts")
            return self._get_all_posts(session, wp_url)
        
        print(f"🔄 Incremental build - checking posts modified since {last_build}")
        
        # Use WordPress API's modified_after parameter
        params = {
            'modified_after': last_build,
            'per_page': 100,
            'status': 'publish'
        }
        
        changed_posts = []
        page = 1
        
        while True:
            params['page'] = page
            try:
                response = session.get(
                    f'{wp_url}/wp-json/wp/v2/posts',
                    params=params,
                    timeout=30
                )
                
                if response.status_code != 200:
                    if response.status_code == 400:
                        # No more pages
                        break
                    print(f"⚠️  API error {response.status_code} on page {page}")
                    break
                
                posts = response.json()
                if not posts:
                    break
                
                changed_posts.extend(posts)
                page += 1
                
            except Exception as e:
                print(f"⚠️  Error fetching changed posts: {e}")
                break
        
        print(f"📊 Incremental build: {len(changed_posts)} changed posts")
        
        # If no changes, we still might need to rebuild archives/pages
        if len(changed_posts) == 0:
            print("✨ No post changes detected")
        
        return changed_posts
    
    def _get_all_posts(self, session, wp_url):
        """Get all posts (for first build)"""
        all_posts = []
        page = 1
        
        while True:
            try:
                response = session.get(
                    f'{wp_url}/wp-json/wp/v2/posts',
                    params={'per_page': 100, 'page': page, 'status': 'publish'},
                    timeout=30
                )
                
                if response.status_code != 200:
                    break
                
                posts = response.json()
                if not posts:
                    break
                
                all_posts.extend(posts)
                page += 1
                
            except Exception as e:
                print(f"⚠️  Error fetching posts: {e}")
                break
        
        return all_posts
    
    def get_changed_pages(self, session, wp_url):
        """Get only pages modified since last build"""
        last_build = self.cache.get('last_build_time')
        
        if not last_build:
            return self._get_all_pages(session, wp_url)
        
        params = {
            'modified_after': last_build,
            'per_page': 100,
            'status': 'publish'
        }
        
        changed_pages = []
        page = 1
        
        while True:
            params['page'] = page
            try:
                response = session.get(
                    f'{wp_url}/wp-json/wp/v2/pages',
                    params=params,
                    timeout=30
                )
                
                if response.status_code != 200:
                    break
                
                pages = response.json()
                if not pages:
                    break
                
                changed_pages.extend(pages)
                page += 1
                
            except Exception as e:
                print(f"⚠️  Error fetching changed pages: {e}")
                break
        
        if changed_pages:
            print(f"📊 Incremental build: {len(changed_pages)} changed pages")
        
        return changed_pages
    
    def _get_all_pages(self, session, wp_url):
        """Get all pages (for first build)"""
        all_pages = []
        page = 1
        
        while True:
            try:
                response = session.get(
                    f'{wp_url}/wp-json/wp/v2/pages',
                    params={'per_page': 100, 'page': page, 'status': 'publish'},
                    timeout=30
                )
                
                if response.status_code != 200:
                    break
                
                pages = response.json()
                if not pages:
                    break
                
                all_pages.extend(pages)
                page += 1
                
            except Exception as e:
                print(f"⚠️  Error fetching pages: {e}")
                break
        
        return all_pages
    
    def mark_processed(self, url, content_hash, modified_date):
        """Mark content as processed"""
        cache_type = self._get_cache_type(url)
        
        self.cache[cache_type][url] = {
            'hash': content_hash,
            'modified': modified_date,
            'processed': datetime.now().isoformat()
        }
    
    def should_rebuild_archives(self):
        """Determine if archive pages (categories, tags, home) need rebuild"""
        # Always rebuild archives if posts changed
        # Or if it's been more than a day since last full build
        last_full = self.cache.get('last_full_build')
        
        if not last_full:
            return True
        
        try:
            last_full_date = datetime.fromisoformat(last_full)
            days_since = (datetime.now() - last_full_date).days
            return days_since >= 1
        except (ValueError, TypeError):
            return True
    
    def finalize_build(self, is_full_build=False):
        """Mark build complete and save cache"""
        self.cache['last_build_time'] = datetime.now().isoformat()
        
        if is_full_build:
            self.cache['last_full_build'] = datetime.now().isoformat()
        
        self._save_cache()
        print(f"💾 Build cache saved to {self.cache_file}")
    
    def get_stats(self):
        """Get cache statistics"""
        return {
            'posts_cached': len(self.cache['posts']),
            'pages_cached': len(self.cache['pages']),
            'assets_cached': len(self.cache['assets']),
            'last_build': self.cache.get('last_build_time'),
            'last_full_build': self.cache.get('last_full_build')
        }
    
    def clear_cache(self):
        """Clear all cache data (force full rebuild)"""
        self.cache = self._empty_cache()
        self._save_cache()
        print("🗑️  Build cache cleared - next build will be full")
    
    def remove_stale_entries(self, current_urls):
        """Remove cache entries for URLs that no longer exist"""
        removed = 0
        
        for cache_type in ['posts', 'pages']:
            cached_urls = list(self.cache[cache_type].keys())
            for url in cached_urls:
                if url not in current_urls:
                    del self.cache[cache_type][url]
                    removed += 1
        
        if removed > 0:
            print(f"🧹 Removed {removed} stale cache entries")
            self._save_cache()
        
        return removed
