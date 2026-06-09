"""Reference provider implementations."""

from __future__ import annotations

import os
from typing import Any

from velaris_contracts.secrets.v0_1 import Secrets
from velaris_contracts.target_environment.v0_1 import TargetEnvironment
from velaris_core.provider_context import pop_emit
from velaris_core.reporting import capability_observed
from velaris_core.types import Teardown


class EnvSecretsProvider:
    """Reference secrets provider backed by ``os.environ``."""

    def get(self, name: str) -> str:
        value = os.environ.get(name)
        if value is None:
            raise KeyError(name)
        return value


class StaticSecrets:
    def __init__(self, values: dict[str, str]) -> None:
        self._values = values

    def get(self, name: str) -> str:
        if name not in self._values:
            raise KeyError(name)
        return self._values[name]


class StaticTargetEnvironment:
    def __init__(self, environment: str, endpoints: dict[str, str]) -> None:
        self._environment = environment
        self._endpoints = endpoints

    @property
    def environment(self) -> str:
        return self._environment

    def endpoint(self, name: str) -> str:
        if name not in self._endpoints:
            raise KeyError(name)
        return self._endpoints[name]


def create_env_secrets(options: dict[str, Any]) -> tuple[Secrets, Teardown]:
    options, emit = pop_emit(options)
    required = options.get("required", [])
    if not isinstance(required, list):
        required = []
    missing = [name for name in required if name not in os.environ]
    if missing:
        raise KeyError(f"Missing required secrets in environment: {', '.join(missing)}")
    if emit is not None:
        emit(capability_observed("secrets", "resolved"))
    return EnvSecretsProvider(), lambda: None


def create_static_secrets(options: dict[str, Any]) -> tuple[Secrets, Teardown]:
    options, emit = pop_emit(options)
    raw = options.get("values", {})
    if not isinstance(raw, dict):
        raw = {}
    values = {str(k): str(v) for k, v in raw.items()}
    if emit is not None:
        emit(capability_observed("secrets", "resolved"))
    return StaticSecrets(values=values), lambda: None


def create_static_target_environment(
    options: dict[str, Any],
) -> tuple[TargetEnvironment, Teardown]:
    environment = str(options.get("environment", "default"))
    raw = options.get("endpoints", {})
    if not isinstance(raw, dict):
        raw = {}
    endpoints = {str(k): str(v) for k, v in raw.items()}
    return StaticTargetEnvironment(environment=environment, endpoints=endpoints), lambda: None
