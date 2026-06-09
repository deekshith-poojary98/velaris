"""random capability stress test."""

from __future__ import annotations

from velaris_core.decorators import test

__test__ = False


@test("random")
def test_seeded_number(random) -> None:
    first = random.number(minimum=1, maximum=10)
    second = random.number(minimum=1, maximum=10)
    assert first == 2
    assert second == 1


@test("random")
def test_number_range(random) -> None:
    value = random.number(minimum=50, maximum=50)
    assert value == 50
