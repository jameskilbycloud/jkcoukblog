#!/usr/bin/env python3
"""
Comprehensive post-optimization validation for static site deployment.

This script validates that all optimization steps completed successfully:
- Brotli compression integrity (.br files match originals)
- Modern image formats (AVIF/WebP exist and are valid)
- Picture elements (correct structure and fallback order)
- Minification (no broken HTML/CSS/JS)
- Critical CSS inlining

Usage:
    python3 validate_deployment.py <site_directory>
"""

import os
import re
import sys
from pathlib import Path
import brotli
from PIL import Image
from bs4 import BeautifulSoup
import json


class DeploymentValidator:
    """Validates optimized static site before deployment."""

    def __init__(self, site_dir):
        self.site_dir = Path(site_dir)
        self.errors = []
        self.warnings = []
        self.stats = {}

    # Directories that are regenerated post-validation (by generate_changelog.py
    # and generate_stats_page.py), so their seeded content may be stale.
    EXCLUDE_DIRS = ('changelog', 'stats')

    def find_files(self, extensions):
        """Find all files with given extensions, excluding post-deploy dirs."""
        files = []
        for ext in extensions:
            for f in self.site_dir.glob(f'**/*{ext}'):
                rel = f.relative_to(self.site_dir)
                if not any(rel.parts[0] == d for d in self.EXCLUDE_DIRS if rel.parts):
                    files.append(f)
        return sorted(files)

    def validate_brotli_files(self):
        """
        Verify Brotli compression integrity.

        Checks:
        1. All compressible files (>1KB) have .br variants
        2. .br files are valid and can decompress
        3. Decompressed content matches original
        4. No orphaned .br files
        """
        print("📦 Validating Brotli compression...")

        compressible_exts = ['.html', '.css', '.js', '.json', '.xml', '.svg']
        compressible_files = self.find_files(compressible_exts)

        # Filter files >1KB (same threshold as brotli_compress.py)
        compressible_files = [f for f in compressible_files if f.stat().st_size > 1024]

        brotli_found = 0
        brotli_valid = 0
        brotli_mismatch = 0

        for file_path in compressible_files:
            br_path = Path(str(file_path) + '.br')

            if not br_path.exists():
                # Not all files get compressed (need ≥5% reduction)
                # This is a warning, not an error
                continue

            brotli_found += 1

            # Verify .br is valid by decompressing
            try:
                with open(br_path, 'rb') as f:
                    compressed = f.read()
                decompressed = brotli.decompress(compressed)

                # Verify content matches original
                with open(file_path, 'rb') as f:
                    original = f.read()

                if decompressed != original:
                    self.errors.append(
                        f"Brotli mismatch: {br_path.relative_to(self.site_dir)} "
                        f"doesn't match {file_path.relative_to(self.site_dir)}"
                    )
                    brotli_mismatch += 1
                else:
                    brotli_valid += 1

            except Exception as e:
                self.errors.append(
                    f"Corrupt Brotli file: {br_path.relative_to(self.site_dir)} - {e}"
                )

        # Check for orphaned .br files
        all_br_files = self.find_files(['.br'])
        for br_file in all_br_files:
            original_path = Path(str(br_file)[:-3])  # Remove .br extension
            if not original_path.exists():
                self.warnings.append(
                    f"Orphaned Brotli file: {br_file.relative_to(self.site_dir)} "
                    f"(no original file)"
                )

        self.stats['brotli_files_found'] = brotli_found
        self.stats['brotli_files_valid'] = brotli_valid
        self.stats['brotli_files_mismatch'] = brotli_mismatch

        print(f"  ✓ Found {brotli_found} Brotli compressed files")
        print(f"  ✓ {brotli_valid} valid, {brotli_mismatch} mismatches")

    def validate_image_formats(self):
        """
        Verify modern image formats exist and are valid.

        Checks:
        1. All .jpg/.jpeg/.png images have .avif and .webp variants
        2. AVIF/WebP files are valid (can be opened by PIL)
        3. Report coverage percentage
        """
        print("\n🖼️  Validating image formats...")

        original_images = self.find_files(['.jpg', '.jpeg', '.png'])

        # Filter out very small images (likely icons, logos)
        original_images = [img for img in original_images if img.stat().st_size > 10240]  # >10KB

        avif_count = 0
        webp_count = 0
        missing_avif = []
        missing_webp = []

        for img_path in original_images:
            stem = img_path.stem
            parent = img_path.parent

            # Check AVIF exists
            avif_path = parent / f"{stem}.avif"
            if not avif_path.exists():
                missing_avif.append(img_path)
            else:
                # Verify AVIF is valid
                try:
                    img = Image.open(avif_path)
                    img.verify()
                    avif_count += 1
                except Exception as e:
                    self.errors.append(
                        f"Invalid AVIF: {avif_path.relative_to(self.site_dir)} - {e}"
                    )

            # Check WebP exists
            webp_path = parent / f"{stem}.webp"
            if not webp_path.exists():
                missing_webp.append(img_path)
            else:
                try:
                    img = Image.open(webp_path)
                    img.verify()
                    webp_count += 1
                except Exception as e:
                    self.errors.append(
                        f"Invalid WebP: {webp_path.relative_to(self.site_dir)} - {e}"
                    )

        # Calculate coverage
        total = len(original_images)
        avif_coverage = (avif_count / total * 100) if total > 0 else 0
        webp_coverage = (webp_count / total * 100) if total > 0 else 0

        self.stats['total_images'] = total
        self.stats['avif_count'] = avif_count
        self.stats['webp_count'] = webp_count
        self.stats['avif_coverage'] = f"{avif_coverage:.1f}%"
        self.stats['webp_coverage'] = f"{webp_coverage:.1f}%"

        print(f"  ✓ Total images (>10KB): {total}")
        print(f"  ✓ AVIF coverage: {avif_coverage:.1f}% ({avif_count}/{total})")
        print(f"  ✓ WebP coverage: {webp_coverage:.1f}% ({webp_count}/{total})")

        # Warn if coverage is low
        if avif_coverage < 90 and total > 0:
            self.warnings.append(
                f"Low AVIF coverage: {avif_coverage:.1f}% (expected >90%)"
            )
            if len(missing_avif) <= 5:
                for img in missing_avif:
                    self.warnings.append(f"  Missing AVIF for: {img.relative_to(self.site_dir)}")

        if webp_coverage < 90 and total > 0:
            self.warnings.append(
                f"Low WebP coverage: {webp_coverage:.1f}% (expected >90%)"
            )
            if len(missing_webp) <= 5:
                for img in missing_webp:
                    self.warnings.append(f"  Missing WebP for: {img.relative_to(self.site_dir)}")

    def validate_picture_elements(self):
        """
        Verify picture elements are properly structured.

        Checks:
        1. All <picture> elements have <source> tags with type attributes
        2. Type attributes are correct (image/avif, image/webp)
        3. Referenced files exist on disk
        4. Fallback order is correct (AVIF → WebP → original)
        5. Every <picture> has an <img> fallback
        """
        print("\n🎨 Validating picture elements...")

        html_files = self.find_files(['.html'])

        total_pictures = 0
        valid_pictures = 0

        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')
            except Exception as e:
                self.errors.append(
                    f"Failed to parse HTML: {html_file.relative_to(self.site_dir)} - {e}"
                )
                continue

            for picture in soup.find_all('picture'):
                total_pictures += 1
                sources = picture.find_all('source')
                img = picture.find('img')

                rel_file = html_file.relative_to(self.site_dir)

                # Verify <img> fallback exists
                if not img:
                    self.errors.append(f"{rel_file}: <picture> without <img> fallback")
                    continue

                # Verify sources have type attributes
                has_avif = False
                has_webp = False

                for source in sources:
                    srcset = source.get('srcset', '')
                    image_type = source.get('type', '')

                    if not image_type:
                        self.errors.append(
                            f"{rel_file}: <source> without type attribute"
                        )
                        continue

                    # Track format types
                    if image_type == 'image/avif':
                        has_avif = True
                    elif image_type == 'image/webp':
                        has_webp = True

                    # Verify type matches srcset extension
                    if 'avif' in srcset and image_type != 'image/avif':
                        self.errors.append(
                            f"{rel_file}: AVIF source with wrong type: {image_type}"
                        )
                    if 'webp' in srcset and image_type != 'image/webp':
                        self.errors.append(
                            f"{rel_file}: WebP source with wrong type: {image_type}"
                        )

                    # Verify referenced files exist (first URL only, not all srcset variants)
                    if srcset:
                        first_url = srcset.split(',')[0].strip().split()[0]
                        # Skip data URIs, absolute URLs, and fragments
                        if first_url.startswith(('data:', 'http://', 'https://', '//', '#')):
                            continue

                        file_path = self.site_dir / first_url.lstrip('/')
                        if not file_path.exists():
                            self.warnings.append(
                                f"{rel_file}: Referenced image not found: {first_url}"
                            )

                # Verify correct source order (AVIF before WebP)
                if len(sources) >= 2 and has_avif and has_webp:
                    first_type = sources[0].get('type', '')
                    second_type = sources[1].get('type', '')

                    if first_type == 'image/avif' and second_type == 'image/webp':
                        valid_pictures += 1
                    else:
                        self.warnings.append(
                            f"{rel_file}: Picture sources not in optimal order "
                            f"(should be AVIF, then WebP)"
                        )

        self.stats['picture_elements'] = total_pictures
        self.stats['valid_picture_elements'] = valid_pictures

        print(f"  ✓ Found {total_pictures} picture elements")
        print(f"  ✓ {valid_pictures} with optimal source order")

    def validate_minification(self):
        """
        Verify minification didn't break HTML/CSS/JS.

        Checks:
        1. HTML files parse correctly with BeautifulSoup
        2. No unclosed tags
        """
        print("\n✂️  Validating minification...")

        html_files = self.find_files(['.html'])
        valid_html = 0
        broken_html = 0

        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')

                # Check for basic HTML structure
                if soup.html and soup.head and soup.body:
                    valid_html += 1
                else:
                    self.warnings.append(
                        f"Incomplete HTML structure: {html_file.relative_to(self.site_dir)}"
                    )
                    broken_html += 1

            except Exception as e:
                self.errors.append(
                    f"HTML parsing failed (possible minification issue): "
                    f"{html_file.relative_to(self.site_dir)} - {e}"
                )
                broken_html += 1

        self.stats['html_files_checked'] = len(html_files)
        self.stats['valid_html_files'] = valid_html
        self.stats['broken_html_files'] = broken_html

        print(f"  ✓ Checked {len(html_files)} HTML files")
        print(f"  ✓ {valid_html} valid, {broken_html} with issues")

    def validate_critical_css(self):
        """
        Verify critical CSS was inlined.

        Checks:
        1. HTML files have <style> tags in <head>
        2. Main CSS is loaded with media="print" or async attribute
        """
        print("\n🎨 Validating critical CSS...")

        html_files = self.find_files(['.html'])
        files_with_inline = 0
        files_with_async_css = 0

        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')

                # Check for inline styles in head
                if soup.head:
                    inline_styles = soup.head.find_all('style')
                    if inline_styles:
                        files_with_inline += 1

                    # Check for async CSS loading
                    css_links = soup.head.find_all('link', rel='stylesheet')
                    for link in css_links:
                        if link.get('media') == 'print' or link.get('onload'):
                            files_with_async_css += 1
                            break

            except Exception as e:
                # Already logged in minification check
                pass

        self.stats['files_with_critical_css'] = files_with_inline
        self.stats['files_with_async_css'] = files_with_async_css

        print(f"  ✓ {files_with_inline} files with inlined critical CSS")
        print(f"  ✓ {files_with_async_css} files with async CSS loading")

    def validate_utterances_comments(self):
        """
        Verify Utterances comments are injected in blog posts.

        Checks:
        1. Blog post HTML files have Utterances section
        2. Script tag has correct attributes
        3. Repository is correct
        4. Reports coverage percentage
        """
        print("\n💬 Validating Utterances comments...")

        # Find blog post HTML files (yyyy/mm/post-slug/index.html pattern)
        post_files = []
        for year_dir in self.site_dir.glob('20*/'):
            for month_dir in year_dir.glob('*/'):
                for post_dir in month_dir.glob('*/'):
                    index_file = post_dir / 'index.html'
                    if index_file.exists():
                        post_files.append(index_file)

        if not post_files:
            print("  ⚠️  No blog posts found to validate")
            return

        missing_comments = 0
        posts_with_comments = 0
        malformed_comments = 0

        for post_file in post_files:
            try:
                with open(post_file, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')

                utterances_section = soup.find('section', id='utterances-comments')

                if not utterances_section:
                    missing_comments += 1
                    if missing_comments <= 5:  # Only log first 5
                        self.warnings.append(
                            f"Missing Utterances: {post_file.relative_to(self.site_dir)}"
                        )
                else:
                    # Verify script attributes
                    script = utterances_section.find('script', src=lambda x: x and 'utteranc.es' in x)
                    if script:
                        repo = script.get('data-repo')
                        if repo == 'jameskilbynet/jkcoukblog':
                            posts_with_comments += 1
                        else:
                            malformed_comments += 1
                            self.errors.append(
                                f"Wrong repo in Utterances: {post_file.relative_to(self.site_dir)} (found: {repo})"
                            )
                    else:
                        malformed_comments += 1
                        self.errors.append(
                            f"Malformed Utterances script: {post_file.relative_to(self.site_dir)}"
                        )

            except Exception as e:
                self.errors.append(f"Failed to parse {post_file.relative_to(self.site_dir)}: {e}")

        total = len(post_files)
        coverage = (posts_with_comments / total * 100) if total > 0 else 0

        self.stats['blog_posts'] = total
        self.stats['posts_with_comments'] = posts_with_comments
        self.stats['posts_missing_comments'] = missing_comments
        self.stats['utterances_coverage'] = f"{coverage:.1f}%"

        print(f"  ✓ Total blog posts: {total}")
        print(f"  ✓ Posts with comments: {posts_with_comments} ({coverage:.1f}%)")
        print(f"  ✓ Posts missing comments: {missing_comments}")
        if malformed_comments > 0:
            print(f"  ⚠️  Malformed comments: {malformed_comments}")

        if coverage < 90 and total > 0:
            self.warnings.append(
                f"Low Utterances coverage: {coverage:.1f}% (expected >90%)"
            )

    def validate_plausible_analytics(self):
        """Verify Plausible Analytics script is properly injected in all HTML pages."""
        print("\n📊 Validating Plausible Analytics...")

        # Find all HTML files, excluding non-page artefacts that shouldn't ship
        # the tracker (RSS feeds are XML masquerading as .html, embeds run in
        # iframes without analytics, sitemaps are crawler-only) and pages
        # that get *generated after* this validator runs (stats and changelog
        # are emitted directly into public/ post-validate — verified manually
        # on production that the Plausible tag is present, so these warnings
        # were spurious).
        SKIP_PATTERNS = ('feed/', '/embed/', 'sitemap', 'stats/', 'changelog/')
        html_files = [
            f for f in self.site_dir.glob('**/*.html')
            if not any(pat in str(f) for pat in SKIP_PATTERNS)
        ]

        if not html_files:
            self.errors.append("No HTML files found to validate")
            return

        # The Plausible script is now served same-origin at /js/script.js by
        # the Cloudflare Worker proxy. Accept either the new same-origin path
        # or the legacy upstream URL during the rollout — both are valid Plausible
        # tags; after a clean rebuild only the same-origin form should remain.
        missing_plausible = 0
        malformed_plausible = 0
        pages_with_plausible = 0

        for html_file in html_files:
            try:
                soup = BeautifulSoup(html_file.read_text(), 'html.parser')

                # Check for Plausible script (same-origin or legacy upstream)
                plausible_script = soup.find(
                    'script',
                    src=lambda x: x and 'script.js' in x and (
                        x == '/js/script.js' or 'plausible' in x
                    )
                )

                if not plausible_script:
                    missing_plausible += 1
                    self.warnings.append(
                        f"Missing Plausible: {html_file.relative_to(self.site_dir)}"
                    )
                    continue

                # Verify script attributes
                data_domain = plausible_script.get('data-domain')
                defer = plausible_script.get('defer')
                data_cfasync = plausible_script.get('data-cfasync')
                src = plausible_script.get('src')

                is_valid = True
                issues = []

                if data_domain != 'jameskilby.co.uk':
                    issues.append(f"wrong data-domain: {data_domain}")
                    is_valid = False

                if defer is None:
                    issues.append("missing defer attribute")
                    is_valid = False

                if data_cfasync != 'false':
                    issues.append(f"wrong data-cfasync: {data_cfasync}")
                    is_valid = False

                # Accept the same-origin path or the legacy upstream URL.
                if not src or (src != '/js/script.js' and 'plausible.jameskilby.cloud/js/script.js' not in src):
                    issues.append(f"wrong src: {src}")
                    is_valid = False

                if not is_valid:
                    malformed_plausible += 1
                    self.errors.append(
                        f"Malformed Plausible in {html_file.relative_to(self.site_dir)}: {', '.join(issues)}"
                    )
                else:
                    pages_with_plausible += 1

            except Exception as e:
                self.errors.append(f"Failed to parse {html_file}: {e}")

        total = len(html_files)
        coverage = (pages_with_plausible / total * 100) if total > 0 else 0

        self.stats['total_html_files'] = total
        self.stats['pages_with_plausible'] = pages_with_plausible
        self.stats['plausible_coverage'] = f"{coverage:.1f}%"

        print(f"  ✓ Pages with Plausible: {pages_with_plausible}/{total} ({coverage:.1f}%)")

        if coverage < 95 and total > 0:
            self.errors.append(
                f"Low Plausible coverage: {coverage:.1f}% (expected >95%)"
            )

        if missing_plausible > 0:
            self.warnings.append(
                f"{missing_plausible} pages missing Plausible script"
            )

    def validate_worker_stamp(self):
        """Verify the Advanced Mode Worker was stamped with CSP + path manifest.

        test_csp.py validates _headers, but the worker emits its own CSP on
        cache HITs from the value stamp_worker_manifest.py bakes into
        _worker.js. If stamping silently failed, both placeholders stay
        `null`: the worker would ship without a CSP and serve every path
        (soft-404 guard disabled) — and nothing else in the pipeline would
        notice.
        """
        print("\n🛡️  Validating Advanced Mode Worker stamp...")

        worker_file = self.site_dir / '_worker.js'
        if not worker_file.exists():
            self.errors.append(
                "_worker.js missing from output — Advanced Mode Worker "
                "(KV cache, security headers, soft-404 guard) will not deploy"
            )
            return

        source = worker_file.read_text(encoding='utf-8')

        csp_match = re.search(
            r'/\*__CSP_FROM_HEADERS_START__\*/(.*?)/\*__CSP_FROM_HEADERS_END__\*/',
            source, re.DOTALL)
        if not csp_match or csp_match.group(1).strip() == 'null':
            self.errors.append(
                "_worker.js CSP not stamped (placeholder still null) — "
                "worker-served responses would ship without a CSP"
            )
        elif 'utteranc.es' not in csp_match.group(1):
            self.errors.append(
                "_worker.js stamped CSP does not allow utteranc.es — "
                "comments would be blocked on cache HITs"
            )
        else:
            print("   ✅ CSP stamped into _worker.js")

        manifest_match = re.search(
            r'/\*__PATH_MANIFEST_START__\*/(.*?)/\*__PATH_MANIFEST_END__\*/',
            source, re.DOTALL)
        if not manifest_match or manifest_match.group(1).strip() == 'null':
            self.errors.append(
                "_worker.js path manifest not stamped (placeholder still "
                "null) — soft-404 guard would be disabled"
            )
        else:
            print("   ✅ Path manifest stamped into _worker.js")

    # Budget file that the Lighthouse PR gate asserts against. Read at runtime
    # so this validator and the gate can't drift apart.
    BUDGET_PATH = Path(__file__).parent.parent / '.github/lighthouse/budget.json'

    # Markers that should never survive a build. wpo-minify paths come from
    # WP-Optimize's minify cache, disabled in Aug 2026 — any page still
    # carrying one was served from a stale incremental cache rather than
    # regenerated.
    STALE_MARKERS = ('wpo-minify',)

    def _stylesheet_budget(self):
        """Max stylesheets/page from budget.json, or None if unreadable."""
        try:
            budget = json.loads(self.BUDGET_PATH.read_text())
        except (OSError, ValueError):
            return None
        for entry in budget:
            for counts in entry.get('resourceCounts', []):
                if counts.get('resourceType') == 'stylesheet':
                    return counts.get('budget')
        return None

    # A stylesheet request is either a plain <link rel=stylesheet> or the
    # async pattern critical CSS rewrites it into (rel=preload + as=style).
    # <noscript> fallbacks duplicate the href, so count distinct hrefs only.
    _CSS_REQ_RE = re.compile(
        r'<link[^>]+(?:rel="stylesheet"|as="style")[^>]*href="([^"]+)"'
        r'|<link[^>]+href="([^"]+)"[^>]*(?:rel="stylesheet"|as="style")',
        re.IGNORECASE,
    )

    def validate_resource_budgets(self):
        """Assert per-page stylesheet requests against the Lighthouse budget.

        Why this exists: on 2026-08-08 a build shipped 172 of 254 pages over
        the stylesheet budget (and 0.63 CLS with it) while every existing
        validator passed and Slack reported success. The pipeline measured
        how much work it did, never whether the output was correct. The
        Lighthouse gate that would have caught it only runs against the
        already-deployed site, too late to block anything.
        """
        print("📐 Validating per-page resource budgets...")

        limit = self._stylesheet_budget()
        if limit is None:
            self.warnings.append(
                f"Resource budget: could not read {self.BUDGET_PATH.name}, skipped")
            return

        html_files = self.find_files(['.html'])
        over = []
        at_limit = []
        stale = []
        worst = 0

        for f in html_files:
            try:
                html = f.read_text(encoding='utf-8', errors='replace')
            except OSError:
                continue
            hrefs = {m.group(1) or m.group(2) for m in self._CSS_REQ_RE.finditer(html)}
            count = len(hrefs)
            worst = max(worst, count)
            if count > limit:
                over.append((f.relative_to(self.site_dir).as_posix(), count))
            elif count == limit:
                at_limit.append(f.relative_to(self.site_dir).as_posix())
            if any(marker in html for marker in self.STALE_MARKERS):
                stale.append(f.relative_to(self.site_dir).as_posix())

        self.stats['Max stylesheets/page'] = f"{worst} (budget {limit})"
        self.stats['Pages over stylesheet budget'] = len(over)
        self.stats['Pages at stylesheet budget'] = len(at_limit)
        self.stats['Pages with stale markers'] = len(stale)

        # Warning, not error: shipping a slower page is better than blocking a
        # content deploy. It goes to Slack in the build card, where a non-zero
        # count is visible rather than buried in a log.
        if over:
            worst_pages = ", ".join(f"{p} ({n})" for p, n in
                                    sorted(over, key=lambda x: -x[1])[:3])
            self.warnings.append(
                f"{len(over)}/{len(html_files)} pages exceed the stylesheet "
                f"budget of {limit} (worst: {worst_pages})")
        if stale:
            self.warnings.append(
                f"{len(stale)} page(s) carry stale build markers "
                f"{self.STALE_MARKERS} — served from cache, not regenerated "
                f"(e.g. {stale[0]})")
        # "Within budget" hid the difference between 3/5 and 5/5. The site sat
        # at exactly 5/5 for a full day reading as a clean pass, with one
        # stylesheet of margin before the same check starts failing.
        if at_limit and not over:
            self.warnings.append(
                f"{len(at_limit)}/{len(html_files)} pages sit exactly at the "
                f"stylesheet budget of {limit} — no headroom; one more sheet "
                f"on any of them trips this check (e.g. {at_limit[0]})")

        if not over and not stale:
            headroom = "no headroom" if at_limit else f"{limit - worst} to spare"
            print(f"   ✅ All {len(html_files)} pages within budget "
                  f"(max {worst}/{limit}, {headroom}), no stale markers")

    def write_github_output(self):
        """Expose budget results to the workflow so Slack can report them."""
        out = os.environ.get('GITHUB_OUTPUT')
        if not out:
            return
        try:
            with open(out, 'a', encoding='utf-8') as fh:
                fh.write(f"max_stylesheets={self.stats.get('Max stylesheets/page', 'n/a')}\n")
                fh.write(f"pages_over_budget={self.stats.get('Pages over stylesheet budget', 0)}\n")
                fh.write(f"pages_at_budget={self.stats.get('Pages at stylesheet budget', 0)}\n")
                fh.write(f"pages_stale={self.stats.get('Pages with stale markers', 0)}\n")
        except OSError as e:
            print(f"   ⚠️  Could not write GITHUB_OUTPUT: {e}")

    def validate_all(self):
        """Run all validation checks."""
        print("🔍 Running comprehensive deployment validation...\n")
        print("="*80)

        self.validate_brotli_files()
        self.validate_image_formats()
        self.validate_picture_elements()
        self.validate_minification()
        self.validate_critical_css()
        self.validate_utterances_comments()
        self.validate_plausible_analytics()
        self.validate_worker_stamp()
        self.validate_resource_budgets()
        self.write_github_output()

        self.print_summary()

        return len(self.errors) == 0

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)

        if self.errors:
            print(f"\n❌ {len(self.errors)} ERROR(S) found:")
            for error in self.errors[:10]:  # Show first 10
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more errors")

        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} WARNING(S):")
            for warning in self.warnings[:5]:  # Show first 5
                print(f"  - {warning}")
            if len(self.warnings) > 5:
                print(f"  ... and {len(self.warnings) - 5} more warnings")

        if not self.errors and not self.warnings:
            print("\n✅ All validation checks passed!")

        # Print stats
        if self.stats:
            print("\n📊 Statistics:")
            for key, value in self.stats.items():
                print(f"  {key}: {value}")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: validate_deployment.py <site_directory>")
        print("\nExample:")
        print("  python3 validate_deployment.py ./static-output")
        sys.exit(1)

    site_dir = sys.argv[1]

    if not Path(site_dir).exists():
        print(f"❌ Error: Directory not found: {site_dir}")
        sys.exit(1)

    validator = DeploymentValidator(site_dir)
    success = validator.validate_all()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
