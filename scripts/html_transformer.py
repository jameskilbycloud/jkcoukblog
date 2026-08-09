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

import os
import sys
import re
import time
import argparse
import collections
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup

# Ensure scripts/ is on the path for imports
sys.path.insert(0, str(Path(__file__).parent))

from fix_seo_issues import SEOFixer
from enhance_html_performance import HTMLPerformanceEnhancer, normalize_self_href
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

        # Per-branch accounting for _apply_inline_tiny_wp_stylesheets. That
        # pass silently no-opped across a whole production build once (no
        # exception, all files "modified", nothing inlined), which was not
        # diagnosable from the logs. Every skip reason is counted, and the
        # first offending path is kept so the build log names it.
        self.wp_inline_stats = collections.defaultdict(int)
        self.wp_inline_stats['over_cap_files'] = {}

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
        self._write_github_output()

    def _write_github_output(self):
        """Expose the inlining counters to the workflow so Slack can report
        them. `skip_not_on_disk` is the number that mattered: it read 1442 on
        the 2026-08-08 build while the log otherwise looked like a clean
        success, and nothing surfaced it outside the raw job output."""
        out = os.environ.get('GITHUB_OUTPUT')
        if not out:
            return
        s = self.wp_inline_stats
        try:
            with open(out, 'a', encoding='utf-8') as fh:
                fh.write(f"css_inlined={s['inlined']}\n")
                fh.write(f"css_inlined_kb={s['inlined_bytes'] // 1024}\n")
                fh.write(f"css_dropped_empty={s['dropped_empty']}\n")
                fh.write(f"css_skip_missing={s['skip_not_on_disk']}\n")
        except OSError as e:
            print(f"⚠️  Could not write GITHUB_OUTPUT: {e}")

    # Pre-compiled at class load so the per-file strip avoids re-parsing.
    # Kadence emits this inline `<script>` once per page — usually right
    # after `<body>`, NOT in `<head>` — so the `_deep_clean_head` pass
    # never sees it. Stripping it from the raw HTML before the head pass
    # catches it wherever it lives. The body of the script is constrained
    # to `[^<]*` so the match can't accidentally swallow neighbour tags.
    _SCROLLBAR_OFFSET_SCRIPT_RE = re.compile(
        r"<script\b[^>]*>[^<]*--scrollbar-offset[^<]*</script>",
        re.IGNORECASE,
    )

    def _process_file(self, file_path):
        """Apply all transforms to a single HTML file in one parse cycle."""
        original_html = file_path.read_text(encoding='utf-8')
        original_size = len(original_html.encode('utf-8'))

        # ── Phase 0a: Strip the Kadence scrollbar-offset script ─────────
        # window.innerWidth and document.documentElement.clientWidth both
        # force layout during early page parse — Lighthouse flagged this
        # as a 70 ms forced reflow on the homepage (June 2026 PSI). The
        # script sits in <body> (line 6 of the live homepage), not <head>,
        # so the `_deep_clean_head` pass missed it; run a whole-document
        # strip here instead. Kadence's CSS uses `var(--scrollbar-offset,
        # 0)` so the default of 0 is safe — only side effect is that on
        # Windows (15–17 px vertical scrollbar) sticky-header alignment
        # may be off when a drawer modal opens. macOS/iOS overlay
        # scrollbars are already 0.
        original_html = self._SCROLLBAR_OFFSET_SCRIPT_RE.sub('', original_html)

        # ── Phase 0b: Aggressive string-level cleanup ───────────────────
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

        # ── Phase 4.7.5: Re-derive font preloads from freshly inlined CSS ──
        # Phase 3 ran optimize_fonts before the project stylesheets were
        # inlined, so it may have keyed off stale @font-face values left in
        # the input HTML by an earlier pipeline run (e.g. all `optional`
        # before the optional→swap split). Re-run after inlining so the
        # preload set reflects the current CSS source of truth.
        if self.perf.optimize_fonts(soup):
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

        # (Kadence's `--scrollbar-offset` script is stripped by
        # `_process_file` BEFORE this method runs — it lives in <body>
        # on every page, not in <head>, so head-scoped substitution
        # could never catch it. See _SCROLLBAR_OFFSET_SCRIPT_RE.)

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

        # 3. Deduplicate <link> tags by href. Keys are normalised so an
        # absolute same-site href and its relative form count as the same
        # resource — exact-string keys let e.g. a relative and an
        # absolutified copy of the same LCP preload both survive.
        seen_hrefs = set()

        def _dedup(m):
            tag = m.group(0)
            href_m = re.search(r'\bhref=["\']([^"\']+)["\']', tag, re.IGNORECASE)
            if not href_m:
                return tag
            href = normalize_self_href(href_m.group(1))
            if href in seen_hrefs:
                return ''
            seen_hrefs.add(href)
            return tag

        head_body = re.sub(r'<link\b[^>]*/?\s*>', _dedup, head_body, flags=re.IGNORECASE)

        # 4. Collapse blank lines
        head_body = re.sub(r'\n{3,}', '\n\n', head_body)

        return html[:head_match.start()] + head_open + head_body + head_close + html[head_match.end():]

    def _apply_seo_fixes(self, soup, file_path):
        """Apply all SEO transforms from SEOFixer on the soup object.

        Mirrors SEOFixer.process_file's call order. When you add a fix method
        to SEOFixer, you MUST also add it here — this orchestrator bypasses
        process_file (which reads/writes the file itself) and drives the
        SEOFixer methods on an already-parsed soup.
        """
        modified = False
        if self.seo.fix_title_length(soup, file_path):
            modified = True
        if self.seo.fix_homepage_title(soup, file_path):
            modified = True
        if self.seo.fix_homepage_h1(soup, file_path):
            modified = True
        if self.seo.fix_title_drop_brand_suffix(soup, file_path):
            modified = True
        if self.seo.fix_thin_archive_noindex(soup, file_path):
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
        if self.seo.fix_dedupe_breadcrumblist(soup, file_path):
            modified = True
        if self.seo.fix_techarticle_dedupe_and_dates(soup, file_path):
            modified = True
        if self.seo.fix_jsonld_headline_brand_suffix(soup, file_path):
            modified = True
        if self.seo.fix_article_entity_links(soup, file_path):
            modified = True
        if self.seo.fix_person_name(soup, file_path):
            modified = True
        if self.seo.fix_person_enrichment(soup, file_path):
            modified = True
        if self.seo.fix_organization_sameas(soup, file_path):
            modified = True
        if self.seo.fix_og_site_name(soup, file_path):
            modified = True
        if self.seo.fix_twitter_attribution(soup, file_path):
            modified = True
        if self.seo.fix_wordpress_host_leak(soup, file_path):
            modified = True
        if self.seo.fix_og_meta_alignment(soup, file_path):
            modified = True
        if self.seo.fix_malformed_stylesheet_attr(soup, file_path):
            modified = True
        return modified

    # Counters for the late-stage repair (Phase 4.8). We report these in the
    # final summary so it's obvious from the build log whether the safety net
    # actually had work to do — and how much.
    _picture_repair_sources_fixed = 0
    _picture_repair_files_touched = 0
    _picture_repair_missing_files = 0
    _picture_repair_partial = 0  # got 1 variant, expected ≥2
    _picture_repair_missing_samples = []  # first few paths we couldn't find

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
                    type(self)._picture_repair_missing_files += 1
                    # Record the first few paths we expected to find so the
                    # build log shows what's actually missing in CI.
                    if len(type(self)._picture_repair_missing_samples) < 6:
                        for part in img_srcset.split(','):
                            comps = part.strip().split()
                            if len(comps) >= 2:
                                expected = (self.pictures.directory /
                                            comps[0].lstrip('/')).with_suffix(ext)
                                if not expected.exists():
                                    type(self)._picture_repair_missing_samples.append(
                                        str(expected)
                                    )
                                    if len(type(self)._picture_repair_missing_samples) >= 6:
                                        break
                else:
                    # Single entry returned (no comma) — only one variant
                    # exists on disk. Count separately so we can tell whether
                    # the issue is "no variants at all" vs "only one variant".
                    type(self)._picture_repair_partial += 1

        if fixed:
            type(self)._picture_repair_sources_fixed += fixed
            type(self)._picture_repair_files_touched += 1
        return fixed > 0

    def _apply_picture_conversion(self, soup):
        """Convert img tags to picture elements using ImageToPictureConverter methods."""
        modified = False

        # Inject EXTRA_WIDTHS (e.g. 480w) into every <img>'s srcset first.
        # Both downstream paths — _update_existing_picture_srcsets and the
        # standalone img → picture conversion loop below — derive AVIF/WebP
        # <source> srcsets from img.srcset, so enriching the img.srcset once
        # here ensures the extra width propagates to every modern source.
        # See convert_images_to_picture._inject_extra_widths_into_img_srcset.
        for img in soup.find_all('img'):
            if self.pictures._inject_extra_widths_into_img_srcset(img):
                modified = True

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
        if self.perf.strip_http_equiv_meta(soup):
            modified = True
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

        modified = False
        if critical_css and self.critical_css._inline_critical_css(
                soup, critical_css, file_path):
            self.critical_css.css_inlined += 1
            modified = True

        # Convert stylesheets to async preload even when nothing was inlined
        # — a page whose async-eligible sheets match no critical selectors
        # must still not ship them render-blocking. The old early-return on
        # empty critical_css left such pages render-blocking forever and
        # stopped the noscript self-healing from persisting.
        if self.critical_css._convert_css_to_preload(soup):
            modified = True

        return modified

    # WP-shipped stylesheets that survive the generator pass: small ones get
    # inlined here so they don't cost a separate request. wp_to_static_generator
    # also has this logic but only fires when a page is regenerated from WP —
    # running it again here covers list pages (homepage, archives) that
    # incremental builds skip.
    #
    # Patterns are broad (whole plugin/theme trees) rather than a list of
    # specific files because WP-Optimize minify is disabled: WordPress now
    # emits each plugin's and theme's stylesheet individually instead of one
    # concatenated wpo-minify bundle. The old three-entry allowlist matched
    # only the bundle and two named Kadence files, so none of the unbundled
    # plugin CSS would ever be considered. The wpo-minify entry is kept so
    # re-enabling the plugin (or replaying an older build) still works.
    # '-inline-css-' catches the pipeline's OWN extracted files under
    # /assets/css/. wp_to_static_generator.extract_inline_css lifts WordPress's
    # inline <style> blocks out to disk; WP-Optimize used to absorb those into
    # its bundle, so with minify off they surface as extra requests on 170
    # pages (kadence-global-inline-css 11450 B, wp-emoji-styles-inline-css
    # 340 B). Putting them back as <style> restores the form WordPress emitted
    # in the first place, so it is cascade-neutral. Matching on the filename
    # convention rather than the whole /assets/css/ directory keeps
    # brutalist-theme.css out of it — that one is handled separately by
    # _PROJECT_INLINE_STYLESHEETS at Phase 4.7.
    _WP_INLINE_PATTERNS = (
        'wp-content/plugins/',
        'wp-content/themes/',
        'wp-content/cache/wpo-minify/',
        '-inline-css-',
    )

    # Per-file ceiling, raised from 2048 when WP-Optimize minify was disabled.
    #
    # Sized from a 51-URL sweep of the live CMS covering every page type
    # (homepage, posts, category/tag archives, pagination, static pages).
    # Stylesheets per page: 5 on archives and the homepage, 7 on a typical
    # post, 9 worst case (a post with comments plus a Rank Math TOC block).
    #
    # Sizes below are *after* optimize_css.py's unused-selector pass, which is
    # what this pass actually sees — the raw files are 2-3x larger:
    #
    #     content.min.css         19136
    #     footer.min.css          16586
    #     header.min.css          13680
    #     global.min.css           9601   ← on every page
    #     kadence-splide.min.css    1699
    #     comments.min.css         1025
    #     related-posts.min.css     883
    #     toc_list_style.css         212   ← the one plugin stylesheet
    #     rankmath.min.css             0   (fully purged → dropped, not inlined)
    #
    # Plus the pipeline's OWN extracted inline CSS, which the sizing above
    # missed because it only modelled what the CMS emits. These are on 170
    # pages and were previously absorbed by the wpo-minify bundle:
    #
    #     kadence-global-inline-css-*.min.css   11450
    #     wp-emoji-styles-inline-css-*.min.css    340
    #
    # 12288 clears kadence-global-inline-css, the largest file worth inlining.
    # The three above it — content, footer, header — stay linked deliberately;
    # inlining ~49 KB into every page would blow the document budget for no
    # LCP gain. That leaves 3 linked stylesheets against the Lighthouse
    # `stylesheet: 5` resourceCounts budget in .github/lighthouse/budget.json.
    #
    # If a future selector corpus pushes a file back over the cap it simply
    # stays linked, so this degrades gracefully rather than breaking.
    _WP_INLINE_MAX_BYTES = 12288

    # Page-level ceiling on total inlined bytes. Inlined CSS is duplicated
    # into every HTML page and counts against the `document: 30` (KB,
    # transfer) budget.
    #
    # Worst case with the caps above is a post page carrying every optional
    # stylesheet: global 9601 + kadence-global-inline 11450 + splide 1699 +
    # comments 1025 + related-posts 883 + emoji 340 + toc 212 = 25,210 B,
    # which is why this is 32768 rather than the earlier 24576. Pages brotli
    # to ~15 KB today; ~32 KB of extra raw CSS adds roughly 7-8 KB on the
    # wire, landing near 23 KB against the 30 KB document budget.
    #
    # The cap also bounds a deliberate trade-off: critical CSS made these
    # links async (non-render-blocking), and inlining makes them render-
    # blocking again. Removing the round-trip is worth more than the parse
    # cost at these sizes — the same reasoning as _apply_inline_project_
    # stylesheets below — but only while the total stays small.
    _WP_INLINE_TOTAL_MAX_BYTES = 32768

    @staticmethod
    def _is_inlinable_css_link(link):
        """True for both forms a stylesheet reaches this pass in.

        Phase 4 (critical CSS) runs first and rewrites render-blocking
        stylesheets into the async pattern
        `rel="preload" as="style" onload="...this.rel='stylesheet'"`, leaving a
        plain `<link rel="stylesheet">` behind only inside the <noscript>
        fallback. Matching `rel="stylesheet"` alone therefore only ever found
        the noscript copy, so the real request was never eliminated and this
        whole pass was close to a no-op on any page that had critical CSS
        extracted (i.e. all of them).
        """
        rel = link.get('rel') or []
        if isinstance(rel, str):
            rel = rel.split()
        rel = {r.lower() for r in rel}
        if 'stylesheet' in rel:
            return True
        return 'preload' in rel and (link.get('as') or '').lower() == 'style'

    def _apply_inline_tiny_wp_stylesheets(self, soup):
        """Inline small WordPress-shipped CSS links into <head> as <style>."""
        if not soup.head:
            return False

        # Pass 1 — collect eligible links and their content, deduped by href.
        # The same stylesheet appears twice once critical CSS has run (the
        # preload and its noscript fallback); inlining it twice would double
        # the bytes and spend the page budget on a duplicate.
        candidates = []
        seen_hrefs = set()
        dropped_empty = 0
        stats = self.wp_inline_stats
        for link in list(soup.find_all('link')):
            if link.parent is None or link.attrs is None:
                continue
            if not self._is_inlinable_css_link(link):
                continue
            raw_href = link.get('href') or ''
            # Absolute same-site URLs must be mapped back to site-relative
            # BEFORE the disk lookup. During a build the hrefs are absolute
            # (`https://jameskilby.co.uk/wp-content/...`) because
            # convert_to_staging.py doesn't rewrite them to relative until the
            # much later "Prepare output for deployment" step. lstrip('/')
            # doesn't touch a scheme, so `public_dir / href` produced
            # `static-output/https:/jameskilby.co.uk/wp-content/...`, which
            # never exists — the pass skipped 1442 links and inlined nothing
            # on the 2026-08-08 build while looking like a success.
            href = normalize_self_href(raw_href).lstrip('/').split('?', 1)[0]
            if href in seen_hrefs:
                continue
            stats['css_links_seen'] += 1
            if not any(p in href for p in self._WP_INLINE_PATTERNS):
                stats['skip_no_pattern_match'] += 1
                stats.setdefault('sample_unmatched', href)
                continue
            stats['pattern_matched'] += 1
            # Claim the href now, before any skip branch. Every <link> for it
            # is handled by this iteration one way or another (inlined and
            # dropped, or deliberately left linked), so a later duplicate —
            # the noscript fallback — must not be reconsidered or re-counted.
            seen_hrefs.add(href)
            css_path = self.public_dir / href
            if not css_path.exists():
                # The branch that silently swallowed everything on the
                # 2026-08-08 deploy: the pass ran on all 255 files, threw no
                # exception, and inlined nothing. Record the resolved path so
                # a build log shows exactly where it looked.
                stats['skip_not_on_disk'] += 1
                stats.setdefault('sample_missing', str(css_path.resolve()))
                continue
            try:
                content = css_path.read_text(encoding='utf-8').strip()
            except Exception as e:
                stats['skip_read_error'] += 1
                stats.setdefault('sample_read_error', f"{css_path}: {e}")
                continue
            # An empty file still costs a request, so drop the link — but
            # there's nothing to inline, and BeautifulSoup won't render an
            # empty <style> reliably.
            if not content:
                self._drop_stylesheet_refs(soup, raw_href)
                dropped_empty += 1
                continue
            size = len(content.encode('utf-8'))
            if size > self._WP_INLINE_MAX_BYTES:
                stats['skip_over_file_cap'] += 1
                stats['over_cap_files'][css_path.name] = size
                continue
            candidates.append((size, link, raw_href, content))

        # Pass 2 — spend the page budget smallest-first, which maximises the
        # number of requests eliminated per byte of HTML added. Selection
        # order only decides *which* files are inlined; each <style> is still
        # inserted at its own <link>'s position below, so the cascade order of
        # the original document is preserved.
        chosen = []
        spent = 0
        for size, link, raw_href, content in sorted(candidates, key=lambda c: c[0]):
            if spent + size > self._WP_INLINE_TOTAL_MAX_BYTES:
                stats['skip_over_page_budget'] += 1
                continue
            spent += size
            chosen.append((link, raw_href, content))

        # Pass 3 — apply, in document order.
        inlined = 0
        for link, raw_href, content in chosen:
            if link.parent is None:
                continue  # already removed as a companion of an earlier href
            style_tag = soup.new_tag('style')
            style_tag.string = content
            link.insert_before(style_tag)
            self._drop_stylesheet_refs(soup, raw_href)
            inlined += 1

        stats['inlined'] += inlined
        stats['inlined_bytes'] += spent
        stats['dropped_empty'] += dropped_empty
        return (inlined + dropped_empty) > 0

    @staticmethod
    def _drop_stylesheet_refs(soup, raw_href):
        """Remove every reference to a stylesheet: the preload/stylesheet link
        itself and the <noscript> fallback that would otherwise re-request it.

        Matching is on the normalised href, not the literal string: a page can
        carry the same file as an absolute preload and a relative noscript
        fallback (pipeline stages absolutify at different points), and an exact
        match would drop one and leave the other still fetching.

        Order matters — the noscript wrapper has to go first. Decomposing the
        links first empties the noscript, so the "does this noscript contain
        the link?" test then finds nothing and leaves an empty <noscript>
        behind on every page."""
        target = normalize_self_href(raw_href).split('?', 1)[0]

        def _matches(tag):
            return normalize_self_href(tag.get('href') or '').split('?', 1)[0] == target

        for noscript in list(soup.find_all('noscript')):
            if any(_matches(link) for link in noscript.find_all('link', href=True)):
                noscript.decompose()
        for companion in list(soup.find_all('link', href=True)):
            if _matches(companion):
                companion.decompose()

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
        print("🔄 SINGLE-PASS HTML TRANSFORMER SUMMARY")
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
                  f"{type(self)._picture_repair_files_touched} files; "
                  f"{type(self)._picture_repair_missing_files} none-on-disk, "
                  f"{type(self)._picture_repair_partial} only-one-variant")
            if type(self)._picture_repair_missing_samples:
                print(f"   Sample missing paths (first {len(type(self)._picture_repair_missing_samples)}):")
                for p in type(self)._picture_repair_missing_samples:
                    print(f"     - {p}")
        if not self.skip_critical_css:
            cc = self.critical_css
            print(f"   Critical CSS: inlined in {cc.css_inlined} files")
            # Saturation is the number that matters: it says above-fold rules
            # are being discarded, which the per-page warnings couldn't convey
            # when they fired 252 times.
            if cc.css_truncated:
                print(f"      ⚠️  {cc.css_truncated}/{cc.css_inlined} pages hit the "
                      f"{cc.max_critical_css}B cap — dropped "
                      f"{cc.css_dropped_rules} rules, {cc.css_dropped_bytes / 1024:.1f} KB total")
                if cc.sample_truncated:
                    print(f"          sample: {cc.sample_truncated}")
        self._print_wp_inline_summary()
        print(f"{'='*60}")

    def _print_wp_inline_summary(self):
        """Report what the WP-stylesheet inlining pass actually did.

        Printed unconditionally, including the zero case — a silent no-op here
        is the failure mode that shipped 172 over-budget pages once already,
        and it looked identical to success in the build log.
        """
        s = self.wp_inline_stats
        print(f"   WP stylesheet inlining: {s['inlined']} inlined "
              f"({s['inlined_bytes'] / 1024:.1f} KB), "
              f"{s['dropped_empty']} empty dropped, "
              f"{s['css_links_seen']} candidate links seen")

        if s['css_links_seen'] and not s['pattern_matched']:
            print(f"      ⚠️  no link matched _WP_INLINE_PATTERNS "
                  f"(sample href: {s.get('sample_unmatched')})")
        if s['skip_not_on_disk']:
            print(f"      ⚠️  {s['skip_not_on_disk']} skipped — file not on disk")
            print(f"          looked for: {s.get('sample_missing')}")
            print(f"          public_dir: {self.public_dir.resolve()}")
        if s['skip_read_error']:
            print(f"      ⚠️  {s['skip_read_error']} skipped — unreadable "
                  f"({s.get('sample_read_error')})")
        if s['skip_over_page_budget']:
            print(f"      ℹ️  {s['skip_over_page_budget']} skipped — page budget "
                  f"({self._WP_INLINE_TOTAL_MAX_BYTES} B) exhausted")
        if s['over_cap_files']:
            over = ", ".join(f"{n} {b}B" for n, b in
                             sorted(s['over_cap_files'].items(),
                                    key=lambda kv: -kv[1])[:6])
            print(f"      ℹ️  left linked, over {self._WP_INLINE_MAX_BYTES} B cap: {over}")
        if not s['css_links_seen']:
            print("      ⚠️  pass saw zero candidate <link> tags — check phase order")


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
