If Velaris is trying to be a **modern successor** rather than a pytest clone, I'd define it as:

```text
Velaris = Execution Engine + Plugin System + Capability Model
```

The interesting part is the **Capability Model**.

---

### Pytest

```text
pytest
├── Core
└── Plugins
```

Pytest says:

> "Plugins can do whatever they want."

Very flexible, but plugins often don't integrate well with each other.

---

### Robot

```text
Robot
├── Core
├── DSL
└── Libraries
```

Robot says:

> "Everything becomes a keyword."

Easy to read, but eventually you end up with:

```robot
Click Button
Input Text
Wait Until Element Is Visible
Get Element Count
```

Thousands of keywords.

---

### Velaris

```text
Velaris
├── Core Engine
├── Capability Model
├── Plugin System
└── Multiple Authoring Styles
```

---

## What is a Capability?

Instead of exposing raw keywords or functions, plugins declare capabilities.

Example:

```python
@capability("browser")
class PlaywrightBrowser:
    ...
```

```python
@capability("browser")
class SeleniumBrowser:
    ...
```

```python
@capability("database")
class PostgreSQLDatabase:
    ...
```

```python
@capability("database")
class MySQLDatabase:
    ...
```

The framework doesn't care which implementation exists.

---

## Test Author Writes

```python
def test_login(browser):
    browser.open("/login")
    browser.click("login")
```

Not:

```python
def test_login(playwright_browser):
```

Not:

```python
def test_login(selenium_browser):
```

Just:

```python
browser
```

because browser is a capability.

---

## Configuration Decides

```yaml
capabilities:
  browser: playwright
```

or

```yaml
capabilities:
  browser: selenium
```

Same tests.

No changes.

---

## Another Example

API testing.

Test:

```python
def test_user(api):
    response = api.get("/users")
```

Config:

```yaml
api: requests
```

or

```yaml
api: httpx
```

or

```yaml
api: custom_company_client
```

No test changes.

---

## Multiple Authoring Styles

One thing I'd steal from Robot.

Users choose how they write tests.

### Python

```python
def test_login(browser):
    ...
```

### YAML

```yaml
test: login

steps:
  - open: /login
  - click: login
```

### BDD

```gherkin
Scenario: Login
```

All converted internally into the same execution model.

---

## Reporting as a Framework Contract

Pytest plugins often reinvent reporting.

In Velaris:

```python
@step("Login")
def login():
    ...
```

Every plugin automatically reports through the same API.

Result:

```text
Login
 ├─ Open Page
 ├─ Enter Username
 └─ Click Login
```

without each plugin building its own report format.

---

## So the one-line definition becomes:

```text
Pytest = Engine + Plugins

Robot = Engine + DSL + Libraries

JUnit = Engine + Annotations

NUnit = Engine + Attributes

Velaris = Engine + Capabilities + Plugins
```

The capability idea is the only part here that I think is genuinely different enough to justify a new framework. Everything else—fixtures, assertions, reporting, parametrization, parallel execution—is table stakes in 2026.

The hard question I'd ask before building Velaris is:

> What can a Capability Model do that pytest fixtures cannot?

If you can't answer that convincingly, Velaris is just another pytest with different syntax. That's the test I'd use before writing a single line of code.
