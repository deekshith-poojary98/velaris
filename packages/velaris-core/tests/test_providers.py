"""Reference provider tests."""

import os

import pytest

from velaris_contracts.secrets.v0_1 import Secrets
from velaris_contracts.target_environment.v0_1 import TargetEnvironment
from velaris_core.providers import (
    create_env_secrets,
    create_static_secrets,
    create_static_target_environment,
)


def test_static_secrets() -> None:
    secrets, teardown = create_static_secrets({"values": {"K": "v"}})
    try:
        assert isinstance(secrets, Secrets)
        assert secrets.get("K") == "v"
    finally:
        teardown()


def test_env_secrets(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MY_TOKEN", "secret")
    secrets, teardown = create_env_secrets({"required": ["MY_TOKEN"]})
    try:
        assert secrets.get("MY_TOKEN") == "secret"
    finally:
        teardown()


def test_env_secrets_missing_required_raises() -> None:
    with pytest.raises(KeyError, match="Missing required secrets"):
        create_env_secrets({"required": ["NOT_SET"]})


def test_static_target_environment() -> None:
    target, teardown = create_static_target_environment(
        {
            "environment": "local-hermetic",
            "endpoints": {
                "api": "https://api.example.test",
                "database_dsn": "postgresql://localhost/db",
            },
        }
    )
    try:
        assert isinstance(target, TargetEnvironment)
        assert target.environment == "local-hermetic"
        assert target.endpoint("api").startswith("https://")
        assert target.endpoint("database_dsn").startswith("postgresql://")
    finally:
        teardown()
