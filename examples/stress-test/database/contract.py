"""database@0.1 capability contract (external stress-test plugin)."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

CAPABILITY_ID = "database"
CONTRACT_VERSION = "0.1"


@runtime_checkable
class Database(Protocol):
    """Minimal row store for architecture stress tests."""

    def get_row(self, table: str, key: str) -> dict[str, str] | None:
        """Return one row from ``table`` keyed by ``key``, or ``None``."""
        ...

    def insert_row(self, table: str, key: str, row: dict[str, str]) -> None:
        """Insert or replace a row in ``table``."""
        ...
