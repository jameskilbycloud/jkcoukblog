"""Tests for html_transformer's string-level <head> cleanup helpers."""

import inspect
import re

from fix_seo_issues import SEOFixer
from html_transformer import HTMLTransformer


def _ordered_fix_calls(func, receiver):
    """Extract the ordered list of `fix_*` method names called inside a
    method's source, matching e.g. `self.fix_x(` or `self.seo.fix_x(`."""
    src = inspect.getsource(func)
    return re.findall(rf'{receiver}\.(fix_[a-z0-9_]+)\(', src)


class TestSeoPassListInSync:
    """The deploy pipeline runs html_transformer.py, whose _apply_seo_fixes()
    is a hand-maintained mirror of SEOFixer.process_file's pass list (it drives
    the SEOFixer methods on an already-parsed soup and never calls process_file).
    A pass added to SEOFixer but not the mirror is silently DEAD in production —
    the exact bug that left fix_jsonld_headline_brand_suffix and
    fix_article_entity_links un-run. This test fails the build if the two lists
    ever drift, so the mirror can't fall behind again.
    """

    def test_orchestrator_runs_every_seofixer_pass(self):
        canonical = _ordered_fix_calls(SEOFixer.process_file, 'self')
        mirror = _ordered_fix_calls(HTMLTransformer._apply_seo_fixes, 'self.seo')

        missing = [p for p in canonical if p not in mirror]
        extra = [p for p in mirror if p not in canonical]
        assert not missing, (
            f"passes in SEOFixer.process_file but NOT run by html_transformer "
            f"(dead in production): {missing}"
        )
        assert not extra, (
            f"passes run by html_transformer but absent from SEOFixer.process_file "
            f"(stale mirror): {extra}"
        )

    def test_pass_order_matches(self):
        canonical = _ordered_fix_calls(SEOFixer.process_file, 'self')
        mirror = _ordered_fix_calls(HTMLTransformer._apply_seo_fixes, 'self.seo')
        # Order matters: some passes depend on an earlier pass's output
        # (e.g. headline cleanup before entity linking).
        assert canonical == mirror, (
            f"SEO pass order differs.\n  process_file: {canonical}\n  orchestrator: {mirror}"
        )


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


def test_normalize_self_href_maps_absolute_same_site_to_relative():
    # Guards the duplicate-LCP-preload fix: an absolutified srcset-derived
    # href and an existing relative preload must compare equal.
    from enhance_html_performance import normalize_self_href

    assert (normalize_self_href('https://jameskilby.co.uk/wp-content/a.avif')
            == '/wp-content/a.avif')
    assert normalize_self_href('/wp-content/a.avif') == '/wp-content/a.avif'
    # Domain-only hrefs (preconnect) and external URLs are left alone.
    assert (normalize_self_href('https://jameskilby.co.uk')
            == 'https://jameskilby.co.uk')
    assert normalize_self_href('https://utteranc.es/x.js') == 'https://utteranc.es/x.js'
