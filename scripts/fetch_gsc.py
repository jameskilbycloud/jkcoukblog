#!/usr/bin/env python3
"""Pull real Google Search Console data for the site via the Search Console API.

Gives the orchestrator ground-truth indexing/coverage state straight from
Google — not a guess derived from the local build — so we can see which URLs
Google actually indexed, which it dropped, and why (canonical mismatch, robots
block, crawl error, soft-404, …), plus the submitted-sitemap health and the
top-performing queries/pages for opportunity analysis.

Three data sources, one report:
  1. URL Inspection  (searchconsole v1, urlInspection.index.inspect) looped over
     every URL in the site's sitemap. Per URL we capture the index verdict,
     coverageState, robots/indexing/pageFetch states, Google-vs-user canonical,
     last-crawl time + crawledAs, and the mobile-usability / rich-results
     verdicts when present. Aggregated into coverage-state counts, a problem-URL
     list (anything not "PASS / Submitted and indexed") and a canonical-mismatch
     flag (googleCanonical != userCanonical).
  2. Sitemaps API   (sitemaps.list / sitemaps.get) — submitted sitemaps with
     their error/warning counts, isPending / isSitemapsIndex, lastDownloaded.
  3. Search Analytics (searchanalytics.query) — trailing 28 days, top ~100 rows
     by clicks for dimensions [query] and [page] separately.

Why a service account (not OAuth installed-app flow): it runs unattended in the
hive with no browser to complete a consent screen. You must grant the service
account access to the property once, in the GSC UI:

    Search Console → Settings → Users and permissions → Add user
        → paste the service account's client_email (…@….iam.gserviceaccount.com)
        → permission "Full" or "Restricted" (Restricted is enough — we only read).

Setup:
    1. GCP console → enable the "Google Search Console API".
    2. Create a service account, add a JSON key, download it.
    3. Save the key at ~/.config/gsc/sa.json  (or point GSC_SA_KEY / --key at it).
    4. Add the service account's client_email as a user on the GSC property
       (see above) — without this every call 403s.

Usage:
    python3 scripts/fetch_gsc.py                       # url-prefix property, all sitemap URLs
    python3 scripts/fetch_gsc.py --limit 200           # inspect only first 200 URLs (rate-limit friendly)
    python3 scripts/fetch_gsc.py --site sc-domain:jameskilby.co.uk   # Domain property
    python3 scripts/fetch_gsc.py --key /path/to/sa.json
    python3 scripts/fetch_gsc.py --out docs/gsc/latest.json

Site / property (--site or GSC_SITE), both are valid GSC property forms:
    URL-prefix  https://jameskilby.co.uk/     (default — derived from config.py)
    Domain      sc-domain:jameskilby.co.uk    (covers http/https + all subdomains)
Use whichever the service account was actually granted on; they are distinct
properties in GSC and a grant on one does NOT imply the other.

Rate limits (Search Console API): URL Inspection is the tight one — ~2000
inspections/day and ~600/minute per property. We add a small polite delay
between inspections and back off on HTTP 429; on repeated quota exhaustion we
stop cleanly and still write the partial report. Use --limit on big sitemaps.

Output:
    docs/gsc/gsc-report-<YYYY-MM-DD>.json   (structured; committable — no secrets)
    + a concise human summary to stdout.

Exit codes:
    0  ran (report written; some URLs may have been skipped on quota — noted)
    1  hard failure (missing/invalid key, 403 no-access, sitemap unreachable)
"""

import argparse
import json
import os
import sys
import time
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from config import Config
    DEFAULT_DOMAIN = Config.TARGET_DOMAIN            # e.g. https://jameskilby.co.uk
except (ImportError, AttributeError):                # pragma: no cover - config always present
    DEFAULT_DOMAIN = 'https://jameskilby.co.uk'

# URL-prefix property form GSC expects a trailing slash on.
DEFAULT_SITE = DEFAULT_DOMAIN.rstrip('/') + '/'
# Domain-property form for the same host, offered in --help as the alternative.
DEFAULT_DOMAIN_PROPERTY = 'sc-domain:' + DEFAULT_DOMAIN.split('://', 1)[-1].rstrip('/')

