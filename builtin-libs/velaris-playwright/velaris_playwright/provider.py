from __future__ import annotations

from typing import Any, Callable
from playwright.sync_api import sync_playwright

from velaris_contracts import Browser
from velaris_core.sdk import Registry, Teardown, capability_observed, pop_emit


class PlaywrightBrowser:
    """A real Playwright browser provider satisfying the Browser contract."""

    def __init__(
        self,
        options: dict[str, Any],
        emit: Callable[[object], None] | None = None,
    ) -> None:
        self._emit = emit
        self._playwright = sync_playwright().start()

        browser_type = str(options.get("browser_type", "chromium")).lower()
        headless = bool(options.get("headless", True))

        if browser_type == "chromium":
            self._browser = self._playwright.chromium.launch(headless=headless)
        elif browser_type == "firefox":
            self._browser = self._playwright.firefox.launch(headless=headless)
        elif browser_type == "webkit":
            self._browser = self._playwright.webkit.launch(headless=headless)
        else:
            self._browser = self._playwright.chromium.launch(headless=headless)

        self._page = self._browser.new_page()
        self._closed = False
        self._active_frame = None
        self._dialog_behavior = "dismiss"
        self._last_alert_text = ""

        # Set up dialog interception
        self._page.on("dialog", self._handle_dialog)

        if self._emit is not None:
            self._emit(capability_observed("browser", "resolved", {"browser_type": browser_type}))

    def _handle_dialog(self, dialog: Any) -> None:
        self._last_alert_text = dialog.message
        if self._dialog_behavior == "accept":
            dialog.accept()
        else:
            dialog.dismiss()

    def _get_context(self) -> Any:
        if self._active_frame is not None:
            return self._page.frame_locator(self._active_frame)
        return self._page

    def open(self, url: str) -> None:
        self._page.goto(url)
        self._emit_action("open", path=url)

    def click(self, selector: str) -> None:
        self._get_context().locator(selector).click()
        self._emit_action("click", path=selector)

    def type(self, selector: str, text: str) -> None:
        self._get_context().locator(selector).fill(text)
        self._emit_action("type", path=selector, text=text)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self._page.close()
        except Exception:
            pass
        try:
            self._browser.close()
        except Exception:
            pass
        try:
            self._playwright.stop()
        except Exception:
            pass
        self._emit_action("close")

    def check(self, selector: str) -> None:
        self._get_context().locator(selector).check()
        self._emit_action("check", path=selector)

    def uncheck(self, selector: str) -> None:
        self._get_context().locator(selector).uncheck()
        self._emit_action("uncheck", path=selector)

    def select_option(self, selector: str, value: str) -> None:
        self._get_context().locator(selector).select_option(value)
        self._emit_action("select_option", path=selector, text=value)

    def hover(self, selector: str) -> None:
        self._get_context().locator(selector).hover()
        self._emit_action("hover", path=selector)

    def press_key(self, selector: str, key: str) -> None:
        self._get_context().locator(selector).press(key)
        self._emit_action("press_key", path=selector, text=key)

    def drag_and_drop(self, source: str, target: str) -> None:
        source_loc = self._get_context().locator(source)
        target_loc = self._get_context().locator(target)
        source_loc.drag_to(target_loc)
        self._emit_action("drag_and_drop", path=source, text=target)

    def switch_to_frame(self, selector: str) -> None:
        self._active_frame = selector
        self._emit_action("switch_to_frame", path=selector)

    def switch_to_main_frame(self) -> None:
        self._active_frame = None
        self._emit_action("switch_to_main_frame")

    def switch_to_tab(self, index: int) -> None:
        import time
        context = self._browser.contexts[0]
        for _ in range(40):
            if index < len(context.pages):
                break
            time.sleep(0.05)

        pages = context.pages
        if index < 0 or index >= len(pages):
            raise IndexError(f"Tab index {index} out of range (total tabs: {len(pages)})")
        self._page = pages[index]
        # Attach dialog listener to the newly selected page
        self._page.on("dialog", self._handle_dialog)
        self._emit_action("switch_to_tab", text=str(index))

    def accept_alert(self) -> None:
        self._dialog_behavior = "accept"
        self._emit_action("accept_alert")

    def dismiss_alert(self) -> None:
        self._dialog_behavior = "dismiss"
        self._emit_action("dismiss_alert")

    def alert_text(self) -> str:
        self._emit_action("alert_text")
        return self._last_alert_text

    def text_content(self, selector: str) -> str:
        val = str(self._get_context().locator(selector).text_content() or "")
        self._emit_action("text_content", path=selector, text=val)
        return val

    def value(self, selector: str) -> str:
        val = str(self._get_context().locator(selector).input_value() or "")
        self._emit_action("value", path=selector, text=val)
        return val

    def is_visible(self, selector: str) -> bool:
        visible = bool(self._get_context().locator(selector).is_visible())
        self._emit_action("is_visible", path=selector, text=str(visible))
        return visible

    def is_enabled(self, selector: str) -> bool:
        enabled = bool(self._get_context().locator(selector).is_enabled())
        self._emit_action("is_enabled", path=selector, text=str(enabled))
        return enabled

    def is_checked(self, selector: str) -> bool:
        checked = bool(self._get_context().locator(selector).is_checked())
        self._emit_action("is_checked", path=selector, text=str(checked))
        return checked

    def wait_for_selector(self, selector: str, state: str = "visible") -> None:
        self._get_context().locator(selector).wait_for(state=state)
        self._emit_action("wait_for_selector", path=selector, text=state)

    def screenshot(self, path: str) -> None:
        self._page.screenshot(path=path)
        self._emit_action("screenshot", path=path)

    def _emit_action(
        self,
        event: str,
        *,
        path: str | None = None,
        text: str | None = None,
    ) -> None:
        if self._emit is None:
            return
        data: dict[str, Any] = {}
        if path is not None:
            data["path"] = path
        if text is not None:
            data["text"] = text
        self._emit(capability_observed("browser", event, data))


def create_playwright_browser(options: dict[str, Any]) -> tuple[Browser, Teardown]:
    """Factory function for creating the Playwright browser provider."""
    cleaned, emit = pop_emit(options)
    browser = PlaywrightBrowser(cleaned, emit=emit)
    return browser, browser.close


def register_playwright_providers(registry: Registry) -> None:
    """Register the playwright browser provider factory."""
    registry.register("browser", "playwright", create_playwright_browser)
