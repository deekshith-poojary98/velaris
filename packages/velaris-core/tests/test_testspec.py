"""TestSpec IR tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from velaris_core.collector import collect, validate_testspecs
from velaris_core.errors import CollectionError
from velaris_core.testspec import TestSpec


def test_collect_returns_testspec() -> None:
    example = Path(__file__).resolve().parents[3] / "examples" / "minimal"
    specs = collect([example / "tests" / "test_users.py"])
    assert len(specs) == 1
    assert isinstance(specs[0], TestSpec)
    assert specs[0].name == "test_users"
    assert specs[0].capabilities == ["api"]
    assert callable(specs[0].callable)


def test_validate_duplicate_names() -> None:
    def fn() -> None:
        pass

    specs = [
        TestSpec("dup", ["api"], fn),
        TestSpec("dup", ["api"], fn),
    ]
    with pytest.raises(CollectionError, match="Duplicate test name"):
        validate_testspecs(specs)


def test_validate_empty_capabilities() -> None:
    def fn() -> None:
        pass

    with pytest.raises(CollectionError, match="declares no capabilities"):
        validate_testspecs([TestSpec("t", [], fn)])


def test_validate_callable_required() -> None:
    with pytest.raises(CollectionError, match="no callable target"):
        validate_testspecs([TestSpec("t", ["api"], "not-callable")])  # type: ignore[arg-type]


def test_python_to_testspec_flow(tmp_path: Path) -> None:
    module = tmp_path / "test_flow.py"
    module.write_text(
        """
from velaris_core.decorators import test as velaris_test

@velaris_test("api")
def test_flow(api):
    assert api is not None
""",
        encoding="utf-8",
    )
    specs = collect([module])
    assert specs[0].name == "test_flow"
    assert specs[0].capabilities == ["api"]
