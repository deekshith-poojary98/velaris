"""Manual plugin registration for the clock example."""

from __future__ import annotations

from velaris_core.sdk import Registry

from clock.provider import register_clock_providers


def register(registry: Registry) -> None:
    register_clock_providers(registry)
