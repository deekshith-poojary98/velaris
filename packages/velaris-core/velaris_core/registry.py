"""Hardcoded capability provider registry."""

from __future__ import annotations

from velaris_core.errors import DuplicateProviderError, UnknownProviderError
from velaris_core.types import ProviderFactory


class Registry:
    """Maps ``(capability_id, provider)`` to a factory. No dynamic loading."""

    def __init__(self) -> None:
        self._factories: dict[tuple[str, str], ProviderFactory] = {}

    def register(
        self,
        capability_id: str | None = None,
        provider: str | None = None,
        factory: ProviderFactory | None = None,
        *,
        capability: str | None = None,
    ) -> None:
        cap = capability if capability is not None else capability_id
        if cap is None or provider is None or factory is None:
            raise TypeError("register() requires capability, provider, and factory")
        key = (cap, provider)
        if key in self._factories:
            raise DuplicateProviderError(
                f"Provider already registered: {cap}={provider!r}"
            )
        self._factories[key] = factory

    def get_factory(self, capability_id: str, provider: str) -> ProviderFactory:
        try:
            return self._factories[(capability_id, provider)]
        except KeyError as exc:
            available = ", ".join(self.list_providers(capability_id)) or "(none)"
            raise UnknownProviderError(
                f"Unknown provider {provider!r} for capability {capability_id!r}.\n"
                f"  Registered providers: {available}"
            ) from exc

    def list_providers(self, capability_id: str) -> list[str]:
        return sorted(name for cap, name in self._factories if cap == capability_id)
