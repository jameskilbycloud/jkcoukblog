"""Tests for the SEO drift baseline's pure logic."""

from drift_baseline import build_snapshot, diff_signals, extract_signals

POST_HTML = """
<html><head>
<title>How to do a thing - James Kilby</title>
<link rel="canonical" href="https://jameskilby.co.uk/2024/10/foo/">
<meta name="description" content="A description.">
<meta property="og:title" content="How to do a thing">
<meta property="og:description" content="A description.">
<meta property="og:image" content="https://jameskilby.co.uk/img.png">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{"@graph":[{"@type":"TechArticle","headline":"x"},{"@type":"Person","name":"James Kilby"},
{"@type":"BreadcrumbList"}]}
</script>
</head><body><h1>How to do a thing</h1></body></html>
"""


def test_extract_signals_happy_path():
    sig = extract_signals(POST_HTML)
    assert sig['title_has_brand_suffix'] is True
    assert sig['h1_count'] == 1
    assert sig['has_canonical'] is True
    assert sig['canonical_absolute'] is True
    assert sig['has_meta_description'] is True
    assert sig['has_og_image'] is True
    assert sig['robots_noindex'] is False
    assert sig['jsonld_types'] == ['BreadcrumbList', 'Person', 'TechArticle']
    assert sig['wp_host_leak'] is False


def test_wp_host_leak_detected():
    html = '<html><body>see https://wordpress.jameskilby.cloud/wp-json/</body></html>'
    assert extract_signals(html)['wp_host_leak'] is True


def test_noindex_detected():
    html = '<html><head><meta name="robots" content="noindex,follow"></head></html>'
    assert extract_signals(html)['robots_noindex'] is True


def test_jsonld_types_handles_malformed_block():
    html = '<html><head><script type="application/ld+json">{bad json</script></head></html>'
    assert extract_signals(html)['jsonld_types'] == []


def test_diff_reports_only_changed_signals():
    old = {'/2024/10/foo/': {'has_canonical': True, 'h1_count': 1}}
    new = {'/2024/10/foo/': {'has_canonical': False, 'h1_count': 1}}
    drifted, missing = diff_signals(old, new)
    assert missing == []
    assert drifted == {'/2024/10/foo/': {'has_canonical': [True, False]}}


def test_diff_reports_missing_pages():
    old = {'/gone/': {'h1_count': 1}, '/stays/': {'h1_count': 1}}
    new = {'/stays/': {'h1_count': 1}}
    drifted, missing = diff_signals(old, new)
    assert drifted == {}
    assert missing == ['/gone/']


def test_diff_is_clean_when_identical():
    sig = extract_signals(POST_HTML)
    drifted, missing = diff_signals({'/2024/10/foo/': sig}, {'/2024/10/foo/': sig})
    assert drifted == {} and missing == []


def test_build_snapshot_selects_home_and_posts(tmp_path):
    # homepage + a post + a non-post page; only home and post are baselined.
    (tmp_path / 'index.html').write_text(POST_HTML, encoding='utf-8')
    post = tmp_path / '2024' / '10' / 'foo'
    post.mkdir(parents=True)
    (post / 'index.html').write_text(POST_HTML, encoding='utf-8')
    archive = tmp_path / 'category' / 'aws'
    archive.mkdir(parents=True)
    (archive / 'index.html').write_text(POST_HTML, encoding='utf-8')

    snap = build_snapshot(tmp_path)
    assert set(snap['pages']) == {'/', '/2024/10/foo/'}
    assert snap['page_count'] == 2
