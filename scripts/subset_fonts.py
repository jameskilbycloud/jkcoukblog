#!/usr/bin/env python3
"""
Subset Anton woff2 to the characters actually used in rendered headings.

Anton ships at ~130 KB and is *preloaded* (on the LCP critical path).
The vast majority of its glyphs are never rendered on this site —
Anton is only applied to h1/h2/h3/h4/h5/h6 and a handful of UI classes
(`.site-title`, `.entry-title`, `.jkr-eyebrow`, etc.). Across all 182
HTML files there are typically ~80-100 unique characters used in that
context. Subsetting cuts the woff2 from ~130 KB → ~12-20 KB.

How it works
------------
1. Walk every *.html under static-output (or a path passed via argv).
2. Pull text content from every element styled with Anton — heading
   tags + the known Anton UI classes from brutalist-theme.css.
3. Build a character set, plus a safety pad of ASCII printable + common
   typography characters (smart quotes, em/en dash, ellipsis) so a
   future post title with mild punctuation doesn't render with .notdef
   boxes.
4. Use fontTools' Subsetter API to emit a new woff2 with only those
   glyphs.

Idempotent: writes the output back over the input path, so a re-run
against the already-subsetted file is a no-op (slightly smaller still
once chars stabilise).

Dependencies: fonttools[woff] (already pinned in requirements.txt for
the og:image generator).

Usage:
    python3 scripts/subset_fonts.py [site_dir]
"""

import shutil
import sys
from pathlib import Path
from bs4 import BeautifulSoup

try:
    from fontTools.subset import Subsetter, Options
    from fontTools.ttLib import TTFont
    _DEPS_OK = True
    _DEPS_ERROR = None
except ImportError as e:
    _DEPS_OK = False
    _DEPS_ERROR = str(e)


# Elements/classes rendered in Anton — sourced from brutalist-theme.css.
# Anything in this list contributes its text to the subset character pool.
ANTON_SELECTORS = (
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    '.site-title', '.entry-title',
    '.jkr-eyebrow', '.jkr-strap-meta', '.jkr-filter-label',
    '.jkr-topic-count', '.jkr-term',
)

# Safety pad — characters that might land in a future heading even if
# they're not currently used. Adding ~30 of these costs <2 KB and avoids
# regenerating fonts every time a post title gains a colon or smart quote.
SAFETY_PAD = (
    # Standard ASCII printable (covers letters, digits, common punctuation)
    ''.join(chr(c) for c in range(0x20, 0x7F))
    # Common typography we might add later
    + "'\"…–—·•‘’“”«»"
)

# Anton is preloaded and on the LCP path; subset it. Space Grotesk
# (also preloaded) is used for body text — far broader character set,
# diminishing returns. Add here if a future audit shows savings worth it.
TARGET_FONT_REL = 'assets/fonts/anton-v27-latin-400.woff2'

# Source-of-truth (full, un-subsetted) Anton woff2. Lives outside the
# deploy output so the workflow's seed-from-public/ step can't
# overwrite it with a previously-subsetted copy. Restored over the
# deployed font on every build, before subsetting.
MASTER_FONT_REL = 'scripts/fonts/anton-v27-latin-400.woff2'


def collect_chars(site_dir: Path) -> set:
    """Scan every HTML file for Anton-rendered text and return the
    unique characters that appear within those elements."""
    chars = set()
    html_files = list(site_dir.rglob('*.html'))
    print(f"   📄 Scanning {len(html_files)} HTML files for Anton-rendered text...")
    for f in html_files:
        try:
            body = f.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        soup = BeautifulSoup(body, 'html.parser')
        # Tags first
        for tag in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
            for el in soup.find_all(tag):
                chars.update(el.get_text())
        # Class-based selectors
        for sel in ANTON_SELECTORS:
            if sel.startswith('.'):
                for el in soup.select(sel):
                    chars.update(el.get_text())
    return chars


def subset_font(font_path: Path, characters: str) -> dict:
    """Run fontTools subsetter against `font_path` in-place. Returns
    a dict with before/after sizes plus retained glyph count.
    Raises if fontTools can't open the file."""
    before = font_path.stat().st_size

    font = TTFont(str(font_path))
    options = Options()
    # Output flavour: keep woff2 so the served URL doesn't need to change
    # and the existing <link rel=preload as=font type=font/woff2> remains
    # valid. Brotli is needed for woff2 (re)compression, pulled by the
    # fonttools[woff] extra.
    options.flavor = 'woff2'
    # Layout features we definitely want to keep so kerning + ligatures
    # still work on the survivors.
    options.layout_features = ['*']
    # Drop name-table entries to save a tiny amount (font name still
    # readable but tools-only metadata gone).
    options.name_IDs = ['*']
    options.name_legacy = True

    subsetter = Subsetter(options=options)
    subsetter.populate(text=characters)
    subsetter.subset(font)
    font.flavor = 'woff2'
    font.save(str(font_path))
    after = font_path.stat().st_size

    return {'before': before, 'after': after, 'chars': len(characters)}


def main():
    if not _DEPS_OK:
        print(f"⚠️  Font subsetting skipped — {_DEPS_ERROR}")
        print("   Install with: pip install 'fonttools[woff]'")
        sys.exit(0)

    site_dir = Path(sys.argv[1] if len(sys.argv) > 1 else 'public')
    font_path = site_dir / TARGET_FONT_REL

    # Always restore from the source-of-truth before subsetting so the
    # subset operates on a font with all glyphs available. Without this,
    # the deployed copy (potentially already-subsetted from a previous
    # build) would be re-subsetted in place — and any new character
    # appearing in a future heading would render as a `.notdef` box.
    repo_root = Path(__file__).resolve().parent.parent
    master_path = repo_root / MASTER_FONT_REL
    if not master_path.exists():
        print(f"⚠️  Source-of-truth font not found at {master_path}")
        print(f"   Expected to seed {font_path} from {master_path} before subsetting.")
        sys.exit(0)
    font_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(master_path, font_path)

    print(f"🔤 Subsetting {font_path.name} (seeded from {master_path.relative_to(repo_root)})")
    used = collect_chars(site_dir)
    full_set = ''.join(sorted(used | set(SAFETY_PAD)))
    print(f"   Used chars (in headings):  {len(used)}")
    print(f"   With safety pad:           {len(full_set)}")

    try:
        stats = subset_font(font_path, full_set)
    except Exception as e:
        print(f"❌ Failed to subset {font_path.name}: {e}")
        sys.exit(1)

    saved = stats['before'] - stats['after']
    pct = saved / stats['before'] * 100 if stats['before'] else 0
    print(f"\n✅ {font_path.name}:")
    print(f"   {stats['before']:>7} bytes → {stats['after']:>7} bytes")
    print(f"   Saved {saved} bytes ({pct:.1f}% reduction)")


if __name__ == '__main__':
    main()
