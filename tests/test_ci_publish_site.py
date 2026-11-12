"""scripts/ci/publish_site.sh against throwaway git repos.

The publish step force-pushes the built site to the `site` branch as one
parentless commit, guarded by a lease on the commit the build started from.
These cover the four states a deploy can be in: first publish, a changed
page, nothing changed, and someone else publishing mid-build.
"""

import shutil
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / 'scripts' / 'ci' / 'publish_site.sh'

pytestmark = pytest.mark.skipif(shutil.which('git') is None or shutil.which('bash') is None,
                                reason='needs git and bash')


def git(cwd, *args):
    return subprocess.run(['git', *args], cwd=cwd, check=True, capture_output=True,
                          text=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    origin = tmp_path / 'origin.git'
    work = tmp_path / 'work'
    git(tmp_path, 'init', '-q', '--bare', '-b', 'main', str(origin))
    git(tmp_path, 'clone', '-q', str(origin), str(work))
    git(work, 'config', 'user.email', 'ci@example.com')
    git(work, 'config', 'user.name', 'CI')
    (work / '.gitignore').write_text('public/\n')
    git(work, 'add', '.gitignore')
    git(work, 'commit', '-q', '-m', 'init')
    git(work, 'push', '-q', 'origin', 'HEAD:main')
    return tmp_path, work


def site_sha(work):
    out = subprocess.run(['git', 'ls-remote', 'origin', 'refs/heads/site'], cwd=work,
                         capture_output=True, text=True).stdout.split()
    return out[0] if out else ''


def publish(tmp_path, work, prev_site_sha):
    """Run the script the way the deploy step does; return (exit code, outputs)."""
    output = tmp_path / 'github_output'
    output.write_text('')
    env = {
        'PATH': '/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin',
        'HOME': str(tmp_path),
        'RUNNER_TEMP': str(tmp_path),
        'GITHUB_SHA': git(work, 'rev-parse', 'HEAD'),
        'GITHUB_OUTPUT': str(output),
        'GITHUB_STEP_SUMMARY': str(tmp_path / 'summary'),
        'PREV_SITE_SHA': prev_site_sha,
    }
    rc = subprocess.run(['bash', str(SCRIPT)], cwd=work, env=env,
                        capture_output=True, text=True).returncode
    outputs = dict(line.split('=', 1) for line in output.read_text().splitlines() if '=' in line)
    return rc, outputs


def write_site(work, files):
    public = work / 'public'
    if public.exists():
        shutil.rmtree(public)
    for rel, content in files.items():
        p = public / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)


def test_first_publish_creates_a_parentless_site_commit(repo):
    tmp_path, work = repo
    write_site(work, {'index.html': '1', 'a/index.html': 'x'})

    rc, out = publish(tmp_path, work, '')

    assert rc == 0
    assert out['pushed_sha'] == site_sha(work)
    assert git(work, 'rev-list', '--parents', '-n1', out['pushed_sha']) == out['pushed_sha']
    assert git(work, 'ls-tree', '-r', '--name-only', out['pushed_sha']).split() == [
        'public/a/index.html', 'public/index.html']


def test_changed_page_replaces_the_site_commit(repo):
    tmp_path, work = repo
    write_site(work, {'index.html': '1', 'a/index.html': 'x'})
    _, first = publish(tmp_path, work, '')
    write_site(work, {'index.html': '1', 'a/index.html': 'y'})

    rc, out = publish(tmp_path, work, first['pushed_sha'])

    assert rc == 0
    assert out['diff_files'] == '1'
    assert site_sha(work) == out['pushed_sha'] != first['pushed_sha']
    assert git(work, 'rev-list', '--count', out['pushed_sha']) == '1'   # still no history


def test_unchanged_site_pushes_nothing(repo):
    tmp_path, work = repo
    write_site(work, {'index.html': '1'})
    _, first = publish(tmp_path, work, '')

    rc, out = publish(tmp_path, work, first['pushed_sha'])

    assert rc == 0
    assert out['pushed_sha'] == ''
    assert site_sha(work) == first['pushed_sha']


def test_publish_mid_build_by_someone_else_is_not_overwritten(repo):
    tmp_path, work = repo
    write_site(work, {'index.html': '1'})
    _, first = publish(tmp_path, work, '')
    # Another publisher replaces site after this build seeded from `first`.
    other = git(work, 'commit-tree', git(work, 'rev-parse', f"{first['pushed_sha']}^{{tree}}"),
                '-m', 'other')
    git(work, 'push', '-q', '-f', 'origin', f'{other}:refs/heads/site')
    write_site(work, {'index.html': '2'})

    rc, _ = publish(tmp_path, work, first['pushed_sha'])

    assert rc == 1
    assert site_sha(work) == other


def test_main_history_is_untouched_by_site_publishes(repo):
    tmp_path, work = repo
    before = git(work, 'ls-remote', 'origin', 'refs/heads/main')
    write_site(work, {'index.html': '1'})
    publish(tmp_path, work, '')

    assert git(work, 'ls-remote', 'origin', 'refs/heads/main') == before
