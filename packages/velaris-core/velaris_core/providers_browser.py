"""browser capability providers (fake, verbose)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from velaris_contracts.browser.v0_1 import Browser
from velaris_core.provider_context import pop_emit
from velaris_core.reporting import capability_observed
from velaris_core.types import Teardown


class FakeBrowser:
    """In-memory browser for architecture stress tests."""

    def __init__(
        self,
        emit: Callable[[object], None] | None = None,
        *,
        verbose: bool = False,
    ) -> None:
        self._emit = emit
        self._verbose = verbose
        self._closed = False
        self.navigation_history: list[str] = []
        self.click_history: list[str] = []
        self.typed_values: list[tuple[str, str]] = []

    def open(self, url: str) -> None:
        self.navigation_history.append(url)
        self._emit_action("open", path=url)

    def click(self, selector: str) -> None:
        self.click_history.append(selector)
        self._emit_action("click", path=selector)

    def type(self, selector: str, text: str) -> None:
        self.typed_values.append((selector, text))
        self._emit_action("type", path=selector, text=text)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        self._emit_action("close")

    def check(self, selector: str) -> None:
        self._emit_action("check", path=selector)

    def uncheck(self, selector: str) -> None:
        self._emit_action("uncheck", path=selector)

    def select_option(self, selector: str, value: str) -> None:
        self._emit_action("select_option", path=selector, text=value)

    def hover(self, selector: str) -> None:
        self._emit_action("hover", path=selector)

    def press_key(self, selector: str, key: str) -> None:
        self._emit_action("press_key", path=selector, text=key)

    def drag_and_drop(self, source: str, target: str) -> None:
        self._emit_action("drag_and_drop", path=source, text=target)

    def switch_to_frame(self, selector: str) -> None:
        self._emit_action("switch_to_frame", path=selector)

    def switch_to_main_frame(self) -> None:
        self._emit_action("switch_to_main_frame")

    def switch_to_tab(self, index: int) -> None:
        self._emit_action("switch_to_tab", text=str(index))

    def accept_alert(self) -> None:
        self._emit_action("accept_alert")

    def dismiss_alert(self) -> None:
        self._emit_action("dismiss_alert")

    def alert_text(self) -> str:
        self._emit_action("alert_text")
        return "mock_alert_text"

    def text_content(self, selector: str) -> str:
        self._emit_action("text_content", path=selector)
        return f"text:{selector}"

    def value(self, selector: str) -> str:
        self._emit_action("value", path=selector)
        return f"value:{selector}"

    def is_visible(self, selector: str) -> bool:
        self._emit_action("is_visible", path=selector)
        return True

    def is_enabled(self, selector: str) -> bool:
        self._emit_action("is_enabled", path=selector)
        return True

    def is_checked(self, selector: str) -> bool:
        self._emit_action("is_checked", path=selector)
        return True

    def wait_for_selector(self, selector: str, state: str = "visible") -> None:
        self._emit_action("wait_for_selector", path=selector, text=state)

    def screenshot(self, path: str) -> None:
        from pathlib import Path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write("mock_screenshot_data")
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
        detail = text
        if self._verbose:
            suffix = f"verbose:{event}"
            if path:
                suffix = f"{suffix} target={path}"
            detail = suffix if text is None else f"{text}|{suffix}"
        data: dict[str, Any] = {}
        if path is not None:
            data["path"] = path
        if detail is not None:
            data["text"] = detail
        self._emit(capability_observed("browser", event, data))


class FakeBrowserVerbose(FakeBrowser):
    """Same contract as FakeBrowser with verbose event payloads."""

    def __init__(self, emit: Callable[[object], None] | None = None) -> None:
        super().__init__(emit, verbose=True)


def create_fake_browser(options: dict[str, Any]) -> tuple[Browser, Teardown]:
    _, emit = pop_emit(options)
    browser = FakeBrowser(emit=emit)
    return browser, browser.close


def create_verbose_browser(options: dict[str, Any]) -> tuple[Browser, Teardown]:
    _, emit = pop_emit(options)
    browser = FakeBrowserVerbose(emit=emit)
    return browser, browser.close
