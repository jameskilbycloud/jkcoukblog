"""Tests for WordPressSourceValidator's pure validation logic.

Network calls go through self._make_api_request() / self._fetch_all_paginated(),
so these tests monkeypatch those seams with canned data rather than mocking
requests/HTTP — constructing a validator itself never touches the network
(build_session just builds a requests.Session with retry adapters mounted).
"""

import json

import pytest

from validate_wordpress_source import WordPressSourceValidator


@pytest.fixture
def validator():
    return WordPressSourceValidator('https://wp.test', 'faketoken', skip_seo=False)


class FakeResponse:
    def __init__(self, status_code=200, json_data=None, headers=None, text=''):
        self.status_code = status_code
        self._json_data = json_data
        self.headers = headers or {}
        self.text = text

    def json(self):
        return self._json_data


# ── _fetch_all_paginated ─────────────────────────────────────────────────

class TestFetchAllPaginated:
    def test_single_page_stops_at_total_pages(self, validator, monkeypatch):
        calls = []

        def fake_request(endpoint, params=None, method='GET'):
            calls.append(dict(params))
            return FakeResponse(200, [{'id': 1}, {'id': 2}],
                               {'X-WP-TotalPages': '1'}), None

        monkeypatch.setattr(validator, '_make_api_request', fake_request)
        items = validator._fetch_all_paginated('/wp-json/wp/v2/posts')
        assert [i['id'] for i in items] == [1, 2]
        assert len(calls) == 1

    def test_multi_page_aggregates_all_pages(self, validator, monkeypatch):
        pages = {
            1: FakeResponse(200, [{'id': 1}], {'X-WP-TotalPages': '3'}),
            2: FakeResponse(200, [{'id': 2}], {'X-WP-TotalPages': '3'}),
            3: FakeResponse(200, [{'id': 3}], {'X-WP-TotalPages': '3'}),
        }

        def fake_request(endpoint, params=None, method='GET'):
            return pages[params['page']], None

        monkeypatch.setattr(validator, '_make_api_request', fake_request)
        items = validator._fetch_all_paginated('/wp-json/wp/v2/posts')
        assert [i['id'] for i in items] == [1, 2, 3]

    def test_400_ends_pagination_without_error(self, validator, monkeypatch):
        def fake_request(endpoint, params=None, method='GET'):
            if params['page'] == 1:
                return FakeResponse(200, [{'id': 1}], {'X-WP-TotalPages': '5'}), None
            return FakeResponse(400), None

        monkeypatch.setattr(validator, '_make_api_request', fake_request)
        items = validator._fetch_all_paginated('/wp-json/wp/v2/posts')
        assert [i['id'] for i in items] == [1]

    def test_request_error_stops_and_keeps_prior_pages(self, validator, monkeypatch):
        def fake_request(endpoint, params=None, method='GET'):
            if params['page'] == 1:
                return FakeResponse(200, [{'id': 1}], {'X-WP-TotalPages': '5'}), None
            return None, 'Connection error'

        monkeypatch.setattr(validator, '_make_api_request', fake_request)
        items = validator._fetch_all_paginated('/wp-json/wp/v2/posts')
        assert [i['id'] for i in items] == [1]

    def test_empty_first_page_returns_empty_list(self, validator, monkeypatch):
        monkeypatch.setattr(
            validator, '_make_api_request',
            lambda endpoint, params=None, method='GET': (FakeResponse(200, []), None)
        )
        assert validator._fetch_all_paginated('/wp-json/wp/v2/posts') == []


# ── _check_endpoint_health ───────────────────────────────────────────────

class TestCheckEndpointHealth:
    def test_healthy_endpoint_returns_true_and_logs_no_error(self, validator, monkeypatch):
        monkeypatch.setattr(
            validator, '_make_api_request',
            lambda endpoint, params=None, method='GET':
                (FakeResponse(200, headers={'X-WP-Total': '42'}), None)
        )
        assert validator._check_endpoint_health('/wp-json/wp/v2/posts', 'Posts') is True
        assert validator.errors == []

    def test_connection_error_records_error(self, validator, monkeypatch):
        monkeypatch.setattr(
            validator, '_make_api_request',
            lambda endpoint, params=None, method='GET': (None, 'Connection refused')
        )
        assert validator._check_endpoint_health('/wp-json/wp/v2/posts', 'Posts') is False
        assert validator.errors[0]['type'] == 'endpoint_unreachable'

    def test_non_200_status_records_error(self, validator, monkeypatch):
        monkeypatch.setattr(
            validator, '_make_api_request',
            lambda endpoint, params=None, method='GET': (FakeResponse(500, text='boom'), None)
        )
        assert validator._check_endpoint_health('/wp-json/wp/v2/posts', 'Posts') is False
        assert validator.errors[0]['type'] == 'endpoint_error'


# ── validate_posts ───────────────────────────────────────────────────────

def _post(**overrides):
    base = {
        'id': 1,
        'title': {'rendered': 'A perfectly reasonable 45-char post title'},
        'link': 'https://wp.test/a-post/',
        'featured_media': 10,
        'categories': [1],
        'tags': [1, 2],
        'excerpt': {'rendered': '<p>' + ('x' * 140) + '</p>'},
    }
    base.update(overrides)
    return base


