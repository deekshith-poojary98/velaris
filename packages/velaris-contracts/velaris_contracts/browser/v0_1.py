"""browser@0.1 capability contract."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from velaris_contracts._metadata import ContractMetadata

CAPABILITY_ID = "browser"
CONTRACT_VERSION = "0.1"

CONTRACT_METADATA: ContractMetadata = {
    "capability_id": CAPABILITY_ID,
    "version": CONTRACT_VERSION,
    "description": "Minimal browser automation surface for integration tests.",
}


@runtime_checkable
class Browser(Protocol):
    """Minimal browser automation for integration tests."""

    def open(self, url: str) -> None:
        """Navigate to ``url``."""
        ...

    def click(self, selector: str) -> None:
        """Click the element identified by ``selector``."""
        ...

    def type(self, selector: str, text: str) -> None:
        """Type ``text`` into the element identified by ``selector``."""
        ...

    def close(self) -> None:
        """Close the browser session."""
        ...
