"""Python authoring style — same capability, executable body."""

from __future__ import annotations

from velaris_core.decorators import test

__test__ = False


@test("random")
def test_dice_roll(random) -> None:
    value = random.number(minimum=1, maximum=6)
    assert 1 <= value <= 6
