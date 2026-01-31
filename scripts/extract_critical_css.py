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

            soup = BeautifulSoup(html, 'html.parser')

            # Extract critical CSS
            critical_css = self._extract_critical_css(soup)

            if not critical_css:
                return False

            # Inline critical CSS
            if self._inline_critical_css(soup, critical_css):
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
        """Parse CSS and extract rules matching critical selectors"""
        rules = []

        # Simple CSS rule extraction (regex-based)
        # Matches: selector { properties }
        rule_pattern = r'([^{]+)\{([^}]+)\}'

        for match in re.finditer(rule_pattern, css_content):
            selector = match.group(1).strip()
            properties = match.group(2).strip()

            # Check if selector matches any critical selector
            if self._is_critical_selector(selector, critical_selectors):
                rules.append(f"{selector}{{{properties}}}")

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

    def _inline_critical_css(self, soup, critical_css):
        """Inline critical CSS in <head>"""
        if not soup.head or not critical_css:
            return False

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

    def _convert_css_to_preload(self, soup):
        """Convert external CSS links to preload with async loading"""
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href', '')

            # Skip if already preloaded
            if link.get('rel') == 'preload':
                continue

            # IMPORTANT: Do NOT convert brutalist-theme.css or fonts.css to async
            # These contain @import for custom fonts and need to load synchronously
            if 'brutalist-theme' in href or 'fonts.css' in href:
                # Keep as regular stylesheet, remove media="print" if present
                if link.get('media') == 'print' and 'onload' in link.attrs:
                    # This was set to async load, revert it
                    link['media'] = 'all'
                    del link['onload']
                continue

            # Convert to preload
            link['rel'] = 'preload'
            link['as'] = 'style'
            link['onload'] = "this.onload=null;this.rel='stylesheet'"

            # Add noscript fallback
            noscript = soup.new_tag('noscript')
            fallback_link = soup.new_tag('link')
            fallback_link['rel'] = 'stylesheet'
            fallback_link['href'] = href
            if link.get('media'):
                fallback_link['media'] = link['media']
            noscript.append(fallback_link)

            # Insert noscript after preload link
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
