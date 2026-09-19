#!/usr/bin/env python3
"""
WordPress to Static Site Generator
A complete solution for converting your WordPress CMS to a static site
"""

import os
import sys
import time
import functools
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
# Post-build site artifact generation (sitemap, RSS, robots.txt, search
# index, script/widget injection — everything that only reads finished HTML
# back off disk) lives in site_artifacts_builder.py; see that module's
# docstring. image_file_present/image_url_to_output_path are re-exported
# here because tests/test_wp_to_static_generator.py imports them from this
# module's path.
from site_artifacts_builder import (
    SiteArtifactsBuilder,
    image_file_present,
    image_url_to_output_path,
)
# Per-page URL rewriting + schema.org JSON-LD enrichment (the next cleanest
# cut after the post-build artifacts group) lives in
# content_schema_rewriter.py; see that module's docstring.
from content_schema_rewriter import ContentSchemaRewriter
# Header/footer brand chrome (logo lockup, search button/box, relocated
# social icons, footer credit line) — fully stateless, see that module's
# docstring.
from header_footer_chrome import HeaderFooterChrome
# WordPress artifact cleanup (admin bar, wp-emoji, generator meta, RSD/
# wlwmanifest links, Rank Math comments, Kadence credit) and embed-block ->
# iframe conversion — see that module's docstring. Only needs wp_url.
from wordpress_cleanup import WordPressCleanup
# Image loading/priority strategy + responsive sizes tuning — fully
# stateless, see that module's docstring.
from image_loading_optimizer import ImageLoadingOptimizer
# Per-page SEO meta fixes (taxonomy descriptions, pagination dedup, thin-page
# noindex, homepage H1 fallback) — fully stateless, see that module's
# docstring.
from page_seo_meta import PageSeoMeta
# Footer/card/content DOM fixups (markdown+API footer links, byline dates,
# category-link trimming, table headers) — fully stateless, see that
# module's docstring.
from content_card_fixups import ContentCardFixups

# Default timeout (seconds) applied to every session HTTP call. Individual
# calls can still pass an explicit `timeout=` to override this.
DEFAULT_HTTP_TIMEOUT = 30


