# Plugin author guide

::: warning Superseded
Use the [Plugin Author Guide](/guide/plugin-author) on the docs site. This file is kept for reference only.
:::

How to add a capability to Velaris without reading framework internals.

## Prerequisites

- Install Velaris: `pip install -e packages/velaris-contracts -e packages/velaris-core`
- A test project directory with `velaris.toml`

## The public SDK

Import **only** from `velaris_core.sdk`:

| Symbol | Purpose |
|--------|---------|
| `Registry` | Register `(capability_id, provider)` → factory |
| `ProviderFactory` | `(options: dict) -> (instance, teardown)` |
| `Teardown` | Callable run after the test (LIFO order) |
| `pop_emit` | Strip internal `_emit` callback from factory options |
| `capability_observed` | Build observation events for reporters |
| `EMIT_OPTION_KEY` | Internal option key (`"_emit"`) — rarely needed directly |
| `register_manual_plugins` | Advanced: load `velaris_plugins.py` explicitly |

Everything else in `velaris_core` (runner, resolver, collector, bootstrap internals) is framework code. You do not need it to author a provider.

## Five steps

### 1. Define a contract

A contract is a `typing.Protocol` describing what tests can call. It lives in **your** package — not in `velaris-contracts` unless you choose to publish it separately.

```python
# clock/contract.py
from typing import Protocol, runtime_checkable

CAPABILITY_ID = "clock"
CONTRACT_VERSION = "0.1"

@runtime_checkable
class Clock(Protocol):
    def now(self) -> str: ...
```

Convention: capability id `clock` with version `0.1` → tests declare `@test("clock")`.

### 2. Implement a provider factory

A factory receives merged config options plus an internal emit callback. Use `pop_emit` to extract it.

```python
# clock/provider.py
from velaris_core.sdk import Teardown, capability_observed, pop_emit

class FixedClock:
    def __init__(self, fixed_time: str, emit=None):
        self._fixed_time = fixed_time
        self._emit = emit

    def now(self) -> str:
        if self._emit:
            self._emit(capability_observed("clock", "now", {"value": self._fixed_time}))
        return self._fixed_time

def create_fixed_clock(options):
    cleaned, emit = pop_emit(options)
    fixed_time = str(cleaned.get("fixed_time", "2026-01-01T00:00:00Z"))

    def teardown():
        pass

    return FixedClock(fixed_time, emit=emit), teardown
```

Rules:

- Return `(instance, teardown)` — teardown may be a no-op.
- Do not mutate options after `pop_emit`.
- Emit observations via `capability_observed(capability, action, data)`.

### 3. Register manually

Create `velaris_plugins.py` next to your `velaris.toml`:

```python
# velaris_plugins.py
from velaris_core.sdk import Registry
from clock.provider import create_fixed_clock

def register(registry: Registry) -> None:
    registry.register("clock", "fixed", create_fixed_clock)
```

When the runner starts, `bootstrap.register_builtin_providers()` loads this file from the **current working directory** and calls `register(registry)`.

There is no auto-discovery, no entry points, and no packaging hook — registration is explicit.

### 4. Bind in config

```toml
# velaris.toml
[capabilities.clock]
provider = "fixed"

[capabilities.clock.options]
fixed_time = "2026-06-02T12:00:00Z"
```

Capabilities not listed in core `KNOWN_PROVIDERS` accept any provider name at config load time. Validation happens at resolution when the registry must have a matching factory.

### 5. Write tests

```python
from velaris_core.decorators import test

@test("clock")
def test_fixed_time(clock):
    assert clock.now() == "2026-06-02T12:00:00Z"
```

Run from the directory that contains both `velaris.toml` and `velaris_plugins.py`:

```bash
cd my-project
velaris run tests/
```

## Working example

See [examples/plugins](../examples/plugins/) for a complete `clock.now()` plugin.

## What you do not touch

| Module | Role | Plugin author |
|--------|------|---------------|
| `runner.py` | Execute TestSpecs | Do not modify |
| `resolver.py` | Inject capabilities | Do not modify |
| `reporting.py` | Event fan-out | Do not modify |
| `bootstrap.py` | Calls your `velaris_plugins.py` | Do not modify |

Extension is: contract + factory + `velaris_plugins.py` + config binding.

## Registration flow (diagram)

```text
velaris run tests/
    │
    ▼
runner.run()
    ├── collect → TestSpec[]
    ├── load_config → velaris.toml bindings
    ├── Registry()
    └── register_builtin_providers(registry)
            ├── built-in factories (api, secrets, …)
            └── register_manual_plugins(registry)
                    └── import velaris_plugins.py (cwd)
                            └── register(registry)
    │
    ▼
for each TestSpec:
    Resolver(registry, bindings).resolve("clock") → FixedClock
    test function runs
    teardown (LIFO)
```

## Architectural notes (Milestone 7)

**Can someone add a capability without understanding internals?**  
Yes, if they follow this guide: Protocol + factory + `velaris_plugins.py` + config. The SDK surface is ~7 symbols.

**Weaknesses discovered:**

1. **`velaris_plugins.py` is cwd-sensitive** — run `velaris run` from the project root that contains the file. No config-path-based plugin discovery yet.
2. **`KNOWN_PROVIDERS` is core-only** — external capabilities skip name validation at config load; typos surface at runtime via `UnknownProviderError`.
3. **Contracts are informal** — external Protocols are not registered anywhere; capability id is by convention and `@test(...)` declaration only.
4. **Bootstrap still orchestrates loading** — authors don't edit bootstrap, but the hook lives there; alternative would be runner accepting a registrar callback (not implemented).
5. **No version negotiation** — `@test("clock")` does not pin `0.1`; versioning is documentation-only today.

## Out of scope (by design)

- Plugin discovery / setuptools entry points
- Dependency graphs between capabilities
- Packaging automation for third-party wheels
- Dynamic contract registration

These may come later; manual registration is intentional for Milestone 7.
