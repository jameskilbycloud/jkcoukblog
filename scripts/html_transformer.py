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

        # ── Phase 4.5: Inline tiny WP-shipped stylesheets ────────────────
        # Has to run on every page (not only WP-regenerated ones) so list
        # pages like the homepage get their rankmath.min.css inlined.
        if self._apply_inline_tiny_wp_stylesheets(soup):
            modified = True

        # ── Phase 4.7: Inline project stylesheets ────────────────────────
        # brutalist-theme.css and consolidated-inline-styles.min.css are
        # render-blocking on every page. Inline their contents directly so
        # FCP/LCP aren't gated on two extra round-trips. Brotli keeps the
        # extra HTML weight to ~10 KB on the wire. The font discovery happens
        # immediately because the @font-face declarations live inside
        # brutalist-theme.css.
        if self._apply_inline_project_stylesheets(soup):
            modified = True

        # ── Phase 4.8: Picture <source> srcset repair ────────────────────
        # Safety net for pictures whose AVIF/WebP <source> tags ended up
        # with single-file srcsets even though the wrapped <img> carries a
        # multi-resolution srcset. Re-derive the responsive srcset on a
        # late pass so the browser fetches the right-sized variant on
        # mobile instead of the full-res original.
        if not self.skip_images:
            if self._apply_picture_responsive_repair(soup):
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

        # 2a. Strip font preloads. A previous pipeline run injected
        #     <link rel="preload" as="font" fetchpriority="high"> for three
        #     WOFF2 weights — ~138 KB at high priority on mobile, competing
        #     with the LCP image. The inline critical CSS pins body to a
        #     system-font stack and fonts.css uses font-display: optional
        #     (fonts that arrive after the ~100 ms swap window are never
        #     rendered), so the preload pressure was pure cost. This strip
        #     keeps the cleanup idempotent for pages that aren't regenerated
        #     by wp_to_static_generator on this run.
        head_body = re.sub(
            r'<link\b[^>]*\bas=["\']font["\'][^>]*/?\s*>',
            '',
            head_body,
            flags=re.IGNORECASE,
        )

        # 2b. Revert preload-as-style back to stylesheet so critical CSS phase
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

    # Counters for the late-stage repair (Phase 4.8). We report these in the
    # final summary so it's obvious from the build log whether the safety net
    # actually had work to do — and how much.
    _picture_repair_sources_fixed = 0
    _picture_repair_files_touched = 0
    _picture_repair_missing_files = 0

    def _apply_picture_responsive_repair(self, soup):
        """Re-derive AVIF/WebP <source> srcsets from the wrapping <img>'s
        srcset for any <picture> still showing single-file sources. This
        duplicates _update_existing_picture_srcsets so it runs even if the
        upstream phase produced a picture without a responsive srcset.
        Records counters for build-log visibility.
        """
        if not soup.body:
            return False

        fixed = 0
        for picture in soup.find_all('picture'):
            img = picture.find('img')
            if img is None:
                continue
            img_srcset = (img.get('srcset') or '').strip()
            if ',' not in img_srcset:
                continue
            for source in picture.find_all('source'):
                srcset = (source.get('srcset') or '').strip()
                if ',' in srcset:
                    continue
                source_type = (source.get('type') or '').lower()
                if source_type == 'image/avif':
                    ext = '.avif'
                elif source_type == 'image/webp':
                    ext = '.webp'
                else:
                    continue
                new_srcset = self.pictures._get_responsive_srcset(img_srcset, ext)
                if new_srcset and ',' in new_srcset:
                    source['srcset'] = new_srcset
                    fixed += 1
                elif new_srcset is None:
                    # Function returned None — at least one variant missing
                    # on disk. Count so the summary surfaces it.
                    type(self)._picture_repair_missing_files += 1

        if fixed:
            type(self)._picture_repair_sources_fixed += fixed
            type(self)._picture_repair_files_touched += 1
        return fixed > 0

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

    # WP-shipped stylesheets that survive the generator pass: small ones get
    # inlined here so they don't cost a separate request. wp_to_static_generator
    # also has this logic but only fires when a page is regenerated from WP —
    # running it again here covers list pages (homepage, archives) that
    # incremental builds skip.
    _WP_INLINE_PATTERNS = (
        'wp-content/themes/kadence/assets/css/rankmath.min.css',
        'wp-content/themes/kadence/assets/css/footer.min.css',
        'wp-content/cache/wpo-minify/',
    )
    _WP_INLINE_MAX_BYTES = 2048

    def _apply_inline_tiny_wp_stylesheets(self, soup):
        """Inline small WordPress-shipped CSS links into <head> as <style>."""
        if not soup.head:
            return False

        inlined = 0
        for link in list(soup.find_all('link', rel='stylesheet')):
            if link.parent is None or link.attrs is None:
                continue
            raw_href = link.get('href') or ''
            href = raw_href.lstrip('/').split('?', 1)[0]
            if not any(p in href for p in self._WP_INLINE_PATTERNS):
                continue
            css_path = self.public_dir / href
            if not css_path.exists():
                continue
            try:
                content = css_path.read_text(encoding='utf-8').strip()
            except Exception:
                continue
            if len(content) > self._WP_INLINE_MAX_BYTES:
                continue

            style_tag = soup.new_tag('style')
            style_tag.string = content
            link.insert_before(style_tag)
            for companion in list(soup.find_all('link', href=raw_href)):
                companion.decompose()
            for noscript in list(soup.find_all('noscript')):
                if noscript.find('link', href=raw_href):
                    noscript.decompose()
            inlined += 1

        return inlined > 0

    # Project-owned stylesheets we inline directly into <head> as <style>
    # tags, trading a few KB of Brotli'd HTML weight for a saved round-trip.
    # brutalist-theme.css also carries the @font-face declarations so the
    # browser discovers font URLs during the initial HTML parse.
    _PROJECT_INLINE_STYLESHEETS = (
        '/assets/css/brutalist-theme.css',
    )

    # Stylesheets we strip from the page without inlining. Used to clean up
    # references to files we've stopped generating; on seeded pages the link
    # would otherwise survive across pipeline runs.
    _PROJECT_STRIP_STYLESHEETS = (
        '/assets/css/consolidated-inline-styles.min.css',
    )

    # <style> id stamped onto inlined content so future runs find and refresh
    # the same tag rather than appending a stale duplicate.
    _PROJECT_INLINE_STYLE_ID = {
        '/assets/css/brutalist-theme.css': 'inlined-brutalist-theme',
    }

    # Content prefixes for detecting previously-inlined <style> tags from
    # builds that predate the id markers. Match against the start of the
    # tag's text content.
    _PROJECT_INLINE_LEGACY_MARKERS = {
        '/assets/css/brutalist-theme.css': (
            '@font-face{font-family:"Anton"',
            '@import url(/assets/fonts/fonts.css)',
        ),
        '/assets/css/consolidated-inline-styles.min.css': (
            '/* /assets/css/inline-styles-',
            '/* /assets/css/wp-block-library-inline-css',
            '/* /assets/css/global-styles-inline-css',
        ),
    }

    def _apply_inline_project_stylesheets(self, soup):
        """Inline project CSS files into <head>; strip references to deprecated
        ones. Idempotent: re-runs refresh existing inline content (matched by
        id or legacy content marker) rather than appending duplicates.
        """
        if not soup.head:
            return False

        def _normalize(href):
            return (href or '').split('?', 1)[0].split('#', 1)[0]

        def _find_existing_inline(target):
            """Find a <style> tag in head that holds inlined content of target,
            via stamped id first or legacy content prefix as fallback.
            """
            style_id = self._PROJECT_INLINE_STYLE_ID.get(target)
            if style_id:
                tag = soup.find('style', id=style_id)
                if tag is not None and tag.parent is not None:
                    return tag
            markers = self._PROJECT_INLINE_LEGACY_MARKERS.get(target, ())
            for style in soup.head.find_all('style'):
                content = style.string or ''
                if any(content.startswith(m) for m in markers):
                    return style
            return None

        def _strip_link_artifacts(target):
            removed = 0
            for link in list(soup.head.find_all('link', rel='stylesheet')):
                if _normalize(link.get('href')) == target:
                    link.decompose()
                    removed += 1
            for preload in list(soup.head.find_all('link', rel='preload')):
                if _normalize(preload.get('href')) == target:
                    preload.decompose()
                    removed += 1
            for noscript in list(soup.head.find_all('noscript')):
                if noscript.find('link', href=lambda h: _normalize(h) == target):
                    noscript.decompose()
                    removed += 1
            return removed

        modified = 0

        for target in self._PROJECT_INLINE_STYLESHEETS:
            css_path = self.public_dir / target.lstrip('/')
            if not css_path.exists():
                continue
            try:
                content = css_path.read_text(encoding='utf-8').strip()
            except Exception:
                continue
            if not content:
                continue

            style_id = self._PROJECT_INLINE_STYLE_ID.get(target)
            existing = _find_existing_inline(target)

            if existing is not None:
                # Refresh content and stamp the id for next time.
                existing.string = content
                if style_id:
                    existing['id'] = style_id
                modified += 1
            else:
                link = next(
                    (l for l in soup.head.find_all('link', rel='stylesheet')
                     if _normalize(l.get('href')) == target),
                    None,
                )
                if link is None:
                    continue
                style_tag = soup.new_tag('style')
                if style_id:
                    style_tag['id'] = style_id
                style_tag.string = content
                link.insert_before(style_tag)
                modified += 1

            _strip_link_artifacts(target)

        for target in self._PROJECT_STRIP_STYLESHEETS:
            modified += _strip_link_artifacts(target)
            existing = _find_existing_inline(target)
            if existing is not None:
                existing.decompose()
                modified += 1

        return modified > 0

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
            print(f"   Picture repair: {type(self)._picture_repair_sources_fixed} "
                  f"<source> srcsets fixed across "
                  f"{type(self)._picture_repair_files_touched} files "
                  f"({type(self)._picture_repair_missing_files} skipped — "
                  f"missing AVIF/WebP variant on disk)")
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
