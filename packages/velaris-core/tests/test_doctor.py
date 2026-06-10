"""Tests for ``velaris doctor`` — diagnostics only, never executes tests."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from velaris_core.cli import main
from velaris_core.doctor import format_report, run_diagnostics

AUTHORING_DIR = Path(__file__).resolve().parents[3] / "examples" / "authoring"


def _project(tmp_path: Path, config: str, test_body: str) -> Path:
    (tmp_path / "velaris.toml").write_text(config) if config is not None else None
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_a.py").write_text(test_body)
    return tmp_path


BROWSER_TEST = (
    "from velaris_core.decorators import test\n\n"
    '@test("browser")\n'
    "def test_a(browser):\n"
    "    pass\n"
)


def test_healthy_project_has_no_issues(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(AUTHORING_DIR)
    report = run_diagnostics(["tests"])
    assert report.errors == []
    assert report.exit_code == 0
    assert report.checks["tests_discovered"] == 5
    assert report.checks["plugins_loaded"] is True


def test_missing_config_is_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_a.py").write_text(BROWSER_TEST)
    monkeypatch.chdir(tmp_path)

    report = run_diagnostics(["tests"])
    assert report.checks["config"] is False
    assert any("not found" in e for e in report.errors)
    assert report.exit_code == 2


def test_no_tests_is_error(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    (tmp_path / "velaris.toml").write_text('[capabilities.browser]\nprovider = "fake"\n')
    monkeypatch.chdir(tmp_path)

    report = run_diagnostics(["tests"])
    assert any("No tests discovered" in e for e in report.errors)
    assert report.exit_code == 2


def test_unknown_provider_for_known_capability(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _project(tmp_path, '[capabilities.browser]\nprovider = "playwright"\n', BROWSER_TEST)
    monkeypatch.chdir(tmp_path)

    report = run_diagnostics(["tests"])
    assert any("playwright" in e for e in report.errors)
    assert report.exit_code == 2


def test_capability_configured_without_provider(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    body = (
        "from velaris_core.decorators import test\n\n"
        '@test("random")\n'
        "def test_a(random):\n"
        "    pass\n"
    )
    _project(tmp_path, '[capabilities.random]\nprovider = "seeded"\n', body)
    monkeypatch.chdir(tmp_path)

    report = run_diagnostics(["tests"])
    assert any("no provider registered" in e for e in report.errors)
    assert report.exit_code == 2


def test_warnings_only_exit_code_one(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _project(
        tmp_path,
        '[capabilities.target_environment]\nprovider = "static"\n',
        BROWSER_TEST,
    )
    monkeypatch.chdir(tmp_path)

    report = run_diagnostics(["tests"])
    assert report.errors == []
    assert any("not configured: browser" in w for w in report.warnings)
    assert any("not used: target_environment" in w for w in report.warnings)
    assert report.exit_code == 1


def test_cli_doctor_json_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(AUTHORING_DIR)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["doctor", "--json"])
    assert code == 0
    payload = json.loads(buffer.getvalue())
    assert set(payload) == {"errors", "warnings", "checks"}
    assert payload["checks"]["tests_discovered"] == 5


def test_cli_doctor_human(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(AUTHORING_DIR)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["doctor"])
    assert code == 0
    out = buffer.getvalue()
    assert "Velaris Environment Check" in out
    assert "No issues detected." in out


def test_format_report_renders_summary(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(tmp_path)
    report = run_diagnostics(["tests"])
    rendered = format_report(report)
    assert "Summary" in rendered
    assert "Errors:" in rendered
