"""Authoring adapter tests — multiple frontends, one execution engine."""

from __future__ import annotations

import ast
import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from velaris_core.adapters import PythonAdapter, YamlAdapter, default_adapters
from velaris_core.adapters.base import AuthoringAdapter
from velaris_core.collector import collect
from velaris_core.errors import CollectionError
from velaris_core.output_mode import OutputMode
from velaris_core.runner import run
from velaris_core.testspec import TestSpec, noop_test

RUNNER_PATH = Path(__file__).resolve().parents[1] / "velaris_core" / "runner.py"


def test_default_adapters_satisfy_protocol() -> None:
    adapters = default_adapters()
    assert all(isinstance(a, AuthoringAdapter) for a in adapters)
    assert [type(a).__name__ for a in adapters] == [
        "PythonAdapter",
        "YamlAdapter",
        "BddAdapter",
    ]


def test_runner_is_authoring_agnostic() -> None:
    """The runner must not import any adapter or authoring-style module."""
    tree = ast.parse(RUNNER_PATH.read_text(encoding="utf-8"))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
    assert not any("adapter" in m for m in modules)
    assert not any("yaml" in m for m in modules)
    # The runner only depends on the collector facade, never on adapters.
    assert "velaris_core.collector" in modules


# ---------- YAML adapter ----------

def test_yaml_adapter_compiles_to_testspec(tmp_path: Path) -> None:
    yaml_file = tmp_path / "test_random.yaml"
    yaml_file.write_text(
        "name: test_random\ncapabilities:\n  - random\n", encoding="utf-8"
    )
    specs = YamlAdapter().collect(yaml_file)
    assert len(specs) == 1
    spec = specs[0]
    assert isinstance(spec, TestSpec)
    assert spec.name == "test_random"
    assert spec.capabilities == ["random"]
    assert spec.callable is noop_test


def test_yaml_adapter_requires_name(tmp_path: Path) -> None:
    yaml_file = tmp_path / "bad.yaml"
    yaml_file.write_text("capabilities:\n  - random\n", encoding="utf-8")
    with pytest.raises(CollectionError, match="'name' must be a non-empty string"):
        YamlAdapter().collect(yaml_file)


def test_yaml_adapter_requires_capabilities(tmp_path: Path) -> None:
    yaml_file = tmp_path / "bad.yaml"
    yaml_file.write_text("name: t\n", encoding="utf-8")
    with pytest.raises(CollectionError, match="'capabilities' must be a non-empty list"):
        YamlAdapter().collect(yaml_file)


# ---------- Python adapter ----------

def test_python_adapter_unchanged(tmp_path: Path) -> None:
    module = tmp_path / "test_mod.py"
    module.write_text(
        "from velaris_core.decorators import test\n"
        "@test('api')\n"
        "def test_x(api):\n"
        "    assert api is not None\n",
        encoding="utf-8",
    )
    specs = PythonAdapter().collect(module)
    assert len(specs) == 1
    assert specs[0].name == "test_x"
    assert specs[0].capabilities == ["api"]
    assert callable(specs[0].callable)


# ---------- Dispatcher ----------

def test_collect_mixed_directory(tmp_path: Path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_py.py").write_text(
        "from velaris_core.decorators import test\n"
        "@test('browser')\n"
        "def test_py(browser):\n"
        "    browser.open('/')\n",
        encoding="utf-8",
    )
    (tests_dir / "test_yaml.yaml").write_text(
        "name: test_yaml\ncapabilities:\n  - browser\n", encoding="utf-8"
    )

    specs = collect([tests_dir])
    names = sorted(s.name for s in specs)
    assert names == ["test_py", "test_yaml"]


def test_collect_unknown_extension(tmp_path: Path) -> None:
    odd = tmp_path / "test.txt"
    odd.write_text("nope", encoding="utf-8")
    with pytest.raises(CollectionError, match="No authoring adapter"):
        collect([odd])


# ---------- Same engine, two authoring styles ----------

def _browser_config(tmp_path: Path) -> Path:
    config = tmp_path / "velaris.toml"
    config.write_text(
        "[capabilities.browser]\nprovider = \"fake\"\n", encoding="utf-8"
    )
    return config


# ---------- Executable YAML (Milestone 10) ----------

def test_yaml_actions_compile_to_callable(tmp_path: Path) -> None:
    yaml_file = tmp_path / "test_login.yaml"
    yaml_file.write_text(
        "name: test_login_yaml\n"
        "capabilities:\n  - browser\n"
        "actions:\n"
        '  - browser.open("/login")\n'
        '  - browser.type("#username", "demo")\n'
        '  - browser.click("#submit")\n',
        encoding="utf-8",
    )
    specs = YamlAdapter().collect(yaml_file)
    assert len(specs) == 1
    assert specs[0].callable is not noop_test
    assert specs[0].callable.__name__ == "yaml::test_login_yaml"