DEFAULT_KEY_PATH = Path.home() / '.config' / 'gsc' / 'sa.json'
SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']

SITEMAP_NS = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

# What we consider "healthy" — everything else lands on the problem list.
HEALTHY_VERDICT = 'PASS'
HEALTHY_COVERAGE = 'Submitted and indexed'

# Politeness / backoff for the rate-limited URL Inspection endpoint.
INSPECT_DELAY_S = 0.5        # ~120/min, well under the 600/min cap
MAX_BACKOFF_RETRIES = 4      # per URL, on HTTP 429
BACKOFF_BASE_S = 5


# ── Sitemap discovery ────────────────────────────────────────────────────────

def _strip_ns(tag):
    return tag.split('}', 1)[-1] if '}' in tag else tag


def fetch_sitemap_urls(sitemap_url, session, *, _depth=0):
    """Return the list of page URLs from a sitemap, following a sitemap index.

    Handles both a <urlset> (leaf sitemap → collect <loc>) and a <sitemapindex>
    (→ recurse into each child sitemap). Namespace-agnostic so it copes with
    sitemaps that omit or vary the xmlns. Raises requests.HTTPError on a bad
    fetch and ET.ParseError on malformed XML — the caller turns those into a
    clean top-level error.
    """
    if _depth > 5:
        return []  # guard against a pathological self-referential index
    resp = session.get(sitemap_url, timeout=30)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    root_tag = _strip_ns(root.tag)

    urls = []
    if root_tag == 'sitemapindex':
        for sm in root:
            loc = sm.find('sm:loc', SITEMAP_NS)
            if loc is None:  # namespace-less fallback
                loc = next((c for c in sm if _strip_ns(c.tag) == 'loc'), None)
            if loc is not None and loc.text:
                urls.extend(fetch_sitemap_urls(loc.text.strip(), session, _depth=_depth + 1))
    else:  # urlset (or anything else — treat direct <loc> children as URLs)
        for url_el in root:
            loc = url_el.find('sm:loc', SITEMAP_NS)
            if loc is None:
                loc = next((c for c in url_el if _strip_ns(c.tag) == 'loc'), None)
            if loc is not None and loc.text:
                urls.append(loc.text.strip())
    return urls


# ── Auth ─────────────────────────────────────────────────────────────────────

def build_service(key_path):
    """Build the authenticated `searchconsole` v1 service from an SA key.

    Imports the Google libraries lazily so `--help` and arg parsing work on a
    box that hasn't got them installed yet. Returns the discovery resource or
    raises SystemExit(1) with an actionable message.
    """
    if not key_path.exists():
        print(
            f"❌ Service-account key not found at {key_path}\n"
            f"   Create one (GCP console → service account → keys → JSON), save it there,\n"
            f"   or point --key / GSC_SA_KEY at it. See this file's docstring for setup.",
            file=sys.stderr,
        )
        raise SystemExit(1)

    try:
        from google.oauth2 import service_account
        from googleapiclient.discovery import build
    except ImportError as e:  # pragma: no cover - libs are installed in this env
        print(
            f"❌ Missing Google client libraries ({e}).\n"
            f"   Install: pip install google-api-python-client google-auth",
            file=sys.stderr,
        )
        raise SystemExit(1) from e

    try:
        creds = service_account.Credentials.from_service_account_file(
            str(key_path), scopes=SCOPES,
        )
    except (ValueError, KeyError) as e:
        print(f"❌ {key_path} is not a valid service-account JSON key: {e}", file=sys.stderr)
        raise SystemExit(1) from e

    # cache_discovery=False avoids the noisy file-cache warning under oauth2.
    return build('searchconsole', 'v1', credentials=creds, cache_discovery=False)


