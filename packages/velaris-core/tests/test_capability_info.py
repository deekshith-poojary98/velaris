"""Tests for capability introspection — ``velaris capabilities`` / ``capability``.

Introspection reads contract metadata and the provider registry. It must never
resolve or instantiate providers, and it must surface plugin-only capabilities
(which have no contract) gracefully.
"""

from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout

import pytest

from velaris_core.capability_info import (
    CapabilityMetadata,
    UnknownCapabilityError,
    describe_capability,
    format_capabilities_list,
    format_capability_detail,
    list_capabilities,
)
from velaris_core.cli import main


def test_list_capabilities_includes_builtin_contracts() -> None:
    caps = list_capabilities()
    for expected in ("api", "browser", "secrets", "target_environment"):
        assert expected in caps
    assert caps == sorted(caps)


def test_describe_browser_from_contract() -> None:
    meta = describe_capability("browser")
    assert meta.id == "browser"
    assert "browser automation" in meta.description.lower()
    assert "open(url)" in meta.methods
    assert "type(selector, text)" in meta.methods
    assert "fake" in meta.providers


def test_describe_surfaces_properties_as_bare_names() -> None:
    meta = describe_capability("target_environment")
    assert "environment" in meta.methods  # a property
    assert "endpoint(name)" in meta.methods  # a method


def test_unknown_capability_raises() -> None:
    with pytest.raises(UnknownCapabilityError, match="Unknown capability"):
        describe_capability("does_not_exist")


def test_format_capabilities_list() -> None:
    out = format_capabilities_list(["api", "browser"])
    assert out == "Available capabilities\n\napi\nbrowser"


def test_format_capability_detail_without_contract() -> None:
    meta = CapabilityMetadata(
        id="random",
        description="",
        methods=[],
        providers=["seeded"],
    )
    out = format_capability_detail(meta)
    assert "Capability: random" in out
    assert "(no description available)" in out
    assert "(no contract methods published)" in out
    assert "  seeded" in out


def test_cli_capabilities_human(monkeypatch: pytest.MonkeyPatch) -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["capabilities"])
    assert code == 0
    assert "Available capabilities" in buffer.getvalue()
    assert "browser" in buffer.getvalue()


def test_cli_capabilities_json() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["capabilities", "--json"])
    assert code == 0
    payload = json.loads(buffer.getvalue())
    assert "browser" in payload


def test_cli_capability_json_shape() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        code = main(["capability", "browser", "--json"])
    assert code == 0
    payload = json.loads(buffer.getvalue())
    assert payload["id"] == "browser"
    assert set(payload) == {"id", "description", "methods", "providers"}
    assert "open(url)" in payload["methods"]


def test_cli_capability_unknown_returns_error() -> None:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(["capability", "nope"])
    assert code == 1
    assert "Unknown capability" in err.getvalue()
