"""Configuration loading tests."""

from pathlib import Path

import pytest

from velaris_core.config import load_config, require_binding
from velaris_core.errors import ProviderNotConfiguredError, UnknownProviderError


def test_load_secrets_and_target_environment(tmp_path: Path) -> None:
    config_file = tmp_path / "velaris.toml"
    config_file.write_text(
        """
[capabilities.secrets]
provider = "static"

[capabilities.secrets.options]
values = { API_TOKEN = "from-config" }

[capabilities.target_environment]
provider = "static"

[capabilities.target_environment.options]
environment = "ci"
endpoints = { api = "https://api.ci.example.test" }
""",
        encoding="utf-8",
    )

    config = load_config(config_file)
    secrets = config.binding("secrets")
    assert secrets.provider == "static"
    assert secrets.options["values"]["API_TOKEN"] == "from-config"

    env = config.binding("target_environment")
    assert env.options["environment"] == "ci"


def test_unknown_provider_raises(tmp_path: Path) -> None:
    config_file = tmp_path / "velaris.toml"
    config_file.write_text(
        """
[capabilities.secrets]
provider = "vault"
""",
        encoding="utf-8",
    )
    with pytest.raises(UnknownProviderError, match="vault"):
        load_config(config_file)


def test_require_binding_missing_raises(tmp_path: Path) -> None:
    config_file = tmp_path / "velaris.toml"
    config_file.write_text("", encoding="utf-8")
    config = load_config(config_file)
    with pytest.raises(ProviderNotConfiguredError, match="secrets"):
        require_binding(config, "secrets")


def test_cli_override(tmp_path: Path) -> None:
    config_file = tmp_path / "velaris.toml"
    config_file.write_text(
        """
[capabilities.secrets]
provider = "static"
""",
        encoding="utf-8",
    )
    config = load_config(config_file, capability_overrides={"secrets": "env"})
    assert config.binding("secrets").provider == "env"
