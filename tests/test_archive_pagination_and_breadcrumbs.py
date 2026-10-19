"""Category/tag archive pagination discovery and the tag breadcrumb trail.

Fixtures mirror the live WordPress on 2026-10-19 (posts_per_page=12), where
/category/homelab/page/2/ etc. were linked via rel="next" but never generated,
and every tag page carried a "Tags" crumb linking to the non-existent /tag/.
"""

from types import SimpleNamespace

from bs4 import BeautifulSoup

from breadcrumb_navigation import BreadcrumbNavigation
from wp_content_discovery import WPContentDiscovery

WP = 'https://wp.example'
PER_PAGE = 12


def _term(kind, slug, count):
    return {'name': slug.title(), 'count': count, 'link': f'{WP}/{kind}/{slug}/'}


CATEGORIES = [_term('category', 'homelab', 27), _term('category', 'vmware', 27),
              _term('category', 'hosting', 11), _term('category', 'empty', 0)]
TAGS = [_term('tag', 'cloudflare', 11), _term('tag', 'homelab', 27),
        _term('tag', 'vmware', 16), _term('tag', 'zoom', 1)]


class FakeSession:
    """Answers HEAD like WordPress: /<base>/page/N/ is 200 iff N <= pages."""

    def __init__(self, home_posts=80):
        self.counts = {'/': home_posts}
        for t in CATEGORIES + TAGS:
            self.counts[t['link'].replace(WP, '')] = t['count']
        self.heads = []

    def head(self, url, **_):
        path = url.replace(WP, '')
        self.heads.append(path)
        base, _, rest = path.rpartition('page/')
        n = int(rest.strip('/'))
        pages = -(-self.counts.get(base, 0) // PER_PAGE)
        return SimpleNamespace(status_code=200 if n <= pages else 404)


def _discovery(session):
    return WPContentDiscovery(session, WP, None, set())


def test_taxonomy_pagination_matches_live_404s():
    d = _discovery(FakeSession())
    urls = d._discover_taxonomy_pagination(CATEGORIES) + d._discover_taxonomy_pagination(TAGS)
    assert sorted(urls) == sorted([
        '/category/homelab/page/2/', '/category/homelab/page/3/',
        '/category/vmware/page/2/', '/category/vmware/page/3/',
        '/tag/homelab/page/2/', '/tag/homelab/page/3/',
        '/tag/vmware/page/2/',
    ])


def test_taxonomy_probing_stops_after_first_unpaginated_term():
    s = FakeSession()
    _discovery(s)._discover_taxonomy_pagination(TAGS)
    # homelab(27) and vmware(16) paginate, cloudflare(11) doesn't -> zoom(1) never probed
    assert not any(h.startswith('/tag/zoom/') for h in s.heads)


def test_homepage_pagination_unchanged():
    assert _discovery(FakeSession(home_posts=80))._probe_pagination('/') == [
        f'/page/{n}/' for n in range(2, 8)]


def _crumbs(url):
    soup = BeautifulSoup('<html><head></head><body><main id="inner-wrap"><h1>x</h1></main></body></html>',
                         'html.parser')
    BreadcrumbNavigation('https://site.example').add_breadcrumb_navigation(soup, url)
    nav = soup.find('nav', attrs={'aria-label': 'Breadcrumb'})
    return [(li.get_text(strip=True).lstrip('/'), (li.find('a') or {}).get('href')) for li in nav.find_all('li')]


def test_tag_breadcrumb_has_no_tag_index_link():
    crumbs = _crumbs('/tag/homelab/')
    assert crumbs == [('Home', 'https://site.example'), ('Homelab', None)]
    assert all(href != 'https://site.example/tag/' for _, href in crumbs)


def test_tag_breadcrumb_matches_category_shape():
    assert len(_crumbs('/tag/vmware/')) == len(_crumbs('/category/vmware/'))
