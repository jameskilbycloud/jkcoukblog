"""Tests for stripping the wp-emoji loader
(wp_to_static_generator.remove_wordpress_elements).

WordPress inlines an emoji-detection script that creates a Web Worker from a
blob: URL. The site CSP has no worker-src, so the worker is blocked and every
page logs a console error (a Lighthouse Best-Practices ding). The polyfill is
dead weight on a static site, so the generator strips the settings JSON, the
inline loader, and the emoji <style>. Critical CSS must survive untouched.
"""

from bs4 import BeautifulSoup

from wp_to_static_generator import WordPressStaticGenerator as G

EMOJI_HTML = """
<html><head>
<style id="critical-css">.brand img{display:block}</style>
<style>img.wp-smiley, img.emoji { height: 1em !important; }</style>
<script id="wp-emoji-settings" type="application/json">{"a":1}</script>
<script type="module">var t=document.querySelector('#wp-emoji-settings');
window._wpemojiSettings={};new Worker(URL.createObjectURL(new Blob([])));</script>
<script src="/assets/js/search.js"></script>
</head><body></body></html>
"""


def _strip(html):
    soup = BeautifulSoup(html, 'html.parser')
    G.remove_wordpress_elements(G, soup)
    return soup


def test_emoji_nodes_removed():
    soup = _strip(EMOJI_HTML)
    s = str(soup)
    assert 'wp-emoji' not in s
    assert '_wpemojiSettings' not in s
    assert 'wp-smiley' not in s


def test_critical_css_and_other_scripts_survive():
    soup = _strip(EMOJI_HTML)
    assert soup.find('style', id='critical-css') is not None
    assert soup.find('script', src='/assets/js/search.js') is not None


def test_no_emoji_is_a_noop():
    html = ('<html><head><style id="critical-css">.x{}</style>'
            '<script src="/a.js"></script></head><body></body></html>')
    soup = _strip(html)
    assert soup.find('style', id='critical-css') is not None
    assert soup.find('script', src='/a.js') is not None
