# What Velaris Can Do Today

**Version:** v0.1.0-alpha  
**Last updated:** 2026-06-09

Velaris is a capability-driven test execution engine. Tests declare what they need (`api`, `browser`, `secrets`, …), configuration selects provider implementations, and the runner handles collection, resolution, injection, execution, teardown, and reporting.

This document describes **what works today**, **what is experimental**, and **what is explicitly not included** — based on the current codebase and test suite (147 tests across `velaris-contracts` and `velaris-core`).

---

## Core model

### Capabilities

A **capability** is a named interface a test depends on. Tests declare capabilities explicitly; the runner resolves and injects them as function parameters.

```python
from velaris_core.decorators import test

@test("api", "secrets")
def test_checkout(api, secrets):
    token = secrets.get("API_TOKEN")
    response = api.get("/users", headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()
```

Rules enforced at collection time:

- Every test must declare at least one capability.
- Parameter names must match declared capability IDs exactly.
- The capability list must match the function signature (no extras, no omissions).

Bare `@test` (no arguments) infers capabilities from parameter names in signature order.

### Providers

A **provider** is a concrete implementation of a capability, selected by configuration. The same test can run against different providers by swapping config — no test code changes.

```toml
[capabilities.secrets]
provider = "env"    # or "static"
```

### Configuration (`velaris.toml`)

`velaris.toml` binds each capability to a provider and optional provider-specific options:

```toml
[capabilities.api]
provider = "requests"

[capabilities.api.options]
base_url = "http://testserver"

[capabilities.browser]
provider = "fake"

[capabilities.secrets]
provider = "env"
```

Provider overrides via environment variables are also supported:

```bash
VELARIS__CAPABILITIES__API__PROVIDER=requests
```

### Execution pipeline

Every `velaris run` follows the same path:

```text
Collect → TestSpec → Resolve → Inject → Execute → Events → Report
```

| Stage | What happens |
|-------|----------------|
| **Collect** | Adapters compile Python, YAML, or BDD files into TestSpec IR |
| **TestSpec** | Validate test name, capabilities, and callable |
| **Resolve** | Look up provider factories from registry + config |
| **Inject** | Pass resolved capability instances as test parameters |
| **Execute** | Run the test callable |
| **Events** | Emit lifecycle and capability observation events |
| **Report** | Stdout, JSON log, or static HTML |

The runner operates on **TestSpec IR only** — it never imports authoring-style-specific code. Python, YAML, and BDD tests all execute through the same engine.

### Teardown

Capabilities are torn down in **LIFO order** (last resolved, first torn down) after each test, whether it passes or fails.

---

## Built-in capabilities

Velaris ships four first-party capability contracts in `velaris-contracts`:

### `api@0.1`

**Provider:** `requests`

Synchronous HTTP client for integration tests.

| Method | Description |
|--------|-------------|
| `get(path, *, headers, params)` | HTTP GET |
| `post(path, *, headers, json, data)` | HTTP POST |
| `put(path, *, headers, json, data)` | HTTP PUT |
| `patch(path, *, headers, json, data)` | HTTP PATCH |
| `delete(path, *, headers)` | HTTP DELETE |

Response surface: `status_code`, `headers`, `body`, `text`, `json()`, `raise_for_status()`.

Config options: `base_url` (prepended to paths).

### `browser@0.1`

**Providers:** `fake`, `verbose`

Minimal browser automation surface. Both providers are in-memory — no real browser, no network.

| Method | Description |
|--------|-------------|
| `open(url)` | Navigate to URL |
| `click(selector)` | Click element |
| `type(selector, text)` | Type into element |
| `close()` | Close session |

- `fake` — silent in-memory browser (records history, no stdout trace)
- `verbose` — same behavior, emits capability observations to stdout in debug mode

### `secrets@0.1`

**Providers:** `env`, `static`

Read-only access to named secret values.

| Method | Description |
|--------|-------------|
| `get(name)` | Return secret value (raises `KeyError` if missing) |

- `env` — reads from environment variables (secret name = env var name)
- `static` — reads from `[capabilities.secrets.options.values]` in config

