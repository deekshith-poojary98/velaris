"""Tests for ``velaris init`` project scaffolding."""

from __future__ import annotations

import io
import re
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import pytest

from velaris_core.cli import main
from velaris_core.runner import run
from velaris_core.scaffold import (
    TEST_LOGIN,
    VELARIS_TOML,
    ScaffoldError,
    format_success_message,
    init_project,
)


def test_init_creates_project_structure(tmp_path: Path) -> None:
    project = tmp_path / "demo"
    created = init_project(str(project))

    assert created == project.resolve()
    assert (project / "velaris.toml").is_file()
    assert (project / "tests" / "test_login.py").is_file()
    assert (project / "README.md").is_file()


def test_init_fails_if_directory_exists(tmp_path: Path) -> None:
    project = tmp_path / "demo"
    project.mkdir()

    with pytest.raises(ScaffoldError, match="Directory already exists"):
        init_project(str(project))


def test_init_fails_if_project_name_empty() -> None:
    with pytest.raises(ScaffoldError, match="must not be empty"):
        init_project("")
    with pytest.raises(ScaffoldError, match="must not be empty"):
        init_project("   ")


def test_init_creates_nested_parent_directories(tmp_path: Path) -> None:
    project = tmp_path / "projects" / "demo"
    init_project(str(project))

    assert project.is_dir()
    assert (project / "velaris.toml").is_file()
    assert (project / "tests" / "test_login.py").is_file()


def test_generated_velaris_toml(tmp_path: Path) -> None:
    project = tmp_path / "demo"
    init_project(str(project))

    assert (project / "velaris.toml").read_text(encoding="utf-8") == VELARIS_TOML


def test_generated_test_contents(tmp_path: Path) -> None:
    project = tmp_path / "demo"
    init_project(str(project))

    assert (project / "tests" / "test_login.py").read_text(encoding="utf-8") == TEST_LOGIN


def test_generated_readme(tmp_path: Path) -> None:
    project = tmp_path / "demo"
    init_project(str(project))

    readme = (project / "README.md").read_text(encoding="utf-8")
    assert len(readme.splitlines()) < 100
    assert "# demo" in readme
    assert "velaris run" in readme
    assert "velaris run --html-report" in readme
    assert "github.com/deekshith-poojary98/velaris" in readme


def test_format_success_message() -> None:
    message = format_success_message("projects/demo")
    assert "Created project: demo" in message
    assert "cd projects/demo" in message
    assert "velaris run" in message


def test_cli_init_prints_next_steps(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    stdout = io.StringIO()
    stderr = io.StringIO()

    with redirect_stdout(stdout), redirect_stderr(stderr):
        code = main(["init", "demo"])

    assert code == 0
    assert stderr.getvalue() == ""
    output = stdout.getvalue()
    assert "Created project: demo" in output
    assert "cd demo" in output
    assert "velaris run" in output
    assert (tmp_path / "demo" / "velaris.toml").is_file()


def test_cli_init_fails_when_directory_exists(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "demo").mkdir()
    stderr = io.StringIO()

    with redirect_stderr(stderr):
        code = main(["init", "demo"])

    assert code == 1
    assert "Directory already exists" in stderr.getvalue()


def test_end_to_end_init_and_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    assert main(["init", "demo"]) == 0

    project = tmp_path / "demo"
    monkeypatch.chdir(project)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run(["tests"], config_path="velaris.toml")

    output = buffer.getvalue()
    assert result.passed == 1
    assert result.failed == 0
    assert re.search(r"✓ test_login|Passed: 1", output)
