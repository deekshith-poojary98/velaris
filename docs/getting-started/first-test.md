# Your First Test

The fastest way to a passing test is `velaris init`. If you haven't installed Velaris yet, follow the [Quickstart](/getting-started/quickstart) first — it covers install, scaffold, and run end to end.

## Scaffold and run

```bash
velaris init demo
cd demo
velaris run
```

Expected output:

```text
✓ test_login

Passed: 1
Failed: 0
```

`velaris init` is the **recommended onboarding path**. It generates a complete, working project that passes immediately — no manual file creation, no extra config flags.

## Read the generated test

`velaris init` creates `tests/test_login.py`:

```python
from velaris_core.decorators import test as velaris_test

@velaris_test("browser")
def test_login(browser):
    browser.open("/login")
    browser.type("#username", "demo")
    browser.click("#submit")
```

Three things to notice:

1. `@velaris_test("browser")` declares the required capability
2. The parameter name `browser` matches the capability ID
3. The test calls methods on the injected instance — no construction

## Read the generated config

`velaris.toml` selects **which provider** backs each capability:

```toml
[capabilities.browser]
provider = "fake"
```

The test code stays the same when you swap providers — that's the core idea behind Velaris.

## Swap the provider

Change the provider in `velaris.toml` (for example to a more verbose backend) and rerun:

```bash
velaris run
```

Same test, different behavior. No test changes.

## Next

- [Configuration](/getting-started/configuration) — full `velaris.toml` reference
- [Examples](/examples/) — more runnable sample projects
- [Concepts: Capabilities](/concepts/capabilities) — contracts and providers
- [What Velaris Can Do Today](/what-velaris-can-do-today) — the complete feature list
