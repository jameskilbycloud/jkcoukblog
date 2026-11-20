"""Tests for wordpress_cleanup.remove_wordpress_elements: the Kadence theme
footer credit, and a sweep over every other WordPress artifact it strips.

The WordPress footer ends with "WordPress Theme by Kadence WP". It must never
reach the static site, whether Kadence renders it as a link to kadencewp.com
or as plain text, and the site's own footer row must survive.
"""

from bs4 import BeautifulSoup

from wordpress_cleanup import WordPressCleanup as G

FOOTER = """
<footer><div class="site-info-inner"><div class="footer-html-inner">
<p>&copy; 2026 James Kilby {credit}</p>
<div class="jk-footer-row"><span class="jk-footer-copy">James Kilby</span></div>
</div></div></footer>
"""


def _strip(credit):
    soup = BeautifulSoup(FOOTER.format(credit=credit), 'html.parser')
    G.remove_wordpress_elements(G, soup)
    return soup


def _assert_clean(soup):
    text = soup.get_text()
    assert 'Kadence' not in text
    assert 'Theme by' not in text
    assert soup.find(class_='jk-footer-row') is not None


def test_linked_credit_removed():
    _assert_clean(_strip(
        '- WordPress Theme by <a href="https://www.kadencewp.com/" rel="nofollow noopener">Kadence WP</a>'))


def test_plain_text_credit_removed():
    _assert_clean(_strip('- WordPress Theme by Kadence WP'))


def test_credit_link_outside_paragraph_removed():
    soup = BeautifulSoup(
        '<footer><span>Theme: <a href="https://kadencewp.com/">Kadence WP</a></span>'
        '<div class="jk-footer-row">James Kilby</div></footer>', 'html.parser')
    G.remove_wordpress_elements(G, soup)
    assert 'Kadence' not in soup.get_text()
    assert soup.find(class_='jk-footer-row') is not None


WP_PAGE = """
<html><head>
<meta name="generator" content="WordPress 6.8">
<link rel="https://api.w.org/" href="https://wp.example/wp-json/">
<link rel="EditURI" type="application/rsd+xml" href="https://wp.example/xmlrpc.php?rsd">
<link rel="pingback" href="https://wp.example/xmlrpc.php">
<link rel="wlwmanifest" href="https://wp.example/wlwmanifest.xml">
<script src="https://wp.example/wp-includes/js/wp-embed.min.js"></script>
<script>window._wpemojiSettings={};</script>
<link rel="stylesheet" href="/assets/css/site.css">
</head><body>
<div id="wpadminbar">admin</div>
<!-- Search Engine Optimization by Rank Math - https://rankmath.com/ -->
<main><p>Post body stays.</p></main>
<!-- /Rank Math WordPress SEO plugin -->
<footer><p>WordPress Theme by <a href="https://www.kadencewp.com/">Kadence WP</a></p></footer>
</body></html>
"""


def test_every_wordpress_artifact_removed():
    soup = BeautifulSoup(WP_PAGE, 'html.parser')
    G.remove_wordpress_elements(G, soup)
    html = str(soup)
    for leftover in ('generator', 'api.w.org', 'EditURI', 'pingback', 'wlwmanifest',
                     'wp-embed', '_wpemojiSettings', 'wpadminbar', 'Rank Math', 'Kadence'):
        assert leftover not in html, leftover
    assert 'Post body stays.' in html
    assert soup.find('link', href='/assets/css/site.css') is not None


def test_remove_kadence_credit_reports_whether_it_removed():
    soup = BeautifulSoup('<footer><p>WordPress Theme by Kadence WP</p></footer>', 'html.parser')
    assert G.remove_kadence_credit(soup) is True
    assert G.remove_kadence_credit(soup) is False


def test_rank_math_phrase_in_post_text_is_kept():
    soup = BeautifulSoup('<main><p>Search Engine Optimization by Rank Math is a plugin.</p></main>',
                         'html.parser')
    G.remove_wordpress_elements(G, soup)
    assert 'Search Engine Optimization by Rank Math is a plugin.' in soup.get_text()