### `target_environment@0.1`

**Provider:** `static`

Named environment slice with string endpoint values (URLs, DSNs, hosts).

| Member | Description |
|--------|-------------|
| `environment` | Environment name (e.g. `local-hermetic`, `ci`) |
| `endpoint(name)` | Return endpoint value by name (raises `KeyError` if missing) |

**Bootstrap convention (Model A):** If `api.options.base_url` is unset, Velaris copies `target_environment.endpoints.api` into the API binding at resolve time. This is a config merge — not a capability dependency. Tests do not need to declare `target_environment` for this merge to apply.

---

## Authoring styles

Velaris supports three authoring frontends, all compiling to the same TestSpec IR:

### 1. Python (`.py`)

The primary authoring style. Use `@test` decorator from `velaris_core.decorators`.

```python
@test("browser")
def test_login(browser):
    browser.open("/login")
    browser.type("#username", "demo")
    browser.click("#submit")
```

### 2. YAML (`.yaml`, `.yml`)

Declaration-only or executable tests.

**Declaration-only** (capabilities declared, no-op body):

```yaml
name: test_login
capabilities:
  - browser
```

**Executable** (serialized capability calls):

```yaml
name: test_login
capabilities:
  - browser
actions:
  - browser.open("/login")
  - browser.type("#username", "demo")
  - browser.click("#submit")
```

YAML actions are **serialized capability calls only**:

- Parsed structurally with `ast` — never `eval`'d
- Single `capability.method(args)` per line
- No loops, conditions, variables, templates, keywords, or user-defined functions

### 3. Minimal BDD (`.feature`)

Not Behave or Cucumber. A tiny Gherkin subset that compiles to the same TestSpec as YAML.

Supported syntax:

```gherkin
Feature: Login

Scenario: User logs in
  Given browser.open("/login")
  When browser.type("#username", "demo")
  Then browser.click("#submit")
```

- `Feature:` and `Scenario:` headers required
- `Given` / `When` / `Then` lines are serialized capability calls (keywords carry no semantics)
- No tags, scenario outlines, tables, backgrounds, or step definitions
- Scenario names become test names (may include spaces)

---

## CLI

The `velaris` CLI (`velaris-core` package) provides these commands. See the
[CLI reference](/getting-started/cli) for full options.

| Command | Purpose |
|---------|---------|
| `velaris init <name>` | Scaffold a new project with a passing sample test |
| `velaris collect [paths]` | Discover tests and show what would run — no execution |
| `velaris run [paths]` | Execute tests |
| `velaris report <json-log>` | Generate a static HTML report from an event log |
| `velaris capabilities` | List capabilities Velaris knows about |
| `velaris capability <id>` | Show one capability's description, methods, providers |
| `velaris doctor` | Diagnose the local environment before running |

### `velaris run`

```bash
velaris run [paths...] [options]
```

| Argument / Option | Default | Description |
|-------------------|---------|-------------|
| `paths` | `tests` | Files or directories to collect |
| `--config` | `velaris.toml` | Path to configuration file |
| `--verbose` | — | Show lifecycle events (run, resolve, pass/fail, teardown) |
| `--debug` | — | Show all events including capability observations |
| `--json-log PATH` | — | Write JSON-lines event log |
| `--html-report [PATH]` | — | Generate static HTML report after run (default: `report.html`) |

Exit code: `0` if all tests pass, `1` if any fail.

### `velaris report`

```bash
velaris report <json-log> [-o report.html]
```

Generate a static HTML report from a prior JSON event log. Fully offline — does not import the runner or resolver.

Typical workflows:

```bash
# One command
velaris run tests/ --html-report

# Two-step (re-generate report from existing log)
velaris run tests/ --json-log run.jsonl
velaris report run.jsonl
```

---

## Reporting

### Stdout (terminal)

Three output modes:

| Mode | Flag | Shows |
|------|------|-------|
| **Default** | (none) | ✓/✗ per test + session summary (passed, failed, duration) |
| **Verbose** | `--verbose` | Lifecycle events: test start, capability resolve, teardown |
| **Debug** | `--debug` | Everything, including per-action capability observations |

