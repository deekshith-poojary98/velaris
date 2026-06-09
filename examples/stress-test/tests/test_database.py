"""database capability stress test."""

from __future__ import annotations

from velaris_core.decorators import test

__test__ = False


@test("database")
def test_read_seeded_row(database) -> None:
    row = database.get_row("users", "alice")
    assert row == {"name": "Alice", "role": "admin"}


@test("database")
def test_insert_row(database) -> None:
    database.insert_row("users", "carol", {"name": "Carol", "role": "guest"})
    row = database.get_row("users", "carol")
    assert row == {"name": "Carol", "role": "guest"}
