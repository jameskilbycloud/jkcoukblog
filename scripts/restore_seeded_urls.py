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
posts that still link to them — and missing-image failures for seeded posts
whose <img> assets returned 404 from WordPress on the original fresh build
(those URLs stay absolute through validation on a full build and are only
collapsed to relative by convert_to_staging.py *after* validation).

This script reverses the relative→absolute URL conversion so the seeded HTML
looks identical to what a fresh full build would produce at validation time.
convert_to_staging.py will re-convert them to relative before the final commit.

Usage:
    python3 scripts/restore_seeded_urls.py ./static-output
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
try:
    from config import Config
    TARGET_DOMAIN = Config.TARGET_DOMAIN
except (ImportError, AttributeError):
    TARGET_DOMAIN = 'https://jameskilby.co.uk'

# href= paths under these prefixes stay relative — they're served as
# assets/APIs at the same origin and the validator's existence checks are
# correct (and desired) for them. Note this list is href-only; img/srcset
# get a different policy (see _absolutify_srcset).
HREF_KEEP_RELATIVE = (
    'wp-content/',
    'wp-json/',
    'feed/',
    'api/',
    'markdown/',
    'sitemap',
    'assets/',
)


def _absolutify_href(text: str) -> str:
    """Convert `href="/path"` to `href="<TARGET_DOMAIN>/path"` for non-asset hrefs."""

    def fix(m: re.Match) -> str:
        path = m.group(1)
        stripped = path.lstrip('/')
        if any(stripped.startswith(e) for e in HREF_KEEP_RELATIVE):
            return m.group(0)
        return f'href="{TARGET_DOMAIN}{path}"'

    return re.sub(r'href="(/[^"]*)"', fix, text)


def _absolutify_src(text: str) -> str:
    """Convert `<img|source ... src="/wp-content/...">` to absolute.

    Only `/wp-content/` paths are absolutified: theme/admin/api paths
    served from `/wp-content/` are the bucket that may have been retained
    as absolute through a fresh build's validation (because the asset
    downloader 404'd them) and only collapsed to relative at commit time.
    Other image src values (rare) stay relative; the validator will then
    check them against disk as a final safety net.
    """
    return re.sub(
        r'(<(?:img|source)\b[^>]*?\s)src="(/wp-content/[^"]*)"',
        rf'\1src="{TARGET_DOMAIN}\2"',
        text,
        flags=re.IGNORECASE,
    )


def _absolutify_srcset(text: str) -> str:
    """Convert relative `/wp-content/...` entries inside srcset/imagesrcset.

    A srcset is a comma-separated list of `<url> <width-or-density>` pairs
    where any entry's url may independently be relative or absolute. We
    walk each entry, absolutify only the `/wp-content/...` relatives, and
    rejoin. Anchored to srcset / imagesrcset attribute names so non-list
    attributes (e.g. data-srcset variants used by other plugins) aren't
    rewritten silently.
    """

    def fix(m: re.Match) -> str:
        attr = m.group(1)
        parts_out = []
        for raw in m.group(2).split(','):
            entry = raw.strip()
            if not entry:
                continue
            bits = entry.split(None, 1)
            url = bits[0]
            descriptor = (' ' + bits[1]) if len(bits) > 1 else ''
            if url.startswith('/wp-content/'):
                url = f'{TARGET_DOMAIN}{url}'
            parts_out.append(f'{url}{descriptor}')
        return f'{attr}="' + ', '.join(parts_out) + '"'

    return re.sub(
        r'\b(srcset|imagesrcset)="([^"]+)"',
        fix,
        text,
        flags=re.IGNORECASE,
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

        new_text = _absolutify_href(text)
        new_text = _absolutify_src(new_text)
        new_text = _absolutify_srcset(new_text)

        if new_text != text:
            f.write_text(new_text, encoding='utf-8')
            count += 1

    print(f'Restored absolute URLs in {count} seeded HTML files')


if __name__ == '__main__':
    directory = sys.argv[1] if len(sys.argv) > 1 else './static-output'
    restore_urls(directory)
