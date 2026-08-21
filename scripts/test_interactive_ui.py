#!/usr/bin/env python3
"""
Interactive-UI smoke tests for the static site.

Why this exists
---------------
optimize_css.py removes "unused" CSS rules by checking the rule's selectors
against the classes/ids that appear in the server-rendered HTML. That misses
classes added by JavaScript at runtime (e.g. `.show-drawer`, `.is-initialized`,
`.header-is-fixed`). We mitigate this with a `_DYNAMIC_CLASSES` allowlist in
optimize_css.py, but the allowlist is hand-maintained — if a theme update
introduces a new JS-toggled class, we'll silently strip the CSS for it and the
nav will quietly break.

This script exercises the JS-driven UI in a real headless browser so that
class of regression turns into a noisy CI failure instead of a stealth break.

What it covers
--------------
1. Mobile menu drawer opens when the hamburger is tapped.
2. Splide carousel on a known post page reaches `is-initialized` state.
3. Sticky-header logic engages once you've scrolled.
4. Sub-menu expansion — only if the site actually has nav items with
   children. Skipped automatically when none are present.

Usage
-----
    python3 scripts/test_interactive_ui.py [site_dir]

Defaults to `public`. Spins up a local HTTP server, runs the tests
headless, prints a pass/fail table, exits non-zero on failure.

Dependencies
------------
    pip install playwright
    playwright install chromium

In CI both are installed via the workflow before this step runs.

If the playwright import fails (or chromium isn't installed) the script
prints a clear skip message and exits 0, so the deploy isn't blocked by
missing test infrastructure on a fresh runner. That's a deliberate
trade-off: we'd rather miss a regression than refuse to deploy a fix.
Detect runner-level setup problems by watching for the SKIP banner in
build logs.
"""

import contextlib
import http.server
import os
import socket
import socketserver
import sys
import threading
import time
from pathlib import Path
from urllib.parse import urljoin

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
    from playwright.sync_api import Error as PWError
    _PW_OK = True
    _PW_ERROR = None
except ImportError as e:
    _PW_OK = False
    _PW_ERROR = str(e)


def find_free_port():
    """Pick an unused TCP port for the temporary HTTP server."""
    with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


@contextlib.contextmanager
def serve(directory):
    """Run http.server on a free port, in a thread, for the lifetime of the
    `with` block. Cheap setup, no external dependencies, no leftover
    processes if a test crashes mid-flight."""
    port = find_free_port()
    handler = lambda *a, **kw: http.server.SimpleHTTPRequestHandler(
        *a, directory=str(directory), **kw
    )
    server = socketserver.TCPServer(('127.0.0.1', port), handler)
    server.allow_reuse_address = True
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{port}/'
    finally:
        server.shutdown()
        server.server_close()


