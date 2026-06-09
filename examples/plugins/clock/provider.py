"""clock capability providers (external plugin)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from velaris_core.sdk import Registry, Teardown, capability_observed, pop_emit

from clock.contract import Clock

DEFAULT_FIXED_TIME = "2026-01-01T00:00:00Z"


class FixedClock:
    """Returns a configured fixed timestamp."""

    def __init__(
        self,
        fixed_time: str,
        emit: Callable[[object], None] | None = None,
    ) -> None:
        self._fixed_time = fixed_time
        self._emit = emit

    def now(self) -> str:
        if self._emit is not None:
            self._emit(capability_observed("clock", "now", {"value": self._fixed_time}))
        return self._fixed_time


def create_fixed_clock(options: dict[str, Any]) -> tuple[Clock, Teardown]:
    cleaned, emit = pop_emit(options)
    fixed_time = str(cleaned.get("fixed_time", DEFAULT_FIXED_TIME))

    def teardown() -> None:
        return None

    return FixedClock(fixed_time, emit=emit), teardown


def register_clock_providers(registry: Registry) -> None:
    registry.register("clock", "fixed", create_fixed_clock)
