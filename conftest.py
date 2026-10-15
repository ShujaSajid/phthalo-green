"""Let ``pytest`` run from a clean checkout without installing the package."""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"

try:  # pragma: no cover - trivial import probe
    import phthalo_green  # noqa: F401
except ModuleNotFoundError:
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
