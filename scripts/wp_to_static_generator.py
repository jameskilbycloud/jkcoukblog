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
# Inline CSS extraction + asset-URL cleanup — needs wp_url/output_dir, see
# that module's docstring.
from inline_css_fixups import InlineCSSFixups
# Head-chrome + static-site optimizations (comments, favicons, brutalist
# CSS, analytics) — the last slice of this decomposition; needs
# output_dir, see that module's docstring.
from head_chrome_optimizations import HeadChromeOptimizations

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
        # Inline CSS extraction + asset-URL cleanup — see
        # inline_css_fixups.py. Needs wp_url/output_dir; owns
        # extracted_css_files/css_output_dir (dedup cache across pages).
        self.inline_css = InlineCSSFixups(self.wp_url, self.output_dir)
        # Head-chrome + static-site optimizations — see
        # head_chrome_optimizations.py. Needs output_dir.
        self.head_chrome = HeadChromeOptimizations(self.output_dir)

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
        self.head_chrome.add_static_optimizations(soup)
        
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
        self.inline_css.fix_inline_css_urls(soup)
        
        # Extract inline CSS to external files
        self.inline_css.extract_inline_css(soup, current_url)
        
        # Consolidate small inline CSS files to reduce critical request chain
        self.head_chrome.consolidate_inline_css_files(soup)

        # Inlining of small WP-shipped stylesheets (rankmath, kadence/footer,
        # wpo-minify <2KB) is handled by html_transformer.py so it runs on
        # every page — not just incrementally regenerated ones.
        
        # Process WordPress embeds (convert to proper iframes)
        self.wp_cleanup.process_wordpress_embeds(soup)

        # Clean up WordPress admin AJAX URLs
        self.wp_cleanup.clean_wordpress_ajax_urls(soup)
        
        # Strip ?ver= query strings from asset URLs (CSS/JS)
        self.inline_css.strip_asset_version_queries(soup)

        # Fix Splide carousel for Similar Posts section
        self.inline_css.fix_splide_carousel(soup)

        # Add Utterances comments to every page
        self.head_chrome.add_utterances_comments(soup)
        
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
        self.head_chrome._sync_brutalist_css()

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
