"""Tests for Milestone 19 — Tags & Test Selection."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from velaris_core.decorators import test
from velaris_core.errors import CollectionError
from velaris_core.testspec import TestSpec
from velaris_core.adapters import YamlAdapter, BddAdapter
from velaris_core.adapters.bdd_parser import parse_feature
from velaris_core.runner import run
from velaris_core.discovery import discover
from velaris_core.report_loader import build_run_report
from velaris_core.html_report import _test_to_dict, render_html, TestReport, RunReport


def test_python_decorator_valid_tags() -> None:
    @test("browser", tags=["smoke", "ui"])
    def test_func(browser):
        pass

    assert getattr(test_func, "__velaris_tags__") == ["smoke", "ui"]


def test_python_decorator_invalid_tags_type() -> None:
    with pytest.raises(CollectionError, match="Tags must be a list"):
        @test("browser", tags="smoke")  # type: ignore
        def test_func(browser):
            pass


def test_python_decorator_invalid_tag_element_type() -> None:
    with pytest.raises(CollectionError, match="Tags must be strings"):
        @test("browser", tags=[123])  # type: ignore
        def test_func(browser):
            pass


def test_python_decorator_empty_tag() -> None:
    with pytest.raises(CollectionError, match="tag cannot be empty string"):
        @test("browser", tags=[""])
        def test_func(browser):
            pass


def test_python_decorator_duplicate_tag() -> None:
    with pytest.raises(CollectionError, match="Duplicate tag 'smoke'"):
        @test("browser", tags=["smoke", "smoke"])
        def test_func(browser):
            pass


def test_yaml_adapter_valid_tags(tmp_path: Path) -> None:
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(
        "name: test_yaml\n"
        "capabilities:\n"
        "  - browser\n"
        "tags:\n"
        "  - smoke\n"
        "  - ui\n",
        encoding="utf-8",
    )
    specs = YamlAdapter().collect(yaml_file)
    assert len(specs) == 1
    assert specs[0].tags == ["smoke", "ui"]


def test_yaml_adapter_invalid_tags(tmp_path: Path) -> None:
    yaml_file = tmp_path / "test.yaml"
    yaml_file.write_text(
        "name: test_yaml\n"
        "capabilities:\n"
        "  - browser\n"
        "tags:\n"
        "  - ''\n",
        encoding="utf-8",
    )
    with pytest.raises(CollectionError, match="tag cannot be empty string"):
        YamlAdapter().collect(yaml_file)


def test_bdd_parser_valid_tags(tmp_path: Path) -> None:
    feature_file = tmp_path / "login.feature"
    feature_file.write_text(
        "@feature-tag\n"
        "Feature: Login\n\n"
        "@smoke @ui\n"
        "Scenario: User logs in\n"
        "  Given browser.open('/login')\n",
        encoding="utf-8",
    )
    scenarios = parse_feature(feature_file)
    assert len(scenarios) == 1
    assert scenarios[0].tags == ("feature-tag", "smoke", "ui")


def test_bdd_parser_invalid_empty_tag(tmp_path: Path) -> None:
    feature_file = tmp_path / "login.feature"
    feature_file.write_text(
        "Feature: Login\n\n"
        "@\n"
        "Scenario: User logs in\n"
        "  Given browser.open('/login')\n",
        encoding="utf-8",
    )
    with pytest.raises(CollectionError, match="tag name cannot be empty"):
        parse_feature(feature_file)


def test_bdd_parser_duplicate_tag(tmp_path: Path) -> None:
    feature_file = tmp_path / "login.feature"
    feature_file.write_text(
        "Feature: Login\n\n"
        "@smoke @smoke\n"
        "Scenario: User logs in\n"
        "  Given browser.open('/login')\n",
        encoding="utf-8",
    )
    with pytest.raises(CollectionError, match="Duplicate tag 'smoke'"):
        parse_feature(feature_file)


def test_bdd_parser_orphaned_tags(tmp_path: Path) -> None:
    feature_file = tmp_path / "login.feature"
    feature_file.write_text(
        "Feature: Login\n\n"
        "Scenario: User logs in\n"
        "  Given browser.open('/login')\n"
        "@orphaned\n",
        encoding="utf-8",
    )
    with pytest.raises(CollectionError, match="orphaned tags"):
        parse_feature(feature_file)


def test_bdd_parser_tags_before_step(tmp_path: Path) -> None:
    feature_file = tmp_path / "login.feature"
    feature_file.write_text(
        "Feature: Login\n\n"
        "Scenario: User logs in\n"
        "  @smoke\n"
        "  Given browser.open('/login')\n",
        encoding="utf-8",
    )
    with pytest.raises(CollectionError, match="cannot be placed before a step"):
        parse_feature(feature_file)


def test_runner_tag_filtering(tmp_path: Path) -> None:
    # Set up some dummy tests in Python adapter format
    t1_path = tmp_path / "test_1.py"
    t1_path.write_text(
        "from velaris_core.decorators import test\n"
        "@test('browser', tags=['smoke'])\n"
        "def test_smoke(browser): pass\n",
        encoding="utf-8",
    )

    t2_path = tmp_path / "test_2.py"
    t2_path.write_text(
        "from velaris_core.decorators import test\n"
        "@test('browser', tags=['ui'])\n"
        "def test_ui(browser): pass\n",
        encoding="utf-8",
    )

    t3_path = tmp_path / "test_3.py"
    t3_path.write_text(
        "from velaris_core.decorators import test\n"
        "@test('browser')\n"
        "def test_none(browser): pass\n",
        encoding="utf-8",
    )

    fake_config = tmp_path / "velaris.toml"
    fake_config.write_text(
        "[capabilities.browser]\n"
        "provider = 'fake'\n",
        encoding="utf-8",
    )

    # Test filtering to 'smoke' only
    res = run([tmp_path], config_path=fake_config, tags=["smoke"])
    assert res.passed == 1

    # Test filtering to 'smoke' or 'ui' (OR semantics)
    res = run([tmp_path], config_path=fake_config, tags=["smoke", "ui"])
    assert res.passed == 2


def test_discovery_tag_filtering(tmp_path: Path) -> None:
    t1_path = tmp_path / "test_1.py"
    t1_path.write_text(
        "from velaris_core.decorators import test\n"
        "@test('browser', tags=['smoke'])\n"
        "def test_smoke(browser): pass\n",
        encoding="utf-8",
    )

    t2_path = tmp_path / "test_2.py"
    t2_path.write_text(
        "from velaris_core.decorators import test\n"
        "@test('browser', tags=['ui'])\n"
        "def test_ui(browser): pass\n",
        encoding="utf-8",
    )

    discovered = discover([tmp_path], tags=["ui"])
    assert len(discovered) == 1
    assert discovered[0].name == "test_ui"
    assert discovered[0].tags == ["ui"]


def test_report_loader_aggregates_tags() -> None:
    events = [
        {"type": "TestStarted", "test": "test_smoke", "tags": ["smoke", "ui"]},
        {"type": "TestPassed", "test": "test_smoke"},
        {"type": "RunFinished", "passed": 1, "failed": 0, "duration_seconds": 0.01},
    ]
    report = build_run_report(events)
    assert len(report.tests) == 1
    assert report.tests[0].name == "test_smoke"
    assert report.tests[0].tags == ["smoke", "ui"]


def test_html_report_serialization_and_rendering() -> None:
    test_rep = TestReport(
        name="test_smoke",
        status="passed",
        tags=["smoke"],
    )
    serialized = _test_to_dict(test_rep)
    assert serialized["tags"] == ["smoke"]

    run_rep = RunReport(passed=1, failed=0, duration_seconds=0.01, tests=[test_rep])
    html_content = render_html(run_rep)
    assert '"tags": ["smoke"]' in html_content
