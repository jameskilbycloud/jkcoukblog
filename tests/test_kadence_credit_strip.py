"""Tests for stripping the Kadence theme footer credit
(wordpress_cleanup.remove_wordpress_elements).

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
