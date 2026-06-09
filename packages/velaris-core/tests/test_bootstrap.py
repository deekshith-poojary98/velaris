"""Bootstrap and provider registration tests."""

from __future__ import annotations

import ast
import io
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from velaris_core.bootstrap import register_builtin_providers
from velaris_core.registry import Registry
from velaris_core.output_mode import OutputMode
from velaris_core.runner import run

EXAMPLE_DIR = Path(__file__).resolve().parents[3] / "examples" / "minimal"
RUNNER_PATH = Path(__file__).resolve().parents[1] / "velaris_core" / "runner.py"


def test_runner_does_not_import_providers() -> None:
    tree = ast.parse(RUNNER_PATH.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    assert "velaris_core.providers" not in imported_modules
    assert "velaris_core.providers_api" not in imported_modules
    assert "velaris_core.bootstrap" in imported_modules


def test_bootstrap_registers_all_builtin_providers() -> None:
    registry = Registry()
    register_builtin_providers(registry)
    assert registry.list_providers("api") == ["requests"]
    assert registry.list_providers("browser") == ["fake", "verbose"]
    assert registry.list_providers("secrets") == ["env", "static"]
    assert registry.list_providers("target_environment") == ["static"]


def test_secrets_provider_swap_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_TOKEN", "swap-demo-token")
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run(
            [EXAMPLE_DIR / "tests" / "test_token.py"],
            config_path=EXAMPLE_DIR / "velaris.env-secrets.toml",
            output_mode=OutputMode.DEBUG,
        )
    assert result.passed == 1
    assert "RESOLVE secrets(env)" in buffer.getvalue()


def test_secrets_provider_swap_static() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run(
            [EXAMPLE_DIR / "tests" / "test_token.py"],
            config_path=EXAMPLE_DIR / "velaris.static-secrets.toml",
            output_mode=OutputMode.DEBUG,
        )
    assert result.passed == 1
    assert "RESOLVE secrets(static)" in buffer.getvalue()
