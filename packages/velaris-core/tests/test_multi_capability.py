"""Multiple capability resolution and lifecycle tests."""

from __future__ import annotations

import io
from contextlib import redirect_stdout

import pytest
import responses

from velaris_core.bootstrap import register_builtin_providers
from velaris_core.errors import CapabilitySetupError
from velaris_core.registry import Registry
from velaris_core.resolver import Resolver
from velaris_core.output_mode import OutputMode
from velaris_core.runner import run
from velaris_core.types import CapabilityBinding

EXAMPLE_DIR = __import__("pathlib").Path(__file__).resolve().parents[3] / "examples" / "minimal"


def _emit_log() -> tuple[list[str], object]:
    events: list[str] = []

    def emit(event: object) -> None:
        events.append(type(event).__name__)

    return events, emit


def test_resolve_multiple_capabilities_in_order() -> None:
    registry = Registry()
    register_builtin_providers(registry)
    bindings = {
        "api": CapabilityBinding("api", "requests", {"base_url": "http://testserver"}),
        "secrets": CapabilityBinding("secrets", "env", {}),
    }
    events, emit = _emit_log()
    resolver = Resolver(registry, bindings, emit=emit)

    api = resolver.resolve("api")
    secrets = resolver.resolve("secrets")
    assert api is resolver.resolve("api")
    assert secrets is resolver.resolve("secrets")
    assert events == [
        "CapabilityResolved",
        "CapabilityObserved",
        "CapabilityResolved",
    ]

    resolver.teardown()
    assert events[-2:] == ["CapabilityTeardown", "CapabilityTeardown"]


def test_teardown_runs_in_reverse_creation_order() -> None:
    registry = Registry()
    register_builtin_providers(registry)
    bindings = {
        "api": CapabilityBinding("api", "requests", {"base_url": "http://testserver"}),
        "secrets": CapabilityBinding("secrets", "env", {}),
    }
    teardown_order: list[str] = []

    def emit(event: object) -> None:
        from velaris_core.events import CapabilityTeardown

        if isinstance(event, CapabilityTeardown):
            teardown_order.append(event.capability)

    resolver = Resolver(registry, bindings, emit=emit)
    resolver.resolve("api")
    resolver.resolve("secrets")
    resolver.teardown()
    assert teardown_order == ["secrets", "api"]


def test_partial_setup_failure_still_teardowns_resolved() -> None:
    registry = Registry()
    register_builtin_providers(registry)
    bindings = {
        "api": CapabilityBinding("api", "requests", {"base_url": "http://testserver"}),
        "secrets": CapabilityBinding(
            "secrets",
            "env",
            {"required": ["MISSING_AT_SETUP"]},
        ),
    }
    teardown_order: list[str] = []

    def emit(event: object) -> None:
        from velaris_core.events import CapabilityTeardown

        if isinstance(event, CapabilityTeardown):
            teardown_order.append(event.capability)

    resolver = Resolver(registry, bindings, emit=emit)
    resolver.resolve("api")
    with pytest.raises(CapabilitySetupError):
        resolver.resolve("secrets")
    resolver.teardown()
    assert teardown_order == ["api"]


@responses.activate
def test_run_checkout_multi_capability(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("API_TOKEN", "test-token")
    responses.add(
        responses.GET,
        "http://testserver/orders",
        status=200,
    )

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run(
            [EXAMPLE_DIR / "tests" / "test_checkout.py"],
            config_path=EXAMPLE_DIR / "velaris.toml",
            output_mode=OutputMode.DEBUG,
        )

    output = buffer.getvalue()
    assert result.passed == 1
    assert result.failed == 0
    assert output.index("RUN test_checkout") < output.index("RESOLVE api(requests)")
    assert output.index("RESOLVE api(requests)") < output.index("RESOLVE secrets(env)")
    assert output.index("RESOLVE secrets(env)") < output.index("PASS test_checkout")
    assert output.index("PASS test_checkout") < output.index("TEARDOWN secrets")
    assert output.index("TEARDOWN secrets") < output.index("TEARDOWN api")


def test_run_missing_secret_failure_and_teardown() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run(
            [EXAMPLE_DIR / "tests" / "test_missing_secret.py"],
            config_path=EXAMPLE_DIR / "velaris.toml",
            output_mode=OutputMode.DEBUG,
        )

    output = buffer.getvalue()
    assert result.passed == 0
    assert result.failed == 1
    assert result.exit_code == 1
    assert "RUN test_missing_secret" in output
    assert "RESOLVE secrets(env)" in output
    assert "FAIL test_missing_secret" in output
    assert "'DOES_NOT_EXIST'" in output
    assert output.index("FAIL test_missing_secret") < output.index("TEARDOWN secrets")
    assert "TEARDOWN api" not in output
