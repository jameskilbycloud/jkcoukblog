"""HAG-33 small SEO defects: breadcrumb names, archive descriptions, sitemap
noindex sniffing, proficiencyLevel, homepage H1 fallback."""

import json
from pathlib import Path

from bs4 import BeautifulSoup

from breadcrumb_navigation import BreadcrumbNavigation
from fix_seo_issues import SEOFixer
from page_seo_meta import PageSeoMeta
from site_artifacts_builder import SiteArtifactsBuilder

T = 'https://jameskilby.co.uk'


def _archive(h1='AWS', desc='As previously mentioned I have been working a lot with VMware Cloud on AWS',
             extra=''):
    return BeautifulSoup(
        f'<html><head><title>{h1} Archives - James Kilby</title>'
        f'<meta name="description" content="{desc}"></head>'
        f'<body class="archive category"><main id="inner-wrap"><header>'
        f'<h1 class="page-title archive-title">{h1}</h1>{extra}</header>'
        '<article><p>Post card excerpt</p></article></main></body></html>', 'html.parser')


def _crumbs(soup):
    return [li.get_text(strip=True).lstrip('/') for li in soup.select('.breadcrumb-list li')]


def test_breadcrumb_uses_archive_h1_not_title_cased_slug():
    soup = _archive('AWS')
    BreadcrumbNavigation(T).add_breadcrumb_navigation(soup, '/category/aws/')
    assert _crumbs(soup) == ['Home', 'AWS']


def test_paginated_archive_breadcrumb_links_term_and_shows_page():
    soup = _archive('VMware')
    BreadcrumbNavigation(T).add_breadcrumb_navigation(soup, '/tag/vmware/page/2/')
    assert _crumbs(soup) == ['Home', 'VMware', 'Page 2']
    link = soup.select_one('.breadcrumb-list a[href$="/tag/vmware/"]')
    assert link is not None and link.get_text() == 'VMware'
    assert soup.select_one('.breadcrumb-current').get_text() == 'Page 2'


def test_taxonomy_description_replaces_first_post_excerpt():
    soup = _archive('AWS')
    PageSeoMeta().add_taxonomy_meta_description(soup, '/category/aws/')
    desc = soup.find('meta', attrs={'name': 'description'})['content']
    assert desc.startswith('Browse all AWS articles.')


def test_taxonomy_description_prefers_wordpress_term_description():
    soup = _archive('Homelab', extra='<div class="archive-description"><p>My homelab: '
                    'servers, storage and networking I run at home.</p></div>')
    PageSeoMeta().add_taxonomy_meta_description(soup, '/category/homelab/')
    assert soup.find('meta', attrs={'name': 'description'})['content'] == (
        'My homelab: servers, storage and networking I run at home.')


def test_pagination_description_has_no_ellipsis_and_is_idempotent():
    soup = BeautifulSoup('<head><meta name="description" content="' + 'word ' * 40 + '"></head>',
                         'html.parser')
    meta = PageSeoMeta()
    meta.fix_pagination_meta_description(soup, '/category/homelab/page/3/')
    meta.fix_pagination_meta_description(soup, '/category/homelab/page/3/')
    desc = soup.find('meta', attrs={'name': 'description'})['content']
    assert '...' not in desc
    assert desc.endswith('word - Page 3') and desc.count(' - Page 3') == 1
    assert len(desc) <= 160


def test_meta_description_not_expanded_from_archive_cards(tmp_path):
    fixer = SEOFixer(public_dir=str(tmp_path))
    soup = BeautifulSoup('<head><meta name="description" content="Short"></head>'
                         '<body><article><p>' + 'Another post excerpt ' * 10 + '</p></article></body>',
                         'html.parser')
    path = tmp_path / 'tag' / 'aws' / 'index.html'
    assert fixer.fix_meta_description(soup, path) is False
    post = tmp_path / '2026' / '01' / 'p' / 'index.html'
    assert fixer.fix_meta_description(soup, post) is True


def test_noindex_detected_after_large_inline_css(tmp_path):
    page = tmp_path / 'x' / 'index.html'
    page.parent.mkdir()
    page.write_text('<html><head><style>' + 'a{color:red}' * 1000 + '</style>'
                    '<meta content="noindex,follow" name="robots"/></head><body>noindex</body></html>')
    b = SiteArtifactsBuilder(tmp_path, T)
    assert b._is_noindex_page(page) is True
    page.write_text('<html><head><meta name="robots" content="index, follow"/></head>'
                    '<body>a post about noindex tags</body></html>')
    assert b._is_noindex_page(page) is False


def test_blanket_expert_proficiency_removed(tmp_path):
    fixer = SEOFixer(public_dir=str(tmp_path))
    graph = [{'@type': 'BlogPosting', 'headline': 'a'},
             {'@type': 'TechArticle', 'headline': 'b', 'proficiencyLevel': 'Expert'}]
    soup = BeautifulSoup('<script type="application/ld+json">'
                         + json.dumps({'@graph': graph}) + '</script>', 'html.parser')
    fixer.fix_blogposting_to_techarticle(soup, Path('x.html'))
    out = json.loads(soup.find('script').string)['@graph']
    assert [n['@type'] for n in out] == ['TechArticle', 'TechArticle']
    assert all('proficiencyLevel' not in n for n in out)


def test_homepage_h1_fallback_keeps_all_children():
    soup = BeautifulSoup('<body><p class="site-title"><a href="/">James</a> <span>Kilby</span>'
                         '</p></body>', 'html.parser')
    PageSeoMeta().ensure_homepage_h1(soup, '/')
    h1 = soup.find('h1')
    assert h1.find('a') is not None and h1.find('span') is not None