def _client_email(key_path):
    """Best-effort read of the SA's client_email, for 403 error guidance."""
    try:
        return json.loads(key_path.read_text()).get('client_email', '<unknown>')
    except (OSError, ValueError):
        return '<unknown>'


def _is_http_error(exc):
    """True if exc looks like a googleapiclient HttpError, without importing it."""
    return exc.__class__.__name__ == 'HttpError' and hasattr(exc, 'resp')


def _http_status(exc):
    return getattr(getattr(exc, 'resp', None), 'status', None)


# ── URL Inspection ───────────────────────────────────────────────────────────

def inspect_url(service, site_url, page_url):
    """Inspect one URL. Returns the raw inspectionResult dict.

    Raises the underlying HttpError (caller handles 429 backoff / 403).
    """
    body = {'inspectionUrl': page_url, 'siteUrl': site_url}
    resp = service.urlInspection().index().inspect(body=body).execute()
    return resp.get('inspectionResult', {})


def summarise_inspection(page_url, result):
    """Flatten one inspectionResult into the fields we report on.

    Pure — no I/O. Returns a dict; missing sub-objects degrade to None/[] rather
    than raising, because the API omits blocks (mobileUsability, richResults)
    when it has nothing to say.
    """
    index_res = result.get('indexStatusResult', {})
    mobile = result.get('mobileUsabilityResult', {})
    rich = result.get('richResultsResult', {})

    google_canonical = index_res.get('googleCanonical')
    user_canonical = index_res.get('userCanonical')
    canonical_mismatch = bool(
        google_canonical and user_canonical and google_canonical != user_canonical
    )

    def _issue_messages(block):
        return [i.get('message') for i in block.get('issues', []) if i.get('message')]

    verdict = index_res.get('verdict')
    coverage = index_res.get('coverageState')
    is_problem = verdict != HEALTHY_VERDICT or coverage != HEALTHY_COVERAGE

    return {
        'url': page_url,
        'verdict': verdict,
        'coverageState': coverage,
        'robotsTxtState': index_res.get('robotsTxtState'),
        'indexingState': index_res.get('indexingState'),
        'pageFetchState': index_res.get('pageFetchState'),
        'googleCanonical': google_canonical,
        'userCanonical': user_canonical,
        'canonicalMismatch': canonical_mismatch,
        'lastCrawlTime': index_res.get('lastCrawlTime'),
        'crawledAs': index_res.get('crawledAs'),
        'mobileUsability': {
            'verdict': mobile.get('verdict'),
            'issues': _issue_messages(mobile),
        } if mobile else None,
        'richResults': {
            'verdict': rich.get('verdict'),
            'issues': _issue_messages(rich),
        } if rich else None,
        'isProblem': is_problem,
    }


def inspect_all(service, site_url, urls, *, delay=INSPECT_DELAY_S):
    """Inspect every URL with polite delay + 429 backoff.

    Returns (inspections, quota_hit): the list of per-URL summaries collected so
    far, and a bool flagging that we stopped early on exhausted quota. Never
    raises on 429 — it degrades to a partial result so the report still writes.
    """
    inspections = []
    total = len(urls)
    for idx, page_url in enumerate(urls, 1):
        result = None
        for attempt in range(MAX_BACKOFF_RETRIES + 1):
            try:
                result = inspect_url(service, site_url, page_url)
                break
            except Exception as exc:  # noqa: BLE001 - re-raised below unless it's a handled HTTP status
                if not _is_http_error(exc):
                    raise
                status = _http_status(exc)
                if status == 403:
                    raise  # no access — fatal, let caller explain
                if status == 429:
                    if attempt >= MAX_BACKOFF_RETRIES:
                        print(
                            f"  ⚠️  quota exhausted (429) after {attempt} retries — "
                            f"stopping at {idx - 1}/{total}. Partial report will still write.",
                            file=sys.stderr,
                        )
                        return inspections, True
                    wait = BACKOFF_BASE_S * (2 ** attempt)
                    print(f"  ⏳ 429 rate-limited; backing off {wait}s "
                          f"(retry {attempt + 1}/{MAX_BACKOFF_RETRIES})", file=sys.stderr)
                    time.sleep(wait)
                    continue
                # Other HTTP errors (4xx/5xx on a single URL): record + move on.
                print(f"  ⚠️  {status} inspecting {page_url}: skipping", file=sys.stderr)
                break

        if result is not None:
            inspections.append(summarise_inspection(page_url, result))
        if idx % 25 == 0 or idx == total:
            print(f"  … inspected {idx}/{total}", file=sys.stderr)
        if idx < total:
            time.sleep(delay)
    return inspections, False


