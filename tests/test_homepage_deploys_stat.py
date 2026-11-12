"""homepage_redesign: the "deploys/mo" ribbon stat counts deploy runs.

It used to count every commit on main this month, which stopped meaning
anything once the built site moved to the `site` branch.
"""

import requests

from config import Config
from homepage_redesign import HomepageRedesign


class _Resp:
    def __init__(self, payload, status=200):
        self._payload, self.status_code = payload, status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(f'{self.status_code}')

    def json(self):
        return self._payload


def _stat(monkeypatch, response):
    calls = []

    def fake_get(url, **kwargs):
        calls.append((url, kwargs))
        if isinstance(response, Exception):
            raise response
        return response

    monkeypatch.setattr(requests, 'get', fake_get)
    monkeypatch.delenv('GITHUB_TOKEN', raising=False)
    redesign = HomepageRedesign.__new__(HomepageRedesign)   # no WP session needed
    return redesign._stat_deploys_this_month(), calls


def test_counts_successful_deploy_runs_this_month(monkeypatch):
    value, calls = _stat(monkeypatch, _Resp({'total_count': 17}))

    assert value == '17'
    url, kwargs = calls[0]
    assert url == (f'https://api.github.com/repos/{Config.GITHUB_REPO}'
                   '/actions/workflows/deploy-static-site.yml/runs')
    assert kwargs['params']['status'] == 'success'
    assert kwargs['params']['created'].startswith('>=') and kwargs['params']['created'].endswith('-01')
    assert 'Authorization' not in kwargs['headers']


def test_uses_github_token_when_present(monkeypatch):
    seen = {}

    def fake_get(url, **kwargs):
        seen.update(kwargs['headers'])
        return _Resp({'total_count': 1})

    monkeypatch.setattr(requests, 'get', fake_get)
    monkeypatch.setenv('GITHUB_TOKEN', 't0k')
    HomepageRedesign.__new__(HomepageRedesign)._stat_deploys_this_month()
    assert seen['Authorization'] == 'Bearer t0k'


def test_api_failure_shows_a_dash(monkeypatch):
    assert _stat(monkeypatch, _Resp({}, status=403))[0] == '—'
    assert _stat(monkeypatch, requests.ConnectionError('offline'))[0] == '—'
