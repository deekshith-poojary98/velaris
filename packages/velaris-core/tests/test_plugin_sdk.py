"""Plugin SDK and manual registration tests."""

from __future__ import annotations

import ast
import io
import textwrap
from contextlib import redirect_stdout
from pathlib import Path

import velaris_core.sdk as sdk
import pytest

from velaris_core.bootstrap import register_builtin_providers
from velaris_core.plugin_loader import register_manual_plugins
from velaris_core.registry import Registry
from velaris_core.output_mode import OutputMode
from velaris_core.runner import run

EXAMPLE_PLUGINS_DIR = Path(__file__).resolve().parents[3] / "examples" / "plugins"
RUNNER_PATH = Path(__file__).resolve().parents[1] / "velaris_core" / "runner.py"
RESOLVER_PATH = Path(__file__).resolve().parents[1] / "velaris_core" / "resolver.py"
REPORTING_PATH = Path(__file__).resolve().parents[1] / "velaris_core" / "reporting.py"


def test_sdk_public_surface() -> None:
    assert set(sdk.__all__) == {
        "EMIT_OPTION_KEY",
        "ProviderFactory",
        "Registry",
        "Teardown",
        "capability_observed",
        "pop_emit",
        "register_manual_plugins",
    }


def _imported_modules(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.add(alias.name)
    return modules


def test_runner_unchanged_for_plugins() -> None:
    modules = _imported_modules(RUNNER_PATH)
    assert "velaris_core.plugin_loader" not in modules
    assert "velaris_core.sdk" not in modules


def test_resolver_and_reporting_unchanged_for_plugins() -> None:
    for path in (RESOLVER_PATH, REPORTING_PATH):
        modules = _imported_modules(path)
        assert "velaris_core.plugin_loader" not in modules
        assert "velaris_core.sdk" not in modules


def test_register_manual_plugins_from_file(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "project"
    plugin_dir.mkdir()
    (plugin_dir / "velaris_plugins.py").write_text(
        textwrap.dedent(
            """
            from velaris_core.sdk import Registry

            def register(registry: Registry) -> None:
                registry.register("demo", "noop", lambda _opts: (object(), lambda: None))
            """
        ),
        encoding="utf-8",
    )

    registry = Registry()
    loaded = register_manual_plugins(registry, search_dirs=[plugin_dir])
    assert loaded is True
    assert registry.list_providers("demo") == ["noop"]


def test_register_builtin_providers_loads_no_plugins_without_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.chdir(tmp_path)
    registry = Registry()
    register_builtin_providers(registry)
    assert registry.list_providers("clock") == []


def test_clock_plugin_example_runs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(EXAMPLE_PLUGINS_DIR)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run(
            [EXAMPLE_PLUGINS_DIR / "tests" / "test_clock.py"],
            config_path=EXAMPLE_PLUGINS_DIR / "velaris.toml",
            output_mode=OutputMode.DEBUG,
        )
    output = buffer.getvalue()
    assert result.passed == 1
    assert result.failed == 0
    assert "RESOLVE clock(fixed)" in output
    assert "clock.now" in output
