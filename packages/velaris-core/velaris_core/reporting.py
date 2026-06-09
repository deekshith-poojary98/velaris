"""Reporter contract and event bus."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, is_dataclass
from typing import Any, Protocol, runtime_checkable

from velaris_core.events import CapabilityObserved, EventEnvelope

EMIT_OPTION_KEY = "_emit"


@runtime_checkable
class Reporter(Protocol):
    def handle(self, event: object) -> None:
        """Receive one execution event (typically an EventEnvelope)."""
        ...


def multiplex(reporters: Sequence[Reporter]) -> Callable[[object], None]:
    """Fan out each event to every reporter."""

    def emit(event: object) -> None:
        for reporter in reporters:
            reporter.handle(event)

    return emit


def unwrap_envelope(event: object) -> tuple[str | None, object]:
    if isinstance(event, EventEnvelope):
        return event.test, event.event
    return None, event


def event_to_dict(event: object) -> dict[str, Any]:
    test, inner = unwrap_envelope(event)
    payload = _inner_event_to_dict(inner)
    payload["test"] = test
    return payload


def _inner_event_to_dict(event: object) -> dict[str, Any]:
    if isinstance(event, CapabilityObserved):
        return {
            "type": "CapabilityObserved",
            "capability": event.capability,
            "action": event.action,
            "data": dict(event.data),
        }
    if is_dataclass(event):
        payload = asdict(event)
        payload["type"] = type(event).__name__
        return payload
    return {"type": type(event).__name__}


def capability_observed(
    capability: str,
    action: str,
    data: Mapping[str, Any] | None = None,
) -> CapabilityObserved:
    """Build a capability observation with optional payload."""
    return CapabilityObserved(
        capability=capability,
        action=action,
        data=dict(data or {}),
    )
