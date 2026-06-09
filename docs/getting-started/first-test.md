# Your First Test

Run a passing test in under two minutes using the **browser** example — no network or environment variables required.

## 1. Install Velaris

If you haven't already, follow [Installation](/getting-started/installation).

## 2. Run the browser example

```bash
cd examples/browser
velaris run tests/ --config velaris.fake.toml
```

Expected output:

```text
✓ test_login

Passed: 1
Failed: 0
Duration: 0.00s
```

## 3. Read the test

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

## 4. Read the config

```toml
# velaris.fake.toml
[capabilities.browser]
provider = "fake"
```

Config selects **which provider** backs the `browser` capability. The test code stays the same when you swap providers.

## 5. Swap the provider

```bash
velaris run tests/ --config velaris.verbose.toml
```

Same test, verbose event payloads. No test changes.

## Scaffold a new project

After [Installation](/getting-started/installation), skip manual file creation:

```bash
velaris init my-project
cd my-project
velaris run
```

## Write your own test

Create a project directory manually:

```text
my-project/
├── velaris.toml
└── tests/
    └── test_demo.py
```

```toml
# velaris.toml
[capabilities.browser]
provider = "fake"
```

```python
# tests/test_demo.py
from velaris_core.decorators import test

@test("browser")
def test_homepage(browser):
    browser.open("/")
    browser.click("#cta")
```

```bash
cd my-project
velaris run tests/
```

## Next

- [Configuration](/getting-started/configuration) — full `velaris.toml` reference
- [Concepts: Capabilities](/concepts/capabilities) — contracts and providers
- [Examples](/examples/) — more sample projects

::: warning HTTP examples need setup
The `examples/minimal` HTTP tests require `API_TOKEN` and HTTP mocking. Start with browser or [stress-test](/examples/stress-test) examples first.
:::
