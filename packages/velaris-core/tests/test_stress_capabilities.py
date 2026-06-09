"""Architecture stress-test integration tests."""

from __future__ import annotations

import ast
import io
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from velaris_core.output_mode import OutputMode
from velaris_core.runner import run

STRESS_DIR = Path(__file__).resolve().parents[3] / "examples" / "stress-test"
RUNNER_PATH = Path(__file__).resolve().parents[1] / "velaris_core" / "runner.py"
RESOLVER_PATH = Path(__file__).resolve().parents[1] / "velaris_core" / "resolver.py"
REPORTING_PATH = Path(__file__).resolve().parents[1] / "velaris_core" / "reporting.py"
TESTSPEC_PATH = Path(__file__).resolve().parents[1] / "velaris_core" / "testspec.py"


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    return modules


def test_core_modules_unchanged_for_stress_capabilities() -> None:
    for path in (RUNNER_PATH, RESOLVER_PATH, REPORTING_PATH, TESTSPEC_PATH):
        modules = _imported_modules(path)
        assert "database" not in modules
        assert "filesystem" not in modules
        assert "rng" not in modules


def test_stress_capabilities_run(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(STRESS_DIR)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run(
            [STRESS_DIR / "tests"],
            config_path=STRESS_DIR / "velaris.toml",
            output_mode=OutputMode.DEBUG,
        )
    output = buffer.getvalue()
    assert result.passed == 7
    assert result.failed == 0
    assert "RESOLVE database(memory)" in output
    assert "RESOLVE filesystem(memory)" in output
    assert "RESOLVE random(seeded)" in output
    assert "database.get_row" in output
    assert "filesystem.read_text" in output
    assert "random.number" in output