def aggregate_inspections(inspections):
    """Roll per-URL inspections into coverage counts + problem/mismatch lists."""
    coverage_counts = {}
    verdict_counts = {}
    problems = []
    mismatches = []
    for ins in inspections:
        cov = ins['coverageState'] or '(unknown)'
        coverage_counts[cov] = coverage_counts.get(cov, 0) + 1
        ver = ins['verdict'] or '(unknown)'
        verdict_counts[ver] = verdict_counts.get(ver, 0) + 1
        if ins['isProblem']:
            problems.append(ins)
        if ins['canonicalMismatch']:
            mismatches.append({
                'url': ins['url'],
                'googleCanonical': ins['googleCanonical'],
                'userCanonical': ins['userCanonical'],
            })
    return {
        'coverageStateCounts': dict(sorted(coverage_counts.items(), key=lambda kv: -kv[1])),
        'verdictCounts': dict(sorted(verdict_counts.items(), key=lambda kv: -kv[1])),
        'problemUrls': problems,
        'canonicalMismatches': mismatches,
    }


# ── Sitemaps API ─────────────────────────────────────────────────────────────

def fetch_sitemaps(service, site_url):
    """Return per-sitemap health via sitemaps.list, enriched by sitemaps.get.

    list() gives the submitted set; we still call get() per entry because it's
    the documented way to get the freshest per-sitemap counts. Individual get()
    failures degrade to the list() row rather than aborting.
    """
    listing = service.sitemaps().list(siteUrl=site_url).execute()
    out = []
    for sm in listing.get('sitemap', []):
        path = sm.get('path')
        detail = sm
        if path:
            try:
                detail = service.sitemaps().get(siteUrl=site_url, feedpath=path).execute()
            except Exception as exc:  # noqa: BLE001 - non-fatal enrichment
                if _is_http_error(exc):
                    pass  # keep the list() row
                else:
                    raise
        contents = detail.get('contents', [])
        out.append({
            'path': path,
            'lastDownloaded': detail.get('lastDownloaded'),
            'lastSubmitted': detail.get('lastSubmitted'),
            'isPending': detail.get('isPending'),
            'isSitemapsIndex': detail.get('isSitemapsIndex'),
            'errors': int(detail.get('errors', 0) or 0),
            'warnings': int(detail.get('warnings', 0) or 0),
            'contents': [
                {
                    'type': c.get('type'),
                    'submitted': int(c.get('submitted', 0) or 0),
                    'indexed': int(c.get('indexed', 0) or 0),
                }
                for c in contents
            ],
        })
    return out


# ── Search Analytics ─────────────────────────────────────────────────────────

def fetch_search_analytics(service, site_url, *, days=28, row_limit=100):
    """Top rows for [query] and [page] over the trailing `days` window.

    GSC data lags ~2-3 days, so the window ends 3 days ago; that's fine for
    opportunity analysis. Returns {'range': …, 'query': [...], 'page': [...]}.
    """
    end = date.today() - timedelta(days=3)
    start = end - timedelta(days=days)
    result = {'range': {'startDate': start.isoformat(), 'endDate': end.isoformat()}, 'days': days}
    for dimension in ('query', 'page'):
        body = {
            'startDate': start.isoformat(),
            'endDate': end.isoformat(),
            'dimensions': [dimension],
            'rowLimit': row_limit,
        }
        resp = service.searchanalytics().query(siteUrl=site_url, body=body).execute()
        result[dimension] = [
            {
                'key': (row.get('keys') or [None])[0],
                'clicks': row.get('clicks', 0),
                'impressions': row.get('impressions', 0),
                'ctr': round(row.get('ctr', 0.0), 4),
                'position': round(row.get('position', 0.0), 1),
            }
            for row in resp.get('rows', [])
        ]
    return result


