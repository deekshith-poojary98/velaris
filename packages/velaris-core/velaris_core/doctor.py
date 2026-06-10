"""Environment diagnostics for ``velaris doctor``.

Validates a local Velaris setup and explains common problems *before* execution.
It runs no tests, resolves no capabilities, and instantiates no providers. Every
check reuses the same infrastructure a real run uses — ``load_config``,
``register_builtin_providers`` (the real plugin path), and ``discover`` — so the
diagnosis can never disagree with what ``velaris run`` would do.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from velaris_core.bootstrap import register_builtin_providers
from velaris_core.config import load_config
from velaris_core.discovery import discover
from velaris_core.errors import CollectionError, ConfigError, UnknownProviderError
from velaris_core.registry import Registry

OK = "✓"
WARN = "⚠"
ERROR = "✗"


@dataclass
class Line:
    """One rendered diagnostic line with an optional indented detail block."""

    symbol: str
    text: str
    detail_label: str | None = None
    detail_lines: list[str] = field(default_factory=list)


@dataclass
class DoctorReport:
    """Accumulated diagnostics: render lines plus machine-readable summary."""

    lines: list[Line] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks: dict[str, object] = field(default_factory=dict)
    usage: dict[str, int] = field(default_factory=dict)

    def ok(self, text: str) -> None:
        self.lines.append(Line(OK, text))

    def warn(self, text: str, detail: list[str] | None = None) -> None:
        self.warnings.append(text)
        self.lines.append(Line(WARN, text, detail_lines=detail or []))

    def error(self, text: str, suggestion: list[str] | None = None) -> None:
        self.errors.append(text)
        self.lines.append(
            Line(ERROR, text, detail_label="Suggestion", detail_lines=suggestion or [])
        )

    @property
    def exit_code(self) -> int:
        if self.errors:
            return 2
        if self.warnings:
            return 1
        return 0


def run_diagnostics(
    paths: list[str] | None = None,
    *,
    config_path: str = "velaris.toml",
) -> DoctorReport:
    """Run all checks and return a :class:`DoctorReport` (no side effects on tests)."""
    report = DoctorReport()
    paths = paths or ["tests"]

    _check_python(report)
    config = _check_config(report, config_path)
    discovered = _check_collection(report, paths)
    registry = _check_plugins(report)
    _check_capability_config(report, config, registry)
    _audit_usage(report, config, discovered)

    return report


def _check_python(report: DoctorReport) -> None:
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    report.checks["python"] = version
    if sys.version_info >= (3, 10):
        report.ok(f"Python {version}")
    else:
        report.error(
            f"Python {version} (Velaris requires 3.10+)",
            ["Install Python 3.10 or newer"],
        )


def _check_config(report: DoctorReport, config_path: str):
    path = Path(config_path)
    found = path.is_file()
    report.checks["config"] = found
    if not found:
        report.error(f"{config_path} not found", ["velaris init demo"])
        return None

    report.ok(f"{path.name} found")
    try:
        return load_config(config_path)
    except UnknownProviderError as exc:
        report.error(_first_line(exc), ["Run:", "    velaris capabilities"])
    except ConfigError as exc:
        report.error(f"Invalid configuration: {_first_line(exc)}", ["Check velaris.toml"])
    return None


def _check_collection(report: DoctorReport, paths: list[str]):
    tests_dir = Path(paths[0])
    if tests_dir.is_dir():
        report.ok("tests directory found")

    try:
        discovered = discover(paths)
    except CollectionError as exc:
        message = str(exc)
        if "Path not found" in message:
            report.checks["tests_discovered"] = 0
            report.error(
                "No tests discovered",
                ["Create tests/ directory", "or run:", "    velaris collect"],
            )
        else:
            report.checks["tests_discovered"] = None
            report.error(f"Collection failed: {message}", ["Run:", "    velaris collect"])
        return None

    count = len(discovered)
    report.checks["tests_discovered"] = count
    if count:
        report.ok(f"{count} {'test' if count == 1 else 'tests'} discovered")
    else:
        report.error(
            "No tests discovered",
            ["Create tests/ directory", "or run:", "    velaris collect"],
        )
    return discovered


def _check_plugins(report: DoctorReport) -> Registry:
    registry = Registry()
    try:
        register_builtin_providers(registry)
        report.checks["plugins_loaded"] = True
    except Exception as exc:  # plugin import/registration failure
        report.checks["plugins_loaded"] = False
        report.lines.append(
            Line(
                ERROR,
                "Failed to load velaris_plugins.py",
                detail_label="Reason",
                detail_lines=[f"{type(exc).__name__}: {exc}"],
            )
        )
        report.errors.append("Failed to load velaris_plugins.py")
    return registry


def _check_capability_config(report: DoctorReport, config, registry: Registry) -> None:
    if config is None:
        return
    for capability_id in sorted(config.bindings):
        binding = config.bindings[capability_id]
        report.ok(f"{capability_id} capability configured")

        providers = registry.list_providers(capability_id)
        if binding.provider in providers:
            report.ok(f"{binding.provider} provider available")
        elif providers:
            report.error(
                f"Provider {binding.provider!r} is not registered "
                f"for capability {capability_id!r}",
                ["Run:", "    velaris capabilities"],
            )
        else:
            report.error(
                f"Capability {capability_id!r} configured but no provider registered",
                ["Verify velaris_plugins.py", "and run from the project root"],
            )


def _audit_usage(report: DoctorReport, config, discovered) -> None:
    if not discovered:
        return

    counts: Counter[str] = Counter()
    for test in discovered:
        for capability in test.capabilities:
            counts[capability] += 1
    report.usage = dict(counts)

    if config is None:
        return

    configured = set(config.bindings)
    used = set(counts)

    for capability in sorted(used - configured):
        report.warn(
            f"Capability used by tests but not configured: {capability}",
            detail=[capability],
        )
    for capability in sorted(configured - used):
        report.warn(
            f"Capability configured but not used: {capability}",
            detail=[capability],
        )


def _first_line(exc: Exception) -> str:
    return str(exc).splitlines()[0] if str(exc) else type(exc).__name__


def format_report(report: DoctorReport) -> str:
    """Render the human-readable diagnostics report."""
    blocks: list[str] = ["Velaris Environment Check", ""]

    for line in report.lines:
        blocks.append(f"{line.symbol} {line.text}")
        if line.detail_lines:
            if line.detail_label:
                blocks.append("")
                blocks.append(f"{line.detail_label}:")
            blocks.extend(f"    {item}" for item in line.detail_lines)
            blocks.append("")

    if report.usage:
        blocks.append("")
        blocks.append("Capabilities used by tests")
        blocks.append("")
        width = max(len(name) for name in report.usage)
        for name in sorted(report.usage, key=lambda n: (-report.usage[n], n)):
            count = report.usage[name]
            dots = "." * max(3, (width + 6) - len(name))
            label = "test" if count == 1 else "tests"
            blocks.append(f"{name} {dots} {count} {label}")

    blocks.append("")
    if not report.errors and not report.warnings:
        blocks.append("No issues detected.")
    else:
        blocks.append("Summary")
        blocks.append("")
        blocks.append(f"Errors: {len(report.errors)}")
        blocks.append(f"Warnings: {len(report.warnings)}")

    return "\n".join(blocks)


def report_to_json(report: DoctorReport) -> str:
    """Render diagnostics as the documented JSON object."""
    payload = {
        "errors": report.errors,
        "warnings": report.warnings,
        "checks": report.checks,
    }
    return json.dumps(payload, indent=2)
