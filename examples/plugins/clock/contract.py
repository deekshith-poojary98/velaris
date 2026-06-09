"""clock@0.1 capability contract (external plugin — not part of velaris-contracts)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

CAPABILITY_ID = "clock"
CONTRACT_VERSION = "0.1"


@runtime_checkable
class Clock(Protocol):
    """Minimal time source for extension demos."""

    def now(self) -> str:
        """Return the current instant as an ISO-8601 string."""
        ...
