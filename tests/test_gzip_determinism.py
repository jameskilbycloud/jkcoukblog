"""Gzip sidecars must be byte-identical for identical input.

The pipeline commits pre-compressed .br/.gz next to every asset, so any
non-determinism in the compressor lands in git. gzip.open(path, 'wb') stamps
the current time into the header MTIME field, so recompressing an unchanged
page on a later build produced different bytes: 589 of the 617 sidecars in
the 2026-08-09 08:51 deploy had a source file that never changed. Brotli's
format carries no timestamp, which is why only 14 .br moved in that commit
against 598 .gz — these tests pin both sides.

The HTML transformer rewrites every page each build, so source mtime always
beats sidecar mtime and should_compress_gzip() always recompresses. Content
stability is therefore the only thing standing between an unchanged page and
a committed diff.
"""

import gzip
import sys
import time
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

pytest.importorskip('brotli')
from brotli_compress import BrotliCompressor  # noqa: E402


# Must exceed the 1 KB floor in should_compress_gzip and compress by >5%,
# or the sidecar is skipped rather than written.
PAYLOAD = ('<html><body>' + ('<p>compressible prose repeated. </p>' * 200)
           + '</body></html>')


def _compress(tmp_path: Path, name: str) -> bytes:
    """Write PAYLOAD, gzip it through the pipeline, return the sidecar bytes."""
    root = tmp_path / name
    root.mkdir(parents=True, exist_ok=True)
    source = root / 'index.html'
    source.write_text(PAYLOAD, encoding='utf-8')

    # quality=1: these tests are about determinism, not compression ratio,
    # and q11 on every case makes the suite needlessly slow.
    compressor = BrotliCompressor(root, quality=1)
    result = compressor._compress_one_gzip(source)
    assert result['success'] is True, f'gzip sidecar not written: {result}'
    return (root / 'index.html.gz').read_bytes()


def test_gzip_output_is_stable_across_time(tmp_path):
    """The regression: same bytes in, same bytes out, a second later."""
    first = _compress(tmp_path, 'first')
    time.sleep(1.1)  # long enough to tick the header's 1-second MTIME field
    second = _compress(tmp_path, 'second')

    assert first == second, (
        'gzip sidecar changed with wall-clock time — the header MTIME field '
        'is being populated, which recommits every sidecar on every build'
    )


def test_gzip_header_mtime_is_zeroed(tmp_path):
    """Assert the mechanism directly, so a future refactor back to
    gzip.open(path) fails here with an obvious reason rather than only
    tripping the timing test above."""
    data = _compress(tmp_path, 'header')
    mtime_field = int.from_bytes(data[4:8], 'little')
    assert mtime_field == 0, f'gzip header MTIME is {mtime_field}, expected 0'


def test_gzip_sidecar_round_trips(tmp_path):
    """Determinism is worthless if the bytes don't decompress."""
    data = _compress(tmp_path, 'roundtrip')
    assert gzip.decompress(data).decode('utf-8') == PAYLOAD


def test_brotli_output_is_stable_across_time(tmp_path):
    """Brotli has no timestamp field, so this already held — pin it so the
    two sidecars can't drift apart."""
    root = tmp_path / 'brotli'
    root.mkdir()
    source = root / 'index.html'
    source.write_text(PAYLOAD, encoding='utf-8')
    compressor = BrotliCompressor(root, quality=1)

    assert compressor._compress_one_gzip(source)['success'] is True
    assert compressor._compress_one_brotli(source)['success'] is True
    first = (root / 'index.html.br').read_bytes()

    time.sleep(1.1)
    assert compressor._compress_one_brotli(source)['success'] is True
    assert (root / 'index.html.br').read_bytes() == first


def test_incompressible_input_leaves_no_sidecar(tmp_path):
    """Below the 5% threshold nothing should be written — and any sidecar an
    earlier build left behind must be removed, not served stale."""
    root = tmp_path / 'incompressible'
    root.mkdir()
    source = root / 'random.json'
    # os.urandom is not meaningfully compressible.
    import os
    source.write_bytes(os.urandom(4096))
    stale = root / 'random.json.gz'
    stale.write_bytes(b'stale sidecar from an earlier build')

    result = BrotliCompressor(root, quality=1)._compress_one_gzip(source)

    assert result['success'] is False
    assert not stale.exists(), 'stale sidecar left on disk'
