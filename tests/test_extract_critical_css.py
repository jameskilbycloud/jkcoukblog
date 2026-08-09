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


def test_empty_extraction_still_converts_to_preload(tmp_path):
    # A page whose async-eligible sheets match no critical selectors must
    # STILL get them converted to preload — the old early-return on empty
    # critical CSS left such pages render-blocking forever.
    (tmp_path / 'widgets.css').write_text('.only-footer-thing{color:red}',
                                          encoding='utf-8')
    page = tmp_path / 'index.html'
    page.write_text(
        '<html><head><link rel="stylesheet" href="/widgets.css"></head>'
        '<body><main><h1>t</h1></main></body></html>',
        encoding='utf-8')
    ex = CriticalCSSExtractor()
    ex.public_dir = tmp_path

    assert ex.process_file(page) is True
    out = page.read_text(encoding='utf-8')
    assert 'rel="preload"' in out
    assert 'noscript' in out


def test_convert_css_to_preload_is_idempotent(tmp_path):
    # Running process_file twice must report no change the second time —
    # a strip+identical-re-add of noscripts is not a modification, so the
    # pipeline doesn't rewrite (and recompress) every file every build.
    (tmp_path / 'widgets.css').write_text('.x{color:red}', encoding='utf-8')
    page = tmp_path / 'index.html'
    page.write_text(
        '<html><head><link rel="stylesheet" href="/widgets.css"></head>'
        '<body><main><h1>t</h1></main></body></html>',
        encoding='utf-8')
    ex = CriticalCSSExtractor()
    ex.public_dir = tmp_path

    assert ex.process_file(page) is True
    first_pass = page.read_text(encoding='utf-8')
    assert ex.process_file(page) is False
    assert page.read_text(encoding='utf-8') == first_pass


def test_excluded_tuple_is_single_source():
    # RENDER_BLOCKING_CSS drives both the extraction skip and the preload
    # conversion — guard against the two lists drifting apart again by
    # checking the conversion path leaves a render-blocking sheet alone.
    from bs4 import BeautifulSoup as BS
    soup = BS('<html><head>'
              '<link rel="stylesheet" href="/assets/css/brutalist-theme.css">'
              '</head><body></body></html>', 'html.parser')
    ex = CriticalCSSExtractor()
    assert ex._convert_css_to_preload(soup) is False
    link = soup.find('link')
    assert link['rel'] == ['stylesheet']


# ── href resolution ──────────────────────────────────────────────────────
# At the point the transformer runs, stylesheet hrefs are absolute
# (`https://jameskilby.co.uk/wp-content/...`) — convert_to_staging.py doesn't
# rewrite them to relative until "Prepare output for deployment", long after.
# _resolve_css_path used to do a bare lstrip('/'), which doesn't touch a
# scheme, so the lookup missed and the sheet contributed nothing.
#
# It failed silently: an unresolvable sheet and a sheet with nothing above the
# fold both yield zero rules. _convert_css_to_preload then deferred those same
# sheets, so header.min.css (13.7 KB) and content.min.css (19.1 KB) loaded
# async with none of their above-fold rules inlined — 0.647 CLS and P73 on
# 2026-08-09. Same defect #146 fixed in html_transformer's inliner.

def _extract_with_href(css, selectors, tmp_path, href):
    (tmp_path / 'styles.css').write_text(css, encoding='utf-8')
    soup = BeautifulSoup(
        f'<html><head><link rel="stylesheet" href="{href}"></head>'
        '<body><main><h1>t</h1><p>x</p></main></body></html>',
        'html.parser')
    ex = CriticalCSSExtractor()
    ex.public_dir = tmp_path
    return ex._extract_matching_css_rules(soup, selectors)


def test_absolute_same_site_href_resolves(tmp_path):
    out = _extract_with_href('p{color:red}', {'p'}, tmp_path,
                             'https://jameskilby.co.uk/styles.css')
    assert 'color:red' in out, 'absolute same-site href did not resolve to disk'


def test_query_string_href_resolves(tmp_path):
    out = _extract_with_href('p{color:red}', {'p'}, tmp_path,
                             '/styles.css?ver=3.1.5')
    assert 'color:red' in out, 'cache-busting query string broke the disk lookup'


def test_absolute_href_with_query_resolves(tmp_path):
    out = _extract_with_href('p{color:red}', {'p'}, tmp_path,
                             'https://jameskilby.co.uk/styles.css?ver=3.1.5')
    assert 'color:red' in out


def test_href_form_does_not_change_the_output(tmp_path):
    """The real invariant. A full build and an incremental build see the same
    page with hrefs in different forms; if extraction depends on the form, the
    two builds emit different critical CSS for identical content — which is
    exactly the 4,621 vs 12,058 byte divergence measured before #148."""
    css = 'p{color:red}h1{margin:0}main{display:block}'
    outputs = {
        href: _extract_with_href(css, {'p', 'h1', 'main'}, tmp_path, href)
        for href in (
            '/styles.css',
            'styles.css',
            '/styles.css?ver=3.1.5',
            'https://jameskilby.co.uk/styles.css',
            'https://jameskilby.co.uk/styles.css?ver=3.1.5',
        )
    }
    distinct = set(outputs.values())
    assert len(distinct) == 1, (
        'critical CSS depends on href form: '
        + repr({h: len(o) for h, o in outputs.items()})
    )
    assert 'color:red' in distinct.pop()


def test_offsite_href_is_not_resolved(tmp_path):
    """normalize_self_href only strips our own origin — a third-party sheet
    must not be mapped onto a same-named local file."""
    (tmp_path / 'styles.css').write_text('p{color:red}', encoding='utf-8')
    out = _extract_with_href('p{color:red}', {'p'}, tmp_path,
                             'https://cdn.example.com/styles.css')
    assert out == ''


def test_deferred_sheets_have_their_rules_inlined(tmp_path):
    """End-to-end statement of the CLS guarantee: any sheet
    _convert_css_to_preload defers must have contributed its above-fold rules
    to the critical block first. A deferred sheet with no inlined rules is a
    layout shift."""
    (tmp_path / 'header.min.css').write_text(
        'header{height:80px}main{display:block}', encoding='utf-8')
    soup = BeautifulSoup(
        '<html><head>'
        '<link rel="stylesheet" href="https://jameskilby.co.uk/header.min.css">'
        '</head><body><header>h</header><main><h1>t</h1></main></body></html>',
        'html.parser')
    ex = CriticalCSSExtractor()
    ex.public_dir = tmp_path

    critical = ex._extract_critical_css(soup)
    deferred = ex._convert_css_to_preload(soup)

    assert deferred is True, 'sheet was not deferred — fixture no longer valid'
    assert 'height:80px' in critical, (
        'header.min.css was deferred without its above-fold rules inlined'
    )
