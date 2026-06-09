"""random capability providers (external stress-test plugin)."""

from __future__ import annotations

import random as random_module
from collections.abc import Callable
from typing import Any

from velaris_core.sdk import Registry, Teardown, capability_observed, pop_emit

from rng.contract import Random


class SeededRandom:
    """Deterministic ``random.Random`` wrapper."""

    def __init__(
        self,
        seed: int,
        emit: Callable[[object], None] | None = None,
    ) -> None:
        self._rng = random_module.Random(seed)
        self._emit = emit

    def number(self, *, minimum: int = 0, maximum: int = 100) -> int:
        value = self._rng.randint(minimum, maximum)
        if self._emit is not None:
            self._emit(
                capability_observed(
                    "random",
                    "number",
                    {"minimum": minimum, "maximum": maximum, "value": value},
                )
            )
        return value


def create_seeded_random(options: dict[str, Any]) -> tuple[Random, Teardown]:
    cleaned, emit = pop_emit(options)
    seed = int(cleaned.get("seed", 0))
    return SeededRandom(seed, emit=emit), lambda: None


def register_random_providers(registry: Registry) -> None:
    registry.register("random", "seeded", create_seeded_random)
