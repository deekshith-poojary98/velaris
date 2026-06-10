"""Shared contract metadata shape (not a class hierarchy)."""

from __future__ import annotations

from typing import TypedDict


class ContractMetadata(TypedDict):
    capability_id: str
    version: str
    description: str


# A published contract: its metadata plus the Protocol that defines its surface.
# ``object`` (rather than ``type[Protocol]``) keeps this dependency-light and
# avoids importing typing internals here.
CapabilityContract = tuple[ContractMetadata, object]
