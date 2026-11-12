"""generate_changelog.is_pipeline_commit: CI bookkeeping commits stay out of /changelog/."""

import pytest

from generate_changelog import is_pipeline_commit


@pytest.mark.parametrize('subject', [
    '🚀 Auto-update static site - 2026-11-08 10:11:18',
    'chore(build): update build caches - 2026-11-12 16:14:33',
    'chore(lighthouse): record scores P91/A96/BP100/S100',
])
def test_pipeline_commits_are_skipped(subject):
    assert is_pipeline_commit(subject)


@pytest.mark.parametrize('subject', [
    'ci: publish the built site to a site branch instead of committing public/ to main (#226)',
    'chore(deps-dev): Bump pytest from 9.1.1 to 9.2.0 (#222)',
    'fix(lighthouse): stop the CLS regression on archive pages',
])
def test_real_changes_are_kept(subject):
    assert not is_pipeline_commit(subject)
