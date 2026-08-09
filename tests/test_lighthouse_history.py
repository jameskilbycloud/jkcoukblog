"""One Lighthouse row per day, but a representative one.

"Latest wins" made the daily row mean "whichever run happened to be last",
which is not a property of the day. On 2026-08-09 the row recorded P73 — a
single cold-cache outlier measured four minutes after a cache-purging deploy
— while seven other runs that day scored 91-93. The 90-day trend then showed
a cliff that nothing in the site had caused, and the six good runs were gone.
"""

import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

from generate_changelog import _median, save_lighthouse_scores  # noqa: E402


def _scores(performance, ts='2026-08-09T10:00:00'):
    return {'timestamp': ts, 'performance': performance,
            'accessibility': 96, 'best_practices': 93, 'seo': 100}


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """save_lighthouse_scores writes a fixed relative path."""
    monkeypatch.chdir(tmp_path)


@pytest.mark.parametrize('values,expected', [
    ([93], 93),
    ([91, 93], 92),
    ([93, 73, 92], 92),
    ([91, 92, 93, 93], 92),
])
def test_median(values, expected):
    assert _median(values) == expected


def test_single_outlier_does_not_define_the_day():
    """The actual regression, with the day's real numbers."""
    history = []
    for p in (93, 91, 92, 93, 91, 92, 93):
        history = save_lighthouse_scores(_scores(p), history)
    history = save_lighthouse_scores(_scores(73), history)   # cold-cache run

    today = history[-1]
    assert today['runs'] == 8
    assert today['performance'] == 92, (
        f"one outlier moved the daily row to P{today['performance']}"
    )


def test_every_run_is_retained_as_a_sample():
    history = []
    for p in (93, 73, 92):
        history = save_lighthouse_scores(_scores(p), history)

    samples = history[-1]['samples']
    assert [s['performance'] for s in samples] == [93, 73, 92]


def test_one_row_per_date():
    """The 90-day trend still wants a single point per day."""
    history = []
    for p in (93, 91, 92):
        history = save_lighthouse_scores(_scores(p), history)
    assert len(history) == 1


def test_legacy_row_is_folded_in_not_discarded():
    """Rows written before `samples` existed must survive the upgrade as a
    data point rather than being dropped on the first write of the day."""
    today = datetime.now().strftime('%Y-%m-%d')
    legacy = [{'date': today, 'timestamp': 'old', 'performance': 90,
               'accessibility': 96, 'best_practices': 93, 'seo': 100}]

    history = save_lighthouse_scores(_scores(94), legacy)

    assert history[-1]['runs'] == 2
    assert [s['performance'] for s in history[-1]['samples']] == [90, 94]
    assert history[-1]['performance'] == 92


def test_consumer_keys_are_preserved():
    """generate_changelog and generate_stats_page both read history[-1] and
    pull these keys straight off it."""
    history = save_lighthouse_scores(_scores(93), [])
    entry = history[-1]
    for key in ('date', 'timestamp', 'performance', 'accessibility',
                'best_practices', 'seo'):
        assert key in entry, f'consumers read {key!r} off the daily row'
