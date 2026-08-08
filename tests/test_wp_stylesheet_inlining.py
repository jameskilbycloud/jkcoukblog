"""Tests for html_transformer's WP-stylesheet inlining budget.

With WP-Optimize minify disabled, WordPress emits each plugin/theme
stylesheet separately instead of one wpo-minify bundle. Inlining the small
ones is what keeps a page under the Lighthouse `stylesheet: 5` resourceCounts
budget — but inlined CSS is duplicated into every page and counts against the
`document: 30` KB transfer budget, so it has to be capped both per-file and
per-page. Both budgets are asserted here, along with the cascade-order
guarantee that makes smallest-first selection safe.
"""

from bs4 import BeautifulSoup
from html_transformer import HTMLTransformer


def _build(tmp_path, stylesheets):
    """Write CSS files and return (transformer, soup) linking them in order."""
    links = []
    for rel, content in stylesheets:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        links.append(f'<link rel="stylesheet" href="/{rel}"/>')

    soup = BeautifulSoup(
        f'<html><head>{"".join(links)}</head><body><p>x</p></body></html>',
        'html.parser',
    )
    return HTMLTransformer(tmp_path), soup


def _css(selector, size):
    """CSS of roughly `size` bytes."""
    body = 'a' * max(0, size - len(selector) - 12)
    return f'.{selector}{{content:"{body}"}}'


PLUGIN = 'wp-content/plugins/acme/style.css'
THEME = 'wp-content/themes/kadence/assets/css/extra.css'


def test_unbundled_plugin_css_is_inlined(tmp_path):
    """The old allowlist named specific files and the wpo-minify bundle, so
    unbundled plugin CSS matched nothing and was never considered."""
    transformer, soup = _build(tmp_path, [(PLUGIN, _css('acme', 500))])

    assert transformer._apply_inline_tiny_wp_stylesheets(soup) is True
    assert soup.find('style') is not None
    assert '.acme' in soup.find('style').string
    assert soup.find('link', href=f'/{PLUGIN}') is None


def test_file_over_per_file_cap_stays_linked(tmp_path):
    big = _css('big', HTMLTransformer._WP_INLINE_MAX_BYTES + 500)
    transformer, soup = _build(tmp_path, [(PLUGIN, big)])

    assert transformer._apply_inline_tiny_wp_stylesheets(soup) is False
    assert soup.find('style') is None
    assert soup.find('link', href=f'/{PLUGIN}') is not None


def test_page_budget_caps_total_inlined_bytes(tmp_path):
    """Six 8 KB files would blow the document transfer budget if all inlined."""
    per_file = HTMLTransformer._WP_INLINE_MAX_BYTES
    sheets = [
        (f'wp-content/plugins/p{i}/style.css', _css(f'p{i}', per_file))
        for i in range(6)
    ]
    transformer, soup = _build(tmp_path, sheets)

    transformer._apply_inline_tiny_wp_stylesheets(soup)

    inlined = sum(
        len(tag.string.encode('utf-8')) for tag in soup.find_all('style')
    )
    assert inlined <= HTMLTransformer._WP_INLINE_TOTAL_MAX_BYTES
    # The ones that didn't fit must still be reachable, not silently dropped.
    assert soup.find_all('link', rel='stylesheet')


def test_cascade_order_is_preserved(tmp_path):
    """Selection is smallest-first, but each <style> is inserted at its own
    <link>'s position. If insertion followed selection order instead, a later
    stylesheet could start winning the cascade over an earlier one."""
    sheets = [
        ('wp-content/plugins/big/style.css', _css('big', 3000)),
        ('wp-content/plugins/small/style.css', _css('small', 200)),
    ]
    transformer, soup = _build(tmp_path, sheets)

    transformer._apply_inline_tiny_wp_stylesheets(soup)

    order = [
        'big' if '.big' in tag.string else 'small'
        for tag in soup.find_all('style')
    ]
    assert order == ['big', 'small'], (
        "inlined <style> tags must keep the original document order"
    )


def test_non_wp_stylesheets_are_left_alone(tmp_path):
    transformer, soup = _build(tmp_path, [('assets/css/ours.css', _css('ours', 100))])

    assert transformer._apply_inline_tiny_wp_stylesheets(soup) is False
    assert soup.find('link', href='/assets/css/ours.css') is not None


def _async_head(tmp_path, rel_path, content):
    """The shape a stylesheet actually has by the time this pass runs: critical
    CSS (Phase 4) has already converted it to an async preload plus a noscript
    fallback."""
    path = tmp_path / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')
    return BeautifulSoup(
        '<html><head>'
        f'<link as="style" href="/{rel_path}" media="all" '
        f'onload="this.onload=null;this.rel=\'stylesheet\'" rel="preload"/>'
        f'<noscript><link rel="stylesheet" href="/{rel_path}"/></noscript>'
        '</head><body></body></html>',
        'html.parser',
    )


