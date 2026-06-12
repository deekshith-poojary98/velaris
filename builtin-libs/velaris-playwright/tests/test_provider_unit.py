from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from velaris_contracts import Browser
from velaris_playwright.provider import create_playwright_browser


def test_contract_compliance_verification() -> None:
    events = []

    def emit(event: Any) -> None:
        events.append(event)

    # Instantiate browser using our factory
    options = {"_emit": emit, "browser_type": "chromium", "headless": True}
    browser, teardown = create_playwright_browser(options)

    try:
        # 1. Verify that the provider satisfies the Browser contract
        assert isinstance(browser, Browser), "PlaywrightBrowser does not satisfy Browser Protocol"

        # 2. Run all operations against kitchen_sink.html
        html_path = Path(__file__).parent.parent / "examples" / "kitchen_sink.html"
        url = f"file://{html_path.resolve()}"

        browser.open(url)
        
        # Checkbox & Radio
        assert not browser.is_checked("#my-checkbox")
        browser.check("#my-checkbox")
        assert browser.is_checked("#my-checkbox")
        browser.uncheck("#my-checkbox")
        
        browser.check("#my-radio")
        assert browser.is_checked("#my-radio")

        # Dropdown
        browser.select_option("#my-dropdown", "val2")
        assert browser.value("#my-dropdown") == "val2"

        # Text & Visibility Queries
        assert browser.text_content("#visible-div") == "I am visible"
        assert browser.is_visible("#visible-div")
        assert not browser.is_visible("#hidden-div")
        assert not browser.is_enabled("#disable-btn")
        assert browser.is_enabled("#enable-btn")

        # Hover & Keypress
        browser.hover("#hover-div")
        assert browser.text_content("#hover-div") == "Hovered!"
        
        browser.type("#key-input", "")
        browser.press_key("#key-input", "x")
        assert browser.text_content("#key-status") == "Pressed:x"

        # Drag and Drop
        browser.drag_and_drop("#drag-source", "#drop-target")
        assert browser.text_content("#drop-target") == "Dropped!"

        # Frame Switching
        browser.switch_to_frame("#my-iframe")
        assert browser.text_content("#frame-title") == "Inside Frame"
        browser.click("#frame-btn")
        assert browser.text_content("#frame-title") == "Frame Btn Clicked"
        browser.switch_to_main_frame()

        # Alerts
        browser.accept_alert()
        browser.click("#alert-btn")
        assert browser.alert_text() == "This is an alert!"

        browser.dismiss_alert()
        browser.click("#confirm-btn")
        assert browser.alert_text() == "Are you sure?"

        # Tab Switching
        browser.click("#new-tab-link")
        browser.switch_to_tab(1)
        browser.open(url)
        assert browser.text_content("#visible-div") == "I am visible"
        browser.switch_to_tab(0)

        # Synchronize
        browser.wait_for_selector("#enable-btn", state="visible")

        # Screenshot
        screenshot_path = Path(__file__).parent.parent / "examples" / "screenshot_unit_test.png"
        if screenshot_path.exists():
            os.remove(screenshot_path)
        browser.screenshot(str(screenshot_path))
        assert screenshot_path.is_file()
        os.remove(screenshot_path)

    finally:
        teardown()

    # 3. Check that actions emitted the expected capability events
    actions = [getattr(e, "action", None) for e in events]
    assert "resolved" in actions
    assert "open" in actions
    assert "check" in actions
    assert "uncheck" in actions
    assert "select_option" in actions
    assert "hover" in actions
    assert "press_key" in actions
    assert "drag_and_drop" in actions
    assert "switch_to_frame" in actions
    assert "switch_to_main_frame" in actions
    assert "switch_to_tab" in actions
    assert "accept_alert" in actions
    assert "dismiss_alert" in actions
    assert "alert_text" in actions
    assert "text_content" in actions
    assert "value" in actions
    assert "is_visible" in actions
    assert "is_enabled" in actions
    assert "is_checked" in actions
    assert "wait_for_selector" in actions
    assert "screenshot" in actions
    assert "close" in actions
