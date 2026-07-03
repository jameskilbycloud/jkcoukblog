#!/usr/bin/env python3
"""
Incremental Builder - Only regenerate changed content
Massive time savings by tracking what's already been built
"""

import json
import hashlib
import re
import threading
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Matches individual post URLs: /YYYY/MM/slug/ or /YYYY/MM/slug (slug must be non-empty)
# Distinguishes posts from monthly archives (/YYYY/MM/) and year archives (/YYYY/).
# The trailing slash is optional so both canonical and non-canonical forms are handled.
_POST_URL_RE = re.compile(r'^/\d{4}/\d{2}/[^/]+')

class IncrementalBuilder:
    # Files whose contents determine the generated HTML. The cache only says
    # "this WordPress content was already rendered" — if the code that renders
    # it changes, every cached page is potentially stale, so any change here
    # invalidates the whole cache and forces a full rebuild.
    FINGERPRINT_FILES = ('config.py', 'wp_to_static_generator.py')

    # Overlap subtracted from the stored watermark when querying WordPress,
    # absorbing clock skew between the runner and the WP host. Re-fetching a
    # few recently-modified posts is cheap — has_changed()'s content-hash
    # check skips regeneration when nothing actually changed.
    WATERMARK_OVERLAP = timedelta(minutes=5)

    def __init__(self, cache_file='.build-cache.json'):
        self.cache_file = Path(cache_file)
        # mark_processed() is called from ThreadPoolExecutor workers in
        # wp_to_static_generator.py — guard all cache mutation/serialisation.
        self._lock = threading.Lock()
        # Watermark for the NEXT build's modified_after filter. Captured at
        # construction (before any posts are fetched), NOT at finalize time —
        # a post edited in WordPress while the 10–40 min build is running is
        # older than an end-of-build stamp, so the next incremental run would
        # have skipped it forever. UTC with explicit offset so runner/WP
        # timezone or DST divergence can't shift the window.
        self._build_started_at = datetime.now(timezone.utc)
        self.cache = self._load_cache()
        self._check_environment_fingerprint()

    def _environment_fingerprint(self):
        """Hash the generator code + config that shape the rendered output."""
        h = hashlib.blake2b(digest_size=16)
        script_dir = Path(__file__).resolve().parent
        for name in self.FINGERPRINT_FILES:
            try:
                h.update((script_dir / name).read_bytes())
            except OSError:
                h.update(f'missing:{name}'.encode())
        return h.hexdigest()

    def _check_environment_fingerprint(self):
        """Invalidate the cache when config.py or the generator changed."""
        fingerprint = self._environment_fingerprint()
        cached = self.cache.get('environment_fingerprint')
        if cached != fingerprint:
            had_entries = bool(self.cache['posts'] or self.cache['pages'])
            if cached is not None or had_entries:
                print("♻️  config.py / generator changed since last build — "
                      "clearing build cache, this build will be full")
                self.cache = self._empty_cache()
        self.cache['environment_fingerprint'] = fingerprint


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
            with self._lock:
                serialized = json.dumps(self.cache, indent=2)
            self.cache_file.write_text(serialized)
        except IOError as e:
            print(f"⚠️  Failed to save cache: {e}")
    
    def _hash_content(self, content):
        """Create hash of content for change detection.

        Uses BLAKE2b (16-byte digest) instead of MD5 — faster in CPython and
        collision-resistant, which matters if the cache file is ever inspected
        or compared across machines.
        """
        if isinstance(content, str):
            content = content.encode('utf-8')
        return hashlib.blake2b(content, digest_size=16).hexdigest()
    
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
        """Determine cache type based on URL.

        WordPress post URLs follow /YYYY/MM/slug/ — they always end with '/'
        so the old check ``not url.endswith('/')`` never matched them.  The
        regex correctly identifies posts while leaving monthly archives
        (/YYYY/MM/), year archives (/YYYY/), and other pages in 'pages'.
        """
        if '/category/' in url or '/tag/' in url:
            return 'pages'  # Archive pages
        if _POST_URL_RE.match(url):
            return 'posts'  # Individual posts: /YYYY/MM/slug/
        return 'pages'  # Home, WP pages, archives, etc.
    
    def _modified_after_param(self, last_build):
        """Watermark minus WATERMARK_OVERLAP, as ISO8601 for modified_after.

        Legacy caches hold naive local-time stamps (pre-UTC fix) — treat
        those as runner-local so the one build that straddles the change
        behaves exactly as before.
        """
        try:
            stamp = datetime.fromisoformat(last_build)
        except (ValueError, TypeError):
            return last_build
        if stamp.tzinfo is None:
            stamp = stamp.astimezone()
        return (stamp - self.WATERMARK_OVERLAP).isoformat()

    def get_changed_posts(self, session, wp_url):
        """Get only posts modified since last build"""
        last_build = self.cache.get('last_build_time')
        cached_count = len(self.cache.get('posts', {})) + len(self.cache.get('pages', {}))

        if not last_build or cached_count == 0:
            print("📦 First build - processing all posts")
            return self._get_all_posts(session, wp_url)
        
        print(f"🔄 Incremental build - checking posts modified since {last_build}")

        # Use WordPress API's modified_after parameter
        params = {
            'modified_after': self._modified_after_param(last_build),
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
        cached_count = len(self.cache.get('posts', {})) + len(self.cache.get('pages', {}))

        if not last_build or cached_count == 0:
            return self._get_all_pages(session, wp_url)

        params = {
            'modified_after': self._modified_after_param(last_build),
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
        """Mark content as processed (thread-safe — called from worker threads)"""
        cache_type = self._get_cache_type(url)

        with self._lock:
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
            if last_full_date.tzinfo is None:
                # Legacy naive local-time stamp — anchor it before comparing
                # against the aware UTC clock (naive - aware raises TypeError,
                # which used to force an archive rebuild every run).
                last_full_date = last_full_date.astimezone()
            days_since = (datetime.now(timezone.utc) - last_full_date).days
            return days_since >= 1
        except (ValueError, TypeError):
            return True
    
    def finalize_build(self, is_full_build=False):
        """Mark build complete and save cache.

        Stamps the build START time (see __init__), not now() — anything
        modified in WordPress after fetching began, including during the
        build itself, stays newer than the watermark and is picked up by
        the next incremental run.
        """
        self.cache['last_build_time'] = self._build_started_at.isoformat()

        if is_full_build:
            self.cache['last_full_build'] = self._build_started_at.isoformat()

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

        with self._lock:
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
