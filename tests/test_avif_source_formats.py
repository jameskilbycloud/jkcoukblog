"""AVIF must be produced from every upload format, not just PNG/JPEG.

The homepage hero — UnifiBeast-768x219.webp, the LCP element — shipped as a
23,778 B WebP with no AVIF anywhere on disk; AVIF encodes the same image at
12,968 B, 45% off the largest resource on the critical path. WordPress accepts
WebP and GIF uploads, but optimize_images only globbed png/jpg/jpeg, so those
files were never encoded. convert_images_to_picture then only wraps an <img>
when an AVIF sibling exists, so they stayed bare <img> tags — no AVIF source,
no <picture> at all. 23 WebP and 3 GIF files were in that state.

Two hazards this has to avoid, both covered below: a .webp source resolves
with_suffix('.webp') to itself (re-encoding would overwrite the original with
a generation-lossy copy on every build), and an animated GIF flattened to a
still frame would silently lose its animation.
"""

import re
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

from convert_images_to_picture import (  # noqa: E402
    CONVERTIBLE_EXT_RE,
    CONVERTIBLE_SRC_RE,
    CONVERTIBLE_SUFFIXES,
)


def _optimize_images():
    """Import optimize_images, or skip.

    It calls sys.exit(1) when Pillow/pillow-avif-plugin are missing, which
    pytest.importorskip cannot catch (SystemExit is not ImportError). The AVIF
    encoder lives in requirements-images.txt while CI's unit-test job installs
    requirements.txt, so this path is the normal one there — the format
    constants and converter regexes above still get full coverage.
    """
    try:
        import optimize_images
    except (ImportError, SystemExit):  # noqa: B014 - SystemExit is the real case
        pytest.skip('needs Pillow + pillow-avif-plugin (requirements-images.txt)')
    return optimize_images


# ── converter eligibility ────────────────────────────────────────────────

@pytest.mark.parametrize('src', [
    '/wp-content/uploads/2026/06/UnifiBeast-768x219.webp',
    '/wp-content/uploads/2023/04/AWS_Services.gif',
    '/wp-content/uploads/a.png',
    '/wp-content/uploads/a.jpg',
    '/wp-content/uploads/a.JPEG',
    '/wp-content/uploads/a.webp?v=2',
])
def test_convertible_sources_are_eligible(src):
    assert CONVERTIBLE_SRC_RE.search(src)


@pytest.mark.parametrize('src', [
    '/wp-content/uploads/logo.svg',
    '/wp-content/uploads/doc.pdf',
    '/wp-content/uploads/already.avif',
])
def test_non_convertible_sources_are_rejected(src):
    assert not CONVERTIBLE_SRC_RE.search(src)


@pytest.mark.parametrize('src,expected', [
    ('/a/UnifiBeast-768x219.webp', '/a/UnifiBeast-768x219'),
    ('/a/AWS_Services.gif', '/a/AWS_Services'),
    ('/a/b.PNG', '/a/b'),
])
def test_variant_basename_strips_every_convertible_extension(src, expected):
    """base_src is what the AVIF/WebP <source> srcsets are built from — an
    unstripped extension produces /a/b.webp.avif, which 404s."""
    assert CONVERTIBLE_EXT_RE.sub('', src) == expected


def test_converter_and_encoder_agree_on_formats():
    """The two lists drifted apart once already: the encoder gained no new
    formats but the converter's filter was the reason webp/gif images stayed
    bare even where an AVIF existed."""
    optimize_images = _optimize_images()
    assert set(CONVERTIBLE_SUFFIXES) == optimize_images.ImageOptimizer.SOURCE_EXTENSIONS


# ── encoder behaviour ────────────────────────────────────────────────────

@pytest.fixture
def optimizer(tmp_path):
    optimize_images = _optimize_images()
    # Explicit cache_dir: the default is the repo's real
    # .image_optimization_cache, and its 3,000+ live entries would decide
    # whether these fixtures get optimised.
    return optimize_images, optimize_images.ImageOptimizer(
        str(tmp_path), cache_dir=str(tmp_path / '.cache'))


def _uploads(tmp_path):
    d = tmp_path / 'wp-content' / 'uploads' / '2026' / '06'
    d.mkdir(parents=True, exist_ok=True)
    return d


