"""Core types for capability resolution."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypeAlias

from velaris_core.errors import ConfigError

Teardown: TypeAlias = Callable[[], None]
ProviderFactory: TypeAlias = Callable[[dict[str, Any]], tuple[Any, Teardown]]


@dataclass(frozen=True)
class CapabilityBinding:
    """Resolved provider binding for one capability."""

    capability_id: str
    provider: str
    options: dict[str, Any]


@dataclass(frozen=True)
class VelarisConfig:
    """Resolved Velaris configuration for a test session."""

    config_path: str | None
    bindings: dict[str, CapabilityBinding]

    def binding(self, capability_id: str) -> CapabilityBinding:
        try:
            return self.bindings[capability_id]
        except KeyError as exc:
            raise ConfigError(
                f"No configuration for capability {capability_id!r}."
            ) from exc
