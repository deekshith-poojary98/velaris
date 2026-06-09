"""target_environment@0.1 capability contract."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from velaris_contracts._metadata import ContractMetadata

CAPABILITY_ID = "target_environment"
CONTRACT_VERSION = "0.1"

CONTRACT_METADATA: ContractMetadata = {
    "capability_id": CAPABILITY_ID,
    "version": CONTRACT_VERSION,
    "description": (
        "Named environment slice with string endpoint values "
        "(URLs, DSNs, hosts, or other connection targets)."
    ),
}


@runtime_checkable
class TargetEnvironment(Protocol):
    """Resolved environment slice and named endpoint values for integration tests."""

    @property
    def environment(self) -> str:
        """Environment name, e.g. ``local-hermetic`` or ``ci``."""
        ...

    def endpoint(self, name: str) -> str:
        """Return the endpoint value for ``name``.

        Values are opaque strings: URLs, DSNs, hostnames, etc.

        Raises:
            KeyError: if the endpoint is not defined for this environment.
        """
        ...