def test_async_preloaded_stylesheet_is_inlined(tmp_path):
    """Regression: matching only rel="stylesheet" found nothing but the
    noscript fallback, so the real request survived and this pass was
    effectively dead on every page that had critical CSS extracted."""
    soup = _async_head(tmp_path, PLUGIN, _css('acme', 400))
    transformer = HTMLTransformer(tmp_path)

    assert transformer._apply_inline_tiny_wp_stylesheets(soup) is True

    assert '.acme' in soup.find('style').string
    # Both the preload and the noscript fallback must go, or the browser
    # still pays for the request.
    assert soup.find('link', href=f'/{PLUGIN}') is None
    assert soup.find('noscript') is None


def test_stylesheet_inlined_only_once_across_both_forms(tmp_path):
    """The preload and its noscript fallback are the same file; inlining both
    would double the bytes and spend the page budget on a duplicate."""
    soup = _async_head(tmp_path, PLUGIN, _css('acme', 400))
    HTMLTransformer(tmp_path)._apply_inline_tiny_wp_stylesheets(soup)

    assert len(soup.find_all('style')) == 1


def test_empty_stylesheet_is_dropped_not_inlined(tmp_path):
    """optimize_css can prune a file to 0 bytes (rankmath.min.css is one). It
    still costs a request, so drop the link rather than emit an empty <style>."""
    soup = _async_head(tmp_path, PLUGIN, '')
    transformer = HTMLTransformer(tmp_path)

    assert transformer._apply_inline_tiny_wp_stylesheets(soup) is True
    assert soup.find('style') is None
    assert soup.find('link', href=f'/{PLUGIN}') is None


EXTRACTED = 'assets/css/kadence-global-inline-css-5290643c.min.css'


def test_pipeline_extracted_inline_css_is_inlined(tmp_path):
    """extract_inline_css lifts WordPress's inline <style> blocks out to
    /assets/css/*-inline-css-*.min.css. WP-Optimize used to absorb those; with
    minify off they became extra requests on 170 pages."""
    soup = _async_head(tmp_path, EXTRACTED, _css('kadence', 900))
    transformer = HTMLTransformer(tmp_path)

    assert transformer._apply_inline_tiny_wp_stylesheets(soup) is True
    assert '.kadence' in soup.find('style').string
    assert soup.find('link', href=f'/{EXTRACTED}') is None


def test_brutalist_theme_is_not_captured_by_inline_css_pattern(tmp_path):
    """brutalist-theme.css also lives under /assets/css/ but is handled by
    _apply_inline_project_stylesheets at Phase 4.7. The pattern matches the
    '-inline-css-' filename convention precisely so it can't grab it."""
    soup = _async_head(tmp_path, 'assets/css/brutalist-theme.css', _css('jk', 500))

    assert HTMLTransformer(tmp_path)._apply_inline_tiny_wp_stylesheets(soup) is False
    assert soup.find('link', href='/assets/css/brutalist-theme.css') is not None


def test_stats_record_why_nothing_was_inlined(tmp_path):
    """The pass once no-opped across a whole production build without raising,
    which was indistinguishable from success in the log. Every skip reason has
    to be counted."""
    soup = _async_head(tmp_path, PLUGIN, _css('acme', 400))
    (tmp_path / PLUGIN).unlink()  # file referenced but absent from the tree

    transformer = HTMLTransformer(tmp_path)
    assert transformer._apply_inline_tiny_wp_stylesheets(soup) is False

    stats = transformer.wp_inline_stats
    assert stats['css_links_seen'] == 1
    assert stats['pattern_matched'] == 1
    assert stats['skip_not_on_disk'] == 1
    assert stats['inlined'] == 0
    assert 'sample_missing' in stats


def test_stats_record_success(tmp_path):
    soup = _async_head(tmp_path, PLUGIN, _css('acme', 400))
    transformer = HTMLTransformer(tmp_path)
    transformer._apply_inline_tiny_wp_stylesheets(soup)

    stats = transformer.wp_inline_stats
    assert stats['inlined'] == 1
    assert stats['inlined_bytes'] > 0
    assert stats['skip_not_on_disk'] == 0


def test_missing_file_is_skipped(tmp_path):
    transformer = HTMLTransformer(tmp_path)
    soup = BeautifulSoup(
        '<html><head><link rel="stylesheet" href="/wp-content/plugins/gone/x.css"/>'
        '</head><body></body></html>',
        'html.parser',
    )

    assert transformer._apply_inline_tiny_wp_stylesheets(soup) is False