class WordPressStaticGenerator:
    def __init__(self, wp_url, auth_token, output_dir, target_domain, use_incremental=True):
        self.wp_url = wp_url.rstrip('/')
        self.auth_token = auth_token
        self.output_dir = Path(output_dir)
        self.target_domain = target_domain.rstrip('/')
        # Shared factory: Basic auth + retry/backoff on transient 429/5xx +
        # session-wide default timeout (explicit `timeout=` kwargs at call
        # sites still override it). accept=None because this session fetches
        # rendered HTML pages and binary assets, not just JSON.
        from wp_session import build_session
        self.session = build_session(
            auth_token,
            user_agent='StaticSiteGenerator/1.0',
            accept=None,
            default_timeout=DEFAULT_HTTP_TIMEOUT,
        )
        self.downloaded_assets = set()
        self.processed_urls = set()
        self.extracted_css_files = {}  # Map CSS hash to filename
        self.css_output_dir = self.output_dir / 'assets' / 'css'
        self.use_incremental = use_incremental
        self.incremental_builder = IncrementalBuilder() if use_incremental else None
        # Map of relative_url -> {'cats': set[int], 'tags': set[int],
        # 'date': str, 'title': str}. Populated once per build by
        # build_post_index() and consumed by add_related_posts(); writes
        # finish before the parallel processing pool starts, so reads from
        # worker threads are safe.
        self.post_index = {}
        # Post-build artifact generation (sitemap, RSS, search index, script/
        # widget injection) — see site_artifacts_builder.py. Only needs
        # output_dir/target_domain, so it's built once here and reused.
        self.artifacts = SiteArtifactsBuilder(self.output_dir, self.target_domain)
        # Per-page URL rewriting + schema.org JSON-LD enrichment — see
        # content_schema_rewriter.py. Only needs wp_url/target_domain.
        self.schema = ContentSchemaRewriter(self.wp_url, self.target_domain)
        # Header/footer brand chrome — see header_footer_chrome.py. Fully
        # stateless; takes no constructor arguments.
        self.chrome = HeaderFooterChrome()
        # WordPress artifact cleanup + embed conversion — see
        # wordpress_cleanup.py. Only needs wp_url.
        self.wp_cleanup = WordPressCleanup(self.wp_url)
        # Image loading/priority strategy — see image_loading_optimizer.py.
        # Fully stateless; takes no constructor arguments.
        self.images = ImageLoadingOptimizer()
        # Per-page SEO meta fixes — see page_seo_meta.py. Fully stateless;
        # takes no constructor arguments.
        self.seo_meta = PageSeoMeta()
        # Footer/card/content DOM fixups — see content_card_fixups.py.
        # Fully stateless; takes no constructor arguments.
        self.card_fixups = ContentCardFixups()

    def _paginate_taxonomy(self, endpoint: str, kind: str) -> list:
        """Fetch every item from a WP taxonomy endpoint (tags, categories, ...).

        WP REST caps per_page at 100 and does NOT auto-paginate. Historically
        this code used per_page=100 with no page loop, silently dropping any
        taxonomy term past position 100. On jameskilby.co.uk WordPress there
        are more than 100 tags; the alphabetical tail (self-hosted, ubuntu,
        vmware, vsphere, zoom, …) was invisible to the generator, producing
        GSC 404s for /tag/vmware/ etc. that posts still linked to.

        Returns an empty list on any error.
        """
        items = []
        page = 1
        while True:
            resp = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/{endpoint}',
                params={'per_page': 100, 'page': page},
            )
            if resp.status_code == 400 and page > 1:
                # WP returns 400 with rest_post_invalid_page_number past the end
                break
            if resp.status_code != 200:
                print(f"   ⚠️  {kind} API returned status {resp.status_code} on page {page}")
                if page == 1:
                    return []
                break
            try:
                batch = resp.json()
            except (json.JSONDecodeError, ValueError):
                print(f"   ⚠️  Invalid JSON on {kind} page {page}, stopping")
                break
            if not isinstance(batch, list) or not batch:
                break
            items.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        return items

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
                # Add essential pages and archives. Per-category/per-tag URLs
                # are added below from the taxonomy listing; the bare
                # `/category/` and `/tag/` paths used to be in here too but
                # WordPress 404s them (they're not real pages, just taxonomy
                # roots), producing two failures per build that obscured
                # real errors.
                urls.add('/')
                
                # Get all categories and tags (archives need full list)
                for category in self._paginate_taxonomy('categories', 'Categories'):
                    if category.get('count', 0) > 0:
                        relative_url = category['link'].replace(self.wp_url, '')
                        urls.add(relative_url)
                        print(f"   📁 Category: {category['name']}")

                for tag in self._paginate_taxonomy('tags', 'Tags'):
                    if tag.get('count', 0) > 0:
                        relative_url = tag['link'].replace(self.wp_url, '')
                        urls.add(relative_url)
                        print(f"   🏷️  Tag: {tag['name']}")

                # Discover homepage pagination pages (/page/2/, /page/3/, etc.)
                pagination_page = 2
                while True:
                    pagination_url = f'/page/{pagination_page}/'
                    check_url = f'{self.wp_url}{pagination_url}'
                    try:
                        resp = self.session.head(check_url, timeout=15, allow_redirects=False)
                        if resp.status_code == 200:
                            urls.add(pagination_url)
                            print(f"   📄 Homepage page: {pagination_url}")
                            pagination_page += 1
                        else:
                            break
                    except Exception as e:
                        print(f"   ⚠️  Pagination discovery stopped at page {pagination_page}: {e}")
                        break

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
                    print("   ❌ Authentication failed - check WP_AUTH_TOKEN")
                else:
                    print(f"   ❌ Error: {posts_response.text[:200]}")
                break
                
            try:
                posts = posts_response.json()
            except (json.JSONDecodeError, ValueError):
                print(f"   ⚠️  Invalid JSON on post page {page}, stopping")
                break
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
                
            try:
                pages = pages_response.json()
            except (json.JSONDecodeError, ValueError):
                break
            if not pages:
                break

            for page_item in pages:
                relative_url = page_item['link'].replace(self.wp_url, '')
                urls.add(relative_url)
                print(f"   📑 Page: {page_item['title']['rendered']}")
            
            page += 1
        
        # Get categories
        for category in self._paginate_taxonomy('categories', 'Categories'):
            if category.get('count', 0) > 0:  # Only categories with posts
                relative_url = category['link'].replace(self.wp_url, '')
                urls.add(relative_url)
                print(f"   📁 Category: {category['name']}")

        # Get tags with posts (paginated — see _paginate_taxonomy for the
        # per_page=100 bug this fixes).
        for tag in self._paginate_taxonomy('tags', 'Tags'):
            if tag.get('count', 0) > 0:
                relative_url = tag['link'].replace(self.wp_url, '')
                urls.add(relative_url)
                print(f"   🏷️  Tag: {tag['name']}")
        
        # Add essential pages. `/category/` and `/tag/` used to be in here
        # too but WordPress 404s those bare taxonomy roots (only the
        # individual `/category/<slug>/` and `/tag/<slug>/` URLs are real),
        # producing two ❌ Failed entries on every build that masked real
        # download errors.
        urls.add('/')

        # Discover homepage pagination pages (/page/2/, /page/3/, etc.)
        print("   🔍 Discovering homepage pagination pages...")
        pagination_page = 2
        while True:
            pagination_url = f'/page/{pagination_page}/'
            check_url = f'{self.wp_url}{pagination_url}'
            try:
                resp = self.session.head(check_url, timeout=15, allow_redirects=False)
                if resp.status_code == 200:
                    urls.add(pagination_url)
                    print(f"   📄 Homepage page: {pagination_url}")
                    pagination_page += 1
                else:
                    break
            except Exception as e:
                print(f"   ⚠️  Pagination discovery stopped at page {pagination_page}: {e}")
                break
        if pagination_page > 2:
            print(f"   ✅ Found {pagination_page - 2} homepage pagination pages")

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
                
            try:
                media_items = media_response.json()
            except (json.JSONDecodeError, ValueError):
                break
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

                    # Record content hash so the incremental cache reflects what
                    # was actually generated.  Use Last-Modified from the server
                    # as the modified_date; fall back to an empty string so the
                    # hash alone still guards against content changes.
                    if self.incremental_builder:
                        content_hash = self.incremental_builder._hash_content(processed_content)
                        modified_date = response.headers.get('Last-Modified', '')
                        self.incremental_builder.mark_processed(url_path, content_hash, modified_date)
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
        self.schema.replace_urls_in_soup(soup)
        
        # Remove WordPress-specific elements
        self.wp_cleanup.remove_wordpress_elements(soup)
        
        # Add static site optimizations
        self.add_static_optimizations(soup)
        
        # Add lazy loading to images
        self.images.add_lazy_loading(soup)

        # Optimize responsive image sizes
        self.images.optimize_responsive_images(soup)
        
        # Add copy code button to code blocks
        self.add_copy_code_button(soup)
        
        # Content freshness indicator disabled: it rendered a standalone
        # "Published … · Updated …" box that duplicated the dates the byline
        # (.entry-meta) already shows — same two dates, twice, one row apart.
        # The box only ever appeared when modified != published, which is
        # exactly when the byline also shows "Updated", so it was always
        # redundant. It carried no schema (dates live in the JSON-LD it read
        # from), so dropping it has no SEO impact. The method itself
        # (add_content_freshness_indicator) was removed rather than kept
        # dead — see git history if it's ever needed again.

        # Add reading time and word count to entry-meta
        self.add_reading_time_indicator(soup)
        
        # Fix inline CSS font URLs
        self.fix_inline_css_urls(soup)
        
        # Extract inline CSS to external files
        self.extract_inline_css(soup, current_url)
        
        # Consolidate small inline CSS files to reduce critical request chain
        self.consolidate_inline_css_files(soup)

        # Inlining of small WP-shipped stylesheets (rankmath, kadence/footer,
        # wpo-minify <2KB) is handled by html_transformer.py so it runs on
        # every page — not just incrementally regenerated ones.
        
        # Process WordPress embeds (convert to proper iframes)
        self.wp_cleanup.process_wordpress_embeds(soup)

        # Clean up WordPress admin AJAX URLs
        self.wp_cleanup.clean_wordpress_ajax_urls(soup)
        
        # Strip ?ver= query strings from asset URLs (CSS/JS)
        self.strip_asset_version_queries(soup)

        # Fix Splide carousel for Similar Posts section
        self.fix_splide_carousel(soup)

        # Add Utterances comments to every page
        self.add_utterances_comments(soup)
        
        # Add meta descriptions for taxonomy pages (tags/categories)
        self.seo_meta.add_taxonomy_meta_description(soup, current_url)

        # Deduplicate meta descriptions on paginated archive pages
        self.seo_meta.fix_pagination_meta_description(soup, current_url)

        # Add noindex to thin archive/taxonomy pages (tags, categories)
        self.seo_meta.add_noindex_to_thin_pages(soup, current_url)

        # Inject the homepage top band first: it emits the editorial
        # <h1 class="jkr-headline">, which must be the page's single H1.
        # ensure_homepage_h1() below is a fallback that only converts the
        # site-title to an H1 when none exists — running it after the inject
        # means it correctly stands down, leaving exactly one H1.
        #
        # This is a *structural* fallback only — it doesn't touch the h1's
        # text. A later pipeline stage, SEOFixer.lock_homepage_h1_text()
        # (scripts/fix_seo_issues.py), rewrites whatever h1 text ends up
        # here to the canonical Config.HOMEPAGE_TITLE. Same-named methods
        # in the two files used to make this two-stage relationship easy to
        # miss; the distinct names now say what each one actually does.
        self.inject_homepage_redesign(soup, current_url)

        # Ensure the homepage has an H1 (fallback if the redesign didn't inject)
        self.seo_meta.ensure_homepage_h1(soup, current_url)

        # Brutalist header/footer chrome (every page): JK monogram logo lockup,
        # relocate the footer social icons into the header (+ mobile drawer),
        # and slim the footer to a logo + copyright line.
        self.chrome.brand_and_relocate_social(soup)

        # Fix byline: published + updated time elements with no separator render
        # as "By James May 29, 2017 June 1, 2026". Insert a separator + 'Updated'
        # label, and hide the updated date if it renders identical to published.
        self.card_fixups.fix_byline_dates(soup)

        # Archive / related cards show at most 2 categories. Kadence joins
        # categories with literal " | " text nodes, which CSS can't hide, so a
        # post with 3+ categories left dangling "| | |" pipes on its cards.
        # Trim the extra links + separators in the DOM instead.
        self.card_fixups.trim_card_categories(soup)

        # Fix table structure (add proper header rows)
        self.card_fixups.fix_table_headers(soup)

        # Add markdown and API links to footer
        self.card_fixups.add_markdown_api_links(soup, current_url)
        
        # Add breadcrumb navigation with schema markup
        self.add_breadcrumb_navigation(soup, current_url)
        
        # Add related posts section (only for single posts)
        self.add_related_posts(soup, current_url)
        
        # Add social media links to bottom of posts
        self.add_social_media_links(soup)

        # Add BlogPosting JSON-LD schema to article pages
        self.schema.add_blogposting_schema(soup, current_url)

        # Add FAQPage JSON-LD when the article contains an FAQ section
        self.schema.add_faq_schema(soup)

        # Add site-level WebSite + Organization schema (all pages)
        self.schema.add_site_schema(soup)

        # Convert to string
        return str(soup)
    
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
                    print("   🎨 Fixed inline CSS font URLs")
    
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
    
    def strip_asset_version_queries(self, soup):
        """Strip ?ver= query strings from CSS/JS asset URLs.

        WordPress appends ?ver=x.y.z to asset URLs for cache busting. When these
        assets are downloaded to disk, the query string becomes part of the filename
        which breaks static file serving (e.g. Cloudflare Pages strips query strings
        from requests, so the file is never found).

        This method:
        1. Strips ?ver=... from all <link> href and <script> src attributes
        2. Renames any files on disk that have ?ver= in their filename
        """
        import re

        # Fix <link> stylesheet hrefs
        for link in soup.find_all('link', href=True):
            href = link['href']
            if '?ver=' in href:
                clean_href = re.sub(r'\?ver=[^&"\']+', '', href)
                link['href'] = clean_href
                # Rename the file on disk if it exists with the versioned name
                versioned_path = self.output_dir / href.lstrip('/')
                clean_path = self.output_dir / clean_href.lstrip('/')
                if versioned_path.exists() and not clean_path.exists():
                    clean_path.parent.mkdir(parents=True, exist_ok=True)
                    versioned_path.rename(clean_path)
                    print(f"   📦 Renamed asset: {href} → {clean_href}")

        # Fix <script> srcs
        for script in soup.find_all('script', src=True):
            src = script['src']
            if '?ver=' in src:
                clean_src = re.sub(r'\?ver=[^&"\']+', '', src)
                script['src'] = clean_src
                versioned_path = self.output_dir / src.lstrip('/')
                clean_path = self.output_dir / clean_src.lstrip('/')
                if versioned_path.exists() and not clean_path.exists():
                    clean_path.parent.mkdir(parents=True, exist_ok=True)
                    versioned_path.rename(clean_path)
                    print(f"   📦 Renamed asset: {src} → {clean_src}")

    def fix_splide_carousel(self, soup):
        """Fix the Kadence theme's Splide carousel for the Similar Posts section.

        The WordPress Kadence theme uses Splide.js for the related/similar posts
        carousel, but the JS was never included in the static export. This method
        adds Splide JS from CDN and initialization code.
        """
        # Only add if there's a Splide carousel on the page
        carousels = soup.find_all(class_=lambda x: x and 'kadence-slide-init' in x)
        if not carousels:
            return

        # Strip pre-baked Splide state classes from static HTML.
        # WordPress server-side rendering adds is-initialized/is-active/splide-initial
        # but without the JS these cause broken display (e.g. display:block on the list).
        # Splide will re-add them correctly when it mounts.
        for carousel in carousels:
            classes = carousel.get('class', [])
            for cls in ['is-initialized', 'is-active', 'splide-initial', 'is-rendered']:
                if cls in classes:
                    classes.remove(cls)
            carousel['class'] = classes

        # Add Splide arrow/pagination styles inline (CSS optimizer strips
        # them from the external stylesheet because JS-injected elements
        # don't exist in the static HTML at build time)
        if soup.head:
            splide_style = soup.new_tag('style')
            splide_style.string = """
.splide button.splide__arrow{background:transparent!important;opacity:1!important;width:36px!important;height:36px!important;border-radius:50%!important;border:2px solid #f6821f!important;transition:all .2s!important}
.splide button.splide__arrow:hover{background:#f6821f!important}
.splide button.splide__arrow svg{fill:#f6821f!important;width:16px!important;height:16px!important;transition:fill .2s!important}
.splide button.splide__arrow:hover svg{fill:#0a0a0a!important}
.splide button.splide__arrow--prev{left:0.5em!important}
.splide button.splide__arrow--next{right:0.5em!important}
.splide .splide__pagination{padding:0.75rem 0!important}
.splide .splide__pagination li{display:inline-block!important;line-height:0!important}
.splide .splide__pagination button.splide__pagination__page{background:#555!important;opacity:1!important;width:8px!important;height:8px!important;min-width:8px!important;min-height:8px!important;max-width:8px!important;max-height:8px!important;border-radius:50%!important;margin:0 3px!important;padding:0!important;transition:all .2s!important;border:none!important}
.splide .splide__pagination button.splide__pagination__page.is-active{background:#f6821f!important;transform:scale(1.4)}
"""
            soup.head.append(splide_style)

        # Add Splide JS from CDN (before </body>)
        body = soup.find('body')
        if not body:
            return

        # Add Splide JS
        splide_script = soup.new_tag('script')
        splide_script['src'] = '/js/splide.min.js'
        splide_script['defer'] = ''
        body.append(splide_script)

        # Add initialization script that reads the data attributes
        init_script = soup.new_tag('script')
        init_script.string = """
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('.kadence-slide-init.splide').forEach(function(el) {
    var cols = parseInt(el.dataset.columnsXxl || el.dataset.columnsMd || 3);
    var colsMd = parseInt(el.dataset.columnsMd || 3);
    var colsSm = parseInt(el.dataset.columnsSm || 2);
    var colsSs = parseInt(el.dataset.columnsSs || 1);
    var gutter = parseInt(el.dataset.sliderGutter || 40);
    var loop = el.dataset.sliderLoop === 'true';
    var arrows = el.dataset.sliderArrows === 'true';
    var dots = el.dataset.sliderDots === 'true';
    var autoplay = el.dataset.sliderAuto === 'true';
    var speed = parseInt(el.dataset.sliderAnimSpeed || 400);
    var perMove = parseInt(el.dataset.sliderScroll || 1);

    new Splide(el, {
      type: loop ? 'loop' : 'slide',
      perPage: cols,
      perMove: perMove,
      gap: gutter + 'px',
      arrows: arrows,
      pagination: dots,
      autoplay: autoplay,
      speed: speed,
      breakpoints: {
        1199: { perPage: colsMd },
        767: { perPage: colsSm },
        543: { perPage: colsSs }
      }
    }).mount();
  });
});
"""
        body.append(init_script)
        print("   🎠 Added Splide carousel JS and initialization")

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
        
        # Remove any existing comments area first (so we can re-insert in the correct position)
        comments_area = soup.find('div', id='comments')
        if comments_area:
            comments_area.decompose()

        # Find the entry-content div to insert comments immediately after it
        insertion_point = None
        articles = soup.find_all('article')
        if articles and len(articles) >= 1:
            article = articles[0]

            # Look for entry-content div inside the article - this is the main post content
            entry_content = article.find('div', class_=lambda x: x and 'entry-content' in x)

            if entry_content:
                # Insert immediately after the article content
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

            from config import Config as _utt_config

            script = soup.new_tag('script')
            script['src'] = 'https://utteranc.es/client.js'
            script['data-repo'] = _utt_config.UTTERANCES_REPO
            script['data-issue-term'] = 'pathname'
            script['data-theme'] = 'github-dark'
            script['crossorigin'] = 'anonymous'
            script['async'] = ''
            script['data-cfasync'] = 'false'  # Bypass Cloudflare Rocket Loader

            section.append(script)
            inner_div.append(section)
            comments_div.append(inner_div)

            # Insert immediately after article content
            insertion_point.insert_after(comments_div)
            print("   💬 Added Utterances comments section after article content")
    
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
        generator_meta['content'] = 'Static Site Generator 1.0'
        soup.head.append(generator_meta)
        
        # Add theme-color meta tag for mobile browsers
        # This colors the browser UI to match the site (improves mobile UX)
        existing_theme_color = soup.find('meta', attrs={'name': 'theme-color'})
        if not existing_theme_color:
            theme_color_meta = soup.new_tag('meta')
            theme_color_meta['name'] = 'theme-color'
            theme_color_meta['content'] = '#0a0a0a'  # Dark background - matches brutalist theme
            soup.head.append(theme_color_meta)
            print("   🎨 Added theme-color meta tag")
        else:
            # Update existing theme-color to match brutalist theme
            existing_theme_color['content'] = '#0a0a0a'
            print("   🎨 Updated theme-color meta tag to dark theme")
        
        # Add favicon links
        self.add_favicon_links(soup)
        
        # Inject brutalist theme CSS
        self.add_brutalist_theme_css(soup)
        
        # Add Plausible analytics if not already present
        self.add_plausible_analytics(soup)
        
        # Font preloads were removed: the inline critical CSS pins body to a
        # system-font stack, fonts.css uses font-display: optional (fonts that
        # arrive after the ~100 ms swap window are never rendered), and on
        # mobile the 138 KB of high-priority preloads contended with the LCP
        # image. See html_transformer._deep_clean_head for the matching
        # idempotent strip on previously-built pages.


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
        
        print("   🐞 Added favicon links for browser support")
    
    # WP-leaked inline CSS files we drop from the page entirely.
    # The brutalist theme already covers every visible element with !important
    # overrides, so these add parse cost (~150 ms on mobile) without changing
    # the rendered output. Gutenberg block content in posts may use the WP
    # preset variables (--wp--preset--color--*); if a regression appears,
    # re-introduce only `global-styles-inline-css` and `wp-block-library-inline-css`.
    _WP_INLINE_CSS_DROP_PATTERNS = (
        'wp-block-library-inline-css',
        'wp-block-heading-inline-css',
        'wp-block-paragraph-inline-css',
        'wp-block-table-inline-css',
        'wp-img-auto-sizes-contain-inline-css',
        'global-styles-inline-css',
        'classic-theme-styles-inline-css',
        'inline-styles-',
    )

    def consolidate_inline_css_files(self, soup):
        """Strip WP-leaked inline CSS link tags. Previously concatenated them
        into consolidated-inline-styles.min.css; now we drop them entirely
        because the brutalist theme overrides everything visible.
        """
        if not soup.head:
            return

        dropped = []
        for link in list(soup.find_all('link', rel='stylesheet')):
            href = link.get('href', '')
            if any(p in href for p in self._WP_INLINE_CSS_DROP_PATTERNS):
                link.decompose()
                dropped.append(href)

        # Also strip the link to the previously-generated consolidated file
        # so seeded pages from older builds don't keep fetching it.
        for link in list(soup.find_all('link', rel='stylesheet')):
            if link.get('href', '').endswith('/consolidated-inline-styles.min.css'):
                link.decompose()
                dropped.append(link.get('href', ''))
        for preload in list(soup.find_all('link', rel='preload')):
            if (preload.get('href') or '').endswith('/consolidated-inline-styles.min.css'):
                preload.decompose()

        if dropped:
            print(f"   🧹 Dropped {len(dropped)} WP-leaked inline CSS link(s)")

    def _sync_brutalist_css(self):
        """Copy brutalist-theme.css into the output tree when its CONTENT differs.

        Runs at most once per build (instance-guarded). Compares bytes rather
        than mtimes: the self-hosted runner reuses its workspace and git-checkout
        timestamps are unreliable, so the old `source.mtime > dest.mtime` gate
        could skip a genuine CSS-only edit. Because brutalist-theme.css is
        excluded from critical-CSS inlining and only ships as the external
        /assets/css/brutalist-theme.css file, that skip meant a CSS-only change
        silently failed to deploy on an incremental build (no content change to
        force a recopy). A byte compare is deterministic regardless of mtimes.
        """
        if getattr(self, '_brutalist_css_synced', False):
            return
        source = Path(__file__).parent / 'brutalist-theme.css'
        dest = self.output_dir / 'assets' / 'css' / 'brutalist-theme.css'
        if not source.exists():
            print(f"   ⚠️  Brutalist theme CSS not found at {source}")
            return
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            if not dest.exists() or source.read_bytes() != dest.read_bytes():
                shutil.copy(source, dest)
                print(f"   📋 Synced brutalist theme CSS → {dest}")
            self._brutalist_css_synced = True
        except OSError as e:
            print(f"   ⚠️  Failed to sync brutalist theme CSS: {e}")

    def add_brutalist_theme_css(self, soup):
        """Add brutalist theme CSS with critical mobile CSS inlined"""
        if not soup.head:
            return
        
        # Check if brutalist theme link is already injected
        existing_brutalist = soup.find('link', href='/assets/css/brutalist-theme.css')
        if existing_brutalist:
            return
        
        # Ensure the stylesheet is deployed to the output tree. Content-based
        # and idempotent (see _sync_brutalist_css); generate_static_site() also
        # calls it once up front, so this per-page call is normally a no-op.
        self._sync_brutalist_css()

        try:
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
            # IMPORTANT: Load synchronously (not media="print" trick) because this
            # CSS contains the @font-face declarations inline — the browser needs
            # to parse it to discover the font URLs and start downloading them.
            link = soup.new_tag('link', rel='stylesheet', href='/assets/css/brutalist-theme.css')
            link['media'] = 'all'
            soup.head.append(link)
            
            print("   🎨 Added brutalist theme CSS with non-blocking load")
        except Exception as e:
            print(f"   ❌ Failed to add brutalist theme CSS: {str(e)}")
    
    def add_plausible_analytics(self, soup):
        """Add Plausible Analytics script to the page if not already present.

        The script is served from a same-origin path (/js/script.js) via the
        Cloudflare Worker, which proxies to the Plausible CE instance. No
        DNS prefetch / preconnect needed — the request is to our own host."""
        if not soup.head:
            return

        # Import config for Plausible settings
        from config import Config

        plausible_script_url = Config.get_plausible_script_url()
        target_analytics_domain = Config.get_plausible_domain()

        # Drop any historical dns-prefetch / preconnect hints to the upstream
        # Plausible host — same-origin now, so they're noise that delays the
        # actual critical preconnects.
        legacy_plausible_host = Config.PLAUSIBLE_URL
        for hint in soup.find_all('link', rel=lambda r: r in ('dns-prefetch', 'preconnect')):
            href = hint.get('href') or ''
            if legacy_plausible_host in href:
                hint.decompose()

        # Look for existing Plausible script — historical pages may have the
        # absolute upstream URL; this also catches any third-party plugin
        # injection that snuck through.
        existing_plausible = soup.find('script', src=lambda x: x and 'script.js' in x and ('plausible' in x or x == plausible_script_url))
        
        if existing_plausible:
            # Update the data-domain attribute to ensure it's correct
            existing_plausible['data-domain'] = target_analytics_domain
            existing_plausible['defer'] = ''  # Use defer for better preconnect timing
            existing_plausible['data-cfasync'] = 'false'  # Bypass Cloudflare Rocket Loader
            # Remove async if it exists
            if existing_plausible.get('async'):
                del existing_plausible['async']
            print("   📊 Updated existing Plausible analytics configuration")
        else:
            # Add new Plausible script
            plausible_script = soup.new_tag('script')
            plausible_script['data-domain'] = target_analytics_domain
            plausible_script['defer'] = ''  # Use defer for better preconnect timing
            plausible_script['data-cfasync'] = 'false'  # Bypass Cloudflare Rocket Loader
            plausible_script['src'] = plausible_script_url
            soup.head.append(plausible_script)
            print("   📊 Added Plausible analytics script to page")
    
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
            print("   ℹ️  No code blocks found to add copy buttons")
    
    def add_reading_time_indicator(self, soup):
        """Add visible reading time and word count to the entry-meta section.

        Iterates over all <article> elements. Only processes articles that have
        an .entry-content div (i.e. full single-post content). Post cards on
        list pages (homepage, archives) lack .entry-content and are skipped.
        """
        articles = soup.find_all('article')
        if not articles:
            print("   ℹ️  Skipping reading time indicator - no articles found")
            return

        added = 0
        for article in articles:
            # Only process articles with full content - skip excerpt cards
            entry_content = article.find(class_='entry-content')
            if not entry_content:
                continue

            # Skip if reading time already present in this article
            if article.find(class_='reading-time'):
                continue

            # Find entry-meta within this specific article
            entry_meta = article.find('div', class_=lambda x: x and 'entry-meta' in x)
            if not entry_meta:
                continue

            # Extract text from entry-content only
            content_copy = entry_content.__copy__()
            for tag in content_copy(['script', 'style', 'nav', 'aside', 'footer', 'header']):
                tag.decompose()
            text = ' '.join(content_copy.get_text(separator=' ', strip=True).split())

            if len(text) < 100:
                continue

            # Calculate word count and reading time
            word_count = len(text.split())
            reading_minutes = max(1, round(word_count / 200))  # 200 words per minute average

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
            added += 1
            print(f"   📖 Added reading time: {reading_minutes} min ({word_count:,} words)")

        if added == 0 and not any(a.find(class_='entry-content') for a in articles):
            print("   ℹ️  Skipping reading time indicator - no articles with entry-content (list page)")
    
    def _compute_ribbon_stats(self):
        """Return the five momentum/credibility stats for the homepage ribbon.

        Keeps posts·words·days-since-last·deploys/mo·lighthouse — the signals
        worth surfacing above the fold. Each is computed in isolation and falls
        back to '—' (or None for days) rather than breaking the build. Cached on
        the instance so it only runs once per build.
        """
        if hasattr(self, '_cached_ribbon_stats'):
            return self._cached_ribbon_stats

        print("   📊 Computing homepage ribbon stats...")

        stats = {
            'posts_count': self._stat_posts_count(),
            'words_total': self._stat_words_total(),
            'days_since_last': self._stat_last_post_days(),
            'deploys_month': self._stat_deploys_this_month(),
            'lighthouse': self._stat_lighthouse_performance(),
        }
        self._cached_ribbon_stats = stats
        print(
            f"   📊 Ribbon: posts={stats['posts_count']} words={stats['words_total']} "
            f"days={stats['days_since_last']} deploys={stats['deploys_month']} "
            f"LH={stats['lighthouse']}"
        )
        return stats

    def _stat_posts_count(self):
        try:
            r = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/posts',
                params={'per_page': 1, 'status': 'publish', '_fields': 'id'},
                timeout=15,
            )
            if r.status_code == 200:
                return r.headers.get('X-WP-Total') or '—'
        except Exception as e:
            print(f"   ⚠️  posts.count: {e}")
        return '—'

    def _stat_last_post_days(self):
        """Integer days since the most recent post, or None if unavailable.

        The ribbon renders this as '{n}d since last post'; returning the raw
        integer (vs. the '8d ago' string) lets the markup format it inline.
        """
        try:
            r = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/posts',
                params={
                    'per_page': 1, 'orderby': 'date', 'order': 'desc',
                    'status': 'publish', '_fields': 'date_gmt',
                },
                timeout=15,
            )
            if r.status_code == 200:
                data = r.json()
                if data and data[0].get('date_gmt'):
                    from datetime import datetime, timezone
                    d = datetime.fromisoformat(data[0]['date_gmt'])
                    if d.tzinfo is None:
                        d = d.replace(tzinfo=timezone.utc)
                    return max(0, (datetime.now(timezone.utc) - d).days)
        except Exception as e:
            print(f"   ⚠️  last_post days: {e}")
        return None

    def _stat_words_total(self):
        """Sum of words across all published posts (paginated).

        Cached to .image_optimization_cache/words_total.json for 24 h so we
        don't refetch hundreds of post bodies on every build.
        """
        from pathlib import Path
        cache = Path('.image_optimization_cache') / 'words_total.json'
        try:
            if cache.exists():
                payload = json.loads(cache.read_text(encoding='utf-8'))
                if time.time() - payload.get('computed_at', 0) < 24 * 3600:
                    return payload.get('formatted', '—')
        except Exception as e:
            # Fall through to live compute — but say why the cache was unusable
            print(f"   ⚠️  words.total cache unreadable ({e}), recomputing")

        try:
            total = 0
            page = 1
            while True:
                r = self.session.get(
                    f'{self.wp_url}/wp-json/wp/v2/posts',
                    params={
                        'per_page': 100, 'page': page, 'status': 'publish',
                        '_fields': 'content',
                    },
                    timeout=60,
                )
                if r.status_code != 200:
                    if r.status_code == 400:
                        break  # past last page
                    print(f"   ⚠️  words.total: page {page} → {r.status_code}")
                    return '—'
                data = r.json()
                if not data:
                    break
                for post in data:
                    html = (post.get('content') or {}).get('rendered', '')
                    if html:
                        text = BeautifulSoup(html, 'html.parser').get_text(separator=' ')
                        total += len(text.split())
                if len(data) < 100:
                    break
                page += 1

            formatted = self._format_word_count(total)
            try:
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps({
                    'computed_at': time.time(),
                    'total': total,
                    'formatted': formatted,
                }))
            except Exception as e:
                print(f"   ⚠️  words.total cache write failed ({e}) — next build recomputes")
            return formatted
        except Exception as e:
            print(f"   ⚠️  words.total: {e}")
            return '—'

    @staticmethod
    def _format_word_count(n):
        if n >= 1_000_000:
            return f'{n/1_000_000:.1f}M'
        if n >= 1_000:
            return f'{round(n/1000)}k'
        return str(n) if n > 0 else '—'

    def _stat_deploys_this_month(self):
        try:
            import subprocess
            from datetime import date
            first = date.today().replace(day=1).isoformat()
            result = subprocess.run(
                ['git', 'log', f'--since={first}', '--oneline'],
                capture_output=True, text=True, timeout=10,
            )
            if result.returncode == 0:
                return str(sum(1 for line in result.stdout.splitlines() if line))
        except Exception as e:
            print(f"   ⚠️  deploys.month: {e}")
        return '—'

    def _fetch_top_categories(self, limit=9):
        """Return the top categories by post count: list of (name, href, count_str).

        href is the relative permalink (with parent prefix when nested), taken
        directly from WP's `link` field — this matters for child categories
        like `vmware-cloud-on-aws` whose real archive lives at
        `/category/vmware/vmware-cloud-on-aws/`, not `/category/vmware-cloud-on-aws/`.

        Pulls live from the WP REST API, sorts by count desc, caches on the
        instance. Returns [] on failure so callers can fall back.
        """
        if hasattr(self, '_cached_top_cats'):
            return self._cached_top_cats[:limit]
        try:
            cats = []
            page = 1
            while True:
                r = self.session.get(
                    f'{self.wp_url}/wp-json/wp/v2/categories',
                    params={
                        'per_page': 100, 'page': page, 'hide_empty': 'true',
                        '_fields': 'name,slug,count,link',
                    },
                    timeout=15,
                )
                if r.status_code != 200:
                    break
                data = r.json()
                if not data:
                    break
                cats.extend(data)
                if len(data) < 100:
                    break
                page += 1
            cats.sort(key=lambda c: -int(c.get('count') or 0))
            result = []
            for c in cats:
                name = c.get('name')
                link = c.get('link') or ''
                count = str(c.get('count') or 0)
                if not name or not link:
                    continue
                # Strip WP URL prefix to get a relative path the static site
                # serves. Same approach as get_all_content_urls() so we stay
                # consistent with what was actually generated on disk.
                href = link.replace(self.wp_url, '')
                if not href.startswith('/'):
                    href = '/' + href.lstrip('/')
                result.append((name, href, count))
            self._cached_top_cats = result
            return result[:limit]
        except Exception as e:
            print(f"   ⚠️  top categories: {e}")
            return []

    def _stat_lighthouse_performance(self):
        # Primary source is data/lighthouse-latest.json — the committed,
        # always-present single source of truth that generate_changelog itself
        # reads (a dict: {"performance": 94, ...}). The changelog history files
        # are only a fallback: static-output/changelog isn't populated until
        # generate_changelog runs later in the pipeline, and the public/ copy
        # is not committed (nothing under public/changelog/ is tracked), so on a
        # clean checkout it is absent and the ribbon showed '—'. Reading the
        # latest file first also avoids surfacing a stale cold-cache outlier
        # that lingered in a persisted runner workspace's history file.
        latest = Path('data') / 'lighthouse-latest.json'
        try:
            if latest.exists():
                data = json.loads(latest.read_text(encoding='utf-8'))
                perf = data.get('performance') if isinstance(data, dict) else None
                if isinstance(perf, (int, float)):
                    return f'{int(perf)}/100'
        except Exception as e:
            print(f"   ⚠️  lighthouse ({latest}): {e}")

        candidates = [
            self.output_dir / 'changelog' / 'lighthouse-history.json',
            Path('public') / 'changelog' / 'lighthouse-history.json',
        ]
        for history in candidates:
            try:
                if history.exists():
                    data = json.loads(history.read_text(encoding='utf-8'))
                    if isinstance(data, list) and data:
                        perf = data[-1].get('performance')
                        if isinstance(perf, (int, float)):
                            return f'{int(perf)}/100'
            except Exception as e:
                print(f"   ⚠️  lighthouse ({history}): {e}")
        return '—'

    def inject_homepage_redesign(self, soup, current_url):
        """Inject the homepage top band (Option B) + topic index.

        Adds, above the post grid:
          - top band: strap + filter on one row, the editorial <h1> headline,
            and a single-line stats ribbon (posts · words · days-since-last ·
            deploys/mo · lighthouse · ● live)
          - featured hero (newest post promoted out of the grid)
        And appends a topic index after the post grid.

        Skips paginated homepage pages (/page/2/, /page/3/, ...).
        """
        if current_url not in ('/', ''):
            return

        # Idempotency guard — don't double-inject if process_html runs twice
        if soup.find(class_='jkr-top'):
            return

        # Kadence renders the loop as a <ul class="kadence-posts-list ...">,
        # but use a tag-agnostic lookup in case the markup shifts.
        posts_list = soup.find(class_='kadence-posts-list')
        if not posts_list:
            print("   ⚠️  Homepage redesign: no .kadence-posts-list found — skipping")
            return

        # ── 0. featured-post hero (page-1 only) ─────────────────────────
        # Promote the newest post (first .loop-entry) into a wide hero card
        # above the grid. Removed from the grid so it doesn't double-render.
        hero = self._build_homepage_hero(soup, posts_list)

        # Hero extraction leaves the grid one short of a clean row in the
        # 3-col layout (WP serves 12 → hero takes 1 → 11 cards = 3 full
        # rows + 2 + an empty slot). Trim trailing cards down to the
        # nearest multiple of 3 so the last row is always full.
        self._trim_grid_to_columns(posts_list, columns=3)

        # ── 1. top band (Option B) ──────────────────────────────────────
        # Strap + filter share one row; the editorial headline is the page's
        # single <h1>; a one-line stats ribbon replaces the old terminal box.
        top = soup.new_tag('header', attrs={'class': 'jkr-top'})

        top_row = soup.new_tag('div', attrs={'class': 'jkr-top-row'})
        strap = soup.new_tag('span', attrs={'class': 'jkr-strap'})
        strap.string = 'VMWARE VEXPERT · HOMELAB · INFRASTRUCTURE-AS-CODE'
        top_row.append(strap)

        nav = soup.new_tag('nav', attrs={'class': 'jkr-filter', 'aria-label': 'Filter posts'})
        filter_label = soup.new_tag('span', attrs={'class': 'jkr-filter-label'})
        filter_label.string = 'FILTER'
        nav.append(filter_label)
        # "All" lands the user back on the homepage; the rest go to category archives.
        chips = (
            ('All', '/'),
            ('VMware', '/category/vmware/'),
            ('Homelab', '/category/homelab/'),
            ('Automation', '/category/automation/'),
            ('AI', '/category/artificial-intelligence/'),
        )
        for label, href in chips:
            attrs = {'href': href}
            if label == 'All':
                attrs['class'] = 'is-active'
            chip = soup.new_tag('a', attrs=attrs)
            chip.string = label
            nav.append(chip)
        top_row.append(nav)
        top.append(top_row)

        # ── 2. headline ─────────────────────────────────────────────────
        # Visible headline is the editorial line (a <p>, for design voice). The
        # page's actual <h1> is a screen-reader-only canonical title: it keeps
        # the keyword-rich heading fix_seo_issues.py wants (HOMEPAGE_TITLE)
        # without that pass overwriting the editorial copy. Exactly one <h1>.
        try:
            from config import Config
            seo_title = Config.HOMEPAGE_TITLE
        except (ImportError, AttributeError):
            seo_title = 'James Kilby — VMware, Homelab & Cloud Infrastructure Notes'
        seo_h1 = soup.new_tag('h1', attrs={'class': 'screen-reader-text jkr-sr-title'})
        seo_h1.string = seo_title
        top.append(seo_h1)

        headline = soup.new_tag('p', attrs={'class': 'jkr-headline'})
        headline.string = 'Field notes from a homelab that costs real money to run.'
        # Headline shares a row with the homepage search box, which is relocated
        # here from main[0] once it's injected (see _relocate_search_into_top).
        # The search fills the dead right-gutter beside the capped headline and
        # removes the standalone centered search island — reclaiming both the
        # vertical dead-zone under the header and the empty gutter. The wrapper
        # is emitted even before the search exists so the relocation has a slot.
        headline_row = soup.new_tag('div', attrs={'class': 'jkr-headline-row'})
        headline_row.append(headline)
        top.append(headline_row)

        # ── 3. stats ribbon (replaces the terminal box) ─────────────────
        stats = self._compute_ribbon_stats()
        ribbon = soup.new_tag(
            'div',
            attrs={'class': 'jkr-ribbon', 'role': 'status', 'aria-label': 'Blog stats'},
        )

        def _ribbon_stat(prefix, value, suffix):
            span = soup.new_tag('span')
            if prefix:
                span.append(soup.new_string(prefix))
            bold = soup.new_tag('b')
            bold.string = str(value)
            span.append(bold)
            if suffix:
                span.append(soup.new_string(suffix))
            return span

        days = stats['days_since_last']
        days_label = f'{days}d' if days is not None else '—'

        # Separators are drawn by CSS (.jkr-ribbon > span + span::before) so the
        # middot is glued to the following stat and can never orphan at a wrap
        # point — no literal '·' spans that flex-wrap onto their own line.
        ribbon.append(_ribbon_stat('', stats['posts_count'], ' posts'))
        ribbon.append(_ribbon_stat('', stats['words_total'], ' words'))
        ribbon.append(_ribbon_stat('', days_label, ' since last post'))
        ribbon.append(_ribbon_stat('', stats['deploys_month'], ' deploys/mo'))
        ribbon.append(_ribbon_stat('lighthouse ', stats['lighthouse'], ''))

        live = soup.new_tag('span', attrs={'class': 'jkr-r-live'})
        live.string = '● live'
        ribbon.append(live)
        top.append(ribbon)

        # ── 4. topic index ──────────────────────────────────────────────
        topics = soup.new_tag('section', attrs={'class': 'jkr-topics'})
        topics_head = soup.new_tag('div', attrs={'class': 'jkr-topics-head'})
        eyebrow = soup.new_tag('span', attrs={'class': 'jkr-eyebrow'})
        eyebrow.string = 'EXPLORE BY TOPIC'
        topics_h2 = soup.new_tag('h2', attrs={'class': 'jkr-topics-h2'})
        topics_h2.string = 'Browse the archive'
        topics_head.append(eyebrow)
        topics_head.append(topics_h2)
        topics.append(topics_head)

        topics_grid = soup.new_tag('div', attrs={'class': 'jkr-topics-grid'})
        # Live list from WP API uses the API's permalink directly so nested
        # categories (e.g. /category/vmware/vmware-cloud-on-aws/) resolve to
        # the right archive. The curated fallback below is used when the API
        # is unreachable — entries are pre-resolved hrefs verified against
        # the existing public/category/ tree.
        topic_list = self._fetch_top_categories(limit=9) or (
            ('VMware', '/category/vmware/', '—'),
            ('Homelab', '/category/homelab/', '—'),
            ('Automation', '/category/automation/', '—'),
            ('Artificial Intelligence', '/category/artificial-intelligence/', '—'),
            ('Ansible', '/category/ansible/', '—'),
            ('NVIDIA', '/category/nvidia/', '—'),
            ('Cloudflare', '/category/cloudflare/', '—'),
            ('Docker', '/category/docker/', '—'),
            ('Containers', '/category/containers/', '—'),
        )
        for name, href, count in topic_list:
            t = soup.new_tag('a', href=href, attrs={'class': 'jkr-topic'})
            t_name = soup.new_tag('span', attrs={'class': 'jkr-topic-name'})
            t_name.string = name
            t_count = soup.new_tag('span', attrs={'class': 'jkr-topic-count'})
            t_count.string = count
            t.append(t_name)
            t.append(t_count)
            topics_grid.append(t)
        topics.append(topics_grid)

        # ── insert ──────────────────────────────────────────────────────
        # Top band → hero sit above the post grid. Each insert_before lands the
        # node directly adjacent to posts_list, so the last one inserted ends up
        # closest to the grid: the top band first, then the hero pulled up right
        # above the post stream (and above the fold).
        posts_list.insert_before(top)
        if hero is not None:
            posts_list.insert_before(hero)
        posts_list.insert_after(topics)

        bits = ['top-band']
        if hero is not None:
            bits.append('hero')
        bits.append('topics')
        print(f"   ✨ Injected homepage redesign sections ({', '.join(bits)})")

    def _build_homepage_hero(self, soup, posts_list):
        """Promote the newest post (first .loop-entry inside posts_list) into a
        featured hero card. Returns the new <a.jkr-hero> element ready to be
        inserted before posts_list, or None if no candidate post is found.

        Side-effect: removes the source .loop-entry from posts_list so the grid
        starts at post #2.

        Drives change 3 of the Jun 2026 homepage refresh — see
        Downloads/design_handoff_homepage_refresh/PATCH-hero-and-meta.md §3.
        """
        first_entry = posts_list.find(class_='loop-entry')
        if not first_entry:
            return None

        # ── pull data from the source card ──
        title_a = first_entry.select_one('.entry-title a')
        if not title_a:
            return None
        title_text = title_a.get_text(strip=True)
        permalink = title_a.get('href', '#')

        # Featured image: reuse the WP-rendered <picture> verbatim so AVIF/WebP
        # sources, srcsets, alt text, and sizes survive untouched.
        picture = first_entry.select_one('.post-thumbnail picture')
        img = first_entry.select_one('.post-thumbnail img') if not picture else None

        # Categories: first two, in source order.
        cat_links = first_entry.select('.category-links a, .entry-taxonomies a')
        cats = []
        seen_cats = set()
        for a in cat_links:
            t = a.get_text(strip=True)
            if t and t not in seen_cats:
                seen_cats.add(t)
                cats.append(t)
            if len(cats) >= 2:
                break

        # Published date — text only (the hero never shows the modified date).
        pub_time = first_entry.select_one('time.entry-date.published') \
            or first_entry.select_one('time.published') \
            or first_entry.select_one('time.entry-date')
        pub_text = pub_time.get_text(strip=True) if pub_time else ''
        pub_datetime = pub_time.get('datetime') if pub_time else None

        # Excerpt.
        excerpt_p = first_entry.select_one('.entry-summary p, .entry-summary')
        excerpt_text = excerpt_p.get_text(strip=True) if excerpt_p else ''

        # ── build the hero element ──
        hero = soup.new_tag('a', href=permalink, attrs={'class': 'jkr-hero'})
        hero['aria-label'] = title_text

        media = soup.new_tag('div', attrs={'class': 'jkr-hero-media'})
        if picture:
            # Clone the <picture> so the original is left alone when we drop the
            # source entry. extract() detaches; we reattach into the hero.
            media.append(picture.extract())
        elif img:
            media.append(img.extract())
        else:
            media.append(soup.new_tag('div', attrs={'class': 'jkr-hero-media-fallback'}))

        badge = soup.new_tag('span', attrs={'class': 'jkr-hero-badge'})
        badge.string = 'LATEST'
        media.append(badge)
        hero.append(media)

        body = soup.new_tag('div', attrs={'class': 'jkr-hero-body'})

        if cats:
            cats_wrap = soup.new_tag('div', attrs={'class': 'jkr-hero-cats'})
            for c in cats:
                chip = soup.new_tag('span')
                chip.string = c
                cats_wrap.append(chip)
            body.append(cats_wrap)

        h_title = soup.new_tag('h2', attrs={'class': 'jkr-hero-title'})
        h_title.string = title_text
        body.append(h_title)

        if excerpt_text:
            p_excerpt = soup.new_tag('p', attrs={'class': 'jkr-hero-excerpt'})
            p_excerpt.string = excerpt_text
            body.append(p_excerpt)

        meta = soup.new_tag('div', attrs={'class': 'jkr-hero-meta'})
        if pub_text:
            date_span = soup.new_tag('time', attrs={'class': 'jkr-hero-date'})
            if pub_datetime:
                date_span['datetime'] = pub_datetime
            date_span.string = pub_text
            meta.append(date_span)
        cta = soup.new_tag('span', attrs={'class': 'jkr-hero-cta'})
        cta.string = 'Read post →'
        meta.append(cta)
        body.append(meta)

        hero.append(body)

        # Remove the source card so the grid starts at post #2. Kadence wraps
        # each article in <li class="entry-list-item"> — decomposing the
        # <article> alone leaves an empty <li> behind that the grid still
        # counts as a slot, so walk up to the nearest list-item wrapper first.
        to_remove = first_entry
        wrapper = first_entry.find_parent('li')
        if wrapper is not None and wrapper is not posts_list:
            to_remove = wrapper
        to_remove.decompose()

        return hero

    def _trim_grid_to_columns(self, posts_list, columns=3):
        """Trim trailing grid items so the card count is a multiple of `columns`.

        The post grid is a `columns`-wide CSS grid. Any orphan card on the
        last row paints as an empty slot; drop them so the layout always
        ends on a full row. No-ops when the count is already aligned.
        """
        items = posts_list.find_all('li', class_='entry-list-item', recursive=False)
        if not items:
            return
        remainder = len(items) % columns
        if remainder == 0:
            return
        for item in items[-remainder:]:
            item.decompose()
        print(f"   ✂️  Trimmed {remainder} orphan grid slot(s) to keep the {columns}-col layout balanced")

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
                elif href.startswith('//'):
                    # Protocol-relative URL (external CDN) - skip
                    print(f"   ⏭️  Skipping external protocol-relative URL: {href}")
                    continue
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
                                elif clean_url.startswith('//'):
                                    # Protocol-relative URL (external CDN) - skip
                                    continue
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
        print("   🔍 Manually detecting WordPress minified cache files...")
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
                    
                # Strip query strings (e.g. ?ver=1.4.5) from file paths
                import re as _re
                relative_path = _re.sub(r'\?.*$', '', relative_path)

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
            print("   Recent downloads:")
            for result in success_results[:5]:
                print(f"     {result}")
        
        if error_results:
            print("   ⚠️  Some download errors:")
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
            
            # Add BreadcrumbList JSON-LD schema — but only if the page
            # doesn't already have one in an existing @graph block. Rank
            # Math emits its own BreadcrumbList inside the main @graph on
            # most posts; emitting a second standalone copy here triggers
            # "Breadcrumbs item not specified" warnings in Search Console
            # and dilutes the rich-result signal.
            if soup.head and not self._has_existing_breadcrumblist(soup):
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
            else:
                print(f"   🍞 Added breadcrumb nav (HTML only — existing BreadcrumbList in @graph): {' > '.join([item['name'] for item in breadcrumb_items])}")

    @staticmethod
    def _has_existing_breadcrumblist(soup):
        """Return True if any JSON-LD block on the page already declares a
        BreadcrumbList (standalone or inside an @graph).
        """
        for script in soup.find_all('script', type='application/ld+json'):
            raw = script.string or ''
            if not raw.strip():
                continue
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict):
                if data.get('@type') == 'BreadcrumbList':
                    return True
                graph = data.get('@graph')
                if isinstance(graph, list) and any(
                    isinstance(n, dict) and n.get('@type') == 'BreadcrumbList'
                    for n in graph
                ):
                    return True
        return False
    
    def build_post_index(self):
        """Bulk-fetch all published posts once and store in self.post_index.

        Replaces the per-post WordPress API calls previously made from
        add_related_posts(). After this runs, related-post scoring is a pure
        in-memory operation against integer category/tag ID sets.

        Index entry shape:
            {
                'cats':  set[int],   # category term IDs
                'tags':  set[int],   # tag term IDs
                'date':  str,        # ISO 8601 published date
                'title': str,        # rendered title (may contain HTML entities)
            }

        Keyed by relative URL (`post['link']` minus `self.wp_url`), matching
        the `current_url` argument that process_html() passes to
        add_related_posts().
        """
        print("📚 Building post index for related-posts scoring...")
        index = {}
        page = 1
        while True:
            resp = self.session.get(
                f'{self.wp_url}/wp-json/wp/v2/posts',
                params={
                    'per_page': 100,
                    'page': page,
                    'status': 'publish',
                    '_fields': 'id,link,date,categories,tags,title',
                },
            )
            if resp.status_code != 200:
                # 400 = past the last page on WP REST; anything else is a real
                # failure but should not break the rest of the build — the
                # related-posts section just won't render.
                if resp.status_code not in (400,):
                    print(f"   ⚠️  Post index fetch returned {resp.status_code} on page {page}")
                break
            try:
                posts = resp.json()
            except (json.JSONDecodeError, ValueError):
                print(f"   ⚠️  Invalid JSON on post-index page {page}")
                break
            if not posts:
                break
            for post in posts:
                relative_url = post['link'].replace(self.wp_url, '')
                index[relative_url] = {
                    'cats': set(post.get('categories') or []),
                    'tags': set(post.get('tags') or []),
                    'date': post.get('date') or '',
                    'title': (post.get('title') or {}).get('rendered', ''),
                }
            page += 1

        self.post_index = index
        total_cats = sum(len(p['cats']) for p in index.values())
        total_tags = sum(len(p['tags']) for p in index.values())
        print(f"   ✅ Indexed {len(index)} posts ({total_tags} tag refs, {total_cats} category refs)")

    def add_related_posts(self, soup, current_url):
        """Inject a 'Related Posts' section scored against self.post_index.

        Score formula:
            score = 3 * |shared_tags| + 2 * |shared_categories|
        Ties broken by recency (newer first). Top 3 selected.

        Tags are weighted higher than categories because categories are
        coarse hubs ("Homelab") while tags are specific facets ("packer",
        "vsan") — overlap on a tag is a stronger topical signal.

        Fallback when no candidate has any overlap: newest 3 posts that
        share at least one category (matches the legacy behaviour). This
        preserves the section's existence on posts whose tags/categories
        are unique enough to score zero against the rest of the corpus.
        """
        body = soup.find('body')
        if not body:
            return

        body_classes = body.get('class', [])
        body_class_str = ' '.join(body_classes).lower()
        if 'single-post' not in body_class_str and 'single' not in body_classes:
            return

        # Avoid double-injection on repeat process_html passes
        for existing in soup.find_all('section', class_='related-posts-section'):
            existing.decompose()

        current_entry = self.post_index.get(current_url)
        if not current_entry:
            # Post isn't in the index — index didn't build, or this is a
            # page/archive misclassified as a single post. Skip silently.
            return

        cur_cats = current_entry['cats']
        cur_tags = current_entry['tags']
        if not cur_cats and not cur_tags:
            return

        scored = []
        for url, entry in self.post_index.items():
            if url == current_url:
                continue
            shared_tags = len(cur_tags & entry['tags'])
            shared_cats = len(cur_cats & entry['cats'])
            score = 3 * shared_tags + 2 * shared_cats
            if score > 0:
                scored.append((score, entry['date'], url, entry['title']))

        if scored:
            # Sort by score desc, then date desc (newer breaks ties). ISO 8601
            # dates sort lexicographically the same as chronologically, so a
            # single tuple sort works.
            scored.sort(key=lambda x: (x[0], x[1]), reverse=True)
            selected = scored[:3]
        else:
            # Fallback: newest 3 sharing any category
            fallback = [
                (entry['date'], url, entry['title'])
                for url, entry in self.post_index.items()
                if url != current_url and (cur_cats & entry['cats'])
            ]
            fallback.sort(reverse=True)  # date desc
            selected = [(0, d, u, t) for d, u, t in fallback[:3]]

        if not selected:
            return

        # Styling lives in brutalist-theme.css (.related-posts-section) using
        # theme tokens — no inline light-theme styles (they were off-palette
        # blue/rounded/shadowed and only survived via global !important resets).
        related_section = soup.new_tag('section')
        related_section['class'] = 'related-posts-section'

        heading = soup.new_tag('h2')
        heading.string = '📚 Related Posts'
        related_section.append(heading)

        posts_list = soup.new_tag('ul')
        posts_list['class'] = 'related-posts-list'

        for _score, _date, rel_url, title in selected:
            li = soup.new_tag('li')
            li['class'] = 'related-posts-item'
            link = soup.new_tag('a')
            link['href'] = rel_url
            link.string = title
            li.append(link)
            posts_list.append(li)

        related_section.append(posts_list)

        entry_content = soup.find('div', class_=lambda x: x and 'entry-content' in x)
        if entry_content:
            article = entry_content.find_parent('article')
            if article:
                comments = article.find('div', id='comments')
                if comments:
                    comments.insert_after(related_section)
                else:
                    entry_content.insert_after(related_section)
                print(f"   📚 Added {len(selected)} related posts (score-based)")

    def add_social_media_links(self, soup):
        """Add social media links (GitHub, Twitter, LinkedIn) to the bottom of each post"""
        
        # Only add to single post pages and regular pages
        body = soup.find('body')
        if not body:
            return
        
        body_classes = body.get('class', [])
        body_class_str = ' '.join(body_classes).lower()
        
        # Add to single posts and pages (not archive/list pages)
        is_single_post = 'single-post' in body_class_str or 'single' in body_classes
        is_page = 'page-template' in body_class_str or ('page' in body_classes and 'single' not in body_class_str)
        
        if not (is_single_post or is_page):
            return  # Not a single post/page, skip social links
        
        # Find the entry-content div to add social links after it
        entry_content = soup.find('div', class_=lambda x: x and 'entry-content' in x)
        
        if not entry_content:
            return
        
        # Create social media section
        social_section = soup.new_tag('div')
        social_section['class'] = 'social-media-links'
        social_section['style'] = '''margin: 40px 0 20px 0; padding: 20px 0; border-top: 2px solid #e2e8f0; text-align: center;'''
        
        # Heading
        heading = soup.new_tag('p')
        heading['style'] = 'margin: 0 0 15px 0; font-size: 16px; color: #4a5568; font-weight: 500;'
        heading.string = 'Connect with me:'
        social_section.append(heading)
        
        # Links container
        links_container = soup.new_tag('div')
        links_container['style'] = 'display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;'
        
        # Social media links — Config.SOCIAL_PROFILES is the single source of
        # truth, shared with the JSON-LD sameAs graph.
        from config import Config as _social_config
        social_links = list(_social_config.SOCIAL_PROFILES)
        
        # Create link for each platform
        for platform in social_links:
            link = soup.new_tag('a')
            link['href'] = platform['url']
            link['target'] = '_blank'
            link['rel'] = 'noopener noreferrer'
            link['style'] = f'''display: inline-block; padding: 8px 16px; 
                background: transparent; border: 1px solid {platform['color']}; border-radius: 4px; 
                color: {platform['color']}; text-decoration: none; font-weight: 500; font-size: 14px;
                transition: all 0.2s; hover: background: {platform['color']}; hover: color: white;'''
            link.string = platform['name']
            
            links_container.append(link)
        
        social_section.append(links_container)
        
        # Insert after the entry-content
        entry_content.insert_after(social_section)
        
        print("   🔗 Added social media links (GitHub, Twitter, LinkedIn)")
    
    def generate_static_site(self):
        """Main generation process"""
        print("🚀 WordPress to Static Site Generator")
        print(f"Source: {self.wp_url}")
        print(f"Target: {self.target_domain}")
        print(f"Output: {self.output_dir}")
        
        # Show build mode
        if self.incremental_builder:
            cache_stats = self.incremental_builder.get_stats()
            if cache_stats['last_build']:
                print(f"Mode: Incremental (cache has {cache_stats['posts_cached'] + cache_stats['pages_cached']} entries)")
            else:
                print("Mode: Full build (creating cache)")
        else:
            print("Mode: Full build (incremental disabled)")
        
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

        # Sync the stylesheet up front so a CSS-only edit deploys even when no
        # page ends up being reprocessed this build (content-based, idempotent).
        self._sync_brutalist_css()

        # Get all URLs from WordPress
        urls = self.get_all_content_urls()

        # Discover all media assets via WordPress API
        print("\\n🖼️  Media Asset Discovery:")
        media_assets = self.get_all_media_assets()

        # Build the post index used by add_related_posts(). Must happen
        # before the parallel processing pool starts so worker threads see
        # a fully-populated, read-only dict.
        self.build_post_index()

        # Download and process all content
        print(f"\\n⬇️  Processing {len(urls)} URLs...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            results = list(executor.map(self.download_and_process_url, urls))
        
        # Print results summary
        success_count = len([r for r in results if r.startswith('✅')])
        failed_results = [r for r in results if not r.startswith('✅') and not r.startswith('⏭️')]
        error_count = len(failed_results)
        print("\\n📊 Processing Results:")
        print(f"   ✅ Success: {success_count}")
        print(f"   ❌ Failed: {error_count}")
        for fail in failed_results:
            print(f"      {fail}")
        
        # Download assets
        print("\\n📁 Asset Processing:")
        self.download_assets()
        
        # Copy static assets (fonts, CSS, etc.)
        print("\n📦 Static Assets:")
        self.artifacts.copy_assets()

        # Create additional files
        print("\n📄 Creating additional files:")
        self.artifacts.create_security_headers()
        self.artifacts.create_robots_txt()
        self.artifacts.create_redirects_file()
        self.artifacts.create_sitemap()
        self.artifacts.generate_rss_feed()
        self.artifacts.generate_search_index()
        self.artifacts.copy_search_script()
        self.artifacts.copy_static_root_files()
        self.artifacts.inject_search_script()
        self.artifacts.inject_power_widget()

        # NOTE: contextual internal links for orphan posts are injected by a
        # dedicated POST-TRANSFORM pipeline step (scripts/internal_links.py),
        # not here. Doing it in-generator logged "N/N linked" from the
        # pre-transform DOM, but incremental-skip / raw-snapshot / transform
        # interactions dropped some links from the files that actually shipped.
        # The post-transform step runs over the final output and verifies the
        # links survived on disk. See Makefile `internal-links` / the workflow.

        # Summary
        end_time = time.time()
        duration = end_time - start_time
        
        print("\\n🎉 GENERATION COMPLETE!")
        print(f"Duration: {duration:.1f} seconds")
        print(f"Output directory: {self.output_dir}")
        
        # Show directory size
        total_size = sum(f.stat().st_size for f in self.output_dir.rglob('*') if f.is_file())
        print(f"Total size: {total_size / 1024 / 1024:.1f} MB")
        
        # Generate build metrics report
        print("\n📊 Generating build report:")
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
            print("\n📦 Build Cache:")
            print(f"   Cached posts: {stats['posts_cached']}")
            print(f"   Cached pages: {stats['pages_cached']}")
            if not is_full_build:
                print("   ⚡ Incremental build — only changed content regenerated")
        
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
        print("\\n💡 Next steps:")
        print(f"1. Review the generated files in: {output_dir}")
        print(f"2. Test locally: python -m http.server 8000 --directory {output_dir}")
        print("3. Deploy to your hosting platform")
        print("4. Verify old URLs redirect correctly")
        
        if deploy_flag:
            print("\\n🚀 Deploy flag detected - implement your deployment logic here")
            # You could add deployment logic here for Cloudflare, Netlify, etc.
    else:
        print("❌ Generation failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
