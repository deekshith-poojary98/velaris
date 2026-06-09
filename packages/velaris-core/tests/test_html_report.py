"""Static HTML report tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from velaris_core.errors import VelarisError
from velaris_core.html_report import generate_report, render_html
from velaris_core.report_loader import build_run_report, load_jsonl

BROWSER_DIR = Path(__file__).resolve().parents[3] / "examples" / "browser"
AUTHORING_DIR = Path(__file__).resolve().parents[3] / "examples" / "authoring"


def _write_jsonl(path: Path, events: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(event, sort_keys=True) for event in events) + "\n",
        encoding="utf-8",
    )


def test_load_jsonl_rejects_missing_file(tmp_path: Path) -> None:
    with pytest.raises(VelarisError, match="not found"):
        load_jsonl(tmp_path / "missing.jsonl")


def test_load_jsonl_rejects_invalid_json(tmp_path: Path) -> None:
    bad = tmp_path / "bad.jsonl"
    bad.write_text("{ not json\n", encoding="utf-8")
    with pytest.raises(VelarisError, match="invalid JSON"):
        load_jsonl(bad)


def test_build_run_report_from_events() -> None:
    events = [
        {"type": "TestStarted", "test": "test_a", "name": "test_a"},
        {"type": "CapabilityResolved", "test": "test_a", "capability": "browser", "provider": "fake"},
        {"type": "CapabilityObserved", "test": "test_a", "capability": "browser", "action": "open", "data": {"path": "/"}},
        {"type": "TestPassed", "test": "test_a", "name": "test_a"},
        {"type": "CapabilityTeardown", "test": "test_a", "capability": "browser", "provider": "fake"},
        {"type": "TestStarted", "test": "test_b", "name": "test_b"},
        {"type": "TestFailed", "test": "test_b", "name": "test_b", "message": "boom", "error_type": "AssertionError"},
        {"type": "RunFinished", "test": None, "passed": 1, "failed": 1, "duration_seconds": 1.5},
    ]
    report = build_run_report(events)
    assert report.passed == 1
    assert report.failed == 1
    assert report.duration_seconds == 1.5
    assert len(report.tests) == 2
    assert report.tests[0].name == "test_a"
    assert report.tests[0].status == "passed"
    assert len(report.tests[0].timeline) == 3
    assert report.tests[1].status == "failed"
    assert report.tests[1].message == "boom"


def test_render_html_contains_summary_and_tests() -> None:
    events = [
        {"type": "TestStarted", "test": "test_login", "name": "test_login"},
        {"type": "CapabilityResolved", "test": "test_login", "capability": "browser", "provider": "fake"},
        {"type": "CapabilityObserved", "test": "test_login", "capability": "browser", "action": "open", "data": {"path": "/login"}},
        {"type": "TestPassed", "test": "test_login", "name": "test_login"},
        {"type": "RunFinished", "test": None, "passed": 1, "failed": 0, "duration_seconds": 0.01},
    ]
    html = render_html(build_run_report(events))
    assert "<!DOCTYPE html>" in html
    assert "Velaris Test Report" in html
    assert "Passed" in html
    assert "test_login" in html
    assert "browser.open" in html
    assert "Resolve browser" in html or "browser" in html


def test_generate_report_writes_file(tmp_path: Path) -> None:
    log = tmp_path / "run.jsonl"
    _write_jsonl(
        log,
        [
            {"type": "TestStarted", "test": "t", "name": "t"},
            {"type": "TestPassed", "test": "t", "name": "t"},
            {"type": "RunFinished", "test": None, "passed": 1, "failed": 0, "duration_seconds": 0.1},
        ],
    )
    out = generate_report(log, tmp_path / "report.html")
    assert out.is_file()
    content = out.read_text(encoding="utf-8")
    assert "Velaris Test Report" in content


def test_generate_report_from_browser_run(tmp_path: Path) -> None:
    """End-to-end: run tests with --json-log, then generate HTML."""
    import io
    from contextlib import redirect_stdout

    from velaris_core.runner import run

    log = tmp_path / "run.jsonl"
    with redirect_stdout(io.StringIO()):
        run(
            [BROWSER_DIR / "tests"],
            config_path=BROWSER_DIR / "velaris.fake.toml",
            json_log=log,
        )
    out = generate_report(log, tmp_path / "report.html")
    html = out.read_text(encoding="utf-8")
    assert "test_login" in html
    assert "browser.open" in html
    assert "Passed" in html


def test_generate_report_from_authoring_multi_test(tmp_path: Path) -> None:
    import io
    from contextlib import redirect_stdout

    from velaris_core.runner import run

    log = tmp_path / "authoring.jsonl"
    with redirect_stdout(io.StringIO()):
        run(
            [AUTHORING_DIR / "tests"],
            config_path=AUTHORING_DIR / "velaris.toml",
            json_log=log,
        )
    out = generate_report(log, tmp_path / "report.html")
    html = out.read_text(encoding="utf-8")
    assert "test_login" in html
    assert "User logs in" in html
