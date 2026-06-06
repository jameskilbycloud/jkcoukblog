#!/usr/bin/env python3
"""
Subset woff2 fonts to the characters actually used in rendered HTML.

Five of the six self-hosted fonts ship full-size and are discovered by the
browser the instant `brutalist-theme.css` parses (the @font-face block is
inlined at the top of the stylesheet). On mobile this puts ~360 KB of
WOFF2 onto the LCP critical path — even with `font-display: optional`
the bytes are still fetched, they just don't end up rendered if late.

Per-font subsetting drops each to ~10–30 KB by keeping only the glyphs
that appear under that font's CSS selectors across every generated HTML
file, plus an ASCII printable + common typography safety pad so future
content additions don't render .notdef boxes.

How it works
------------
1. For every FontSpec in FONT_SPECS:
   a. Restore the deployed font from its source-of-truth master so we
      always operate on a fully-glyph font (idempotent: re-running
      against a previously-subsetted output would compound the strip
      and eventually leave us with nothing).
   b. Walk every *.html under site_dir and collect characters from the
      elements styled with this font (heading tags, monospace selectors,
      nav classes, etc.).
   c. Union with the safety pad and feed to fontTools' Subsetter.
   d. Write the subset woff2 back over the deployed file.

2. Anton is the original (preloaded) subset target — kept on the LCP path
   so its full Latin range is overkill. JetBrains Mono 400/700 and Space
   Grotesk 500/700 were added in June 2026 to reclaim ~310 KB on mobile
   that was sitting on the critical-request chain. Space Grotesk 400
   (body) is intentionally not subsetted — body text uses a much wider
   character set so the savings would be small and the .notdef risk
   higher.

Idempotent: outputs are written over the inputs, and each run begins by
restoring from the master so the in-place edit is safe across rebuilds.

Bootstrap: if a master file is missing under scripts/fonts/ but the
deployed file exists at the expected target, we treat the deployed file
as the master, copy it across, and proceed. This lets the script add new
fonts to FONT_SPECS without a separate "copy the master" commit.

Dependencies: fonttools[woff] (already pinned in requirements.txt for
the og:image generator).

Usage:
    python3 scripts/subset_fonts.py [site_dir]
"""

import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from bs4 import BeautifulSoup

try:
    from fontTools.subset import Subsetter, Options
    from fontTools.ttLib import TTFont
    _DEPS_OK = True
    _DEPS_ERROR = None
except ImportError as e:
    _DEPS_OK = False
    _DEPS_ERROR = str(e)


# ─────────────────────────── safety pads ────────────────────────────
# Standard ASCII printable (covers letters, digits, common punctuation).
ASCII_PRINTABLE = ''.join(chr(c) for c in range(0x20, 0x7F))
# Typography characters that might land in future content even if they
# aren't currently used. Adding ~30 of these costs <2 KB and saves the
# subset-output from rendering smart quotes / em-dashes / ellipsis as
# .notdef boxes when a future post adds a stray Unicode punctuation.
TYPO_PAD = "'\"…–—·•‘’“”«»"
# Common code glyphs that aren't in standard ASCII printable. Useful for
# any monospace font subset where future code might use them.
CODE_PAD = "→←↑↓⇒⇐⇔≈≠≤≥≡∞±°²³¬"


@dataclass
class FontSpec:
    """One self-hosted font's subset configuration.

    Attributes
    ----------
    label
        Human-readable name for log output.
    target_rel
        Path of the deployed font under `site_dir`, relative.
    master_rel
        Path of the un-subsetted source-of-truth font from the repo root.
        On bootstrap (master missing + target present) we'll copy the
        deployed file across so a new entry can be added without a
        separate seed commit.
    tag_selectors
        HTML tag names whose text contributes to the character pool.
    class_selectors
        CSS class selectors (BS4 .select-style strings) whose text
        contributes to the pool. Prefix with `.` for class, leave bare
        for descendant patterns like 'pre code'.
    safety_pad
        Characters always kept regardless of scan results.
    """

    label: str
    target_rel: str
    master_rel: str
    tag_selectors: tuple = ()
    class_selectors: tuple = ()
    safety_pad: str = ASCII_PRINTABLE + TYPO_PAD


