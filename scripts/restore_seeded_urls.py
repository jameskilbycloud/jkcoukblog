#!/usr/bin/env python3
"""
Restore absolute URLs in seeded HTML files.

When running an incremental build, ./static-output/ is seeded from the
previously-committed public/ directory.  The committed HTML has already been
processed by convert_to_staging.py which converts absolute URLs
(https://jameskilby.co.uk/tag/foo/) to relative (/tag/foo/).

The HTML validator (validate_html.py) treats https:// URLs as external and
skips them, but it does check relative internal links.  Deleted archive pages
(old tags, categories) would therefore cause broken-link failures for seeded
posts that still link to them.

This script reverses the relative→absolute URL conversion so the seeded HTML
looks identical to what a fresh full build would produce at validation time.
convert_to_staging.py will re-convert them to relative before the final commit.

Usage:
    python3 scripts/restore_seeded_urls.py ./static-output
"""

import re
import sys
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent))
try:
    from config import Config
    TARGET_DOMAIN = Config.TARGET_DOMAIN
except (ImportError, AttributeError):
    TARGET_DOMAIN = 'https://jameskilby.co.uk'

# Paths that must stay relative — they are assets/API endpoints served
# directly and are never converted to absolute by the generator.
KEEP_RELATIVE = (
    'wp-content/',
    'wp-json/',
    'feed/',
    'api/',
    'markdown/',
    'sitemap',
    'assets/',
)


def restore_urls(output_dir: str) -> None:
    root = Path(output_dir)
    html_files = list(root.rglob('*.html'))
    count = 0

    for f in html_files:
        try:
            text = f.read_text(encoding='utf-8', errors='replace')
        except OSError:
            continue

        def fix(m: re.Match) -> str:
            path = m.group(1)
            stripped = path.lstrip('/')
            if any(stripped.startswith(e) for e in KEEP_RELATIVE):
                return m.group(0)
            return f'href="{TARGET_DOMAIN}{path}"'

        new_text = re.sub(r'href="(/[^"]*)"', fix, text)
        if new_text != text:
            f.write_text(new_text, encoding='utf-8')
            count += 1

    print(f'Restored absolute URLs in {count} seeded HTML files')


if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else './static-output'
    restore_urls(directory)
