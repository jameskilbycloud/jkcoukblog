#!/usr/bin/env python3
"""Fetch real Core Web Vitals field data from the Chrome UX Report (CrUX) API.

Replaces the lab/estimate perf score in the SEO audit with *field* data —
the p75 LCP / INP / CLS that real Chrome users experienced on the site over
the trailing 28-day window. This is what Google actually uses for the
page-experience signal, so it's the only number worth tuning against.

Why CrUX and not PageSpeed/Lighthouse: the CrUX REST API needs only a simple
API key (no OAuth), returns origin- and URL-level field data directly, and is
free. GSC query-level data would need OAuth and is a possible follow-up.

Usage:
    export CRUX_API_KEY=...                 # https://goo.gle/crux-api-key
    python3 scripts/fetch_crux_metrics.py                 # origin, PHONE
    python3 scripts/fetch_crux_metrics.py --form-factor DESKTOP
    python3 scripts/fetch_crux_metrics.py --url https://jameskilby.co.uk/2024/10/foo/
    python3 scripts/fetch_crux_metrics.py --out docs/seo-audit-2026-06/crux-latest.json

Exit codes:
    0  ran successfully (even if some targets had no field data — low-traffic
       URLs legitimately return "no data")
    1  hard failure (missing API key, auth error, network/API error)
"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from config import Config
    DEFAULT_ORIGIN = Config.TARGET_DOMAIN
except (ImportError, AttributeError):
    DEFAULT_ORIGIN = 'https://jameskilby.co.uk'

CRUX_ENDPOINT = 'https://chromeuxreport.googleapis.com/v1/records:queryRecord'

# The three Core Web Vitals, mapped to their CrUX metric keys.
CWV_METRICS = {
    'largest_contentful_paint': 'lcp',
    'interaction_to_next_paint': 'inp',
    'cumulative_layout_shift': 'cls',
}

# Google's "good" / "poor" p75 thresholds. Between the two is "needs
# improvement". LCP/INP are milliseconds; CLS is unitless.
THRESHOLDS = {
    'lcp': (2500, 4000),
    'inp': (200, 500),
    'cls': (0.10, 0.25),
}


def parse_crux_record(record):
    """Extract the p75 of each Core Web Vital from a CrUX ``record`` object.

    Returns a dict like ``{'lcp': 1820, 'inp': 130, 'cls': 0.03}``; metrics
    absent from the record are simply omitted. Pure — no I/O.
    """
    metrics = record.get('metrics', {}) if isinstance(record, dict) else {}
    out = {}
    for crux_key, short in CWV_METRICS.items():
        block = metrics.get(crux_key)
        if not isinstance(block, dict):
            continue
        p75 = block.get('percentiles', {}).get('p75')
        if p75 is None:
            continue
        # CrUX returns CLS as a string ("0.05") and timings as ints/strings.
        try:
            out[short] = float(p75) if short == 'cls' else int(float(p75))
        except (TypeError, ValueError):
            continue
    return out


def assess(short, value):
    """Classify a p75 value as 'good' / 'needs-improvement' / 'poor'."""
    good, poor = THRESHOLDS[short]
    if value <= good:
        return 'good'
    if value <= poor:
        return 'needs-improvement'
    return 'poor'


def _fmt(short, value):
    return f"{value:.2f}" if short == 'cls' else f"{value} ms"


def query_crux(session, api_key, *, origin=None, url=None, form_factor='PHONE'):
    """Query the CrUX API for one origin or URL.

    Returns the parsed ``record`` dict, or ``None`` when CrUX has insufficient
    field data for the target (the API signals this with HTTP 404). Raises
    ``requests.HTTPError`` for genuine failures (401/403/429/5xx).
    """
    body = {
        'formFactor': form_factor,
        'metrics': list(CWV_METRICS.keys()),
    }
    if url:
        body['url'] = url
    else:
        body['origin'] = origin
    resp = session.post(
        CRUX_ENDPOINT, params={'key': api_key}, json=body, timeout=30
    )
    if resp.status_code == 404:
        return None  # no field data for this target — not an error
    resp.raise_for_status()
    return resp.json().get('record', {})


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--origin', default=DEFAULT_ORIGIN,
                        help=f'origin to query (default: {DEFAULT_ORIGIN})')
    parser.add_argument('--url', action='append', default=[],
                        help='specific URL to query (repeatable); origin is always queried too')
    parser.add_argument('--form-factor', default='PHONE',
                        choices=['PHONE', 'DESKTOP', 'TABLET', 'ALL_FORM_FACTORS'],
                        help='device class (default: PHONE — mobile is the SEO-critical one)')
    parser.add_argument('--out', help='write results as JSON to this path')
    args = parser.parse_args(argv)

    api_key = os.environ.get('CRUX_API_KEY')
    if not api_key:
        print('❌ CRUX_API_KEY is not set. Get one at https://goo.gle/crux-api-key '
              'and export it (or add it as a GitHub secret).', file=sys.stderr)
        return 1

    targets = [{'origin': args.origin}] + [{'url': u} for u in args.url]
    session = requests.Session()
    results = []
    worst = 'good'
    rank = {'good': 0, 'needs-improvement': 1, 'poor': 2}

    print(f"Chrome UX Report — {args.form_factor} — trailing 28 days\n")
    for target in targets:
        label = target.get('url') or target.get('origin')
        try:
            record = query_crux(session, api_key, form_factor=args.form_factor, **target)
        except requests.RequestException as e:
            print(f"❌ API error for {label}: {e}", file=sys.stderr)
            return 1

        if record is None:
            print(f"  • {label}\n      (no field data — insufficient CrUX traffic)\n")
            results.append({**target, 'data': None})
            continue

        vitals = parse_crux_record(record)
        entry = {**target, 'data': {}}
        print(f"  • {label}")
        for short in ('lcp', 'inp', 'cls'):
            if short not in vitals:
                continue
            value = vitals[short]
            verdict = assess(short, value)
            if rank[verdict] > rank[worst]:
                worst = verdict
            icon = {'good': '🟢', 'needs-improvement': '🟡', 'poor': '🔴'}[verdict]
            print(f"      {icon} {short.upper():3} p75 = {_fmt(short, value):>8}  ({verdict})")
            entry['data'][short] = {'p75': value, 'assessment': verdict}
        print()
        results.append(entry)

    if args.out:
        Path(args.out).write_text(json.dumps(
            {'origin': args.origin, 'formFactor': args.form_factor, 'results': results},
            indent=2,
        ))
        print(f"📄 Wrote {args.out}")

    print(f"Overall page-experience assessment: {worst}")
    return 0


if __name__ == '__main__':
    sys.exit(main())
