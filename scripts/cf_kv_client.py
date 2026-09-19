#!/usr/bin/env python3
"""Shared Cloudflare Workers KV helpers for the purge_*_kv_cache.py scripts.

scripts/purge_html_kv_cache.py and scripts/purge_soft404_kv_cache.py both
talk to the same Cloudflare API — list keys by prefix, then bulk-delete —
and previously carried separate, drifting copies of this logic. This module
is the one implementation; the two purge scripts differ only in *which*
keys they select for deletion (everything vs. only the soft-404 poisoned
ones).
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request

CF_API_BASE = 'https://api.cloudflare.com/client/v4'

# Namespace ID from wrangler.toml [[kv_namespaces]] binding = "HTML_CACHE"
DEFAULT_HTML_CACHE_NAMESPACE_ID = '5528672ccf0644c9bd65e7de8b629189'

# Cloudflare KV bulk delete accepts up to 10,000 keys per request
BULK_DELETE_LIMIT = 10_000


def cf_request(method: str, path: str, token: str, account_id: str, body=None):
    """Make a Cloudflare API request and return parsed JSON."""
    url = f'{CF_API_BASE}/accounts/{account_id}{path}'
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        },
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode(errors='replace')
        print(f'❌ HTTP {e.code} from Cloudflare API: {body_text}', file=sys.stderr)
        sys.exit(1)


def list_all_keys(token: str, account_id: str, namespace_id: str,
                   prefix: str = 'html:') -> list[str]:
    """Page through KV keys with the given prefix, returning all key names."""
    keys: list[str] = []
    cursor = None
    page = 1

    while True:
        path = f'/storage/kv/namespaces/{namespace_id}/keys?limit=1000&prefix={prefix}'
        if cursor:
            path += f'&cursor={cursor}'

        print(f'  📋 Fetching key page {page}…', end=' ', flush=True)
        result = cf_request('GET', path, token, account_id)

        if not result.get('success'):
            print(f'\n❌ API error: {result.get("errors")}', file=sys.stderr)
            sys.exit(1)

        batch = result.get('result', [])
        keys.extend(k['name'] for k in batch)
        print(f'{len(batch)} keys')

        cursor = result.get('result_info', {}).get('cursor')
        if not cursor or not batch:
            break
        page += 1

    return keys


def bulk_delete(token: str, account_id: str, namespace_id: str, keys: list[str],
                 dry_run: bool = False, preview_limit: int = 20) -> int:
    """Delete keys in batches of BULK_DELETE_LIMIT. Returns the count deleted
    (0 on a dry run — the caller's own dry-run message covers that case)."""
    if not keys:
        print('ℹ️  No keys to delete.')
        return 0

    if dry_run:
        print(f'🔍 DRY RUN — would delete {len(keys)} keys (no changes made)')
        for k in keys[:preview_limit]:
            print(f'   {k}')
        if len(keys) > preview_limit:
            print(f'   … and {len(keys) - preview_limit} more')
        return 0

    deleted = 0
    for i in range(0, len(keys), BULK_DELETE_LIMIT):
        batch = keys[i:i + BULK_DELETE_LIMIT]
        path = f'/storage/kv/namespaces/{namespace_id}/bulk/delete'
        result = cf_request('POST', path, token, account_id, body=batch)
        if result.get('success'):
            deleted += len(batch)
            print(f'  🗑️  Deleted batch of {len(batch)} keys ({deleted}/{len(keys)} total)')
        else:
            print(f'❌ Bulk delete failed: {result.get("errors")}', file=sys.stderr)
            sys.exit(1)

    return deleted
