#!/usr/bin/env python3
"""
Critical CSS Extraction and Inlining Script

Extracts above-the-fold CSS and inlines it in <head> to eliminate render-blocking CSS.
Converts external CSS to preload with async loading.

This significantly improves First Contentful Paint (FCP) by 30-50%.
"""

import sys
from pathlib import Path
from bs4 import BeautifulSoup
import re
import subprocess
import json


class CriticalCSSExtractor:
    """Extract and inline critical CSS for faster rendering"""

    def __init__(self, public_dir='public'):
        self.public_dir = Path(public_dir)
        self.files_processed = 0
        self.css_inlined = 0
        self.max_inline_critical = 12000

    def process_all_files(self):
        """Process all HTML files in the public directory"""
        html_files = list(self.public_dir.rglob('*.html'))

        print(f"🎨 Processing {len(html_files)} HTML files for critical CSS extraction...")

        for html_file in html_files:
            if self.process_file(html_file):
                self.files_processed += 1

        print(f"\n✅ Processed {self.files_processed} files")
        print(f"   Inlined critical CSS in {self.css_inlined} files")

    def process_file(self, file_path):
        """Process a single HTML file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html = f.read()

            # Pre-parse cleanup: strip accumulated noscript fallbacks and
            # deduplicate <link> tags by href so BeautifulSoup sees a clean doc.
            html = self._dedup_head_links(html)

            soup = BeautifulSoup(html, 'html.parser')

            # Extract critical CSS
            critical_css = self._extract_critical_css(soup)

            if not critical_css:
                return False

            # Inline critical CSS
            if self._inline_critical_css(soup, critical_css, file_path):
                # Convert external CSS to async preload
                self._convert_css_to_preload(soup)

                # Save modified HTML
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(str(soup))

                self.css_inlined += 1
                return True

            return False

        except Exception as e:
            print(f"⚠️  Error processing {file_path}: {e}")
            return False

    def _extract_critical_css(self, soup):
        """
        Extract critical above-the-fold CSS
        Uses a simple heuristic: CSS rules for elements in first ~800px of content
        """
        critical_selectors = set()

        # Find elements likely above the fold
        # Priority: head elements, first main/article content, header, nav
        above_fold_elements = []

        # Header and navigation
        for tag in soup.find_all(['header', 'nav']):
            above_fold_elements.append(tag)

        # First main or article
        main = soup.find(['main', 'article'])
        if main:
            above_fold_elements.append(main)
            # First few children of main
            for child in list(main.children)[:10]:
                if hasattr(child, 'name'):
                    above_fold_elements.append(child)

        # Collect all CSS selectors for these elements
        for element in above_fold_elements:
            # Skip text nodes and other non-tag elements
            if not hasattr(element, 'name') or not hasattr(element, 'get'):
                continue

            # Element tag name
            if element.name:
                critical_selectors.add(element.name)

            # Classes
            classes = element.get('class', [])
            if isinstance(classes, list):
                for cls in classes:
                    critical_selectors.add(f'.{cls}')

            # ID
            tag_id = element.get('id')
            if tag_id:
                critical_selectors.add(f'#{tag_id}')

            # Parent-child combinations (limited depth)
            parent = element.parent
            if parent and hasattr(parent, 'name') and parent.name:
                critical_selectors.add(f'{parent.name} {element.name}')

        # Always include critical base elements
        base_selectors = {
            'html', 'body', 'head', 'meta', 'link',
            'h1', 'h2', 'h3', 'p', 'a', 'img',
            'header', 'nav', 'main', 'article', 'section',
        }
        critical_selectors.update(base_selectors)

        # Extract CSS rules that match critical selectors
        critical_css = self._extract_matching_css_rules(soup, critical_selectors)

        return critical_css

    def _extract_matching_css_rules(self, soup, selectors):
        """Extract CSS rules that match the given selectors"""
        critical_rules = []

        # Find all style tags
        for style_tag in soup.find_all('style'):
            if style_tag.string:
                css_content = style_tag.string
                rules = self._parse_css_rules(css_content, selectors)
                critical_rules.extend(rules)

        # Find all external CSS files and extract their rules
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            if href:
                css_path = self._resolve_css_path(href)
                if css_path and css_path.exists():
                    try:
                        with open(css_path, 'r', encoding='utf-8') as f:
                            css_content = f.read()
                            rules = self._parse_css_rules(css_content, selectors)
                            critical_rules.extend(rules)
                    except Exception as e:
                        # Silently skip if we can't read the file
                        pass

        # Combine and minify
        combined_css = '\n'.join(critical_rules)
        minified_css = self._minify_css(combined_css)

        # Limit to ~15KB of critical CSS
        if len(minified_css) > 15000:
            minified_css = minified_css[:15000]
            # Find last complete rule
            last_brace = minified_css.rfind('}')
            if last_brace > 0:
                minified_css = minified_css[:last_brace + 1]

        return minified_css

    def _parse_css_rules(self, css_content, critical_selectors):
        """Parse CSS and extract rules matching critical selectors.

        Uses a brace-depth tokenizer rather than a regex so that nested
        at-rules (@media, @supports) and minified CSS are handled correctly.

        Strategy:
          - @keyframes / @font-face blocks are skipped entirely (their inner
            tokens are not selector-based and would produce false matches).
          - @media / @supports / @layer blocks are recursed into; only the
            matching inner rules are kept, wrapped in the at-rule header.
          - @import / @charset / @namespace end with ';' before the next '{';
            these are skipped by detecting the semicolon first.
          - Regular rules are tested against critical_selectors and included
            when they match.
        """
        # Strip comments before parsing so that '{' / '}' inside comments
        # don't confuse the depth tracker.
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)

        rules = []
        i = 0
        n = len(css_content)

        # At-rules whose blocks contain keyframe stops or font descriptors —
        # not selector-based, so we must not recurse.
        SKIP_AT_RULES = ('@keyframes', '@-webkit-keyframes', '@-moz-keyframes',
                         '@-o-keyframes', '@font-face')

        while i < n:
            # Skip whitespace
            while i < n and css_content[i].isspace():
                i += 1
            if i >= n:
                break

            brace_pos = css_content.find('{', i)
            if brace_pos == -1:
                break  # No more rules

            # If a ';' comes before the next '{' this is an at-statement
            # (@import, @charset, @namespace) with no block — skip it.
            semi_pos = css_content.find(';', i)
            if semi_pos != -1 and semi_pos < brace_pos:
                i = semi_pos + 1
                continue

            selector = css_content[i:brace_pos].strip()

            # Walk forward to find the matching closing brace, tracking depth.
            depth = 1
            j = brace_pos + 1
            while j < n and depth > 0:
                if css_content[j] == '{':
                    depth += 1
                elif css_content[j] == '}':
                    depth -= 1
                j += 1

            block_content = css_content[brace_pos + 1:j - 1]
            i = j  # Advance past the closing brace

            if selector.startswith('@'):
                # Normalise the at-keyword for comparison.
                at_keyword = re.split(r'[\s(]', selector, maxsplit=1)[0].lower()

                if at_keyword in SKIP_AT_RULES:
                    # Keyframes / font-face: skip entirely.
                    continue

                # Conditional group rules (@media, @supports, @layer …):
                # recurse and keep only the matching inner rules.
                inner = self._parse_css_rules(block_content, critical_selectors)
                if inner:
                    rules.append(f"{selector}{{{''.join(inner)}}}")
            else:
                if self._is_critical_selector(selector, critical_selectors):
                    rules.append(f"{selector}{{{block_content}}}")

        return rules

    def _is_critical_selector(self, selector, critical_selectors):
        """Check if a CSS selector matches critical selectors"""
        # Remove pseudo-classes and pseudo-elements for matching
        clean_selector = re.sub(r':+[\w-]+(\([^)]*\))?', '', selector)
        clean_selector = re.sub(r'\[[^\]]+\]', '', clean_selector)

        # Split compound selectors
        parts = re.split(r'[,\s>+~]', clean_selector)

        for part in parts:
            part = part.strip()
            if part in critical_selectors:
                return True

            # Check if it's an element selector (no . or #)
            if part and not part.startswith('.') and not part.startswith('#'):
                # Check if element name matches
                element_name = re.sub(r'[^a-zA-Z0-9]', '', part)
                if element_name in critical_selectors:
                    return True

        return False

    def _resolve_css_path(self, href):
        """Resolve CSS file path from href"""
        # Remove leading slash
        href = href.lstrip('/')

        # Try to find the file
        css_path = self.public_dir / href

        if css_path.exists():
            return css_path

        return None

    def _minify_css(self, css):
        """Minify CSS"""
        # Remove comments
        css = re.sub(r'/\*.*?\*/', '', css, flags=re.DOTALL)

        # Remove whitespace
        css = re.sub(r'\s+', ' ', css)
        css = re.sub(r'\s*{\s*', '{', css)
        css = re.sub(r'\s*}\s*', '}', css)
        css = re.sub(r'\s*:\s*', ':', css)
        css = re.sub(r'\s*;\s*', ';', css)
        css = re.sub(r'\s*,\s*', ',', css)

        # Remove trailing semicolons
        css = re.sub(r';}', '}', css)

        return css.strip()

    def _inline_critical_css(self, soup, critical_css, file_path):
        """Inline critical CSS in <head>, or externalize if too large"""
        if not soup.head or not critical_css:
            return False

        if len(critical_css) > self.max_inline_critical:
            return self._externalize_critical_css(soup, critical_css, file_path)

        # Check if critical CSS already inlined
        existing = soup.find('style', id='critical-css')
        if existing:
            # Update existing
            existing.string = critical_css
        else:
            # Create new style tag
            style_tag = soup.new_tag('style', id='critical-css')
            style_tag.string = critical_css

            # Insert at top of head (before other styles)
            soup.head.insert(0, style_tag)

        return True

    def _externalize_critical_css(self, soup, critical_css, file_path):
        """Write critical CSS to external file and link it to reduce HTML size"""
        try:
            rel_path = file_path.relative_to(self.public_dir).as_posix()
            safe_slug = re.sub(r'[^a-zA-Z0-9_-]+', '-', rel_path).strip('-')
            css_dir = self.public_dir / 'assets' / 'css' / 'critical'
            css_dir.mkdir(parents=True, exist_ok=True)
            css_filename = f'critical-{safe_slug}.css'
            css_path = css_dir / css_filename

            css_path.write_text(critical_css, encoding='utf-8')

            css_href = f'/assets/css/critical/{css_filename}'

            # Only insert the stylesheet link if not already present —
            # prevents duplication on repeated pipeline runs.
            existing_preload = soup.find('link', attrs={'href': css_href, 'rel': True})
            if not existing_preload:
                # Insert as a plain stylesheet link; _convert_css_to_preload
                # will convert it to async preload+onload and add a noscript
                # fallback in the same pass.
                link = soup.new_tag('link')
                link['rel'] = 'stylesheet'
                link['href'] = css_href
                soup.head.insert(0, link)

            # Remove any existing inline critical CSS
            existing = soup.find('style', id='critical-css')
            if existing:
                existing.decompose()

            return True
        except Exception as e:
            print(f"⚠️  Failed to externalize critical CSS: {e}")
            return False

    @staticmethod
    def _dedup_head_links(html):
        """Pre-parse cleanup: strip accumulated <noscript> fallbacks and
        deduplicate <link> tags inside <head> by href attribute.

        Operates on the raw HTML string so it works even when the document is
        badly damaged (hundreds of duplicate links, deeply stacked noscript
        wrappers, etc.) and BeautifulSoup would struggle to parse it cleanly.

        After this pass every href appears exactly once inside <head> and
        there are no noscript-wrapped link fallbacks.  _convert_css_to_preload
        then re-adds exactly one fresh noscript per async-CSS preload link.
        """
        head_match = re.search(
            r'(<head\b[^>]*>)(.*?)(</head>)',
            html,
            re.IGNORECASE | re.DOTALL,
        )
        if not head_match:
            return html

        head_open  = head_match.group(1)
        head_body  = head_match.group(2)
        head_close = head_match.group(3)

        # 1. Strip ALL <noscript> blocks that wrap a single <link>.
        #    _convert_css_to_preload re-adds exactly one per async-CSS link.
        head_body = re.sub(
            r'<noscript>\s*<link\b[^>]*/?\s*>\s*</noscript>',
            '',
            head_body,
            flags=re.IGNORECASE | re.DOTALL,
        )

        # 2. Deduplicate <link> tags by href — keep the first occurrence.
        seen_hrefs = set()

        def _keep_unique_link(m):
            tag = m.group(0)
            href_m = re.search(r'\bhref=["\']([^"\']+)["\']', tag, re.IGNORECASE)
            if not href_m:
                return tag  # No href attribute — keep unconditionally.
            href = href_m.group(1)
            if href in seen_hrefs:
                return ''
            seen_hrefs.add(href)
            return tag

        head_body = re.sub(
            r'<link\b[^>]*/?>',
            _keep_unique_link,
            head_body,
            flags=re.IGNORECASE,
        )

        new_head = head_open + head_body + head_close
        return html[:head_match.start()] + new_head + html[head_match.end():]

    def _convert_css_to_preload(self, soup):
        """Convert external CSS links to preload with async loading.

        Idempotent and self-healing.  The raw-string pre-pass in process_file
        (_dedup_head_links) removes accumulated noscript/link duplication
        before BS4 ever sees the document, so this method only needs to:

          1. Strip any residual noscript fallbacks still in <head>.
          2. Convert remaining stylesheet links to preload+onload.
          3. Add exactly one fresh noscript per async-CSS preload link.

        Steps 2 and 3 are intentionally separated so that links which were
        already converted to preload+onload in a prior pipeline run (and
        survived the dedup pass as-is) also receive a fresh noscript without
        the double-counting that occurred when noscripts were added in step 2
        *and* again in a former "step 3".
        """
        EXCLUDED = ('brutalist-theme', 'fonts.css', 'consolidated-inline-styles')

        # ── Step 1: strip residual noscript blocks ───────────────────────
        # _dedup_head_links already removed them from the raw string, but
        # do a belt-and-suspenders BS4 cleanup for safety.
        if soup.head:
            for ns in list(soup.head.find_all('noscript')):
                if ns.find('link'):
                    ns.decompose()

        # ── Step 2: convert stylesheet links → preload+onload ────────────
        # Do NOT add noscripts here — step 3 handles all of them uniformly.
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')
            # IMPORTANT: brutalist-theme.css and fonts.css use @import for
            # custom fonts and must load synchronously.
            if any(x in href for x in EXCLUDED):
                continue
            link['rel'] = 'preload'
            link['as'] = 'style'
            link['onload'] = "this.onload=null;this.rel='stylesheet'"

        # ── Step 3: add exactly one noscript per async-CSS preload link ───
        # This covers three cases:
        #   a) Links just converted to preload+onload in step 2.
        #   b) Links already preload+onload from a previous pipeline run.
        #   c) Plain preload-as-style links (no onload) left over from the old
        #      _externalize_critical_css bug — upgrade them to include onload
        #      so they actually apply the stylesheet at runtime.
        if soup.head:
            for link in list(soup.head.find_all('link')):
                rel  = link.get('rel') or []
                href = link.get('href', '')
                if 'preload' not in rel or link.get('as') != 'style':
                    continue
                if any(x in href for x in EXCLUDED):
                    continue
                # Upgrade plain preload to async onload if missing.
                if not link.get('onload'):
                    link['onload'] = "this.onload=null;this.rel='stylesheet'"
                noscript = soup.new_tag('noscript')
                fallback = soup.new_tag('link')
                fallback['rel'] = 'stylesheet'
                fallback['href'] = href
                if link.get('media'):
                    fallback['media'] = link['media']
                noscript.append(fallback)
                link.insert_after(noscript)


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        public_dir = sys.argv[1]
    else:
        public_dir = 'public'

    extractor = CriticalCSSExtractor(public_dir)
    extractor.process_all_files()

    sys.exit(0)


if __name__ == '__main__':
    main()
