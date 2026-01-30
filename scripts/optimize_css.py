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

# Suppress cssutils warnings
cssutils.log.setLevel(logging.CRITICAL)


class CSSOptimizer:
    """Optimize CSS files by removing unused selectors"""

    def __init__(self, public_dir='public'):
        self.public_dir = Path(public_dir)
        self.files_optimized = 0
        self.bytes_saved = 0

    def optimize_all_css(self):
        """Process all CSS files in the public directory"""
        css_files = list(self.public_dir.rglob('*.css'))

        # Exclude already minified files
        css_files = [f for f in css_files if '.min.' not in f.name]

        if not css_files:
            print("⚠️  No CSS files found to optimize")
            return

        print(f"🎨 Optimizing {len(css_files)} CSS files...")

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
        """Collect all class and ID selectors used in HTML files"""
        used_selectors = set()

        # Find all HTML files
        html_files = list(self.public_dir.rglob('*.html'))

        for html_file in html_files:
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    soup = BeautifulSoup(f.read(), 'html.parser')

                # Collect classes
                for tag in soup.find_all(class_=True):
                    classes = tag.get('class', [])
                    if isinstance(classes, list):
                        for cls in classes:
                            used_selectors.add(f'.{cls}')
                    else:
                        used_selectors.add(f'.{classes}')

                # Collect IDs
                for tag in soup.find_all(id=True):
                    tag_id = tag.get('id')
                    if tag_id:
                        used_selectors.add(f'#{tag_id}')

                # Collect element selectors (always keep these)
                for tag in soup.find_all():
                    if tag.name:
                        used_selectors.add(tag.name)

            except Exception as e:
                print(f"   ⚠️  Error reading {html_file}: {e}")

        # Always keep common pseudo-selectors and element selectors
        always_keep = {
            'html', 'body', 'head', 'meta', 'link', 'script', 'style',
            'div', 'span', 'p', 'a', 'img', 'ul', 'ol', 'li',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'header', 'footer', 'main', 'article', 'section', 'nav', 'aside',
            'table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot',
            'form', 'input', 'textarea', 'select', 'option', 'button', 'label',
            'strong', 'em', 'b', 'i', 'u', 'code', 'pre', 'blockquote',
        }
        used_selectors.update(always_keep)

        return used_selectors

    def optimize_css_file(self, css_file, used_selectors):
        """Optimize a single CSS file"""
        try:
            # Read original CSS
            with open(css_file, 'r', encoding='utf-8') as f:
                original_css = f.read()

            original_size = len(original_css.encode('utf-8'))

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

    def _is_selector_used(self, selector_text, used_selectors):
        """Check if a CSS selector is used in HTML"""
        # Always keep @media, @keyframes, etc.
        if selector_text.startswith('@'):
            return True

        # Split compound selectors (e.g., ".class1 .class2" or ".class1, .class2")
        parts = re.split(r'[,\s>+~]', selector_text)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Remove pseudo-classes and pseudo-elements for matching
            part = re.sub(r':+[\w-]+(\([^)]*\))?', '', part)
            part = re.sub(r'\[[^\]]+\]', '', part)  # Remove attribute selectors
            part = part.strip()

            if not part:
                continue

            # Check if base selector is used
            if part in used_selectors:
                return True

            # Check for element selectors (no . or #)
            if not part.startswith('.') and not part.startswith('#'):
                # Element selector - always keep
                return True

        # Selector not found in HTML
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
    if len(sys.argv) > 1:
        public_dir = sys.argv[1]
    else:
        public_dir = 'public'

    # Check if cssutils is installed
    try:
        import cssutils
    except ImportError:
        print("❌ Error: cssutils is required for CSS optimization")
        print("   Install it with: pip install cssutils")
        sys.exit(1)

    optimizer = CSSOptimizer(public_dir)
    optimizer.optimize_all_css()

    sys.exit(0)


if __name__ == '__main__':
    main()
