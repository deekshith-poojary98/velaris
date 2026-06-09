"""Capability resolution for one test."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from velaris_core.errors import CapabilitySetupError, ProviderNotConfiguredError
from velaris_core.registry import Registry
from velaris_core.reporting import EMIT_OPTION_KEY
from velaris_core.types import CapabilityBinding, Teardown


class Resolver:
    """Resolve capabilities for a single test scope."""

    def __init__(
        self,
        registry: Registry,
        bindings: dict[str, CapabilityBinding],
        emit: Callable[[object], None] | None = None,
    ) -> None:
        self._registry = registry
        self._bindings = bindings
        self._emit = emit or (lambda _event: None)
        self._instances: dict[str, Any] = {}
        self._teardowns: list[tuple[str, str, Teardown]] = []

    def resolve(self, capability_id: str) -> Any:
        if capability_id in self._instances:
            return self._instances[capability_id]
        try:
            binding = self._bindings[capability_id]
        except KeyError as exc:
            raise ProviderNotConfiguredError(
                f"No provider bound for capability {capability_id!r}."
            ) from exc
        factory = self._registry.get_factory(capability_id, binding.provider)
        factory_options = {**binding.options, EMIT_OPTION_KEY: self._emit}
        try:
            instance, teardown = factory(factory_options)
        except Exception as exc:
            raise CapabilitySetupError(
                f"Setup failed for {capability_id}={binding.provider!r}: {exc}"
            ) from exc
        self._instances[capability_id] = instance
        self._teardowns.append((capability_id, binding.provider, teardown))
        from velaris_core.events import CapabilityResolved

        self._emit(CapabilityResolved(capability_id, binding.provider))
        return instance

    def teardown(self) -> None:
        from velaris_core.events import CapabilityTeardown

        while self._teardowns:
            capability_id, provider, fn = self._teardowns.pop()
            try:
                fn()
            except Exception:
                pass
            self._emit(CapabilityTeardown(capability_id, provider))
        self._instances.clear()
