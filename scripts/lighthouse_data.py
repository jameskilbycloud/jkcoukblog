#!/usr/bin/env python3
"""
Shared Lighthouse data access.

Single source of truth for the two pages that surface Lighthouse numbers
(generate_changelog.py and generate_stats_page.py). Before this module the
logic was copy-pasted across both scripts and had already drifted, which is
exactly how the "Estimated 95/95/100/100" placeholder ended up masquerading
as a real measurement.

Data flow:
    quality-checks.yml (real Lighthouse on prod)
        -> data/lighthouse-latest.json        (latest measurement, incl. CWV)
            -> save_to_history()
                -> public/changelog/lighthouse-history.json   (dated trend)
"""

import json
from datetime import datetime
from pathlib import Path

# The Quality Checks workflow commits the latest real measurement here. We READ
# it rather than calling Google's PageSpeed Insights API — the unauthenticated
# PSI endpoint returns HTTP 429 (shared daily quota exhausted), which is what
# the old code silently swallowed before falling back to fabricated scores.
LATEST_FILE = Path('data/lighthouse-latest.json')
HISTORY_FILE = Path('public/changelog/lighthouse-history.json')

# Core Web Vitals carried through from the measurement, in render order.
CWV_FIELDS = ('lcp', 'fcp', 'cls', 'tti')


def load_latest():
    """Return the latest real measurement dict, or None when none exists yet.

    Returning None (rather than inventing numbers) lets callers reuse the last
    real history entry or show an honest "no data" state.
    """
    if not LATEST_FILE.exists():
        return None
    try:
        with open(LATEST_FILE, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"   ⚠️  Could not read {LATEST_FILE} ({e})")
        return None

    try:
        record = {
            'performance': int(data['performance']),
            'accessibility': int(data['accessibility']),
            'best_practices': int(data['best_practices']),
            'seo': int(data['seo']),
            'timestamp': data.get('measured_at', 'unknown'),
        }
    except (KeyError, TypeError, ValueError) as e:
        print(f"   ⚠️  {LATEST_FILE} is missing expected fields ({e})")
        return None

    # Core Web Vitals are optional — older measurements predate them.
    for field in CWV_FIELDS:
        value = data.get(field)
        if value not in (None, '', 'N/A'):
            record[field] = value
    return record


def has_cwv(record):
    """True when a measurement carries at least one Core Web Vital."""
    return bool(record) and any(field in record for field in CWV_FIELDS)


def load_history():
    """Load the dated Lighthouse history (oldest first). Empty list if none."""
    if not HISTORY_FILE.exists():
        return []
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"⚠️  Lighthouse history unreadable ({e}) — starting fresh")
        return []


def save_to_history(scores, history):
    """Record a measurement, keeping one entry per date (latest wins) and 90 days.

    The deploy pipeline runs many times a day; without the per-date collapse the
    history would fill with identical same-day rows and the trend series would be
    useless. Core Web Vitals are persisted when present so the trend can grow
    beyond the four category scores later.
    """
    today = datetime.now().strftime('%Y-%m-%d')
    entry = {
        'date': today,
        'timestamp': scores['timestamp'],
        'performance': scores['performance'],
        'accessibility': scores['accessibility'],
        'best_practices': scores['best_practices'],
        'seo': scores['seo'],
    }
    for field in CWV_FIELDS:
        if field in scores:
            entry[field] = scores[field]

    history = [e for e in history if e.get('date') != today]
    history.append(entry)

    cutoff = datetime.now().timestamp() - (90 * 24 * 60 * 60)
    history = [e for e in history if datetime.strptime(e['date'], '%Y-%m-%d').timestamp() > cutoff]

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

    print(f"✅ Saved Lighthouse scores to history ({len(history)} entries)")
    return history


def score_class(value):
    """CSS class for a 0-100 Lighthouse score (matches the .score-* styles)."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        return 'score-poor'
    if value >= 90:
        return 'score-excellent'
    if value >= 50:
        return 'score-good'
    return 'score-poor'
