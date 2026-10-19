"""Tests for stripping WordPress <link> header tags that are broken or
misleading on the static site (wordpress_cleanup.remove_wordpress_elements).

- rel="EditURI" (RSD) and rel="pingback" point at xmlrpc.php, which 404s.
- rel="shortlink" points at /?p=ID; the static site ignores the query string
  and serves the homepage, a misleading 200.
Canonical and stylesheet links must survive.
"""

from bs4 import BeautifulSoup

from wordpress_cleanup import WordPressCleanup as G

HEAD_HTML = """
<html><head>
<link rel="canonical" href="https://jameskilby.co.uk/2018/04/nutanix-life-cycle-manager/">
<link rel="stylesheet" href="/assets/css/site.css">
<link rel="EditURI" type="application/rsd+xml" href="https://wordpress.jameskilby.cloud/xmlrpc.php?rsd">
<link rel="pingback" href="https://wordpress.jameskilby.cloud/xmlrpc.php">
<link rel="shortlink" href="https://jameskilby.co.uk/?p=123">
</head><body></body></html>
"""


def _strip(html):
    soup = BeautifulSoup(html, 'html.parser')
    G.remove_wordpress_elements(G, soup)
    return soup


def test_pingback_and_shortlink_removed():
    s = str(_strip(HEAD_HTML))
    assert 'rel="pingback"' not in s
    assert 'rel="shortlink"' not in s
    assert '?p=123' not in s


def test_edituri_still_removed():
    s = str(_strip(HEAD_HTML))
    assert 'EditURI' not in s
    assert 'xmlrpc.php' not in s


def test_canonical_and_stylesheet_survive():
    soup = _strip(HEAD_HTML)
    assert soup.find('link', rel='canonical') is not None
    assert soup.find('link', rel='stylesheet') is not None
