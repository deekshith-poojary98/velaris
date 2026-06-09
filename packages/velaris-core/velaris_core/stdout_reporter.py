"""Stdout event reporter with default, verbose, and debug output modes."""

from __future__ import annotations

import os
import sys

from velaris_core.events import (
    CapabilityObserved,
    CapabilityResolved,
    CapabilityTeardown,
    RunFinished,
    TestFailed,
    TestPassed,
    TestStarted,
)
from velaris_core.output_mode import OutputMode
from velaris_core.reporting import unwrap_envelope

_PASS = "\u2713"
_FAIL = "\u2717"
_GREEN = "\033[32m"
_RED = "\033[31m"
_RESET = "\033[0m"


def _use_color() -> bool:
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return sys.stdout.isatty()


def _green(text: str) -> str:
    if not _use_color():
        return text
    return f"{_GREEN}{text}{_RESET}"


def _red(text: str) -> str:
    if not _use_color():
        return text
    return f"{_RED}{text}{_RESET}"


class StdoutReporter:
    """Filter and format execution events for terminal output.

    The event bus still receives every event unchanged. This reporter decides
    what to show based on :class:`OutputMode`:

    * **default** — pass/fail lines and session summary only
    * **verbose** — lifecycle events (run, resolve, pass/fail, teardown)
    * **debug** — everything, including capability observations (legacy trace)
    """

    def __init__(self, mode: OutputMode = OutputMode.DEFAULT) -> None:
        self._mode = mode
        self._result_lines = 0

    def handle(self, event: object) -> None:
        _, inner = unwrap_envelope(event)
        if isinstance(inner, TestStarted):
            self._on_test_started(inner)
        elif isinstance(inner, CapabilityResolved):
            self._on_capability_resolved(inner)
        elif isinstance(inner, CapabilityObserved):
            self._on_capability_observed(inner)
        elif isinstance(inner, TestPassed):
            self._on_test_passed(inner)
        elif isinstance(inner, TestFailed):
            self._on_test_failed(inner)
        elif isinstance(inner, CapabilityTeardown):
            self._on_capability_teardown(inner)
        elif isinstance(inner, RunFinished):
            self._on_run_finished(inner)

    def _on_test_started(self, event: TestStarted) -> None:
        if self._mode in (OutputMode.VERBOSE, OutputMode.DEBUG):
            print(f"RUN {event.name}")

    def _on_capability_resolved(self, event: CapabilityResolved) -> None:
        if self._mode in (OutputMode.VERBOSE, OutputMode.DEBUG):
            print(f"RESOLVE {event.capability}({event.provider})")

    def _on_capability_observed(self, event: CapabilityObserved) -> None:
        if self._mode == OutputMode.DEBUG:
            self._print_capability_observed(event)

    def _on_test_passed(self, event: TestPassed) -> None:
        self._result_lines += 1
        if self._mode == OutputMode.DEFAULT:
            print(f"{_green(_PASS)} {event.name}")
        else:
            print(f"PASS {event.name}")

    def _on_test_failed(self, event: TestFailed) -> None:
        self._result_lines += 1
        if self._mode == OutputMode.DEFAULT:
            print(f"{_red(_FAIL)} {event.name}")
            print()
            if event.error_type:
                print(f"{event.error_type}:")
            if event.message:
                print(event.message)
            return
        print(f"FAIL {event.name}")
        if event.message:
            print(event.message)

    def _on_capability_teardown(self, event: CapabilityTeardown) -> None:
        if self._mode in (OutputMode.VERBOSE, OutputMode.DEBUG):
            print(f"TEARDOWN {event.capability}")

    def _on_run_finished(self, event: RunFinished) -> None:
        if self._mode == OutputMode.DEFAULT and self._result_lines:
            print()
        print(f"Passed: {event.passed}")
        print(f"Failed: {event.failed}")
        print(f"Duration: {event.duration_seconds:.2f}s")

    def _print_capability_observed(self, event: CapabilityObserved) -> None:
        data = event.data
        if event.action == "resolved":
            print(f"{event.capability} resolved")
            return
        if event.action == "request.started":
            print(
                f"{event.capability} request started "
                f"{data.get('method')} {data.get('path')}"
            )
            return
        if event.action == "request.completed":
            print(
                f"{event.capability} request completed "
                f"{data.get('method')} {data.get('path')} {data.get('status_code')}"
            )
            return
        if event.action == "open":
            print(f"{event.capability}.open {data.get('path')}")
            return
        if event.action == "type":
            text = data.get("text")
            if isinstance(text, str) and "|" in text:
                text = text.split("|", 1)[0]
            print(f"{event.capability}.type {data.get('path')} {text}")
            return
        if event.action == "click":
            print(f"{event.capability}.click {data.get('path')}")
            return
        if event.action == "close":
            print(f"{event.capability}.close")
            return
        print(f"{event.capability}.{event.action}")
