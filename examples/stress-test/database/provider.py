"""database capability providers (external stress-test plugin)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from velaris_core.sdk import Registry, Teardown, capability_observed, pop_emit

from database.contract import Database


class MemoryDatabase:
    """In-memory tables keyed by primary key."""

    def __init__(
        self,
        seed: dict[str, dict[str, dict[str, str]]],
        emit: Callable[[object], None] | None = None,
    ) -> None:
        self._tables = {
            table: {key: dict(row) for key, row in rows.items()}
            for table, rows in seed.items()
        }
        self._emit = emit

    def get_row(self, table: str, key: str) -> dict[str, str] | None:
        row = self._tables.get(table, {}).get(key)
        if self._emit is not None:
            self._emit(
                capability_observed(
                    "database",
                    "get_row",
                    {"table": table, "key": key, "found": row is not None},
                )
            )
        if row is None:
            return None
        return dict(row)

    def insert_row(self, table: str, key: str, row: dict[str, str]) -> None:
        self._tables.setdefault(table, {})[key] = dict(row)
        if self._emit is not None:
            self._emit(
                capability_observed(
                    "database",
                    "insert_row",
                    {"table": table, "key": key, "columns": sorted(row)},
                )
            )


def create_memory_database(options: dict[str, Any]) -> tuple[Database, Teardown]:
    cleaned, emit = pop_emit(options)
    raw_seed = cleaned.get("seed", {})
    seed: dict[str, dict[str, dict[str, str]]] = {}
    if isinstance(raw_seed, dict):
        for table, rows in raw_seed.items():
            if not isinstance(rows, dict):
                continue
            seed[str(table)] = {
                str(key): {str(k): str(v) for k, v in row.items()}
                for key, row in rows.items()
                if isinstance(row, dict)
            }

    instance = MemoryDatabase(seed, emit=emit)

    def teardown() -> None:
        instance._tables.clear()

    return instance, teardown


def register_database_providers(registry: Registry) -> None:
    registry.register("database", "memory", create_memory_database)
