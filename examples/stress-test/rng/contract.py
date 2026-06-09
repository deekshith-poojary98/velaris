"""random@0.1 capability contract (external stress-test plugin)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

CAPABILITY_ID = "random"
CONTRACT_VERSION = "0.1"


@runtime_checkable
class Random(Protocol):
    """Minimal deterministic random source for architecture stress tests."""

    def number(self, *, minimum: int = 0, maximum: int = 100) -> int:
        """Return an integer in ``[minimum, maximum]``."""
        ...