# ── Human summary ────────────────────────────────────────────────────────────

def print_summary(report):
    site = report['site']
    print(f"\nGoogle Search Console — {site}")
    print(f"Generated {report['generatedAt']}\n")

    insp = report.get('inspection', {})
    agg = insp.get('aggregate', {})
    inspected = insp.get('inspectedCount', 0)
    sitemap_total = insp.get('sitemapUrlCount', 0)
    print(f"URL Inspection: {inspected} inspected"
          + (f" of {sitemap_total} in sitemap" if sitemap_total else ""))
    if insp.get('quotaHit'):
        print("  ⚠️  stopped early on API quota (429) — results are partial")
    for state, count in agg.get('coverageStateCounts', {}).items():
        icon = '🟢' if state == HEALTHY_COVERAGE else '🔴'
        print(f"    {icon} {count:>4}  {state}")

    problems = agg.get('problemUrls', [])
    print(f"\n  Problem URLs: {len(problems)}")
    for p in problems[:15]:
        detail = p['coverageState'] or p['verdict'] or '?'
        print(f"    • {p['url']}\n        {detail}")
    if len(problems) > 15:
        print(f"    … and {len(problems) - 15} more (see JSON report)")

    mismatches = agg.get('canonicalMismatches', [])
    print(f"\n  Canonical mismatches (google != user): {len(mismatches)}")
    for m in mismatches[:10]:
        print(f"    • {m['url']}\n        google={m['googleCanonical']}\n        user  ={m['userCanonical']}")

    sitemaps = report.get('sitemaps', [])
    print(f"\nSitemaps: {len(sitemaps)} submitted")
    for sm in sitemaps:
        flags = []
        if sm.get('isPending'):
            flags.append('pending')
        if sm.get('isSitemapsIndex'):
            flags.append('index')
        flag_str = f" [{', '.join(flags)}]" if flags else ''
        print(f"    • {sm['path']}{flag_str}")
        print(f"        errors={sm['errors']} warnings={sm['warnings']} "
              f"lastDownloaded={sm.get('lastDownloaded') or '—'}")

    sa = report.get('searchAnalytics', {})
    if sa:
        rng = sa.get('range', {})
        print(f"\nSearch Analytics ({rng.get('startDate')} → {rng.get('endDate')}):")
        top_q = sa.get('query', [])[:5]
        print(f"    Top queries ({len(sa.get('query', []))} rows):")
        for r in top_q:
            print(f"      {r['clicks']:>4} clk  {r['impressions']:>6} imp  "
                  f"pos {r['position']:>4}  {r['key']}")
        print(f"    Top pages ({len(sa.get('page', []))} rows):")
        for r in sa.get('page', [])[:5]:
            print(f"      {r['clicks']:>4} clk  {r['impressions']:>6} imp  "
                  f"pos {r['position']:>4}  {r['key']}")
    print()


# ── Main ─────────────────────────────────────────────────────────────────────

