"""Test execution engine."""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

from velaris_core.bootstrap import register_builtin_providers
from velaris_core.collector import collect
from velaris_core.compose import apply_bootstrap_conventions
from velaris_core.config import load_config
from velaris_core.events import EventEnvelope, RunFinished, TestFailed, TestPassed, TestStarted
from velaris_core.json_reporter import JsonReporter
from velaris_core.registry import Registry
from velaris_core.reporting import Reporter, multiplex
from velaris_core.resolver import Resolver
from velaris_core.output_mode import OutputMode
from velaris_core.stdout_reporter import StdoutReporter


@dataclass
class RunResult:
    passed: int = 0
    failed: int = 0
    exit_code: int = 0
    duration_seconds: float = 0.0


def run(
    paths: list[str | Path],
    *,
    config_path: str | Path = "velaris.toml",
    reporters: list[Reporter] | None = None,
    json_log: str | Path | None = None,
    output_mode: OutputMode = OutputMode.DEFAULT,
    tags: list[str] | None = None,
) -> RunResult:
    started = time.monotonic()
    active_reporters: list[Reporter] = [StdoutReporter(mode=output_mode)]
    json_reporter: JsonReporter | None = None

    if json_log is not None:
        json_reporter = JsonReporter(path=json_log)
        active_reporters.append(json_reporter)
    if reporters:
        active_reporters.extend(reporters)

    emit = multiplex(active_reporters)

    def emit_for_test(test_name: str | None, event: object) -> None:
        emit(EventEnvelope(test=test_name, event=event))

    tests = collect(paths)
    if tags:
        tests = [t for t in tests if any(tag in t.tags for tag in tags)]

    config = load_config(config_path)
    bindings = apply_bootstrap_conventions(config.bindings)

    registry = Registry()
    register_builtin_providers(registry)

    result = RunResult()
    for spec in tests:
        emit_for_test(spec.name, TestStarted(spec.name, tags=list(spec.tags)))
        resolver = Resolver(
            registry,
            bindings,
            emit=lambda event: emit_for_test(spec.name, event),
        )
        try:
            kwargs = {cap: resolver.resolve(cap) for cap in spec.capabilities}
            spec.callable(**kwargs)
        except AssertionError as exc:
            result.failed += 1
            emit_for_test(
                spec.name,
                TestFailed(
                    spec.name,
                    str(exc) or "assertion failed",
                    error_type="AssertionError",
                ),
            )
        except Exception as exc:
            result.failed += 1
            emit_for_test(
                spec.name,
                TestFailed(spec.name, str(exc), error_type=type(exc).__name__),
            )
        else:
            result.passed += 1
            emit_for_test(spec.name, TestPassed(spec.name))
        finally:
            resolver.teardown()

    result.duration_seconds = time.monotonic() - started
    result.exit_code = 0 if result.failed == 0 else 1
    emit_for_test(
        None,
        RunFinished(
            passed=result.passed,
            failed=result.failed,
            duration_seconds=result.duration_seconds,
        ),
    )

    if json_reporter is not None:
        json_reporter.close()

    return result
