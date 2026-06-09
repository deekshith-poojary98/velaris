# Authoring Styles Example

Three authoring styles, one execution engine. Every test compiles to the same `TestSpec` and runs through the same runner, resolver, and reporting.

**Location:** `examples/authoring/`

## Run

```bash
cd examples/authoring
velaris run tests/
```

::: warning Working directory
Must run from `examples/authoring/` — `velaris_plugins.py` is loaded from cwd only.
:::

Expected:

```text
✓ test_dice_roll
✓ test_login
✓ test_login_yaml
✓ test_random
✓ User logs in

Passed: 5
Failed: 0
Duration: 0.01s
```

With HTML report:

```bash
velaris run tests/ --html-report
open report.html
```

## Three ways to write the same login test

**Python**

```python
@test("browser")
def test_login(browser):
    browser.open("/login")
    browser.type("#username", "demo")
    browser.click("#submit")
```

**YAML**

```yaml
name: test_login_yaml
capabilities:
  - browser
actions:
  - browser.open("/login")
  - browser.type("#username", "demo")
  - browser.click("#submit")
```

**BDD**

```gherkin
Feature: Login

Scenario: User logs in

  Given browser.open("/login")
  When browser.type("#username", "demo")
  Then browser.click("#submit")
```

All three emit identical capability events. See [BDD Adapter](/bdd-adapter) and [Executable YAML](/executable-yaml).

## Learn

- [Authoring Style Architecture](/authoring-styles)
- [Executable YAML](/executable-yaml)
- [BDD Adapter](/bdd-adapter)