class TestValidatePosts:
    def _validator_with_posts(self, validator, monkeypatch, posts):
        validator.cache['media_ids'] = {10}
        validator.cache['categories'] = {1: {'id': 1}}
        validator.cache['tags'] = {1: {'id': 1}, 2: {'id': 2}}
        monkeypatch.setattr(validator, '_fetch_all_paginated', lambda *a, **kw: posts)
        return validator

    def test_clean_post_produces_no_findings(self, validator, monkeypatch):
        self._validator_with_posts(validator, monkeypatch, [_post()])
        validator.validate_posts()
        assert validator.errors == []
        assert validator.warnings == []
        assert validator.stats['total_posts'] == 1

    def test_missing_featured_image_warns(self, validator, monkeypatch):
        self._validator_with_posts(validator, monkeypatch, [_post(featured_media=0)])
        validator.validate_posts()
        assert [w['type'] for w in validator.warnings] == ['missing_featured_image']

    def test_broken_featured_image_errors(self, validator, monkeypatch):
        self._validator_with_posts(validator, monkeypatch, [_post(featured_media=999)])
        validator.validate_posts()
        assert validator.errors[0]['type'] == 'broken_featured_image'
        assert validator.errors[0]['media_id'] == 999

    def test_missing_categories_warns(self, validator, monkeypatch):
        self._validator_with_posts(validator, monkeypatch, [_post(categories=[])])
        validator.validate_posts()
        assert 'missing_categories' in [w['type'] for w in validator.warnings]

    def test_broken_category_errors(self, validator, monkeypatch):
        self._validator_with_posts(validator, monkeypatch, [_post(categories=[999])])
        validator.validate_posts()
        assert validator.errors[0]['type'] == 'broken_category'
        assert validator.errors[0]['category_id'] == 999

    def test_missing_tags_warns(self, validator, monkeypatch):
        self._validator_with_posts(validator, monkeypatch, [_post(tags=[])])
        validator.validate_posts()
        assert 'missing_tags' in [w['type'] for w in validator.warnings]

    def test_tag_count_out_of_range_warns(self, validator, monkeypatch):
        self._validator_with_posts(validator, monkeypatch, [_post(tags=[1])])
        validator.validate_posts()
        assert [w['type'] for w in validator.warnings] == ['tags_out_of_range']

    def test_broken_tag_errors(self, validator, monkeypatch):
        self._validator_with_posts(validator, monkeypatch, [_post(tags=[1, 999])])
        validator.validate_posts()
        assert validator.errors[0]['type'] == 'broken_tag'
        assert validator.errors[0]['tag_id'] == 999

    @pytest.mark.parametrize('length,expected_type', [
        (10, 'seo_title_short'),
        (75, 'seo_title_long'),
    ])
    def test_title_length_seo_bounds(self, validator, monkeypatch, length, expected_type):
        title = 'x' * length
        self._validator_with_posts(validator, monkeypatch, [_post(title={'rendered': title})])
        validator.validate_posts()
        assert expected_type in [w['type'] for w in validator.warnings]

    @pytest.mark.parametrize('excerpt_len,expected_type', [
        (0, 'seo_excerpt_missing'),
        (50, 'seo_excerpt_short'),
        (200, 'seo_excerpt_long'),
    ])
    def test_excerpt_length_seo_bounds(self, validator, monkeypatch, excerpt_len, expected_type):
        excerpt_html = '<p>' + ('x' * excerpt_len) + '</p>' if excerpt_len else ''
        self._validator_with_posts(
            validator, monkeypatch, [_post(excerpt={'rendered': excerpt_html})]
        )
        validator.validate_posts()
        assert expected_type in [w['type'] for w in validator.warnings]

    def test_skip_seo_suppresses_seo_warnings(self, validator, monkeypatch):
        validator.skip_seo = True
        self._validator_with_posts(
            validator, monkeypatch, [_post(title={'rendered': 'x'}, excerpt={'rendered': ''})]
        )
        validator.validate_posts()
        seo_types = [w['type'] for w in validator.warnings if w['type'].startswith('seo_')]
        assert seo_types == []

    def test_no_posts_warns_and_leaves_stats_unset(self, validator, monkeypatch):
        monkeypatch.setattr(validator, '_fetch_all_paginated', lambda *a, **kw: [])
        validator.validate_posts()
        assert [w['type'] for w in validator.warnings] == ['no_posts']
        assert 'total_posts' not in validator.stats


# ── generate_report / status ─────────────────────────────────────────────

class TestGenerateReport:
    def test_status_pass_with_no_errors(self, validator, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        report = validator.generate_report()
        assert report['summary']['status'] == 'PASS'
        assert report['summary']['errors'] == 0

    def test_status_fail_when_errors_present(self, validator, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        validator.errors.append({'type': 'broken_tag', 'message': 'x'})
        report = validator.generate_report()
        assert report['summary']['status'] == 'FAIL'
        assert report['summary']['errors'] == 1

    def test_report_written_to_disk_as_valid_json(self, validator, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        validator.generate_report()
        written = json.loads((tmp_path / 'wordpress-source-validation.json').read_text())
        assert written['wordpress_url'] == 'https://wp.test'


# ── warning/error type categorisation stays complete ─────────────────────

def test_every_warning_type_is_categorised_or_falls_back_to_other():
    """_print_warning_rollup categorises known types and buckets the rest
    under "Other" — harmless, but it silently loses the triage-friendly
    roll-up the comment above _WARNING_CATEGORIES asks contributors to keep
    updated. This lists every 'type' literal actually used in the file's
    warnings/errors and fails if one isn't registered, so a newly added
    warning can't fall into "Other" by accident.
    """
    import inspect
    import re

    import validate_wordpress_source as mod

    src = inspect.getsource(mod)
    used_types = set(re.findall(r"'type':\s*'([a-z_]+)'", src))

    categorised = {
        t for types in WordPressSourceValidator._WARNING_CATEGORIES.values()
        for t in types
    }

    missing = used_types - categorised
    assert not missing, (
        f"warning/error types used but not in _WARNING_CATEGORIES "
        f"(will silently land in 'Other'): {sorted(missing)}"
    )
