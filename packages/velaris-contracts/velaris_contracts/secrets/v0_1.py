"""secrets@0.1 capability contract."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from velaris_contracts._metadata import ContractMetadata

CAPABILITY_ID = "secrets"
CONTRACT_VERSION = "0.1"

CONTRACT_METADATA: ContractMetadata = {
    "capability_id": CAPABILITY_ID,
    "version": CONTRACT_VERSION,
    "description": "Read-only access to named secret values for integration tests.",
}


@runtime_checkable
class Secrets(Protocol):
    """Read-only access to named secret values for integration tests."""

    def get(self, name: str) -> str:
        """Return the secret value for ``name``.

        Raises:
            KeyError: if the secret is not available.
        """
        ...
