"""Tests for the shared WordPress session factory."""

from requests.adapters import HTTPAdapter

from wp_session import build_session


def test_auth_and_cf_headers_set():
    s = build_session('dG9rZW4=', 'cf-id', 'cf-secret')
    assert s.headers['Authorization'] == 'Basic dG9rZW4='
    assert s.headers['CF-Access-Client-Id'] == 'cf-id'
    assert s.headers['CF-Access-Client-Secret'] == 'cf-secret'
    assert s.headers['Accept'] == 'application/json'


def test_unauthenticated_session_has_no_auth_header():
    s = build_session()
    assert 'Authorization' not in s.headers
    assert 'CF-Access-Client-Id' not in s.headers


def test_cf_headers_require_both_halves():
    s = build_session('t', 'cf-id', None)
    assert 'CF-Access-Client-Id' not in s.headers


def test_retry_adapter_mounted():
    s = build_session(retries=5)
    adapter = s.get_adapter('https://wordpress.jameskilby.cloud/wp-json/')
    assert isinstance(adapter, HTTPAdapter)
    assert adapter.max_retries.total == 5
    assert 503 in adapter.max_retries.status_forcelist


def test_custom_user_agent():
    s = build_session(user_agent='apply-typo-patches/1.0')
    assert s.headers['User-Agent'] == 'apply-typo-patches/1.0'