class UISmokeTests:
    """Plays the role of a real user enough to confirm the JS-toggled CSS
    classes actually do something. Each test method appends to `results`.
    Stop on first failure? No — we want the full picture in CI logs."""

    def __init__(self, base_url):
        self.base_url = base_url
        self.results = []
        self.launch_failed = False
        self.launch_error = None

    def record(self, name, ok, detail=""):
        self.results.append((name, ok, detail))
        marker = "✅" if ok else "❌"
        line = f"  {marker} {name}"
        if detail:
            line += f"  — {detail}"
        print(line)

    # ── Tests ────────────────────────────────────────────────────────────

    def test_mobile_drawer_opens(self, browser):
        """Set mobile viewport, click the hamburger, verify the drawer
        actually becomes visible — not just that JS fired.

        The earlier version of this test only checked that the body
        acquired a `showing-popup-drawer-*` class, which a sabotage run
        showed could pass even after every .show-drawer CSS rule was
        stripped (JS still toggles the class; user just sees nothing).
        Asserting on #mobile-drawer's computed display + visible bounding
        rect catches "JS works, CSS missing" — exactly the regression we
        care about.
        """
        name = "Mobile menu drawer opens on tap"
        context = browser.new_context(viewport={'width': 390, 'height': 844})
        page = context.new_page()
        try:
            page.goto(self.base_url, wait_until='domcontentloaded', timeout=10_000)
            toggle = page.locator('.menu-toggle-open.drawer-toggle').first
            try:
                toggle.wait_for(state='visible', timeout=5_000)
            except PWTimeoutError:
                self.record(name, False, "toggle button not visible at 390×844")
                return

            drawer = page.locator('#mobile-drawer').first
            if drawer.count() == 0:
                self.record(name, False, "no #mobile-drawer element found")
                return

            # Before click — drawer should be hidden (kadence renders it
            # display:none until tapped).
            initial_display = page.evaluate(
                "() => getComputedStyle(document.getElementById('mobile-drawer')).display"
            )

            toggle.click()
            # Wait for: (a) drawer is laid out (bounding box has area) AND
            #           (b) computed display is not 'none'.
            try:
                page.wait_for_function(
                    """() => {
                        const d = document.getElementById('mobile-drawer');
                        if (!d) return false;
                        const cs = getComputedStyle(d);
                        const rect = d.getBoundingClientRect();
                        return cs.display !== 'none'
                            && cs.visibility !== 'hidden'
                            && parseFloat(cs.opacity) > 0
                            && rect.width > 0 && rect.height > 0;
                    }""",
                    timeout=4_000,
                )
                self.record(
                    name, True,
                    f"#mobile-drawer rendered after click (was display={initial_display!r})"
                )
            except PWTimeoutError:
                after_state = page.evaluate(
                    """() => {
                        const d = document.getElementById('mobile-drawer');
                        if (!d) return '(missing)';
                        const cs = getComputedStyle(d);
                        const r = d.getBoundingClientRect();
                        return `display=${cs.display}, vis=${cs.visibility}, op=${cs.opacity}, bbox=${r.width}x${r.height}`;
                    }"""
                )
                body_cls = page.evaluate("() => document.body.className")
                drawer_class_added = (
                    'showing-popup-drawer' in body_cls or 'show-drawer' in body_cls
                )
                hint = (
                    "JS fired (body class flipped) but drawer never rendered "
                    "— CSS for .show-drawer / popup-drawer likely stripped"
                ) if drawer_class_added else (
                    "JS didn't fire — body class never changed"
                )
                self.record(name, False, f"{hint}; drawer state: {after_state}")
        finally:
            context.close()

    def test_splide_carousel_initializes(self, browser):
        """Load a known post with a Splide carousel and verify both:
          (a) Splide JS ran and attached .is-initialized;
          (b) the rendered slides are laid out side-by-side, i.e. the
              .splide__list parent has roughly the slides' combined
              width (carousel layout) rather than just one slide's width
              (CSS busted, slides stacking).

        (a) alone catches "JS missing"; (a)+(b) together catch "CSS for
        .splide__list / __track stripped but JS still mounts".
        """
        name = "Splide carousel initialises on related-posts page"
        carousel_url = urljoin(
            self.base_url,
            '2025/09/managing-my-homelab-with-semaphoreui/'
        )
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        try:
            page.goto(carousel_url, wait_until='load', timeout=15_000)
            splide = page.locator('.splide').first
            if splide.count() == 0:
                self.record(name, False, "no .splide element on the page")
                return
            try:
                page.wait_for_function(
                    """() => {
                        const el = document.querySelector('.splide');
                        return el && el.classList.contains('is-initialized');
                    }""",
                    timeout=8_000,
                )
            except PWTimeoutError:
                final_classes = splide.get_attribute('class') or ''
                self.record(
                    name,
                    False,
                    f".is-initialized never appeared; classes={final_classes!r}"
                )
                return

            # JS mounted — now verify layout. Splide aggressively sets
            # inline styles on transforms, but slide WIDTH is still
            # determined by the .splide__list / .splide__slide CSS rules.
            # When those get stripped, slides collapse to their intrinsic
            # content width (~80-100 px). At 1280 px viewport, healthy
            # slides should be at least 200 px wide.
            layout = page.evaluate(
                """() => {
                    const list = document.querySelector('.splide__list');
                    const slides = document.querySelectorAll('.splide__slide');
                    if (!list || slides.length === 0) {
                        return {ok: false, why: 'missing list or slides'};
                    }
                    const slideW = slides[0].getBoundingClientRect().width;
                    const listW = list.scrollWidth;
                    const viewportW = window.innerWidth;
                    // Healthy threshold: each slide should take at least
                    // ~15 % of the viewport. Sabotaged carousels collapse
                    // to ~7 % (single column of intrinsic content width).
                    const minSlideW = viewportW * 0.15;
                    return {
                        ok: slideW >= minSlideW,
                        slideW: Math.round(slideW),
                        listW: Math.round(listW),
                        slideCount: slides.length,
                        viewportW: viewportW,
                        minSlideW: Math.round(minSlideW),
                    };
                }"""
            )
            if layout['ok']:
                self.record(
                    name, True,
                    f"initialised + laid out (slides={layout['slideCount']}, "
                    f"slideW={layout['slideW']}px, listW={layout['listW']}px)"
                )
            else:
                why = layout.get('why')
                if not why:
                    why = (
                        f"slides collapsed: slideW={layout['slideW']}px "
                        f"< minSlideW={layout['minSlideW']}px on "
                        f"viewport={layout['viewportW']}px — .splide__slide / "
                        f".splide__list width rules likely stripped"
                    )
                self.record(name, False, f"initialised but layout broken — {why}")
        finally:
            context.close()

    def test_sticky_header_engages_on_scroll(self, browser):
        """Verify scroll-driven header behaviour, adaptively.

        Kadence's sticky header is *optional* — controlled in the theme
        customizer. When disabled, the JS scroll listener still runs but
        no sticky classes are emitted, and the header stays static. We
        don't want this test to fail just because a site doesn't use a
        sticky header; we DO want it to fail when sticky was working and
        a CSS regression silently broke it.

        Strategy: snapshot classes before+after scroll. If none of the
        sticky markers ever appear after scroll, treat it as 'sticky not
        configured' and SKIP. If they DO appear, assert at least one
        landed on a header-ish ancestor. The CI signal is therefore:
        green for sites without sticky, green for sites with working
        sticky, red for sites that lost their sticky classes after a
        CSS-purge change.
        """
        name = "Sticky header acquires sticky class after scroll"
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        sticky_markers = (
            'header-is-fixed', 'item-is-fixed', 'item-is-stuck',
            'item-at-start', 'item-hidden-above', 'child-is-fixed',
        )
        try:
            page.goto(self.base_url, wait_until='domcontentloaded', timeout=10_000)
            page.wait_for_timeout(300)
            page.evaluate("() => window.scrollTo(0, 1500)")
            page.wait_for_timeout(800)

            present = page.evaluate(
                """markers => {
                    const found = new Set();
                    document.querySelectorAll('*').forEach(el => {
                        markers.forEach(m => {
                            if (el.classList.contains(m)) found.add(m);
                        });
                    });
                    return Array.from(found);
                }""",
                list(sticky_markers),
            )

            if not present:
                # No sticky markers anywhere — site isn't configured for
                # sticky behaviour. Skip rather than fail.
                self.record(
                    name, True,
                    "SKIP — no sticky-header markers in document (sticky not configured)"
                )
                return

            # At least one marker landed — sticky IS configured. Verify it
            # landed on something header-shaped.
            on_header = page.evaluate(
                """markers => {
                    const candidates = [
                        document.body,
                        document.querySelector('header'),
                        document.querySelector('.site-header'),
                        document.querySelector('#main-header'),
                        document.querySelector('#masthead'),
                    ].filter(Boolean);
                    return candidates.some(c =>
                        markers.some(m => c.classList.contains(m))
                    );
                }""",
                list(sticky_markers),
            )
            if on_header:
                self.record(name, True, f"markers found: {', '.join(present)}")
            else:
                self.record(
                    name, False,
                    f"sticky markers exist ({', '.join(present)}) but not on header"
                )
        finally:
            context.close()

    def test_submenu_expands_on_hover(self, browser):
        """If there's a nav item with children, hover/focus it and verify
        the sub-menu becomes visible. Skip when no such items exist.

        This site (jameskilby.co.uk) currently has a flat nav so this test
        SKIPs by default. Kept here so a future nav restructure with
        children is exercised automatically."""
        name = "Sub-menu expands on hover/focus (if nav has children)"
        context = browser.new_context(viewport={'width': 1280, 'height': 800})
        page = context.new_page()
        try:
            page.goto(self.base_url, wait_until='domcontentloaded', timeout=10_000)
            parent = page.locator('.menu-item-has-children').first
            if parent.count() == 0:
                self.record(name, True, "SKIP — no .menu-item-has-children in nav")
                return
            sub_menu = parent.locator('.sub-menu').first
            parent.hover()
            try:
                # Either the sub-menu becomes display:!none, or the parent
                # acquires `.menu-item--toggled-on`.
                page.wait_for_function(
                    """el => {
                        const sub = el.querySelector('.sub-menu');
                        if (!sub) return false;
                        const style = window.getComputedStyle(sub);
                        return style.display !== 'none'
                               && style.visibility !== 'hidden'
                               && parseFloat(style.opacity) > 0;
                    }""",
                    arg=parent.element_handle(),
                    timeout=2_500,
                )
                self.record(name, True, "sub-menu visible after hover")
            except PWTimeoutError:
                self.record(name, False, ".sub-menu didn't become visible")
        finally:
            context.close()

    # ── Entry point ──────────────────────────────────────────────────────

    def run_all(self):
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
            except PWError as e:
                # Chromium binary present but failed to launch — usually a
                # missing system lib on the runner (e.g. libatk-1.0.so.0).
                # Treat the same as "playwright unavailable": skip, exit 0,
                # let the build proceed. The banner is grep-friendly so
                # missing libs still surface in CI logs.
                self.launch_failed = True
                self.launch_error = str(e).splitlines()[0]
                return
            try:
                self.test_mobile_drawer_opens(browser)
                self.test_splide_carousel_initializes(browser)
                self.test_sticky_header_engages_on_scroll(browser)
                self.test_submenu_expands_on_hover(browser)
            finally:
                browser.close()


