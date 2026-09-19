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
# Content-enrichment UX (copy-code button, reading-time indicator) — fully
# stateless, see that module's docstring.
from content_enrichment_ux import ContentEnrichmentUX
# Breadcrumb navigation + BreadcrumbList schema — only needs target_domain,
# see that module's docstring.
from breadcrumb_navigation import BreadcrumbNavigation
# Social links footer — fully stateless, see that module's docstring.
from social_links import SocialLinks
# Homepage stats ribbon + layout redesign (top band, hero, topic index) —
# needs session/wp_url/output_dir, see that module's docstring.
from homepage_redesign import HomepageRedesign
# WordPress REST API content/media discovery (URL enumeration, media-asset
# listing, taxonomy pagination) — needs session/wp_url/incremental_builder/
# downloaded_assets, see that module's docstring.
from wp_content_discovery import WPContentDiscovery
# Static asset extraction + download — needs session/wp_url/target_domain/
# output_dir/downloaded_assets, see that module's docstring.
from asset_pipeline import AssetPipeline
# Related-posts index + injection — needs session/wp_url, see that
# module's docstring.
from related_posts import RelatedPosts

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
        # Content-enrichment UX — see content_enrichment_ux.py. Fully
        # stateless; takes no constructor arguments.
        self.enrichment = ContentEnrichmentUX()
        # Breadcrumb navigation + schema — see breadcrumb_navigation.py.
        # Only needs target_domain.
        self.breadcrumbs = BreadcrumbNavigation(self.target_domain)
        # Social links footer — see social_links.py. Fully stateless;
        # takes no constructor arguments.
        self.social = SocialLinks()
        # Homepage stats ribbon + layout redesign (top band, hero, topic
        # index) — see homepage_redesign.py. Needs session/wp_url/output_dir.
        self.homepage = HomepageRedesign(self.session, self.wp_url, self.output_dir)
        # WordPress REST API content/media discovery — see
        # wp_content_discovery.py. Shares downloaded_assets with the asset
        # pipeline: media-library URLs discovered here are folded into the
        # same set download_assets() consumes.
        self.discovery = WPContentDiscovery(
            self.session, self.wp_url, self.incremental_builder, self.downloaded_assets
        )
        # Static asset extraction + download — see asset_pipeline.py. Shares
        # downloaded_assets with self.discovery (both write into it).
        self.assets = AssetPipeline(
            self.session, self.wp_url, self.target_domain, self.output_dir, self.downloaded_assets
        )
        # Related-posts index + injection — see related_posts.py. Needs
        # session/wp_url; owns post_index (built once per build, read per
        # single-post page — see that module's docstring for the threading
        # note).
        self.related_posts = RelatedPosts(self.session, self.wp_url)

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
        self.assets.extract_assets(soup, current_url)
        
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
        self.enrichment.add_copy_code_button(soup)
        
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
        self.enrichment.add_reading_time_indicator(soup)
        
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
        self.homepage.inject_homepage_redesign(soup, current_url)

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
        self.breadcrumbs.add_breadcrumb_navigation(soup, current_url)
        
        # Add related posts section (only for single posts)
        self.related_posts.add_related_posts(soup, current_url)
        
        # Add social media links to bottom of posts
        self.social.add_social_media_links(soup)

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
        urls = self.discovery.get_all_content_urls()

        # Discover all media assets via WordPress API
        print("\\n🖼️  Media Asset Discovery:")
        media_assets = self.discovery.get_all_media_assets()

        # Build the post index used by add_related_posts(). Must happen
        # before the parallel processing pool starts so worker threads see
        # a fully-populated, read-only dict.
        self.related_posts.build_post_index()

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
        self.assets.download_assets()
        
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
