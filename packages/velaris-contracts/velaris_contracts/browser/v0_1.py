"""browser@0.1 capability contract."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from velaris_contracts._metadata import ContractMetadata

CAPABILITY_ID = "browser"
CONTRACT_VERSION = "0.1"

CONTRACT_METADATA: ContractMetadata = {
    "capability_id": CAPABILITY_ID,
    "version": CONTRACT_VERSION,
    "description": "Comprehensive browser automation, query, and assertion interface for integration testing.",
}


@runtime_checkable
class Browser(Protocol):
    """Comprehensive browser automation, query, and assertion interface for integration testing."""

    def open(self, url: str) -> None:
        """Navigate to ``url``."""
        ...

    def click(self, selector: str) -> None:
        """Click the element identified by ``selector``."""
        ...

    def type(self, selector: str, text: str) -> None:
        """Type ``text`` into the element identified by ``selector``."""
        ...

    def close(self) -> None:
        """Close the browser session."""
        ...

    def check(self, selector: str) -> None:
        """Check a checkbox or radio button."""
        ...

    def uncheck(self, selector: str) -> None:
        """Uncheck a checkbox."""
        ...

    def select_option(self, selector: str, value: str) -> None:
        """Select a value in a dropdown."""
        ...

    def hover(self, selector: str) -> None:
        """Hover mouse over the element identified by ``selector``."""
        ...

    def press_key(self, selector: str, key: str) -> None:
        """Press a keyboard key on the element identified by ``selector``."""
        ...

    def drag_and_drop(self, source: str, target: str) -> None:
        """Drag element ``source`` and drop it onto ``target``."""
        ...

    def switch_to_frame(self, selector: str) -> None:
        """Target subsequent actions inside the iframe identified by ``selector``."""
        ...

    def switch_to_main_frame(self) -> None:
        """Switch target context back to the main document frame."""
        ...

    def switch_to_tab(self, index: int) -> None:
        """Switch target context to a browser tab identified by its index."""
        ...

    def accept_alert(self) -> None:
        """Configure the browser to accept subsequent JavaScript dialogs."""
        ...

    def dismiss_alert(self) -> None:
        """Configure the browser to dismiss subsequent JavaScript dialogs."""
        ...

    def alert_text(self) -> str:
        """Return the text of the most recently triggered JavaScript dialog."""
        ...

    def text_content(self, selector: str) -> str:
        """Return the inner text content of the element identified by ``selector``."""
        ...

    def value(self, selector: str) -> str:
        """Return the input value of the element identified by ``selector``."""
        ...

    def is_visible(self, selector: str) -> bool:
        """Return True if the element identified by ``selector`` is visible, False otherwise."""
        ...

    def is_enabled(self, selector: str) -> bool:
        """Return True if the element identified by ``selector`` is enabled, False otherwise."""
        ...

    def is_checked(self, selector: str) -> bool:
        """Return True if the checkbox or radio button identified by ``selector`` is checked, False otherwise."""
        ...

    def wait_for_selector(self, selector: str, state: str = "visible") -> None:
        """Wait for the element identified by ``selector`` to reach the specified state."""
        ...

    def screenshot(self, path: str) -> None:
        """Take a screenshot of the active page and save it to ``path``."""
        ...
