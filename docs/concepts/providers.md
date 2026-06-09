# Providers

A **provider** is a named implementation of a capability, registered as a factory function.

## Factory signature

```python
def create_my_provider(options: dict) -> tuple[Any, Teardown]:
    cleaned, emit = pop_emit(options)
    instance = MyProvider(cleaned, emit=emit)

    def teardown() -> None:
        instance.close()

    return instance, teardown
```

| Return | Purpose |
|--------|---------|
| Instance | Object injected into the test (must satisfy the contract) |
| Teardown | Callable invoked after the test (LIFO with other capabilities) |

## Registration

Built-in providers register in `bootstrap.py`. External providers register in `velaris_plugins.py`:

```python
def register(registry: Registry) -> None:
    registry.register("clock", "fixed", create_fixed_clock)
```

Registry key: `(capability_id, provider_name)` — must match `velaris.toml`.

## Options from config

Factory `options` merges config bindings with an internal emit callback:

```python
from velaris_core.sdk import pop_emit

def create_fixed_clock(options):
    cleaned, emit = pop_emit(options)
    fixed_time = cleaned.get("fixed_time", "2026-01-01T00:00:00Z")
    ...
```

Never mutate `options` after `pop_emit`. The resolver injects `_emit` for event emission.

## Emitting events

```python
from velaris_core.sdk import capability_observed

self._emit(capability_observed("browser", "open", {"path": url}))
```

Observations appear in JSON logs as `CapabilityObserved`. On stdout they appear only with `--debug` (default mode shows ✓/✗ per test).

## Built-in providers

| Capability | Provider | Description |
|------------|----------|-------------|
| `api` | `requests` | HTTP client via `requests` library |
| `secrets` | `env` | Read from environment variables |
| `secrets` | `static` | Read from config `values` table |
| `browser` | `fake` | In-memory browser for tests |
| `browser` | `verbose` | Fake browser with verbose events |
| `target_environment` | `static` | Named environment + endpoint map |

## Provider swap

Same test, different config:

```bash
velaris run tests/test_token.py --config velaris.env-secrets.toml
velaris run tests/test_token.py --config velaris.static-secrets.toml
```

The test declares `@test("secrets")` — config chooses `env` vs `static`.
