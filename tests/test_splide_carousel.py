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
