"""Tests for build-time injection of the blog search box into <main>
(wp_to_static_generator._inject_search_box).

search.js originally built this box at runtime and inserted it at the top of
<main> ~2s after load. That pushed every page's content down 82px — 0.079 CLS
on the homepage, 0.099 on posts, measured on a throttled Pixel 7 profile — and
took the origin's p75 CLS from 0.05 to 0.22 between the CrUX windows ending
2026-07-25 and 2026-08-22. Rendering it at build time reserves the space.

_inject_search_box only touches the soup it is handed, so it runs against a
lightweight stub rather than the full WordPress-dependent generator.
"""

import re
from pathlib import Path

from bs4 import BeautifulSoup

from wp_to_static_generator import WordPressStaticGenerator as G

SEARCH_JS = Path(__file__).resolve().parent.parent / 'scripts' / 'assets' / 'js' / 'search.js'


def _inject(html):
    soup = BeautifulSoup(html, 'html.parser')
    G._inject_search_box(G, soup)
    return soup


def test_box_is_first_child_of_main():
    soup = _inject('<html><body><header>h</header>'
                   '<main><div id="primary">post</div></main></body></html>')
    main = soup.find('main')
    first = next(c for c in main.children if getattr(c, 'name', None))
    assert first.get('id') == 'blog-search-container', (
        'search box must occupy its space above the content, not after it')
    assert soup.find(id='blog-search-input') is not None


def test_injection_is_idempotent():
    once = _inject('<html><body><main><div id="primary">p</div></main></body></html>')
    twice = BeautifulSoup(str(once), 'html.parser')
    G._inject_search_box(G, twice)
    assert len(twice.find_all(id='blog-search-container')) == 1
    assert str(twice) == str(once)


def test_page_without_main_is_left_alone():
    html = '<html><body><div id="primary">no main here</div></body></html>'
    soup = _inject(html)
    assert soup.find(id='blog-search-container') is None
    assert str(soup) == html


def test_build_time_markup_matches_the_search_js_fallback():
    """search.js still ships the same markup for the case where the build-time
    copy is missing. If the two drift, the box changes shape after load — the
    exact layout shift this injection exists to remove."""
    js = SEARCH_JS.read_text(encoding='utf-8')
    template = re.search(r'const searchHTML = `(.*?)`;', js, re.S)
    assert template, 'search.js fallback template not found — did it move?'

    def norm(markup):
        # Compare rendered structure, not source whitespace: the JS template is
        # indented across lines, the Python constant is one string. Parsing
        # first normalises attribute order and quoting; collapsing the runs
        # between tags drops the JS template's indentation, which is inert
        # here (every node in the box is a block or a replaced element).
        parsed = str(BeautifulSoup(markup, 'html.parser'))
        return re.sub(r'>\s+<', '><', re.sub(r'\s+', ' ', parsed)).strip()

    assert norm(template.group(1)) == norm(G.SEARCH_BOX_HTML)


def test_search_js_wires_up_a_prerendered_box():
    """The early return must attach behaviour rather than bail, or the
    pre-rendered box would render but never respond to typing."""
    js = SEARCH_JS.read_text(encoding='utf-8')
    guard = re.search(
        r"if \(document\.getElementById\('blog-search-container'\)\) \{(.*?)\}",
        js, re.S)
    assert guard, 'search.js no longer guards on an existing container'
    assert 'attachSearchListener()' in guard.group(1)
    assert 'attachKeyboardShortcut()' in guard.group(1)
