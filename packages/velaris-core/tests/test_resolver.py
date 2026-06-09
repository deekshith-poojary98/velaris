"""Resolver lifecycle tests."""

import pytest

from velaris_core.errors import CapabilitySetupError, ProviderNotConfiguredError
from velaris_core.bootstrap import register_builtin_providers
from velaris_core.registry import Registry
from velaris_core.resolver import Resolver
from velaris_core.types import CapabilityBinding


def _bindings(**sections: tuple[str, dict]) -> dict[str, CapabilityBinding]:
    return {
        capability_id: CapabilityBinding(
            capability_id=capability_id,
            provider=provider,
            options=options,
        )
        for capability_id, (provider, options) in sections.items()
    }


def test_resolve_and_teardown() -> None:
    registry = Registry()
    register_builtin_providers(registry)
    bindings = _bindings(
        secrets=("static", {"values": {"API_TOKEN": "abc"}}),
    )
    resolver = Resolver(registry, bindings)

    secrets = resolver.resolve("secrets")
    assert secrets.get("API_TOKEN") == "abc"

    resolver.teardown()

    with pytest.raises(ProviderNotConfiguredError):
        Resolver(registry, {}).resolve("secrets")


def test_resolve_is_cached_per_test_scope() -> None:
    registry = Registry()
    register_builtin_providers(registry)
    bindings = _bindings(secrets=("static", {"values": {"X": "1"}}))
    resolver = Resolver(registry, bindings)

    first = resolver.resolve("secrets")
    second = resolver.resolve("secrets")
    assert first is second
    assert first.get("X") == "1"


def test_setup_failure_raises_capability_setup_error() -> None:
    registry = Registry()
    register_builtin_providers(registry)
    bindings = _bindings(secrets=("env", {"required": ["MISSING_SECRET"]}))
    resolver = Resolver(registry, bindings)

    with pytest.raises(CapabilitySetupError, match="Setup failed"):
        resolver.resolve("secrets")

    resolver.teardown()
