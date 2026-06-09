"""Central provider registration for Velaris."""

from __future__ import annotations

from velaris_core.providers import (
    create_env_secrets,
    create_static_secrets,
    create_static_target_environment,
)
from velaris_core.providers_api import create_requests_api
from velaris_core.providers_browser import create_fake_browser, create_verbose_browser
from velaris_core.plugin_loader import register_manual_plugins
from velaris_core.registry import Registry


def register_builtin_providers(registry: Registry) -> None:
    """Register built-in providers and any manual plugins.

    Built-in providers are registered here. External capabilities register
    through ``velaris_plugins.py`` in the project directory (see ``velaris_core.sdk``).
    The runner creates a registry and calls this function — nothing else.
    """
    registry.register("api", "requests", create_requests_api)
    registry.register("secrets", "env", create_env_secrets)
    registry.register("secrets", "static", create_static_secrets)
    registry.register("target_environment", "static", create_static_target_environment)
    registry.register("browser", "fake", create_fake_browser)
    registry.register("browser", "verbose", create_verbose_browser)
    register_manual_plugins(registry)
