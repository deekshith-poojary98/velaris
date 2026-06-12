from __future__ import annotations

import os
from pathlib import Path
from velaris_core.decorators import test

__test__ = False


@test("browser")
def test_kitchen_sink(browser) -> None:
    html_path = Path(__file__).parent.parent / "kitchen_sink.html"
    url = f"file://{html_path.resolve()}"

    # 1. Navigation & Open
    browser.open(url)

    # 2. Check / Uncheck & state assertions
    assert not browser.is_checked("#my-checkbox")
    browser.check("#my-checkbox")
    assert browser.is_checked("#my-checkbox")
    browser.uncheck("#my-checkbox")
    assert not browser.is_checked("#my-checkbox")

    browser.check("#my-radio")
    assert browser.is_checked("#my-radio")

    # 3. Dropdown Select
    assert browser.value("#my-dropdown") == "val1"
    browser.select_option("#my-dropdown", "val2")
    assert browser.value("#my-dropdown") == "val2"

    # 4. Text & Value Queries
    assert browser.text_content("#visible-div") == "I am visible"
    assert browser.is_visible("#visible-div")
    assert not browser.is_visible("#hidden-div")

    assert not browser.is_enabled("#disable-btn")
    assert browser.is_enabled("#enable-btn")

    # 5. Hover & Keypress
    assert browser.text_content("#hover-div") == "Not Hovered"
    browser.hover("#hover-div")
    assert browser.text_content("#hover-div") == "Hovered!"

    browser.type("#key-input", "")  # focus the input
    browser.press_key("#key-input", "a")
    assert browser.text_content("#key-status") == "Pressed:a"

    # 6. Drag and Drop
    assert browser.text_content("#drop-target") == "Target"
    browser.drag_and_drop("#drag-source", "#drop-target")
    assert browser.text_content("#drop-target") == "Dropped!"

    # 7. IFrame Context Switching
    browser.switch_to_frame("#my-iframe")
    assert browser.text_content("#frame-title") == "Inside Frame"
    assert browser.value("#frame-input") == "initial-frame-value"
    browser.click("#frame-btn")
    assert browser.text_content("#frame-title") == "Frame Btn Clicked"

    # Switch back
    browser.switch_to_main_frame()
    assert browser.text_content("#visible-div") == "I am visible"

    # 8. Alert Interception & Dialog Text
    browser.accept_alert()
    browser.click("#alert-btn")
    assert browser.alert_text() == "This is an alert!"

    browser.dismiss_alert()
    browser.click("#confirm-btn")
    assert browser.alert_text() == "Are you sure?"

    # 9. Wait For Selector
    browser.wait_for_selector("#enable-btn", state="visible")

    # 10. Multi-tab Switching
    browser.click("#new-tab-link")
    # There should now be two pages in the context
    browser.switch_to_tab(1)
    browser.open(url)  # Navigate the new tab
    assert browser.text_content("#visible-div") == "I am visible"
    # Switch back to the first tab
    browser.switch_to_tab(0)
    assert browser.text_content("#visible-div") == "I am visible"

    # 11. Screenshot (saving to examples/screenshot_test.png)
    screenshot_path = Path(__file__).parent.parent / "screenshot_test.png"
    if screenshot_path.exists():
        os.remove(screenshot_path)
    browser.screenshot(str(screenshot_path))
    assert screenshot_path.is_file()
    os.remove(screenshot_path)
