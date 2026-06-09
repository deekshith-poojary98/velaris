"""filesystem@0.1 capability contract (external stress-test plugin)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

CAPABILITY_ID = "filesystem"
CONTRACT_VERSION = "0.1"


@runtime_checkable
class Filesystem(Protocol):
    """Minimal file read/write surface for architecture stress tests."""

    def read_text(self, path: str) -> str:
        """Return file contents at ``path``."""
        ...

    def write_text(self, path: str, content: str) -> None:
        """Write ``content`` to ``path``."""
        ...