# ───────────────────────────── fonts ────────────────────────────────
# Each FontSpec is processed independently — order doesn't matter for
# correctness but the log reads top-to-bottom in this order.
FONT_SPECS = (
    # Anton — preloaded, used for all heading text + a few UI labels.
    # See brutalist-theme.css line ~67. Original subset target.
    FontSpec(
        label='Anton 400',
        target_rel='assets/fonts/anton-v27-latin-400.woff2',
        master_rel='scripts/fonts/anton-v27-latin-400.woff2',
        tag_selectors=('h1', 'h2', 'h3', 'h4', 'h5', 'h6'),
        class_selectors=(
            '.site-title', '.entry-title',
            '.jkr-eyebrow', '.jkr-strap-meta', '.jkr-filter-label',
            '.jkr-topic-count', '.jkr-term',
        ),
    ),

    # JetBrains Mono 400 — code blocks + monospace UI labels (hero
    # category chips, hero meta line, terminal-style branding).
    # Includes a code-glyph safety pad so future code snippets using
    # arrow operators, ≤, etc. don't render as .notdef.
    FontSpec(
        label='JetBrains Mono 400',
        target_rel='assets/fonts/jetbrainsmono-v24-latin-400.woff2',
        master_rel='scripts/fonts/jetbrainsmono-v24-latin-400.woff2',
        tag_selectors=('code', 'pre', 'kbd', 'samp'),
        class_selectors=(
            '.wp-block-code',
            '.jkr-hero-cats', '.jkr-hero-cats span',
            '.jkr-hero-meta',
        ),
        safety_pad=ASCII_PRINTABLE + TYPO_PAD + CODE_PAD,
    ),

    # JetBrains Mono 700 — hero "LATEST" badge plus any bold inside
    # code blocks. Smallest character set on the site — the badge text
    # is hard-coded and meta labels rarely render in 700.
    FontSpec(
        label='JetBrains Mono 700',
        target_rel='assets/fonts/jetbrainsmono-v24-latin-700.woff2',
        master_rel='scripts/fonts/jetbrainsmono-v24-latin-700.woff2',
        class_selectors=(
            '.jkr-hero-badge',
        ),
        safety_pad=ASCII_PRINTABLE + TYPO_PAD + CODE_PAD,
    ),

    # Space Grotesk 500 — primary navigation menu items + dropdown
    # links. Small character set (menu labels only) so the subset
    # comes out tight.
    FontSpec(
        label='Space Grotesk 500',
        target_rel='assets/fonts/spacegrotesk-v22-latin-500.woff2',
        master_rel='scripts/fonts/spacegrotesk-v22-latin-500.woff2',
        class_selectors=(
            '.main-navigation a', '.menu-item a', '.nav-menu a',
            '.dropdown-nav-toggle',
        ),
    ),

    # Space Grotesk 700 — bold body text (<strong>, <b>, anything CSS-
    # styled to 700). Wider character set than the 500-weight but still
    # much narrower than body 400 — most posts don't have huge amounts
    # of bold prose.
    FontSpec(
        label='Space Grotesk 700',
        target_rel='assets/fonts/spacegrotesk-v22-latin-700.woff2',
        master_rel='scripts/fonts/spacegrotesk-v22-latin-700.woff2',
        tag_selectors=('strong', 'b'),
        class_selectors=(
            '.skip-link',
        ),
    ),

    # Space Grotesk 400 (body) intentionally NOT subsetted — body text
    # uses the whole Latin set and the savings would be small relative
    # to the .notdef risk for blockquoted comments or quoted strings.
)


