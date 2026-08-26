"""Tests for the homepage stats-ribbon Lighthouse value
(wp_to_static_generator._stat_lighthouse_performance).

The ribbon used to read only changelog/lighthouse-history.json. That file is
written by generate_changelog, which runs *later* in the pipeline than the
ribbon is computed, and its public/ copy is not committed — so on a clean
checkout the ribbon fell back to '—'. It now reads data/lighthouse-latest.json
first: the committed, always-present single source of truth that
generate_changelog itself consumes. These tests pin that precedence.
"""

import json
from pathlib import Path

from wp_to_static_generator import WordPressStaticGenerator as G


class _Stub:
    """Minimal stand-in — the stat only touches self.output_dir."""

    def __init__(self, output_dir):
        self.output_dir = output_dir


def _write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding='utf-8')


def test_reads_latest_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / 'data' / 'lighthouse-latest.json', {'performance': 94})
    assert G._stat_lighthouse_performance(_Stub(tmp_path / 'static-output')) == '94/100'


def test_latest_wins_over_history(tmp_path, monkeypatch):
    # A stale history score must not shadow the fresh latest score.
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / 'data' / 'lighthouse-latest.json', {'performance': 94})
    _write(tmp_path / 'public' / 'changelog' / 'lighthouse-history.json',
           [{'performance': 73}])
    assert G._stat_lighthouse_performance(_Stub(tmp_path / 'static-output')) == '94/100'


def test_falls_back_to_history_when_latest_missing(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write(tmp_path / 'public' / 'changelog' / 'lighthouse-history.json',
           [{'performance': 88}])
    assert G._stat_lighthouse_performance(_Stub(tmp_path / 'static-output')) == '88/100'


def test_dash_when_no_sources(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert G._stat_lighthouse_performance(_Stub(tmp_path / 'static-output')) == '—'
