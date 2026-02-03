#!/usr/bin/env python3
"""
HTML Minification Script
Minifies HTML files to reduce transfer size.
"""

import sys
import re
from pathlib import Path


def minify_html(html):
    """Minify HTML while preserving pre/code/script/style content."""
    placeholders = []

    def _stash(match):
        placeholders.append(match.group(0))
        return f"__HTML_MINIFY_PLACEHOLDER_{len(placeholders) - 1}__"

    # Preserve content where whitespace is significant
    html = re.sub(r'(<pre\b[^>]*>.*?</pre>)', _stash, html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'(<code\b[^>]*>.*?</code>)', _stash, html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'(<script\b[^>]*>.*?</script>)', _stash, html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'(<style\b[^>]*>.*?</style>)', _stash, html, flags=re.DOTALL | re.IGNORECASE)

    # Remove HTML comments (keep conditional comments)
    html = re.sub(r'<!--(?!\[if).*?-->', '', html, flags=re.DOTALL)

    # Collapse whitespace between tags and within text
    html = re.sub(r'>\s+<', '><', html)
    html = re.sub(r'\s{2,}', ' ', html)
    html = html.strip()

    # Restore preserved blocks
    for i, block in enumerate(placeholders):
        html = html.replace(f"__HTML_MINIFY_PLACEHOLDER_{i}__", block)

    return html


def main():
    if len(sys.argv) > 1:
        public_dir = Path(sys.argv[1])
    else:
        public_dir = Path('public')

    html_files = list(public_dir.rglob('*.html'))
    if not html_files:
        print("⚠️  No HTML files found to minify")
        return 0

    bytes_saved = 0
    files_minified = 0

    for html_file in html_files:
        try:
            original = html_file.read_text(encoding='utf-8')
            minified = minify_html(original)
            if len(minified) < len(original):
                html_file.write_text(minified, encoding='utf-8')
                bytes_saved += (len(original.encode('utf-8')) - len(minified.encode('utf-8')))
                files_minified += 1
        except Exception as e:
            print(f"⚠️  Error minifying {html_file}: {e}")

    print(f"✅ Minified {files_minified} HTML files")
    print(f"   Saved {bytes_saved / 1024:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
