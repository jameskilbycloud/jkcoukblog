"""Tests for the CrUX field-metrics fetcher's pure logic.

Network is never touched — query_crux is exercised with a fake session.
"""

import pytest

from fetch_crux_metrics import assess, parse_crux_record, query_crux


# ── parse_crux_record ──────────────────────────────────────────────────────

def test_parses_all_three_vitals():
    record = {'metrics': {
        'largest_contentful_paint': {'percentiles': {'p75': 1820}},
        'interaction_to_next_paint': {'percentiles': {'p75': '130'}},
        'cumulative_layout_shift': {'percentiles': {'p75': '0.03'}},
    }}
    assert parse_crux_record(record) == {'lcp': 1820, 'inp': 130, 'cls': 0.03}


def test_cls_kept_as_float_timings_as_int():
    record = {'metrics': {
        'largest_contentful_paint': {'percentiles': {'p75': '2500.7'}},
        'cumulative_layout_shift': {'percentiles': {'p75': '0.0'}},
    }}
    out = parse_crux_record(record)
    assert out['lcp'] == 2500 and isinstance(out['lcp'], int)
    assert out['cls'] == 0.0 and isinstance(out['cls'], float)


def test_missing_metrics_omitted_not_errored():
    assert parse_crux_record({'metrics': {}}) == {}
    assert parse_crux_record({}) == {}
    # a metric block with no p75 is skipped
    assert parse_crux_record({'metrics': {
        'largest_contentful_paint': {'percentiles': {}},
    }}) == {}


def test_malformed_value_skipped():
    record = {'metrics': {
        'largest_contentful_paint': {'percentiles': {'p75': 'not-a-number'}},
        'interaction_to_next_paint': {'percentiles': {'p75': 200}},
    }}
    assert parse_crux_record(record) == {'inp': 200}


# ── assess (Google's good/poor thresholds) ─────────────────────────────────

@pytest.mark.parametrize('short,value,expected', [
    ('lcp', 2500, 'good'),               # boundary: <= good
    ('lcp', 2501, 'needs-improvement'),
    ('lcp', 4000, 'needs-improvement'),  # boundary: <= poor
    ('lcp', 4001, 'poor'),
    ('inp', 200, 'good'),
    ('inp', 350, 'needs-improvement'),
    ('inp', 501, 'poor'),
    ('cls', 0.10, 'good'),
    ('cls', 0.20, 'needs-improvement'),
    ('cls', 0.30, 'poor'),
])
def test_assess_thresholds(short, value, expected):
    assert assess(short, value) == expected


# ── query_crux (HTTP layer, faked) ─────────────────────────────────────────

class _FakeResp:
    def __init__(self, status_code, payload=None):
        self.status_code = status_code
        self._payload = payload or {}

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            import requests
            raise requests.HTTPError(f"{self.status_code}")


class _FakeSession:
    def __init__(self, resp):
        self._resp = resp
        self.last_body = None

    def post(self, url, params=None, json=None, timeout=None):
        self.last_body = json
        return self._resp


def test_query_returns_none_on_404_no_data():
    session = _FakeSession(_FakeResp(404))
    assert query_crux(session, 'key', origin='https://x.test') is None


def test_query_returns_record_and_sends_url_when_given():
    payload = {'record': {'metrics': {'cumulative_layout_shift': {'percentiles': {'p75': '0.01'}}}}}
    session = _FakeSession(_FakeResp(200, payload))
    rec = query_crux(session, 'key', url='https://x.test/post/', form_factor='DESKTOP')
    assert rec == payload['record']
    # URL targets must send `url`, not `origin`
    assert session.last_body['url'] == 'https://x.test/post/'
    assert 'origin' not in session.last_body
    assert session.last_body['formFactor'] == 'DESKTOP'


def test_query_raises_on_auth_error():
    import requests
    session = _FakeSession(_FakeResp(403))
    with pytest.raises(requests.HTTPError):
        query_crux(session, 'badkey', origin='https://x.test')