def test_webp_and_gif_are_discovered(optimizer, tmp_path):
    _, opt = optimizer
    from PIL import Image
    d = _uploads(tmp_path)
    for name in ('hero.webp', 'anim.gif', 'shot.png', 'logo.svg'):
        if name.endswith('.svg'):
            (d / name).write_text('<svg/>', encoding='utf-8')
        else:
            Image.new('RGB', (12, 12), 'red').save(d / name)

    found = {p.name for p in opt.find_all_images()}
    assert {'hero.webp', 'anim.gif', 'shot.png'} <= found
    assert 'logo.svg' not in found


def test_webp_source_is_not_overwritten_by_its_own_encode(optimizer, tmp_path):
    """with_suffix('.webp') on a .webp source is the source. Re-encoding it
    would replace the original with a lossy copy of itself, compounding on
    every build."""
    _, opt = optimizer
    from PIL import Image
    d = _uploads(tmp_path)
    src = d / 'hero.webp'
    Image.new('RGB', (60, 40), 'blue').save(src, 'WEBP', quality=95)
    before = src.read_bytes()

    result = opt.optimize_image(src)

    assert src.read_bytes() == before, 'the .webp source was rewritten'
    assert result['webp_created'] is False, 'counted a WebP it did not create'
    assert (d / 'hero.avif').exists(), 'no AVIF produced for the .webp source'


def test_animated_gif_is_left_alone(optimizer, tmp_path):
    """Flattening an animation to a still and wrapping it in <picture> would
    replace a moving image with a frozen frame."""
    _, opt = optimizer
    from PIL import Image
    d = _uploads(tmp_path)
    src = d / 'anim.gif'
    # Frames must differ in pixel content: PIL collapses identical solid
    # frames into a single one, and the fixture then isn't animated at all.
    frames = []
    for i in range(3):
        frame = Image.new('RGB', (20, 20), 'black')
        for x in range(20):
            frame.putpixel((x, (x + i * 5) % 20), (255, 255, 255))
        frames.append(frame.convert('P'))
    frames[0].save(src, save_all=True, append_images=frames[1:], duration=100, loop=0)
    assert Image.open(src).n_frames == 3, 'fixture is not animated'

    result = opt.optimize_image(src)

    assert not (d / 'anim.avif').exists()
    assert result['error'] == 'animated source skipped'


def test_still_gif_gets_both_modern_formats(optimizer, tmp_path):
    _, opt = optimizer
    from PIL import Image
    d = _uploads(tmp_path)
    src = d / 'still.gif'
    Image.new('P', (30, 20), 3).save(src)

    opt.optimize_image(src)

    assert (d / 'still.avif').exists()
    assert (d / 'still.webp').exists()


def test_no_stray_png_variants_from_webp_masters(optimizer, tmp_path):
    """The extra-width helper writes `<stem>.png`; running it for a .webp
    master would materialise PNGs nothing on the site references."""
    _, opt = optimizer
    from PIL import Image
    d = _uploads(tmp_path)
    src = d / 'master.webp'          # no WP -WxH suffix, so it is a "master"
    Image.new('RGB', (1400, 400), 'green').save(src, 'WEBP')

    opt.optimize_image(src)

    strays = [p.name for p in d.glob('*.png')]
    assert strays == [], f'unexpected PNG variants written: {strays}'


def test_avif_is_smaller_than_the_webp_it_supplements(optimizer, tmp_path):
    """The whole point — if AVIF isn't smaller here the change costs bytes."""
    _, opt = optimizer
    from PIL import Image
    d = _uploads(tmp_path)
    src = d / 'photo.webp'
    img = Image.new('RGB', (400, 300))
    img.putdata([(x % 256, (x * 7) % 256, (x * 13) % 256)
                 for x in range(400 * 300)])
    img.save(src, 'WEBP', quality=85)

    opt.optimize_image(src)

    assert (d / 'photo.avif').stat().st_size < src.stat().st_size


def test_source_extensions_are_lowercase_and_dotted():
    """find_all_images globs both cases off this set; a missing dot or an
    uppercase entry silently drops a whole format."""
    optimize_images = _optimize_images()
    for ext in optimize_images.ImageOptimizer.SOURCE_EXTENSIONS:
        assert re.fullmatch(r'\.[a-z0-9]+', ext), ext
