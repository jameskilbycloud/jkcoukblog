"""Grouped API endpoints must be byte-stable between builds.

/api/categories/*.json, /api/tags/*.json and /api/archive/*.json used to emit
posts in Path.glob() order — filesystem order, which is not stable across
builds. The content was never wrong, just shuffled, so nothing failed: the
only symptom was that every deploy rewrote the endpoints. On 2026-08-09 that
was 32 category and 13 archive endpoints churning 13,234 lines (against
13,234 deletions — a pure permutation) for zero content change, plus their
Brotli/Gzip sidecars and a needless KV re-upload of the search index.

These tests pin the emitted order rather than the iteration order, so the
endpoints stay stable however the directory happens to be walked.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

pytest.importorskip('yaml')
from markdown_api import MarkdownAPIGenerator, _newest_first  # noqa: E402


POSTS = [
    # (slug, date, categories, tags)
    ('oldest-post', '2019-03-01T09:00:00Z', ['Homelab'], ['zfs']),
    ('middle-post', '2022-07-14T18:30:00Z', ['Homelab', 'VMware'], ['zfs', 'vsan']),
    ('newest-post', '2026-01-05T07:15:00Z', ['VMware'], ['vsan']),
    # Same timestamp as middle-post — the slug tiebreaker has to decide, or
    # the order is left to sort stability over an unstable input.
    ('middle-post-duplicate-date', '2022-07-14T18:30:00Z', ['Homelab'], ['zfs']),
]


def _write_corpus(root: Path, order):
    """Write the markdown corpus, creating files in the given order.

    Creation order is what drives filesystem walk order on most filesystems,
    so writing the same corpus in two different orders is how these tests
    reproduce the original bug.
    """
    posts_dir = root / 'posts'
    posts_dir.mkdir(parents=True, exist_ok=True)
    by_slug = {p[0]: p for p in POSTS}
    for slug in order:
        _, date, categories, tags = by_slug[slug]
        frontmatter = {
            'title': slug.replace('-', ' ').title(),
            'description': f'Description for {slug}',
            'date': date,
            'modified': date,
            'categories': categories,
            'tags': tags,
            'url': f'https://jameskilby.co.uk/{slug}/',
        }
        lines = ['---']
        for key, value in frontmatter.items():
            if isinstance(value, list):
                lines.append(f'{key}:')
                lines.extend(f'  - {item}' for item in value)
            else:
                lines.append(f'{key}: "{value}"')
        lines += ['---', '', f'Body text for {slug}.', '']
        (posts_dir / f'{slug}.md').write_text('\n'.join(lines), encoding='utf-8')


def _generate(tmp_path: Path, order, label: str) -> dict:
    """Generate the API from a corpus written in `order`; return {path: text}."""
    markdown_dir = tmp_path / label / 'markdown'
    api_dir = tmp_path / label / 'api'
    _write_corpus(markdown_dir, order)
    MarkdownAPIGenerator(markdown_dir, api_dir).generate_api()
    return {
        str(p.relative_to(api_dir)): p.read_text(encoding='utf-8')
        for p in sorted(api_dir.rglob('*.json'))
    }


def test_newest_first_orders_by_date_then_slug():
    posts = [
        {'slug': 'b', 'date': '2020-01-01T00:00:00Z'},
        {'slug': 'a', 'date': '2026-01-01T00:00:00Z'},
        {'slug': 'c', 'date': '2020-01-01T00:00:00Z'},
    ]
    assert [p['slug'] for p in _newest_first(posts)] == ['a', 'b', 'c']


def test_newest_first_tolerates_missing_dates():
    """A post with no date must sort last, not raise — the archive endpoint
    already logs and skips unparseable dates, and the grouped endpoints
    shouldn't be the thing that takes the build down."""
    posts = [
        {'slug': 'no-date'},
        {'slug': 'dated', 'date': '2021-01-01T00:00:00Z'},
        {'slug': 'null-date', 'date': None},
    ]
    assert [p['slug'] for p in _newest_first(posts)] == ['dated', 'no-date', 'null-date']


# /api/index.json carries a `generated: datetime.now()` field, so it is
# rewritten every build by construction and can't be compared byte-for-byte.
# That is a separate (and much smaller) source of churn — one file plus its
# sidecars — left alone here because the field is part of the published API
# surface, not an accident of iteration order.
TIMESTAMPED = {'index.json'}


def test_output_is_identical_regardless_of_walk_order(tmp_path, monkeypatch):
    """The regression itself: same corpus, different walk order, same bytes.

    Creation order alone doesn't reliably change the walk order — on APFS
    these fixtures come back identically ordered either way, so a test built
    only on creation order passes whether the bug is fixed or not. Patching
    glob for the second run reproduces a different walk on any filesystem.
    """
    natural = _generate(tmp_path, [p[0] for p in POSTS], 'natural')

    original = Path.glob
    monkeypatch.setattr(
        Path, 'glob',
        lambda self, pattern, *a, **kw: iter(
            sorted(original(self, pattern, *a, **kw), reverse=True)
        ),
    )
    walked_backwards = _generate(tmp_path, [p[0] for p in POSTS], 'backwards')

    assert natural.keys() == walked_backwards.keys()
    differing = [
        name for name in natural
        if name not in TIMESTAMPED and natural[name] != walked_backwards[name]
    ]
    assert not differing, f'endpoints differ with walk order: {differing}'


def test_only_the_timestamped_index_is_allowed_to_churn(tmp_path):
    """Pin the exemption so it stays one known file rather than a growing
    list of things quietly excused from determinism."""
    api = _generate(tmp_path, [p[0] for p in POSTS], 'exemption')
    for name in TIMESTAMPED:
        assert name in api, f'{name} is exempted but no longer generated'
        assert 'generated' in json.loads(api[name])


def test_category_posts_are_newest_first(tmp_path):
    api = _generate(tmp_path, [p[0] for p in POSTS], 'cats')
    homelab = json.loads(api['categories/homelab.json'])
    assert [p['slug'] for p in homelab['posts']] == [
        'middle-post',
        'middle-post-duplicate-date',
        'oldest-post',
    ]


def test_tag_posts_are_newest_first(tmp_path):
    api = _generate(tmp_path, [p[0] for p in POSTS], 'tags')
    zfs = json.loads(api['tags/zfs.json'])
    assert [p['slug'] for p in zfs['posts']] == [
        'middle-post',
        'middle-post-duplicate-date',
        'oldest-post',
    ]


def test_archive_posts_are_newest_first(tmp_path):
    api = _generate(tmp_path, [p[0] for p in POSTS], 'archive')
    july = json.loads(api['archive/2022-07.json'])
    assert [p['slug'] for p in july['posts']] == [
        'middle-post',
        'middle-post-duplicate-date',
    ]


def test_index_endpoints_are_slug_sorted(tmp_path):
    api = _generate(tmp_path, [p[0] for p in POSTS], 'indexes')
    categories = json.loads(api['categories/index.json'])
    tags = json.loads(api['tags/index.json'])
    assert [c['slug'] for c in categories] == sorted(c['slug'] for c in categories)
    assert [t['slug'] for t in tags] == sorted(t['slug'] for t in tags)


def test_grouped_endpoints_carry_every_post(tmp_path):
    """Sorting must not drop or duplicate anything."""
    api = _generate(tmp_path, [p[0] for p in POSTS], 'coverage')
    from_categories = set()
    for name, text in api.items():
        if name.startswith('categories/') and not name.endswith('index.json'):
            from_categories.update(p['slug'] for p in json.loads(text)['posts'])
    assert from_categories == {p[0] for p in POSTS}
