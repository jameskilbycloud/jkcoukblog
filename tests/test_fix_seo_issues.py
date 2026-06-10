"""Tests for the SEO fixer's pure transforms."""

from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from fix_seo_issues import SEOFixer


@pytest.fixture
def fixer(tmp_path):
    return SEOFixer(public_dir=str(tmp_path))


def _soup(html):
    return BeautifulSoup(html, 'html.parser')


class TestCleanTruncate:
    def test_short_text_passes_through(self):
        assert SEOFixer._clean_truncate('Short text.', 100) == 'Short text.'

    def test_cuts_at_sentence_boundary(self):
        # The sentence terminator must land in the latter half of the window
        # for the sentence cut to be taken (avoids overly short snippets).
        text = 'First sentence goes here nicely. Second part continues even longer.'
        out = SEOFixer._clean_truncate(text, 40)
        assert out == 'First sentence goes here nicely.'

    def test_early_sentence_break_falls_back_to_word_cut(self):
        # Terminator in the first half of the window → word-boundary cut wins.
        text = 'First sentence here. Second sentence is much longer and goes on.'
        out = SEOFixer._clean_truncate(text, 40)
        assert out == 'First sentence here. Second sentence is'

    def test_cuts_at_word_boundary_without_ellipsis(self):
        text = 'word ' * 50
        out = SEOFixer._clean_truncate(text, 32)
        assert len(out) <= 32
        assert not out.endswith('...')
        assert not out.endswith(' ')

    def test_never_breaks_mid_word(self):
        text = 'supercalifragilistic expialidocious words continue here'
        out = SEOFixer._clean_truncate(text, 30)
        assert out in text  # a clean prefix cut at a word boundary


class TestFixMultipleH1:
    def test_extra_h1s_demoted_to_h2(self, fixer):
        soup = _soup('<body><h1>Keep</h1><h1>Demote</h1><h1>Demote too</h1></body>')
        assert fixer.fix_multiple_h1(soup, Path('x.html')) is True
        assert len(soup.find_all('h1')) == 1
        assert soup.find('h1').get_text() == 'Keep'
        assert len(soup.find_all('h2')) == 2

    def test_single_h1_untouched(self, fixer):
        soup = _soup('<body><h1>Only</h1></body>')
        assert fixer.fix_multiple_h1(soup, Path('x.html')) is False
        assert len(soup.find_all('h1')) == 1


class TestEnsureImageAltText:
    def test_alt_derived_from_filename(self, fixer):
        soup = _soup('<img src="/wp-content/uploads/my-test-image.png">')
        assert fixer.ensure_image_alt_text(soup, Path('x.html')) is True
        assert soup.find('img')['alt'] == 'My Test Image'

    def test_existing_alt_untouched(self, fixer):
        soup = _soup('<img src="/a.png" alt="Hand written alt">')
        assert fixer.ensure_image_alt_text(soup, Path('x.html')) is False
        assert soup.find('img')['alt'] == 'Hand written alt'

    def test_srcless_image_gets_generic_alt(self, fixer):
        soup = _soup('<img>')
        fixer.ensure_image_alt_text(soup, Path('x.html'))
        assert soup.find('img')['alt'] == 'Image'


class TestFixTitleLength:
    def test_truncated_title_restored_from_jsonld(self, fixer):
        soup = _soup(
            '<head><title>How to configure VMware vSphere with...</title>'
            '<script type="application/ld+json">'
            '{"@graph": [{"@type": "TechArticle", '
            '"headline": "How to configure VMware vSphere with NSX overlay networking"}]}'
            '</script></head>'
        )
        assert fixer.fix_title_length(soup, Path('x.html')) is True
        assert soup.find('title').get_text() == (
            'How to configure VMware vSphere with NSX overlay networking')

    def test_untruncated_title_left_alone(self, fixer):
        soup = _soup('<head><title>A perfectly fine title</title></head>')
        assert fixer.fix_title_length(soup, Path('x.html')) is False

    def test_no_jsonld_means_no_change(self, fixer):
        soup = _soup('<head><title>Broken title that ends with...</title></head>')
        assert fixer.fix_title_length(soup, Path('x.html')) is False
        assert soup.find('title').get_text() == 'Broken title that ends with...'
