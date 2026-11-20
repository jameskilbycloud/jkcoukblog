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
    assert v.check_denylist('I run Stash at home', public_terms=('Stash',))
    assert v.check_denylist('git stash pop', public_terms=('Stash',)) == []
    assert v.check_denylist('Stashed it', public_terms=('Stash',)) == []


def test_denylist_private_terms_are_never_echoed():
    issues = v.check_denylist('my secret Word', public_terms=(), private_terms=('word',))
    assert issues and all('word' not in detail.lower() for _, detail in issues)


def test_scan_walks_html_and_text_outputs(tmp_path):
    (tmp_path / 'index.html').write_text(CLEAN)
    (tmp_path / 'markdown').mkdir()
    (tmp_path / 'markdown' / 'p.md').write_text('WordPress Theme by Kadence WP')
    (tmp_path / 'api').mkdir()
    (tmp_path / 'api' / 'p.json').write_text(json.dumps({'body': 'I run Stash'}))
    (tmp_path / 'img.png').write_bytes(b'Stash')  # binaries are skipped
    found = v.scan(tmp_path)
    assert set(found) == {'kadence-credit', 'denylist'}
    assert found['denylist'] == [('api/p.json', 'contains "Stash"')]


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
