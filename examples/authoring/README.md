# Authoring styles example

Three authoring styles, one execution engine. Every test below compiles to the same `TestSpec` and runs through the same runner, resolver, and reporting.

**Must run from this directory** — `velaris_plugins.py` registers the external `random` capability from cwd.

## Layout

```text
examples/authoring/
├── velaris.toml            # binds random → seeded, browser → fake
├── velaris_plugins.py      # registers the random provider
├── rng/                  # external capability (contract + provider)
└── tests/
    ├── test_dice.py      # Python — random
    ├── test_random.yaml  # YAML — declaration only (random)
    ├── test_login.py     # Python — browser login
    ├── test_login.yaml   # YAML — executable browser login
    └── login.feature     # BDD — browser login
```

## Run

```bash
cd examples/authoring
velaris run tests/
```

The three login tests (Python, YAML, BDD) emit **identical** browser capability events — see [BDD Adapter](../../docs/bdd-adapter.md).

## HTML report

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

## Docs

- [Authoring Styles](../../docs/authoring-styles.md)
- [Executable YAML](../../docs/executable-yaml.md)
- [BDD Adapter](../../docs/bdd-adapter.md)
