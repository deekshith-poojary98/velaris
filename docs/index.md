---
layout: home

hero:
  name: Velaris
  text: Capability-driven testing
  tagline: Tests declare what they need. Configuration selects implementations. The runner handles collection, resolution, injection, and teardown.
  actions:
    - theme: brand
      text: Get Started
      link: /getting-started/
    - theme: alt
      text: How It's Different
      link: /concepts/how-velaris-is-different

features:
  - icon: 🧩
    title: Capabilities, not fixtures
    details: Tests declare required capabilities with @test("api", "secrets"). Parameter names match capability IDs. No global setup functions.
  - icon: ⚙️
    title: Config-driven providers
    details: velaris.toml binds each capability to a provider implementation. Swap env vs static secrets without changing test code.
  - icon: 📝
    title: Multiple authoring styles
    details: Python, YAML, and minimal BDD (.feature) all compile to the same TestSpec IR — one runner, one resolver.
  - icon: 🔌
    title: Manual plugins
    details: Extend Velaris with velaris_plugins.py and velaris_core.sdk. No entry points or auto-discovery in v0.1.0-alpha.
  - icon: 📊
    title: Reports that read like tests
    details: Default ✓/✗ stdout, optional --verbose/--debug, JSON event logs, and static HTML reports.
  - icon: 🔬
    title: Alpha release
    details: v0.1.0-alpha — execution engine is stable. Plugin ecosystem and packaging are experimental.
---

## How it works

Velaris follows a single execution pipeline for every test run:

```mermaid
flowchart LR
    A[Collect] --> B[TestSpec]
    B --> C[Resolve]
    C --> D[Inject]
    D --> E[Execute]
    E --> F[Events]
    F --> G[Report]
```

| Stage | What happens |
|-------|----------------|
| **Collect** | Adapters compile Python, YAML, or BDD into TestSpec |
| **TestSpec** | Validate name, capabilities, and callable into IR |
| **Resolve** | Look up provider factories from registry + config |
| **Inject** | Pass capability instances as test parameters |
| **Execute** | Run the test callable |
| **Events** | Emit lifecycle and capability observations |
| **Report** | Stdout, JSON log, or static HTML |

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

## What Velaris is not (v0.1.0-alpha)

- Not a pytest replacement
- No plugin discovery or PyPI plugin packages
- No full Cucumber/Behave-style BDD (minimal Gherkin only)
- No parallel execution
- No Playwright or Selenium providers (fake browser only)

See [Alpha scope](/alpha-scope) for full limitations.

<style>
/* Hide the redundant top-of-content H2 spacing on the home markdown block */
.VPHome .vp-doc { padding-top: 8px; }
</style>
