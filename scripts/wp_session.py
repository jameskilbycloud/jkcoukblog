#!/usr/bin/env python3
"""
Shared WordPress REST API session factory.

Single source of truth for how scripts talk to the (Cloudflare Access
protected) WordPress instance: Basic auth header, CF Access service-token
headers, and retry/backoff on transient failures. Import this instead of
hand-rolling a requests.Session per script.

Usage:
    from wp_session import build_session

    session = build_session(auth_token, cf_id, cf_secret)
    # or pull everything from the environment:
    session = build_session_from_env()
"""

import os

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Transient statuses worth retrying: rate limit + upstream hiccups. 4xx auth
# errors are NOT retried — they will not heal and retrying delays the real
# error message.
_RETRY_STATUSES = (429, 500, 502, 503, 504)


def build_session(auth_token: str | None = None,
                  cf_id: str | None = None,
                  cf_secret: str | None = None,
                  user_agent: str = 'jkcoukblog-scripts/1.0',
                  retries: int = 3) -> requests.Session:
    """Build a requests.Session for the WordPress REST API.

    auth_token: base64 of "user:application-password" (Basic auth), or None
                for unauthenticated reads.
    cf_id/cf_secret: Cloudflare Access service-token pair — only needed when
                running off the self-hosted runner.
    retries: attempts per request on connect errors and _RETRY_STATUSES,
             with exponential backoff (0.5s, 1s, 2s ...).
    """
    s = requests.Session()
    s.headers.update({
        'User-Agent': user_agent,
        'Accept': 'application/json',
    })
    if auth_token:
        s.headers['Authorization'] = f'Basic {auth_token}'
    if cf_id and cf_secret:
        s.headers['CF-Access-Client-Id'] = cf_id
        s.headers['CF-Access-Client-Secret'] = cf_secret

    retry = Retry(
        total=retries,
        backoff_factor=0.5,
        status_forcelist=_RETRY_STATUSES,
        allowed_methods=None,  # retry POST too — WP REST updates are idempotent per-id
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    s.mount('https://', adapter)
    s.mount('http://', adapter)
    return s


def build_session_from_env(user_agent: str = 'jkcoukblog-scripts/1.0') -> requests.Session:
    """build_session() reading WP_AUTH_TOKEN / CF_ACCESS_CLIENT_* from the env."""
    return build_session(
        auth_token=os.environ.get('WP_AUTH_TOKEN') or None,
        cf_id=os.environ.get('CF_ACCESS_CLIENT_ID') or None,
        cf_secret=os.environ.get('CF_ACCESS_CLIENT_SECRET') or None,
        user_agent=user_agent,
    )
