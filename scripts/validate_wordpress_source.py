#!/usr/bin/env python3
"""
WordPress Source Health Validator

Validates WordPress source health BEFORE static site generation.
Checks API health, content integrity, and SEO readiness.

Usage:
    export WP_AUTH_TOKEN="base64_encoded_credentials"
    python3 scripts/validate_wordpress_source.py
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Optional, Tuple
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


class WordPressSourceValidator:
    """Validates WordPress source health before static generation."""

    def __init__(self, wp_url: str, auth_token: str, skip_seo: bool = False, verbose: bool = False):
        """
        Initialize validator.

        Args:
            wp_url: WordPress base URL
            auth_token: Basic auth token (base64 encoded)
            skip_seo: Skip SEO readiness checks
            verbose: Enable verbose output
        """
        self.wp_url = wp_url.rstrip('/')
        self.auth_token = auth_token
        self.skip_seo = skip_seo
        self.verbose = verbose

        # Set up HTTP session with authentication
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Basic {auth_token}',
            'User-Agent': 'WordPressSourceValidator/1.0'
        })
        self.session.timeout = 30  # 30 second timeout per request

        # Tracking structures (following ContentValidator pattern)
        self.errors: List[Dict] = []          # Critical issues (block deployment)
        self.warnings: List[Dict] = []        # Non-critical issues
        self.stats: Dict = {}                 # Statistics for reporting

        # Cache to avoid duplicate API calls
        self.cache: Dict = {
            'categories': {},      # {id: category_data}
            'tags': {},           # {id: tag_data}
            'media_ids': set(),   # {id1, id2, id3...}
            'urls_checked': {}    # {url: is_accessible}
        }

        self.start_time = time.time()

    def _log(self, message: str, level: str = 'info'):
        """Log message to console."""
        if level == 'verbose' and not self.verbose:
            return
        print(message)

    def _make_api_request(self, endpoint: str, params: Optional[Dict] = None, method: str = 'GET') -> Tuple[Optional[requests.Response], Optional[str]]:
        """
        Make an API request with error handling.

        Args:
            endpoint: API endpoint path (e.g., '/wp-json/wp/v2/posts')
            params: Query parameters
            method: HTTP method

        Returns:
            Tuple of (response, error_message). If successful, error_message is None.
        """
        url = f"{self.wp_url}{endpoint}"

        try:
            if method == 'GET':
                response = self.session.get(url, params=params)
            elif method == 'HEAD':
                response = self.session.head(url, params=params)
            else:
                return None, f"Unsupported HTTP method: {method}"

            return response, None

        except requests.exceptions.Timeout:
            return None, f"Request timeout after 30 seconds"
        except requests.exceptions.ConnectionError as e:
            return None, f"Connection error: {str(e)}"
        except requests.exceptions.RequestException as e:
            return None, f"Request failed: {str(e)}"

    def validate_api_health(self) -> bool:
        """
        Test WordPress API accessibility and authentication.

        Returns:
            True if all health checks pass
        """
        self._log("\n🌐 WordPress API Health Check...")

        # Check base URL (WordPress site accessible)
        response, error = self._make_api_request('/')
        if error or not response or response.status_code != 200:
            self.errors.append({
                'type': 'site_not_accessible',
                'message': f'WordPress site not accessible at {self.wp_url}',
                'details': error or f'Status code: {response.status_code if response else "N/A"}'
            })
            self._log("   ❌ WordPress site not accessible")
            return False
        self._log("   ✅ WordPress site accessible")

        # Check REST API discovery endpoint
        response, error = self._make_api_request('/wp-json/')
        if error or not response or response.status_code != 200:
            self.errors.append({
                'type': 'api_not_available',
                'message': 'REST API endpoint not available',
                'details': error or f'Status code: {response.status_code if response else "N/A"}'
            })
            self._log("   ❌ REST API endpoint not available")
            return False
        self._log("   ✅ REST API endpoint available")

        # Test authentication with minimal posts request
        response, error = self._make_api_request('/wp-json/wp/v2/posts', {'per_page': 1})
        if error:
            self.errors.append({
                'type': 'api_request_failed',
                'endpoint': 'posts',
                'message': 'Failed to connect to Posts endpoint',
                'details': error
            })
            self._log("   ❌ Posts endpoint connection failed")
            return False

        if response.status_code == 401:
            self.errors.append({
                'type': 'auth_failed',
                'message': 'Authentication failed - check WP_AUTH_TOKEN',
                'details': 'Received 401 Unauthorized'
            })
            self._log("   ❌ Authentication failed (401)")
            return False
        elif response.status_code == 403:
            self.errors.append({
                'type': 'auth_forbidden',
                'message': 'Access forbidden - check user permissions',
                'details': 'Received 403 Forbidden'
            })
            self._log("   ❌ Access forbidden (403)")
            return False
        elif response.status_code != 200:
            self.errors.append({
                'type': 'api_error',
                'endpoint': 'posts',
                'message': f'Posts endpoint returned status {response.status_code}',
                'details': response.text[:200] if response.text else ''
            })
            self._log(f"   ❌ Posts endpoint error ({response.status_code})")
            return False

        self._log("   ✅ Authentication successful")

        # Check all critical endpoints
        endpoints = [
            ('/wp-json/wp/v2/posts', 'Posts'),
            ('/wp-json/wp/v2/pages', 'Pages'),
            ('/wp-json/wp/v2/media', 'Media'),
            ('/wp-json/wp/v2/categories', 'Categories'),
            ('/wp-json/wp/v2/tags', 'Tags')
        ]

        for endpoint, name in endpoints:
            if not self._check_endpoint_health(endpoint, name):
                return False

        return True

    def _check_endpoint_health(self, endpoint: str, name: str) -> bool:
        """
        Check a single endpoint for 200 OK response.

        Args:
            endpoint: Full URL path (e.g., '/wp-json/wp/v2/posts')
            name: Friendly name for logging (e.g., 'Posts')

        Returns:
            True if endpoint is healthy
        """
        response, error = self._make_api_request(endpoint, {'per_page': 1})

        if error:
            self.errors.append({
                'type': 'endpoint_unreachable',
                'endpoint': name,
                'message': f'{name} endpoint unreachable',
                'details': error
            })
            self._log(f"   ❌ {name} endpoint unreachable")
            return False

        if response.status_code != 200:
            self.errors.append({
                'type': 'endpoint_error',
                'endpoint': name,
                'message': f'{name} endpoint returned status {response.status_code}',
                'details': response.text[:200] if response.text else ''
            })
            self._log(f"   ❌ {name} endpoint error ({response.status_code})")
            return False

        # Try to get count from response
        try:
            total = int(response.headers.get('X-WP-Total', 0))
            self._log(f"   ✅ {name} endpoint healthy ({total} items)")
        except (ValueError, TypeError):
            self._log(f"   ✅ {name} endpoint healthy")

        return True

    def _prefetch_reference_data(self):
        """Pre-fetch categories, tags, and media IDs to avoid N+1 queries."""
        self._log("\n📦 Pre-fetching reference data...")

        # Fetch all categories
        categories = self._fetch_all_paginated('/wp-json/wp/v2/categories')
        for cat in categories:
            self.cache['categories'][cat['id']] = cat
        self._log(f"   📁 Loaded {len(categories)} categories")

        # Fetch all tags
        tags = self._fetch_all_paginated('/wp-json/wp/v2/tags')
        for tag in tags:
            self.cache['tags'][tag['id']] = tag
        self._log(f"   🏷️  Loaded {len(tags)} tags")

        # Fetch all media IDs (just IDs, not full data)
        media_items = self._fetch_all_paginated('/wp-json/wp/v2/media', fields='id')
        for item in media_items:
            self.cache['media_ids'].add(item['id'])
        self._log(f"   🖼️  Indexed {len(media_items)} media items")

    def _fetch_all_paginated(self, endpoint: str, fields: Optional[str] = None) -> List[Dict]:
        """
        Fetch all items from a paginated endpoint.

        Args:
            endpoint: API endpoint
            fields: Optional comma-separated list of fields to fetch

        Returns:
            List of all items across all pages
        """
        all_items = []
        page = 1
        per_page = 100  # WordPress default max

        while True:
            params = {'per_page': per_page, 'page': page}
            if fields:
                params['_fields'] = fields

            response, error = self._make_api_request(endpoint, params)

            if error or not response:
                self._log(f"   ⚠️  Failed to fetch page {page}: {error}", 'verbose')
                break

            if response.status_code == 400:
                # End of pagination (WordPress returns 400 for page beyond last)
                break

            if response.status_code != 200:
                self._log(f"   ⚠️  Page {page} returned status {response.status_code}", 'verbose')
                break

            try:
                items = response.json()
                if not items:
                    break

                all_items.extend(items)

                # Check if there are more pages
                total_pages = int(response.headers.get('X-WP-TotalPages', 1))
                if page >= total_pages:
                    break

                page += 1

            except (ValueError, KeyError) as e:
                self._log(f"   ⚠️  Failed to parse response: {e}", 'verbose')
                break

        return all_items

    def validate_posts(self):
        """Validate all published posts for integrity."""
        self._log("\n📄 Validating posts...")

        posts = self._fetch_all_paginated(
            '/wp-json/wp/v2/posts',
            fields='id,title,link,featured_media,categories,tags,excerpt,content'
        )

        if not posts:
            self.warnings.append({
                'type': 'no_posts',
                'message': 'No posts found in WordPress'
            })
            self._log("   ⚠️  No posts found")
            return

        self.stats['total_posts'] = len(posts)
        posts_without_featured_image = 0
        posts_without_categories = 0
        posts_without_tags = 0
        posts_with_short_title = 0
        posts_with_long_title = 0
        posts_with_short_excerpt = 0
        posts_with_long_excerpt = 0
        posts_with_broken_featured_image = 0
        posts_with_broken_categories = 0
        posts_with_broken_tags = 0

        for i, post in enumerate(posts, 1):
            self._log(f"   🔍 Validating post {i}/{len(posts)}: {post.get('title', {}).get('rendered', 'Untitled')[:50]}...", 'verbose')

            post_id = post['id']
            post_title = post.get('title', {}).get('rendered', 'Untitled')
            post_link = post.get('link', '')

            # Check featured image
            featured_media = post.get('featured_media', 0)
            if featured_media == 0:
                posts_without_featured_image += 1
                self.warnings.append({
                    'type': 'missing_featured_image',
                    'content_type': 'post',
                    'content_id': post_id,
                    'content_title': post_title,
                    'content_url': post_link,
                    'message': 'Missing featured image'
                })
            elif featured_media not in self.cache['media_ids']:
                posts_with_broken_featured_image += 1
                self.errors.append({
                    'type': 'broken_featured_image',
                    'content_type': 'post',
                    'content_id': post_id,
                    'content_title': post_title,
                    'content_url': post_link,
                    'message': f'Featured image ID {featured_media} not found (404)',
                    'media_id': featured_media
                })

            # Check categories
            categories = post.get('categories', [])
            if not categories:
                posts_without_categories += 1
                self.warnings.append({
                    'type': 'missing_categories',
                    'content_type': 'post',
                    'content_id': post_id,
                    'content_title': post_title,
                    'content_url': post_link,
                    'message': 'Post has no categories'
                })
            else:
                for cat_id in categories:
                    if cat_id not in self.cache['categories']:
                        posts_with_broken_categories += 1
                        self.errors.append({
                            'type': 'broken_category',
                            'content_type': 'post',
                            'content_id': post_id,
                            'content_title': post_title,
                            'content_url': post_link,
                            'message': f'Category ID {cat_id} not found',
                            'category_id': cat_id
                        })

            # Check tags
            tags = post.get('tags', [])
            if not tags:
                posts_without_tags += 1
                self.warnings.append({
                    'type': 'missing_tags',
                    'content_type': 'post',
                    'content_id': post_id,
                    'content_title': post_title,
                    'content_url': post_link,
                    'message': 'Post has no tags'
                })
            elif len(tags) < 2 or len(tags) > 10:
                self.warnings.append({
                    'type': 'tags_out_of_range',
                    'content_type': 'post',
                    'content_id': post_id,
                    'content_title': post_title,
                    'content_url': post_link,
                    'message': f'Post has {len(tags)} tags (recommended 2-10)',
                    'tag_count': len(tags)
                })
            else:
                for tag_id in tags:
                    if tag_id not in self.cache['tags']:
                        posts_with_broken_tags += 1
                        self.errors.append({
                            'type': 'broken_tag',
                            'content_type': 'post',
                            'content_id': post_id,
                            'content_title': post_title,
                            'content_url': post_link,
                            'message': f'Tag ID {tag_id} not found',
                            'tag_id': tag_id
                        })

            # SEO checks (if not skipped)
            if not self.skip_seo:
                # Title length
                title_len = len(post_title)
                if title_len < 30:
                    posts_with_short_title += 1
                    self.warnings.append({
                        'type': 'seo_title_short',
                        'content_type': 'post',
                        'content_id': post_id,
                        'content_title': post_title,
                        'content_url': post_link,
                        'message': f'Title too short ({title_len} chars, recommended 30-60)',
                        'title_length': title_len
                    })
                elif title_len > 60:
                    posts_with_long_title += 1
                    self.warnings.append({
                        'type': 'seo_title_long',
                        'content_type': 'post',
                        'content_id': post_id,
                        'content_title': post_title,
                        'content_url': post_link,
                        'message': f'Title too long ({title_len} chars, recommended 30-60)',
                        'title_length': title_len
                    })

                # Excerpt length
                excerpt = post.get('excerpt', {}).get('rendered', '')
                excerpt_text = BeautifulSoup(excerpt, 'html.parser').get_text().strip()
                excerpt_len = len(excerpt_text)
                if excerpt_len == 0:
                    self.warnings.append({
                        'type': 'seo_excerpt_missing',
                        'content_type': 'post',
                        'content_id': post_id,
                        'content_title': post_title,
                        'content_url': post_link,
                        'message': 'Missing meta description/excerpt'
                    })
                elif excerpt_len < 120:
                    posts_with_short_excerpt += 1
                    self.warnings.append({
                        'type': 'seo_excerpt_short',
                        'content_type': 'post',
                        'content_id': post_id,
                        'content_title': post_title,
                        'content_url': post_link,
                        'message': f'Excerpt too short ({excerpt_len} chars, recommended 120-160)',
                        'excerpt_length': excerpt_len
                    })
                elif excerpt_len > 160:
                    posts_with_long_excerpt += 1
                    self.warnings.append({
                        'type': 'seo_excerpt_long',
                        'content_type': 'post',
                        'content_id': post_id,
                        'content_title': post_title,
                        'content_url': post_link,
                        'message': f'Excerpt too long ({excerpt_len} chars, recommended 120-160)',
                        'excerpt_length': excerpt_len
                    })

        # Update stats
        self.stats['posts_validated'] = len(posts)
        self.stats['posts_without_featured_image'] = posts_without_featured_image
        self.stats['posts_without_categories'] = posts_without_categories
        self.stats['posts_without_tags'] = posts_without_tags
        self.stats['posts_with_broken_featured_image'] = posts_with_broken_featured_image
        self.stats['posts_with_broken_categories'] = posts_with_broken_categories
        self.stats['posts_with_broken_tags'] = posts_with_broken_tags

        if not self.skip_seo:
            self.stats['posts_with_short_title'] = posts_with_short_title
            self.stats['posts_with_long_title'] = posts_with_long_title
            self.stats['posts_with_short_excerpt'] = posts_with_short_excerpt
            self.stats['posts_with_long_excerpt'] = posts_with_long_excerpt

        self._log(f"   ✅ Validated {len(posts)} posts")
        if posts_without_featured_image > 0:
            self._log(f"   ⚠️  {posts_without_featured_image} posts missing featured images")
        if posts_with_broken_featured_image > 0:
            self._log(f"   ❌ {posts_with_broken_featured_image} posts with broken featured images")

    def validate_pages(self):
        """Validate all published pages for integrity."""
        self._log("\n📑 Validating pages...")

        pages = self._fetch_all_paginated(
            '/wp-json/wp/v2/pages',
            fields='id,title,link,featured_media,content'
        )

        if not pages:
            self._log("   ℹ️  No pages found (optional)")
            return

        self.stats['total_pages'] = len(pages)
        pages_without_featured_image = 0

        for page in pages:
            page_id = page['id']
            page_title = page.get('title', {}).get('rendered', 'Untitled')
            page_link = page.get('link', '')

            # Check featured image (optional for pages, just warn)
            featured_media = page.get('featured_media', 0)
            if featured_media == 0:
                pages_without_featured_image += 1
                # Don't add warning - featured images are optional for pages
            elif featured_media not in self.cache['media_ids']:
                self.errors.append({
                    'type': 'broken_featured_image',
                    'content_type': 'page',
                    'content_id': page_id,
                    'content_title': page_title,
                    'content_url': page_link,
                    'message': f'Featured image ID {featured_media} not found (404)',
                    'media_id': featured_media
                })

        self.stats['pages_validated'] = len(pages)
        self.stats['pages_without_featured_image'] = pages_without_featured_image

        self._log(f"   ✅ Validated {len(pages)} pages")

    def validate_media_library(self):
        """Validate media library items are accessible."""
        self._log("\n🖼️  Validating media library...")

        media_count = len(self.cache['media_ids'])
        if media_count == 0:
            self.warnings.append({
                'type': 'no_media',
                'message': 'No media items found in WordPress'
            })
            self._log("   ⚠️  No media items found")
            return

        self.stats['total_media'] = media_count
        self._log(f"   ✅ {media_count} media items indexed")

    def generate_report(self) -> Dict:
        """
        Generate comprehensive JSON validation report.

        Returns:
            Report dictionary
        """
        duration = time.time() - self.start_time

        report = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'wordpress_url': self.wp_url,
            'summary': {
                'status': 'FAIL' if self.errors else 'PASS',
                'total_posts': self.stats.get('total_posts', 0),
                'total_pages': self.stats.get('total_pages', 0),
                'total_media': self.stats.get('total_media', 0),
                'errors': len(self.errors),
                'warnings': len(self.warnings),
                'duration_seconds': round(duration, 2)
            },
            'errors': self.errors,
            'warnings': self.warnings,
            'stats': self.stats
        }

        # Save to file
        report_file = Path('wordpress-source-validation.json')
        report_file.write_text(json.dumps(report, indent=2))

        return report

    def print_summary(self):
        """Print human-readable validation summary to console."""
        print("\n" + "=" * 80)
        print("WORDPRESS SOURCE VALIDATION SUMMARY")
        print("=" * 80)
        print()
        print(f"WordPress URL:     {self.wp_url}")
        print(f"Posts validated:   {self.stats.get('posts_validated', 0)}")
        print(f"Pages validated:   {self.stats.get('pages_validated', 0)}")
        print(f"Media checked:     {self.stats.get('total_media', 0)}")
        print()

        status = "✅ PASS" if not self.errors else "❌ FAIL"
        if self.warnings and not self.errors:
            status = "⚠️  PASS WITH WARNINGS"

        print(f"Status: {status}")
        print(f"Errors: {len(self.errors)}")
        print(f"Warnings: {len(self.warnings)}")
        print()

        # Print first 10 errors
        if self.errors:
            print("❌ CRITICAL ERRORS:")
            for i, error in enumerate(self.errors[:10], 1):
                content_type = error.get('content_type', '')
                content_title = error.get('content_title', '')
                content_id = error.get('content_id', '')
                message = error.get('message', '')

                if content_type and content_title:
                    print(f"   {i}. {content_type.capitalize()} \"{content_title}\" (ID: {content_id})")
                    print(f"      {message}")
                else:
                    print(f"   {i}. {message}")

            if len(self.errors) > 10:
                print(f"   ... and {len(self.errors) - 10} more errors")
            print()

        # Print first 10 warnings
        if self.warnings:
            print("⚠️  WARNINGS:")
            for i, warning in enumerate(self.warnings[:10], 1):
                content_type = warning.get('content_type', '')
                content_title = warning.get('content_title', '')
                content_id = warning.get('content_id', '')
                message = warning.get('message', '')

                if content_type and content_title:
                    print(f"   {i}. {content_type.capitalize()} \"{content_title}\" (ID: {content_id})")
                    print(f"      {message}")
                else:
                    print(f"   {i}. {message}")

            if len(self.warnings) > 10:
                print(f"   ... and {len(self.warnings) - 10} more warnings")
            print()

        # Print key statistics
        if self.stats:
            print("📊 Statistics:")
            for key, value in sorted(self.stats.items()):
                if key not in ['total_posts', 'total_pages', 'total_media']:
                    print(f"   {key}: {value}")
            print()

        print("=" * 80)
        print()
        print("📄 Full report saved to: wordpress-source-validation.json")

        duration = time.time() - self.start_time
        print()
        status_emoji = "✅" if not self.errors else "❌"
        print(f"{status_emoji} Validation complete! ({duration:.1f} seconds)")

    def validate_all(self) -> bool:
        """
        Run all validation checks in sequence.

        Returns:
            True if no critical errors found
        """
        print("🔍 Starting WordPress Source Validation...")
        print("=" * 80)

        # Step 1: API Health (if this fails, stop immediately)
        if not self.validate_api_health():
            print("\n❌ API health check failed. Cannot proceed with content validation.")
            self.generate_report()
            self.print_summary()
            return False

        # Step 2: Pre-fetch reference data
        self._prefetch_reference_data()

        # Step 3: Validate content
        self.validate_posts()
        self.validate_pages()
        self.validate_media_library()

        # Step 4: Generate report and summary
        self.generate_report()
        self.print_summary()

        return len(self.errors) == 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Validate WordPress source health before static site generation'
    )
    parser.add_argument(
        '--wp-url',
        default=None,
        help='WordPress URL (default: from config.py)'
    )
    parser.add_argument(
        '--skip-seo',
        action='store_true',
        help='Skip SEO readiness checks (only validate integrity)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Get configuration
    try:
        # Add scripts directory to path so we can import config
        scripts_dir = Path(__file__).parent
        sys.path.insert(0, str(scripts_dir))
        from config import Config
        config = Config()
        wp_url = args.wp_url or config.WP_URL
    except ImportError:
        print("❌ Error: Could not import config.py")
        print("   Make sure scripts/config.py exists")
        sys.exit(1)

    # Get auth token from environment
    auth_token = os.environ.get('WP_AUTH_TOKEN')
    if not auth_token:
        print("❌ Error: WP_AUTH_TOKEN environment variable not set")
        print()
        print("Set the environment variable with your WordPress credentials:")
        print("  export WP_AUTH_TOKEN=\"base64_encoded_credentials\"")
        sys.exit(1)

    # Run validation
    validator = WordPressSourceValidator(
        wp_url=wp_url,
        auth_token=auth_token,
        skip_seo=args.skip_seo,
        verbose=args.verbose
    )

    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
