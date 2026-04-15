#!/usr/bin/env python3
"""
Single-pass HTML Transformer

Applies all HTML transforms (SEO, images, performance, critical CSS, minification)
in one BeautifulSoup parse/serialize cycle per file, instead of 5-6 separate passes.

Transform order (each depends on the previous being stable):
  1. SEO fixes         — title, meta, canonical, H1, alt text, JSON-LD
  2. Image → picture   — wraps <img> in <picture> with AVIF/WebP <source>
  3. Performance hints  — async/defer, lazy loading, preconnect, preload
  4. Critical CSS       — extract above-fold CSS, inline in <head>, async preload
  5. Dedup head links   — clean up any accumulated noscript/link duplicates
  6. Minification       — collapse whitespace, strip comments (string-level)

The original standalone scripts remain functional for individual use.
"""

import sys
import re
import time
import argparse
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

# Ensure scripts/ is on the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fix_seo_issues import SEOFixer
from enhance_html_performance import HTMLPerformanceEnhancer
from convert_images_to_picture import ImageToPictureConverter
from extract_critical_css import CriticalCSSExtractor
from minify_html import minify_html


class HTMLTransformer:
    """Single-pass HTML transformer that applies all optimizations per file."""

    def __init__(self, public_dir='public', skip_images=False, skip_critical_css=False):
        self.public_dir = Path(public_dir)
        self.skip_images = skip_images
        self.skip_critical_css = skip_critical_css

        # Instantiate the transform classes — we'll call their per-soup methods
        self.seo = SEOFixer(public_dir)
        self.perf = HTMLPerformanceEnhancer(public_dir)
        self.pictures = ImageToPictureConverter(str(public_dir))
        self.critical_css = CriticalCSSExtractor(public_dir)

        # Stats
        self.files_processed = 0
        self.files_modified = 0
        self.total_bytes_saved = 0

    def process_all_files(self):
        """Process all HTML files in a single pass each."""
        html_files = list(self.public_dir.rglob('*.html'))

        # Exclude feeds and sitemaps (same filter as SEOFixer)
        html_files = [f for f in html_files if not any(
            pattern in str(f) for pattern in ['feed/', 'sitemap']
        )]

        if not html_files:
            print("⚠️  No HTML files found to transform")
            return

        print(f"🔄 Single-pass HTML transformer: {len(html_files)} files")
        start_time = time.time()

        for html_file in html_files:
            self.files_processed += 1
            try:
                if self._process_file(html_file):
                    self.files_modified += 1
            except Exception as e:
                print(f"⚠️  Error processing {html_file.name}: {e}")

            # Progress every 50 files
            if self.files_processed % 50 == 0:
                print(f"   ⏳ {self.files_processed}/{len(html_files)} files...")

        elapsed = time.time() - start_time
        self._print_summary(elapsed)

    def _process_file(self, file_path):
        """Apply all transforms to a single HTML file in one parse cycle."""
        original_html = file_path.read_text(encoding='utf-8')
        original_size = len(original_html.encode('utf-8'))

        # ── Phase 0: Aggressive string-level cleanup ────────────────────
        # Seeded files from public/ may carry accumulated corruption from
        # prior pipeline runs (orphaned </noscript> tags, preload links
        # missing onload handlers).  Fix this before BS4 parses.
        html = self._deep_clean_head(original_html)

        # Parse once
        soup = BeautifulSoup(html, 'html.parser')
        modified = False

        # ── Phase 1: SEO fixes ──────────────────────────────────────────
        if self._apply_seo_fixes(soup, file_path):
            modified = True

        # ── Phase 2: Image → picture conversion ─────────────────────────
        if not self.skip_images:
            if self._apply_picture_conversion(soup):
                modified = True

        # ── Phase 3: Performance enhancements ────────────────────────────
        if self._apply_performance_hints(soup):
            modified = True

        # ── Phase 4: Critical CSS extraction + inlining ──────────────────
        if not self.skip_critical_css:
            if self._apply_critical_css(soup, file_path):
                modified = True

        if not modified:
            return False

        # Serialize once
        result_html = str(soup)

        # ── Phase 5: String-level dedup of head links ────────────────────
        # This catches any noscript/link duplicates introduced by critical CSS
        result_html = self._dedup_head_string(result_html)

        # ── Phase 6: Minification (string-level) ────────────────────────
        result_html = minify_html(result_html)

        # Write once
        new_size = len(result_html.encode('utf-8'))
        self.total_bytes_saved += max(0, original_size - new_size)
        file_path.write_text(result_html, encoding='utf-8')
        return True

    # ── Per-phase wrappers that call existing class methods on soup ──────

    @staticmethod
    def _deep_clean_head(html):
        """Aggressive string-level cleanup of <head> before BS4 parsing.

        Seeded files from public/ may carry accumulated corruption from prior
        pipeline runs:
        - Dozens of orphaned </noscript> closing tags
        - Preload links missing onload handlers (CSS never applies)
        - Duplicate <link> tags

        This method resets the <head> to a clean state so subsequent transforms
        (critical CSS, preload conversion) can work from a known baseline.
        """
        head_match = re.search(
            r'(<head\b[^>]*>)(.*?)(</head>)',
            html,
            re.IGNORECASE | re.DOTALL,
        )
        if not head_match:
            return html

        head_open = head_match.group(1)
        head_body = head_match.group(2)
        head_close = head_match.group(3)

        # 1. Strip ALL <noscript> blocks and orphaned </noscript> tags
        head_body = re.sub(
            r'<noscript\b[^>]*>.*?</noscript>',
            '',
            head_body,
            flags=re.IGNORECASE | re.DOTALL,
        )
        head_body = re.sub(r'</noscript>', '', head_body, flags=re.IGNORECASE)

        # 2. Revert preload-as-style back to stylesheet so critical CSS phase
        #    can redo the conversion cleanly with proper onload handlers.
        #    Match: <link ... rel="preload" ... as="style" ...>
        def _revert_preload(m):
            tag = m.group(0)
            # Only revert CSS preloads (as="style"), not font/image/script preloads
            if not re.search(r'\bas=["\']style["\']', tag, re.IGNORECASE):
                return tag
            # Remove as="style" and onload attributes
            tag = re.sub(r'\s*as=["\']style["\']', '', tag, flags=re.IGNORECASE)
            tag = re.sub(r'\s*onload=["\'][^"\']*["\']', '', tag, flags=re.IGNORECASE)
            # Change rel="preload" to rel="stylesheet"
            tag = re.sub(r'rel=["\']preload["\']', 'rel="stylesheet"', tag, flags=re.IGNORECASE)
            return tag

        head_body = re.sub(r'<link\b[^>]*/?\s*>', _revert_preload, head_body, flags=re.IGNORECASE)

        # 3. Deduplicate <link> tags by href
        seen_hrefs = set()

        def _dedup(m):
            tag = m.group(0)
            href_m = re.search(r'\bhref=["\']([^"\']+)["\']', tag, re.IGNORECASE)
            if not href_m:
                return tag
            href = href_m.group(1)
            if href in seen_hrefs:
                return ''
            seen_hrefs.add(href)
            return tag

        head_body = re.sub(r'<link\b[^>]*/?\s*>', _dedup, head_body, flags=re.IGNORECASE)

        # 4. Collapse blank lines
        head_body = re.sub(r'\n{3,}', '\n\n', head_body)

        return html[:head_match.start()] + head_open + head_body + head_close + html[head_match.end():]

    def _apply_seo_fixes(self, soup, file_path):
        """Apply all SEO transforms from SEOFixer on the soup object."""
        modified = False
        if self.seo.fix_title_length(soup, file_path):
            modified = True
        if self.seo.fix_meta_description(soup, file_path):
            modified = True
        if self.seo.fix_multiple_h1(soup, file_path):
            modified = True
        if self.seo.ensure_image_alt_text(soup, file_path):
            modified = True
        if self.seo.fix_canonical_url(soup, file_path):
            modified = True
        if self.seo.fix_og_absolute_urls(soup, file_path):
            modified = True
        if self.seo.fix_jsonld_absolute_ids(soup, file_path):
            modified = True
        if self.seo.fix_blogposting_to_techarticle(soup, file_path):
            modified = True
        if self.seo.fix_breadcrumb_positions(soup, file_path):
            modified = True
        if self.seo.fix_person_name(soup, file_path):
            modified = True
        return modified

    def _apply_picture_conversion(self, soup):
        """Convert img tags to picture elements using ImageToPictureConverter methods."""
        modified = False

        # Update existing picture elements with responsive srcsets
        updated = self.pictures._update_existing_picture_srcsets(soup)
        if updated > 0:
            modified = True

        # Convert standalone img tags
        for img in soup.find_all('img'):
            if not self.pictures._should_convert_img(img):
                self.pictures.stats['images_skipped'] += 1
                continue

            has_avif, has_webp = self.pictures._has_modern_format(
                img.get('src', ''),
                self.pictures.directory
            )

            if not (has_avif or has_webp):
                self.pictures.stats['images_skipped'] += 1
                continue

            picture = self.pictures._create_picture_element(img, has_avif, has_webp)
            img.replace_with(picture)
            self.pictures.stats['images_converted'] += 1
            modified = True

        return modified

    def _apply_performance_hints(self, soup):
        """Apply all performance enhancements from HTMLPerformanceEnhancer."""
        modified = False
        if self.perf.add_async_defer_to_scripts(soup):
            modified = True
        if self.perf.add_media_attributes_to_css(soup):
            modified = True
        if self.perf.optimize_external_scripts(soup):
            modified = True
        if self.perf.add_resource_hints(soup):
            modified = True
        if self.perf.optimize_fonts(soup):
            modified = True
        if self.perf.add_preload_hints(soup):
            modified = True
        if self.perf.optimize_images(soup):
            modified = True
        return modified

    def _apply_critical_css(self, soup, file_path):
        """Extract and inline critical CSS, convert stylesheets to async preload."""
        critical_css = self.critical_css._extract_critical_css(soup)
        if not critical_css:
            return False

        if self.critical_css._inline_critical_css(soup, critical_css, file_path):
            self.critical_css._convert_css_to_preload(soup)
            self.critical_css.css_inlined += 1
            return True
        return False

    @staticmethod
    def _dedup_head_string(html):
        """String-level dedup of <link> tags and noscript in <head>."""
        from fix_duplicate_resource_hints import _clean_head

        head_match = re.search(
            r'(<head\b[^>]*>)(.*?)(</head>)',
            html,
            re.IGNORECASE | re.DOTALL,
        )
        if not head_match:
            return html

        cleaned, changed = _clean_head(head_match.group(2))
        if not changed:
            return html

        return (html[:head_match.start()] +
                head_match.group(1) + cleaned + head_match.group(3) +
                html[head_match.end():])

    def _print_summary(self, elapsed):
        """Print combined summary from all transform phases."""
        print(f"\n{'='*60}")
        print(f"🔄 SINGLE-PASS HTML TRANSFORMER SUMMARY")
        print(f"{'='*60}")
        print(f"📄 Files processed:     {self.files_processed}")
        print(f"✏️  Files modified:      {self.files_modified}")
        print(f"💾 Bytes saved:         {self.total_bytes_saved / 1024:.1f} KB")
        print(f"⏱️  Elapsed:            {elapsed:.1f}s")
        if self.files_processed > 0:
            print(f"⚡ Avg per file:        {elapsed / self.files_processed * 1000:.0f}ms")
        print()

        # Sub-summaries
        print(f"   SEO: {self.seo.issues_fixed} issues fixed in {self.seo.files_fixed} files")
        print(f"   Performance: {self.perf.optimizations_applied} optimizations applied")
        if not self.skip_images:
            print(f"   Pictures: {self.pictures.stats['images_converted']} converted, "
                  f"{self.pictures.stats['responsive_srcsets_added']} responsive srcsets")
        if not self.skip_critical_css:
            print(f"   Critical CSS: inlined in {self.critical_css.css_inlined} files")
        print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description='Single-pass HTML transformer — applies all optimizations in one cycle'
    )
    parser.add_argument(
        'directory',
        nargs='?',
        default='public',
        help='Directory containing HTML files (default: public)',
    )
    parser.add_argument(
        '--skip-images',
        action='store_true',
        help='Skip image-to-picture conversion (use if AVIF/WebP not yet generated)',
    )
    parser.add_argument(
        '--skip-critical-css',
        action='store_true',
        help='Skip critical CSS extraction and inlining',
    )
    args = parser.parse_args()

    transformer = HTMLTransformer(
        public_dir=args.directory,
        skip_images=args.skip_images,
        skip_critical_css=args.skip_critical_css,
    )
    transformer.process_all_files()

    return 0


if __name__ == '__main__':
    sys.exit(main())