Color is enabled on TTY stdout (respects `NO_COLOR` / `FORCE_COLOR`).

### JSON event log

`--json-log` writes one JSON object per line. Event types include:

| Event | Description |
|-------|-------------|
| `TestStarted` | Test execution began |
| `CapabilityResolved` | Capability bound to provider |
| `CapabilityObserved` | Provider action trace (e.g. `browser.open`) |
| `TestPassed` / `TestFailed` | Test outcome |
| `CapabilityTeardown` | Provider cleanup |
| `RunFinished` | Session summary (passed, failed, duration) |

Events are wrapped in `EventEnvelope` with a `test` field for per-test correlation.

### Static HTML report

Self-contained HTML file with embedded CSS and JavaScript:

- Summary cards (total, passed, failed, duration)
- Test list with click-to-select
- Detail panel (failure message + capability timeline)
- Dark/light theme toggle (persisted in `localStorage`)

Generated by `velaris report` or `velaris run --html-report`. No server required to view.

---

## Plugins and extension

### Plugin SDK (`velaris_core.sdk`)

Public surface for capability authors (~7 symbols):

| Symbol | Purpose |
|--------|---------|
| `Registry` | Register provider factories |
| `ProviderFactory` | Factory type alias |
| `Teardown` | Teardown callable type |
| `capability_observed` | Emit observation events from providers |
| `pop_emit` | Retrieve emit callback from provider options |
| `EMIT_OPTION_KEY` | Option key for emit injection |
| `register_manual_plugins` | Load `velaris_plugins.py` explicitly |

### Manual plugin bootstrap

External capabilities register via `velaris_plugins.py` in the **project directory**:

```python
# velaris_plugins.py
from velaris_core.sdk import Registry
from my_package.provider import register_my_providers

def register(registry: Registry) -> None:
    register_my_providers(registry)
```

**Critical:** `velaris_plugins.py` is loaded from the **current working directory only**. Always `cd` into your project before `velaris run`.

### What plugin authors build

1. A `typing.Protocol` contract (in your package)
2. A provider factory: `(options) -> (instance, teardown)`
3. `registry.register(capability_id, provider_name, factory)` in `velaris_plugins.py`
4. A `[capabilities.<id>]` binding in `velaris.toml`

Example external capabilities in the repo: `database`, `filesystem`, `random` (stress-test), `clock` (plugins example).

---

## Runnable examples

| Example | Passes out of the box? | Demonstrates |
|---------|------------------------|--------------|
| [browser/](../examples/browser/) | **Yes** | Fake browser, first-run path |
| [authoring/](../examples/authoring/) | **Yes** | Python + YAML + BDD → same engine |
| [stress-test/](../examples/stress-test/) | **Yes** | External capabilities via plugin SDK |
| [plugins/](../examples/plugins/) | **Yes** | Clock capability, manual plugin registration |
| [reporting/](../examples/reporting/) | **Yes** | Pre-built HTML report sample |
| [composition/](../examples/composition/) | No | Model A composition (needs HTTP mock) |
| [minimal/](../examples/minimal/) | No | API + secrets swap (needs `API_TOKEN` + mock) |

Recommended first run:

```bash
cd examples/browser
velaris run tests/ --config velaris.fake.toml
```

---

## Install

