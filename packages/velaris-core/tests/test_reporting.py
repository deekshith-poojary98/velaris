"""Reporting and event bus tests."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest
import responses

from velaris_core.events import RunFinished
from velaris_core.json_reporter import JsonReporter
from velaris_core.reporting import multiplex, unwrap_envelope
from velaris_core.output_mode import OutputMode
from velaris_core.runner import run
from velaris_core.stdout_reporter import StdoutReporter

EXAMPLE_DIR = Path(__file__).resolve().parents[3] / "examples" / "minimal"


class CollectReporter:
    def __init__(self) -> None:
        self.events: list[object] = []

    def handle(self, event: object) -> None:
        self.events.append(event)


@responses.activate
def test_multiple_reporters_receive_same_events(tmp_path: Path) -> None:
    responses.add(responses.GET, "http://testserver/users", status=200)
    collector = CollectReporter()
    json_path = tmp_path / "events.jsonl"

    buffer = io.StringIO()
    stdout = StdoutReporter()
    original_handle = stdout.handle

    def tee_handle(event: object) -> None:
        with redirect_stdout(buffer):
            original_handle(event)

    stdout.handle = tee_handle  # type: ignore[method-assign]
    emit = multiplex([stdout, collector, JsonReporter(path=json_path)])

    from velaris_core.bootstrap import register_builtin_providers
    from velaris_core.collector import collect
    from velaris_core.compose import apply_bootstrap_conventions
    from velaris_core.config import load_config
    from velaris_core.events import EventEnvelope, TestStarted
    from velaris_core.registry import Registry
    from velaris_core.resolver import Resolver

    config = load_config(EXAMPLE_DIR / "velaris.toml")
    bindings = apply_bootstrap_conventions(config.bindings)
    registry = Registry()
    register_builtin_providers(registry)
    tests = collect([EXAMPLE_DIR / "tests" / "test_users.py"])

    test_name = tests[0].name
    emit(EventEnvelope(test=test_name, event=TestStarted(test_name)))
    resolver = Resolver(
        registry,
        bindings,
        emit=lambda event: emit(EventEnvelope(test=test_name, event=event)),
    )
    kwargs = {cap: resolver.resolve(cap) for cap in tests[0].capabilities}
    tests[0].callable(**kwargs)
    resolver.teardown()

    assert len(collector.events) >= 3
    lines = json_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 3
    first = json.loads(lines[0])
    assert first["type"] == "TestStarted"
    assert first["test"] == test_name


@responses.activate
def test_run_emits_session_summary(tmp_path: Path) -> None:
    responses.add(responses.GET, "http://testserver/users", status=200)
    json_path = tmp_path / "run.jsonl"

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run(
            [EXAMPLE_DIR / "tests" / "test_users.py"],
            config_path=EXAMPLE_DIR / "velaris.toml",
            json_log=json_path,
        )

    output = buffer.getvalue()
    assert result.passed == 1
    assert "Passed: 1" in output
    assert "Failed: 0" in output
    assert "Duration:" in output

    lines = json_path.read_text(encoding="utf-8").strip().splitlines()
    types = [json.loads(line)["type"] for line in lines]
    assert types[-1] == "RunFinished"
    summary = json.loads(lines[-1])
    assert summary["passed"] == 1
    assert summary["failed"] == 0


@responses.activate
def test_capability_events_in_output(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_TOKEN", "tok")
    responses.add(responses.GET, "http://testserver/orders", status=200)

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        run(
            [EXAMPLE_DIR / "tests" / "test_checkout.py"],
            config_path=EXAMPLE_DIR / "velaris.toml",
            output_mode=OutputMode.DEBUG,
        )

    output = buffer.getvalue()
    assert "secrets resolved" in output
    assert "api request started GET /orders" in output
    assert "api request completed GET /orders 200" in output


def test_custom_reporter_via_run_api(tmp_path: Path) -> None:
    collector = CollectReporter()
    run([EXAMPLE_DIR / "tests" / "test_missing_secret.py"], reporters=[collector])
    assert any(
        isinstance(unwrap_envelope(event)[1], RunFinished) for event in collector.events
    )
