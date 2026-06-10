"""Guard the dependency-pinning invariants.

requirements-images.txt overlaps requirements.txt (Pillow, beautifulsoup4,
requests) and the comment in each file says versions must match — this test
makes that invariant checked instead of aspirational, and catches any
unpinned (non-==) requirement sneaking back in.
"""

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIREMENT_FILES = (
    'requirements.txt',
    'requirements-images.txt',
    'requirements-dev.txt',
)


def _parse(path: Path) -> dict:
    """Return {normalized_name: version} for every requirement line."""
    pins = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        match = re.fullmatch(r'([A-Za-z0-9_.-]+)(\[[^\]]+\])?==(\S+)', line)
        assert match, f'{path.name}: {line!r} is not an exact == pin'
        # PEP 503 normalization so Pillow / pillow compare equal
        name = re.sub(r'[-_.]+', '-', match.group(1)).lower()
        pins[name] = match.group(3)
    return pins


def test_all_requirements_are_exact_pins():
    for name in REQUIREMENT_FILES:
        pins = _parse(REPO_ROOT / name)
        assert pins, f'{name} parsed to nothing'


def test_overlapping_packages_pin_identical_versions():
    parsed = {name: _parse(REPO_ROOT / name) for name in REQUIREMENT_FILES}
    seen = {}
    for fname, pins in parsed.items():
        for pkg, version in pins.items():
            if pkg in seen:
                other_file, other_version = seen[pkg]
                assert version == other_version, (
                    f'{pkg} pinned to {version} in {fname} but '
                    f'{other_version} in {other_file}'
                )
            else:
                seen[pkg] = (fname, version)
