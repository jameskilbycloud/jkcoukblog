"""Tests for the incremental build cache: URL routing, change detection,
thread-safety, and the config/generator fingerprint invalidation."""

import json
import threading

import pytest

from incremental_builder import IncrementalBuilder


@pytest.fixture
def builder(tmp_path):
    return IncrementalBuilder(cache_file=str(tmp_path / 'cache.json'))


def test_cache_type_routing(builder):
    assert builder._get_cache_type('/2026/01/some-post/') == 'posts'
    assert builder._get_cache_type('/2026/01/some-post') == 'posts'
    assert builder._get_cache_type('/2026/01/') == 'pages'      # monthly archive
    assert builder._get_cache_type('/2026/') == 'pages'         # year archive
    assert builder._get_cache_type('/about-me/') == 'pages'
    assert builder._get_cache_type('/category/aws/') == 'pages'
    assert builder._get_cache_type('/tag/vmware/') == 'pages'
    assert builder._get_cache_type('/') == 'pages'


def test_has_changed_lifecycle(builder):
    url = '/2026/01/post/'
    assert builder.has_changed(url, 'h1', 'd1') is True          # never seen
    builder.mark_processed(url, 'h1', 'd1')
    assert builder.has_changed(url, 'h1', 'd1') is False         # unchanged
    assert builder.has_changed(url, 'h2', 'd1') is True          # content changed
    assert builder.has_changed(url, 'h1', 'd2') is True          # date changed


def test_mark_processed_is_thread_safe(builder):
    n_threads, per_thread = 8, 250

    def worker(start):
        for i in range(start, start + per_thread):
            builder.mark_processed(f'/2026/01/post-{i}/', f'h{i}', 'd')

    threads = [threading.Thread(target=worker, args=(k * per_thread,))
               for k in range(n_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(builder.cache['posts']) == n_threads * per_thread


def test_cache_survives_reload_with_same_fingerprint(tmp_path):
    cache_file = str(tmp_path / 'cache.json')
    b1 = IncrementalBuilder(cache_file=cache_file)
    b1.mark_processed('/2026/01/post/', 'h1', 'd1')
    b1.finalize_build()

    b2 = IncrementalBuilder(cache_file=cache_file)
    assert '/2026/01/post/' in b2.cache['posts']
    assert b2.cache.get('environment_fingerprint')


def test_fingerprint_mismatch_clears_cache(tmp_path):
    cache_file = tmp_path / 'cache.json'
    b1 = IncrementalBuilder(cache_file=str(cache_file))
    b1.mark_processed('/2026/01/post/', 'h1', 'd1')
    b1.finalize_build()

    data = json.loads(cache_file.read_text())
    data['environment_fingerprint'] = 'stale'
    cache_file.write_text(json.dumps(data))

    b2 = IncrementalBuilder(cache_file=str(cache_file))
    assert b2.cache['posts'] == {}


def test_legacy_cache_without_fingerprint_is_cleared(tmp_path):
    cache_file = tmp_path / 'cache.json'
    cache_file.write_text(json.dumps({
        'posts': {'/2026/01/x/': {'hash': 'h'}},
        'pages': {}, 'assets': {},
        'last_build_time': '2026-01-01T00:00:00',
        'last_full_build': None,
    }))
    b = IncrementalBuilder(cache_file=str(cache_file))
    assert b.cache['posts'] == {}
    assert b.cache.get('environment_fingerprint')


def test_remove_stale_entries(builder):
    builder.mark_processed('/2026/01/keep/', 'h', 'd')
    builder.mark_processed('/2026/01/drop/', 'h', 'd')
    removed = builder.remove_stale_entries({'/2026/01/keep/'})
    assert removed == 1
    assert '/2026/01/keep/' in builder.cache['posts']
    assert '/2026/01/drop/' not in builder.cache['posts']


def test_watermark_is_build_start_in_utc(tmp_path):
    # The modified_after watermark must be the time fetching BEGAN, not the
    # time the build finished — a post edited mid-build is older than an
    # end-of-build stamp and would be skipped forever. It must also carry
    # an explicit UTC offset so runner/WP timezone drift can't shift it.
    from datetime import datetime, timezone

    before = datetime.now(timezone.utc)
    b = IncrementalBuilder(cache_file=str(tmp_path / 'cache.json'))
    after_init = datetime.now(timezone.utc)

    b.finalize_build(is_full_build=True)

    stamp = datetime.fromisoformat(b.cache['last_build_time'])
    assert stamp.tzinfo is not None
    assert before <= stamp <= after_init  # start-of-build, not finalize time
    assert b.cache['last_full_build'] == b.cache['last_build_time']


def test_modified_after_param_subtracts_overlap(builder):
    from datetime import datetime

    param = builder._modified_after_param('2026-07-01T12:00:00+00:00')
    stamp = datetime.fromisoformat(param)
    assert stamp == datetime.fromisoformat('2026-07-01T11:55:00+00:00')


def test_modified_after_param_handles_legacy_naive_stamp(builder):
    # Pre-fix caches hold naive local-time stamps; they must parse (as
    # runner-local), gain an offset, and still get the overlap.
    from datetime import datetime, timedelta

    param = builder._modified_after_param('2026-07-01T12:00:00')
    stamp = datetime.fromisoformat(param)
    assert stamp.tzinfo is not None
    naive_local = datetime.fromisoformat('2026-07-01T12:00:00').astimezone()
    assert stamp == naive_local - timedelta(minutes=5)


def test_should_rebuild_archives_accepts_legacy_naive_stamp(builder):
    # A recent naive last_full_build must NOT force a rebuild — the old
    # naive-minus-aware TypeError path silently rebuilt archives every run.
    from datetime import datetime

    builder.cache['last_full_build'] = datetime.now().isoformat()
    assert builder.should_rebuild_archives() is False

    builder.cache['last_full_build'] = '2020-01-01T00:00:00+00:00'
    assert builder.should_rebuild_archives() is True
