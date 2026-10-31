"""Tests for validate_seo's content-page rules (noindex, author, dates)."""

import json

from validate_seo import validate_page


def _write(tmp_path, rel, robots, graph):
    path = tmp_path / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    ld = json.dumps({'@context': 'https://schema.org', '@graph': graph})
    path.write_text(
        '<html><head><title>A page title that is long enough</title>'
        '<meta name="description" content="' + 'd' * 130 + '">'
        f'<meta name="robots" content="{robots}">'
        f'<script type="application/ld+json">{ld}</script></head>'
        '<body><h1>x</h1></body></html>', encoding='utf-8')
    return path


PERSON_ID = 'https://jameskilby.co.uk/#person'


def _categories(issues, severity=None):
    return {i.category for i in issues if severity is None or i.severity == severity}


def test_noindex_on_article_hub_page_fails(tmp_path):
    path = _write(tmp_path, 'evs/index.html', 'noindex,follow',
                  [{'@type': 'Article', 'headline': 'EVS'}])
    assert 'noindex-on-article' in _categories(validate_page(path, tmp_path), 'error')


def test_noindex_allowlisted_page_passes(tmp_path):
    path = _write(tmp_path, 'privacy-policy-2/index.html', 'noindex,follow',
                  [{'@type': 'Article', 'headline': 'Privacy'}])
    assert 'noindex-on-article' not in _categories(validate_page(path, tmp_path))


def test_noindex_without_article_passes(tmp_path):
    path = _write(tmp_path, 'tag/x/index.html', 'noindex,follow', [{'@type': 'CollectionPage'}])
    assert 'noindex-on-article' not in _categories(validate_page(path, tmp_path))


def test_wp_author_id_fails(tmp_path):
    path = _write(tmp_path, 'lab/index.html', 'index, follow', [
        {'@type': 'Article', 'headline': 'Lab',
         'author': {'@id': 'https://jameskilby.co.uk/author/admin/', 'name': 'James'}}])
    assert 'jsonld-author-not-person' in _categories(validate_page(path, tmp_path), 'error')


def test_person_author_and_offset_dates_pass(tmp_path):
    path = _write(tmp_path, 'lab/index.html', 'index, follow', [
        {'@type': 'Article', 'headline': 'Lab', 'author': {'@id': PERSON_ID},
         'datePublished': '2025-01-01T10:00:00+00:00', 'dateModified': '2025-02-01T10:00:00+00:00'}])
    cats = _categories(validate_page(path, tmp_path))
    assert not cats & {'jsonld-author-not-person', 'jsonld-date-no-offset'}


def test_naive_date_warns(tmp_path):
    path = _write(tmp_path, 'lab/index.html', 'index, follow', [
        {'@type': 'Article', 'headline': 'Lab', 'author': {'@id': PERSON_ID},
         'datePublished': '2025-01-01T10:00:00'}])
    assert 'jsonld-date-no-offset' in _categories(validate_page(path, tmp_path), 'warning')
