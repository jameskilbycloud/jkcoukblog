"""Tests for the JS minifier.

WP-Optimize's minify feature was the only thing minifying JavaScript; it was
disabled because its cache path embedded a timestamp that rewrote every page
on each WordPress-side rebuild. scripts/minify_js.py replaces it. The two
behaviours that matter beyond "it makes files smaller" are both here:
_worker.js must never be touched, and files must not be rewritten when
minification doesn't actually help.
"""

import pytest

pytest.importorskip("rjsmin", reason="rjsmin is required for JS minification")

from minify_js import JSMinifier  # noqa: E402  (must follow importorskip)

UNMINIFIED = """
// a comment that should not survive
function greet(name) {
    var message = "hello " + name;   /* inline comment */
    return message;
}
"""


def _site(tmp_path, files):
    for rel, content in files.items():
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
    return tmp_path


def test_minifies_and_shrinks(tmp_path):
    site = _site(tmp_path, {'js/app.js': UNMINIFIED})
    JSMinifier(site).minify_all()

    out = (site / 'js/app.js').read_text()
    assert len(out) < len(UNMINIFIED)
    assert 'a comment that should not survive' not in out
    # Behaviour must be preserved, not just bytes removed.
    assert 'function greet' in out
    assert '"hello "' in out


def test_worker_js_is_never_touched(tmp_path):
    """_worker.js is the Cloudflare worker: not browser-served, and
    stamp_worker_manifest.py finds its injection points via comment markers
    a minifier would strip."""
    worker = '/*__PATH_MANIFEST_START__*/null/*__PATH_MANIFEST_END__*/\n' + UNMINIFIED
    site = _site(tmp_path, {'_worker.js': worker})

    JSMinifier(site).minify_all()

    assert (site / '_worker.js').read_text() == worker


def test_no_rewrite_when_already_minimal(tmp_path):
    """Rewriting for a zero-byte gain would churn the content hash and force
    a pointless recompression, defeating the incremental builder."""
    already = 'var a=1;'
    site = _site(tmp_path, {'js/tiny.js': already})

    minifier = JSMinifier(site)
    minifier.minify_all()

    assert (site / 'js/tiny.js').read_text() == already
    assert minifier.files_minified == 0
    assert minifier.files_skipped == 1


def test_unparseable_file_is_skipped_not_fatal(tmp_path):
    """A single bad asset should ship unminified rather than fail the build."""
    site = _site(tmp_path, {'js/ok.js': UNMINIFIED})
    (site / 'js/bad.js').write_bytes(b'\xff\xfe\x00 not utf-8')

    minifier = JSMinifier(site)
    minifier.minify_all()

    assert minifier.files_minified == 1
    assert minifier.files_skipped == 1


def test_reports_bytes_saved(tmp_path):
    site = _site(tmp_path, {'js/app.js': UNMINIFIED})
    minifier = JSMinifier(site)
    minifier.minify_all()

    assert minifier.bytes_saved > 0
    assert minifier.files_minified == 1
