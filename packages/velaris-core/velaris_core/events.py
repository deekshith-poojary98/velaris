"""Execution events."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EventEnvelope:
    """Correlates an event with the test that produced it."""

    test: str | None
    event: object


@dataclass(frozen=True)
class TestStarted:
    __test__ = False

    name: str


@dataclass(frozen=True)
class TestPassed:
    __test__ = False

    name: str


@dataclass(frozen=True)
class TestFailed:
    __test__ = False

    name: str
    message: str
    error_type: str = ""


@dataclass(frozen=True)
class CapabilityResolved:
    capability: str
    provider: str


@dataclass(frozen=True)
class CapabilityTeardown:
    capability: str
    provider: str


@dataclass(frozen=True)
class CapabilityObserved:
    """Capability-agnostic provider observation."""

    capability: str
    action: str
    data: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RunFinished:
    passed: int
    failed: int
    duration_seconds: float
