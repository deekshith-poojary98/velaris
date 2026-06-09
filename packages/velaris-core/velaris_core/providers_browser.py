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
