"""Multi-capability stress test — independent capabilities in one test."""

from __future__ import annotations

from velaris_core.decorators import test

__test__ = False


@test("database", "filesystem", "random")
def test_independent_capabilities_composed(database, filesystem, random) -> None:
    user_id = str(random.number(minimum=1000, maximum=9999))
    database.insert_row("sessions", user_id, {"status": "active"})
    filesystem.write_text(f"/sessions/{user_id}.json", f'{{"id": "{user_id}"}}')

    row = database.get_row("sessions", user_id)
    payload = filesystem.read_text(f"/sessions/{user_id}.json")

    assert row == {"status": "active"}
    assert user_id in payload
