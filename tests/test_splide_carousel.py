"""Tests for InlineCSSFixups.fix_splide_carousel.

WordPress ships the Kadence theme's own Splide + kadenceSlide init next to
the related-posts carousel, and fix_splide_carousel injects the vendored
/js/splide.min.js plus its own init. Both together load Splide twice and
mount the carousel twice, so the theme's copy must be stripped.
"""

from pathlib import Path

from bs4 import BeautifulSoup

from inline_css_fixups import InlineCSSFixups

THEME = '/wp-content/themes/kadence/assets/js'
CAROUSEL = '<div class="entry-related-carousel kadence-slide-init splide is-initialized"></div>'
THEME_HEAD = (
    f'<link rel="preload" as="script" href="{THEME}/splide.min.js">'
    f'<link rel="preload" as="script" href="{THEME}/splide-init.min.js?ver=1.2">'
    f'<link rel="preload" as="script" href="{THEME}/navigation.min.js">'
)
THEME_BODY = (
    f'<script async id="kad-splide-js" src="{THEME}/splide.min.js"></script>'
    '<script id="kadence-slide-init-js-extra">var kadenceSlideConfig = {};</script>'
    f'<script async id="kadence-slide-init-js" src="{THEME}/splide-init.min.js"></script>'
    f'<script async id="kadence-navigation-js" src="{THEME}/navigation.min.js"></script>'
)


def _run(body):
    soup = BeautifulSoup(f'<html><head>{THEME_HEAD}</head><body>{body}</body></html>', 'html.parser')
    InlineCSSFixups('https://wp.example', Path('/nonexistent')).fix_splide_carousel(soup)
    return soup


def _splide_srcs(soup):
    return [s['src'] for s in soup.find_all('script', src=True) if 'splide' in s['src']]


def test_theme_splide_replaced_by_single_vendored_copy():
    soup = _run(CAROUSEL + THEME_BODY)
    assert _splide_srcs(soup) == ['/js/splide.min.js']
    assert soup.find(id='kadence-slide-init-js-extra') is None
    preloads = [lnk['href'] for lnk in soup.find_all('link', rel='preload')]
    assert preloads == [f'{THEME}/navigation.min.js']
    assert soup.find(id='kadence-navigation-js') is not None
    assert 'is-initialized' not in soup.find(class_='kadence-slide-init')['class']


def test_page_without_carousel_untouched():
    soup = _run(THEME_BODY)
    assert _splide_srcs(soup) == [f'{THEME}/splide.min.js', f'{THEME}/splide-init.min.js']
    assert len(soup.find_all('link', rel='preload')) == 3


def _init_js(soup):
    return next(s.string for s in soup.find_all('script') if s.string and 'new Splide(' in s.string)


def _inline_css(soup):
    return ''.join(s.string or '' for s in soup.find_all('style'))


def test_init_adds_splide_initial_before_mount():
    # The theme lays the slides out in a row only under .splide.splide-initial;
    # without it the list stays a grid and every slide collapses (Nov 2026).
    js = _init_js(_run(CAROUSEL + THEME_BODY))
    assert "el.classList.add('splide-initial')" in js
    assert js.index("classList.add('splide-initial')") < js.index('new Splide(')


def test_arrow_css_includes_splide_core_layout():
    # Without Splide's core arrow rules the buttons sit in normal flow and
    # the theme's button padding squeezes the icon to 0px wide.
    css = _inline_css(_run(CAROUSEL + THEME_BODY))
    arrow = css.split('.splide button.splide__arrow{', 1)[1].split('}', 1)[0]
    for decl in ('position:absolute', 'display:flex', 'align-items:center',
                 'justify-content:center', 'padding:0'):
        assert decl in arrow
    assert '.splide button.splide__arrow--prev svg{transform:scaleX(-1)}' in css
