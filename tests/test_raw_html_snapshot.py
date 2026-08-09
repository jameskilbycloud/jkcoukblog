"""Guard the raw pre-transform snapshot wiring in the deploy workflow.

Incremental builds seed ./static-output from public/, which holds
*post-processed* HTML. Re-running optimize_css / html_transformer over their
own output is not idempotent — the WP stylesheet inliner has already turned
some <link rel=stylesheet> into <style>, and extract_critical_css only
harvests rules from the <link>s still present, so the critical-CSS block comes
out different every run. Measured 2026-08-09: two consecutive incremental runs
with identical code and zero content changes rewrote 250 of 255 pages,
differing only in that block.

The fix is a snapshot of static-output taken immediately after generation and
overlaid on the seed next run. Nothing about it fails loudly if it breaks: a
renamed cache key, a save step that stops running, or a capture that drifts
after the first optimisation pass all degrade silently back to whole-site
churn. These tests pin the ordering and key agreement that make it work.
"""

import re
from pathlib import Path

import pytest

yaml = pytest.importorskip('yaml')

REPO_ROOT = Path(__file__).resolve().parent.parent
DEPLOY = REPO_ROOT / '.github/workflows/deploy-static-site.yml'
FORCE_FULL = REPO_ROOT / '.github/workflows/force-full-deploy.yml'

CACHE_KEY_PREFIX = 'raw-html-snapshot-'
SNAPSHOT_DIR = '.raw-html-snapshot'


def _steps(workflow: Path, job: str):
    data = yaml.safe_load(workflow.read_text())
    return data['jobs'][job]['steps']


def _step_index(steps, predicate, what):
    for i, step in enumerate(steps):
        if predicate(step):
            return i
    raise AssertionError(f'no step found for: {what}')


@pytest.fixture(scope='module')
def deploy_steps():
    return _steps(DEPLOY, 'build-and-deploy')


@pytest.fixture(scope='module')
def generate_step(deploy_steps):
    for step in deploy_steps:
        if step.get('name') == 'Generate static site':
            return step
    raise AssertionError('"Generate static site" step not found')


def test_restore_and_save_agree_on_key_and_path(deploy_steps):
    """A typo in either key silently disables the snapshot — nothing errors,
    the build just goes back to churning every page."""
    restore = save = None
    for step in deploy_steps:
        uses = step.get('uses', '')
        with_ = step.get('with', {})
        if with_.get('path') != SNAPSHOT_DIR:
            continue
        if 'cache/restore@' in uses:
            restore = with_
        elif 'cache/save@' in uses:
            save = with_

    assert restore, 'no actions/cache/restore step for the raw snapshot'
    assert save, 'no actions/cache/save step for the raw snapshot'

    assert restore['key'].startswith(CACHE_KEY_PREFIX)
    assert save['key'].startswith(CACHE_KEY_PREFIX)
    assert restore['key'] == save['key'], 'restore and save keys must match'

    # run_attempt keeps a re-run from colliding with the key its own failed
    # attempt already reserved.
    assert 'run_attempt' in save['key']

    restore_keys = [k.strip() for k in restore['restore-keys'].splitlines() if k.strip()]
    assert restore_keys == [CACHE_KEY_PREFIX], (
        'the restore-keys wildcard is what actually finds the previous run — '
        f'expected exactly [{CACHE_KEY_PREFIX!r}], got {restore_keys!r}'
    )


def test_snapshot_is_captured_before_any_optimisation_pass(deploy_steps, generate_step):
    """The snapshot is only worth anything as *pre-transform* state. Capturing
    it after an optimisation step would persist exactly the transformed HTML
    the fix exists to avoid re-processing."""
    run = generate_step['run']

    capture = run.index(f'rm -rf {SNAPSHOT_DIR}')
    generator = run.index('python3 scripts/wp_to_static_generator.py')
    assert generator < capture, 'snapshot must be captured after the generator runs'

    # Optimisation lives in later steps, so "after generate, before anything
    # else" reduces to the save step sitting ahead of the first one.
    save_idx = _step_index(
        deploy_steps,
        lambda s: s.get('with', {}).get('path') == SNAPSHOT_DIR
        and 'cache/save@' in s.get('uses', ''),
        'raw snapshot cache/save',
    )
    first_optimise_idx = _step_index(
        deploy_steps,
        lambda s: str(s.get('name', '')).startswith(('Optimize ', 'Single-pass HTML transformer')),
        'first optimisation step',
    )
    assert save_idx < first_optimise_idx, (
        'the snapshot must be saved before optimisation mutates static-output'
    )


def test_overlay_runs_before_the_generator(generate_step):
    """Overlay order matters: the generator must be able to overwrite snapshot
    files for posts that changed this run, and to re-sync repo-sourced assets
    like brutalist-theme.css."""
    run = generate_step['run']

    overlay = run.index(f'rsync -a {SNAPSHOT_DIR}/ ./static-output/')
    seed = run.index("rsync -a --exclude='*.br' --exclude='*.gz' public/ ./static-output/")
    generator = run.index('python3 scripts/wp_to_static_generator.py')

    assert seed < overlay < generator, (
        'expected order: seed from public/ → overlay raw snapshot → run generator'
    )


def test_missing_snapshot_degrades_instead_of_failing(generate_step):
    """First run after this lands (and any run after a cache eviction) has no
    snapshot. That must fall back to the old public/ seed, not abort."""
    run = generate_step['run']
    assert f'if [ -d "{SNAPSHOT_DIR}" ]; then' in run
    assert 'No raw snapshot to overlay' in run


def test_force_full_deploy_purges_the_snapshot():
    """force-full-deploy exists to clear stale incremental state; a surviving
    snapshot from a superseded template would undercut that."""
    text = FORCE_FULL.read_text()
    assert re.search(
        rf'gh cache list .*--key {re.escape(CACHE_KEY_PREFIX.rstrip("-"))}', text
    ), 'force-full-deploy.yml must purge raw-html-snapshot-* caches'


def test_snapshot_dir_is_gitignored():
    """31 MB of HTML per build must never reach a commit."""
    ignored = (REPO_ROOT / '.gitignore').read_text().splitlines()
    assert f'{SNAPSHOT_DIR}/' in [line.strip() for line in ignored]
