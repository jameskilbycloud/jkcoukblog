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

import hashlib
import json
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable
from bs4 import BeautifulSoup

# Records which master + character set produced each deployed subset, so a
# rebuild with both unchanged can skip the work. Sits under the site tree so
# it travels with the incremental seed from public/.
_CACHE_REL = 'assets/fonts/.subset-cache.json'

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
            '.jkr-eyebrow', '.jkr-topic-count',
            # .jkr-headline is the visible editorial headline — a <p> in Anton,
            # so it needs an explicit selector (not covered by the h1 tags).
            '.jkr-headline',
            # Slim-footer wordmark (Anton).
            '.jk-footer-name',
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
            # Homepage top band (Option B): strap, filter and stats ribbon all
            # render in JetBrains Mono.
            '.jkr-strap', '.jkr-filter', '.jkr-filter-label', '.jkr-ribbon',
            # Header brand subline + slim-footer copyright line.
            '.jk-brand-sub', '.jk-footer-copy',
        ),
        # '●' (U+25CF) the ribbon live marker; '©' (U+00A9) the footer copyright
        # — both outside ASCII, kept so they don't fall back to system mono.
        safety_pad=ASCII_PRINTABLE + TYPO_PAD + CODE_PAD + '●©',
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
    bad_selectors = set()
    for f in html_files:
        try:
            body = f.read_text(encoding='utf-8', errors='ignore')
        except Exception as e:
            print(f"   ⚠️  Skipping unreadable {f}: {e}")
            continue
        soup = BeautifulSoup(body, 'html.parser')
        for tag in spec.tag_selectors:
            for el in soup.find_all(tag):
                chars.update(el.get_text())
        for sel in spec.class_selectors:
            try:
                for el in soup.select(sel):
                    chars.update(el.get_text())
            except Exception as e:
                # Bad selector syntax shouldn't kill the whole subset run —
                # but a silently skipped selector means its characters are
                # missing from the subset and render as .notdef boxes. Warn
                # once per selector, not once per file.
                if sel not in bad_selectors:
                    bad_selectors.add(sel)
                    print(f"   ⚠️  Selector {sel!r} failed ({e}) — its glyphs "
                          f"will be missing from the subset unless covered "
                          f"by another selector")
                continue
    return chars


def _subset_font(font_path: Path, characters: str) -> dict:
    """Run fontTools' Subsetter against `font_path` in-place.

    Returns a dict with before/after sizes plus retained glyph count.
    Raises if fontTools can't open the file.
    """
    before = font_path.stat().st_size

    # recalcTimestamp=False pins the OpenType head.modified field. fontTools
    # otherwise stamps "now" on save, so a rebuild with an identical glyph set
    # produced a byte-different woff2: same 11,592 bytes, same 142 glyphs,
    # only head.modified moved (3869108660 → 3869141786 across two deploys).
    #
    # That cost more than a noisy diff. All five fonts landed in every deploy
    # commit with their .br/.gz sidecars, and because the static-asset purge
    # gate keys on `assets/fonts/*.woff2` appearing in the diff, every deploy
    # also fired a Cloudflare edge purge for fonts that were byte-equivalent.
    font = TTFont(str(font_path), recalcTimestamp=False)
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


def corpus_fingerprint(site_dir: Path) -> str:
    """Hash every HTML file that feeds character collection.

    Computed once per run and shared by all specs. This is what lets the
    cache be checked BEFORE _collect_chars rather than after: the character
    set is a pure function of (corpus, selectors), so an unchanged corpus
    means an unchanged character set without having to parse anything.

    Hashing the corpus costs a read; _collect_chars costs a BeautifulSoup
    parse of every page, once per font. On the real 253-page site that is
    16s — which is why checking the cache after it saved nothing measurable
    (16.1s → 16.0s) in the first version of this.
    """
    h = hashlib.blake2b(digest_size=16)
    for path in sorted(site_dir.rglob('*.html')):
        h.update(str(path.relative_to(site_dir)).encode('utf-8'))
        h.update(b'\0')
        h.update(path.read_bytes())
        h.update(b'\0')
    return h.hexdigest()


def _cache_key(master_path: Path, spec: 'FontSpec', corpus_hash: str) -> str:
    """Identity of a subset: the master, the selectors that choose glyphs
    from it, and the corpus those selectors run against.

    The selectors are part of the key so that editing FONT_SPECS invalidates
    the cache — otherwise a code change to which elements feed a font would
    silently keep serving the previous subset.
    """
    h = hashlib.blake2b(digest_size=16)
    h.update(master_path.read_bytes())
    h.update(b'\0')
    h.update(repr((spec.tag_selectors, spec.class_selectors,
                   spec.safety_pad)).encode('utf-8'))
    h.update(b'\0')
    h.update(corpus_hash.encode('ascii'))
    return h.hexdigest()


def _load_cache(site_dir: Path) -> dict:
    cache_path = site_dir / _CACHE_REL
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_cache(site_dir: Path, cache: dict) -> None:
    cache_path = site_dir / _CACHE_REL
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, indent=2, sort_keys=True),
                              encoding='utf-8')
    except OSError as e:
        print(f"⚠️  Could not write font subset cache: {e}")


def _process_one(repo_root: Path, site_dir: Path, spec: FontSpec,
                 corpus_hash: str, cache: dict) -> dict | None:
    """Restore master → target, collect chars, subset target.

    Whole step took ~43s of a 319s deploy (13.5%) rebuilding five files whose
    content essentially never changes — the Anton character set has been
    stable at ~87 glyphs. The cache check has to come before _collect_chars:
    that scan is the expensive part, not the subsetting.
    """
    master_path = _ensure_master(repo_root, site_dir, spec)
    if not master_path:
        return None

    font_path = site_dir / spec.target_rel
    font_path.parent.mkdir(parents=True, exist_ok=True)

    key = _cache_key(master_path, spec, corpus_hash)
    cached = cache.get(spec.target_rel)
    if (cached and cached.get('key') == key and font_path.exists()
            and font_path.stat().st_size == cached.get('after')):
        return {'label': spec.label, 'file': font_path.name,
                'before': cached.get('before', 0), 'after': cached['after'],
                'chars': cached.get('total_chars', 0),
                'used_chars': cached.get('used_chars', 0),
                'total_chars': cached.get('total_chars', 0), 'cached': True}

    used = _collect_chars(site_dir, spec)
    full_set = ''.join(sorted(used | set(spec.safety_pad)))

    shutil.copy2(master_path, font_path)

    try:
        stats = _subset_font(font_path, full_set)
    except Exception as e:
        print(f"❌ {spec.label}: failed to subset {font_path.name}: {e}")
        return None

    cache[spec.target_rel] = {'key': key, 'before': stats['before'],
                              'after': stats['after'],
                              'used_chars': len(used),
                              'total_chars': len(full_set)}

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

    corpus_hash = corpus_fingerprint(site_dir)
    cache = _load_cache(site_dir)

    results = []
    for spec in FONT_SPECS:
        print(f"\n   • {spec.label} ({spec.target_rel})")
        stats = _process_one(repo_root, site_dir, spec, corpus_hash, cache)
        if stats:
            saved = stats['before'] - stats['after']
            pct = saved / stats['before'] * 100 if stats['before'] else 0
            print(f"     used={stats['used_chars']} chars (+safety pad → {stats['total_chars']})")
            suffix = '  [cached — master + charset unchanged]' if stats.get('cached') else ''
            print(f"     {stats['before']:>7} → {stats['after']:>7} bytes "
                  f"({pct:.1f}% saved){suffix}")
            results.append(stats)

    _save_cache(site_dir, cache)

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
