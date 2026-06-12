from __future__ import annotations

from pathlib import Path
from velaris_core.decorators import test

__test__ = False


@test("browser")
def test_login(browser) -> None:
    html_path = Path(__file__).parent.parent / "login.html"
    url = f"file://{html_path.resolve()}"

    browser.open(url)
    browser.type("#username", "playwright_user")
    browser.click("#submit")
