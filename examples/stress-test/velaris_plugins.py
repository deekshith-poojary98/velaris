"""Manual plugin registration for architecture stress-test capabilities."""

from __future__ import annotations

from velaris_core.sdk import Registry

from database.provider import register_database_providers
from filesystem.provider import register_filesystem_providers
from rng.provider import register_random_providers


def register(registry: Registry) -> None:
    register_database_providers(registry)
    register_filesystem_providers(registry)
    register_random_providers(registry)
