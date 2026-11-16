"""ImageOptimizer progress lines: a multi-hour --force run must show how far it got."""

from optimize_images import ImageOptimizer


def test_progress_line_reports_count_rate_and_eta(capsys):
    ImageOptimizer._print_progress(1000, 4000, 1800.0)  # 1000 in 30 min
    out = capsys.readouterr().out
    assert '1000/4000 images (25%)' in out
    assert '33/min' in out
    assert '~90 min left' in out


def test_progress_line_handles_zero_elapsed(capsys):
    ImageOptimizer._print_progress(250, 500, 0.0)
    assert '250/500 images (50%)' in capsys.readouterr().out
