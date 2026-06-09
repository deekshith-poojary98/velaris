"""filesystem capability stress test."""

from __future__ import annotations

from velaris_core.decorators import test

__test__ = False


@test("filesystem")
def test_read_seeded_file(filesystem) -> None:
    assert filesystem.read_text("/data/input.txt") == "seed-content"


@test("filesystem")
def test_write_file(filesystem) -> None:
    filesystem.write_text("/data/output.txt", "written-by-test")
    assert filesystem.read_text("/data/output.txt") == "written-by-test"
