"""Tests for build-time injection of the homelab power widget into the lab
page (wp_to_static_generator.inject_power_widget).

The widget is a repo-maintained partial injected into public/lab/index.html at
build time (not WordPress content). Injection is idempotent via the widget's
stable id, inserts before the Table-of-Contents anchor, and only touches the
lab page.

inject_power_widget only uses self.output_dir and self._POWER_WIDGET_ANCHORS
(and reads the real partial from scripts/assets/), so we exercise it against a
lightweight stub rather than the full WordPress-dependent generator.
"""

import types

from wp_to_static_generator import WordPressStaticGenerator as G

TOC = '<div class="wp-block-rank-math-toc-block" id="rank-math-toc">'
CONTENT = '<div class="entry-content single-content">'


def _lab_html(anchor=TOC):
    return (
        "<html><body><main>"
        f"<p>My homelab intro.</p>{anchor}<h2>At a Glance</h2>"
        "</main></body></html>"
    )


def _run(tmp_path, lab_html):
    lab = tmp_path / 'lab'
    lab.mkdir()
    (lab / 'index.html').write_text(lab_html)
    stub = types.SimpleNamespace(
        output_dir=tmp_path,
        _POWER_WIDGET_ANCHORS=G._POWER_WIDGET_ANCHORS,
    )
    G.inject_power_widget(stub)
    return (lab / 'index.html').read_text()


def test_injects_widget_before_toc(tmp_path):
    out = _run(tmp_path, _lab_html(TOC))
    assert out.count('id="homelab-power"') == 1
    # widget must sit before the TOC anchor
    assert out.index('id="homelab-power"') < out.index('id="rank-math-toc"')
    # and after the intro paragraph
    assert out.index('My homelab intro') < out.index('id="homelab-power"')


def test_idempotent_second_run_no_duplicate(tmp_path):
    once = _run(tmp_path, _lab_html(TOC))
    # feed the already-injected HTML back through: must be unchanged
    lab = tmp_path / 'lab'
    (lab / 'index.html').write_text(once)
    stub = types.SimpleNamespace(
        output_dir=tmp_path, _POWER_WIDGET_ANCHORS=G._POWER_WIDGET_ANCHORS)
    G.inject_power_widget(stub)
    twice = (lab / 'index.html').read_text()
    assert twice == once
    assert twice.count('id="homelab-power"') == 1


def test_fallback_anchor_when_no_toc(tmp_path):
    out = _run(tmp_path, _lab_html(CONTENT))
    assert out.count('id="homelab-power"') == 1
    assert out.index('id="homelab-power"') < out.index(CONTENT.split('>')[0])


def test_no_anchor_leaves_page_untouched(tmp_path):
    html = "<html><body><main><p>no anchors here</p></main></body></html>"
    out = _run(tmp_path, html)
    assert 'id="homelab-power"' not in out
    assert out == html


def test_missing_lab_page_is_noop(tmp_path):
    # No lab/ dir at all — must not raise.
    stub = types.SimpleNamespace(
        output_dir=tmp_path, _POWER_WIDGET_ANCHORS=G._POWER_WIDGET_ANCHORS)
    G.inject_power_widget(stub)  # should simply print + return


def test_stale_widget_is_replaced_in_place(tmp_path):
    """An older widget baked into public/ must be swapped for the current one.

    Regression: the guard only asked "is a widget present?", so once any copy
    was committed under public/ the partial was frozen and edits to it could
    never reach the site.
    """
    once = _run(tmp_path, _lab_html(TOC))
    stale = once.replace('data-power-widget-version="', 'data-power-widget-version="old', 1)
    assert stale != once
    lab = tmp_path / 'lab'
    (lab / 'index.html').write_text(stale)
    stub = types.SimpleNamespace(
        output_dir=tmp_path, _POWER_WIDGET_ANCHORS=G._POWER_WIDGET_ANCHORS)
    G.inject_power_widget(stub)
    out = (lab / 'index.html').read_text()
    assert out == once, "stale widget should be refreshed back to current"
    assert out.count('id="homelab-power"') == 1
    # still positioned before the TOC, i.e. replaced in place
    assert out.index('id="homelab-power"') < out.index('id="rank-math-toc"')


def test_unversioned_legacy_widget_is_replaced(tmp_path):
    """A widget from before the version stamp existed must still be upgraded.

    This is the exact shape sitting in public/lab/index.html today: the card as
    the root element, no wrapper and no version attribute.
    """
    legacy = (
        '<div id="homelab-power" class="hp" aria-live="polite">'
        '<span class="hp-watts">—</span></div>'
        '<style>#homelab-power{color:red}</style>'
        '<script>(function(){var x=1;})();</script>'
    )
    html = f"<html><body><main><p>Intro.</p>{legacy}{TOC}<h2>At a Glance</h2></main></body></html>"
    out = _run(tmp_path, html)
    assert 'data-power-widget-version="' in out, "legacy widget should be upgraded"
    assert 'What am I looking at' in out, "current partial's explainer should be present"
    assert out.count('id="homelab-power"') == 1, "must not leave the old copy behind"
    assert '#homelab-power{color:red}' not in out, "old widget CSS should be gone"


def test_repeated_runs_are_stable(tmp_path):
    """Three consecutive builds must not churn the page (noisy public/ diffs)."""
    first = _run(tmp_path, _lab_html(TOC))
    lab = tmp_path / 'lab'
    for _ in range(2):
        stub = types.SimpleNamespace(
            output_dir=tmp_path, _POWER_WIDGET_ANCHORS=G._POWER_WIDGET_ANCHORS)
        G.inject_power_widget(stub)
    assert (lab / 'index.html').read_text() == first


def test_partial_root_is_stampable():
    """The injector stamps the version onto this exact root; guard the contract."""
    from pathlib import Path
    import re as _re
    import wp_to_static_generator as mod
    partial = (Path(mod.__file__).parent / 'partials'
               / 'homelab-power-widget.html').read_text()
    assert _re.search(r'<div\b[^>]*\bid="homelab-power-block"', partial), \
        "inject_power_widget stamps id=homelab-power-block; root must keep it"


def test_partial_contains_expected_hooks():
    # Guard the contract the injector/JS relies on.
    from pathlib import Path
    import wp_to_static_generator as mod
    partial = (Path(mod.__file__).parent / 'partials'
               / 'homelab-power-widget.html').read_text()
    assert 'id="homelab-power"' in partial
    assert '/api/power' in partial
    assert 'hp-watts' in partial and 'hp-spark-line' in partial
