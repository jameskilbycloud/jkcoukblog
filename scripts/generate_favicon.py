#!/usr/bin/env python3
"""Generate the JK monogram favicons from the locked logo.

Renders the inverted-tile JK mark — black field, orange rule, Anton "JK"
reversed out in the accent, the same mark used in the site header — to the
favicon set:

    favicon.ico            (16 / 32 / 48 multi-size)
    favicon-16x16.png
    favicon-32x32.png
    apple-touch-icon.png   (180, opaque field for the iOS mask)

Output goes to scripts/static-files/, which the build copies to the site root
(the <link rel="icon"> tags are already emitted by add_favicon_links()).

Pillow can't read woff2, so we reuse the Anton woff2 → ttf trick from
generate_og_images.py. Render big once and downscale (LANCZOS) for crisp
small icons.

Run: python3 scripts/generate_favicon.py
Dependencies: Pillow, fontTools[woff] (already in requirements.txt).
"""

import sys
import tempfile
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
    from fontTools.ttLib import TTFont
except ImportError as e:  # pragma: no cover
    print(f"❌ Missing dependency: {e} (need Pillow + fontTools[woff])")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
ANTON_WOFF2 = ROOT / 'scripts' / 'fonts' / 'anton-v27-latin-400.woff2'
OUT_DIR = ROOT / 'scripts' / 'static-files'

INK = (10, 10, 10, 255)        # #0a0a0a
ACCENT = (246, 130, 31, 255)   # #f6821f
MASTER = 512                   # render at this size, then downscale


def _anton_ttf():
    """Strip the woff2 wrapper → a TrueType file PIL can render. Temp, per run."""
    tmp = tempfile.NamedTemporaryFile(suffix='.ttf', prefix='anton-', delete=False)
    tmp.close()
    font = TTFont(str(ANTON_WOFF2))
    font.flavor = None
    font.save(tmp.name)
    return tmp.name


def render_master(ttf, opaque=False):
    """Draw the inverted JK tile at MASTER px. opaque fills the whole canvas
    (apple-touch — iOS masks to a rounded square, transparency looks wrong)."""
    s = MASTER
    img = Image.new('RGBA', (s, s), INK if opaque else (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    inset = round(s * 0.04)
    border = round(s * 0.06)
    tile = [inset, inset, s - inset - 1, s - inset - 1]
    draw.rectangle(tile, fill=INK)                       # black field
    draw.rectangle(tile, outline=ACCENT, width=border)   # orange rule

    font = ImageFont.truetype(ttf, round(s * 0.6))
    bbox = draw.textbbox((0, 0), 'JK', font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    pos = ((s - tw) / 2 - bbox[0], (s - th) / 2 - bbox[1])
    draw.text(pos, 'JK', font=font, fill=ACCENT)
    return img


def main():
    if not ANTON_WOFF2.exists():
        print(f"❌ Anton font not found at {ANTON_WOFF2}")
        sys.exit(1)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    ttf = _anton_ttf()
    master = render_master(ttf)
    master_opaque = render_master(ttf, opaque=True)

    def save_png(img, size, name):
        img.resize((size, size), Image.LANCZOS).save(OUT_DIR / name)
        print(f"   ✅ {name} ({size}px)")

    save_png(master, 16, 'favicon-16x16.png')
    save_png(master, 32, 'favicon-32x32.png')
    save_png(master_opaque, 180, 'apple-touch-icon.png')

    master.resize((48, 48), Image.LANCZOS).save(
        OUT_DIR / 'favicon.ico', sizes=[(16, 16), (32, 32), (48, 48)])
    print("   ✅ favicon.ico (16/32/48)")
    print(f"🎨 JK favicons written → {OUT_DIR}")


if __name__ == '__main__':
    main()
