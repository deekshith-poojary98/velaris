"""Shared contract metadata shape (not a class hierarchy)."""

from __future__ import annotations

from typing import TypedDict


class ContractMetadata(TypedDict):
    capability_id: str
    version: str
    description: str
