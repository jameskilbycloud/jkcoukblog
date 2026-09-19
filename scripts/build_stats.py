#!/usr/bin/env python3
"""Shared Lighthouse/git statistics helpers for generate_changelog.py and
generate_stats_page.py — both render the same underlying build data and
previously carried separate, drifting copies of get_lighthouse_scores() and
get_git_stats(). This module is the one implementation each page reads from.
"""

import subprocess
from pathlib import Path
from datetime import datetime
import json

# Real Lighthouse scores are produced by the `Quality Checks` workflow
# (quality-checks.yml), which runs the genuine Lighthouse CI against the
# production URL and commits the latest run here. We READ that measurement
# rather than calling Google's PageSpeed Insights API — the unauthenticated
# PSI endpoint returns HTTP 429 (shared daily quota exhausted) and the old
# code silently fell back to hardcoded 95/95/100/100 "Estimated" scores,
# which then masqueraded as real data on /changelog/ and /stats/.
LIGHTHOUSE_LATEST_FILE = Path('data/lighthouse-latest.json')


def get_lighthouse_scores():
    """Load the latest real Lighthouse scores measured by the Quality Checks workflow.

    Returns a scores dict, or None when no real measurement is available yet
    (e.g. the workflow has not run since this file was wired up). Returning
    None lets callers fall back to the most recent real history entry
    instead of fabricating numbers.
    """
    print("📊 Loading Lighthouse scores from latest measurement...")

    if not LIGHTHOUSE_LATEST_FILE.exists():
        print(f"   ⚠️  {LIGHTHOUSE_LATEST_FILE} not found — no real scores to record this run")
        return None

    try:
        with open(LIGHTHOUSE_LATEST_FILE, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"   ⚠️  Could not read {LIGHTHOUSE_LATEST_FILE} ({e}) — skipping")
        return None

    try:
        scores = {
            'performance': int(data['performance']),
            'accessibility': int(data['accessibility']),
            'best_practices': int(data['best_practices']),
            'seo': int(data['seo']),
            'timestamp': data.get('measured_at', 'unknown'),
        }
    except (KeyError, TypeError, ValueError) as e:
        print(f"   ⚠️  {LIGHTHOUSE_LATEST_FILE} is missing expected fields ({e}) — skipping")
        return None

    print(f"   ✅ Loaded real scores measured {scores['timestamp']} "
          f"(perf {scores['performance']}, a11y {scores['accessibility']}, "
          f"bp {scores['best_practices']}, seo {scores['seo']})")
    return scores


def get_git_stats():
    """Git repository statistics used by both the stats and changelog pages.

    Returns the union of fields either page needs: total_commits,
    contributors, age_days (changelog), plus last_deploy_date,
    last_deploy_time and commits_this_month (stats page). last_deploy keeps
    the raw `git log -1 --format=%ci` string so existing `.split()` call
    sites keep working unchanged.
    """
    print("📈 Gathering git statistics...")

    stats = {}

    # Total commits
    result = subprocess.run(['git', 'rev-list', '--count', 'HEAD'],
                          capture_output=True, text=True)
    stats['total_commits'] = result.stdout.strip() if result.returncode == 0 else 'N/A'

    # Contributors
    result = subprocess.run(['git', 'shortlog', '-sn', '--all'],
                          capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        stats['contributors'] = len(result.stdout.strip().split('\n'))
    else:
        stats['contributors'] = 'N/A'

    # Repository age
    result = subprocess.run(['git', 'log', '--reverse', '--format=%ci'],
                          capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        first_commit = result.stdout.strip().split('\n')[0]
        if first_commit:
            first_date = datetime.fromisoformat(first_commit.split()[0])
            stats['age_days'] = (datetime.now() - first_date).days
        else:
            stats['age_days'] = 'N/A'
    else:
        stats['age_days'] = 'N/A'

    # Last deployment — full raw string, plus date/time split out
    result = subprocess.run(['git', 'log', '-1', '--format=%ci'],
                          capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        last_deploy = result.stdout.strip()
        stats['last_deploy'] = last_deploy
        stats['last_deploy_date'] = last_deploy.split()[0]
        stats['last_deploy_time'] = last_deploy.split()[1]
    else:
        stats['last_deploy'] = 'N/A'
        stats['last_deploy_date'] = 'Unknown'
        stats['last_deploy_time'] = ''

    # Commits this month
    result = subprocess.run([
        'git', 'log', '--since', '1 month ago', '--oneline'
    ], capture_output=True, text=True)
    stats['commits_this_month'] = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0

    print(f"   ✅ {stats['total_commits']} total commits, {stats['commits_this_month']} this month")
    return stats
