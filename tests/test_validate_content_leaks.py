"""Tests for validate_content_leaks: the build gate that fails when WordPress
leftovers or denylisted words reach the published site."""

import json

import pytest

import validate_content_leaks as v
from html_transformer import HTMLTransformer

HOST = v.WP_HOST

CLEAN = """<html><head><title>x</title><style>body{margin:0}</style></head><body>
<main><p>I moved {host} to a static site.</p></main>
<footer><div class="jk-footer-row"><span>James Kilby</span></div></footer>
</body></html>""".replace('{host}', HOST)


def _rules(issues):
    return {rule for rule, _ in issues}


def test_clean_page_passes_even_with_host_in_prose():
    assert v.check_html(CLEAN) == []


@pytest.mark.parametrize('snippet, rule', [
    ('<p>WordPress Theme by Kadence WP</p>', 'kadence-credit'),
    ('<meta name="generator" content="WordPress 6.8">', 'wp-generator'),
    ('<div id="wpadminbar"></div>', 'wp-admin-bar'),
    ('<script src="/wp-includes/js/wp-embed.min.js"></script>', 'wp-embed'),
    ('<script>window._wpemojiSettings={}</script>', 'wp-emoji'),
    ('<link rel="pingback" href="/xmlrpc.php">', 'wp-discovery-link'),
    (f'<img src="https://{HOST}/wp-content/uploads/a.png" alt="">', 'wp-host'),
    (f'<style>a{{}} /*# sourceURL=https://{HOST}/wp-includes/x.css */</style>', 'wp-host'),
    (f'<style>a{{background:url(https://{HOST}/a.png)}}</style>', 'wp-host'),
])
def test_each_leftover_is_caught(snippet, rule):
    page = CLEAN.replace('<main>', snippet + '<main>')
    assert rule in _rules(v.check_html(page))


def test_footer_needs_exactly_one_row_and_no_empty_paragraph():
    doubled = CLEAN.replace('</footer>', '<div class="jk-footer-row"></div></footer>')
    assert 'footer' in _rules(v.check_html(doubled))
    emptied = CLEAN.replace('</footer>', '<p> </p></footer>')
    assert 'footer' in _rules(v.check_html(emptied))
    no_footer = '<html><body><main>standalone tool page</main></body></html>'
    assert v.check_html(no_footer) == []


def test_text_outputs():
    assert v.check_text(f'post about {HOST} and its wp-json API') == []
    assert 'wp-asset-link' in _rules(v.check_text(f'![x](https://{HOST}/wp-content/uploads/a.png)'))
    assert 'kadence-credit' in _rules(v.check_text('WordPress Theme by Kadence WP'))


def test_denylist_public_is_whole_word_and_case_sensitive():
    assert v.check_denylist('I run Zorblat at home', public_terms=('Zorblat',))
    assert v.check_denylist('zorblat pop', public_terms=('Zorblat',)) == []
    assert v.check_denylist('Zorblats it', public_terms=('Zorblat',)) == []


def test_denylist_private_terms_are_never_echoed():
    issues = v.check_denylist('my secret Word', public_terms=(), private_terms=('word',))
    assert issues and all('word' not in detail.lower() for _, detail in issues)


def test_scan_walks_html_and_text_outputs(tmp_path):
    (tmp_path / 'index.html').write_text(CLEAN)
    (tmp_path / 'markdown').mkdir()
    (tmp_path / 'markdown' / 'p.md').write_text('WordPress Theme by Kadence WP')
    (tmp_path / 'api').mkdir()
    (tmp_path / 'api' / 'p.json').write_text(json.dumps({'body': 'I run Zorblat'}))
    (tmp_path / 'img.png').write_bytes(b'Zorblat')  # binaries are skipped
    found = v.scan(tmp_path, public_terms=('Zorblat',))
    assert set(found) == {'kadence-credit', 'denylist'}
    assert found['denylist'] == [('api/p.json', 'contains "Zorblat"')]


def test_transformer_strips_what_the_gate_rejects(tmp_path):
    """A page seeded from the previous deploy carries the WP sourceURL
    comment and the Kadence credit; one transformer pass must leave it
    passing the gate, even when no other pass changes the page."""
    page = tmp_path / 'index.html'
    page.write_text(CLEAN.replace(
        '<style>body{margin:0}</style>',
        f'<style>body{{margin:0}} /*# sourceURL=https://{HOST}/wp-includes/x.css */</style>',
    ).replace('<footer>', '<footer><p>WordPress Theme by Kadence WP</p>'))
    assert {'wp-host', 'kadence-credit'} <= _rules(v.check_html(page.read_text()))

    t = HTMLTransformer(str(tmp_path), skip_images=True, skip_critical_css=True)
    assert t._process_file(page) is True
    assert v.check_html(page.read_text()) == []


def test_seeded_extracted_css_is_cleaned_before_inlining(tmp_path):
    """The Nov 2026 failure: WP block styles are extracted to
    /assets/css/*.css with the sourceURL comment, and the transformer inlines
    the small ones back into pages after its own string-level strip. A seeded
    CSS file must be cleaned first, so neither the page nor the file leaks."""
    css_dir = tmp_path / 'assets' / 'css'
    css_dir.mkdir(parents=True)
    css = css_dir / 'wp-block-list-inline-css-abcd1234.min.css'
    css.write_text(f'ol,ul{{box-sizing:border-box}}\n/*# sourceURL=https://{HOST}/wp-includes/blocks/list/style.min.css */')
    page = tmp_path / 'index.html'
    page.write_text(CLEAN.replace(
        '</head>', '<link rel="stylesheet" href="/assets/css/' + css.name + '" media="all"></head>'))
    assert 'wp-host' in _rules(v.check_text(css.read_text()))

    HTMLTransformer(str(tmp_path), skip_images=True, skip_critical_css=True).process_all_files()
    assert v.scan(tmp_path, public_terms=()) == {}
    assert 'box-sizing:border-box' in page.read_text() or 'box-sizing: border-box' in page.read_text()


def test_extracted_css_is_written_clean(tmp_path):
    from bs4 import BeautifulSoup
    from inline_css_fixups import InlineCSSFixups
    soup = BeautifulSoup(
        '<html><head><style id="wp-block-list-inline-css">ol,ul{box-sizing:border-box;padding:0;margin:0}'
        'ol.x,ul.x{list-style:none}' + 'li.y{padding-left:1em}' * 5 + f'\n/*# sourceURL=https://{HOST}/wp-includes/blocks/list/style.min.css */'
        '</style></head><body></body></html>', 'html.parser')
    fx = InlineCSSFixups('https://example.test', tmp_path)
    fx.extract_inline_css(soup, 'https://example.test/')
    files = list((tmp_path / 'assets' / 'css').glob('*.css'))
    assert files and all(HOST not in f.read_text() for f in files)
