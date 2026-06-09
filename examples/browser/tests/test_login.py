"""Browser capability stress-test."""

from velaris_core.decorators import test as velaris_test


@velaris_test("browser")
def test_login(browser):
    browser.open("/login")
    browser.type("#username", "demo")
    browser.click("#submit")
