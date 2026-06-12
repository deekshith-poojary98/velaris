"""Load Velaris JSON-lines event logs into a report model."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from velaris_core.errors import VelarisError


@dataclass
class TimelineEvent:
    """One event in a test's capability timeline."""

    type: str
    label: str
    detail: str = ""


@dataclass
class TestReport:
    """Aggregated report for one test."""

    __test__ = False

    name: str
    status: str  # "passed" | "failed" | "unknown"
    message: str = ""
    error_type: str = ""
    timeline: list[TimelineEvent] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass
class RunReport:
    """Aggregated report for one test run."""

    passed: int = 0
    failed: int = 0
    duration_seconds: float = 0.0
    tests: list[TestReport] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.passed + self.failed


def load_jsonl(path: Path | str) -> list[dict[str, Any]]:
    """Read a JSON-lines event log produced by ``--json-log``."""
    file_path = Path(path)
    if not file_path.is_file():
        raise VelarisError(f"Event log not found: {file_path}")

    events: list[dict[str, Any]] = []
    for line_no, raw in enumerate(
        file_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        line = raw.strip()
        if not line:
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise VelarisError(
                f"{file_path}:{line_no}: invalid JSON — {exc.msg}"
            ) from exc
        if not isinstance(event, dict) or "type" not in event:
            raise VelarisError(
                f"{file_path}:{line_no}: event must be a JSON object with 'type'."
            )
        events.append(event)
    return events


def build_run_report(events: list[dict[str, Any]]) -> RunReport:
    """Transform raw JSON events into a :class:`RunReport`."""
    summary = RunReport()
    tests: dict[str, TestReport] = {}
    order: list[str] = []

    for event in events:
        event_type = event.get("type", "")
        test_name = event.get("test")

        if event_type == "RunFinished":
            summary.passed = int(event.get("passed", 0))
            summary.failed = int(event.get("failed", 0))
            summary.duration_seconds = float(event.get("duration_seconds", 0.0))
            continue

        if not test_name:
            continue

        if test_name not in tests:
            tests[test_name] = TestReport(name=test_name, status="unknown")
            order.append(test_name)

        report = tests[test_name]

        if event_type == "TestStarted":
            report.tags = list(event.get("tags", []))
            continue
        if event_type == "TestPassed":
            report.status = "passed"
            continue
        if event_type == "TestFailed":
            report.status = "failed"
            report.message = str(event.get("message", ""))
            report.error_type = str(event.get("error_type", ""))
            continue

        timeline_event = _to_timeline(event)
        if timeline_event is not None:
            report.timeline.append(timeline_event)

    summary.tests = [tests[name] for name in order]
    return summary


def _to_timeline(event: dict[str, Any]) -> TimelineEvent | None:
    event_type = event.get("type", "")

    if event_type == "CapabilityResolved":
        cap = event.get("capability", "?")
        provider = event.get("provider", "?")
        return TimelineEvent(
            type=event_type,
            label=f"Resolve {cap}",
            detail=f"provider: {provider}",
        )

    if event_type == "CapabilityTeardown":
        cap = event.get("capability", "?")
        provider = event.get("provider", "")
        detail = f"provider: {provider}" if provider else ""
        return TimelineEvent(type=event_type, label=f"Teardown {cap}", detail=detail)

    if event_type == "CapabilityObserved":
        cap = event.get("capability", "?")
        action = event.get("action", "?")
        data = event.get("data") or {}
        detail = _format_data(data)
        return TimelineEvent(
            type=event_type,
            label=f"{cap}.{action}",
            detail=detail,
        )

    return None


def _format_data(data: dict[str, Any]) -> str:
    if not data:
        return ""
    parts = [f"{key}={value!r}" for key, value in data.items()]
    return ", ".join(parts)
