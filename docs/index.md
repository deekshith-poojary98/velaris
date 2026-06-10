---
layout: home

hero:
  name: Velaris
  text: One engine, many test styles
  tagline: A capability-driven testing framework where Python, YAML, and BDD tests share the same execution engine — and you swap implementations without touching test code.
  actions:
    - theme: brand
      text: Quickstart
      link: /getting-started/quickstart
    - theme: alt
      text: What can it do today?
      link: /what-velaris-can-do-today

features:
  - icon: 🔁
    title: Swap implementations, not tests
    details: Tests declare what they need. velaris.toml picks how. Switch env vs static secrets, or fake vs verbose browser, without changing a line of test code.
  - icon: 📝
    title: Multiple authoring styles
    details: Write tests in Python, YAML, or minimal BDD (.feature). All three run on one engine with one set of results.
  - icon: 📊
    title: Shared reporting and execution
    details: Every test style flows through the same runner, the same lifecycle events, and the same reports — stdout, JSON logs, or static HTML.
---

## Why Velaris?

- **Swap implementations without changing tests** — capabilities are declared in tests, providers are chosen in config.
- **Multiple authoring styles** — Python, YAML, and BDD, all on one engine.
- **Shared reporting and execution model** — one runner, one event stream, consistent reports.

## Start here

New to Velaris? **[Follow the Quickstart](/getting-started/quickstart)** — install, scaffold, and run a passing test in a few minutes.

Curious what's possible? See **[What Velaris Can Do Today](/what-velaris-can-do-today)**.

## Quick example

```python
from velaris_core.decorators import test

@test("browser")
def test_login(browser):
    browser.open("/login")
    browser.type("#username", "demo")
    browser.click("#submit")
```

```toml
# velaris.toml
[capabilities.browser]
provider = "fake"
```

```bash
velaris run tests/ --html-report
open report.html
```

## What Velaris is not (yet)

Velaris is **v0.1.0-alpha**. Be aware before you try it:

- Not a pytest replacement — see [Why Not pytest?](/concepts/why-not-pytest)
- No PyPI package yet — install from source
- No Playwright or Selenium providers — the browser capability is an in-memory fake
- No full Cucumber/Behave BDD (minimal Gherkin only) and no parallel execution

See [What Velaris Can Do Today](/what-velaris-can-do-today) for the honest, complete picture.

<style>
/* Hide the redundant top-of-content H2 spacing on the home markdown block */
.VPHome .vp-doc { padding-top: 8px; }
</style>