def test_yaml_action_unknown_capability_fails_at_compile(tmp_path: Path) -> None:
    yaml_file = tmp_path / "bad.yaml"
    yaml_file.write_text(
        "name: t\ncapabilities:\n  - browser\n"
        "actions:\n  - api.get(\"/x\")\n",
        encoding="utf-8",
    )
    with pytest.raises(CollectionError, match="not declared in 'capabilities'"):
        YamlAdapter().collect(yaml_file)


def test_yaml_action_invalid_syntax_fails_at_compile(tmp_path: Path) -> None:
    yaml_file = tmp_path / "bad.yaml"
    yaml_file.write_text(
        "name: t\ncapabilities:\n  - browser\n"
        "actions:\n  - browser.open(\n",
        encoding="utf-8",
    )
    with pytest.raises(CollectionError, match="invalid action syntax"):
        YamlAdapter().collect(yaml_file)


def test_yaml_action_non_literal_arg_fails_at_compile(tmp_path: Path) -> None:
    yaml_file = tmp_path / "bad.yaml"
    yaml_file.write_text(
        "name: t\ncapabilities:\n  - browser\n"
        "actions:\n  - browser.open(some_var)\n",
        encoding="utf-8",
    )
    with pytest.raises(CollectionError, match="must be literals"):
        YamlAdapter().collect(yaml_file)


def test_yaml_action_not_a_call_fails_at_compile(tmp_path: Path) -> None:
    yaml_file = tmp_path / "bad.yaml"
    yaml_file.write_text(
        "name: t\ncapabilities:\n  - browser\n"
        "actions:\n  - browser.open\n",
        encoding="utf-8",
    )
    with pytest.raises(CollectionError, match="capability call"):
        YamlAdapter().collect(yaml_file)


def test_yaml_unknown_method_fails_at_runtime(tmp_path: Path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_bad.yaml").write_text(
        "name: test_bad\ncapabilities:\n  - browser\n"
        "actions:\n  - browser.scroll(\"#x\")\n",
        encoding="utf-8",
    )
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run([tests_dir], config_path=_browser_config(tmp_path))
    # Unknown method surfaces as an ordinary test failure (runner unchanged).
    assert result.failed == 1
    assert "has no method 'scroll'" in buffer.getvalue()


def test_yaml_bad_arg_count_fails_at_runtime(tmp_path: Path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_bad.yaml").write_text(
        "name: test_bad\ncapabilities:\n  - browser\n"
        "actions:\n  - browser.open(\"/a\", \"/b\")\n",
        encoding="utf-8",
    )
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run([tests_dir], config_path=_browser_config(tmp_path))
    assert result.failed == 1
    assert "invalid call to browser.open" in buffer.getvalue()


def test_python_and_yaml_actions_emit_identical_events(tmp_path: Path) -> None:
    """Python and executable YAML must produce the same capability events."""
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_py.py").write_text(
        "from velaris_core.decorators import test\n"
        "@test('browser')\n"
        "def test_py(browser):\n"
        "    browser.open('/login')\n"
        "    browser.click('#submit')\n",
        encoding="utf-8",
    )
    (tests_dir / "test_yaml.yaml").write_text(
        "name: test_yaml\ncapabilities:\n  - browser\n"
        "actions:\n"
        '  - browser.open("/login")\n'
        '  - browser.click("#submit")\n',
        encoding="utf-8",
    )
    json_log = tmp_path / "events.jsonl"
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        run([tests_dir], config_path=_browser_config(tmp_path), json_log=json_log)

    events = [json.loads(line) for line in json_log.read_text().splitlines()]

    def observed(test_name: str) -> list[tuple[str, dict]]:
        return [
            (e["action"], e["data"])
            for e in events
            if e.get("type") == "CapabilityObserved" and e["test"] == test_name
        ]

    # Identical capability observations (open, click, and the close teardown).
    assert observed("test_py") == observed("test_yaml")


def test_python_and_yaml_run_through_same_engine(tmp_path: Path) -> None:
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_py.py").write_text(
        "from velaris_core.decorators import test\n"
        "@test('browser')\n"
        "def test_py(browser):\n"
        "    browser.open('/login')\n",
        encoding="utf-8",
    )
    (tests_dir / "test_yaml.yaml").write_text(
        "name: test_yaml\ncapabilities:\n  - browser\n", encoding="utf-8"
    )
    config = tmp_path / "velaris.toml"
    config.write_text(
        "[capabilities.browser]\nprovider = \"fake\"\n", encoding="utf-8"
    )

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run([tests_dir], config_path=config, output_mode=OutputMode.DEBUG)
    output = buffer.getvalue()

    assert result.passed == 2
    assert result.failed == 0
    # Both authoring styles produced the same lifecycle events.
    assert "RUN test_py" in output
    assert "RUN test_yaml" in output
    assert output.count("RESOLVE browser(fake)") == 2
