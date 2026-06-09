"""Python authoring style — browser login flow."""

from __future__ import annotations

from velaris_core.decorators import test

__test__ = False


@test("browser")
def test_login(browser) -> None:
    browser.open("/login")
    browser.type("#username", "demo")
    browser.click("#submit")
