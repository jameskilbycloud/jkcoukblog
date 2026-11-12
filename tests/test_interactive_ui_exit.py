"""test_interactive_ui.py: a skipped run exits 0 locally, 3 under --require-browser.

CI relies on the non-zero exit to report a skip instead of passing silently.
"""

import pytest

import test_interactive_ui as ui


@pytest.fixture
def no_playwright(monkeypatch):
    monkeypatch.setattr(ui, '_PW_OK', False)
    monkeypatch.setattr(ui, '_PW_ERROR', 'No module named playwright')


def run_main(monkeypatch, *argv):
    monkeypatch.setattr('sys.argv', ['test_interactive_ui.py', *argv])
    with pytest.raises(SystemExit) as exc:
        ui.main()
    return exc.value.code


def test_skip_exits_zero_by_default(monkeypatch, no_playwright, tmp_path):
    assert run_main(monkeypatch, str(tmp_path)) == 0


def test_skip_fails_with_require_browser(monkeypatch, no_playwright, tmp_path):
    assert run_main(monkeypatch, str(tmp_path), '--require-browser') == ui.EXIT_SKIPPED


def test_flag_position_does_not_matter(monkeypatch, no_playwright, tmp_path):
    assert run_main(monkeypatch, '--require-browser', str(tmp_path)) == ui.EXIT_SKIPPED


def test_launch_failure_fails_with_require_browser(monkeypatch, tmp_path):
    (tmp_path / 'index.html').write_text('<html></html>')

    class LaunchFails:
        def __init__(self, base_url):
            self.launch_failed, self.launch_error, self.results = True, 'missing libatk', []

        def run_all(self):
            pass

    monkeypatch.setattr(ui, '_PW_OK', True)
    monkeypatch.setattr(ui, 'UISmokeTests', LaunchFails)
    assert run_main(monkeypatch, str(tmp_path), '--require-browser') == ui.EXIT_SKIPPED
    assert run_main(monkeypatch, str(tmp_path)) == 0