def _collect_chars(site_dir: Path, spec: FontSpec) -> set:
    """Walk every HTML file and return the unique characters appearing
    inside elements styled with this font."""
    chars = set()
    html_files = list(site_dir.rglob('*.html'))
    for f in html_files:
        try:
            body = f.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        soup = BeautifulSoup(body, 'html.parser')
        for tag in spec.tag_selectors:
            for el in soup.find_all(tag):
                chars.update(el.get_text())
        for sel in spec.class_selectors:
            try:
                for el in soup.select(sel):
                    chars.update(el.get_text())
            except Exception:
                # Bad selector syntax shouldn't kill the whole subset run.
                continue
    return chars


def _subset_font(font_path: Path, characters: str) -> dict:
    """Run fontTools' Subsetter against `font_path` in-place.

    Returns a dict with before/after sizes plus retained glyph count.
    Raises if fontTools can't open the file.
    """
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


def _ensure_master(repo_root: Path, site_dir: Path, spec: FontSpec) -> Path | None:
    """Locate the master font, bootstrapping from the deployed copy if
    needed.

    Returns the master Path, or None if no master can be obtained (in
    which case the caller should skip this spec — no font shipped at
    all is worse than shipping the un-subsetted original).
    """
    master_path = repo_root / spec.master_rel
    target_path = site_dir / spec.target_rel
    if master_path.exists():
        return master_path
    if target_path.exists():
        # First-run bootstrap: treat the currently-deployed font as the
        # source of truth and copy it across. Future runs will read from
        # master so re-subsetting can't compound.
        master_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(target_path, master_path)
        print(f"   ↪ bootstrapped master {spec.master_rel} from deployed font")
        return master_path
    print(f"   ⚠️  {spec.label}: master not found at {spec.master_rel} "
          "and no deployed copy to bootstrap from — skipping")
    return None


def _process_one(repo_root: Path, site_dir: Path, spec: FontSpec) -> dict | None:
    """Restore master → target, collect chars, subset target."""
    master_path = _ensure_master(repo_root, site_dir, spec)
    if not master_path:
        return None

    font_path = site_dir / spec.target_rel
    font_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(master_path, font_path)

    used = _collect_chars(site_dir, spec)
    full_set = ''.join(sorted(used | set(spec.safety_pad)))

    try:
        stats = _subset_font(font_path, full_set)
    except Exception as e:
        print(f"❌ {spec.label}: failed to subset {font_path.name}: {e}")
        return None

    stats['label'] = spec.label
    stats['file'] = font_path.name
    stats['used_chars'] = len(used)
    stats['total_chars'] = len(full_set)
    return stats


def main():
    if not _DEPS_OK:
        print(f"⚠️  Font subsetting skipped — {_DEPS_ERROR}")
        print("   Install with: pip install 'fonttools[woff]'")
        sys.exit(0)

    site_dir = Path(sys.argv[1] if len(sys.argv) > 1 else 'public')
    repo_root = Path(__file__).resolve().parent.parent

    html_count = len(list(site_dir.rglob('*.html')))
    print(f"🔤 Subsetting {len(FONT_SPECS)} fonts against {html_count} HTML files in {site_dir}")

    results = []
    for spec in FONT_SPECS:
        print(f"\n   • {spec.label} ({spec.target_rel})")
        stats = _process_one(repo_root, site_dir, spec)
        if stats:
            saved = stats['before'] - stats['after']
            pct = saved / stats['before'] * 100 if stats['before'] else 0
            print(f"     used={stats['used_chars']} chars (+safety pad → {stats['total_chars']})")
            print(f"     {stats['before']:>7} → {stats['after']:>7} bytes ({pct:.1f}% saved)")
            results.append(stats)

    if not results:
        print("\n⚠️  No fonts were subsetted.")
        return

    total_before = sum(r['before'] for r in results)
    total_after = sum(r['after'] for r in results)
    total_saved = total_before - total_after
    pct = total_saved / total_before * 100 if total_before else 0
    print(f"\n✅ Total: {total_before/1024:.1f} KB → {total_after/1024:.1f} KB "
          f"({total_saved/1024:.1f} KB saved, {pct:.1f}%)")


if __name__ == '__main__':
    main()
