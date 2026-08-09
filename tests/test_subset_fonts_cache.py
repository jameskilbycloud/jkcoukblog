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
never change. The expensive half is _collect_chars parsing every page once per
font — not the subsetting — so the cache has to be consulted before that scan.
Measured on the real 253-page corpus: 16.6s uncached, 0.3s cached. Checking
the cache after the scan (the obvious placement) saved nothing: 16.1s → 16.0s.
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


def test_corpus_fingerprint_tracks_content(tmp_path):
    _corpus(tmp_path, {'a.html': '<h1>Alpha</h1>'})
    first = subset_fonts.corpus_fingerprint(tmp_path)

    assert subset_fonts.corpus_fingerprint(tmp_path) == first, 'not stable'

    _corpus(tmp_path, {'a.html': '<h1>Beta</h1>'})
    assert subset_fonts.corpus_fingerprint(tmp_path) != first, 'content ignored'


def test_corpus_fingerprint_tracks_added_and_removed_pages(tmp_path):
    _corpus(tmp_path, {'a.html': '<h1>A</h1>'})
    one = subset_fonts.corpus_fingerprint(tmp_path)

    _corpus(tmp_path, {'b.html': '<h1>B</h1>'})
    two = subset_fonts.corpus_fingerprint(tmp_path)
    assert two != one, 'a new page must invalidate'

    (tmp_path / 'b.html').unlink()
    assert subset_fonts.corpus_fingerprint(tmp_path) == one, 'removal must too'


def test_corpus_fingerprint_ignores_non_html(tmp_path):
    """Only HTML feeds character collection — images and fonts churning
    must not force a re-subset."""
    _corpus(tmp_path, {'a.html': '<h1>A</h1>'})
    before = subset_fonts.corpus_fingerprint(tmp_path)

    (tmp_path / 'notes.txt').write_text('anything', encoding='utf-8')
    (tmp_path / 'img.bin').write_bytes(b'\x00\x01')

    assert subset_fonts.corpus_fingerprint(tmp_path) == before


def test_cache_key_covers_master_selectors_and_corpus(tmp_path):
    """All three inputs decide the output; a key missing any of them serves
    a stale subset after that input changes."""
    master = tmp_path / 'master.woff2'
    master.write_bytes(b'font-bytes')
    spec = subset_fonts.FONT_SPECS[0]

    base = subset_fonts._cache_key(master, spec, 'corpus-1')

    assert subset_fonts._cache_key(master, spec, 'corpus-2') != base, 'corpus'

    master.write_bytes(b'different-font-bytes')
    assert subset_fonts._cache_key(master, spec, 'corpus-1') != base, 'master'

    master.write_bytes(b'font-bytes')
    other = subset_fonts.FontSpec(
        label=spec.label, target_rel=spec.target_rel, master_rel=spec.master_rel,
        tag_selectors=spec.tag_selectors + ('h7',),
        class_selectors=spec.class_selectors, safety_pad=spec.safety_pad)
    assert subset_fonts._cache_key(master, other, 'corpus-1') != base, 'selectors'


def test_cache_key_is_stable_for_identical_inputs(tmp_path):
    master = tmp_path / 'master.woff2'
    master.write_bytes(b'font-bytes')
    spec = subset_fonts.FONT_SPECS[0]

    assert (subset_fonts._cache_key(master, spec, 'c')
            == subset_fonts._cache_key(master, spec, 'c'))


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
