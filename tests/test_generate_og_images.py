"""Tests for generate_og_images' card trigger and meta rewriting (no rendering)."""

from PIL import Image

from generate_og_images import OGImageGenerator


def _gen(tmp_path):
    return OGImageGenerator(tmp_path)


def _html(og_url, width=None, title="Can't stop: a post", alt='Old diagram'):
    w = f'<meta content="{width}" property="og:image:width"/>' if width else ''
    return (
        f'<head><title>{title} - James Kilby</title>'
        f'<meta content="{title}" property="og:title"/>'
        f'<meta content="{og_url}" property="og:image"/>{w}'
        '<meta content="501" property="og:image:height"/>'
        '<meta content="image/webp" property="og:image:type"/>'
        f'<meta content="{alt}" property="og:image:alt"/>'
        f'<meta content="{og_url}" name="twitter:image"/>'
        f'<meta content="{alt}" name="twitter:image:alt"/></head>'
    )


def test_fallback_image_needs_card(tmp_path):
    url = 'https://jameskilby.co.uk/wp-content/uploads/2025/12/ChatGPT-Image-x.png'
    assert _gen(tmp_path)._needs_card(_html(url, 1024), url) == 'fallback'


def test_small_image_needs_card(tmp_path):
    url = 'https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png'
    assert _gen(tmp_path)._needs_card(_html(url, 588), url) == 'small'


def test_wide_image_kept(tmp_path):
    url = 'https://jameskilby.co.uk/wp-content/uploads/2026/06/UnifiBeast.webp'
    assert _gen(tmp_path)._needs_card(_html(url, 1400), url) is None


def test_generated_card_not_reprocessed(tmp_path):
    url = 'https://jameskilby.co.uk/wp-content/uploads/og/some-post.png'
    assert _gen(tmp_path)._needs_card(_html(url, 600), url) is None


def test_width_measured_from_file_when_meta_missing(tmp_path):
    img = tmp_path / 'wp-content/uploads/2026/04/small.png'
    img.parent.mkdir(parents=True)
    Image.new('RGB', (640, 300)).save(img)
    url = 'https://jameskilby.co.uk/wp-content/uploads/2026/04/small.png'
    assert _gen(tmp_path)._needs_card(_html(url), url) == 'small'


def test_unknown_width_left_alone(tmp_path):
    url = 'https://jameskilby.co.uk/wp-content/uploads/2026/04/missing.png'
    assert _gen(tmp_path)._needs_card(_html(url), url) is None


def test_title_with_apostrophe_extracted_whole(tmp_path):
    url = 'https://jameskilby.co.uk/x.png'
    assert _gen(tmp_path)._extract_title(_html(url)) == "Can't stop: a post"


def test_rewrite_meta_updates_image_size_type_and_alt():
    url = 'https://jameskilby.co.uk/wp-content/uploads/2026/04/offlinedepot.png'
    new = 'https://jameskilby.co.uk/wp-content/uploads/og/post.png'
    html = _html(url, 588, alt="It's the old diagram")
    out = OGImageGenerator._rewrite_meta(html, new, alt='A "quoted" title')
    assert f'<meta content="{new}" property="og:image"/>' in out
    assert f'<meta content="{new}" name="twitter:image"/>' in out
    assert '<meta content="1200" property="og:image:width"/>' in out
    assert '<meta content="630" property="og:image:height"/>' in out
    assert '<meta content="image/png" property="og:image:type"/>' in out
    assert '<meta content="A &quot;quoted&quot; title" property="og:image:alt"/>' in out
    assert '<meta content="A &quot;quoted&quot; title" name="twitter:image:alt"/>' in out
    assert 'old diagram' not in out
