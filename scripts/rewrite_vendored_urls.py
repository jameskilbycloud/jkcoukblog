#!/usr/bin/env python3
"""Rewrite third-party CDN URLs in generated HTML to vendored /js/ paths.

wp_to_static_generator.py is incremental — for posts whose WordPress source
hasn't changed, cached HTML is reused and the script-tag injection that emits
the canonical /js/* URLs is skipped. This sweep runs after generation and
rewrites any stragglers. Idempotent.
"""

import sys
from pathlib import Path

REWRITES = {
    'https://cdn.jsdelivr.net/npm/@splidejs/splide@4/dist/splide.min.js': '/js/splide.min.js',
    'https://cdn.jsdelivr.net/npm/fuse.js@7.0.0': '/js/fuse.min.js',
}


def rewrite_file(path: Path) -> dict:
    text = path.read_text(encoding='utf-8', errors='ignore')
    counts = {}
    new_text = text
    for old, new in REWRITES.items():
        n = new_text.count(old)
        if n:
            new_text = new_text.replace(old, new)
            counts[old] = n
    if new_text != text:
        path.write_text(new_text, encoding='utf-8')
    return counts


def main(root: str) -> int:
    root_path = Path(root)
    if not root_path.is_dir():
        print(f"❌ Not a directory: {root}", file=sys.stderr)
        return 1

    print(f"🔁 Sweeping {root}/ for stale vendored-CDN URLs...")
    files_changed = 0
    totals = {k: 0 for k in REWRITES}
    for html in root_path.rglob('*.html'):
        counts = rewrite_file(html)
        if counts:
            files_changed += 1
            for k, v in counts.items():
                totals[k] += v

    print(f"   files modified: {files_changed}")
    for old, n in totals.items():
        if n:
            print(f"   {n}× {old}")
            print(f"      → {REWRITES[old]}")
    if not files_changed:
        print("   ✅ no stale URLs found (already clean)")
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else 'public'))
