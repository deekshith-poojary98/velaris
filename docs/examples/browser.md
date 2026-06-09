# Browser Example

Stateful, event-heavy capability without real browser drivers.

**Location:** `examples/browser/`

## Run

```bash
cd examples/browser
velaris run tests/ --config velaris.fake.toml
```

## Provider swap

```bash
velaris run tests/ --config velaris.verbose.toml
```

Same test, different event payloads in `--debug` mode.

## JSON log and HTML report

```bash
velaris run tests/ --config velaris.fake.toml --json-log events.jsonl
velaris run tests/ --config velaris.fake.toml --html-report
open report.html
```

## Test

```python
from velaris_core.decorators import test as velaris_test

@velaris_test("browser")
def test_login(browser):
    browser.open("/login")
    browser.type("#username", "demo")
    browser.click("#submit")
```

## Config

```toml
# velaris.fake.toml
[capabilities.browser]
provider = "fake"
```

## Expected output (default)

```text
✓ test_login

Passed: 1
Failed: 0
Duration: 0.00s
```

Use `--verbose` or `--debug` for lifecycle and capability detail. See [CLI UX redesign](/cli-ux-redesign).

## Learn

- [browser@0.1 capability](/guide/capabilities/browser)
- [Events & Reporting](/concepts/events)
- [HTML Report](/html-report)
