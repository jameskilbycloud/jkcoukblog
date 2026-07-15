"""Tests for the search-script injection + cache-busting in
wp_to_static_generator.

The generator copies /js/search.js and injects a single <script> reference
into every page. /js/search.js is served with a ~186-day max-age and no
version, so the reference carries a `?v=<content-hash>` cache-buster: the URL
changes only when the file's bytes change, so returning visitors pick up fixes
immediately while the long cache lifetime is preserved.

inject_search_script only touches self.output_dir, self._SEARCH_SCRIPT_TAG_RE
and self._search_script_version(), so we exercise it against a lightweight
stub rather than constructing the full (WordPress-dependent) generator.
"""

import types

import pytest

from wp_to_static_generator import WordPressStaticGenerator as G

RE = G._SEARCH_SCRIPT_TAG_RE
VER = 'abc123def456'
BODY = "<html><body><p>hi</p></body></html>"


def _tag(src):
    return f'<script src="{src}" data-cfasync="false"></script>'


def _seed(tag):
    return BODY.replace('</body>', f'{tag}\n</body>')


def _run(tmp_path, files, version=VER):
    for name, content in files.items():
        (tmp_path / name).write_text(content)
    stub = types.SimpleNamespace(
        output_dir=tmp_path,
        _SEARCH_SCRIPT_TAG_RE=RE,
        _search_script_version=lambda: version,
    )
    G.inject_search_script(stub)
    return {name: (tmp_path / name).read_text() for name in files}


def _count(html):
    return len(list(RE.finditer(html)))


def test_injects_versioned_tag_into_bare_page(tmp_path):
    out = _run(tmp_path, {'a.html': BODY})['a.html']
    assert _count(out) == 1
    assert f'/js/search.js?v={VER}' in out


def test_idempotent_when_version_current(tmp_path):
    seeded = _seed(_tag(f'/js/search.js?v={VER}'))
    out = _run(tmp_path, {'b.html': seeded})['b.html']
    assert out == seeded  # byte-identical, no rewrite


def test_idempotent_with_reordered_attributes(tmp_path):
    # html_transformer adds defer / data-cfasync before src; a current-version
    # tag must still be recognised so we don't rewrite it every build.
    tag = f'<script defer data-cfasync="false" src="/js/search.js?v={VER}"></script>'
    seeded = _seed(tag)
    out = _run(tmp_path, {'b.html': seeded})['b.html']
    assert out == seeded


def test_stale_version_is_replaced(tmp_path):
    stale = _seed(_tag('/js/search.js?v=0000deadbeef'))
    out = _run(tmp_path, {'c.html': stale})['c.html']
    assert _count(out) == 1
    assert '0000deadbeef' not in out
    assert f'?v={VER}' in out


def test_unversioned_legacy_tag_is_upgraded(tmp_path):
    legacy = _seed(_tag('/js/search.js'))
    out = _run(tmp_path, {'c.html': legacy})['c.html']
    assert _count(out) == 1
    assert f'?v={VER}' in out


def test_duplicates_collapse_to_single_current_tag(tmp_path):
    dup = BODY.replace(
        '</body>',
        _tag('/js/search.js')
        + '<script defer src="/js/search.js?v=oldish" data-cfasync="false"></script>\n</body>',
    )
    out = _run(tmp_path, {'d.html': dup})['d.html']
    assert _count(out) == 1
    assert f'?v={VER}' in out


def test_empty_version_falls_back_to_unversioned(tmp_path):
    out = _run(tmp_path, {'e.html': BODY}, version='')['e.html']
    assert _count(out) == 1
    assert 'src="/js/search.js"' in out
    assert '?v=' not in out


def test_version_helper_hashes_real_file():
    ver = G._search_script_version(types.SimpleNamespace())
    # 6-byte blake2b digest -> 12 hex chars; empty only if the file is missing.
    assert ver == '' or (len(ver) == 12 and all(c in '0123456789abcdef' for c in ver))
