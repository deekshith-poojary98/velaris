# Execution Pipeline

Every `velaris run` follows the same pipeline:

```mermaid
flowchart LR
    A["① Collect"] --> B["② TestSpec"]
    B --> C["③ Resolve"]
    C --> D["④ Inject"]
    D --> E["⑤ Execute"]
    E --> F["⑥ Events"]
    F --> G["⑦ Report"]
```

## ① Collect

`collector.py` dispatches each file to an authoring adapter (Python, YAML, or BDD).

```python
# Python: tests/test_login.py
@test("browser")
def test_login(browser): ...
```

```yaml
# YAML: tests/test_login.yaml
name: test_login_yaml
capabilities: [browser]
actions: [browser.open("/login")]
```

All adapters produce the same `TestSpec` shape.

## ② TestSpec

Validated IR passed to the runner:

```python
TestSpec(name="test_login", capabilities=["browser"], callable=...)
```

Duplicate names and parameter mismatches fail here.

## ③ Resolve

For each capability in the TestSpec:

1. Load binding from `velaris.toml` → `(provider, options)`
2. Look up factory in registry → `registry.get_factory("browser", "fake")`
3. Call factory with options + emit callback
4. Cache instance for this test scope

With `--verbose` or `--debug`, resolution is printed:

```text
RESOLVE browser(fake)
```

(Default stdout omits this — see [CLI UX redesign](/cli-ux-redesign).)

## ④ Inject

Build kwargs from resolved instances:

```python
kwargs = {cap: resolver.resolve(cap) for cap in spec.capabilities}
spec.callable(**kwargs)
```

Parameter names must match capability IDs.

## ⑤ Execute

Run the test function. Catch:

- `AssertionError` → `TestFailed`
- Any other exception → `TestFailed`

Always run `resolver.teardown()` in `finally` (LIFO).

## ⑥ Events

Every stage emits events through `EventEnvelope`:

```mermaid
sequenceDiagram
    participant Runner
    participant Resolver
    participant Provider
    participant Reporter

    Runner->>Reporter: TestStarted
    Runner->>Resolver: resolve("browser")
    Resolver->>Provider: factory(options)
    Provider-->>Resolver: instance
    Resolver->>Reporter: CapabilityResolved
    Runner->>Provider: test uses browser
    Provider->>Reporter: CapabilityObserved
    Runner->>Reporter: TestPassed
    Runner->>Resolver: teardown()
    Resolver->>Reporter: CapabilityTeardown
```

## ⑦ Report

`multiplex()` fans out to all reporters:

- **StdoutReporter** — always active (default / `--verbose` / `--debug` modes)
- **JsonReporter** — when `--json-log` or `--html-report` is set
- **HTML generator** — after run when `--html-report`, or via `velaris report`

Session ends with `RunFinished` (pass/fail counts, duration).

## Full run diagram

```mermaid
flowchart TB
    START([velaris run]) --> COLLECT[collect paths]
    COLLECT --> CONFIG[load_config]
    CONFIG --> COMPOSE[apply_bootstrap_conventions]
    COMPOSE --> REG[register_builtin_providers]
    REG --> LOOP{for each TestSpec}

    LOOP --> TS[TestStarted]
    TS --> NEW[new Resolver]
    NEW --> RESOLVE[resolve each capability]
    RESOLVE --> CALL[call test function]
    CALL -->|pass| PASS[TestPassed]
    CALL -->|fail| FAIL[TestFailed]
    PASS --> TD[teardown LIFO]
    FAIL --> TD
    TD --> LOOP

    LOOP -->|done| FIN[RunFinished]
    FIN --> END([exit code])
```

## What the runner does not do

- Import provider modules directly (bootstrap only)
- Build capability dependency graphs
- Share instances across tests
- Parse YAML or Gherkin
