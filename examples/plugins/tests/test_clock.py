"""Clock plugin demo — external capability, manual registration."""

from __future__ import annotations

from velaris_core.decorators import test

__test__ = False


@test("clock")
def test_fixed_time(clock) -> None:
    assert clock.now() == "2026-06-02T12:00:00Z"
