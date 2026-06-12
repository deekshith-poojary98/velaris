"""Tests for ``velaris collect`` — discovery and introspection only.

Collection runs (Collect → TestSpec) and stops: no resolution, no providers,
no execution. These tests assert the user-facing view, both output modes, and
that collection validation still fails as it does for ``run``.
"""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path

import pytest

from velaris_core.cli import main
from velaris_core.discovery import CollectedTest, discover, format_tree, to_json
from velaris_core.errors import CollectionError

AUTHORING_DIR = Path(__file__).resolve().parents[3] / "examples" / "authoring"


def test_discover_reports_style_source_and_capabilities() -> None:
    tests = discover([AUTHORING_DIR / "tests"], base=AUTHORING_DIR)
    by_name = {t.name: t for t in tests}

    assert by_name["test_login"].authoring_style == "python"
    assert by_name["test_login"].source == "tests/test_login.py"
    assert by_name["test_login"].capabilities == ["browser"]

    assert by_name["test_login_yaml"].authoring_style == "yaml"
    assert by_name["test_login_yaml"].source == "tests/test_login.yaml"

    assert by_name["User logs in"].authoring_style == "bdd"
    assert by_name["User logs in"].source == "tests/login.feature"


def test_discover_does_not_expose_callable() -> None:
    tests = discover([AUTHORING_DIR / "tests"], base=AUTHORING_DIR)
    assert all(not hasattr(t, "callable") for t in tests)
    assert all(isinstance(t, CollectedTest) for t in tests)


def test_format_tree_matches_expected_shape() -> None:
    tests = [
        CollectedTest(
            name="test_login",
            authoring_style="python",
            source="tests/test_login.py",
            capabilities=["browser"],
        )
    ]
    output = format_tree(tests)
    assert output == (
        "Found 1 test\n"
        "\n"
        "test_login\n"
        "  source: tests/test_login.py\n"
        "  authoring_style: python\n"
        "  capabilities:\n"
        "    - browser"
    )


def test_format_tree_empty() -> None:
    assert format_tree([]) == "Found 0 tests"


def test_to_json_is_stable_array() -> None:
    tests = [
        CollectedTest(
            name="test_login",
            authoring_style="python",
            source="tests/test_login.py",
            capabilities=["browser"],
        )
    ]
    payload = json.loads(to_json(tests))
    assert payload == [
        {
            "name": "test_login",
            "authoring_style": "python",
            "source": "tests/test_login.py",
            "capabilities": ["browser"],
            "tags": [],
        }
    ]


def test_cli_collect_human_output(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(AUTHORING_DIR)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["collect", "tests/"])
    assert code == 0
    out = buffer.getvalue()
    assert "Found 5 tests" in out
    assert "authoring_style: bdd" in out


def test_cli_collect_json_output(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(AUTHORING_DIR)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["collect", "tests/", "--json"])
    assert code == 0
    payload = json.loads(buffer.getvalue())
    assert {t["authoring_style"] for t in payload} == {"python", "yaml", "bdd"}


def test_collect_still_fails_on_duplicate_names(tmp_path: Path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    body = (
        "from velaris_core.decorators import test\n\n"
        '@test("browser")\n'
        "def test_login(browser):\n"
        "    pass\n"
    )
    (tests_dir / "a.py").write_text(body)
    (tests_dir / "b.py").write_text(body)

    with pytest.raises(CollectionError, match="Duplicate test name"):
        discover([tests_dir])


def test_cli_collect_reports_collection_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    body = (
        "from velaris_core.decorators import test\n\n"
        '@test("browser")\n'
        "def test_login(browser):\n"
        "    pass\n"
    )
    (tests_dir / "a.py").write_text(body)
    (tests_dir / "b.py").write_text(body)
    monkeypatch.chdir(tmp_path)

    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(["collect", "tests/"])
    assert code == 1
    assert "CollectionError:" in err.getvalue()
    assert "Duplicate test name" in err.getvalue()
