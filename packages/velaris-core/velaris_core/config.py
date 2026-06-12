"""Configuration loading."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Mapping

from velaris_core.errors import ConfigError, UnknownProviderError
from velaris_core.types import CapabilityBinding, VelarisConfig

KNOWN_PROVIDERS: dict[str, frozenset[str]] = {
    "api": frozenset({"requests"}),
    "browser": frozenset({"fake", "verbose"}),
    "secrets": frozenset({"env", "static"}),
    "target_environment": frozenset({"static"}),
}

ENV_PROVIDER_PREFIX = "VELARIS__CAPABILITIES__"


def load_config(
    path: str | Path = "velaris.toml",
    *,
    capability_overrides: Mapping[str, str] | None = None,
) -> VelarisConfig:
    """Load capability bindings from TOML."""
    config_path = Path(path)
    raw = _read_toml(config_path) if config_path.is_file() else {}
    capabilities = raw.get("capabilities", {})
    if capabilities is None:
        capabilities = {}
    if not isinstance(capabilities, dict):
        raise ConfigError("[capabilities] must be a table.")

    bindings: dict[str, CapabilityBinding] = {}
    for capability_id, section in capabilities.items():
        if not isinstance(section, dict):
            raise ConfigError(f"[capabilities.{capability_id}] must be a table.")
        provider = _provider_from_section(str(capability_id), section)
        options = _options_from_section(str(capability_id), section.get("options", {}))
        provider = _apply_overrides(str(capability_id), provider, capability_overrides)
        if provider:
            _validate_provider(str(capability_id), provider)
            bindings[str(capability_id)] = CapabilityBinding(
                capability_id=str(capability_id),
                provider=provider,
                options=options,
            )

    for capability_id, known in KNOWN_PROVIDERS.items():
        if capability_id in bindings:
            continue
        env_provider = os.environ.get(
            f"{ENV_PROVIDER_PREFIX}{capability_id.upper()}__PROVIDER"
        )
        if env_provider:
            provider = env_provider.strip()
            _validate_provider(capability_id, provider)
            bindings[capability_id] = CapabilityBinding(
                capability_id=capability_id,
                provider=provider,
                options={},
            )

    return VelarisConfig(
        config_path=str(config_path) if config_path.is_file() else None,
        bindings=bindings,
    )


def require_binding(config: VelarisConfig, capability_id: str) -> CapabilityBinding:
    from velaris_core.errors import ProviderNotConfiguredError

    try:
        return config.bindings[capability_id]
    except KeyError as exc:
        known = ", ".join(sorted(KNOWN_PROVIDERS.get(capability_id, ())))
        raise ProviderNotConfiguredError(
            f"No provider bound for capability {capability_id!r}.\n"
            f"  Known providers: {known}\n"
            f"  Fix: set [capabilities.{capability_id}] provider in velaris.toml"
        ) from exc


def _provider_from_section(capability_id: str, section: dict[str, Any]) -> str | None:
    provider = section.get("provider")
    if provider is None:
        return None
    if not isinstance(provider, str) or not provider.strip():
        raise ConfigError(f"[capabilities.{capability_id}] provider must be a string.")
    return provider.strip()


def _options_from_section(capability_id: str, raw: Any) -> dict[str, Any]:
    if raw is None:
        return {}
    if not isinstance(raw, dict):
        raise ConfigError(f"[capabilities.{capability_id}.options] must be a table.")
    return dict(raw)


def _apply_overrides(
    capability_id: str,
    provider: str | None,
    overrides: Mapping[str, str] | None,
) -> str | None:
    if overrides and capability_id in overrides:
        return overrides[capability_id].strip()
    return provider


def _validate_provider(capability_id: str, provider: str) -> None:
    known = KNOWN_PROVIDERS.get(capability_id)
    if known is None:
        return
    if provider in known:
        return

    try:
        from velaris_core.bootstrap import register_builtin_providers
        from velaris_core.registry import Registry

        registry = Registry()
        register_builtin_providers(registry)
        providers = registry.list_providers(capability_id)
        if provider in providers:
            return
    except Exception:
        pass

    available = ", ".join(sorted(known)) or "(none)"
    raise UnknownProviderError(
        f"Unknown provider {provider!r} for capability {capability_id!r}.\n"
        f"  Known providers: {available}"
    )


def _read_toml(path: Path) -> dict[str, Any]:
    if sys.version_info >= (3, 11):
        import tomllib

        with path.open("rb") as handle:
            data = tomllib.load(handle)
    else:
        import tomli

        with path.open("rb") as handle:
            data = tomli.load(handle)
    if not isinstance(data, dict):
        raise ConfigError(f"Config file {path} must contain a TOML table at the root.")
    return data
