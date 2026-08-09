"""search-index.json must be byte-stable between builds.

generate_search_index() walked output_dir.rglob('*.html'), which yields
filesystem order — not stable across builds. The same pages came out in a
different order every deploy, rewriting search-index.json and its .min
sibling (and re-uploading the index to Workers KV) for no content change.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

from wp_to_static_generator import WordPressStaticGenerator  # noqa: E402

# The indexer skips anything under 50 words as a navigation page.
BODY = ' '.join(f'word{i}' for i in range(80))

PAGES = ['zebra', 'alpha', 'middle', 'beta']


def _page(slug: str) -> str:
    return (
        f'<html><head><title>{slug} - James Kilby</title>'
        f'<meta name="description" content="Description for {slug}">'
        f'</head><body><main><p>{slug} {BODY}</p></main></body></html>'
    )


def _build(root: Path, order) -> list:
    """Write the pages in `order`, index them, return the index entries."""
    for slug in order:
        page_dir = root / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / 'index.html').write_text(_page(slug), encoding='utf-8')

    generator = WordPressStaticGenerator(
        'https://wordpress.example',
        'test-token',
        str(root),
        'https://example.com',
        use_incremental=False,
    )
    generator.generate_search_index()
    return json.loads((root / 'search-index.json').read_text(encoding='utf-8'))


def test_index_order_is_independent_of_walk_order(tmp_path, monkeypatch):
    """Creation order alone doesn't reliably change rglob's order — on APFS
    both corpora come back identically ordered, so the test would pass with
    the bug present. Patching rglob for the second build reproduces a
    different walk on any filesystem."""
    natural = _build(tmp_path / 'natural', PAGES)

    original = Path.rglob
    monkeypatch.setattr(
        Path, 'rglob',
        lambda self, pattern, *a, **kw: iter(
            sorted(original(self, pattern, *a, **kw), reverse=True)
        ),
    )
    walked_backwards = _build(tmp_path / 'backwards', PAGES)

    assert [e['url'] for e in natural] == [e['url'] for e in walked_backwards]


def test_index_is_path_sorted(tmp_path):
    entries = _build(tmp_path / 'sorted', PAGES)
    urls = [e['url'] for e in entries]
    assert urls == sorted(urls), f'expected path-sorted entries, got {urls}'


def test_min_variant_matches_the_full_index(tmp_path):
    """Both files are written from the same list; if they ever diverge the
    KV upload and the client-side search disagree about the corpus."""
    root = tmp_path / 'min'
    entries = _build(root, PAGES)
    minified = json.loads((root / 'search-index.min.json').read_text(encoding='utf-8'))
    assert minified == entries


def test_every_page_is_indexed(tmp_path):
    """Sorting must not drop entries."""
    entries = _build(tmp_path / 'coverage', PAGES)
    slugs = {e['url'].rstrip('/').rsplit('/', 1)[-1] for e in entries}
    assert slugs == set(PAGES)
