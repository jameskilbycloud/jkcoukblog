"""Tests for scripts/internal_links.py — the contextual internal-linking pass
that gives every orphan post (no inbound post-to-post body link) one relevant
inbound link.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
import internal_links as il  # noqa: E402


# ---- normalise_post_url --------------------------------------------------
@pytest.mark.parametrize('href,expected', [
    ('/2023/10/vgpu-setup/', '/2023/10/vgpu-setup/'),
    ('/2023/10/vgpu-setup', '/2023/10/vgpu-setup/'),          # add trailing slash
    ('https://jameskilby.co.uk/2020/06/veeamon2020/', '/2020/06/veeamon2020/'),
    ('https://jkcoukblog.pages.dev/2020/06/x/', '/2020/06/x/'),
    ('/2023/10/vgpu-setup/#section', '/2023/10/vgpu-setup/'),  # strip fragment
    ('/category/homelab/', None),                              # not a post
    ('/tag/vsan/', None),
    ('/about/', None),
    ('https://external.example/2023/10/x/', None),            # off-site
    ('', None),
])
def test_normalise_post_url(href, expected):
    assert il.normalise_post_url(href) == expected


# ---- body_post_links: only <article> links count -------------------------
def _post(article_html, extra=''):
    return (f'<html><body><nav><a href="/2000/01/navlink/">nav</a></nav>'
            f'<article>{article_html}</article>'
            f'<footer><a href="/2000/02/footlink/">foot</a></footer>{extra}</body></html>')


def test_body_links_scope_excludes_nav_and_footer():
    html = _post('<div class="entry-content"><p>see '
                 '<a href="/2021/05/target/">target</a></p></div>'
                 '<section class="related-posts-section">'
                 '<a href="/2022/07/related/">rel</a></section>')
    links = il.body_post_links(html)
    assert links == {'/2021/05/target/', '/2022/07/related/'}
    assert '/2000/01/navlink/' not in links   # nav excluded
    assert '/2000/02/footlink/' not in links   # footer excluded


# ---- build_inbound_graph + find_orphans ----------------------------------
def test_graph_and_orphans():
    posts = {
        '/2023/01/x/': _post('<div class="entry-content"><p><a href="/2023/02/y/">y</a></p></div>'),
        '/2023/02/y/': _post('<div class="entry-content"><p>orphan, links nobody back</p></div>'),
        '/2023/03/z/': _post('<div class="entry-content"><p><a href="/2023/02/y/">y</a></p></div>'),
    }
    graph = il.build_inbound_graph(posts)
    assert graph['/2023/02/y/'] == {'/2023/01/x/', '/2023/03/z/'}
    # x and z receive no inbound links -> orphans; y is well-linked
    assert il.find_orphans(graph) == ['/2023/01/x/', '/2023/03/z/']


# ---- assign_hosts: relevance + fallback ----------------------------------
def test_assign_hosts_prefers_most_relevant():
    index = {
        '/o/': {'cats': {'vmware'}, 'tags': {'vgpu', 'homelab'}, 'date': '2023'},
        '/strong/': {'cats': {'vmware'}, 'tags': {'vgpu', 'homelab'}, 'date': '2024'},  # 3*2+2*1=8
        '/weak/': {'cats': {'vmware'}, 'tags': set(), 'date': '2025'},                   # 2*1=2
    }
    hosts = il.assign_hosts(['/o/'], index)
    assert hosts['/o/'] == '/strong/'


def test_assign_hosts_zero_overlap_falls_back_and_never_empty():
    index = {
        '/orphan/': {'cats': {'money'}, 'tags': {'finance'}, 'date': '2017'},
        '/newer/': {'cats': {'vmware'}, 'tags': {'esxi'}, 'date': '2026'},
        '/older/': {'cats': {'homelab'}, 'tags': {'zfs'}, 'date': '2019'},
    }
    hosts = il.assign_hosts(['/orphan/'], index)
    # no taxonomy overlap -> newest overall
    assert hosts['/orphan/'] == '/newer/'


def test_assign_hosts_excludes_other_orphans_as_hosts():
    index = {
        '/o1/': {'cats': {'x'}, 'tags': {'t'}, 'date': '2023'},
        '/o2/': {'cats': {'x'}, 'tags': {'t'}, 'date': '2024'},
        '/host/': {'cats': {'x'}, 'tags': set(), 'date': '2022'},
    }
    hosts = il.assign_hosts(['/o1/', '/o2/'], index, exclude_hosts={'/o1/', '/o2/'})
    assert hosts['/o1/'] == '/host/' and hosts['/o2/'] == '/host/'


# ---- inject_related_link: placement + idempotency ------------------------
def test_inject_lands_in_entry_content():
    html = _post('<div class="entry-content"><p>Intro paragraph.</p>'
                 '<p>Body paragraph.</p></div>')
    out, changed = il.inject_related_link(html, '/2023/10/vgpu/', 'vGPU Setup')
    assert changed
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(out, 'html.parser')
    note = soup.select_one('p.internal-related-link')
    assert note is not None
    assert note.find_parent(class_='entry-content') is not None
    a = note.find('a')
    assert a['href'] == '/2023/10/vgpu/' and a.string == 'vGPU Setup'


def test_inject_is_idempotent():
    html = _post('<div class="entry-content"><p>Intro.</p></div>')
    once, c1 = il.inject_related_link(html, '/2023/10/vgpu/', 'vGPU')
    twice, c2 = il.inject_related_link(once, '/2023/10/vgpu/', 'vGPU')
    assert c1 and not c2
    assert once == twice


def test_inject_noop_when_link_already_present_in_prose():
    html = _post('<div class="entry-content"><p>see '
                 '<a href="/2023/10/vgpu/">it</a></p></div>')
    out, changed = il.inject_related_link(html, '/2023/10/vgpu/', 'vGPU')
    assert not changed and out == html


def test_inject_noop_without_entry_content():
    html = '<html><body><article><p>no entry-content div</p></article></body></html>'
    out, changed = il.inject_related_link(html, '/2023/10/vgpu/', 'vGPU')
    assert not changed


# ---- apply_to_output: end-to-end over a tiny built site ------------------
def _write(root, url, article_html):
    d = root / url.strip('/')
    d.mkdir(parents=True, exist_ok=True)
    (d / 'index.html').write_text(
        f'<html><head><title>{url}</title></head><body>'
        f'<article>{article_html}</article></body></html>', encoding='utf-8')


def test_apply_to_output_links_every_orphan(tmp_path):
    # host links to itself-relevant hub; two orphans get nothing inbound
    _write(tmp_path, '/2024/01/hub/',
           '<div class="entry-content"><p>Hub. <a href="/2024/02/linked/">linked</a></p></div>')
    _write(tmp_path, '/2024/02/linked/',
           '<div class="entry-content"><p>Linked, and links back to '
           '<a href="/2024/01/hub/">hub</a>.</p></div>')
    _write(tmp_path, '/2020/05/orphan-a/', '<div class="entry-content"><p>Orphan A.</p></div>')
    _write(tmp_path, '/2019/05/orphan-b/', '<div class="entry-content"><p>Orphan B.</p></div>')
    index = {
        '/2024/01/hub/': {'cats': {'homelab'}, 'tags': {'vmware'}, 'date': '2024', 'title': 'Hub'},
        '/2024/02/linked/': {'cats': {'homelab'}, 'tags': set(), 'date': '2024', 'title': 'Linked'},
        '/2020/05/orphan-a/': {'cats': {'homelab'}, 'tags': {'vmware'}, 'date': '2020', 'title': 'Orphan A'},
        '/2019/05/orphan-b/': {'cats': {'homelab'}, 'tags': set(), 'date': '2019', 'title': 'Orphan B'},
    }
    applied = il.apply_to_output(tmp_path, index=index, log=lambda *a: None)
    orphans_fixed = {o for o, _ in applied}
    assert orphans_fixed == {'/2020/05/orphan-a/', '/2019/05/orphan-b/'}

    # After the pass, no post is orphaned any more.
    posts = {u: (tmp_path / u.strip('/') / 'index.html').read_text(encoding='utf-8')
             for u in index}
    graph = il.build_inbound_graph(posts)
    assert il.find_orphans(graph) == []

    # Idempotent second run.
    assert il.apply_to_output(tmp_path, index=index, log=lambda *a: None) == []
    # Guard sees a fully-linked site as clean.
    assert il.verify(tmp_path, log=lambda *a: None) == []


def test_verify_flags_unlinked_and_pass_recovers(tmp_path):
    """Reproduces the deploy defect: a host that lost its injected paragraph.
    verify() must flag the now-orphaned target, and a re-run must recover it."""
    # host <-> other link each other, so only `orphan` starts unlinked.
    _write(tmp_path, '/2024/01/host/',
           '<div class="entry-content"><p>Host body, links '
           '<a href="/2024/02/other/">other</a>.</p></div>')
    _write(tmp_path, '/2024/02/other/',
           '<div class="entry-content"><p>Other, links '
           '<a href="/2024/01/host/">host</a>.</p></div>')
    _write(tmp_path, '/2020/05/orphan/', '<div class="entry-content"><p>Orphan.</p></div>')
    index = {
        '/2024/01/host/': {'cats': {'x'}, 'tags': {'t'}, 'date': '2024', 'title': 'Host'},
        '/2024/02/other/': {'cats': {'x'}, 'tags': set(), 'date': '2024', 'title': 'Other'},
        '/2020/05/orphan/': {'cats': {'x'}, 'tags': {'t'}, 'date': '2020', 'title': 'Orphan'},
    }
    il.apply_to_output(tmp_path, index=index, log=lambda *a: None)
    assert il.verify(tmp_path, log=lambda *a: None) == []

    # Simulate a later pipeline step reverting the host to its pre-injection
    # state (keeps its editorial link to `other`, drops the injected paragraph).
    host_file = tmp_path / '2024/01/host/index.html'
    host_file.write_text('<html><body><article>'
                         '<div class="entry-content"><p>Host body, links '
                         '<a href="/2024/02/other/">other</a>.</p></div>'
                         '</article></body></html>', encoding='utf-8')
    assert il.verify(tmp_path, log=lambda *a: None) == ['/2020/05/orphan/']

    # Re-running the pass recovers it; guard then clean.
    il.apply_to_output(tmp_path, index=index, log=lambda *a: None)
    assert il.verify(tmp_path, log=lambda *a: None) == []
