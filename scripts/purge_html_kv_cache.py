#!/usr/bin/env python3
"""
Bulk-purge all html:* entries from the HTML_CACHE KV namespace.

Run this whenever you need to force-refresh the live site from the static
files in public/ — for example, after fixing SEO issues (like canonical tags)
that were corrected in the build output but are still being served from a
stale KV cache.

Usage:
    python3 scripts/purge_html_kv_cache.py [--dry-run]

Required environment variables (same ones used by GitHub Actions):
    CLOUDFLARE_API_TOKEN   — API token with KV:Edit permission
    CLOUDFLARE_ACCOUNT_ID  — Your Cloudflare account ID

Optional:
    KV_NAMESPACE_ID        — Override the HTML_CACHE namespace ID
                             (defaults to the value in wrangler.toml)
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.error

# ── Config ────────────────────────────────────────────────────────────────────

# Namespace ID from wrangler.toml [[kv_namespaces]] binding = "HTML_CACHE"
DEFAULT_NAMESPACE_ID = '5528672ccf0644c9bd65e7de8b629189'

CF_API_BASE = 'https://api.cloudflare.com/client/v4'

# Cloudflare KV bulk delete accepts up to 10,000 keys per request
BULK_DELETE_LIMIT = 10_000


# ── Helpers ───────────────────────────────────────────────────────────────────

def cf_request(method, path, token, account_id, body=None):
    """Make a Cloudflare API request and return parsed JSON."""
    url = f"{CF_API_BASE}/accounts/{account_id}{path}"
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
        }
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body_text = e.read().decode()
        print(f'❌ HTTP {e.code} from Cloudflare API: {body_text}', file=sys.stderr)
        sys.exit(1)


def list_all_keys(token, account_id, namespace_id, prefix='html:'):
    """Page through KV keys with the given prefix, returning all key names."""
    keys = []
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


def bulk_delete(token, account_id, namespace_id, keys, dry_run=False):
    """Delete keys in batches of BULK_DELETE_LIMIT."""
    if not keys:
        print('ℹ️  No keys to delete.')
        return

    if dry_run:
        print(f'🔍 DRY RUN — would delete {len(keys)} keys (no changes made)')
        for k in keys[:20]:
            print(f'   {k}')
        if len(keys) > 20:
            print(f'   … and {len(keys) - 20} more')
        return

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

    print(f'\n✅ Purged {deleted} KV cache entries')
    print('   Cloudflare Pages will now serve fresh HTML from public/ and')
    print('   re-populate the KV cache on the next request to each page.')


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--dry-run', action='store_true',
                        help='List what would be deleted without deleting anything')
    parser.add_argument('--namespace-id', default=None,
                        help='Override KV namespace ID (default: HTML_CACHE from wrangler.toml)')
    args = parser.parse_args()

    token = os.environ.get('CLOUDFLARE_API_TOKEN')
    account_id = os.environ.get('CLOUDFLARE_ACCOUNT_ID')
    namespace_id = args.namespace_id or os.environ.get('KV_NAMESPACE_ID') or DEFAULT_NAMESPACE_ID

    if not token:
        print('❌ CLOUDFLARE_API_TOKEN environment variable is not set.', file=sys.stderr)
        print('   Export it before running this script.', file=sys.stderr)
        sys.exit(1)

    if not account_id:
        print('❌ CLOUDFLARE_ACCOUNT_ID environment variable is not set.', file=sys.stderr)
        print('   Export it before running this script.', file=sys.stderr)
        sys.exit(1)

    print(f'🔑 Using KV namespace: {namespace_id}')
    print(f'{"🔍 DRY RUN — no changes will be made" if args.dry_run else "🗑️  Purging html:* keys from HTML_CACHE…"}')
    print()

    print('Listing all html:* keys…')
    keys = list_all_keys(token, account_id, namespace_id)
    print(f'Found {len(keys)} html:* keys\n')

    bulk_delete(token, account_id, namespace_id, keys, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
