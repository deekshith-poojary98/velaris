"""End-to-end capability resolution flow (no pytest host)."""

from pathlib import Path

from velaris_core.config import load_config, require_binding
from velaris_core.bootstrap import register_builtin_providers
from velaris_core.registry import Registry
from velaris_core.resolver import Resolver


def test_full_resolution_flow(tmp_path: Path) -> None:
    config_file = tmp_path / "velaris.toml"
    config_file.write_text(
        """
[capabilities.secrets]
provider = "static"

[capabilities.secrets.options]
values = { PAYMENT_API_KEY = "key-123" }

[capabilities.target_environment]
provider = "static"

[capabilities.target_environment.options]
environment = "local-hermetic"
endpoints = { api = "https://api.local.test" }
""",
        encoding="utf-8",
    )

    config = load_config(config_file)
    registry = Registry()
    register_builtin_providers(registry)
    resolver = Resolver(registry, config.bindings)

    try:
        for capability_id in ("secrets", "target_environment"):
            require_binding(config, capability_id)
            resolver.resolve(capability_id)

        secrets = resolver.resolve("secrets")
        target = resolver.resolve("target_environment")

        assert secrets.get("PAYMENT_API_KEY") == "key-123"
        assert target.environment == "local-hermetic"
        assert target.endpoint("api") == "https://api.local.test"
    finally:
        resolver.teardown()

    scope2 = Resolver(registry, config.bindings)
    require_binding(config, "secrets")
    scope2.resolve("secrets")
    scope2.teardown()
