"""Manual plugin registration for the authoring-style example."""

from __future__ import annotations

from velaris_core.sdk import Registry

from rng.provider import register_random_providers


def register(registry: Registry) -> None:
    register_random_providers(registry)
