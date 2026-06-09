"""Capability composition tests (Model A — no dependency graph)."""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path

import pytest
import responses

from velaris_core.compose import apply_bootstrap_conventions
from velaris_core.output_mode import OutputMode
from velaris_core.runner import run
from velaris_core.types import CapabilityBinding

EXAMPLE_DIR = Path(__file__).resolve().parents[3] / "examples" / "composition"


def test_bootstrap_convention_merges_api_base_url() -> None:
    bindings = {
        "api": CapabilityBinding("api", "requests", {}),
        "target_environment": CapabilityBinding(
            "target_environment",
            "static",
            {"endpoints": {"api": "http://merged.example"}},
        ),
    }
    merged = apply_bootstrap_conventions(bindings)
    assert merged["api"].options["base_url"] == "http://merged.example"


def test_bootstrap_convention_explicit_base_url_wins() -> None:
    bindings = {
        "api": CapabilityBinding(
            "api",
            "requests",
            {"base_url": "http://explicit.example"},
        ),
        "target_environment": CapabilityBinding(
            "target_environment",
            "static",
            {"endpoints": {"api": "http://merged.example"}},
        ),
    }
    merged = apply_bootstrap_conventions(bindings)
    assert merged["api"].options["base_url"] == "http://explicit.example"


def test_bootstrap_convention_no_op_without_target() -> None:
    bindings = {
        "api": CapabilityBinding("api", "requests", {}),
    }
    merged = apply_bootstrap_conventions(bindings)
    assert "base_url" not in merged["api"].options


@responses.activate
@pytest.mark.parametrize(
    ("test_file", "config_file", "expected_caps"),
    [
        (
            "test_compose_in_test.py",
            "velaris.test-code.toml",
            ["target_environment", "secrets", "api"],
        ),
        (
            "test_compose_in_config.py",
            "velaris.config.toml",
            ["secrets", "api"],
        ),
        (
            "test_compose_in_bootstrap.py",
            "velaris.bootstrap.toml",
            ["secrets", "api"],
        ),
    ],
)
def test_composition_examples_pass(
    test_file: str,
    config_file: str,
    expected_caps: list[str],
) -> None:
    responses.add(responses.GET, "http://testserver/orders", status=200)

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run(
            [EXAMPLE_DIR / "tests" / test_file],
            config_path=EXAMPLE_DIR / config_file,
            output_mode=OutputMode.DEBUG,
        )

    output = buffer.getvalue()
    assert result.passed == 1
    for cap in expected_caps:
        assert f"RESOLVE {cap}(" in output
    assert "TEARDOWN" in output


@responses.activate
def test_bootstrap_example_does_not_resolve_target_environment() -> None:
    responses.add(responses.GET, "http://testserver/orders", status=200)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        run(
            [EXAMPLE_DIR / "tests" / "test_compose_in_bootstrap.py"],
            config_path=EXAMPLE_DIR / "velaris.bootstrap.toml",
            output_mode=OutputMode.DEBUG,
        )
    output = buffer.getvalue()
    assert "RESOLVE target_environment" not in output
    assert "RESOLVE api(requests)" in output


def test_three_capability_teardown_order_in_test_code_example() -> None:
    responses.add(responses.GET, "http://testserver/orders", status=200)
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        run(
            [EXAMPLE_DIR / "tests" / "test_compose_in_test.py"],
            config_path=EXAMPLE_DIR / "velaris.test-code.toml",
            output_mode=OutputMode.DEBUG,
        )
    output = buffer.getvalue()
    assert output.index("TEARDOWN target_environment") < output.index("TEARDOWN secrets")
    assert output.index("TEARDOWN secrets") < output.index("TEARDOWN api")
