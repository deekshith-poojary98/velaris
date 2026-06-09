"""BDD adapter tests — Gherkin compiles to the same TestSpec as Python and YAML."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path

import pytest

from velaris_core.adapters import BddAdapter, default_adapters
from velaris_core.adapters.bdd_parser import parse_feature
from velaris_core.collector import collect
from velaris_core.errors import CollectionError
from velaris_core.output_mode import OutputMode
from velaris_core.runner import run

AUTHORING_DIR = Path(__file__).resolve().parents[3] / "examples" / "authoring"
BROWSER_CONFIG = AUTHORING_DIR / "velaris.toml"


def test_default_adapters_include_bdd() -> None:
    assert [type(a).__name__ for a in default_adapters()] == [
        "PythonAdapter",
        "YamlAdapter",
        "BddAdapter",
    ]


def test_bdd_parser_extracts_scenario_and_steps(tmp_path: Path) -> None:
    feature = tmp_path / "login.feature"
    feature.write_text(
        "Feature: Login\n\n"
        "Scenario: User logs in\n\n"
        '  Given browser.open("/login")\n'
        '  When browser.type("#username", "demo")\n'
        '  Then browser.click("#submit")\n',
        encoding="utf-8",
    )
    scenarios = parse_feature(feature)
    assert len(scenarios) == 1
    assert scenarios[0].feature == "Login"
    assert scenarios[0].name == "User logs in"
    assert scenarios[0].steps == (
        'browser.open("/login")',
        'browser.type("#username", "demo")',
        'browser.click("#submit")',
    )


def test_bdd_adapter_compiles_to_testspec(tmp_path: Path) -> None:
    feature = tmp_path / "login.feature"
    feature.write_text(
        "Feature: Login\n\n"
        "Scenario: User logs in\n\n"
        '  Given browser.open("/login")\n',
        encoding="utf-8",
    )
    specs = BddAdapter().collect(feature)
    assert len(specs) == 1
    assert specs[0].name == "User logs in"
    assert specs[0].capabilities == ["browser"]
    assert specs[0].callable.__name__ == "bdd::User logs in"


def test_bdd_rejects_unsupported_gherkin(tmp_path: Path) -> None:
    feature = tmp_path / "bad.feature"
    feature.write_text(
        "Feature: Login\n\n"
        "@browser\n"
        "Scenario: User logs in\n\n"
        '  Given browser.open("/login")\n',
        encoding="utf-8",
    )
    with pytest.raises(CollectionError, match="unsupported line"):
        BddAdapter().collect(feature)


def test_bdd_rejects_step_outside_scenario(tmp_path: Path) -> None:
    feature = tmp_path / "bad.feature"
    feature.write_text('Given browser.open("/login")\n', encoding="utf-8")
    with pytest.raises(CollectionError, match="must appear inside a Scenario block"):
        BddAdapter().collect(feature)


def _browser_observations(events: list[dict]) -> list[tuple[str, dict]]:
    return [
        (event["action"], event["data"])
        for event in events
        if event.get("type") == "CapabilityObserved" and event.get("capability") == "browser"
    ]


def test_python_yaml_and_bdd_emit_identical_browser_events(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """All three authoring styles must produce the same capability observations."""
    monkeypatch.chdir(AUTHORING_DIR)
    json_log = tmp_path / "events.jsonl"
    with redirect_stdout(io.StringIO()):
        run(
            [
                AUTHORING_DIR / "tests" / "test_login.py",
                AUTHORING_DIR / "tests" / "test_login.yaml",
                AUTHORING_DIR / "tests" / "login.feature",
            ],
            config_path=BROWSER_CONFIG,
            json_log=json_log,
            output_mode=OutputMode.DEBUG,
        )

    events = [json.loads(line) for line in json_log.read_text().splitlines()]
    py_events = _browser_observations(
        [e for e in events if e.get("test") == "test_login"]
    )
    yaml_events = _browser_observations(
        [e for e in events if e.get("test") == "test_login_yaml"]
    )
    bdd_events = _browser_observations(
        [e for e in events if e.get("test") == "User logs in"]
    )

    expected = [
        ("open", {"path": "/login"}),
        ("type", {"path": "#username", "text": "demo"}),
        ("click", {"path": "#submit"}),
        ("close", {}),
    ]
    assert py_events == expected
    assert yaml_events == expected
    assert bdd_events == expected


def test_collect_mixed_authoring_directory() -> None:
    specs = collect([AUTHORING_DIR / "tests" / "login.feature"])
    names = [spec.name for spec in specs if spec.name == "User logs in"]
    assert names == ["User logs in"]