def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--site', default=os.environ.get('GSC_SITE', DEFAULT_SITE),
        help=(f'GSC property. URL-prefix (default: {DEFAULT_SITE}) '
              f'or Domain property ({DEFAULT_DOMAIN_PROPERTY}). Env: GSC_SITE.'),
    )
    parser.add_argument(
        '--key', default=os.environ.get('GSC_SA_KEY', str(DEFAULT_KEY_PATH)),
        help=f'service-account JSON key path (default: {DEFAULT_KEY_PATH}). Env: GSC_SA_KEY.',
    )
    parser.add_argument(
        '--sitemap', default=DEFAULT_DOMAIN.rstrip('/') + '/sitemap.xml',
        help='sitemap URL to source pages for URL Inspection (default: <site>/sitemap.xml)',
    )
    parser.add_argument(
        '--limit', type=int, default=None,
        help='cap the number of URLs inspected (URL Inspection is ~2000/day, 600/min)',
    )
    parser.add_argument(
        '--delay', type=float, default=INSPECT_DELAY_S,
        help=f'polite delay between inspections in seconds (default: {INSPECT_DELAY_S})',
    )
    parser.add_argument(
        '--skip-inspection', action='store_true',
        help='skip the per-URL inspection loop (just sitemaps + search analytics)',
    )
    parser.add_argument(
        '--out', default=None,
        help='output JSON path (default: docs/gsc/gsc-report-<YYYY-MM-DD>.json)',
    )
    args = parser.parse_args(argv)

    # Everything below needs credentials / network. Arg parsing above is
    # deliberately side-effect-free so `--help` works with no key present.
    key_path = Path(args.key).expanduser()
    service = build_service(key_path)

    report = {
        'site': args.site,
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'inspection': {},
        'sitemaps': [],
        'searchAnalytics': {},
    }

    session = requests.Session()
    session.headers['User-Agent'] = 'jkcoukblog-gsc-fetcher/1.0'

    try:
        # 1) URL Inspection over the sitemap.
        if not args.skip_inspection:
            print(f"Fetching sitemap {args.sitemap} …", file=sys.stderr)
            try:
                urls = fetch_sitemap_urls(args.sitemap, session)
            except (requests.RequestException, ET.ParseError) as e:
                print(f"❌ Could not fetch/parse sitemap {args.sitemap}: {e}", file=sys.stderr)
                return 1
            sitemap_count = len(urls)
            if args.limit is not None:
                urls = urls[:args.limit]
            print(f"  {sitemap_count} URLs in sitemap; inspecting {len(urls)}", file=sys.stderr)

            inspections, quota_hit = inspect_all(service, args.site, urls, delay=args.delay)
            report['inspection'] = {
                'sitemapUrlCount': sitemap_count,
                'inspectedCount': len(inspections),
                'quotaHit': quota_hit,
                'aggregate': aggregate_inspections(inspections),
                'urls': inspections,
            }

        # 2) Sitemaps API.
        try:
            report['sitemaps'] = fetch_sitemaps(service, args.site)
        except Exception as exc:  # noqa: BLE001 - map HTTP status to a message
            if _is_http_error(exc) and _http_status(exc) == 403:
                raise
            print(f"  ⚠️  sitemaps.list failed: {exc}", file=sys.stderr)

        # 3) Search Analytics.
        try:
            report['searchAnalytics'] = fetch_search_analytics(service, args.site)
        except Exception as exc:  # noqa: BLE001 - map HTTP status to a message
            if _is_http_error(exc) and _http_status(exc) == 403:
                raise
            print(f"  ⚠️  searchanalytics.query failed: {exc}", file=sys.stderr)

    except Exception as exc:  # noqa: BLE001 - single place to explain a 403
        if _is_http_error(exc) and _http_status(exc) == 403:
            email = _client_email(key_path)
            print(
                f"\n❌ 403 from Search Console for {args.site}.\n"
                f"   The service account is authenticated but not authorised on this property.\n"
                f"   Add its email as a user on the GSC property:\n"
                f"     Search Console → Settings → Users and permissions → Add user\n"
                f"     → {email}   (Restricted is enough — read-only)\n"
                f"   Also confirm --site matches the property form the SA was granted on\n"
                f"   (URL-prefix {DEFAULT_SITE} vs Domain {DEFAULT_DOMAIN_PROPERTY}).",
                file=sys.stderr,
            )
            return 1
        raise

    # Write report.
    out_path = Path(args.out) if args.out else Path('docs/gsc') / f"gsc-report-{date.today().isoformat()}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"📄 Wrote {out_path}", file=sys.stderr)

    print_summary(report)
    return 0


if __name__ == '__main__':
    sys.exit(main())
