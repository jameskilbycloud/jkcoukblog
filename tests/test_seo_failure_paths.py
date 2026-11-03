"""Failure paths that used to be silent: a crashing SEO fix, a WordPress API
error during discovery, and a sitemap that lost most of its URLs."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from bs4 import BeautifulSoup

import html_transformer
from fix_seo_issues import SEOFixer
from validate_seo import validate_site_artifacts
from wp_content_discovery import WPContentDiscovery


def test_one_failing_fix_does_not_skip_the_others(tmp_path, monkeypatch):
    fixer = SEOFixer(public_dir=str(tmp_path))

    def boom(soup, file_path):
        raise ValueError('bad JSON-LD shape')

    monkeypatch.setattr(fixer, 'fix_title_length', boom)
    soup = BeautifulSoup('<html><head></head><body><img src="/a.png"></body></html>',
                         'html.parser')
    assert fixer.apply_all(soup, tmp_path / 'x' / 'index.html') is True
    assert soup.find('img')['alt'] == ''          # later fix still ran
    assert [name for _, name, _ in fixer.errors] == ['fix_title_length']
    assert fixer.report_errors() == 1


def test_process_all_files_returns_error_count(tmp_path, monkeypatch):
    (tmp_path / 'p').mkdir()
    (tmp_path / 'p' / 'index.html').write_text('<html><head></head><body></body></html>')
    fixer = SEOFixer(public_dir=str(tmp_path))
    monkeypatch.setattr(fixer, 'fix_multiple_h1',
                        lambda s, f: (_ for _ in ()).throw(RuntimeError('x')))
    assert fixer.process_all_files() == 1


def test_fix_order_names_real_methods_and_covers_every_fix():
    for name in SEOFixer.FIX_ORDER:
        assert callable(getattr(SEOFixer, name)), name
    fix_methods = {n for n in dir(SEOFixer)
                   if (n.startswith('fix_') or n in ('ensure_image_alt_text',
                                                     'lock_homepage_h1_text'))
                   and callable(getattr(SEOFixer, n))}
    assert fix_methods == set(SEOFixer.FIX_ORDER)


def test_transformer_uses_shared_fix_list():
    src = Path(html_transformer.__file__).read_text()
    assert 'self.seo.apply_all(soup, file_path)' in src
    assert 'self.seo.fix_title_length' not in src


class _PostsSession:
    def __init__(self, status):
        self.status = status

    def get(self, url, params=None, **_):
        return SimpleNamespace(status_code=self.status, text='upstream error',
                               json=lambda: [])


@pytest.mark.parametrize('status', [401, 500, 502])
def test_post_discovery_error_stops_the_build(status):
    d = WPContentDiscovery(_PostsSession(status), 'https://wp.example', None, set())
    with pytest.raises(RuntimeError, match=str(status)):
        d.get_all_content_urls()


SM = ('<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
      '{}</urlset>')


def _sitemap(path, n):
    locs = ''.join(f'<url><loc>https://jameskilby.co.uk/p{i}/</loc></url>' for i in range(n))
    path.write_text(SM.format(locs))


def _site(tmp_path, n):
    site = tmp_path / 'site'
    for i in range(n):
        (site / f'p{i}').mkdir(parents=True)
        (site / f'p{i}' / 'index.html').write_text('<html></html>')
    (site / 'robots.txt').write_text('Sitemap: https://jameskilby.co.uk/sitemap.xml\n')
    _sitemap(site / 'sitemap.xml', n)
    return site


def test_sitemap_shrink_over_threshold_fails(tmp_path):
    site = _site(tmp_path, 50)
    base = tmp_path / 'base.xml'
    _sitemap(base, 80)
    cats = {i.category for i in validate_site_artifacts(site, base) if i.severity == 'error'}
    assert 'sitemap-shrunk' in cats


def test_sitemap_small_change_passes(tmp_path):
    site = _site(tmp_path, 78)
    base = tmp_path / 'base.xml'
    _sitemap(base, 80)
    assert 'sitemap-shrunk' not in {i.category for i in validate_site_artifacts(site, base)}


def test_sitemap_without_baseline_skips_check(tmp_path):
    site = _site(tmp_path, 3)
    assert 'sitemap-shrunk' not in {i.category for i in validate_site_artifacts(site)}
