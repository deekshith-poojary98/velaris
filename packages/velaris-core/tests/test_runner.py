"""End-to-end runner tests."""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from pathlib import Path

import pytest
import responses

from velaris_core.errors import CollectionError
from velaris_core.runner import run

EXAMPLE_DIR = Path(__file__).resolve().parents[3] / "examples" / "minimal"


@pytest.fixture(autouse=True)
def _mock_example_http(monkeypatch: pytest.MonkeyPatch) -> None:
    """Keep the example hermetic when run() loads jsonplaceholder config."""
    monkeypatch.setenv("VELARIS__CAPABILITIES__API__PROVIDER", "requests")


@responses.activate
def test_run_example_test_users() -> None:
    responses.add(
        responses.GET,
        "http://testserver/users",
        status=200,
    )

    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run(
            [EXAMPLE_DIR / "tests" / "test_users.py"],
            config_path=EXAMPLE_DIR / "velaris.toml",
        )

    output = buffer.getvalue()
    assert result.passed == 1
    assert result.failed == 0
    assert result.exit_code == 0
    assert "\u2713 test_users" in output
    assert "Passed: 1" in output
    assert "RUN test_users" not in output


def test_run_missing_path_raises() -> None:
    with pytest.raises(CollectionError, match="Path not found"):
        run(["/no/such/path/velaris-tests"])
