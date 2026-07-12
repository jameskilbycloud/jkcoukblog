"""Tests for the unused-CSS remover's dynamic allowlists.

The optimizer decides "is this selector used?" from the served HTML, which
can't see classes/ids that JavaScript creates at runtime. Regressions here
are silent — the rule just never ships (that's how the #blog-search-input
placeholder styling from the search restyle disappeared).
"""

from optimize_css import CSSOptimizer


def _used(selector, used_selectors=frozenset()):
    return CSSOptimizer()._is_selector_used(selector, used_selectors)


def test_dynamic_ids_survive_purge():
    # search.js injects these ids after load — they never appear in HTML.
    assert _used('#blog-search-input::placeholder') is True
    assert _used('#blog-search-input::-webkit-search-cancel-button') is True
    assert _used('#blog-search-container') is True


def test_unknown_id_is_still_dropped():
    assert _used('#no-such-element') is False


def test_dynamic_classes_survive_purge():
    assert _used('.show-drawer') is True
    assert _used('.header-is-fixed .site-header', {'.site-header'}) is True


def test_static_selectors_follow_html_usage():
    assert _used('.present', {'.present'}) is True
    assert _used('.absent') is False
    # Pure element selectors are always kept.
    assert _used('p > a') is True
