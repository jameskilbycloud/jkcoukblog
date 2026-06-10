"""Tests for html_transformer's string-level <head> cleanup helpers."""

from html_transformer import HTMLTransformer


def _wrap(head_body, body='<body><p>x</p></body>'):
    return f'<html><head>{head_body}</head>{body}</html>'


class TestDeepCleanHead:
    def test_html_without_head_is_unchanged(self):
        html = '<p>no head here</p>'
        assert HTMLTransformer._deep_clean_head(html) == html

    def test_noscript_blocks_and_orphans_stripped(self):
        html = _wrap(
            '<noscript><link rel="stylesheet" href="/a.css"></noscript>'
            '</noscript></noscript>'
            '<title>t</title>'
        )
        out = HTMLTransformer._deep_clean_head(html)
        assert '<noscript' not in out
        assert '</noscript>' not in out
        assert '<title>t</title>' in out

    def test_duplicate_links_deduped_by_href(self):
        html = _wrap(
            '<link rel="stylesheet" href="/a.css">'
            '<link rel="stylesheet" href="/a.css">'
            '<link rel="stylesheet" href="/b.css">'
        )
        out = HTMLTransformer._deep_clean_head(html)
        assert out.count('href="/a.css"') == 1
        assert out.count('href="/b.css"') == 1

    def test_style_preload_reverted_to_stylesheet(self):
        html = _wrap(
            '<link rel="preload" as="style" href="/a.css" '
            'onload="this.rel=\'stylesheet\'">'
        )
        out = HTMLTransformer._deep_clean_head(html)
        assert 'rel="stylesheet"' in out
        assert 'as="style"' not in out
        assert 'onload' not in out

    def test_font_preloads_stripped(self):
        html = _wrap('<link rel="preload" as="font" href="/f.woff2" crossorigin>')
        out = HTMLTransformer._deep_clean_head(html)
        assert '/f.woff2' not in out

    def test_body_content_untouched(self):
        body = '<body><noscript>kept in body</noscript><h1>title</h1></body>'
        html = _wrap('<title>t</title>', body)
        out = HTMLTransformer._deep_clean_head(html)
        assert '<noscript>kept in body</noscript>' in out
