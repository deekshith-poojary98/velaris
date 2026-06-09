"""Browser capability stress tests."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from pathlib import Path


from velaris_core.bootstrap import register_builtin_providers
from velaris_core.providers_browser import FakeBrowser, create_fake_browser
from velaris_core.registry import Registry
from velaris_core.output_mode import OutputMode
from velaris_core.runner import run
from velaris_contracts.browser.v0_1 import Browser

EXAMPLE_DIR = Path(__file__).resolve().parents[3] / "examples" / "browser"


def test_fake_browser_implements_contract() -> None:
    browser, teardown = create_fake_browser({})
    try:
        assert isinstance(browser, Browser)
        browser.open("/login")
        browser.type("#username", "demo")
        browser.click("#submit")
        assert browser.navigation_history == ["/login"]
        assert browser.typed_values == [("#username", "demo")]
        assert browser.click_history == ["#submit"]
    finally:
        teardown()


def test_run_login_fake_provider() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        result = run(
            [EXAMPLE_DIR / "tests" / "test_login.py"],
            config_path=EXAMPLE_DIR / "velaris.fake.toml",
            output_mode=OutputMode.DEBUG,
        )

    output = buffer.getvalue()
    assert result.passed == 1
    assert result.failed == 0
    assert output.index("RUN test_login") < output.index("RESOLVE browser(fake)")
    assert output.index("RESOLVE browser(fake)") < output.index("browser.open /login")
    assert output.index("browser.open /login") < output.index("browser.type #username demo")
    assert output.index("browser.type #username demo") < output.index("browser.click #submit")
    assert output.index("browser.click #submit") < output.index("PASS test_login")
    assert output.index("PASS test_login") < output.index("browser.close")
    assert output.index("browser.close") < output.index("TEARDOWN browser")


def test_provider_swap_verbose(tmp_path: Path) -> None:
    buffer = io.StringIO()
    json_path = tmp_path / "browser.jsonl"
    with redirect_stdout(buffer):
        result = run(
            [EXAMPLE_DIR / "tests" / "test_login.py"],
            config_path=EXAMPLE_DIR / "velaris.verbose.toml",
            json_log=json_path,
            output_mode=OutputMode.VERBOSE,
        )

    assert result.passed == 1
    assert "RESOLVE browser(verbose)" in buffer.getvalue()

    lines = [json.loads(line) for line in json_path.read_text().strip().splitlines()]
    browser_events = [
        line for line in lines if line.get("type") == "CapabilityObserved"
    ]
    assert any(
        e["action"] == "open" and "verbose:" in str(e.get("data", {}).get("text", ""))
        for e in browser_events
    )
    assert any(
        e["action"] == "type" and "verbose:" in str(e.get("data", {}).get("text", ""))
        for e in browser_events
    )


def test_browser_events_reach_json_and_stdout(tmp_path: Path) -> None:
    json_path = tmp_path / "events.jsonl"
    stdout_buffer = io.StringIO()

    with redirect_stdout(stdout_buffer):
        run(
            [EXAMPLE_DIR / "tests" / "test_login.py"],
            config_path=EXAMPLE_DIR / "velaris.fake.toml",
            json_log=json_path,
            output_mode=OutputMode.DEBUG,
        )

    stdout = stdout_buffer.getvalue()
    assert "browser.open /login" in stdout

    types = [json.loads(line)["type"] for line in json_path.read_text().strip().splitlines()]
    assert "CapabilityObserved" in types
    assert "CapabilityResolved" in types
    assert "RunFinished" in types


def test_registry_lists_browser_providers() -> None:
    registry = Registry()
    register_builtin_providers(registry)
    assert registry.list_providers("browser") == ["fake", "verbose"]


def test_emit_on_actions() -> None:
    events: list[object] = []

    def emit(event: object) -> None:
        events.append(event)

    browser = FakeBrowser(emit=emit)
    browser.open("/a")
    browser.click("#b")
    browser.close()

    from velaris_core.events import CapabilityObserved

    assert len(events) == 3
    assert all(isinstance(e, CapabilityObserved) for e in events)
    assert events[0].action == "open"
    assert events[1].action == "click"
    assert events[2].action == "close"
