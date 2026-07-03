"""Tests for critical-CSS extraction — above all that the size cap can never
produce unbalanced braces (the pre-2026-06 slice-at-15000-chars bug).

Critical CSS is extracted only from the external stylesheets that get
converted to async loading; inline <style> blocks and the render-blocking
sheets are already applied at first paint, so they're skipped (see
CriticalCSSExtractor.RENDER_BLOCKING_CSS). These tests therefore feed CSS via
an external <link>, which also exercises _resolve_css_path."""

from bs4 import BeautifulSoup

from extract_critical_css import CriticalCSSExtractor


def _brace_depth_ok(css: str) -> bool:
    depth = 0
    for ch in css:
        if ch == '{':
            depth += 1
        elif ch == '}':
            depth -= 1
        if depth < 0:
            return False
    return depth == 0


def _extract(css: str, selectors, tmp_path, file_path=None):
    """Write css to an external sheet, link it, and run the extractor."""
    (tmp_path / 'styles.css').write_text(css, encoding='utf-8')
    soup = BeautifulSoup(
        '<html><head><link rel="stylesheet" href="/styles.css"></head>'
        '<body><main><h1>t</h1><p>x</p></main></body></html>',
        'html.parser')
    ex = CriticalCSSExtractor()
    ex.public_dir = tmp_path
    return ex, ex._extract_matching_css_rules(soup, selectors, file_path)


def test_small_input_passes_through(tmp_path):
    ex, out = _extract('p{color:red}h1{margin:0}', {'p', 'h1'}, tmp_path)
    assert 'color:red' in out
    assert 'margin:0' in out
    assert ex.css_truncated == 0


def test_render_blocking_sheets_are_skipped(tmp_path):
    # brutalist-theme.css loads render-blocking, so its rules must NOT be
    # re-inlined into the critical block.
    (tmp_path / 'brutalist-theme.css').write_text('p{color:red}', encoding='utf-8')
    soup = BeautifulSoup(
        '<html><head><link rel="stylesheet" href="/brutalist-theme.css"></head>'
        '<body><main><p>x</p></main></body></html>',
        'html.parser')
    ex = CriticalCSSExtractor()
    ex.public_dir = tmp_path
    assert ex._extract_matching_css_rules(soup, {'p'}) == ''


def test_truncation_keeps_braces_balanced(tmp_path):
    # Enough rules to blow the cap, with the boundary landing inside @media.
    rules = ''.join(f'p{{padding:{i}px;color:#0{i % 10}{i % 10}}}' for i in range(300))
    media = '@media (max-width:600px){' + ''.join(f'h1{{margin:{i}px}}' for i in range(600)) + '}'
    ex, out = _extract(rules + media, {'p', 'h1'}, tmp_path, 'test.html')

    assert 0 < len(out) <= ex.max_critical_css
    assert _brace_depth_ok(out), 'truncated critical CSS has unbalanced braces'
    assert ex.css_truncated == 1


def test_media_query_rules_are_wrapped(tmp_path):
    ex, out = _extract('@media (max-width:600px){h1{margin:0}}', {'h1'}, tmp_path)
    assert '@media' in out
    assert _brace_depth_ok(out)


def test_keyframes_are_skipped(tmp_path):
    ex, out = _extract('@keyframes spin{from{opacity:0}to{opacity:1}}p{color:red}',
                       {'p'}, tmp_path)
    assert '@keyframes' not in out
    assert 'color:red' in out


def test_sheet_cache_reuses_parse_and_invalidates_on_rewrite(tmp_path):
    # One extractor instance processes every page — the tokenized sheet must
    # be parsed once and reused, but a rewritten file must not serve stale
    # nodes (keyed on mtime_ns + size).
    sheet = tmp_path / 't.css'
    sheet.write_text('h1{color:red}', encoding='utf-8')
    ex = CriticalCSSExtractor()
    ex.public_dir = tmp_path

    first = ex._get_sheet_nodes(sheet)
    assert first is ex._get_sheet_nodes(sheet), 'second read should hit the cache'

    # Different size guarantees a new fingerprint even on coarse mtime clocks.
    sheet.write_text('h2{margin:0;padding:0}', encoding='utf-8')
    fresh = ex._get_sheet_nodes(sheet)
    assert fresh is not first
    assert fresh[0][0] == 'h2'


def test_cached_extraction_matches_uncached(tmp_path):
    # _parse_css_rules (raw string path) and the cached sheet path must
    # produce identical output for the same CSS + selector set.
    css = 'p{color:red}@media (max-width:600px){h1{margin:0}.skip{x:1}}'
    ex, out = _extract(css, {'p', 'h1'}, tmp_path)
    direct = ''.join(
        ex._minify_css(r) for r in ex._parse_css_rules(css, {'p', 'h1'})
    )
    assert out == direct