Alpha requires cloning the repository and installing editable packages:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e packages/velaris-contracts -e "packages/velaris-core[dev]"
```

No PyPI packages yet. The `velaris` CLI is provided by `velaris-core`.

---

## What is stable (test-covered, intended to stay consistent)

- `velaris run` execution loop
- Multi-format collection → TestSpec → runner (Python, YAML, minimal BDD)
- Config binding via `velaris.toml`
- Per-test resolver with LIFO teardown
- Event model (`EventEnvelope`, `CapabilityObserved`, lifecycle events)
- Plugin SDK (`velaris_core.sdk`)
- Model A composition — independent capabilities composed in test code or config
- CLI output modes (default / `--verbose` / `--debug`)
- Static HTML report (`velaris report` or `velaris run --html-report`)
- Provider swap without test code changes

---

## What is experimental (works, but rough edges expected)

| Area | Notes |
|------|-------|
| **Install path** | Clone + editable pip only; no PyPI |
| **External capability packaging** | No conventions for publishing contract packages |
| **`velaris_plugins.py` loading** | Cwd-sensitive; silent skip if run from wrong directory |
| **Config validation for external capabilities** | Built-in providers are validated; external ones are not |
| **YAML adapter** | Minimal syntax only — not a keyword engine |
| **BDD adapter** | Minimal Gherkin only — not Behave/Cucumber |
| **Capability version pinning** | `@0.1` suffix is documentation-only; not enforced at runtime |
| **Plugin discovery** | No entry points, no auto-discovery |

---

## Limitations (not included in v0.1.0-alpha)

### Execution

| Feature | Status |
|---------|--------|
| Parallel test execution | Not implemented |
| Test retries / flakiness handling | Not implemented |
| Parametrized tests (`@pytest.mark.parametrize` equivalent) | Not implemented |
| Test markers / tags / filtering | Not implemented |
| Profiles (`--profile ci`) | Not implemented |
| `conftest.py` / hierarchical fixtures | Not implemented |

### Authoring

| Feature | Status |
|---------|--------|
| Full Gherkin (tags, outlines, tables, backgrounds, step defs) | Not implemented |
| YAML keyword engine (loops, conditions, variables) | Explicitly out of scope |
| Robot Framework-style keywords | Not implemented |
| IDE test discovery integration | Not implemented |

### Capabilities and providers

| Feature | Status |
|---------|--------|
| Real browser drivers (Playwright, Selenium) | Not implemented (fake/verbose only) |
| Mobile automation | Not implemented |
| Database providers (Postgres, SQLite) | Not built-in (plugin example only) |
| Authentication / OAuth providers | Not implemented |
| Commercial test grids (BrowserStack, etc.) | Not implemented |

### Plugins and packaging

| Feature | Status |
|---------|--------|
| Plugin discovery via entry points | Not implemented |
| PyPI-distributed plugin packages | Not implemented |
| Plugin marketplace / registry | Not implemented |
| Config-path-based plugin discovery | Not implemented |

### Reporting and CI

| Feature | Status |
|---------|--------|
| JUnit XML output | Not implemented |
| Historical report trends / databases | Not implemented |
| CI integration helpers | Not implemented |
| Report diffing across runs | Not implemented |

### Ecosystem

| Feature | Status |
|---------|--------|
| pytest coexistence / `velaris-pytest` plugin | Designed (RFC-006), not shipped |
| pytest replacement for unit tests | Explicit non-goal |
| Enterprise governance / org-wide policy | Not implemented |
| Migration tooling (`velaris migrate`) | Not implemented |

---

## What Velaris is not

- **Not a pytest replacement.** Unit tests should stay on pytest. Velaris targets integration and E2E orchestration.
- **Not a plugin marketplace.** Extension is manual via `velaris_plugins.py` and the SDK.
- **Not a full BDD framework.** The `.feature` adapter validates architecture; it is not Cucumber.
- **Not a keyword engine.** YAML and BDD actions are serialized capability calls, not a DSL.
- **Not production-hardened.** v0.1.0-alpha is a public preview with known onboarding friction.

---

## Repository layout

```text
velaris/
├── packages/
│   ├── velaris-contracts/   # Versioned capability Protocols
│   └── velaris-core/        # Runner, resolver, adapters, CLI, HTML report
├── examples/                # Runnable demo projects
├── docs/                    # VitePress documentation site
└── pyproject.toml           # Monorepo workspace (pytest config)
```

---

## Related docs

- [Alpha scope](/alpha-scope) — official alpha boundaries
- [Getting started](/getting-started/) — install and first test
- [CLI reference](/getting-started/cli) — full command options
- [Plugin author guide](/guide/plugin-author) — build a custom capability
- [Examples](/examples/) — runnable projects
- [Roadmap](/roadmap) — milestone history and future direction
