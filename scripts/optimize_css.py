#!/usr/bin/env python3
"""
CSS Optimization Script
Removes unused CSS selectors and minifies CSS files
"""

import sys
import re
from pathlib import Path
from bs4 import BeautifulSoup
import cssutils
import logging
import argparse

# Suppress cssutils warnings
cssutils.log.setLevel(logging.CRITICAL)


class CSSOptimizer:
    """Optimize CSS files by removing unused selectors"""

    def __init__(self, public_dir='public', minify_only=False):
        self.public_dir = Path(public_dir)
        self.minify_only = minify_only
        self.files_optimized = 0
        self.bytes_saved = 0

    def optimize_all_css(self):
        """Process all CSS files in the public directory"""
        css_files = list(self.public_dir.rglob('*.css'))

        # Skip *our own* minified files (already optimised pipeline output).
        # WordPress-leaked .min.css files (wpo-minify, kadence theme) live
        # under wp-content/ and DO need unused-selector removal — that's the
        # whole point of running this on the static site. Without this, the
        # 98 KB wpo-minify-header bundle ships unchanged on every page.
        #
        # The earlier `'/assets/' in posix` test was too loose: WP themes
        # ship CSS under `wp-content/themes/<theme>/assets/css/*.min.css`
        # and the wpo-minify cache lives at `wp-content/cache/wpo-minify/
        # <id>/assets/<name>.min.css`. Both contain `/assets/` and were
        # therefore being treated as ours and skipped. Pin to the top-level
        # `assets/` directory (relative to public/) so only our own pipeline
        # output is excluded.
        def _is_ours(path):
            try:
                rel = path.relative_to(self.public_dir).as_posix()
            except ValueError:
                return False
            return rel.startswith('assets/')

        css_files = [
            f for f in css_files
            if '.min.' not in f.name or not _is_ours(f)
        ]

        if not css_files:
            print("⚠️  No CSS files found to optimize")
            return

        print(f"🎨 Optimizing {len(css_files)} CSS files...")

        used_selectors = set()
        if not self.minify_only:
            # Collect all HTML content to identify used selectors
            print("📄 Scanning HTML files for used CSS selectors...")
            used_selectors = self._collect_used_selectors()
            print(f"   Found {len(used_selectors)} unique selectors in HTML")

        # Optimize each CSS file
        for css_file in css_files:
            if self.optimize_css_file(css_file, used_selectors):
                self.files_optimized += 1

        print(f"\n✅ Optimized {self.files_optimized} CSS files")
        print(f"   Saved {self._format_bytes(self.bytes_saved)}")

    def _collect_used_selectors(self):
        """Collect class and ID selectors used across all HTML files.

        Only classes (.foo) and IDs (#bar) are collected here.  Element
        selectors (div, p, a, …) are kept unconditionally by
        _is_selector_used(), so there is no need to enumerate them from
        the HTML or maintain a hard-coded allow-list.
        """
        used_selectors = set()

        # Find all HTML files
        html_files = list(self.public_dir.rglob('*.html'))

        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')

                # Collect classes — BeautifulSoup always returns a list
                for tag in soup.find_all(class_=True):
                    for cls in tag.get('class', []):
                        used_selectors.add(f'.{cls}')

                # Collect IDs
                for tag in soup.find_all(id=True):
                    tag_id = tag.get('id')
                    if tag_id:
                        used_selectors.add(f'#{tag_id}')

            except Exception as e:
                print(f"   ⚠️  Error reading {html_file}: {e}")

        return used_selectors

    def optimize_css_file(self, css_file, used_selectors):
        """Optimize a single CSS file"""
        try:
            # Read original CSS
            with open(css_file, 'r', encoding='utf-8') as f:
                original_css = f.read()

            original_size = len(original_css.encode('utf-8'))

            if self.minify_only:
                optimized_css = original_css
            else:
                # Parse CSS
                sheet = cssutils.parseString(original_css)

                # Track removed rules
                rules_to_remove = []

                # Check each rule
                for rule in sheet:
                    if rule.type == rule.STYLE_RULE:
                        selector_text = rule.selectorText

                        # Check if selector is used
                        if not self._is_selector_used(selector_text, used_selectors):
                            rules_to_remove.append(rule)

                # Remove unused rules
                for rule in rules_to_remove:
                    sheet.deleteRule(rule)

                # Minify CSS (remove comments, whitespace)
                optimized_css = sheet.cssText.decode('utf-8')

            # Additional minification
            optimized_css = self._minify_css(optimized_css)

            # Calculate savings
            optimized_size = len(optimized_css.encode('utf-8'))
            saved = original_size - optimized_size

            if saved > 0:
                # Write optimized CSS
                with open(css_file, 'w', encoding='utf-8') as f:
                    f.write(optimized_css)

                self.bytes_saved += saved
                reduction = (saved / original_size) * 100 if original_size > 0 else 0

                print(f"   ✂️  {css_file.name}: {self._format_bytes(saved)} saved ({reduction:.1f}% reduction)")
                return True
            else:
                print(f"   ⏭️  {css_file.name}: Already optimized")
                return False

        except Exception as e:
            print(f"   ⚠️  Error optimizing {css_file}: {e}")
            return False

    # Classes that exist only after JavaScript runs — never present in the
    # initial server-rendered HTML, but their CSS rules are essential for
    # interactive UI (mobile menu toggles, drawer open/close, sticky-header
    # state, scroll-into-view animations, focus management). Without this
    # allowlist the old WP plugin/theme CSS would have these rules purged
    # and the nav / sticky header / carousels would silently break the
    # moment a user interacts with them.
    #
    # Source of truth: a wide grep of `classList.(add|remove|toggle)("...")`
    # across wpo-minify-footer-*.min.js. When adding theme features or
    # third-party widgets, re-run that grep and update this set.
    _DYNAMIC_CLASSES = frozenset({
        # Generic interactive state
        'active', 'open', 'opened',
        'show', 'shown', 'hidden', 'is-hidden',

        # Focus / accessibility
        'hide-focus-outline',

        # Mobile drawer + menu
        'show-drawer', 'toggle-show',
        'toggled-on', 'menu-item--toggled-on', 'menu-item--has-toggle',
        'dropdown-nav-special-toggle', 'sub-menu-edge',
        'current-menu-item',
        'kadence-scrollbar-fixer',

        # Sticky header / scroll-tracking states
        'header-is-fixed', 'item-is-fixed', 'item-is-stuck',
        'item-at-start', 'item-hidden-above', 'child-is-fixed',
        'scroll-visible',

        # Animation triggers
        'pop-animated', 'splide-initial',
    })

    # IDs created by JavaScript at runtime — same rationale as
    # _DYNAMIC_CLASSES, but for id selectors. search.js injects the search
    # box into <main> on load, so its ids never appear in the served HTML;
    # without this allowlist the optimizer stripped the
    # #blog-search-input::placeholder / cancel-button rules and part of the
    # search restyle silently never shipped.
    # Source of truth: `grep -oE 'id="[^"]+"' scripts/assets/js/search.js`.
    _DYNAMIC_IDS = frozenset({
        'blog-search-container', 'blog-search-input',
    })

    def _is_selector_used(self, selector_text, used_selectors):
        """Check if a CSS selector is used in HTML.

        Returns True if the selector (or any of its comma-separated
        alternatives) is potentially used by the rendered page or by JS-driven
        interaction. The check splits each compound selector on the descendant
        / sibling combinators and requires every compound to reference at
        least one class/id that is either present in HTML or in the
        dynamic-class allowlist.
        """
        # Always keep @media, @keyframes, etc.
        if selector_text.startswith('@'):
            return True

        # Top-level split: comma separates fully independent selectors. Any
        # match is enough to keep the rule.
        for raw_selector in selector_text.split(','):
            raw_selector = raw_selector.strip()
            if not raw_selector:
                continue

            # Split into compounds on combinators (descendant / >, +, ~).
            # ".a.b .c" → ["[.a.b]", "[.c]"] — both compounds must individually
            # be plausibly present for the rule to be matchable. If any
            # compound references only unknown classes/ids, the selector
            # cannot ever match → drop.
            compounds = re.split(r'[\s>+~]+', raw_selector)
            all_compounds_satisfied = True
            for compound in compounds:
                compound = compound.strip()
                if not compound:
                    continue

                # Strip pseudo-classes/elements + attribute selectors before
                # extracting class/id references. ":hover" / "[type=...]"
                # don't change which classes a rule matches.
                stripped = re.sub(r':+[\w-]+(\([^)]*\))?', '', compound)
                stripped = re.sub(r'\[[^\]]+\]', '', stripped)
                stripped = stripped.strip()

                if not stripped:
                    # Compound was just pseudos/attrs (e.g. ":root::before").
                    # Nothing to assert about classes — treat as satisfied.
                    continue

                # Extract class and id references *anywhere* in the compound.
                classes = re.findall(r'\.([a-zA-Z_][\w-]+)', stripped)
                ids = re.findall(r'#([a-zA-Z_][\w-]+)', stripped)

                if not classes and not ids:
                    # Pure element selector (e.g. "div", "p > a") — keep.
                    continue

                # If the compound references at least one class that is in
                # HTML *or* in the dynamic-class allowlist, OR at least one
                # id that is in HTML *or* in the dynamic-id allowlist, this
                # compound is matchable.
                if (any(f'.{c}' in used_selectors for c in classes)
                        or any(c in self._DYNAMIC_CLASSES for c in classes)
                        or any(f'#{i}' in used_selectors for i in ids)
                        or any(i in self._DYNAMIC_IDS for i in ids)):
                    continue

                # No referenced class/id matches → this compound (and the
                # whole selector) is unreachable.
                all_compounds_satisfied = False
                break

            if all_compounds_satisfied:
                return True

        return False

    def _minify_css(self, css):
        """Additional CSS minification"""
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)

        # Remove unnecessary whitespace
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r'\s*{\s*', '{', css)
        css = re.sub(r'\s*}\s*', '}', css)
        css = re.sub(r'\s*:\s*', ':', css)
        css = re.sub(r'\s*;\s*', ';', css)
        css = re.sub(r'\s*,\s*', ',', css)

        # Remove trailing semicolons
        css = re.sub(r';}', '}', css)

        return css.strip()

    def _format_bytes(self, bytes_count):
        """Format bytes to human-readable format"""
        for unit in ['B', 'KB', 'MB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} GB"


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Optimize CSS by removing unused selectors and minifying.")
    parser.add_argument("public_dir", nargs="?", default="public", help="Directory containing HTML/CSS files")
    parser.add_argument("--minify-only", action="store_true", help="Only minify CSS without removing selectors")
    args = parser.parse_args()

    # Check if cssutils is installed
    try:
        import cssutils
    except ImportError:
        print("❌ Error: cssutils is required for CSS optimization")
        print("   Install it with: pip install cssutils")
        sys.exit(1)

    optimizer = CSSOptimizer(args.public_dir, minify_only=args.minify_only)
    optimizer.optimize_all_css()

    sys.exit(0)


if __name__ == '__main__':
    main()
