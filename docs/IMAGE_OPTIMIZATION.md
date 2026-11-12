# Image Optimization

Every JPEG/PNG in the build gets AVIF and WebP siblings, and every `<img>` is
served through a `<picture>` element so browsers pick the smallest format they
support. This runs inside the deploy workflow; there is no separate image
workflow.

## How it works

1. **Generate** downloads the originals from WordPress into
   `static-output/wp-content/uploads/`, seeded from the previous build
   (restored from the `site` branch). AVIF/WebP files from that build are copied
   across with `rsync --ignore-existing`, so unchanged images aren't re-encoded
   (unless the run was dispatched with `reencode_images=true`).
   Originals are never copied from the previous build: a size difference can
   only mean the image was replaced in WordPress.
2. **"Optimize images"** runs `scripts/optimize_images.py`:
   ```bash
   python3 scripts/optimize_images.py ./static-output --workers 4 --skip-html \
     --json-output optimization-results.json --cache-dir .image_optimization_cache
   ```
   - Encodes with **Pillow** and its built-in AVIF support (Pillow >= 11.2
     wheels; `pillow-avif-plugin` is no longer used): WebP at quality 85 / `method=6`, AVIF at quality 85 /
     `speed=4`, and an extra 480 px-wide variant of each for `srcset`.
   - Transparent images are flattened onto white before encoding.
   - A source that already *is* `.webp` isn't re-encoded over itself.
   - Results are cached by BLAKE2b content hash in
     `.image_optimization_cache/optimization_cache.json`, which is committed to
     `main` when it changes. An image is skipped when its AVIF and WebP already
     exist and its hash still matches the cache.
   - `--skip-html`: the script can also rewrite `<img>` into `<picture>`, but CI
     leaves that to the transformer below. Doing both rewrote ~250 pages per
     build for nothing — the final HTML was byte-identical either way.
   - `--force` (`reencode_images=true`) re-encodes every source even when its
     AVIF/WebP exist and the hash matches.
3. **The single-pass HTML transformer** (`html_transformer.py`) runs
   `convert_images_to_picture.py` over every page: `<picture>` with AVIF and
   WebP `<source>`s and the original as the `<img>` fallback. In the same pass,
   `enhance_html_performance.py` sets `fetchpriority="high"` on the first
   content image (the LCP candidate) and `loading="lazy"` + `decoding="async"`
   on the rest.

Browser behaviour: AVIF where supported (Chrome, Edge, Firefox, Safari 16+),
otherwise WebP, otherwise the original.

## Running it locally

```bash
make generate          # needs WP access — see DEVELOPMENT.md
make optimize-images   # encode AVIF/WebP in ./static-output (FORCE=1 re-encodes everything)
make optimize-html     # <picture> markup, via the single-pass transformer
```

Options: `--quality` (default 85), `--workers` (default 4), `--skip-html`,
`--force`, `--json-output`, `--cache-dir`. Run `python3 scripts/optimize_images.py --help`.

Requirements: `pip install -r requirements-images.txt` (Pillow, which encodes
AVIF natively). The script exits if Pillow can't encode AVIF.

## Troubleshooting

**No AVIF/WebP for an image** — check the "Optimize images" step log for that
file. To re-encode everything, run `force-full-deploy.yml` with
`reencode_images=true` (or `make optimize-images FORCE=1` locally).

**An image replaced in WordPress still shows the old version** — the original is
re-downloaded and its hash changes, so new AVIF/WebP files are generated. If the
old one is still served, it's the CDN/KV cache: see "Site shows old content" in
[DEPLOYMENT.md](DEPLOYMENT.md#troubleshooting).

**`ERROR: Required packages not installed`** or **`can't encode AVIF`** —
`pip install -r requirements-images.txt` (a PyPI Pillow wheel).

## Related Documentation
- [OPTIMIZATION.md](OPTIMIZATION.md) — compression, CSS and JS
- [DEPLOYMENT.md](DEPLOYMENT.md) — where this sits in the pipeline
