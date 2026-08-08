#!/usr/bin/env python3
"""
JS Minification Script
Minifies JavaScript files in the built site.

Why this exists
---------------
WP-Optimize's minify feature used to concatenate *and* minify every
plugin/theme script into one wpo-minify-footer bundle. That feature was
disabled because the bundle path embeds a regeneration timestamp
(`wp-content/cache/wpo-minify/<ts>/...`) which changed on every WordPress-side
cache rebuild, rewriting all ~250 HTML pages for zero content change and
invalidating the incremental build cache, the KV HTML cache and every
.br/.gz sidecar along with it.

Nothing else in this pipeline minifies JS: `optimize_css.py` covers CSS, and
`minify_html.py` deliberately *stashes* <script> bodies so it won't touch
them. Brotli compresses JS but compression is not minification — it can't
drop comments or shorten the token stream before the browser parses it.

Scope, measured against the live CMS: the theme scripts WordPress now emits
(navigation.min.js, splide.min.js, splide-init.min.js) are already minified
by Kadence, so they gain 0-0.3% here. WP-Optimize was concatenating
pre-minified files rather than minifying source, so disabling it lost less
than it first appeared. The real win is project-owned JS — search.js is
-27.8% — plus insurance for any future plugin that ships unminified script.

It runs over the built output after CSS optimisation and before Brotli
compression, so the .br/.gz sidecars are generated from the minified bytes.
"""

import argparse
import sys
from pathlib import Path

try:
    import rjsmin
except ImportError:
    rjsmin = None


class JSMinifier:
    """Minify JavaScript files in the built output tree."""

    # Never minify these, matched against the path relative to public_dir.
    #
    # _worker.js is the Cloudflare Advanced Mode Worker. It is not served to
    # browsers, so minifying it buys nothing, and scripts/stamp_worker_manifest.py
    # locates its injection points via literal comment markers
    # (/*__PATH_MANIFEST_START__*/ etc.) that a minifier would strip. Excluding
    # it keeps re-stamping an already-built tree safe.
    EXCLUDED_PATHS = (
        '_worker.js',
    )

    def __init__(self, public_dir='public'):
        self.public_dir = Path(public_dir)
        self.files_minified = 0
        self.files_skipped = 0
        self.bytes_saved = 0

    def _is_excluded(self, path):
        try:
            rel = path.relative_to(self.public_dir).as_posix()
        except ValueError:
            return False
        return any(rel == e or rel.endswith('/' + e) for e in self.EXCLUDED_PATHS)

    def minify_all(self):
        js_files = [
            f for f in sorted(self.public_dir.rglob('*.js'))
            if not self._is_excluded(f)
        ]

        if not js_files:
            print("⚠️  No JS files found to minify")
            return

        print(f"📜 Minifying {len(js_files)} JS files...")

        for js_file in js_files:
            self.minify_file(js_file)

        print(f"\n✅ Minified {self.files_minified} JS files"
              f" ({self.files_skipped} unchanged)")
        print(f"   Saved {self._format_bytes(self.bytes_saved)}")

    def minify_file(self, js_file):
        """Minify one file in place. Returns True if it was rewritten."""
        try:
            original = js_file.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError) as e:
            # Not fatal: a single unreadable asset shouldn't fail the build,
            # it just ships unminified. Brotli still compresses it.
            print(f"   ⚠️  Skipped {js_file.name}: {e}")
            self.files_skipped += 1
            return False

        try:
            minified = rjsmin.jsmin(original)
        except Exception as e:
            print(f"   ⚠️  Skipped {js_file.name}: minifier error: {e}")
            self.files_skipped += 1
            return False

        before = len(original.encode('utf-8'))
        after = len(minified.encode('utf-8'))

        # Only rewrite on a real reduction. Rewriting for a 0-byte delta would
        # churn the file's mtime and content hash, which defeats the
        # incremental builder and forces a pointless recompression.
        if after >= before:
            self.files_skipped += 1
            return False

        try:
            js_file.write_text(minified, encoding='utf-8')
        except OSError as e:
            print(f"   ⚠️  Could not write {js_file.name}: {e}")
            self.files_skipped += 1
            return False

        saved = before - after
        self.bytes_saved += saved
        self.files_minified += 1
        pct = (saved / before * 100) if before else 0
        print(f"   📜 {js_file.relative_to(self.public_dir)}: "
              f"{self._format_bytes(before)} → {self._format_bytes(after)} "
              f"(-{pct:.1f}%)")
        return True

    @staticmethod
    def _format_bytes(bytes_count):
        """Format bytes to human-readable format"""
        value = float(bytes_count)
        for unit in ['B', 'KB', 'MB']:
            if value < 1024.0:
                return f"{value:.1f} {unit}"
            value /= 1024.0
        return f"{value:.1f} GB"


def main():
    parser = argparse.ArgumentParser(
        description="Minify JavaScript files in the built site."
    )
    parser.add_argument("public_dir", nargs="?", default="public",
                        help="Directory containing the built site")
    args = parser.parse_args()

    if rjsmin is None:
        print("❌ Error: rjsmin is required for JS minification")
        print("   Install it with: pip install rjsmin")
        sys.exit(1)

    minifier = JSMinifier(args.public_dir)
    minifier.minify_all()
    sys.exit(0)


if __name__ == '__main__':
    main()