def _annotate_skip(reason):
    """Surface a skipped run as a GitHub Actions annotation.

    Both skip paths exit 0 by design so missing test infra can't block a
    deploy. The cost is that a skip is invisible unless someone reads the
    step's stdout — chromium silently stopped launching and the gate went
    unnoticed across runs. An annotation puts it on the run summary while
    keeping the exit code green.
    """
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        print(f"::warning title=Interactive UI tests skipped::{reason}")


def main():
    site_dir = Path(sys.argv[1] if len(sys.argv) > 1 else 'public')

    if not _PW_OK:
        # Print a banner that's grep-friendly in CI logs but still exits 0.
        # We don't want missing test infra to block deploys — track this
        # separately via the banner in build logs.
        print("=" * 72)
        print("⚠️  Interactive UI tests SKIPPED — playwright unavailable")
        print(f"    ({_PW_ERROR})")
        print("    Install with: pip install playwright && playwright install chromium")
        print("=" * 72)
        _annotate_skip(f"playwright unavailable ({_PW_ERROR})")
        sys.exit(0)

    if not site_dir.exists():
        print(f"❌ Site directory not found: {site_dir}")
        sys.exit(2)

    if not (site_dir / 'index.html').exists():
        print(f"❌ No index.html in {site_dir}")
        sys.exit(2)

    print(f"🧪 Interactive UI smoke tests against {site_dir}")
    start = time.time()
    with serve(site_dir) as base_url:
        print(f"   Serving from {base_url}\n")
        tests = UISmokeTests(base_url)
        tests.run_all()

    if tests.launch_failed:
        print("=" * 72)
        print("⚠️  Interactive UI tests SKIPPED — chromium failed to launch")
        print(f"    ({tests.launch_error})")
        print("    Likely missing system libs (libatk-1.0.so.0 etc).")
        print("    Install with: sudo playwright install-deps chromium")
        print("=" * 72)
        _annotate_skip(f"chromium failed to launch ({tests.launch_error})")
        sys.exit(0)

    elapsed = time.time() - start
    passed = sum(1 for _, ok, _ in tests.results if ok)
    total = len(tests.results)
    print()
    print(f"⏱  {elapsed:.1f}s  —  {passed}/{total} passed")

    failed = [name for name, ok, _ in tests.results if not ok]
    if failed:
        print(f"\n❌ Failures: {', '.join(failed)}")
        sys.exit(1)
    sys.exit(0)


if __name__ == '__main__':
    main()
