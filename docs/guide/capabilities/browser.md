# browser@0.1

Minimal browser automation for integration tests. **No Playwright or Selenium** in alpha — fake in-memory providers only.

## Contract

```python
from velaris_contracts.browser.v0_1 import Browser
```

| Method | Description |
|--------|-------------|
| `open(url)` | Navigate to URL |
| `click(selector)` | Click element |
| `type(selector, text)` | Type into element |
| `close()` | Close session |

## Providers

### `fake`

In-memory browser tracking navigation, clicks, and typed values.

```toml
[capabilities.browser]
provider = "fake"
```

### `verbose`

Same behavior with verbose event payloads.

```toml
[capabilities.browser]
provider = "verbose"
```

## Test example

```python
from velaris_core.decorators import test as velaris_test

@velaris_test("browser")
def test_login(browser):
    browser.open("/login")
    browser.type("#username", "demo")
    browser.click("#submit")
```

## Recommended first example

```bash
cd examples/browser
velaris run tests/ --config velaris.fake.toml
```

Runs without network or environment variables.

## Events

Default stdout shows only pass/fail (`✓ test_login`). Capability actions appear with `--debug`:

| Action | `--debug` stdout |
|--------|------------------|
| `open` | `browser.open /login` |
| `type` | `browser.type #username demo` |
| `click` | `browser.click #submit` |
| `close` | `browser.close` |

## JSON log

```bash
velaris run tests/ --config velaris.fake.toml --json-log events.jsonl
```

## Stateful behavior

`FakeBrowser` tracks history lists (`navigation_history`, `click_history`, `typed_values`) — useful for architecture stress tests. Teardown closes the session.
