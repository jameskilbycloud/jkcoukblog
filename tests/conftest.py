"""Make scripts/ importable from the tests (scripts are standalone modules,
not a package — each one assumes scripts/ is on sys.path, which is true when
they run as `python3 scripts/foo.py`)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))
