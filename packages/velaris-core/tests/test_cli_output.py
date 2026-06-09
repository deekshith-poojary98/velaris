"""CLI output mode tests."""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from velaris_core.cli import main
from velaris_core.output_mode import OutputMode
from velaris_core.runner import run

STRESS_DIR = Path(__file__).resolve().parents[3] / "examples" / "stress-test"
BROWSER_DIR = Path(__file__).resolve().parents[3] / "examples" / "browser"


def test_default_output_is_result_focused(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(STRESS_DIR)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run([STRESS_DIR / "tests"], config_path=STRESS_DIR / "velaris.toml")

    output = buffer.getvalue()
    assert result.passed == 7
    assert "\u2713 test_independent_capabilities_composed" in output
    assert "\u2713 test_insert_row" in output
    assert "Passed: 7" in output
    assert "Failed: 0" in output
    assert "Duration:" in output
    assert "RUN " not in output
    assert "RESOLVE " not in output
    assert "TEARDOWN " not in output
    assert "database.insert_row" not in output


def test_verbose_output_shows_lifecycle_not_observations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(STRESS_DIR)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        run(
            [STRESS_DIR / "tests" / "test_database.py"],
            config_path=STRESS_DIR / "velaris.toml",
            output_mode=OutputMode.VERBOSE,
        )

    output = buffer.getvalue()
    assert "RUN test_insert_row" in output
    assert "RESOLVE database(memory)" in output
    assert "PASS test_insert_row" in output
    assert "TEARDOWN database" in output
    assert "database.insert_row" not in output
    assert "\u2713" not in output


def test_debug_output_shows_capability_observations(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(STRESS_DIR)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        run(
            [STRESS_DIR / "tests" / "test_database.py"],
            config_path=STRESS_DIR / "velaris.toml",
            output_mode=OutputMode.DEBUG,
        )

    output = buffer.getvalue()
    assert "RUN test_insert_row" in output
    assert "RESOLVE database(memory)" in output
    assert "database.insert_row" in output
    assert "database.get_row" in output
    assert "PASS test_insert_row" in output
    assert "TEARDOWN database" in output


def test_default_failure_output_is_scannable(tmp_path: Path) -> None:
    failing = tmp_path / "test_fail.py"
    failing.write_text(
        "from velaris_core.decorators import test\n\n"
        "@test('browser')\n"
        "def test_login(browser):\n"
        "    assert False, 'Expected 2 rows\\nActual: 1'\n",
        encoding="utf-8",
    )
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run(
            [failing],
            config_path=BROWSER_DIR / "velaris.fake.toml",
        )
    output = buffer.getvalue()
    assert result.failed == 1
    assert "\u2717 test_login" in output
    assert "AssertionError:" in output
    assert "Expected 2 rows" in output
    assert "Actual: 1" in output
    assert "RUN " not in output


def test_cli_debug_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(STRESS_DIR)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(
            [
                "run",
                str(STRESS_DIR / "tests" / "test_database.py"),
                "--config",
                str(STRESS_DIR / "velaris.toml"),
                "--debug",
            ]
        )
    assert code == 0
    assert "database.insert_row" in buffer.getvalue()


def test_cli_verbose_flag() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(
            [
                "run",
                str(BROWSER_DIR / "tests"),
                "--config",
                str(BROWSER_DIR / "velaris.fake.toml"),
                "--verbose",
            ]
        )
    assert code == 0
    output = buffer.getvalue()
    assert "RUN test_login" in output
    assert "browser.open" not in output


def test_cli_html_report_flag(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.chdir(BROWSER_DIR)
    html_path = tmp_path / "out.html"
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(
            [
                "run",
                "tests/",
                "--config",
                "velaris.fake.toml",
                "--html-report",
                str(html_path),
            ]
        )
    assert code == 0
    assert html_path.is_file()
    assert "Report written to" in buffer.getvalue()
    assert (tmp_path / "out.jsonl").is_file()
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(
            [
                "run",
                str(BROWSER_DIR / "tests"),
                "--config",
                str(BROWSER_DIR / "velaris.fake.toml"),
                "--verbose",
                "--debug",
            ]
        )
    assert code == 0
    assert "browser.open /login" in buffer.getvalue()
