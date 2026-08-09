"""Tests for critical-CSS extraction — above all that the size cap can never
produce unbalanced braces (the pre-2026-06 slice-at-15000-chars bug).

Critical CSS is extracted only from the external stylesheets that get
converted to async loading; inline <style> blocks and the render-blocking
sheets are already applied at first paint, so they're skipped (see
CriticalCSSExtractor.RENDER_BLOCKING_CSS). These tests therefore feed CSS via
an external <link>, which also exercises _resolve_css_path."""

import pytest
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


# ── cap invariant and truncation accounting ──────────────────────────────

def test_harvest_cap_cannot_trigger_externalisation():
    """max_critical_css above max_inline_critical would externalise every
    page's block into an extra render-blocking request — the opposite of what
    critical CSS is for, and enough to push pages past the 5/5 stylesheet
    budget. The two constants are set independently, so the relationship has
    to be asserted rather than assumed."""
    ex = CriticalCSSExtractor()
    assert ex.max_critical_css <= ex.max_inline_critical

    ex.max_critical_css = ex.max_inline_critical + 1
    with pytest.raises(ValueError, match='render-blocking'):
        ex._assert_cap_invariant()


def test_truncation_totals_are_accumulated(tmp_path):
    """Saturation was reported as one warning line per page. At 252/252 pages
    that buried the fact rather than conveying it, so the run summary needs
    totals to print instead."""
    # Same shape as test_truncation_keeps_braces_balanced: enough matching
    # rules that the cap binds.
    big = (''.join(f'p{{padding:{i}px;color:#0{i % 10}{i % 10}}}' for i in range(300))
           + '@media (max-width:600px){'
           + ''.join(f'h1{{margin:{i}px}}' for i in range(600)) + '}')
    ex, out = _extract(big, {'p', 'h1'}, tmp_path)
    # Re-run over a second page to prove the counters accumulate.
    ex._extract_matching_css_rules(
        BeautifulSoup('<html><head><link rel="stylesheet" href="/styles.css">'
                      '</head><body><main><p>x</p></main></body></html>',
                      'html.parser'),
        {'p', 'h1'})

    assert ex.css_truncated == 2
    assert ex.css_dropped_rules > 0
    assert ex.css_dropped_bytes > 0
    assert len(out) <= ex.max_critical_css


# ── harvest order ────────────────────────────────────────────────────────
# Rules are kept in harvest order until max_critical_css, so harvest order
# decides what survives truncation. Document order was actively wrong: the
# homepage links footer.min.css, content.min.css, header.min.css in that
# sequence, so with all 252 pages saturating the cap the dropped tail was
# HEADER rules — the most above-the-fold CSS on the page — while footer rules
# for content below several screenfuls were kept.

def test_above_fold_sheets_are_harvested_first():
    ex = CriticalCSSExtractor()
    base = '/wp-content/themes/kadence/assets/css/'
    order = sorted(('header.min.css', 'content.min.css', 'footer.min.css'),
                   key=lambda n: ex._sheet_priority(base + n))
    assert order == ['header.min.css', 'content.min.css', 'footer.min.css']


@pytest.mark.parametrize('name,tier', [
    ('header.min.css', 0),
    ('global.min.css', 0),
    ('content.min.css', 1),
    ('rankmath.min.css', 1),
    ('footer.min.css', 2),
    ('comments.min.css', 2),
    ('related-posts.min.css', 2),
])
def test_sheet_tiers(name, tier):
    ex = CriticalCSSExtractor()
    assert ex._sheet_priority(f'/wp-content/themes/kadence/assets/css/{name}') == tier


def test_priority_matches_the_filename_not_the_path():
    """Every sheet lives under /wp-content/, so matching the whole href puts
    all of them in the 'content' tier — footer.min.css included, which is the
    one sheet this ordering most needs to rank last."""
    ex = CriticalCSSExtractor()
    assert ex._sheet_priority('/wp-content/themes/x/footer.min.css') == 2
    assert ex._sheet_priority('/wp-content/themes/x/comments.min.css') == 2


def test_related_posts_is_not_treated_as_main_content():
    """'post' as a tier-1 needle also matches related-posts.min.css, and
    tier 1 is tested first — so the needle has to stay out."""
    ex = CriticalCSSExtractor()
    assert ex._sheet_priority('/a/related-posts.min.css') == 2


def test_unknown_sheets_keep_document_order_within_their_tier():
    ex = CriticalCSSExtractor()
    assert ex._sheet_priority('/a/mystery.css') == ex._DEFAULT_SHEET_PRIORITY


def test_header_rules_survive_truncation_over_footer_rules(tmp_path):
    """End-to-end statement of the fix: with a cap that can only fit one
    sheet's worth, the header sheet is what lands in the block."""
    (tmp_path / 'header.min.css').write_text(
        ''.join(f'header .h{i}{{margin:{i}px}}' for i in range(200)), encoding='utf-8')
    (tmp_path / 'footer.min.css').write_text(
        ''.join(f'footer .f{i}{{margin:{i}px}}' for i in range(200)), encoding='utf-8')

    soup = BeautifulSoup(
        '<html><head>'
        '<link rel="stylesheet" href="/footer.min.css">'   # document order:
        '<link rel="stylesheet" href="/header.min.css">'   # footer first
        '</head><body><header><div class="h1">x</div></header>'
        '<footer><div class="f1">y</div></footer></body></html>',
        'html.parser')
    ex = CriticalCSSExtractor()
    ex.public_dir = tmp_path
    ex.max_critical_css = 600          # room for roughly one sheet

    out = ex._extract_matching_css_rules(soup, {'header', 'footer', '.h1', '.f1'})

    assert 'header' in out, 'header rules were dropped by the cap'
    assert out.index('header') < (out.index('footer') if 'footer' in out else len(out))
