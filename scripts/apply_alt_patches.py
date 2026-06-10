#!/usr/bin/env python3
"""Apply audit-derived image alt-text fixes to WordPress media library.

Reads `alt-patches.json` at the repo root and, for each entry, locates the
WP media attachment by filename pattern and PATCHes its `alt_text` field via
the REST API.

alt-patches.json shape:

    {
      "patches": [
        {
          "file_pattern": "55f91c39-f0dd-42e1-939a-cdffc92c0b52",
          "new_alt": "Presenting at the London VMUG with my good friend Gareth",
          "note": "About Me featured image; old alt was the filename."
        },
        ...
      ]
    }

Default is DRY-RUN. Pass --apply to actually write.

Auth (env vars):
  WP_AUTH_TOKEN              REQUIRED for --apply. Base64 of "user:application-password".
  CF_ACCESS_CLIENT_ID        Optional. Only needed off-runner.
  CF_ACCESS_CLIENT_SECRET    Optional. Only needed off-runner.

On the self-hosted runner, CF Access is handled at the network layer and
the two CF_ vars are NOT required — same pattern as apply_typo_patches.py.

Usage:
  python3 scripts/apply_alt_patches.py                          # dry-run
  python3 scripts/apply_alt_patches.py --apply                  # apply all
  python3 scripts/apply_alt_patches.py --apply --pattern 55f9   # one only
"""
from __future__ import annotations
import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

from config import Config
from wp_session import build_session as _build_session

REPO_ROOT = Path(__file__).resolve().parent.parent
PATCHES_PATH = REPO_ROOT / 'alt-patches.json'

WP_URL = Config.WP_URL


def build_session(auth_token: str, cf_id: str | None, cf_secret: str | None) -> requests.Session:
    return _build_session(auth_token, cf_id, cf_secret,
                          user_agent='apply-alt-patches/1.0')


def find_media(session: requests.Session, file_pattern: str) -> dict | None:
    """Locate a media attachment by filename pattern.

    Strategy: page through /wp/v2/media (slug field) looking for a slug or
    source_url containing the pattern. We don't use ?search= because that
    matches title/caption too and can return false positives.
    """
    page = 1
    while page <= 20:  # safety cap — 20×100 = 2000 attachments
        resp = session.get(
            f'{WP_URL}/wp-json/wp/v2/media',
            params={'per_page': 100, 'page': page, 'context': 'edit',
                    '_fields': 'id,slug,source_url,alt_text,title,caption'},
        )
        if resp.status_code != 200:
            print(f'   ❌ GET /media?page={page} → {resp.status_code}: {resp.text[:200]}', file=sys.stderr)
            return None
        items = resp.json()
        if not items:
            return None
        for it in items:
            slug = (it.get('slug') or '').lower()
            src = (it.get('source_url') or '').lower()
            if file_pattern.lower() in slug or file_pattern.lower() in src:
                return it
        if len(items) < 100:
            return None
        page += 1
    return None


def patch_alt(session: requests.Session, media_id: int, new_alt: str) -> bool:
    resp = session.post(
        f'{WP_URL}/wp-json/wp/v2/media/{media_id}',
        json={'alt_text': new_alt},
    )
    if resp.status_code == 200:
        # WP returns the updated attachment; confirm the field actually changed.
        returned_alt = (resp.json().get('alt_text') or '').strip()
        if returned_alt == new_alt:
            return True
        print(f'   ⚠️  POST returned 200 but alt_text in response is {returned_alt!r} (expected {new_alt!r})', file=sys.stderr)
        return False
    print(f'   ❌ POST /media/{media_id} → {resp.status_code}: {resp.text[:200]}', file=sys.stderr)
    return False


def process_patch(session: requests.Session, patch: dict, apply_changes: bool) -> dict:
    pattern = patch['file_pattern']
    new_alt = patch['new_alt']
    note = patch.get('note', '')

    print(f'\n=== pattern: {pattern} ===')
    if note:
        print(f'   note: {note}')

    media = find_media(session, pattern)
    if not media:
        print(f'   ❌ no media attachment matched the pattern')
        return {'pattern': pattern, 'resolved': False, 'applied': False}

    media_id = media['id']
    current_alt = (media.get('alt_text') or '').strip()
    src = media.get('source_url') or media.get('slug') or '(unknown)'
    print(f'   → media id={media_id}  src={src}')
    print(f'   current alt: {current_alt!r}')
    print(f'   new alt:     {new_alt!r}')

    if current_alt == new_alt:
        print(f'   ✓ already correct — no change needed')
        return {'pattern': pattern, 'resolved': True, 'applied': False, 'noop': True}

    if not apply_changes:
        print(f'   [DRY RUN] would PATCH alt_text on media {media_id}')
        return {'pattern': pattern, 'resolved': True, 'applied': False, 'media_id': media_id}

    print(f'   → PATCHing alt_text on media {media_id}...')
    ok = patch_alt(session, media_id, new_alt)
    if ok:
        print(f'   ✅ written')
        time.sleep(0.5)
        return {'pattern': pattern, 'resolved': True, 'applied': True, 'media_id': media_id}
    return {'pattern': pattern, 'resolved': True, 'applied': False, 'media_id': media_id, 'wp_error': True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--apply', action='store_true', help='actually write changes to WordPress')
    ap.add_argument('--pattern', help='only process patches whose file_pattern contains this substring')
    args = ap.parse_args()

    if not PATCHES_PATH.exists():
        print(f'No patch file at {PATCHES_PATH}', file=sys.stderr)
        return 1

    data = json.loads(PATCHES_PATH.read_text())
    patches = data.get('patches', [])
    if args.pattern:
        patches = [p for p in patches if args.pattern in p.get('file_pattern', '')]

    auth = os.environ.get('WP_AUTH_TOKEN', '')
    cf_id = os.environ.get('CF_ACCESS_CLIENT_ID', '')
    cf_secret = os.environ.get('CF_ACCESS_CLIENT_SECRET', '')

    if args.apply and not auth:
        print('❌ --apply requires the WP_AUTH_TOKEN env var', file=sys.stderr)
        return 2

    session = build_session(auth, cf_id, cf_secret)

    print(f'Mode: {"APPLY (writing to WP)" if args.apply else "DRY RUN"}')
    print(f'Target: {WP_URL}')
    print(f'Patches to process: {len(patches)}')

    results = []
    for p in patches:
        try:
            results.append(process_patch(session, p, args.apply))
        except Exception as e:
            print(f'   💥 exception: {e}', file=sys.stderr)
            results.append({'pattern': p.get('file_pattern'), 'resolved': False, 'applied': False, 'error': str(e)})

    print()
    print('=' * 60)
    print(f'Patches processed:  {len(results)}')
    print(f'Resolved:           {sum(1 for r in results if r.get("resolved"))}')
    print(f'{"Written" if args.apply else "Would write"}: {sum(1 for r in results if r.get("applied") or r.get("media_id"))}')
    print(f'No-op (already correct): {sum(1 for r in results if r.get("noop"))}')
    print(f'Errors:             {sum(1 for r in results if r.get("wp_error") or r.get("error"))}')
    print('=' * 60)

    log_path = REPO_ROOT / 'alt-patches-applied.log.json'
    log_path.write_text(json.dumps(results, indent=2))
    print(f'log: {log_path}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
