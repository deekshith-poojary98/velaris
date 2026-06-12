# Tags & Test Selection

Tags provide a lightweight, first-class classification mechanism to organize and selectively execute subsets of tests across all authoring styles (Python, YAML, and BDD).

---

## Why Tags Exist

As test suites grow, executing all tests on every run becomes impractical. Tags allow you to group related tests together under arbitrary labels (e.g. `smoke`, `ui`, `slow`, `api-only`) so they can be filtered during discovery and execution.

Unlike a rigid hierarchy of directories or test suites, tags are flat metadata strings. A test can carry multiple tags or none at all.

---

## Defining Tags in Authoring Styles

### Python

Use the `tags` list argument inside the `@test` decorator:

```python
from velaris_core.decorators import test

@test("browser", tags=["smoke"])
def test_login(browser):
    ...

@test("api", "secrets", tags=["smoke", "regression"])
def test_payment(api, secrets):
    ...
```

### YAML

Specify the `tags` key as a list of strings:

```yaml
name: test_login
capabilities:
  - browser
tags:
  - smoke
  - ui
actions:
  - browser.open("/login")
```

### BDD (Gherkin)

Use standard Gherkin-style tag annotations starting with `@` before a Feature or Scenario:

```gherkin
@smoke
@ui
Scenario: User logs in
  Given browser.open("/login")
  When browser.type("#username", "demo")
  Then browser.click("#submit")
```

Both feature-level tags (placed above the `Feature:` declaration) and scenario-level tags are aggregated.

---

## CLI Filtering & Selection

### Running Selected Tags

Use the `--tag` option in `velaris run` to execute only matching tests:

```bash
# Run tests containing the "smoke" tag
velaris run --tag smoke
```

### Multiple Tags (OR Semantics)

Specify multiple `--tag` options to run tests matching *any* of the specified tags:

```bash
# Run tests that contain either "smoke" OR "ui" tags
velaris run --tag smoke --tag ui
```

> [!NOTE]
> Velaris uses **OR semantics** rather than **AND semantics** for tag combinations. This is designed to facilitate quick, ad-hoc execution batches (e.g. "run all smoke tests plus all UI tests in one run"). Tag expressions (like `smoke and not ui`) are not supported.

### Collect Filtering

Filter test discovery output using `--tag` with `velaris collect`:

```bash
# Show only tests matching "regression" tag
velaris collect --tag regression
```

---

## Validation Rules

To prevent typos and ensure clean suites, Velaris strictly validates tags during collection:

1. **Non-empty strings**: Tags cannot be empty (`""` or `@`).
2. **Uniqueness per test**: A test cannot declare the same tag multiple times. If duplicates are found, collection will fail with a `CollectionError`. (Velaris will not silently deduplicate tags).
