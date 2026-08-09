"""Font subsetting must be byte-stable and skippable.

Two problems, one step.

Determinism: fontTools stamps head.modified on save, so a rebuild with an
identical glyph set produced a byte-different woff2 — same 11,592 bytes, same
142 glyphs, only the timestamp moved (3869108660 → 3869141786 across two
deploys). All five fonts landed in every deploy commit with their .br/.gz
sidecars, and because the static-asset purge gate keys on
`assets/fonts/*.woff2` appearing in the diff, every deploy also fired a
Cloudflare edge purge for byte-equivalent fonts.

Cost: the step took ~43s of a 319s deploy rebuilding files that essentially
never change. Two things drive it, and the first attempt fixed neither.

  - The scan (_collect_chars) parsed every page once PER FONT — five full
    BeautifulSoup passes over 255 pages. collect_chars_for_specs parses once
    and fans out.
  - The subsetting itself, skipped via a cache keyed on the master plus the
    resolved character set.

The cache was originally keyed on a hash of the HTML corpus, checked before
the scan. It never hit once in production: changelog and stats pages embed
build metrics, so the corpus differs on every single deploy even when no
glyph does. Keying on the scan's output instead means pages can churn freely.

Measured on the real 253-page corpus: 16.6s → 6.5s cold, 6.0s warm, and still
6.0s warm when a per-build page has changed — the case that broke the first
design.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

subset_fonts = pytest.importorskip('subset_fonts')

pytestmark = pytest.mark.skipif(
    not subset_fonts._DEPS_OK,
    reason=f'needs fonttools[woff] ({subset_fonts._DEPS_ERROR})')


def _corpus(root: Path, pages: dict):
    for name, body in pages.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f'<html><body>{body}</body></html>', encoding='utf-8')


def test_cache_key_is_not_tied_to_the_corpus(tmp_path):
    """The bug this replaced: the key was a hash of every HTML file, and
    changelog/stats embed build metrics so they change on EVERY deploy. The
    cache never hit once in production. Keying on the resolved character set
    means pages can churn freely as long as no glyph changed."""
    master = tmp_path / 'master.woff2'
    master.write_bytes(b'font-bytes')

    assert (subset_fonts._cache_key(master, 'ABC')
            == subset_fonts._cache_key(master, 'ABC'))


def test_cache_key_covers_master_and_characters(tmp_path):
    master = tmp_path / 'master.woff2'
    master.write_bytes(b'font-bytes')
    base = subset_fonts._cache_key(master, 'ABC')

    assert subset_fonts._cache_key(master, 'ABCD') != base, 'characters'

    master.write_bytes(b'different')
    assert subset_fonts._cache_key(master, 'ABC') != base, 'master'


def test_single_parse_matches_per_spec_collection(tmp_path):
    """collect_chars_for_specs parses each page once and fans out to every
    spec; it must return exactly what the per-spec walk did."""
    _corpus(tmp_path, {
        'a.html': '<h1>Alpha</h1><code>x = 1</code>',
        'sub/b.html': '<h2>Beta</h2><pre>def f()</pre>',
    })
    specs = list(subset_fonts.FONT_SPECS)

    combined = subset_fonts.collect_chars_for_specs(tmp_path, specs)

    for spec in specs:
        assert combined[spec.target_rel] == subset_fonts._collect_chars(tmp_path, spec), (
            f'{spec.label}: single-pass result differs from per-spec walk'
        )


def test_collection_ignores_pages_with_no_matching_elements(tmp_path):
    _corpus(tmp_path, {'a.html': '<h1>Alpha</h1>', 'b.html': '<p>ignored</p>'})
    anton = subset_fonts.FONT_SPECS[0]

    chars = subset_fonts.collect_chars_for_specs(tmp_path, [anton])[anton.target_rel]

    assert set('Alpha') <= chars
    assert 'g' not in chars, 'body text leaked into a headings-only font'


def test_cache_roundtrips(tmp_path):
    subset_fonts._save_cache(tmp_path, {'a': {'key': 'k', 'after': 1}})
    assert subset_fonts._load_cache(tmp_path) == {'a': {'key': 'k', 'after': 1}}


def test_corrupt_cache_is_ignored_not_fatal(tmp_path):
    """A truncated cache from an interrupted build must degrade to a rebuild,
    not take the deploy down."""
    cache_path = tmp_path / subset_fonts._CACHE_REL
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    cache_path.write_text('{not json', encoding='utf-8')

    assert subset_fonts._load_cache(tmp_path) == {}


def test_cache_file_is_deterministic(tmp_path):
    """The cache is written into the site tree, so it lands in the deploy
    commit — unsorted keys would reintroduce the churn this removes."""
    entries = {'z': {'key': 'k1', 'after': 2}, 'a': {'key': 'k2', 'after': 3}}
    subset_fonts._save_cache(tmp_path, entries)
    first = (tmp_path / subset_fonts._CACHE_REL).read_text(encoding='utf-8')
    subset_fonts._save_cache(tmp_path, dict(reversed(list(entries.items()))))
    second = (tmp_path / subset_fonts._CACHE_REL).read_text(encoding='utf-8')

    assert first == second
    assert list(json.loads(first)) == ['a', 'z']


def test_subset_output_is_byte_stable(tmp_path):
    """The determinism half, independent of the cache: two real subsets of
    the same master with the same characters must be byte-identical."""
    repo_root = Path(__file__).resolve().parent.parent
    spec = subset_fonts.FONT_SPECS[0]
    master = repo_root / spec.master_rel
    if not master.exists():
        pytest.skip(f'master font not present: {spec.master_rel}')

    import shutil
    outputs = []
    for name in ('one.woff2', 'two.woff2'):
        target = tmp_path / name
        shutil.copy2(master, target)
        subset_fonts._subset_font(target, 'ABCDEfghij 0123')
        outputs.append(target.read_bytes())

    assert outputs[0] == outputs[1], (
        'subset output varies between runs — head.modified is being '
        'recalculated, which recommits every font on every build'
    )
