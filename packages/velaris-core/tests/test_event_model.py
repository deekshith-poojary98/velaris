"""Event model hardening tests."""

from __future__ import annotations

import json
from pathlib import Path


from velaris_core.events import CapabilityObserved, EventEnvelope, TestStarted
from velaris_core.reporting import event_to_dict, unwrap_envelope
from velaris_core.runner import run

EXAMPLE_BROWSER = Path(__file__).resolve().parents[3] / "examples" / "browser"


def test_event_to_dict_includes_test_correlation() -> None:
    payload = event_to_dict(
        EventEnvelope(test="test_login", event=TestStarted("test_login"))
    )
    assert payload["test"] == "test_login"
    assert payload["type"] == "TestStarted"
    assert payload["name"] == "test_login"


def test_capability_observed_is_capability_agnostic() -> None:
    observed = CapabilityObserved(
        "browser",
        "type",
        {"path": "#username", "text": "demo"},
    )
    payload = event_to_dict(EventEnvelope(test="test_login", event=observed))
    assert payload["type"] == "CapabilityObserved"
    assert payload["capability"] == "browser"
    assert payload["action"] == "type"
    assert payload["data"] == {"path": "#username", "text": "demo"}
    assert "method" not in payload
    assert "status_code" not in payload


def test_run_json_log_partitions_by_test(tmp_path: Path) -> None:
    json_path = tmp_path / "run.jsonl"
    run(
        [EXAMPLE_BROWSER / "tests" / "test_login.py"],
        config_path=EXAMPLE_BROWSER / "velaris.fake.toml",
        json_log=json_path,
    )
    records = [json.loads(line) for line in json_path.read_text().strip().splitlines()]
    login_events = [r for r in records if r.get("test") == "test_login"]
    session_events = [r for r in records if r.get("test") is None]
    assert len(login_events) >= 5
    assert any(r["type"] == "CapabilityObserved" for r in login_events)
    assert any(r["type"] == "RunFinished" for r in session_events)


def test_unwrap_envelope() -> None:
    inner = TestStarted("t")
    assert unwrap_envelope(EventEnvelope(test="t", event=inner)) == ("t", inner)
    assert unwrap_envelope(inner) == (None, inner)
