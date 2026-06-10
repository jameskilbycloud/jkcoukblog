"""Tests for the typo-patch matching logic — the pure functions that decide
whether and how a find/replace lands in WP raw content."""

from apply_typo_patches import (
    apply_patches_to_content,
    slug_from_url,
    is_post_url,
)


def test_slug_from_url():
    assert slug_from_url('https://jameskilby.co.uk/2026/01/my-post/') == 'my-post'
    assert slug_from_url('https://jameskilby.co.uk/about-me/') == 'about-me'
    assert slug_from_url('https://jameskilby.co.uk/') == ''


def test_is_post_url():
    assert is_post_url('https://jameskilby.co.uk/2026/01/my-post/') is True
    assert is_post_url('https://jameskilby.co.uk/about-me/') is False


def test_exact_match_applies():
    raw = 'The quick brwon fox.'
    new, results = apply_patches_to_content(raw, [{'find': 'brwon', 'replace': 'brown'}])
    assert new == 'The quick brown fox.'
    assert results[0]['ok'] is True
    assert results[0]['matched_via'] == 'exact'


def test_missing_find_is_reported_not_silently_skipped():
    raw = 'Nothing to see here.'
    new, results = apply_patches_to_content(raw, [{'find': 'absent', 'replace': 'x'}])
    assert new == raw
    assert results[0]['ok'] is False
    assert 'not present' in results[0]['reason']


def test_ambiguous_find_refuses_bulk_replace():
    raw = 'dup text and dup text'
    new, results = apply_patches_to_content(raw, [{'find': 'dup text', 'replace': 'fixed'}])
    assert new == raw, 'must not replace when the find string is ambiguous'
    assert results[0]['ok'] is False


def test_smart_quote_normalisation_bridges_rendered_to_raw():
    # The audit captured rendered curly quotes; WP raw content has straight ones.
    raw = "It's a teh test."
    new, results = apply_patches_to_content(
        raw, [{'find': 'It’s a teh test.', 'replace': 'It’s a the test.'}])
    assert results[0]['ok'] is True
    assert results[0]['matched_via'] == 'normalised'
    # The replacement is re-transformed into the raw style (straight quote).
    assert new == "It's a the test."


def test_patches_apply_sequentially():
    raw = 'aa bb'
    new, results = apply_patches_to_content(raw, [
        {'find': 'aa', 'replace': 'cc'},
        {'find': 'cc bb', 'replace': 'done'},
    ])
    assert new == 'done'
    assert all(r['ok'] for r in results)
